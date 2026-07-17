from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_C = ROOT / "applications" / "m33" / "m55_model_bridge.c"
BRIDGE_H = ROOT / "applications" / "m33" / "m55_model_bridge.h"


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1:index]
    raise AssertionError(f"unterminated function: {signature}")


def test_latency_observer_is_read_only_and_nonblocking() -> None:
    bridge = BRIDGE_C.read_text(encoding="utf-8")
    handler = _function_body(
        bridge, "static void m55_model_bridge_handle_voice_latency"
    )

    assert "case MSG_TYPE_VOICE_LATENCY:" in bridge
    assert "m55_model_bridge_handle_voice_latency(msg);" in bridge
    assert "rt_hw_interrupt_disable()" in handler
    assert "rt_hw_interrupt_enable(level)" in handler
    assert "rt_kprintf" not in handler
    assert "rt_malloc" not in handler
    assert "control_" not in handler
    assert "can" not in handler.lower()


def test_latency_observer_validates_and_preserves_latest_good_sample() -> None:
    bridge = BRIDGE_C.read_text(encoding="utf-8")
    header = BRIDGE_H.read_text(encoding="utf-8")
    handler = _function_body(
        bridge, "static void m55_model_bridge_handle_voice_latency"
    )

    assert "VOICE_LATENCY_ALLOWED_FLAGS" in bridge
    assert "VOICE_LATENCY_FLAG_VALID" in bridge
    assert "VOICE_LATENCY_FLAG_REAL_WAKE" in bridge
    assert "VOICE_LATENCY_FLAG_MANUAL" in bridge
    assert "invalid_count++" in handler
    assert "stale_count++" in handler
    assert handler.index("invalid_count++") < handler.index("latency = *latency")
    assert handler.index("stale_count++") < handler.index("latency = *latency")
    assert "dropped_count" in handler
    assert "m55_voice_latency_snapshot_t" in header
    assert "m55_model_bridge_get_voice_latency" in header


if __name__ == "__main__":
    test_latency_observer_is_read_only_and_nonblocking()
    test_latency_observer_validates_and_preserves_latest_good_sample()
