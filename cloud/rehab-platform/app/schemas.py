from pydantic import BaseModel, Field


class SessionRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    rehab_stage: str | None = None
    affected_side: str | None = None
    medical_constraints: list[str] | None = None


class DeviceBindRequest(BaseModel):
    m33_device_id: str = Field(min_length=1)
    ble_name: str | None = None
    trust_status: str | None = "trusted"
    firmware_version: str | None = None


class LegacySppInboundRequest(BaseModel):
    raw_text: str = Field(min_length=1)
    related_message_id: str | None = None
    transport_event: dict[str, object] | None = None


class TrainingSessionCreateRequest(BaseModel):
    device_id: str = Field(min_length=1)
    plan_id: str | None = None
    duration_seconds: int = Field(ge=1)
    completed_movements: int = Field(ge=0)
    target_movements: int = Field(ge=1)
    pain_score: int = Field(ge=0, le=10)
    fatigue_score: int = Field(ge=0, le=10)
    emg_summary: dict[str, object] | None = None
    notes: str | None = None


class AiTrainingDraftGenerateRequest(BaseModel):
    input_text: str = Field(min_length=1)
    context_snapshot: dict[str, object] | None = None


class AgentMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    context_snapshot: dict[str, object] | None = None


class WorkflowActionRequest(BaseModel):
    action_code: str = Field(min_length=1)
    payload: dict[str, object] | None = None


class PlanSyncRequest(BaseModel):
    device_id: str = Field(min_length=1)


class BleMessageRequest(BaseModel):
    message_type: str = Field(min_length=1)
    plan_id: str | None = None
    payload: dict[str, object] | None = None


class PhoneVerificationStartRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=32)
    purpose: str = "bind_account"


class PhoneVerificationConfirmRequest(BaseModel):
    code: str = Field(min_length=4, max_length=12)


class ModelRelayConfigRequest(BaseModel):
    provider: str = Field(min_length=1)
    base_url: str | None = None
    model: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    external_enabled: bool = True
