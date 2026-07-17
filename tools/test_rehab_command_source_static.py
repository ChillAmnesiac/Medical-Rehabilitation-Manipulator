from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTROL_C = (ROOT / "applications" / "control" / "control_layer.c").read_text(encoding="utf-8")
MANAGER_C = (ROOT / "applications" / "control" / "rehab_mode_manager.c").read_text(encoding="utf-8")
MANAGER_H = (ROOT / "applications" / "control" / "rehab_mode_manager.h").read_text(encoding="utf-8")
SERVICE_C = (ROOT / "applications" / "control" / "rehab_service.c").read_text(encoding="utf-8")
SERVICE_H = (ROOT / "applications" / "control" / "rehab_service.h").read_text(encoding="utf-8")
SHELL_C = (ROOT / "applications" / "control" / "rehab_shell.c").read_text(encoding="utf-8")


def body(text, start_marker, end_marker):
    start = text.index(start_marker)
    return text[start:text.index(end_marker, start)]


class RehabCommandSourceStaticTest(unittest.TestCase):
    def test_voice_is_distinct_and_command_source_is_explicit(self):
        self.assertIn("REHAB_CMD_SOURCE_VOICE", SERVICE_H)
        command = body(MANAGER_H, "typedef struct\n{\n    rehab_mode_t mode;", "} rehab_mode_command_t;")
        self.assertIn("rehab_cmd_source_t source;", command)

    def test_can_decoder_keeps_can_source(self):
        apply_can = body(CONTROL_C, "static rt_err_t ctrl_apply_rehab_mode_command", "static rt_err_t ctrl_apply_ros_command")
        self.assertIn("mode_cmd.source = REHAB_CMD_SOURCE_CAN;", apply_can)

    def test_manager_rejects_default_and_unknown_sources(self):
        apply_command = body(MANAGER_C, "rt_err_t rehab_mode_manager_apply_command", "void rehab_mode_manager_record_reject")
        self.assertIn("rehab_mode_adapter_source_supported(cmd->source)", apply_command)
        self.assertIn("return -RT_EINVAL;", apply_command)

    def test_manager_propagates_voice_without_hardcoded_can_calls(self):
        apply_command = body(MANAGER_C, "rt_err_t rehab_mode_manager_apply_command", "void rehab_mode_manager_record_reject")
        self.assertIn("rehab_service_stop(cmd->source)", apply_command)
        self.assertIn("rehab_service_record_start(0U, REHAB_JOINT_ELBOW, cmd->source)", apply_command)
        self.assertIn("rehab_service_play_start(0U, REHAB_JOINT_ELBOW, cmd->source)", apply_command)
        self.assertIn("rehab_service_set_mode_mask(service_mode, joint_mask, cmd->source)", apply_command)

    def test_conditioned_stop_accepts_only_can_or_voice_and_matches_owner(self):
        stop = body(SERVICE_C, "rt_err_t rehab_service_stop_if_owned", "rt_err_t rehab_service_record_start")
        self.assertIn("expected_source != REHAB_CMD_SOURCE_CAN", stop)
        self.assertIn("expected_source != REHAB_CMD_SOURCE_VOICE", stop)
        self.assertIn("s_rehab.status.source != expected_source", stop)
        self.assertIn("s_rehab.status.mode_generation != expected_generation", stop)
        self.assertNotIn("REHAB_CMD_SOURCE_BENCH_MSH) ||", stop)

    def test_timeout_uses_leased_owner_source_and_shell_stays_bench(self):
        tick = body(MANAGER_C, "void rehab_mode_manager_tick", "rt_bool_t rehab_mode_manager_accepts_ros_target")
        self.assertIn("expected_source", tick)
        self.assertIn("rehab_service_stop_if_owned(expected_source", tick)
        self.assertIn("REHAB_CMD_SOURCE_BENCH_MSH", SHELL_C)
        self.assertNotIn("REHAB_CMD_SOURCE_VOICE", SHELL_C)


if __name__ == "__main__":
    unittest.main()
