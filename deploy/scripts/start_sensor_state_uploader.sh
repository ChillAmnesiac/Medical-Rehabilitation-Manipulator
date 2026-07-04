#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/home/pi/rehab_arm_ros2_ws}"
ROS_NETWORK_ENV="${ROS_NETWORK_ENV:-/home/pi/.rehab_arm_ros2_network}"
ROS_LOG_DIR="${ROS_LOG_DIR:-/home/pi/.ros/log}"
API_BASE_URL="${API_BASE_URL:-http://106.55.62.122:8011/api/rehab-arm/v1}"
PROJECT_ID="${PROJECT_ID:-e201f41c-25a6-46e1-baf8-be6dcb83284c}"
ROBOT_ID="${ROBOT_ID:-rehab-arm-alpha}"
DEVICE_ID="${DEVICE_ID:-nanopi-m5}"
RELAY_TOKEN="${RELAY_TOKEN:-}"
MIN_INTERVAL_SEC="${MIN_INTERVAL_SEC:-0.10}"
TIMEOUT_SEC="${TIMEOUT_SEC:-3.0}"

mkdir -p "$ROS_LOG_DIR"
chmod 0775 "$ROS_LOG_DIR" 2>/dev/null || true
export ROS_LOG_DIR

if [ -f /opt/ros/jazzy/setup.bash ]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
  set -u
elif [ -f /opt/ros/humble/setup.bash ]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
  set -u
else
  echo "No supported ROS setup.bash found under /opt/ros" >&2
  exit 2
fi

if [ -f "$ROS_NETWORK_ENV" ]; then
  set +u
  # shellcheck disable=SC1090
  source "$ROS_NETWORK_ENV"
  set -u
fi

if [ ! -f "$WORKSPACE/install/setup.bash" ]; then
  echo "ROS workspace install setup not found: $WORKSPACE/install/setup.bash" >&2
  exit 2
fi

set +u
# shellcheck disable=SC1090
source "$WORKSPACE/install/setup.bash"
set -u

ROS_ARGS=(
  -p api_base_url:="$API_BASE_URL"
  -p robot_id:="$ROBOT_ID"
  -p device_id:="$DEVICE_ID"
  -p project_id:="$PROJECT_ID"
  -p min_interval_sec:="$MIN_INTERVAL_SEC"
  -p timeout_sec:="$TIMEOUT_SEC"
)

if [ -n "$RELAY_TOKEN" ]; then
  ROS_ARGS+=(-p relay_token:="$RELAY_TOKEN")
fi

exec ros2 run rehab_arm_psoc_bridge sensor_state_uploader_node.py --ros-args \
  "${ROS_ARGS[@]}"
