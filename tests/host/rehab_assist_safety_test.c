#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "rehab_assist_safety.h"

static void require_true(int condition, const char *message)
{
    if (!condition)
    {
        fprintf(stderr, "FAIL: %s\n", message);
        exit(1);
    }
}

static control_motor_feedback_t feedback(float velocity_rad_s)
{
    control_motor_feedback_t fb;

    memset(&fb, 0, sizeof(fb));
    fb.vel_rad_s = velocity_rad_s;
    return fb;
}

static void test_assist_overspeed_checks_both_directions(void)
{
    control_motor_feedback_t fb = feedback(0.20f);

    require_true(!rehab_assist_overspeed(&fb, 0.20f),
                 "velocity at the limit must remain allowed");

    fb.vel_rad_s = 0.201f;
    require_true(rehab_assist_overspeed(&fb, 0.20f),
                 "positive overspeed must trip");

    fb.vel_rad_s = -0.201f;
    require_true(rehab_assist_overspeed(&fb, 0.20f),
                 "negative overspeed must trip");
}

static void test_joint5_position_must_stay_inside_calibrated_range(void)
{
    control_motor_feedback_t fb = feedback(0.0f);

    fb.pos_rad = 6.000f;
    require_true(rehab_assist_position_safe(5U, &fb),
                 "joint 5 hard minimum must be allowed");

    fb.pos_rad = 8.264f;
    require_true(rehab_assist_position_safe(5U, &fb),
                 "joint 5 hard maximum must be allowed");

    fb.pos_rad = 5.801f;
    require_true(!rehab_assist_position_safe(5U, &fb),
                 "joint 5 below the hard minimum must be rejected");

    fb.pos_rad = 8.300f;
    require_true(!rehab_assist_position_safe(5U, &fb),
                 "joint 5 above the hard maximum must be rejected");
}

int main(void)
{
    test_assist_overspeed_checks_both_directions();
    test_joint5_position_must_stay_inside_calibrated_range();
    printf("rehab_assist_safety_test PASS\n");
    return 0;
}
