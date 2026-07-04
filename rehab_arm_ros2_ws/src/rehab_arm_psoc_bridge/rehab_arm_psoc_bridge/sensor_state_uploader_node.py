#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path
from typing import Callable
from urllib import request

try:
    import rclpy
    from rclpy.executors import ExternalShutdownException
    from rclpy.node import Node
    from std_msgs.msg import String
except ModuleNotFoundError:
    rclpy = None
    Node = object  # type: ignore[assignment,misc]
    String = object  # type: ignore[assignment,misc]
    ExternalShutdownException = Exception  # type: ignore[assignment,misc]

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rehab_arm_psoc_bridge.f103_sensor_state import ADC_MAX, ADC_REF_VOLTAGE, EMG4_CHANNEL_MAP, F103_HEALTH_ID_HEX, F103_SENSOR_ID_HEX


DEFAULT_API_BASE_URL = 'http://106.55.62.122:8011/api/rehab-arm/v1'
DEFAULT_PROJECT_ID = 'e201f41c-25a6-46e1-baf8-be6dcb83284c'
OpenUrl = Callable[[request.Request, float], object]


def normalize_api_base_url(api_base_url: str) -> str:
    base = str(api_base_url or DEFAULT_API_BASE_URL).rstrip('/')
    if base.endswith('/api/rehab-arm/v1'):
        return base
    return f'{base}/api/rehab-arm/v1'


def sensor_state_url(api_base_url: str, device_id: str) -> str:
    return f'{normalize_api_base_url(api_base_url)}/devices/{device_id}/sensor-state'


def _health_summary(health_payload: dict[str, object]) -> dict[str, object]:
    return {
        'schema_version': health_payload.get('schema_version'),
        'source': health_payload.get('source'),
        'id_hex': health_payload.get('id_hex'),
        'valid': health_payload.get('valid'),
        'state': health_payload.get('state'),
        'state_code': health_payload.get('state_code'),
        'error_count': health_payload.get('error_count'),
        'queue_fill': health_payload.get('queue_fill'),
        'queue_fill_percent': health_payload.get('queue_fill_percent'),
        'control_boundary': health_payload.get('control_boundary'),
    }


def _zero_emg4_channels() -> list[dict[str, object]]:
    return [
        {
            'channel': channel,
            'name': channel,
            'channel_id': f'f103_adc{adc_index}',
            'adc_index': adc_index,
            'muscle': muscle,
            'muscle_name': muscle_name,
            'raw_adc': 0,
            'value': 0.0,
            'activation': 0.0,
            'unit': 'adc_counts',
            'raw_adc_unit': 'adc_counts',
            'voltage_v': 0.0,
            'value_v': 0.0,
            'voltage_unit': 'V',
            'voltage_reference_v': ADC_REF_VOLTAGE,
            'range': [0, ADC_MAX],
            'signal_quality': 'missing',
        }
        for channel, adc_index, muscle, muscle_name in EMG4_CHANNEL_MAP
    ]


