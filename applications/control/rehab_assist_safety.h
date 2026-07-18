#ifndef __REHAB_ASSIST_SAFETY_H__
#define __REHAB_ASSIST_SAFETY_H__

#include "rehab_strategy.h"

rt_bool_t rehab_assist_overspeed(const control_motor_feedback_t *feedback,
                                  float max_velocity_rad_s);

#endif /* __REHAB_ASSIST_SAFETY_H__ */
