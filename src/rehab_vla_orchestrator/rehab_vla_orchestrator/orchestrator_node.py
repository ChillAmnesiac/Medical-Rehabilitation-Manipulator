from __future__ import annotations

import json
from dataclasses import asdict

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .action_planner import make_action_plan
from .intent_classifier import classify_language_intent
from .loop_contracts import LoopInput


class RehabVlaOrchestrator(Node):
    def __init__(self) -> None:
        super().__init__("rehab_vla_orchestrator")
        self.plan_publisher = self.create_publisher(String, "/rehab_arm/vla/action_plan", 10)
        self.create_subscription(String, "/rehab_arm/language_intent_text", self.on_language_text, 10)
        self.get_logger().info("rehab_vla_orchestrator ready; dry-run plans only")

    def on_language_text(self, message: String) -> None:
        intent = classify_language_intent(message.data)
        plan = make_action_plan(LoopInput(language=intent))
        payload = json.dumps(asdict(plan), ensure_ascii=False)
        self.plan_publisher.publish(String(data=payload))
        self.get_logger().info(f"published dry-run plan mode={plan.mode.value} state={plan.state}")


def main() -> None:
    rclpy.init()
    node = RehabVlaOrchestrator()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
