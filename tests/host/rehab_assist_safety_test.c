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

int main(void)
{
    test_assist_overspeed_checks_both_directions();
    printf("rehab_assist_safety_test PASS\n");
    return 0;
}
