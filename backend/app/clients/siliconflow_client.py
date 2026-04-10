"""SiliconFlow 官方 API 客户端封装。"""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class SiliconFlowClient:
    def __init__(self) -> None:
        """初始化 SiliconFlow 客户端及公共请求参数。"""
        if not settings.siliconflow_api_key:
            raise RuntimeError("SILICONFLOW_API" \
            "_KEY is not configured.")

        self.base_url = settings.siliconflow_base_url.rstrip("/")
        self.timeout = settings.siliconflow_request_timeout
        self.headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
        }

    def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        response_format_json: bool = True,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """调用 SiliconFlow 文本/视觉模型完成对话补全。"""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format_json:
            payload["response_format"] = {"type": "json_object"}

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload,
            timeout=self.timeout,
        )
        self._raise_for_status(response, "chat completion")
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def transcribe_audio(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str | None = None,
        language: str | None = None,
    ) -> str:
        """调用 SiliconFlow 音频转写接口返回纯文本结果。"""
        files = {
            "file": (filename, audio_bytes, content_type or "application/octet-stream"),
        }
        data: dict[str, Any] = {"model": settings.siliconflow_audio_model}
        if language:
            data["language"] = language

        response = httpx.post(
            f"{self.base_url}/audio/transcriptions",
            headers=self.headers,
            data=data,
            files=files,
            timeout=self.timeout,
        )
        self._raise_for_status(response, "audio transcription")
        payload = response.json()
        text = payload.get("text")
        if not text:
            raise RuntimeError("SiliconFlow transcription returned an empty result.")
        return text

    @staticmethod
    def _raise_for_status(response: httpx.Response, action: str) -> None:
        """把非 2xx HTTP 响应统一转换成业务可读错误。"""
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(f"SiliconFlow {action} failed: {detail}") from exc

