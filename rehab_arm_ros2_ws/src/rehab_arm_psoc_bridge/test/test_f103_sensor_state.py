from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rehab_arm_psoc_bridge.f103_sensor_state import (  # noqa: E402
    parse_f103_health_payload,
    parse_f103_sensor_payload,
)


class F103SensorStateTests(unittest.TestCase):
    def test_parse_sensor_payload(self) -> None:
        payload = parse_f103_sensor_payload(bytes.fromhex('E803D007B80BA00F'))

        self.assertEqual(payload['schema_version'], 'rehab_arm_sensor_state_v1')
        self.assertEqual(payload['source'], 'f103_sensor')
        self.assertEqual(payload['sensor_node'], 'stm32_f103_emg3')
        self.assertEqual(payload['physical_source'], 'stm32_f103_emg3_can_0x7c2')
        self.assertEqual(payload['payload_format'], 'adc4_le_u16_v1')
        self.assertEqual(payload['id_hex'], '0x7C2')
        self.assertEqual(payload['adc_raw'], [1000, 2000, 3000, 4000])
        self.assertEqual(payload['emg4_raw'], [1000, 2000, 3000, 4000])
        self.assertEqual(payload['emg3_raw'], [1000, 2000, 3000])
        self.assertEqual(payload['debug_adc_raw'], 4000)
        self.assertEqual(payload['emg_raw'], 1000)
        self.assertEqual(payload['emg']['schema_version'], 'rehab_arm_emg4_adc_v1')
        self.assertEqual(payload['emg']['sample_unit'], 'adc_counts')
        self.assertEqual(payload['emg']['voltage_reference_v'], 3.3)
        self.assertEqual(payload['emg']['voltage_unit'], 'V')
        self.assertEqual(len(payload['emg']['channels']), 4)
        self.assertEqual(payload['emg']['channels'][0]['channel'], 'ch1')
        self.assertEqual(payload['emg']['channels'][0]['muscle'], 'biceps')
        self.assertAlmostEqual(payload['emg']['channels'][0]['voltage_v'], 1000 * 3.3 / 4095, places=6)
        self.assertEqual(payload['emg']['channels'][1]['muscle'], 'triceps')
        self.assertEqual(payload['emg']['channels'][2]['muscle'], 'anterior_deltoid')
        self.assertEqual(payload['emg']['channels'][2]['raw_adc'], 3000)
        self.assertAlmostEqual(payload['emg']['channels'][2]['activation'], 3000 / 4095, places=6)
        self.assertEqual(payload['emg']['channels'][3]['channel'], 'ch4')
        self.assertEqual(payload['emg']['channels'][3]['muscle'], 'forearm_extensor')
        self.assertEqual(payload['emg']['channels'][3]['raw_adc'], 4000)
        self.assertAlmostEqual(payload['emg']['channels'][3]['voltage_v'], 4000 * 3.3 / 4095, places=6)
        self.assertEqual(payload['muscle_signals']['biceps'], payload['emg']['channels'][0]['activation'])
        self.assertEqual(payload['muscle_signals']['forearm_extensor'], payload['emg']['channels'][3]['activation'])
        self.assertEqual(payload['control_boundary'], 'telemetry_only_not_motion_permission')

    def test_parse_short_sensor_payload_is_invalid_but_keeps_raw_data(self) -> None:
        payload = parse_f103_sensor_payload(bytes.fromhex('010203'))

        self.assertIs(payload['valid'], False)
        self.assertEqual(payload['detail'], 'short_frame')
        self.assertEqual(payload['dlc'], 3)
        self.assertEqual(payload['data'], '010203')

    def test_parse_health_payload(self) -> None:
        payload = parse_f103_health_payload(bytes([2, 3, 0, 128]))

        self.assertEqual(payload['schema_version'], 'rehab_arm_sensor_health_v1')
        self.assertEqual(payload['source'], 'f103_health')
        self.assertEqual(payload['sensor_node'], 'stm32_f103_emg3')
        self.assertEqual(payload['physical_source'], 'stm32_f103_health_can_0x7c3')
        self.assertEqual(payload['id_hex'], '0x7C3')
        self.assertEqual(payload['state_code'], 2)
        self.assertEqual(payload['state'], 'streaming')
        self.assertEqual(payload['error_count'], 3)
        self.assertEqual(payload['queue_fill'], 128)
        self.assertEqual(payload['queue_fill_percent'], 50.2)

    def test_parse_unknown_health_state(self) -> None:
        payload = parse_f103_health_payload(bytes([99, 0, 0, 0]))

        self.assertEqual(payload['state'], 'unknown')
        self.assertIs(payload['valid'], True)


if __name__ == '__main__':
    unittest.main()
