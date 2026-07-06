from __future__ import annotations

import json
from collections.abc import Callable

import httpx

from app.core.config import Settings
from app.models import TrainingReport, User


UNSAFE_MARKERS = (
    "bypass",
    "disable safety",
    "direct control",
    "directly control",
    "maximum torque",
    "override m33",
    "\u7ed5\u8fc7",
    "\u5173\u95ed\u5b89\u5168",
    "\u76f4\u63a5\u63a7\u5236",
    "\u6700\u5927\u626d\u77e9",
)


class CloudModelError(RuntimeError):
    """Raised when the configured external model cannot return a usable answer."""


CloudModelCaller = Callable[[Settings, list[dict[str, str]]], str]


def is_unsafe_motion_request(text: str) -> bool:
    normalized = text.casefold()
    return any(marker in normalized for marker in UNSAFE_MARKERS)


def build_rule_based_draft(
    user: User,
    latest_report: TrainingReport | None,
    input_text: str,
    app_context: dict[str, object] | None,
) -> dict[str, object]:
    app_context = app_context or {}
    pain_score = _number(app_context.get("pain_level"))
    if pain_score is None and latest_report is not None:
        pain_score = latest_report.pain_score
    pain_score = pain_score or 0

    movement_type = str(app_context.get("movement_type") or "elbow_flexion")
    completion_rate = latest_report.completion_rate if latest_report is not None else 0.0
    sets = 1 if pain_score >= 4 else 2
    reps = 6 if pain_score >= 4 else 8
    assist_level = 0.45 if completion_rate < 0.6 else 0.35
    speed_level = "very_slow" if pain_score >= 4 else "slow"
    generated_plan = {
        "title": "AI rehab draft",
        "goal": _goal_text(user, latest_report, input_text),
        "movement_type": movement_type,
        "sets": sets,
        "reps": reps,
        "assist_level": assist_level,
        "speed_level": speed_level,
        "target_angle_range": [0, 45],
    }
    risk_notes = [
        "M33 safety acceptance and preflight are required before any real movement.",
        "Stop and contact a clinician if pain rises sharply, numbness appears, or fatigue becomes unusual.",
    ]
    context_snapshot = {
        "profile": {
            "rehab_stage": user.rehab_stage,
            "affected_side": user.affected_side,
            "medical_constraints": _split_constraints(user.medical_constraints),
        },
        "latest_report": _report_context(latest_report),
        "app_context": app_context,
        "ai_planner": {
            "status": "fallback_rule_based",
            "model": None,
            "reason": "external_model_not_configured",
        },
    }
    return {
        "generated_plan": generated_plan,
        "risk_notes": risk_notes,
        "context_snapshot": context_snapshot,
    }


def call_openai_compatible_model(settings: Settings, messages: list[dict[str, str]]) -> str:
    url = settings.agent_model_base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"
    payload = {
        "model": settings.agent_model_name,
        "messages": messages,
        "temperature": settings.agent_model_temperature,
        "max_tokens": settings.agent_model_max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.agent_model_api_key}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=settings.agent_model_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise CloudModelError("cloud_model_unavailable") from exc

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise CloudModelError("cloud_model_invalid_response") from exc
    answer = str(content or "").strip()
    if not answer:
        raise CloudModelError("cloud_model_empty_response")
    return answer


def answer_patient_question(
    user: User,
    latest_report: TrainingReport | None,
    message: str,
    settings: Settings | None = None,
    cloud_model_caller: CloudModelCaller = call_openai_compatible_model,
) -> dict[str, object]:
    if settings is not None and _cloud_model_configured(settings):
        try:
            answer = cloud_model_caller(settings, _agent_messages(user, latest_report, message))
            return _agent_response(
                message,
                answer,
                {
                    "mode": "cloud_model",
                    "configured": True,
                    "provider": settings.agent_model_provider,
                    "model": settings.agent_model_name,
                },
            )
        except CloudModelError:
            model_status = {
                "mode": "fallback_rule_based",
                "configured": True,
                "provider": settings.agent_model_provider,
                "model": settings.agent_model_name,
                "fallback_reason": "cloud_model_unavailable",
            }
            return _agent_response(message, _rule_based_patient_answer(user, latest_report), model_status)

    model_status = {
        "mode": "fallback_rule_based",
        "configured": False,
        "provider": settings.agent_model_provider if settings is not None else "openai_compatible",
        "model": settings.agent_model_name if settings is not None else None,
        "fallback_reason": "external_model_not_configured",
    }
    return _agent_response(message, _rule_based_patient_answer(user, latest_report), model_status)


def _agent_response(message: str, answer: str, model_status: dict[str, object]) -> dict[str, object]:
    return {
        "role": "rehab_therapist_agent",
        "answer": answer,
        "safety_scope": "education_and_plan_suggestion_only",
        "boundary": "我可以解释训练和报告，并给出康复建议；真正开始训练前仍需要设备安全系统确认。",
        "input_echo": message,
        "model_status": model_status,
    }


def _rule_based_patient_answer(user: User, latest_report: TrainingReport | None) -> str:
    pain_score = latest_report.pain_score if latest_report is not None else None
    if pain_score is None:
        report_phrase = "我还没有读到最近一次疼痛评分"
    else:
        report_phrase = f"你最近一次疼痛评分是 {pain_score}/10"
    stage = user.rehab_stage or "当前"
    return (
        f"{report_phrase}。下一次训练建议先保持低强度热身，动作质量稳定再逐步增加；"
        f"如果疼痛升高、麻木或疲劳异常，请暂停并联系康复师。这个建议基于你的 {stage} 档案和云端训练记录。"
    )


def _cloud_model_configured(settings: Settings) -> bool:
    return bool(settings.agent_model_base_url and settings.agent_model_api_key and settings.agent_model_name)


def _agent_messages(user: User, latest_report: TrainingReport | None, message: str) -> list[dict[str, str]]:
    context = {
        "profile": {
            "rehab_stage": user.rehab_stage,
            "affected_side": user.affected_side,
            "medical_constraints": _split_constraints(user.medical_constraints),
        },
        "latest_report": _report_context(latest_report),
        "patient_message": message,
    }
    return [
        {
            "role": "system",
            "content": (
                "你是一名谨慎的康复师，只回答康复教育、训练建议和报告解释。"
                "不要给出诊断，不要承诺疗效，不要输出设备直控或绕过安全系统的指令。"
                "回答要简短、中文、面向患者。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(context, ensure_ascii=False, separators=(",", ":")),
        },
    ]


def _goal_text(user: User, latest_report: TrainingReport | None, input_text: str) -> str:
    if latest_report is None:
        return f"{input_text} Keep the first session conservative for {user.rehab_stage or 'the current stage'}."
    percent = int(latest_report.completion_rate * 100)
    return f"{input_text} Last session completion was {percent}%, so keep intensity controlled."


def _report_context(report: TrainingReport | None) -> dict[str, object] | None:
    if report is None:
        return None
    return {
        "id": str(report.id),
        "pain_score": report.pain_score,
        "fatigue_score": report.fatigue_score,
        "completion_rate": report.completion_rate,
        "safety_level": report.safety_level,
    }


def _split_constraints(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _number(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
