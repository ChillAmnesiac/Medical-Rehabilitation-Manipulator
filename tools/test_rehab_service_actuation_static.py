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

    def test_active_mode_prepares_fresh_feedback_before_state_transition(self):
        start = SERVICE_C.index("static rt_err_t rehab_service_enter_mode_on_m33")
        end = SERVICE_C.index("static rt_err_t rehab_service_enter_mode(", start)
        body = SERVICE_C[start:end]
        self.assertIn("rehab_service_prepare_feedback(m33_joint_id)", body)
        prepare = body.index("rehab_service_prepare_feedback(m33_joint_id)")
        transition = body.index("rehab_service_apply_status_locked(")
        self.assertLess(prepare, transition)

    def test_feedback_prepare_requests_reporting_with_bounded_wait(self):
        self.assertIn("control_motor_set_active_report(m33_joint_id, RT_TRUE)", SERVICE_C)
        self.assertIn("CONTROL_REHAB_FEEDBACK_PREPARE_TIMEOUT_MS", SERVICE_C)
        self.assertIn("return -RT_ETIMEOUT;", SERVICE_C)

    def test_mask_mode_prepares_all_feedback_before_state_transition(self):
        start = SERVICE_C.index("rt_err_t rehab_service_set_mode_mask")
        end = SERVICE_C.index("rt_err_t rehab_service_set_mode_on_m33", start)
        body = SERVICE_C[start:end]
        self.assertIn("rehab_service_prepare_feedback_mask(active_joint_mask)", body)
        prepare = body.index("rehab_service_prepare_feedback_mask(active_joint_mask)")
        transition = body.index("rehab_service_apply_status_locked(")
        self.assertLess(prepare, transition)

    def test_mask_feedback_prepare_has_one_shared_timeout_window(self):
        self.assertIn("static rt_err_t rehab_service_prepare_feedback_mask", SERVICE_C)
        start = SERVICE_C.index("static rt_err_t rehab_service_prepare_feedback_mask")
        end = SERVICE_C.index("static void rehab_service_reset_all_strategy_states_locked", start)
        body = SERVICE_C[start:end]
        self.assertIn("control_motor_set_active_report(joint, RT_TRUE)", body)
        self.assertEqual(body.count("start = rt_tick_get();"), 1)
        self.assertIn("return -RT_ETIMEOUT;", body)


if __name__ == "__main__":
    unittest.main()
