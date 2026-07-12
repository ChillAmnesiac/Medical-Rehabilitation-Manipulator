from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m33_xiaozhi_latency_contract() -> None:
    comm = (ROOT / "applications" / "common" / "m33_m55_comm.h").read_text(encoding="utf-8")
    bridge = (ROOT / "applications" / "m33" / "m55_model_bridge.c").read_text(encoding="utf-8")
    qa = (ROOT / "applications" / "m33" / "m55_qa_bridge.c").read_text(encoding="utf-8")

    assert "MSG_TYPE_VOICE_LATENCY" in comm
    assert "voice_latency_msg_t" in comm
    assert "VOICE_LATENCY_FLAG_QA_TEXT" in comm
    assert "case MSG_TYPE_VOICE_LATENCY:" in bridge
    assert "m55_model_bridge_get_voice_latency" in bridge
    assert "m55qa_xz_latency" in qa
    assert "speech_end_to_first_write_ms" in qa
    assert "MSH_CMD_EXPORT(m55qa_xz_latency" in qa


if __name__ == "__main__":
    test_m33_xiaozhi_latency_contract()
