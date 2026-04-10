"""AI 任务执行器。"""

from __future__ import annotations

import base64
import json
import re
from html import unescape
from typing import Any

import httpx

from app.clients.siliconflow_client import SiliconFlowClient
from app.core.config import settings
from app.models.ai_task import AITask


TARGET_FIELDS: dict[str, str] = {
    "paper": (
        "meta_json 必须优先包含 authors, conference, year, source, identifier, "
        "domain_tags, keywords, method_tags, dedup_key, summary_short, summary_zh, summary_en, tags, note。"
    ),
    "article": (
        "meta_json 必须优先包含 platform, account_name, author, publish_date, summary_short, "
        "keywords, topic_tags, core_points, referenced_links, paper_candidates, note。"
    ),
    "competition": (
        "meta_json 必须优先包含 organizer, prizePool, deadline, theme, competitionType, "
        "website, registrationUrl, timeline。"
    ),
    "insight": "meta_json 必须优先包含 source, tags, note。",
    "voice": "meta_json 必须优先包含 duration, transcription, note。",
}

WEBPAGE_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


class AITaskProcessor:
    def __init__(self) -> None:
        """初始化 AI 任务处理器并创建底层模型客户端。"""
        self.client = SiliconFlowClient()

    def process(self, task: AITask) -> dict[str, Any]:
        """根据任务类型分发到对应的处理流程。"""
        if task.task_type == "parse-link":
            return self._process_link_task(task)
        if task.task_type == "structure-text":
            return self._process_text_task(task)
        if task.task_type == "parse-image":
            return self._process_image_task(task)
        if task.task_type == "transcribe-audio":
            return self._process_audio_task(task)

        raise RuntimeError(f"Unsupported AI task type: {task.task_type}")

    def _process_link_task(self, task: AITask) -> dict[str, Any]:
        """抓取网页正文后执行结构化提取。"""
        url = self._require_string(task.input_payload, "url")
        target_type = task.input_payload.get("target_type")
        page_title, page_text = self._fetch_webpage(url)
        result = self._structure_text(
            text=page_text,
            target_type=target_type,
            task_hint="这是通过 URL 抓取到的网页正文，请优先提炼结构化信息。",
            source_payload={"url": url, "page_title": page_title},
        )
        result["origin_url"] = url
        if page_title and not result.get("title"):
            result["title"] = page_title
        return result

    def _process_text_task(self, task: AITask) -> dict[str, Any]:
        """对用户直接提交的文本执行结构化整理。"""
        text = self._require_string(task.input_payload, "text")
        target_type = task.input_payload.get("target_type")
        return self._structure_text(
            text=text,
            target_type=target_type,
            task_hint="这是用户直接提交的文本内容，请完成结构化整理。",
            source_payload={"source_type": "text"},
        )

    def _process_image_task(self, task: AITask) -> dict[str, Any]:
        """对图片输入执行 OCR 与视觉结构化分析。"""
        image_url = self._resolve_media_url(task.input_payload, "image")
        target_type = task.input_payload.get("target_type")
        prompt = self._build_system_prompt(target_type)
        filename = task.input_payload.get("filename")
        content = [
            {
                "type": "text",
                "text": (
                    "请先执行 OCR，再结合图像内容提取结构化信息。"
                    "如果内容像论文截图、海报、网页卡片或竞赛海报，请按最合适的 item_type 组织输出。"
                    f"\n文件名: {filename or 'unknown'}"
                ),
            },
            {
                "type": "image_url",
                "image_url": {"url": image_url},
            },
        ]
        raw = self.client.chat_completion(
            model=settings.siliconflow_vision_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
        )
        result = self._parse_json_response(raw)
        result.setdefault("source_type", "image")
        return self._normalize_output(result)

    def _process_audio_task(self, task: AITask) -> dict[str, Any]:
        """先完成音频转写，再对转写结果做结构化整理。"""
        filename = task.input_payload.get("filename", "audio.wav")
        audio_bytes = self._resolve_audio_bytes(task.input_payload)
        language = task.input_payload.get("language")
        transcription = self.client.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=task.input_payload.get("content_type"),
            language=language,
        )
        target_type = task.input_payload.get("target_type") or "voice"
        result = self._structure_text(
            text=transcription,
            target_type=target_type,
            task_hint="这是语音转写文本，请补充结构化摘要、标签和记录建议。",
            source_payload={"source_type": "audio", "filename": filename},
        )
        result.setdefault("meta_json", {})
        result["meta_json"]["transcription"] = transcription
        return self._normalize_output(result)

    def _structure_text(
        self,
        *,
        text: str,
        target_type: str | None,
        task_hint: str,
        source_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """调用文本模型把原始内容整理成统一 JSON 结构。"""
        prompt = self._build_system_prompt(target_type)
        clipped_text = text[:12000]
        user_prompt = (
            f"{task_hint}\n"
            f"target_type: {target_type or 'auto'}\n"
            f"source_payload: {json.dumps(source_payload, ensure_ascii=False)}\n"
            "请返回一个严格可解析的 JSON 对象，不要附带 markdown 代码块。\n"
            f"content:\n{clipped_text}"
        )
        raw = self.client.chat_completion(
            model=settings.siliconflow_text_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        result = self._parse_json_response(raw)
        result.setdefault("source_payload", source_payload)
        return self._normalize_output(result)

    @staticmethod
    def _build_system_prompt(target_type: str | None) -> str:
        """为不同目标类型生成结构化抽取提示词。"""
        schema_hint = TARGET_FIELDS.get(target_type or "", "meta_json 应尽量补齐适合当前内容类型的结构化字段。")
        return (
            "你是 Gist Research Workspace 的结构化信息抽取引擎。"
            "你的任务是把输入内容整理成适合 items 表和 meta_json 字段消费的 JSON。"
            "请始终返回如下顶层结构："
            '{'
            '"item_type":"paper|article|competition|insight|voice",'
            '"title":"string",'
            '"summary":"string",'
            '"tags":["string"],'
            '"meta_json":{},'
            '"content_md":"string 可为空"'
            "}"
            "规则："
            "1. 返回必须是合法 JSON；"
            "2. summary 用中文，简洁但可读，包含主要信息；"
            "3. tags 返回数组；"
            "4. content_md 如果无法可靠生成可返回空字符串；"
            "5. note 必须放进 meta_json，不要覆盖用户字段语义；"
            f"6. {schema_hint}"
        )

    @staticmethod
    def _normalize_output(payload: dict[str, Any]) -> dict[str, Any]:
        """把模型输出规范成前后端统一约定的字段结构。"""
        result = dict(payload)
        result["item_type"] = result.get("item_type") or "insight"
        result["title"] = result.get("title") or "未命名 AI 结果"
        result["summary"] = result.get("summary") or ""
        tags = result.get("tags") or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        result["tags"] = tags
        meta_json = result.get("meta_json") or {}
        if not isinstance(meta_json, dict):
            meta_json = {"raw_meta": meta_json}
        result["meta_json"] = meta_json
        result["content_md"] = result.get("content_md") or ""
        return result

    @staticmethod
    def _parse_json_response(raw: str) -> dict[str, Any]:
        """从模型响应文本中解析出合法 JSON 对象。"""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise RuntimeError("SiliconFlow returned a non-JSON response.")
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise RuntimeError("SiliconFlow returned invalid JSON.") from exc

    @staticmethod
    def _require_string(payload: dict[str, Any], key: str) -> str:
        """读取并校验输入载荷中的必填字符串字段。"""
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"input_payload.{key} is required.")
        return value.strip()

    @staticmethod
    def _resolve_media_url(payload: dict[str, Any], media_type: str) -> str:
        """把图片或其他媒体输入统一解析成可直接访问的 URL。"""
        direct_url = payload.get(f"{media_type}_url")
        if isinstance(direct_url, str) and direct_url.strip():
            return direct_url.strip()

        data_url = payload.get("data_url")
        if isinstance(data_url, str) and data_url.strip():
            return data_url.strip()

        base64_body = payload.get(f"{media_type}_base64")
        if isinstance(base64_body, str) and base64_body.strip():
            mime_type = payload.get("content_type") or f"{media_type}/png"
            return f"data:{mime_type};base64,{base64_body.strip()}"

        raise RuntimeError(f"{media_type} input requires {media_type}_url, data_url, or {media_type}_base64.")

    @staticmethod
    def _resolve_audio_bytes(payload: dict[str, Any]) -> bytes:
        """把音频输入统一解析成原始二进制字节。"""
        audio_url = payload.get("audio_url")
        if isinstance(audio_url, str) and audio_url.strip():
            response = httpx.get(audio_url.strip(), timeout=settings.siliconflow_request_timeout, follow_redirects=True)
            response.raise_for_status()
            return response.content

        data_url = payload.get("data_url")
        if isinstance(data_url, str) and data_url.startswith("data:"):
            _, encoded = data_url.split(",", 1)
            return base64.b64decode(encoded)

        audio_base64 = payload.get("audio_base64")
        if isinstance(audio_base64, str) and audio_base64.strip():
            return base64.b64decode(audio_base64.strip())

        raise RuntimeError("audio input requires audio_url, data_url, or audio_base64.")

    @staticmethod
    def _fetch_webpage(url: str) -> tuple[str | None, str]:
        """抓取网页并提取标题与可读纯文本正文。"""
        retries = max(settings.webpage_fetch_retries, 0)
        html = ""
        last_error: Exception | None = None

        for attempt in range(retries + 1):
            try:
                html = AITaskProcessor._download_webpage_html(url)
                break
            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt >= retries:
                    raise RuntimeError(
                        f"读取 URL 超时：{url}。目标网站响应较慢、页面过大或限制访问，请稍后重试，"
                        "或改用文本导入。"
                    ) from exc
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                raise RuntimeError(
                    f"读取 URL 失败：{url} 返回 HTTP {status_code}。目标网站可能拒绝访问、地址失效，"
                    "或当前链接不适合直接抓取网页正文。"
                ) from exc
            except httpx.RequestError as exc:
                raise RuntimeError(
                    f"读取 URL 失败：无法连接到 {url}。请检查链接是否可访问，或稍后重试。"
                ) from exc

        if not html and last_error is not None:
            raise RuntimeError(
                f"读取 URL 失败：{url}。请检查目标网页是否可访问。"
            ) from last_error

        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        page_title = unescape(title_match.group(1).strip()) if title_match else None

        cleaned = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<style.*?>.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<noscript.*?>.*?</noscript>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = unescape(cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned:
            raise RuntimeError("Fetched webpage does not contain readable text.")
        return page_title, cleaned[:15000]

    @staticmethod
    def _download_webpage_html(url: str) -> str:
        """以流式方式抓取网页，避免等待超大页面完整下载。"""
        timeout = httpx.Timeout(
            connect=settings.webpage_fetch_connect_timeout,
            read=settings.webpage_fetch_read_timeout,
            write=settings.webpage_fetch_connect_timeout,
            pool=settings.webpage_fetch_connect_timeout,
        )
        max_bytes = max(settings.webpage_fetch_max_bytes, 1)
        chunks: list[bytes] = []
        total_bytes = 0

        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers=WEBPAGE_FETCH_HEADERS,
        ) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "application/pdf" in content_type:
                    raise RuntimeError(
                        "目标 URL 返回的是 PDF 文件，当前 URL 解析仅支持网页正文抓取；"
                        "请先提取 PDF 文本后再走文本整理。"
                    )

                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    remaining = max_bytes - total_bytes
                    if remaining <= 0:
                        break
                    if len(chunk) > remaining:
                        chunks.append(chunk[:remaining])
                        total_bytes += remaining
                        break
                    chunks.append(chunk)
                    total_bytes += len(chunk)

                encoding = response.encoding or "utf-8"

        html = b"".join(chunks).decode(encoding, errors="ignore")
        if not html.strip():
            raise RuntimeError("Fetched webpage is empty.")
        return html

