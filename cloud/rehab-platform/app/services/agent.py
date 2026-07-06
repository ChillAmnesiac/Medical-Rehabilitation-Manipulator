from __future__ import annotations

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


def answer_patient_question(user: User, latest_report: TrainingReport | None, message: str) -> dict[str, object]:
    pain_score = latest_report.pain_score if latest_report is not None else None
    report_phrase = f"Your latest pain score {pain_score}/10 is in the low range" if pain_score is not None else "I do not have a recent pain score yet"
    answer = (
        f"{report_phrase}. For tomorrow, keep the session light, warm up first, and stop if pain increases or motion quality drops. "
        f"This guidance is based on your {user.rehab_stage or 'current'} rehab profile and recent training data."
    )
    return {
        "role": "rehab_therapist_agent",
        "answer": answer,
        "safety_scope": "education_and_plan_suggestion_only",
        "boundary": "The app and cloud agent never bypass M33 safety acceptance, preflight, or clinician limits.",
        "input_echo": message,
    }


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
