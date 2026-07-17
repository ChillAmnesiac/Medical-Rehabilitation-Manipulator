import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "applications" / "m33" / "voice_mode_request_guard.c"


HARNESS = r'''
#include <assert.h>
#include <stdint.h>

#include "voice_mode_request_guard.h"

static voice_mode_request_t request(uint32_t epoch,
                                    uint32_t id,
                                    uint32_t mode,
                                    uint32_t received_tick,
                                    uint32_t ttl_ms)
{
    voice_mode_request_t value = {
        VOICE_MODE_SOURCE_VOICE,
        epoch,
        id,
        VOICE_MODE_JOINT_MASK,
        mode,
        received_tick,
        ttl_ms,
    };
    return value;
}

int main(void)
{
    voice_mode_guard_t guard;
    voice_mode_request_t req;

    voice_mode_guard_init(&guard);

    req = request(0U, 1U, VOICE_MODE_ASSIST, 100U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 100U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_INVALID);
    req = request(1U, 0U, VOICE_MODE_ASSIST, 100U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 100U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_INVALID);
    req = request(1U, 1U, VOICE_MODE_ASSIST, 100U, 501U);
    assert(voice_mode_guard_decide(&guard, &req, 100U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_INVALID);
    req = request(1U, 1U, VOICE_MODE_ASSIST, 100U, 500U);
    req.joint_mask = 0x20U;
    assert(voice_mode_guard_decide(&guard, &req, 100U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_INVALID);
    req = request(1U, 1U, 99U, 100U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 100U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_INVALID);

    req = request(1U, 1U, VOICE_MODE_ASSIST, 100U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 601U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_EXPIRED);
    assert(voice_mode_guard_decide(&guard, &req, 99U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_EXPIRED);
    req = request(1U, 1U, VOICE_MODE_ASSIST, 0xfffffff0U, 32U);
    assert(voice_mode_guard_decide(&guard, &req, 0x00000008U,
                                   VOICE_MODE_PASSIVE, 0U, 1U) ==
           VOICE_MODE_DECISION_APPLY_ACTIVE);
    assert(voice_mode_guard_decide(&guard, &req, 0x00000011U,
                                   VOICE_MODE_PASSIVE, 0U, 1U) ==
           VOICE_MODE_DECISION_REJECT_EXPIRED);

    req = request(7U, 10U, VOICE_MODE_ASSIST, 1000U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 1000U, VOICE_MODE_PASSIVE,
                                   0U, 0U) == VOICE_MODE_DECISION_REJECT_PRECONDITION);
    assert(voice_mode_guard_decide(&guard, &req, 1000U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_APPLY_ACTIVE);
    voice_mode_guard_commit(&guard, &req);
    assert(voice_mode_guard_decide(&guard, &req, 1001U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_REJECT_DUPLICATE);
    req = request(7U, 9U, VOICE_MODE_PASSIVE, 1001U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 1001U, VOICE_MODE_ASSIST,
                                   1U, 0U) == VOICE_MODE_DECISION_REJECT_STALE);

    req = request(7U, 11U, VOICE_MODE_PASSIVE, 1010U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 1010U, VOICE_MODE_ASSIST,
                                   1U, 0U) == VOICE_MODE_DECISION_APPLY_PASSIVE);
    voice_mode_guard_commit(&guard, &req);

    req = request(7U, 12U, VOICE_MODE_RESIST, 1020U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 1020U, VOICE_MODE_ASSIST,
                                   1U, 1U) == VOICE_MODE_DECISION_NEEDS_PASSIVE);
    assert(voice_mode_guard_decide(&guard, &req, 1020U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_APPLY_ACTIVE);

    req = request(8U, 1U, VOICE_MODE_ASSIST, 1030U, 500U);
    assert(voice_mode_guard_decide(&guard, &req, 1030U, VOICE_MODE_RESIST,
                                   1U, 1U) == VOICE_MODE_DECISION_NEEDS_REARM);
    assert(voice_mode_guard_decide(&guard, &req, 1030U, VOICE_MODE_PASSIVE,
                                   0U, 1U) == VOICE_MODE_DECISION_APPLY_ACTIVE);

    return 0;
}
'''


def test_voice_mode_request_guard_behavior():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = pathlib.Path(temp_dir)
        harness = temp / "voice_mode_request_guard_test.c"
        executable = temp / "voice_mode_request_guard_test.exe"
        harness.write_text(HARNESS, encoding="ascii")
        compile_result = subprocess.run(
            [
                "gcc",
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I",
                str(ROOT / "applications" / "m33"),
                str(harness),
                str(SOURCE),
                "-o",
                str(executable),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert compile_result.returncode == 0, compile_result.stderr

        run_result = subprocess.run(
            [str(executable)], capture_output=True, text=True, check=False
        )
        assert run_result.returncode == 0, run_result.stderr
