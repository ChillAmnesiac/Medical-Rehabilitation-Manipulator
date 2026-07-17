from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SERVICE_C = (ROOT / "applications" / "control" / "rehab_service.c").read_text(encoding="utf-8")


class RehabServiceActuationStaticTest(unittest.TestCase):
    def test_fault_stop_is_generation_guarded_and_serialized(self):
        start = SERVICE_C.index("static void rehab_service_note_fault_mask")
        end = SERVICE_C.index("static void rehab_service_note_fault(", start)
        body = SERVICE_C[start:end]
        self.assertIn("expected_generation", body)
        self.assertIn("s_rehab.status.mode_generation != expected_generation", body)
        self.assertIn("rt_mutex_take(&s_rehab.actuation_lock", body)

    def test_failed_stop_latch_blocks_normal_mode_entry(self):
        self.assertGreaterEqual(SERVICE_C.count("if (s_rehab.stop_pending)"), 2)
        self.assertGreaterEqual(SERVICE_C.count("return -RT_EBUSY;"), 4)


if __name__ == "__main__":
    unittest.main()
