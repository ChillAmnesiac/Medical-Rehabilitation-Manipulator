import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAG_H = ROOT / "applications" / "m33" / "app_ble_diag.h"
DIAG_C = ROOT / "applications" / "m33" / "app_ble_diag.c"
RUNTIME_GATE_C = ROOT / "applications" / "m33" / "bt_runtime_gate.c"
HCI_PORT_C = ROOT / "applications" / "m33" / "bt_hci_uart_platform_port.c"


class M33BleDiagStaticTest(unittest.TestCase):
    def test_bounded_snapshot_api_exists(self):
        header = DIAG_H.read_text(encoding="utf-8")

        self.assertIn("app_ble_diag_snapshot_t", header)
        for field in (
            "gatt_events",
            "rx_drops",
            "rx_queue_peak",
            "tx_queue_peak",
            "notify_failures",
            "hci_rx_queue_percent",
            "hci_tx_queue_percent",
            "heap_free_bytes",
            "heap_min_free_bytes",
            "hci_tx_largest_free_bytes",
        ):
            self.assertRegex(header, rf"rt_uint32_t\s+{field}\s*;")
        self.assertIn("void app_ble_diag_snapshot(app_ble_diag_snapshot_t *out);", header)

    def test_shell_snapshot_uses_public_runtime_metrics(self):
        source = DIAG_C.read_text(encoding="utf-8")

        self.assertIn("rt_memory_info(", source)
        self.assertIn("cybt_platform_task_get_queue_utilization(BT_TASK_ID_HCI_RX)", source)
        self.assertIn("cybt_platform_task_get_queue_utilization(BT_TASK_ID_HCI_TX)", source)
        self.assertIn("cybt_platform_task_get_tx_heap_utilization(", source)
        self.assertIn("MSH_CMD_EXPORT_ALIAS(cmd_m33_ble_diag, m33_ble_diag", source)
        self.assertIn("BLE_DIAG_STACK_HIGH", source)
        self.assertIn("tx_heap_source=unsupported", source)
        self.assertIn("largest_free=unsupported", source)
        self.assertIn("rehab_svc", source)
        self.assertIn("tshell", source)

    def test_hci_queue_peak_sampling_is_wired_without_logging(self):
        diag_source = DIAG_C.read_text(encoding="utf-8")
        source = HCI_PORT_C.read_text(encoding="utf-8")

        self.assertIn('#include "app_ble_diag.h"', source)
        self.assertIn("app_ble_diag_note_hci_queue_percent(task_id", source)
        self.assertIn("percent == CYBT_INVALID_QUEUE_UTILIZATION", diag_source)

    def test_runtime_remains_default_off_and_only_registers_diagnostics(self):
        source = RUNTIME_GATE_C.read_text(encoding="utf-8")

        self.assertRegex(
            source,
            re.compile(
                r"#ifndef\s+M33_ENABLE_APP_BLE_RUNTIME\s*\n"
                r"#define\s+M33_ENABLE_APP_BLE_RUNTIME\s+0",
                re.MULTILINE,
            ),
        )
        self.assertNotIn("m33_ble_gate_start();\nINIT_", source)


if __name__ == "__main__":
    unittest.main()
