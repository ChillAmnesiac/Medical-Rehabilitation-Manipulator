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

static void test_assist_overspeed_rejects_spikes_but_trips_persistent_motion(void)
{
    rehab_assist_safety_state_t state;
    control_motor_feedback_t fb = feedback(1.459f);

    rehab_assist_safety_reset(&state);
    require_true(!rehab_assist_overspeed_step(&state, &fb, 1.0f, 2.0f, 3U),
                 "one soft-threshold spike must not trip");

    fb.vel_rad_s = 0.2f;
    require_true(!rehab_assist_overspeed_step(&state, &fb, 1.0f, 2.0f, 3U),
                 "normal motion must reset the consecutive count");

    fb.vel_rad_s = -1.2f;
    require_true(!rehab_assist_overspeed_step(&state, &fb, 1.0f, 2.0f, 3U),
                 "first persistent sample must not trip");
    require_true(!rehab_assist_overspeed_step(&state, &fb, 1.0f, 2.0f, 3U),
                 "second persistent sample must not trip");
    require_true(rehab_assist_overspeed_step(&state, &fb, 1.0f, 2.0f, 3U),
                 "third persistent sample must trip");

    rehab_assist_safety_reset(&state);
    fb.vel_rad_s = 2.01f;
    require_true(rehab_assist_overspeed_step(&state, &fb, 1.0f, 2.0f, 3U),
                 "hard-threshold overspeed must trip immediately");
}

int main(void)
{
    test_assist_overspeed_rejects_spikes_but_trips_persistent_motion();
    printf("rehab_assist_safety_test PASS\n");
    return 0;
}
