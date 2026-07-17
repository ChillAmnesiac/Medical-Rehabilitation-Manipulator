import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "applications" / "control" / "voice_active_precheck.c"


def test_voice_active_precheck_runtime_gates(tmp_path):
    (tmp_path / "rtthread.h").write_text(
        """
#ifndef RTTHREAD_H
#define RTTHREAD_H
#include <stdint.h>
#include <stdio.h>
typedef int rt_err_t;
typedef uint8_t rt_uint8_t;
typedef uint16_t rt_uint16_t;
typedef uint32_t rt_uint32_t;
typedef uint64_t rt_uint64_t;
typedef int16_t rt_int16_t;
typedef uint32_t rt_tick_t;
typedef uintptr_t rt_base_t;
typedef uint8_t rt_bool_t;
#define RT_TRUE 1
#define RT_FALSE 0
#define RT_NULL ((void *)0)
#define RT_EOK 0
#define RT_ERROR 1
#define RT_EINVAL 22
#define RT_TICK_PER_SECOND 1000U
#define rt_kprintf printf
rt_tick_t rt_tick_get(void);
rt_base_t rt_hw_interrupt_disable(void);
void rt_hw_interrupt_enable(rt_base_t level);
#endif
""",
        encoding="ascii",
    )
    (tmp_path / "finsh.h").write_text(
        "#define MSH_CMD_EXPORT(fn, desc) "
        "static void *export_##fn __attribute__((used)) = (void *)&fn\n",
        encoding="ascii",
    )
    (tmp_path / "control_layer.h").write_text(
        """
#ifndef CONTROL_LAYER_H
#define CONTROL_LAYER_H
#include <rtthread.h>
typedef enum {
    CONTROL_MOTOR_PROTOCOL_TYPE_PRIVATE = 0,
    CONTROL_MOTOR_PROTOCOL_TYPE_CANSIMPLE = 1
} control_motor_protocol_type_t;
typedef struct {
    rt_uint8_t motor_id;
    control_motor_protocol_type_t protocol;
    rt_uint8_t mode_state;
    rt_uint8_t fault_summary;
    float pos_rad;
    float vel_rad_s;
    float torque_nm;
    float temp_c;
    rt_tick_t timestamp;
} control_motor_feedback_t;
rt_bool_t control_layer_is_initialized(void);
rt_err_t control_get_motor_feedback(rt_uint8_t joint_id, control_motor_feedback_t *out);
rt_bool_t control_motor_is_joint_calibrated(rt_uint8_t joint_id);
#endif
""",
        encoding="ascii",
    )
    harness = tmp_path / "harness.c"
    harness.write_text(
        """
#include <assert.h>
#include <string.h>
#include "voice_active_precheck.h"
#include "control_layer.h"

static rt_bool_t initialized = RT_TRUE;
static rt_bool_t calibrated = RT_TRUE;
static rt_bool_t have_feedback = RT_TRUE;
static rt_tick_t now_tick = 1000U;
static control_motor_feedback_t feedback;

rt_tick_t rt_tick_get(void) { return now_tick; }
rt_base_t rt_hw_interrupt_disable(void) { return 0U; }
void rt_hw_interrupt_enable(rt_base_t level) { (void)level; }
rt_bool_t control_layer_is_initialized(void) { return initialized; }
rt_bool_t control_motor_is_joint_calibrated(rt_uint8_t joint) {
    assert(joint == 5U); return calibrated;
}
rt_err_t control_get_motor_feedback(rt_uint8_t joint, control_motor_feedback_t *out) {
    assert(joint == 5U);
    if (!have_feedback) return -RT_ERROR;
    *out = feedback;
    return RT_EOK;
}

static rt_uint32_t assess(void) {
    control_voice_precheck_result_t result;
    assert(control_voice_precheck_assess(&result) == RT_EOK);
    return result.reason_mask;
}

int main(void) {
    control_voice_precheck_diag_t diag;
    memset(&feedback, 0, sizeof(feedback));
    feedback.motor_id = 5U;
    feedback.protocol = CONTROL_MOTOR_PROTOCOL_TYPE_PRIVATE;
    feedback.mode_state = 0U;
    feedback.fault_summary = 0U;
    feedback.timestamp = 950U;
    assert(assess() == 0U);

    feedback.fault_summary = 0x02U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_FAULT);
    feedback.fault_summary = 0x20U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_FAULT);
    feedback.fault_summary = 0U;

    feedback.timestamp = 899U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_STALE);
    feedback.timestamp = 950U;
    feedback.motor_id = 6U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_ID);
    feedback.motor_id = 5U;
    feedback.protocol = CONTROL_MOTOR_PROTOCOL_TYPE_CANSIMPLE;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_PROTOCOL);
    feedback.protocol = CONTROL_MOTOR_PROTOCOL_TYPE_PRIVATE;

    now_tick = 20U;
    feedback.timestamp = 0xFFFFFFE2U;
    assert(assess() == 0U);
    now_tick = 1000U;
    feedback.timestamp = 950U;

    calibrated = RT_FALSE;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_CALIBRATION);
    calibrated = RT_TRUE;
    feedback.mode_state = 1U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_MODE);
    feedback.mode_state = 2U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_MODE);
    feedback.mode_state = 3U;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_MODE);
    feedback.mode_state = 0U;

    have_feedback = RT_FALSE;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_NO_FEEDBACK);
    have_feedback = RT_TRUE;
    initialized = RT_FALSE;
    assert(assess() & CONTROL_VOICE_PRECHECK_REJECT_NOT_INIT);

    control_voice_precheck_diag_snapshot(&diag);
    assert(diag.total == 13U);
    assert(diag.pass == 2U);
    assert(diag.reject_fault == 2U);
    assert(diag.reject_mode == 3U);
    return 0;
}
""",
        encoding="ascii",
    )
    exe = tmp_path / "voice_precheck.exe"
    subprocess.run(
        [
            "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(tmp_path),
            "-I", str(ROOT / "applications" / "control"),
            str(SOURCE), str(harness), "-o", str(exe),
        ],
        check=True,
    )
    subprocess.run([str(exe)], check=True)


def test_voice_precheck_has_no_motion_side_effects():
    source = SOURCE.read_text(encoding="utf-8")
    forbidden = (
        "control_motor_enable(",
        "control_motor_current_control(",
        "control_motor_stop(",
        "control_motor_set_run_mode(",
        "rehab_service_",
        "rehab_mode_manager_",
        "ctrl_can_send(",
    )
    for call in forbidden:
        assert call not in source
    for raw_gate in ("feedback.pos_rad", "feedback.torque_nm", "feedback.temp_c"):
        assert raw_gate not in source
    assert "MSH_CMD_EXPORT(cmd_voice_precheck" in source
    assert "CONTROL_VOICE_PRECHECK_JOINT_ID 5U" in source
    assert "CONTROL_VOICE_PRECHECK_JOINT_MASK 0x10U" in source
