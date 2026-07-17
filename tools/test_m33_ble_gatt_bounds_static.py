from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATT_C = (ROOT / "applications" / "m33" / "bt_app_gatt_handler.c").read_text(encoding="utf-8")


def body(signature, next_signature):
    start = GATT_C.index(signature)
    return GATT_C[start:GATT_C.index(next_signature, start)]


class M33BleGattBoundsStaticTest(unittest.TestCase):
    def test_event_callback_checks_pointer_before_member_access(self):
        callback = body("wiced_bt_gatt_status_t app_bt_gatt_callback", "wiced_bt_gatt_status_t app_bt_gatt_req_cb")
        self.assertLess(callback.index("p_event_data == RT_NULL"), callback.index("p_event_data->attribute_request"))

    def test_write_rejects_null_payload_and_nonzero_offset(self):
        write = body("wiced_bt_gatt_status_t app_bt_gatt_req_write_handler", "wiced_bt_gatt_status_t app_bt_gatt_req_read_by_type_handler")
        self.assertIn("p_write_req == RT_NULL", write)
        self.assertIn("p_write_req->p_val == RT_NULL", write)
        self.assertIn("p_write_req->offset != 0u", write)
        self.assertIn("WICED_BT_GATT_INVALID_OFFSET", write)

    def test_cccd_length_is_checked_before_copy(self):
        setter = body("wiced_bt_gatt_status_t app_bt_set_value", "void app_bt_free_buffer")
        self.assertLess(setter.index("HDLD_NUS_TX_CLIENT_CHAR_CONFIG"), setter.index("memcpy(p_attr->p_data"))

    def test_response_allocation_failure_is_reported(self):
        callback = body("wiced_bt_gatt_status_t app_bt_gatt_callback", "wiced_bt_gatt_status_t app_bt_gatt_req_cb")
        self.assertIn("WICED_BT_GATT_INSUF_RESOURCE", callback)


if __name__ == "__main__":
    unittest.main()
