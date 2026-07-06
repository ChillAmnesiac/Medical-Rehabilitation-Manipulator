#!/usr/bin/env python3
"""Smoke-test a rehab agent model provider before saving it to staging.

This tool calls the model provider directly and never prints the API key.
Use it before running configure_rehab_model_relay.py so an invalid key/model
does not get persisted into the cloud app configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Callable
from urllib.parse import quote


DEFAULT_PROVIDER_BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta",
    "google_gemini": "https://generativelanguage.googleapis.com/v1beta",
}
OPENAI_COMPATIBLE_PROVIDERS = {"openai", "openai_compatible", "openai-compatible"}
GEMINI_PROVIDERS = {"gemini", "google_gemini", "google-gemini"}
UrlOpener = Callable[..., Any]


def require_text(name: str, value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def normalize_provider(provider: str) -> str:
    normalized = require_text("provider", provider).casefold()
    if normalized in OPENAI_COMPATIBLE_PROVIDERS:
        return "openai_compatible"
    if normalized in GEMINI_PROVIDERS:
        return "gemini"
    raise ValueError(f"unsupported provider: {provider}")


def provider_base_url(provider: str, base_url: str | None) -> str:
    normalized = normalize_provider(provider)
    default_base_url = DEFAULT_PROVIDER_BASE_URLS.get(normalized)
    return require_text("base_url", (base_url or "").strip() or default_base_url).rstrip("/")


def summarize_request(provider: str, base_url: str, model: str, api_key: str) -> dict[str, Any]:
    return {
        "provider": normalize_provider(provider),
        "base_url": base_url,
        "model": require_text("model", model),
        "api_key": "<redacted>" if api_key else None,
    }


def gemini_generate_content_url(base_url: str, model: str) -> str:
    if base_url.endswith(":generateContent"):
        return base_url
    return f"{base_url}/models/{quote(model, safe='')}:generateContent"


def openai_chat_completions_url(base_url: str) -> str:
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def build_gemini_payload(message: str) -> dict[str, Any]:
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 256,
        },
        "system_instruction": {
            "parts": [
                {
                    "text": (
                        "You are a cautious rehabilitation therapist. Only answer rehabilitation education, "
                        "training suggestions, and report interpretation. Do not diagnose, promise outcomes, "
                        "or provide direct device-control or safety-bypass instructions."
                    )
                }
            ]
        },
    }


def build_openai_compatible_payload(model: str, message: str) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
        "temperature": 0.2,
        "max_tokens": 256,
    }


def post_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
    opener: UrlOpener,
) -> tuple[int, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with opener(request, timeout=timeout) as response:
            return response.status, parse_body(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, parse_body(exc.read())


def parse_body(raw: bytes) -> Any:
    text = raw.decode("utf-8", errors="replace")
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def parse_gemini_answer(body: Any) -> str:
    try:
        parts = body["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return ""
    return "".join(str(part.get("text") or "") for part in parts if isinstance(part, dict)).strip()


def parse_openai_compatible_answer(body: Any) -> str:
    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""
    return str(content or "").strip()


def answer_preview(answer: str, limit: int = 120) -> str:
    text = " ".join(answer.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def run(args: argparse.Namespace, opener: UrlOpener = urllib.request.urlopen) -> tuple[int, dict[str, Any]]:
    provider = normalize_provider(args.provider)
    base_url = provider_base_url(provider, args.base_url)
    model = require_text("model", args.model)
    api_key = require_text("api_key", args.api_key)
    message = require_text("message", args.message)
    timeout = int(args.timeout)

    if provider == "gemini":
        url = gemini_generate_content_url(base_url, model)
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-goog-api-key": api_key,
        }
        payload = build_gemini_payload(message)
        parse_answer = parse_gemini_answer
    else:
        url = openai_chat_completions_url(base_url)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = build_openai_compatible_payload(model, message)
        parse_answer = parse_openai_compatible_answer

    status_code, body = post_json(url, headers, payload, timeout, opener)
    answer = parse_answer(body)
    ok = 200 <= status_code < 300 and bool(answer)
    summary = {
        "request": summarize_request(provider, base_url, model, api_key),
        "status_code": status_code,
        "status": "ok" if ok else ("provider_http_error" if status_code >= 400 else "provider_invalid_response"),
        "answer_present": bool(answer),
        "answer_preview": answer_preview(answer),
    }
    return (0 if ok else 3), summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default=os.getenv("REHAB_MODEL_RELAY_PROVIDER", "openai_compatible"))
    parser.add_argument("--base-url", default=os.getenv("REHAB_MODEL_RELAY_BASE_URL"))
    parser.add_argument("--model", default=os.getenv("REHAB_MODEL_RELAY_MODEL"))
    parser.add_argument("--api-key", default=os.getenv("REHAB_MODEL_RELAY_API_KEY"))
    parser.add_argument("--message", default=os.getenv("REHAB_MODEL_SMOKE_MESSAGE"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        exit_code, summary = run(parse_args(argv))
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
