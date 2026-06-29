#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import asdict

from rehab_vla_orchestrator.action_planner import make_action_plan
from rehab_vla_orchestrator.intent_classifier import classify_language_intent
from rehab_vla_orchestrator.loop_contracts import EmgIntent, LoopInput, TrainingGoal, VisionObservation


def main() -> int:
    cases = [
        LoopInput(language=classify_language_intent("我口渴了，帮我拿水杯")),
        LoopInput(
            language=classify_language_intent("帮我拿水杯"),
            vision=VisionObservation(
                target_label="target_cup",
                target_center_px=(320.0, 260.0),
                end_effector_center_px=(250.0, 240.0),
            ),
        ),
        LoopInput(
            language=classify_language_intent("我要开始今天的训练"),
            training=TrainingGoal(active=True, goal_id="elbow_flexion_a1", display_name="肘关节屈曲训练"),
        ),
        LoopInput(
            language=classify_language_intent("开启肌电助力"),
            emg=EmgIntent(active=True, intended_motion="elbow_flexion", confidence=0.76, muscle_channels={"biceps": 0.82}),
        ),
        LoopInput(language=classify_language_intent("今天天气怎么样")),
    ]

    for case in cases:
        plan = make_action_plan(case)
        print(json.dumps(asdict(plan), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
