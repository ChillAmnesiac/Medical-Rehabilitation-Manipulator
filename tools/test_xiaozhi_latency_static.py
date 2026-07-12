from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m55_xiaozhi_latency_contract() -> None:
    comm = (ROOT / "applications" / "m33_m55_comm.h").read_text(encoding="utf-8")
    voice = (ROOT / "applications" / "voice_service.c").read_text(encoding="utf-8")

    assert "MSG_TYPE_VOICE_LATENCY" in comm
    assert "voice_latency_msg_t" in comm
    assert "VOICE_LATENCY_FLAG_QA_TEXT" in comm
    assert "voice_latency" in comm
    assert '#define XIAOZHI_EOU_SILENCE_MS       900U' in voice
    assert '#define XIAOZHI_EOU_MANUAL_MIN_RECORD_MS 900U' in voice
    assert '#define XIAOZHI_EOU_VOICE_PEAK       1200U' in voice
    assert '#define XIAOZHI_EOU_VOICE_AVG        400U' in voice
    assert '(model_result->peak >= XIAOZHI_EOU_VOICE_PEAK) &&' in voice
    assert '(model_result->avg_abs >= XIAOZHI_EOU_VOICE_AVG)' in voice
    assert 'g_service.xiaozhi_voice_seen_frames = 0U;' in voice
    assert '#define VOICE_TTS_PREBUFFER_MIN_SLOTS 1U' in voice
    assert '#define VOICE_TTS_PREBUFFER_MAX_MS   80U' in voice
    assert '"m55-%08lx-%04lx"' in voice
    assert "voice_service_publish_latency" in voice
    assert "voice_service_publish_latency(rt_tick_get());" in voice
    assert voice.index("rt_device_write(g_service.xiaozhi_speaker_dev") < voice.index("voice_service_publish_latency(rt_tick_get());")
    assert "speech_end_to_first_write_ms" in voice


if __name__ == "__main__":
    test_m55_xiaozhi_latency_contract()
