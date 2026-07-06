from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    phone_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(80), default="康复用户")
    role: Mapped[str] = mapped_column(String(32), default="patient")
    rehab_stage: Mapped[str] = mapped_column(String(80), default="亚急性期")
    affected_side: Mapped[str] = mapped_column(String(32), default="左侧")
    medical_constraints: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    m33_device_id: Mapped[str] = mapped_column(String(120), index=True)
    ble_name: Mapped[str] = mapped_column(String(120), default="")
    trust_status: Mapped[str] = mapped_column(String(32), default="trusted")
    firmware_version: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LegacySppInbound(Base):
    __tablename__ = "legacy_spp_inbound"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    parsed_json: Mapped[str] = mapped_column(Text, default="")
    related_message_id: Mapped[str] = mapped_column(String(120), default="")
    transport_event_json: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="matched")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    plan_id: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(32), default="completed")
    duration_seconds: Mapped[int] = mapped_column(Integer)
    completed_movements: Mapped[int] = mapped_column(Integer)
    target_movements: Mapped[int] = mapped_column(Integer)
    completion_rate: Mapped[float] = mapped_column(Float)
    pain_score: Mapped[int] = mapped_column(Integer)
    fatigue_score: Mapped[int] = mapped_column(Integer)
    emg_summary_json: Mapped[str] = mapped_column(Text, default="{}")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TrainingReport(Base):
    __tablename__ = "training_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id"), index=True)
    title: Mapped[str] = mapped_column(String(120), default="Daily rehab session")
    summary: Mapped[str] = mapped_column(Text, default="")
    safety_level: Mapped[str] = mapped_column(String(32), default="normal")
    pain_score: Mapped[int] = mapped_column(Integer)
    fatigue_score: Mapped[int] = mapped_column(Integer)
    completion_rate: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_draft_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="ai_draft")
    title: Mapped[str] = mapped_column(String(120))
    goal: Mapped[str] = mapped_column(Text, default="")
    movement_type: Mapped[str] = mapped_column(String(80), default="elbow_flexion")
    sets: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    assist_level: Mapped[float] = mapped_column(Float)
    speed_level: Mapped[str] = mapped_column(String(32), default="slow")
    target_angle_range_json: Mapped[str] = mapped_column(Text, default="[]")
    risk_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    device_sync_status: Mapped[str] = mapped_column(String(32), default="not_synced")
    m33_status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AiTrainingDraft(Base):
    __tablename__ = "ai_training_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    input_text: Mapped[str] = mapped_column(Text)
    generated_plan_json: Mapped[str] = mapped_column(Text)
    risk_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    context_snapshot_json: Mapped[str] = mapped_column(Text, default="{}")
    accepted_plan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BleMessage(Base):
    __tablename__ = "ble_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    plan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message_type: Mapped[str] = mapped_column(String(80))
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(32), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PhoneVerification(Base):
    __tablename__ = "phone_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    phone: Mapped[str] = mapped_column(String(32), index=True)
    purpose: Mapped[str] = mapped_column(String(40), default="bind_account")
    code_hash: Mapped[str] = mapped_column(String(255))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
