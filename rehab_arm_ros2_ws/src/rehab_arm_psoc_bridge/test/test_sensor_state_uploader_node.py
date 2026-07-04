from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rehab_arm_psoc_bridge.f103_sensor_state import (  # noqa: E402
    parse_f103_health_payload,
    parse_f103_sensor_payload,
)
from rehab_arm_psoc_bridge.sensor_state_uploader_node import (  # noqa: E402
    build_sensor_state_upload_payload,
    make_sensor_state_request,
    post_sensor_state,
    sensor_state_url,
)


class FakeResponse:
    status = 200

    def read(self) -> bytes:
        return b'{"ok":true}'


class SensorStateUploaderTests(unittest.TestCase):
    def test_sensor_state_url_accepts_server_root_or_api_root(self) -> None:
        self.assertEqual(
            sensor_state_url('http://server.local', 'nanopi-m5'),
            'http://server.local/api/rehab-arm/v1/devices/nanopi-m5/sensor-state',
        )
        self.assertEqual(
            sensor_state_url('http://server.local/api/rehab-arm/v1/', 'nanopi-m5'),
            'http://server.local/api/rehab-arm/v1/devices/nanopi-m5/sensor-state',
        )

    def test_build_upload_payload_wraps_emg_and_health_without_raw_can_top_level(self) -> None:
        sensor = parse_f103_sensor_payload(bytes.fromhex('E803D007B80BA00F'))
        health = parse_f103_health_payload(bytes([2, 3, 0, 128]))
        payload = build_sensor_state_upload_payload(
            sensor,
            robot_id='rehab-arm-alpha',
            device_id='nanopi-m5',
            project_id='project-1',
            now_unix=123.5,
            health_payload=health,
        )

        self.assertEqual(payload['robot_id'], 'rehab-arm-alpha')
        self.assertEqual(payload['device_id'], 'nanopi-m5')
        self.assertEqual(payload['project_id'], 'project-1')
        self.assertEqual(payload['ts_unix'], 123.5)
        self.assertEqual(payload['source'], 'nanopi_ros2_f103_can_gateway')
        self.assertNotIn('data', payload)
        emg = payload['emg']
        self.assertEqual(emg['channel_count'], 4)
        self.assertEqual(emg['voltage_reference_v'], 3.3)
        self.assertEqual(emg['voltage_unit'], 'V')
        self.assertEqual(emg['channels'][0]['raw_adc'], 1000)
        self.assertEqual(emg['channels'][2]['muscle'], 'anterior_deltoid')
        self.assertEqual(emg['channels'][3]['channel'], 'ch4')
        self.assertEqual(emg['channels'][3]['muscle'], 'forearm_extensor')
        self.assertAlmostEqual(emg['channels'][3]['voltage_v'], 4000 * 3.3 / 4095, places=6)
        self.assertEqual(emg['transport']['source_can_id'], '0x7C2')
        self.assertEqual(emg['f103_health']['state'], 'streaming')

    def test_build_upload_payload_pads_missing_emg_channels_with_zeroes(self) -> None:
        payload = build_sensor_state_upload_payload(
            {'source': 'f103_sensor', 'id_hex': '0x7C2'},
            robot_id='rehab-arm-alpha',
            device_id='nanopi-m5',
            project_id='project-1',
            now_unix=123.5,
        )

        emg = payload['emg']
        self.assertEqual(emg['schema_version'], 'rehab_arm_emg4_adc_v1')
        self.assertEqual(emg['channel_count'], 4)
        self.assertEqual([channel['channel'] for channel in emg['channels']], ['ch1', 'ch2', 'ch3', 'ch4'])
        self.assertEqual([channel['raw_adc'] for channel in emg['channels']], [0, 0, 0, 0])
        self.assertEqual([channel['activation'] for channel in emg['channels']], [0.0, 0.0, 0.0, 0.0])
        self.assertEqual([channel['voltage_v'] for channel in emg['channels']], [0.0, 0.0, 0.0, 0.0])
        self.assertEqual(emg['signal_quality']['status'], 'degraded')

    def test_make_request_posts_schema_payload(self) -> None:
        payload = {
            'robot_id': 'rehab-arm-alpha',
            'device_id': 'nanopi-m5',
            'project_id': 'project-1',
            'ts_unix': 1.0,
            'emg': {'channels': []},
            'source': 'nanopi_ros2_f103_can_gateway',
        }
        http_request = make_sensor_state_request(
            'http://server.local/api/rehab-arm/v1',
            payload,
            relay_token='token-1',
        )

        self.assertEqual(
            http_request.full_url,
            'http://server.local/api/rehab-arm/v1/devices/nanopi-m5/sensor-state',
        )
        self.assertEqual(http_request.get_method(), 'POST')
        self.assertEqual(http_request.headers['Authorization'], 'Bearer token-1')
        self.assertEqual(json.loads(http_request.data.decode('utf-8')), payload)

    def test_post_sensor_state_uses_opener(self) -> None:
        seen = []

        def opener(http_request, timeout_sec):
            seen.append((http_request.full_url, timeout_sec))
            return FakeResponse()

        result = post_sensor_state(
            'http://server.local',
            {
                'robot_id': 'rehab-arm-alpha',
                'device_id': 'nanopi-m5',
                'project_id': 'project-1',
                'ts_unix': 1.0,
                'emg': {'channels': []},
                'source': 'nanopi_ros2_f103_can_gateway',
            },
            timeout_sec=2.0,
            opener=opener,
        )

        self.assertIs(result['ok'], True)
        self.assertEqual(
            seen,
            [('http://server.local/api/rehab-arm/v1/devices/nanopi-m5/sensor-state', 2.0)],
        )


if __name__ == '__main__':
    unittest.main()
