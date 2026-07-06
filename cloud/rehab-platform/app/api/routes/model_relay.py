from __future__ import annotations

from pathlib import Path
from re import fullmatch

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_settings, require_current_user
from app.core.config import Settings
from app.models import User
from app.schemas import ModelRelayConfigRequest

router = APIRouter(prefix="/api/rehab-arm/v1/projects", tags=["rehab-model-relay"])

DEFAULT_PROVIDER_BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta",
    "google_gemini": "https://generativelanguage.googleapis.com/v1beta",
}
OPENAI_COMPATIBLE_PROVIDERS = {"openai", "openai_compatible", "openai-compatible"}
GEMINI_PROVIDERS = {"gemini", "google_gemini", "google-gemini"}


@router.put("/{project_id}/model-relay/config")
def configure_model_relay(
    project_id: str,
    request: ModelRelayConfigRequest,
    _user: User = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    provider = _normalize_provider(request.provider)
    base_url = _provider_base_url(provider, request.base_url)
    model = _require_text("model", request.model)
    api_key = _require_text("api_key", request.api_key)

    settings.agent_model_provider = provider
    settings.agent_model_base_url = base_url
    settings.agent_model_name = model
    settings.agent_model_api_key = api_key if request.external_enabled else None
    _persist_model_env(settings)

    return {
        "data": {
            "project_id": project_id,
            "config": {
                "provider": provider,
                "base_url": base_url,
                "model": model,
                "external_enabled": request.external_enabled,
                "api_key": "<redacted>" if request.external_enabled else None,
            },
            "model_readiness": _agent_model_readiness(settings),
        }
    }


def _normalize_provider(provider: str) -> str:
    normalized = _require_text("provider", provider).casefold()
    if normalized in OPENAI_COMPATIBLE_PROVIDERS:
        return "openai_compatible"
    if normalized in GEMINI_PROVIDERS:
        return "gemini"
    raise HTTPException(
        status_code=400,
        detail={"code": "MODEL_PROVIDER_UNSUPPORTED", "message": "Unsupported model provider."},
    )


def _provider_base_url(provider: str, base_url: str | None) -> str:
    default_base_url = DEFAULT_PROVIDER_BASE_URLS.get(provider)
    return _require_text("base_url", (base_url or "").strip() or default_base_url).rstrip("/")


def _require_text(name: str, value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail={"code": "MODEL_RELAY_FIELD_REQUIRED", "message": f"{name} is required.", "field": name},
        )
    return text


def _agent_model_readiness(settings: Settings) -> dict[str, object]:
    configured = bool(
        (settings.agent_model_base_url or "").strip()
        and (settings.agent_model_api_key or "").strip()
        and (settings.agent_model_name or "").strip()
    )
    if configured:
        return {
            "mode": "cloud_model_configured",
            "configured": True,
            "provider": settings.agent_model_provider,
            "model": settings.agent_model_name,
            "reason": None,
        }
    return {
        "mode": "fallback_rule_based",
        "configured": False,
        "provider": settings.agent_model_provider,
        "model": None,
        "reason": "external_model_not_configured",
    }


def _persist_model_env(settings: Settings) -> None:
    env_path = Path(settings.runtime_env_path)
    existing_lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    updates = {
        "AGENT_MODEL_PROVIDER": settings.agent_model_provider,
        "AGENT_MODEL_BASE_URL": settings.agent_model_base_url,
        "AGENT_MODEL_NAME": settings.agent_model_name,
        "AGENT_MODEL_API_KEY": settings.agent_model_api_key or "",
    }
    rendered: list[str] = []
    seen: set[str] = set()
    for line in existing_lines:
        key = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else ""
        if key in updates:
            rendered.append(f"{key}={_env_value(str(updates[key]))}")
            seen.add(key)
        else:
            rendered.append(line)
    for key, value in updates.items():
        if key not in seen:
            rendered.append(f"{key}={_env_value(str(value))}")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text("\n".join(rendered).rstrip() + "\n", encoding="utf-8")


def _env_value(value: str) -> str:
    if value == "":
        return ""
    if fullmatch(r"[A-Za-z0-9_./:\-]+", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
