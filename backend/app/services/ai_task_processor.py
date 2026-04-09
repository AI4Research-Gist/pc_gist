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


class AITaskProcessor:
    def __init__(self) -> None:
        self.client = SiliconFlowClient()

    def process(self, task: AITask) -> dict[str, Any]:
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
        text = self._require_string(task.input_payload, "text")
        target_type = task.input_payload.get("target_type")
        return self._structure_text(
            text=text,
            target_type=target_type,
            task_hint="这是用户直接提交的文本内容，请完成结构化整理。",
            source_payload={"source_type": "text"},
        )

    def _process_image_task(self, task: AITask) -> dict[str, Any]:
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
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"input_payload.{key} is required.")
        return value.strip()

    @staticmethod
    def _resolve_media_url(payload: dict[str, Any], media_type: str) -> str:
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
        response = httpx.get(
            url,
            timeout=settings.siliconflow_request_timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        html = response.text

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

