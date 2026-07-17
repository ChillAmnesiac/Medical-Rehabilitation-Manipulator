from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "applications" / "m33" / "voice_rehab_ipc_bridge.h"
SOURCE = ROOT / "applications" / "m33" / "voice_rehab_ipc_bridge.c"


def test_voice_rehab_ipc_bridge_is_bounded_and_control_free():
    header = HEADER.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")

    assert "VOICE_REHAB_IPC_QUEUE_DEPTH 4U" in header
    assert "voice_rehab_ipc_bridge_submit" in header
    assert "voice_rehab_ipc_bridge_diag_snapshot" in header
    assert "rt_mq_init" in source
    assert "rt_mq_send" in source
    assert "rt_tick_get()" in source
    assert "rt_mq_recv" in source
    assert "recv_size != (rt_ssize_t)sizeof(item)" in source
    assert "rehab_mode_manager_apply_command" in source
    assert "rehab_service_adjust_intensity_level" in source
    assert "m33_m55_comm_try_publish" in source


def test_voice_rehab_ipc_worker_keeps_ownership_and_guard_gates():
    source = SOURCE.read_text(encoding="utf-8")

    assert "voice_mode_guard_decide" in source
    assert "voice_mode_guard_commit" in source
    assert "control_voice_precheck_assess" in source
    assert "status.source != REHAB_CMD_SOURCE_VOICE" in source
    assert "VOICE_MODE_DECISION_ALREADY_ACTIVE" in source
    assert source.count("result_status == REHAB_MODE_RESULT_NONE") >= 2
    assert "REHAB_MODE_RESULT_QUEUE_FULL" in source
    assert "REHAB_MODE_RESULT_APPLIED" in source


def test_voice_rehab_ipc_bridge_validates_v2_request_fields():
    source = SOURCE.read_text(encoding="utf-8")

    for token in (
        "REHAB_MODE_PROTOCOL_VERSION",
        "REHAB_MODE_SOURCE_VOICE",
        "REHAB_MODE_JOINT_MASK",
        "REHAB_MODE_MAX_TTL_MS",
        "REHAB_MODE_ACTION_SET_MODE",
        "REHAB_MODE_ACTION_LEVEL_UP",
        "REHAB_MODE_ACTION_LEVEL_DOWN",
    ):
        assert token in source
