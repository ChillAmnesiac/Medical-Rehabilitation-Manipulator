from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="rehab_vla_orchestrator",
                executable="rehab_vla_orchestrator",
                name="rehab_vla_orchestrator",
                output="screen",
            )
        ]
    )
