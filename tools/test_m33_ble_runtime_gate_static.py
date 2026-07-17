from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATE_C = (ROOT / "applications" / "m33" / "bt_runtime_gate.c").read_text(encoding="utf-8")


class M33BleRuntimeGateStaticTest(unittest.TestCase):
    def test_runtime_is_disabled_by_default_and_never_auto_started(self):
        self.assertIn("#define M33_ENABLE_APP_BLE_RUNTIME 0", GATE_C)
        self.assertNotIn("INIT_APP_EXPORT", GATE_C)
        self.assertNotIn("INIT_ENV_EXPORT", GATE_C)

    def test_manual_start_is_single_owner_and_ordered(self):
        self.assertIn("M33_BLE_GATE_STARTING", GATE_C)
        self.assertIn("M33_BLE_GATE_FAILED", GATE_C)
        start = GATE_C.index("static rt_err_t m33_ble_gate_start")
        end = GATE_C.index("static int cmd_m33_ble_start", start)
        body = GATE_C[start:end]
        calls = [
            "app_ble_service_init()",
            "app_ble_service_start()",
            "bt_hci_transport_init()",
            "bt_hci_transport_start()",
        ]
        positions = [body.index(call) for call in calls]
        self.assertEqual(positions, sorted(positions))

    def test_shell_exposes_start_and_status_only(self):
        self.assertIn("MSH_CMD_EXPORT_ALIAS(cmd_m33_ble_start", GATE_C)
        self.assertIn("MSH_CMD_EXPORT_ALIAS(cmd_m33_ble_status", GATE_C)
        self.assertNotIn("clear_bonds", GATE_C)
        self.assertNotIn("deinit", GATE_C.lower())


if __name__ == "__main__":
    unittest.main()
