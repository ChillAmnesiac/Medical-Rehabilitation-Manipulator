#include "voice_mode_request_guard.h"

#include <stddef.h>

static uint32_t voice_mode_is_supported(voice_mode_target_t mode)
{
    return (mode == VOICE_MODE_PASSIVE) ||
           (mode == VOICE_MODE_ASSIST) ||
           (mode == VOICE_MODE_RESIST);
}

void voice_mode_guard_init(voice_mode_guard_t *guard)
{
    if (guard != NULL)
    {
        guard->committed_epoch = 0U;
        guard->committed_request_id = 0U;
    }
}

voice_mode_decision_t voice_mode_guard_decide(
    const voice_mode_guard_t *guard,
    const voice_mode_request_t *request,
    uint32_t now_tick,
    voice_mode_target_t current_mode,
    uint32_t owner_action_active,
    uint32_t active_preconditions_met)
{
    int32_t age;
    uint32_t epoch_changed;

    if ((guard == NULL) || (request == NULL) ||
        (request->source != VOICE_MODE_SOURCE_VOICE) ||
        (request->boot_epoch == 0U) || (request->request_id == 0U) ||
        (request->joint_mask != VOICE_MODE_JOINT_MASK) ||
        (request->ttl_ms == 0U) ||
        (request->ttl_ms > VOICE_MODE_MAX_TTL_MS) ||
        !voice_mode_is_supported(request->target_mode) ||
        !voice_mode_is_supported(current_mode))
    {
        return VOICE_MODE_DECISION_REJECT_INVALID;
    }

    age = (int32_t)(now_tick - request->received_tick);
    if ((age < 0) || ((uint32_t)age > request->ttl_ms))
    {
        return VOICE_MODE_DECISION_REJECT_EXPIRED;
    }

    epoch_changed = (guard->committed_epoch != 0U) &&
                    (request->boot_epoch != guard->committed_epoch);
    if (!epoch_changed && (request->boot_epoch == guard->committed_epoch))
    {
        if (request->request_id == guard->committed_request_id)
        {
            return VOICE_MODE_DECISION_REJECT_DUPLICATE;
        }
        if (request->request_id < guard->committed_request_id)
        {
            return VOICE_MODE_DECISION_REJECT_STALE;
        }
    }

    if (request->target_mode == VOICE_MODE_PASSIVE)
    {
        return VOICE_MODE_DECISION_APPLY_PASSIVE;
    }

    if (epoch_changed &&
        ((owner_action_active != 0U) || (current_mode != VOICE_MODE_PASSIVE)))
    {
        return VOICE_MODE_DECISION_NEEDS_REARM;
    }

    if ((current_mode != VOICE_MODE_PASSIVE) &&
        (current_mode != request->target_mode))
    {
        return VOICE_MODE_DECISION_NEEDS_PASSIVE;
    }

    if ((current_mode == VOICE_MODE_PASSIVE) &&
        (active_preconditions_met == 0U))
    {
        return VOICE_MODE_DECISION_REJECT_PRECONDITION;
    }

    return VOICE_MODE_DECISION_APPLY_ACTIVE;
}

void voice_mode_guard_commit(voice_mode_guard_t *guard,
                             const voice_mode_request_t *request)
{
    if ((guard != NULL) && (request != NULL))
    {
        guard->committed_epoch = request->boot_epoch;
        guard->committed_request_id = request->request_id;
    }
}
