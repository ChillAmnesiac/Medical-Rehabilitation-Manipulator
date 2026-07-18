#include "rehab_assist_safety.h"

rt_bool_t rehab_assist_overspeed(const control_motor_feedback_t *feedback,
                                  float max_velocity_rad_s)
{
    float velocity_rad_s;

    if ((feedback == RT_NULL) || (max_velocity_rad_s <= 0.0f))
    {
        return RT_FALSE;
    }

    velocity_rad_s = feedback->vel_rad_s;
    if (velocity_rad_s < 0.0f)
    {
        velocity_rad_s = -velocity_rad_s;
    }

    return (velocity_rad_s > max_velocity_rad_s) ? RT_TRUE : RT_FALSE;
}