def build_sensor_state_upload_payload(
    sensor_payload: dict[str, object],
    *,
    robot_id: str,
    device_id: str,
    project_id: str,
    now_unix: float | None = None,
    health_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    emg_source = sensor_payload.get('emg')
    emg = copy.deepcopy(emg_source) if isinstance(emg_source, dict) else {}
    if not emg:
        channels = _zero_emg4_channels()
        emg = {
            'schema_version': 'rehab_arm_emg4_adc_v1',
            'source': sensor_payload.get('source') or 'stm32_f103_emg3_can_0x7c2',
            'channels': channels,
            'channel_count': len(channels),
            'sample_unit': 'adc_counts',
            'adc_range': [0, ADC_MAX],
            'voltage_reference_v': ADC_REF_VOLTAGE,
            'voltage_unit': 'V',
            'signal_quality': {
                'status': 'degraded',
                'reason': 'no_emg_channels_in_sensor_payload',
                'valid_channel_count': 0,
            },
            'control_boundary': 'telemetry_only_not_motion_permission',
        }

    emg['transport'] = {
        'gateway': 'nanopi_ros2',
        'ros_topic': '/rehab_arm/sensor_state',
        'source_can_id': sensor_payload.get('id_hex') or F103_SENSOR_ID_HEX,
    }
    if health_payload:
        emg['f103_health'] = _health_summary(health_payload)

    return {
        'robot_id': robot_id,
        'device_id': device_id,
        'project_id': project_id,
        'ts_unix': float(now_unix if now_unix is not None else time.time()),
        'emg': emg,
        'source': 'nanopi_ros2_f103_can_gateway',
    }


def make_sensor_state_request(
    api_base_url: str,
    payload: dict[str, object],
    *,
    relay_token: str = '',
) -> request.Request:
    url = sensor_state_url(api_base_url, str(payload['device_id']))
    headers = {'Content-Type': 'application/json'}
    if relay_token:
        headers['Authorization'] = f'Bearer {relay_token}'
    body = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return request.Request(url, data=body, headers=headers, method='POST')


def post_sensor_state(
    api_base_url: str,
    payload: dict[str, object],
    *,
    relay_token: str = '',
    timeout_sec: float = 3.0,
    opener: OpenUrl | None = None,
) -> dict[str, object]:
    http_request = make_sensor_state_request(api_base_url, payload, relay_token=relay_token)
    try:
        response = (
            request.urlopen(http_request, timeout=timeout_sec)
            if opener is None
            else opener(http_request, timeout_sec)
        )
        status = int(getattr(response, 'status', getattr(response, 'code', 0)))
        body = response.read().decode('utf-8', errors='replace')
        return {'ok': 200 <= status < 300, 'status': status, 'body': body, 'url': http_request.full_url}
    except Exception as exc:
        return {'ok': False, 'error': str(exc), 'url': http_request.full_url}


class SensorStateUploaderNode(Node):  # type: ignore[misc,valid-type]
    def __init__(self):
        if rclpy is None:
            raise RuntimeError('rclpy is required to run sensor_state_uploader_node')
        super().__init__('rehab_arm_sensor_state_uploader')
        self.declare_parameter('api_base_url', DEFAULT_API_BASE_URL)
        self.declare_parameter('robot_id', 'rehab-arm-alpha')
        self.declare_parameter('device_id', 'nanopi-m5')
        self.declare_parameter('project_id', DEFAULT_PROJECT_ID)
        self.declare_parameter('relay_token', '')
        self.declare_parameter('timeout_sec', 3.0)
        self.declare_parameter('min_interval_sec', 0.10)

        self.api_base_url = str(self.get_parameter('api_base_url').value)
        self.robot_id = str(self.get_parameter('robot_id').value)
        self.device_id = str(self.get_parameter('device_id').value)
        self.project_id = str(self.get_parameter('project_id').value)
        self.relay_token = str(self.get_parameter('relay_token').value)
        self.timeout_sec = float(self.get_parameter('timeout_sec').value)
        self.min_interval_sec = float(self.get_parameter('min_interval_sec').value)
        self.last_emg_payload: dict[str, object] | None = None
        self.last_health_payload: dict[str, object] | None = None
        self.last_upload_monotonic = 0.0
        self.upload_count = 0
        self.drop_count = 0

        self.create_subscription(String, '/rehab_arm/sensor_state', self.on_sensor_state, 50)
        self.get_logger().info(
            'sensor state uploader ready; '
            f'url={sensor_state_url(self.api_base_url, self.device_id)} min_interval={self.min_interval_sec:.2f}s'
        )

    def on_sensor_state(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.drop_count += 1
            self.get_logger().warn(f'ignored non-json sensor_state: {exc}')
            return
        if not isinstance(payload, dict):
            self.drop_count += 1
            return

        id_hex = str(payload.get('id_hex') or '')
        if id_hex == F103_HEALTH_ID_HEX:
            self.last_health_payload = payload
        elif id_hex == F103_SENSOR_ID_HEX:
            self.last_emg_payload = payload
        else:
            self.drop_count += 1
            return

        if self.last_emg_payload is None:
            return

        now_monotonic = time.monotonic()
        if now_monotonic - self.last_upload_monotonic < self.min_interval_sec:
            return
        self.last_upload_monotonic = now_monotonic

        upload_payload = build_sensor_state_upload_payload(
            self.last_emg_payload,
            robot_id=self.robot_id,
            device_id=self.device_id,
            project_id=self.project_id,
            now_unix=time.time(),
            health_payload=self.last_health_payload,
        )
        result = post_sensor_state(
            self.api_base_url,
            upload_payload,
            relay_token=self.relay_token,
            timeout_sec=self.timeout_sec,
        )
        if result.get('ok') is True:
            self.upload_count += 1
        else:
            self.get_logger().warn(f'sensor-state upload failed: {result}')


def main(args=None):
    if rclpy is None:
        raise RuntimeError('rclpy is required to run sensor_state_uploader_node')
    rclpy.init(args=args)
    node = SensorStateUploaderNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
