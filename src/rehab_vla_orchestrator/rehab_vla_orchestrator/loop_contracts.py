from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RehabMode(str, Enum):
    CHAT = "chat"
    FETCH_OBJECT = "fetch_object"
    TRAINING = "training"
    ASSISTIVE_EMG = "assistive_emg"
    VISION_SERVO = "vision_servo"
    SAFETY_REVIEW = "safety_review"


class PlanBoundary(str, Enum):
    CHAT_ONLY = "chat_only"
    DRY_RUN = "dry_run"
    OPERATOR_REVIEW = "operator_review"
    M33_REQUIRED = "m33_required"


@dataclass(frozen=True)
class LanguageIntent:
    raw_text: str
    mode: RehabMode
    target_label: str = ""
    confidence: float = 0.0
    source: str = "xiaozhi_or_text"


@dataclass(frozen=True)
class VisionObservation:
    target_label: str = ""
    target_center_px: tuple[float, float] | None = None
    end_effector_center_px: tuple[float, float] | None = None
    gripper_tip_center_px: tuple[float, float] | None = None
    frame_size_px: tuple[int, int] = (640, 480)
    confidence: float = 0.0
    metric_depth_available: bool = False


@dataclass(frozen=True)
class EmgIntent:
    active: bool = False
    intended_motion: str = ""
    confidence: float = 0.0
    muscle_channels: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingGoal:
    active: bool = False
    goal_id: str = ""
    display_name: str = ""
    assistive: bool = True


@dataclass(frozen=True)
class LoopInput:
    language: LanguageIntent
    vision: VisionObservation = field(default_factory=VisionObservation)
    emg: EmgIntent = field(default_factory=EmgIntent)
    training: TrainingGoal = field(default_factory=TrainingGoal)
    safety_state: str = "unknown"


@dataclass(frozen=True)
class ActionPlan:
    schema_version: str
    mode: RehabMode
    boundary: PlanBoundary
    state: str
    reason: str
    next_step: str
    target_label: str = ""
    dry_run_commands: list[dict[str, Any]] = field(default_factory=list)
    display_hints: dict[str, Any] = field(default_factory=dict)
