import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_settings, require_current_user
from app.core.config import Settings
from app.models import (
    AiTrainingDraft,
    BleMessage,
    Device,
    LegacySppInbound,
    PhoneVerification,
    TrainingPlan,
    TrainingReport,
    TrainingSession,
    User,
)
from app.schemas import (
    AgentMessageRequest,
    AiTrainingDraftGenerateRequest,
    BleMessageRequest,
    DeviceBindRequest,
    LegacySppInboundRequest,
    PlanSyncRequest,
    PhoneVerificationConfirmRequest,
    PhoneVerificationStartRequest,
    ProfileUpdateRequest,
    TrainingSessionCreateRequest,
    WorkflowActionRequest,
)
from app.services.agent import answer_patient_question, build_rule_based_draft, is_unsafe_motion_request
from app.models import utcnow
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/rehab-arm/app/v1", tags=["rehab-app"])


def _phone_delivery_status(settings: Settings) -> dict[str, object]:
    if settings.phone_verification_debug_code_enabled:
        return {
            "mode": "debug_sms",
            "configured": False,
            "provider": None,
            "exposes_debug_code": True,
            "reason": "debug_code_enabled",
        }

    provider = settings.phone_verification_sms_provider
    webhook_url = settings.phone_verification_sms_webhook_url
    if provider and webhook_url:
        return {
            "mode": "sms",
            "configured": True,
            "provider": provider,
            "exposes_debug_code": False,
        }

    return {
        "mode": "sms_unconfigured",
        "configured": False,
        "provider": provider,
        "exposes_debug_code": False,
        "reason": "sms_provider_not_configured",
    }


@router.get("/public-config")
def get_public_config(settings: Settings = Depends(get_settings)):
    return {
        "data": {
            "app_name": settings.app_name,
            "rehab_app": {
                "catalog_endpoint": "/api/rehab-arm/app/v1/catalog",
                "workflow_endpoint": "/api/rehab-arm/app/v1/me/workflow",
                "agent_message_endpoint": "/api/rehab-arm/app/v1/agent/messages",
            },
            "phone_verification": {
                "start_endpoint": "/api/rehab-arm/app/v1/account/phone-verifications",
                "confirm_endpoint_template": (
                    "/api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm"
                ),
                "delivery_status": _phone_delivery_status(settings),
            },
            "m33_legacy_spp_profile": _m33_legacy_spp_profile(),
            "safety_boundary": "Cloud suggests plans only. M33 remains final motion authority.",
        }
    }


@router.get("/catalog")
def get_catalog():
    return {
        "data": {
            "training_movements": [
                {
                    "code": "elbow_flexion",
                    "label": "\u8098\u5173\u8282\u5c48\u4f38",
                    "default_sets": 2,
                    "default_reps": 8,
                    "target_angle_range": {"min_deg": 0, "max_deg": 45},
                },
                {
                    "code": "grip",
                    "label": "\u6293\u63e1\u8bad\u7ec3",
                    "default_sets": 2,
                    "default_reps": 8,
                    "target_angle_range": {"min_deg": 0, "max_deg": 30},
                },
                {
                    "code": "wrist_extension",
                    "label": "\u8155\u5173\u8282\u80cc\u4f38",
                    "default_sets": 1,
                    "default_reps": 6,
                    "target_angle_range": {"min_deg": 0, "max_deg": 25},
                },
            ],
            "fatigue_levels": ["low", "medium", "high"],
            "m33_legacy_spp_profile": _m33_legacy_spp_profile(),
        }
    }


