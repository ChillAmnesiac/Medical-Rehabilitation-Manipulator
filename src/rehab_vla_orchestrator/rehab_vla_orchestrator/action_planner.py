from __future__ import annotations

from .loop_contracts import ActionPlan, LoopInput, PlanBoundary, RehabMode, VisionObservation


def _pixel_delta(vision: VisionObservation) -> tuple[float, float] | None:
    target = vision.target_center_px
    end_effector = vision.gripper_tip_center_px or vision.end_effector_center_px
    if target is None or end_effector is None:
        return None
    return target[0] - end_effector[0], target[1] - end_effector[1]


def _fetch_object_plan(loop_input: LoopInput) -> ActionPlan:
    vision = loop_input.vision
    target_label = loop_input.language.target_label or vision.target_label or "target_object"
    delta = _pixel_delta(vision)

    if not vision.target_center_px:
        return ActionPlan(
            schema_version="rehab_vla_action_plan_v1",
            mode=RehabMode.FETCH_OBJECT,
            boundary=PlanBoundary.DRY_RUN,
            state="waiting_for_target",
            reason="target_not_visible",
            next_step="keep_scanning",
            target_label=target_label,
            display_hints={"need": ["target_bbox", "end_effector_bbox"]},
        )

    if delta is None:
        return ActionPlan(
            schema_version="rehab_vla_action_plan_v1",
            mode=RehabMode.FETCH_OBJECT,
            boundary=PlanBoundary.DRY_RUN,
            state="waiting_for_end_effector",
            reason="target_visible_but_end_effector_not_visible",
            next_step="show_target_lock_only",
            target_label=target_label,
            display_hints={"target_center_px": vision.target_center_px},
        )

    dx, dy = delta
    frame_w, frame_h = vision.frame_size_px
    norm_dx = dx / max(frame_w, 1)
    norm_dy = dy / max(frame_h, 1)
    close_enough = abs(norm_dx) < 0.08 and abs(norm_dy) < 0.08
    state = "visual_servo_aligned" if close_enough else "visual_servo_adjust"
    next_step = "hold_and_request_operator_review" if close_enough else "dry_run_pixel_servo_step"

    return ActionPlan(
        schema_version="rehab_vla_action_plan_v1",
        mode=RehabMode.FETCH_OBJECT,
        boundary=PlanBoundary.OPERATOR_REVIEW if close_enough else PlanBoundary.DRY_RUN,
        state=state,
        reason="target_and_end_effector_visible",
        next_step=next_step,
        target_label=target_label,
        dry_run_commands=[
            {
                "type": "pixel_servo_hint",
                "dx_px": round(dx, 2),
                "dy_px": round(dy, 2),
                "dx_norm": round(norm_dx, 4),
                "dy_norm": round(norm_dy, 4),
                "metric_depth_available": vision.metric_depth_available,
            }
        ],
        display_hints={
            "target_center_px": vision.target_center_px,
            "end_effector_center_px": vision.gripper_tip_center_px or vision.end_effector_center_px,
        },
    )


def _training_plan(loop_input: LoopInput) -> ActionPlan:
    goal = loop_input.training
    return ActionPlan(
        schema_version="rehab_vla_action_plan_v1",
        mode=RehabMode.TRAINING,
        boundary=PlanBoundary.DRY_RUN,
        state="training_goal_selected" if goal.active else "waiting_for_training_goal",
        reason="language_intent_training",
        next_step="load_training_library_goal",
        target_label=goal.goal_id,
        display_hints={
            "training_goal": goal.display_name,
            "assistive": goal.assistive,
            "requires_emg_context": True,
        },
    )


def _assistive_plan(loop_input: LoopInput) -> ActionPlan:
    emg = loop_input.emg
    return ActionPlan(
        schema_version="rehab_vla_action_plan_v1",
        mode=RehabMode.ASSISTIVE_EMG,
        boundary=PlanBoundary.M33_REQUIRED,
        state="emg_intent_ready" if emg.active else "waiting_for_emg_intent",
        reason="assistive_mode_requires_m33_safety_gate",
        next_step="display_assist_direction_and_wait_for_safety",
        dry_run_commands=[
            {
                "type": "assistive_hint",
                "intended_motion": emg.intended_motion,
                "confidence": emg.confidence,
                "muscle_channels": emg.muscle_channels,
            }
        ],
    )


def make_action_plan(loop_input: LoopInput) -> ActionPlan:
    mode = loop_input.language.mode
    if mode == RehabMode.FETCH_OBJECT:
        return _fetch_object_plan(loop_input)
    if mode == RehabMode.TRAINING:
        return _training_plan(loop_input)
    if mode == RehabMode.ASSISTIVE_EMG:
        return _assistive_plan(loop_input)
    return ActionPlan(
        schema_version="rehab_vla_action_plan_v1",
        mode=RehabMode.CHAT,
        boundary=PlanBoundary.CHAT_ONLY,
        state="chat_only",
        reason="no_robot_action_intent",
        next_step="respond_in_language_channel_only",
    )