@router.get("/me")
def get_mobile_bootstrap(
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    devices = list(db.scalars(select(Device).where(Device.owner_id == user.id)).all())
    reports = list(
        db.scalars(
            select(TrainingReport)
            .where(TrainingReport.owner_id == user.id)
            .order_by(TrainingReport.created_at.desc(), TrainingReport.id.desc())
            .limit(10)
        ).all()
    )
    plans = list(
        db.scalars(
            select(TrainingPlan)
            .where(TrainingPlan.owner_id == user.id)
            .order_by(TrainingPlan.created_at.desc(), TrainingPlan.id.desc())
            .limit(10)
        ).all()
    )
    latest_open_draft = db.scalar(
        select(AiTrainingDraft)
        .where(AiTrainingDraft.owner_id == user.id, AiTrainingDraft.accepted_plan_id.is_(None))
        .order_by(AiTrainingDraft.created_at.desc(), AiTrainingDraft.id.desc())
        .limit(1)
    )
    return {"data": build_mobile_bootstrap(user, devices, reports, plans, latest_open_draft)}


@router.get("/me/workflow")
def get_workflow(
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    return {"data": _workflow_for_user(db, user.id)}


@router.post("/me/workflow/actions")
def execute_workflow_action(
    request: WorkflowActionRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    workflow = _workflow_for_user(db, user.id)
    return {
        "data": {
            "accepted": True,
            "action_code": request.action_code,
            "payload": request.payload or {},
            "workflow": workflow,
            "safety_boundary": "Workflow actions update app state only; M33 remains final motion authority.",
        }
    }


@router.post("/account/phone-verifications")
def start_phone_verification(
    request: PhoneVerificationStartRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    phone = _normalize_phone(request.phone)
    purpose = request.purpose or "bind_account"
    if purpose != "bind_account":
        raise HTTPException(
            status_code=400,
            detail={"code": "PHONE_PURPOSE_UNSUPPORTED", "message": "Unsupported phone verification purpose"},
        )
    code = _debug_phone_code(phone)
    verification = PhoneVerification(
        owner_id=user.id,
        phone=phone,
        purpose=purpose,
        code_hash=hash_password(code),
        expires_at=utcnow() + timedelta(seconds=settings.phone_verification_ttl_seconds),
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    payload = {
        "verification_id": str(verification.id),
        "masked_phone": _mask_phone(phone),
        "expires_in": settings.phone_verification_ttl_seconds,
        "delivery_channel": "debug_sms" if settings.phone_verification_debug_code_enabled else "sms",
    }
    if settings.phone_verification_debug_code_enabled:
        payload["debug_code"] = code
    return {"data": payload}


@router.post("/account/phone-verifications/{verification_id}/confirm")
def confirm_phone_verification(
    verification_id: int,
    request: PhoneVerificationConfirmRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    verification = db.get(PhoneVerification, verification_id)
    now = utcnow()
    if (
        verification is None
        or verification.owner_id != user.id
        or verification.consumed_at is not None
        or _as_aware_utc(verification.expires_at) < now
    ):
        raise HTTPException(
            status_code=400,
            detail={"code": "PHONE_CODE_INVALID", "message": "Phone verification code is invalid or expired"},
        )
    if verification.attempts >= settings.phone_verification_max_attempts:
        raise HTTPException(
            status_code=400,
            detail={"code": "PHONE_CODE_ATTEMPTS_EXCEEDED", "message": "Phone verification attempts exceeded"},
        )
    verification.attempts += 1
    if not verify_password(request.code.strip(), verification.code_hash):
        db.add(verification)
        db.commit()
        if verification.attempts >= settings.phone_verification_max_attempts:
            raise HTTPException(
                status_code=400,
                detail={"code": "PHONE_CODE_ATTEMPTS_EXCEEDED", "message": "Phone verification attempts exceeded"},
            )
        raise HTTPException(
            status_code=400,
            detail={"code": "PHONE_CODE_INVALID", "message": "Phone verification code is invalid or expired"},
        )
    user.phone = verification.phone
    user.phone_verified_at = now
    verification.consumed_at = now
    db.add(user)
    db.add(verification)
    db.commit()
    db.refresh(user)
    return {"data": {"profile": build_mobile_bootstrap(user)["profile"]}}


@router.put("/me/profile")
def update_profile(
    request: ProfileUpdateRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    if request.name is not None:
        user.name = request.name.strip() or "\u5eb7\u590d\u7528\u6237"
    if request.phone is not None:
        user.phone = request.phone.strip() or None
    if request.rehab_stage is not None:
        user.rehab_stage = request.rehab_stage.strip()
    if request.affected_side is not None:
        user.affected_side = request.affected_side.strip()
    if request.medical_constraints is not None:
        user.medical_constraints = ";".join(item.strip() for item in request.medical_constraints if item.strip())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"data": {"profile": build_mobile_bootstrap(user)["profile"]}}


@router.post("/devices/bind")
def bind_device(
    request: DeviceBindRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    devices_with_same_hardware_id = list(
        db.scalars(
            select(Device)
            .where(Device.m33_device_id == request.m33_device_id)
            .order_by(Device.created_at.asc(), Device.id.asc())
        ).all()
    )
    device = next((existing for existing in devices_with_same_hardware_id if existing.owner_id == user.id), None)
    if device is None and devices_with_same_hardware_id:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "DEVICE_ALREADY_BOUND",
                "message": "This rehab device is already bound to another account.",
            },
        )
    if device is None:
        device = Device(owner_id=user.id, m33_device_id=request.m33_device_id)
    device.ble_name = request.ble_name or request.m33_device_id
    device.trust_status = request.trust_status or "trusted"
    device.firmware_version = request.firmware_version or device.firmware_version or ""
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"data": device_to_dict(device)}


@router.post("/devices/{device_id}/legacy-spp/inbound")
def record_legacy_spp_inbound(
    device_id: int,
    request: LegacySppInboundRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    device = db.get(Device, device_id)
    if device is None or device.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"},
        )
    parsed = _parse_raw_text(request.raw_text)
    record = LegacySppInbound(
        device_id=device.id,
        owner_id=user.id,
        raw_text=request.raw_text,
        parsed_json=json.dumps(parsed, ensure_ascii=False) if parsed is not None else "",
        related_message_id=request.related_message_id or "",
        transport_event_json=json.dumps(request.transport_event or {}, ensure_ascii=False),
        status="matched" if parsed is not None else "stored",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "data": {
            "id": str(record.id),
            "device_id": str(device.id),
            "status": record.status,
            "raw_text": record.raw_text,
            "parsed": parsed,
            "related_message_id": record.related_message_id,
        }
    }


@router.post("/training-sessions")
def create_training_session(
    request: TrainingSessionCreateRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    device = _get_owned_device(db, user.id, request.device_id)
    completion_rate = _calculate_completion_rate(request.completed_movements, request.target_movements)
    session = TrainingSession(
        owner_id=user.id,
        device_id=device.id,
        plan_id=request.plan_id or "",
        status="completed",
        duration_seconds=request.duration_seconds,
        completed_movements=request.completed_movements,
        target_movements=request.target_movements,
        completion_rate=completion_rate,
        pain_score=request.pain_score,
        fatigue_score=request.fatigue_score,
        emg_summary_json=json.dumps(request.emg_summary or {}, ensure_ascii=False),
        notes=request.notes or "",
    )
    db.add(session)
    db.flush()
    report = TrainingReport(
        owner_id=user.id,
        session_id=session.id,
        title="Daily rehab session",
        summary=_report_summary(request.completed_movements, request.target_movements, request.pain_score),
        safety_level=_safety_level(request.pain_score, request.fatigue_score),
        pain_score=request.pain_score,
        fatigue_score=request.fatigue_score,
        completion_rate=completion_rate,
    )
    db.add(report)
    db.commit()
    db.refresh(session)
    db.refresh(report)
    return {"data": {"session": session_to_dict(session), "report": report_to_dict(report)}}


@router.get("/training-sessions/recent")
def list_recent_training_sessions(
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    sessions = list(
        db.scalars(
            select(TrainingSession)
            .where(TrainingSession.owner_id == user.id)
            .order_by(TrainingSession.created_at.desc(), TrainingSession.id.desc())
            .limit(20)
        ).all()
    )
    return {"data": {"sessions": [session_to_dict(session) for session in sessions]}}


@router.post("/ai-training-drafts/generate")
def generate_ai_training_draft(
    request: AiTrainingDraftGenerateRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    if is_unsafe_motion_request(request.input_text):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "UNSAFE_MOTION_REQUEST",
                "message": "The cloud agent cannot bypass device safety or issue direct motor commands.",
            },
        )
    latest_report = _latest_report(db, user.id)
    draft_payload = build_rule_based_draft(user, latest_report, request.input_text, request.context_snapshot)
    draft = AiTrainingDraft(
        owner_id=user.id,
        input_text=request.input_text,
        generated_plan_json=json.dumps(draft_payload["generated_plan"], ensure_ascii=False),
        risk_notes_json=json.dumps(draft_payload["risk_notes"], ensure_ascii=False),
        context_snapshot_json=json.dumps(draft_payload["context_snapshot"], ensure_ascii=False),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return {"data": draft_to_dict(draft)}


@router.post("/ai-training-drafts/{draft_id}/accept")
def accept_ai_training_draft(
    draft_id: int,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    draft = db.get(AiTrainingDraft, draft_id)
    if draft is None or draft.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail={"code": "AI_DRAFT_NOT_FOUND", "message": "AI training draft not found"},
        )
    if draft.accepted_plan_id is not None:
        plan = db.get(TrainingPlan, draft.accepted_plan_id)
        if plan is not None and plan.owner_id == user.id:
            return {"data": training_plan_to_dict(plan)}

    generated_plan = _json_loads(draft.generated_plan_json, {})
    plan = TrainingPlan(
        owner_id=user.id,
        source_draft_id=draft.id,
        source="ai_draft",
        title=str(generated_plan.get("title") or "AI rehab draft"),
        goal=str(generated_plan.get("goal") or ""),
        movement_type=str(generated_plan.get("movement_type") or "elbow_flexion"),
        sets=_int(generated_plan.get("sets"), 1),
        reps=_int(generated_plan.get("reps"), 6),
        assist_level=_float(generated_plan.get("assist_level"), 0.4),
        speed_level=str(generated_plan.get("speed_level") or "slow"),
        target_angle_range_json=json.dumps(generated_plan.get("target_angle_range") or [], ensure_ascii=False),
        risk_notes_json=draft.risk_notes_json,
        device_sync_status="not_synced",
        m33_status="pending",
    )
    db.add(plan)
    db.flush()
    draft.accepted_plan_id = plan.id
    db.add(draft)
    db.commit()
    db.refresh(plan)
    return {"data": training_plan_to_dict(plan)}


@router.post("/agent/messages")
def create_agent_message(
    request: AgentMessageRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if is_unsafe_motion_request(request.message):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "UNSAFE_MOTION_REQUEST",
                "message": "The rehab agent can educate and suggest plans, but cannot issue direct motion commands.",
            },
        )
    return {"data": answer_patient_question(user, _latest_report(db, user.id), request.message, settings=settings)}


@router.post("/training-plans/{plan_id}/sync-to-device")
def sync_training_plan_to_device(
    plan_id: int,
    request: PlanSyncRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    plan = _get_owned_plan(db, user.id, plan_id)
    device = _get_owned_device(db, user.id, request.device_id)
    plan.device_sync_status = "synced"
    plan.m33_status = "pending"
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return {
        "data": {
            "status": "queued_for_m33_acceptance",
            "plan": training_plan_to_dict(plan),
            "device": device_to_dict(device),
            "safety_boundary": "Plan sync is transport preparation only; M33 must accept before motion.",
        }
    }


@router.post("/devices/{device_id}/ble/messages")
def create_ble_message(
    device_id: int,
    request: BleMessageRequest,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    device = db.get(Device, device_id)
    if device is None or device.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"},
        )
    plan = _get_owned_plan(db, user.id, int(request.plan_id)) if request.plan_id else None
    frame_json = _legacy_frame_json(request.message_type, plan, request.payload or {})
    payload = {
        "legacy_transport_frame": {
            "sendable": True,
            "wire_text": json.dumps(frame_json, ensure_ascii=False, separators=(",", ":")) + "\n",
            "json": frame_json,
            "control_boundary": "Phone transports this frame only; M33 is the final safety authority.",
        }
    }
    message = BleMessage(
        owner_id=user.id,
        device_id=device.id,
        plan_id=plan.id if plan is not None else None,
        message_type=request.message_type,
        payload_json=json.dumps(payload, ensure_ascii=False),
        status="queued",
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return {"data": ble_message_to_dict(message)}


@router.get("/emg/latest")
def get_latest_emg(
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    records = list(
        db.scalars(
            select(LegacySppInbound)
            .where(LegacySppInbound.owner_id == user.id)
            .order_by(LegacySppInbound.created_at.desc(), LegacySppInbound.id.desc())
            .limit(20)
        ).all()
    )
    for record in records:
        parsed = _json_loads(record.parsed_json, None)
        if isinstance(parsed, dict) and ("emg" in parsed or parsed.get("type") == "sensor"):
            return {
                "data": {
                    "source": "legacy_spp_inbound",
                    "device_id": str(record.device_id),
                    "sample": parsed,
                    "created_at": record.created_at.isoformat(),
                }
            }
    raise HTTPException(
        status_code=404,
        detail={"code": "EMG_NOT_FOUND", "message": "No EMG sample has been uploaded yet"},
    )


def build_mobile_bootstrap(
    user: User,
    devices: list[Device] | None = None,
    reports: list[TrainingReport] | None = None,
    plans: list[TrainingPlan] | None = None,
    latest_open_draft: AiTrainingDraft | None = None,
) -> dict[str, object]:
    device_payloads = [device_to_dict(device) for device in (devices or [])]
    report_payloads = [report_to_dict(report) for report in (reports or [])]
    plan_payloads = [training_plan_to_dict(plan) for plan in (plans or [])]
    draft_payload = draft_to_dict(latest_open_draft) if latest_open_draft is not None else None
    latest_report = report_payloads[0] if report_payloads else None
    if plan_payloads:
        next_action = {
            "code": "sync_plan",
            "label": "\u540c\u6b65\u8bad\u7ec3\u8ba1\u5212",
            "title": "\u540c\u6b65\u8bad\u7ec3\u8ba1\u5212",
        }
        readiness_status = "needs_device_sync"
        readiness_summary = "\u8bad\u7ec3\u8ba1\u5212\u5df2\u751f\u6210\uff0c\u8bf7\u540c\u6b65\u8bbe\u5907\u5e76\u7b49\u5f85 M33 \u786e\u8ba4\u3002"
    elif draft_payload:
        next_action = {
            "code": "accept_ai_plan",
            "label": "\u63a5\u53d7 AI \u8bad\u7ec3\u8349\u7a3f",
            "title": "\u63a5\u53d7 AI \u8bad\u7ec3\u8349\u7a3f",
        }
        readiness_status = "needs_plan_acceptance"
        readiness_summary = "\u5df2\u751f\u6210 AI \u8bad\u7ec3\u8349\u7a3f\uff0c\u63a5\u53d7\u540e\u624d\u80fd\u540c\u6b65\u8bbe\u5907\u3002"
    elif latest_report:
        next_action = {
            "code": "review_report",
            "label": "\u67e5\u770b\u8bad\u7ec3\u62a5\u544a",
            "title": "\u590d\u76d8\u4eca\u65e5\u8bad\u7ec3",
        }
        readiness_status = "ready"
        readiness_summary = "\u8bad\u7ec3\u5df2\u4fdd\u5b58\uff0c\u8bf7\u5148\u67e5\u770b\u62a5\u544a\u518d\u5f00\u59cb\u4e0b\u4e00\u6b65\u3002"
    elif device_payloads:
        next_action = {
            "code": "generate_plan",
            "label": "\u751f\u6210\u4eca\u65e5\u8bad\u7ec3\u5efa\u8bae",
            "title": "\u751f\u6210\u4eca\u65e5\u8bad\u7ec3\u5efa\u8bae",
        }
        readiness_status = "needs_plan"
        readiness_summary = "\u5df2\u7ed1\u5b9a\u8bbe\u5907\uff0c\u7b49\u5f85\u751f\u6210\u8bad\u7ec3\u8ba1\u5212\u3002"
    else:
        next_action = {
            "code": "bind_device",
            "label": "\u7ed1\u5b9a\u5eb7\u590d\u8bbe\u5907",
            "title": "\u7ed1\u5b9a\u5eb7\u590d\u8bbe\u5907",
        }
        readiness_status = "needs_device"
        readiness_summary = "\u5df2\u767b\u5f55\uff0c\u7b49\u5f85\u7ed1\u5b9a\u53ef\u4fe1\u5eb7\u590d\u8bbe\u5907\u3002"
    profile = {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone or "",
        "phone_verified": user.phone_verified_at is not None,
        "name": user.name or "\u5eb7\u590d\u7528\u6237",
        "role": user.role,
        "rehab_stage": user.rehab_stage or "",
        "affected_side": user.affected_side or "",
        "medical_constraints": _split_constraints(user.medical_constraints),
    }
    patient_view = _patient_view_for_mobile(
        profile=profile,
        devices=device_payloads,
        readiness_status=readiness_status,
        next_action=next_action,
        latest_report=latest_report,
        plans=plan_payloads,
        draft=draft_payload,
    )
    return {
        "profile": profile,
        "patient_view": patient_view,
        "devices": device_payloads,
        "training_plans": plan_payloads,
        "training_reports": report_payloads,
        "latest_report": latest_report,
        "latest_open_ai_draft": draft_payload,
        "care_timeline": {
            "items": _timeline_items(report_payloads, plan_payloads, draft_payload),
        },
        "daily_action_guide": {
            "summary": readiness_summary,
            "next_action": next_action,
        },
        "mobile_readiness_guide": {
            "status": readiness_status,
            "summary": readiness_summary,
            "next_action": next_action,
        },
    }


def _patient_view_for_mobile(
    profile: dict[str, object],
    devices: list[dict[str, object]],
    readiness_status: str,
    next_action: dict[str, object],
    latest_report: dict[str, object] | None,
    plans: list[dict[str, object]],
    draft: dict[str, object] | None,
) -> dict[str, object]:
    display_name = _patient_text(str(profile.get("name") or "康复用户"))
    phone = str(profile.get("phone") or "")
    phone_verified = profile.get("phone_verified") is True
    medical_items = [_patient_text(str(item)) for item in profile.get("medical_constraints") or []]
    device_bound = bool(devices)
    primary_action = _patient_primary_action(next_action)

    facts = [
        {"label": "账号", "value": "已登录"},
        {"label": "手机号", "value": "已验证" if phone_verified else "待绑定"},
        {"label": "设备", "value": "已绑定" if device_bound else "待绑定"},
    ]
    if latest_report:
        completion_rate = latest_report.get("completion_rate")
        if isinstance(completion_rate, (int, float)):
            facts.append({"label": "上次训练", "value": f"完成 {int(completion_rate * 100)}%"})
    elif plans:
        facts.append({"label": "训练建议", "value": "待同步"})
    elif draft:
        facts.append({"label": "训练建议", "value": "待确认"})

    device_status_text = "设备已绑定" if device_bound else "等待绑定康复设备"
    device_primary_action = (
        {"label": "查看设备状态", "route": "device.html", "code": "view_device"}
        if device_bound
        else {"label": "绑定康复设备", "route": "device.html", "code": "bind_device"}
    )

    return {
        "home": {
            "greeting": f"{display_name}，今天按步骤来",
            "summary": _patient_readiness_summary(readiness_status),
            "primary_action": primary_action,
            "facts": facts,
            "safety_state": "训练开始前，设备安全系统会再次确认。",
            "ask_therapist": {"label": "问康复师", "route": "ai-plan.html"},
        },
        "profile": {
            "title": "我的康复档案",
            "display_name": display_name,
            "account": {"email": str(profile.get("email") or ""), "role": "康复用户"},
            "phone": {
                "label": "手机号",
                "verified": phone_verified,
                "value": _mask_phone(phone) if phone else "待绑定",
                "masked_phone": _mask_phone(phone) if phone else "",
                "status_text": "手机号已验证" if phone_verified else "待绑定手机号",
                "action_label": "更换手机号" if phone_verified else "绑定手机号",
            },
            "rehab_stage": {
                "label": "康复阶段",
                "value": _patient_stage_label(str(profile.get("rehab_stage") or "")),
            },
            "affected_side": {
                "label": "患侧",
                "value": _patient_side_label(str(profile.get("affected_side") or "")),
            },
            "medical_constraints": {
                "status": "已填写" if medical_items else "待完善",
                "items": medical_items,
                "helper_text": (
                    "训练前请继续遵守已填写的禁忌备注。"
                    if medical_items
                    else "还没有填写禁忌备注，训练前请按医生/康复师建议补充。"
                ),
                "action_label": "编辑禁忌备注" if medical_items else "添加禁忌备注",
            },
        },
        "device": {
            "title": "设备管家",
            "status": "bound" if device_bound else "unbound",
            "status_text": device_status_text,
            "primary_action": device_primary_action,
            "readiness_rows": [
                {"label": "账号", "value": "已登录"},
                {"label": "手机号", "value": "已验证" if phone_verified else "待绑定"},
                {"label": "康复设备", "value": device_status_text},
                {"label": "训练安全", "value": "开始前再次确认"},
            ],
            "binding_steps": [
                "打开康复设备电源",
                "手机靠近设备",
                "选择蓝牙设备或扫码绑定",
                "等待设备安全系统确认",
            ],
        },
        "agent": {
            "title": "康复师助手",
            "entry_label": "问康复师",
            "placeholder": "今天哪里不舒服？想问什么？",
            "quick_questions": [
                "今天还能训练吗？",
                "手臂酸痛怎么办？",
                "帮我解释报告",
                "生成轻量训练建议",
            ],
            "endpoint": "/api/rehab-arm/app/v1/agent/messages",
            "unsafe_copy": "为了保护你，我不能绕过设备安全系统或发送直接运动指令。可以帮你调整训练建议或解释报告。",
            "boundary_copy": "我可以解释报告和给出训练建议，真正开始运动前仍要完成设备安全确认。",
            "boundary": "我可以解释训练和报告，但不能直接控制设备。",
        },
    }


def _patient_primary_action(next_action: dict[str, object]) -> dict[str, str]:
    code = str(next_action.get("code") or "")
    action_map = {
        "bind_device": {"label": "绑定康复设备", "route": "device.html", "code": "bind_device"},
        "generate_plan": {"label": "生成今日训练建议", "route": "ai-plan.html", "code": "generate_plan"},
        "accept_ai_plan": {"label": "确认康复师建议", "route": "ai-plan.html", "code": "accept_plan"},
        "sync_plan": {"label": "同步训练计划", "route": "device.html", "code": "sync_plan"},
        "review_report": {"label": "查看训练报告", "route": "report.html", "code": "review_report"},
    }
    if code in action_map:
        return action_map[code]
    return {
        "label": _patient_text(str(next_action.get("label") or next_action.get("title") or "查看下一步")),
        "route": "home.html",
        "code": "next_step",
    }


def _patient_readiness_summary(status: str) -> str:
    return {
        "needs_device": "先绑定康复设备，再开始训练闭环。",
        "needs_plan": "设备已就绪，可以生成今日训练建议。",
        "needs_plan_acceptance": "已有训练建议，确认后再同步到设备。",
        "needs_device_sync": "训练计划已生成，请同步设备并等待安全确认。",
        "ready": "训练记录已保存，请先查看报告再进入下一步。",
    }.get(status, "按页面提示完成下一步。")


def _patient_stage_label(value: str) -> str:
    return {
        "early_active": "主动训练早期",
        "subacute": "亚急性期",
        "recovery": "恢复期",
        "chronic": "稳定康复期",
    }.get(value, _patient_text(value) if value else "待完善")


def _patient_side_label(value: str) -> str:
    return {
        "left": "左侧",
        "right": "右侧",
        "bilateral": "双侧",
    }.get(value, _patient_text(value) if value else "待完善")


def _patient_text(value: str) -> str:
    replacements = {
        "M33": "设备安全系统",
        "M55": "肌电记录设备",
        "SPP": "蓝牙连接",
        "CAN": "设备指令",
        "UUID": "设备识别码",
        "preflight": "训练前检查",
        "setup_required": "完成首次设置",
        "early_active": "主动训练早期",
        "direct_motor_command": "直接运动指令",
        "can_frame": "设备指令",
        "m33_safety": "设备安全系统",
        "motion_permission": "运动许可",
        "AI": "康复师",
    }
    cleaned = value
    for raw, replacement in replacements.items():
        cleaned = cleaned.replace(raw, replacement)
    return cleaned


def _split_constraints(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _normalize_phone(phone: str) -> str:
    return "".join(char for char in phone.strip() if char.isdigit() or char == "+")


def _mask_phone(phone: str) -> str:
    if len(phone) <= 8:
        return phone[:2] + "****" + phone[-2:]
    return phone[:4] + "****" + phone[-4:]


def _debug_phone_code(phone: str) -> str:
    digits = "".join(char for char in phone if char.isdigit())
    suffix = digits[-4:] if len(digits) >= 4 else digits.rjust(4, "0")
    return f"42{suffix}"[-6:]


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def device_to_dict(device: Device) -> dict[str, object]:
    return {
        "id": str(device.id),
        "m33_device_id": device.m33_device_id,
        "ble_name": device.ble_name,
        "trust_status": device.trust_status,
        "firmware_version": device.firmware_version,
    }


def session_to_dict(session: TrainingSession) -> dict[str, object]:
    return {
        "id": str(session.id),
        "device_id": str(session.device_id),
        "plan_id": session.plan_id,
        "status": session.status,
        "duration_seconds": session.duration_seconds,
        "completed_movements": session.completed_movements,
        "target_movements": session.target_movements,
        "completion_rate": session.completion_rate,
        "pain_score": session.pain_score,
        "fatigue_score": session.fatigue_score,
        "emg_summary": _json_loads(session.emg_summary_json, {}),
        "notes": session.notes,
        "created_at": session.created_at.isoformat(),
    }


def report_to_dict(report: TrainingReport) -> dict[str, object]:
    return {
        "id": str(report.id),
        "session_id": str(report.session_id),
        "title": report.title,
        "summary": report.summary,
        "safety_level": report.safety_level,
        "pain_score": report.pain_score,
        "fatigue_score": report.fatigue_score,
        "completion_rate": report.completion_rate,
        "created_at": report.created_at.isoformat(),
    }


def training_plan_to_dict(plan: TrainingPlan) -> dict[str, object]:
    return {
        "id": str(plan.id),
        "source": plan.source,
        "source_draft_id": str(plan.source_draft_id) if plan.source_draft_id is not None else "",
        "title": plan.title,
        "goal": plan.goal,
        "movement_type": plan.movement_type,
        "sets": plan.sets,
        "reps": plan.reps,
        "assist_level": plan.assist_level,
        "speed_level": plan.speed_level,
        "target_angle_range": _json_loads(plan.target_angle_range_json, []),
        "risk_notes": _json_loads(plan.risk_notes_json, []),
        "device_sync_status": plan.device_sync_status,
        "m33_status": plan.m33_status,
        "created_at": plan.created_at.isoformat(),
    }


def draft_to_dict(draft: AiTrainingDraft) -> dict[str, object]:
    return {
        "id": str(draft.id),
        "input_text": draft.input_text,
        "generated_plan": _json_loads(draft.generated_plan_json, {}),
        "risk_notes": _json_loads(draft.risk_notes_json, []),
        "context_snapshot": _json_loads(draft.context_snapshot_json, {}),
        "accepted_plan_id": str(draft.accepted_plan_id) if draft.accepted_plan_id is not None else "",
        "created_at": draft.created_at.isoformat(),
    }


def ble_message_to_dict(message: BleMessage) -> dict[str, object]:
    return {
        "id": str(message.id),
        "device_id": str(message.device_id),
        "plan_id": str(message.plan_id) if message.plan_id is not None else "",
        "message_type": message.message_type,
        "payload": _json_loads(message.payload_json, {}),
        "status": message.status,
        "created_at": message.created_at.isoformat(),
    }


def _parse_raw_text(raw_text: str) -> object | None:
    text = raw_text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _get_owned_device(db: Session, owner_id: int, device_id: str) -> Device:
    try:
        numeric_device_id = int(device_id)
    except ValueError:
        numeric_device_id = -1
    device = db.get(Device, numeric_device_id)
    if device is None or device.owner_id != owner_id:
        raise HTTPException(
            status_code=404,
            detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"},
        )
    return device


def _get_owned_plan(db: Session, owner_id: int, plan_id: int) -> TrainingPlan:
    plan = db.get(TrainingPlan, plan_id)
    if plan is None or plan.owner_id != owner_id:
        raise HTTPException(
            status_code=404,
            detail={"code": "TRAINING_PLAN_NOT_FOUND", "message": "Training plan not found"},
        )
    return plan


def _calculate_completion_rate(completed_movements: int, target_movements: int) -> float:
    return round(min(completed_movements / target_movements, 1.0), 2)


def _safety_level(pain_score: int, fatigue_score: int) -> str:
    if pain_score >= 7 or fatigue_score >= 8:
        return "stop"
    if pain_score >= 4 or fatigue_score >= 6:
        return "attention"
    return "normal"


def _report_summary(completed_movements: int, target_movements: int, pain_score: int) -> str:
    percent = int(_calculate_completion_rate(completed_movements, target_movements) * 100)
    return f"Completed {percent}% of planned movements with pain score {pain_score}/10."


def _json_loads(value: str, fallback: object) -> object:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _latest_report(db: Session, owner_id: int) -> TrainingReport | None:
    return db.scalar(
        select(TrainingReport)
        .where(TrainingReport.owner_id == owner_id)
        .order_by(TrainingReport.created_at.desc(), TrainingReport.id.desc())
        .limit(1)
    )


def _int(value: object, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _float(value: object, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _m33_legacy_spp_profile() -> dict[str, object]:
    return {
        "service_uuid": "6e400001-b5a3-f393-e0a9-e50e24dcca9e",
        "write_characteristic_uuid": "6e400002-b5a3-f393-e0a9-e50e24dcca9e",
        "notify_characteristic_uuid": "6e400003-b5a3-f393-e0a9-e50e24dcca9e",
        "line_delimiter": "\n",
        "transport": "legacy_spp_or_nus_bridge",
        "control_boundary": "transport_only_m33_final_authority",
    }


def _workflow_for_user(db: Session, owner_id: int) -> dict[str, object]:
    device_count = db.scalar(select(Device).where(Device.owner_id == owner_id).limit(1)) is not None
    plan = db.scalar(
        select(TrainingPlan)
        .where(TrainingPlan.owner_id == owner_id)
        .order_by(TrainingPlan.created_at.desc(), TrainingPlan.id.desc())
        .limit(1)
    )
    draft = db.scalar(
        select(AiTrainingDraft)
        .where(AiTrainingDraft.owner_id == owner_id, AiTrainingDraft.accepted_plan_id.is_(None))
        .order_by(AiTrainingDraft.created_at.desc(), AiTrainingDraft.id.desc())
        .limit(1)
    )
    if not device_count:
        phase = {
            "status": "needs_device",
            "title": "\u7b49\u5f85\u7ed1\u5b9a\u8bbe\u5907",
            "description": "\u5148\u7ed1\u5b9a\u53ef\u4fe1 M33/PSoC \u5eb7\u590d\u8bbe\u5907\u3002",
        }
        next_action = {"code": "BIND_DEVICE", "title": "\u7ed1\u5b9a\u8bbe\u5907"}
        blockers = [{"code": "DEVICE_REQUIRED", "title": "\u672a\u7ed1\u5b9a\u8bbe\u5907"}]
    elif plan is not None and plan.device_sync_status != "synced":
        phase = {
            "status": "needs_sync",
            "title": "\u7b49\u5f85\u540c\u6b65\u8bad\u7ec3\u8ba1\u5212",
            "description": "\u5df2\u6709\u8bad\u7ec3\u8ba1\u5212\uff0c\u9700\u8981\u540c\u6b65\u5230\u8bbe\u5907\u5e76\u7b49\u5f85 M33 \u63a5\u53d7\u3002",
        }
        next_action = {"code": "SYNC_ACCEPTED_PLAN_TO_M33", "title": "\u540c\u6b65\u8bad\u7ec3\u8ba1\u5212"}
        blockers = []
    elif draft is not None:
        phase = {
            "status": "needs_plan_acceptance",
            "title": "\u7b49\u5f85\u63a5\u53d7 AI \u8bad\u7ec3\u8349\u7a3f",
            "description": "AI \u8349\u7a3f\u9700\u8981\u7528\u6237\u786e\u8ba4\u540e\u624d\u4f1a\u6210\u4e3a\u8bad\u7ec3\u8ba1\u5212\u3002",
        }
        next_action = {"code": "ACCEPT_AI_DRAFT", "title": "\u63a5\u53d7 AI \u8349\u7a3f"}
        blockers = []
    else:
        phase = {
            "status": "ready_for_plan",
            "title": "\u53ef\u751f\u6210\u4eca\u65e5\u8bad\u7ec3",
            "description": "\u8bbe\u5907\u5df2\u7ed1\u5b9a\uff0c\u53ef\u7531\u5eb7\u590d\u5e08 Agent \u751f\u6210\u4e0b\u4e00\u6b21\u8bad\u7ec3\u8349\u7a3f\u3002",
        }
        next_action = {"code": "GENERATE_AI_DRAFT", "title": "\u751f\u6210 AI \u8bad\u7ec3\u8349\u7a3f"}
        blockers = []
    return {
        "phase": phase,
        "next_action": next_action,
        "action_queue": [next_action],
        "blockers": blockers,
        "forbidden_actions": ["DIRECT_MOTOR_COMMAND", "BYPASS_M33_PREFLIGHT"],
        "safety_boundary": "App workflow is advisory. M33 is final authority for movement.",
    }


def _legacy_frame_json(message_type: str, plan: TrainingPlan | None, payload: dict[str, object]) -> dict[str, object]:
    frame = {
        "type": message_type,
        "payload": payload,
        "control_boundary": "transport_only_m33_final_authority",
    }
    if plan is not None:
        frame.update(
            {
                "plan_id": str(plan.id),
                "movement_type": plan.movement_type,
                "sets": plan.sets,
                "reps": plan.reps,
                "assist_level": plan.assist_level,
                "speed_level": plan.speed_level,
                "target_angle_range": _json_loads(plan.target_angle_range_json, []),
            }
        )
    return frame


def _timeline_items(
    reports: list[dict[str, object]],
    plans: list[dict[str, object]],
    draft: dict[str, object] | None,
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for plan in plans:
        items.append(
            {
                "id": f"plan-{plan['id']}",
                "kind": "training_plan",
                "event_at": plan["created_at"],
                "display": {"title": plan["title"], "subtitle": plan["device_sync_status"]},
                "primary_action": {"code": "SYNC_ACCEPTED_PLAN_TO_M33"},
            }
        )
    for report in reports:
        items.append(
            {
                "id": f"report-{report['id']}",
                "kind": "training_report",
                "event_at": report["created_at"],
                "display": {"title": report["title"], "subtitle": report["safety_level"]},
                "primary_action": {"code": "RECORD_REPORT_REVIEW"},
            }
        )
    if draft is not None:
        items.append(
            {
                "id": f"draft-{draft['id']}",
                "kind": "ai_training_draft",
                "event_at": draft["created_at"],
                "display": {"title": draft["generated_plan"].get("title", "AI rehab draft"), "subtitle": "waiting"},
                "primary_action": {"code": "ACCEPT_AI_DRAFT"},
            }
        )
    return sorted(items, key=lambda item: str(item["event_at"]), reverse=True)
