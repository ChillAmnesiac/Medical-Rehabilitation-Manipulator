#include "voice_rehab_ipc_bridge.h"

typedef struct
{
    rehab_mode_request_msg_t request;
    rt_tick_t received_tick;
} voice_rehab_ipc_queue_item_t;

static struct rt_messagequeue s_voice_rehab_mq;
static rt_uint8_t s_voice_rehab_mq_pool[
    RT_MQ_BUF_SIZE(sizeof(voice_rehab_ipc_queue_item_t),
                   VOICE_REHAB_IPC_QUEUE_DEPTH)];
static voice_rehab_ipc_bridge_diag_t s_voice_rehab_diag;
static rt_bool_t s_voice_rehab_initialized;

static rt_bool_t voice_rehab_mode_supported(rt_uint32_t mode)
{
    return ((mode == REHAB_MODE_REQUEST_MODE_PASSIVE) ||
            (mode == REHAB_MODE_REQUEST_MODE_ASSIST) ||
            (mode == REHAB_MODE_REQUEST_MODE_RESIST))
               ? RT_TRUE
               : RT_FALSE;
}

static rt_bool_t voice_rehab_action_supported(rt_uint32_t action,
                                              rt_uint32_t mode)
{
    if (action == REHAB_MODE_ACTION_SET_MODE)
    {
        return RT_TRUE;
    }
    if ((action == REHAB_MODE_ACTION_LEVEL_UP) ||
        (action == REHAB_MODE_ACTION_LEVEL_DOWN))
    {
        return ((mode == REHAB_MODE_REQUEST_MODE_ASSIST) ||
                (mode == REHAB_MODE_REQUEST_MODE_RESIST))
                   ? RT_TRUE
                   : RT_FALSE;
    }
    return RT_FALSE;
}

static rt_bool_t voice_rehab_request_valid(const rehab_mode_request_msg_t *request)
{
    return ((request != RT_NULL) &&
            (request->version == REHAB_MODE_PROTOCOL_VERSION) &&
            (request->boot_epoch != 0U) &&
            (request->request_id != 0U) &&
            (request->source == REHAB_MODE_SOURCE_VOICE) &&
            voice_rehab_mode_supported(request->mode) &&
            (request->joint_mask == REHAB_MODE_JOINT_MASK) &&
            (request->ttl_ms != 0U) &&
            (request->ttl_ms <= REHAB_MODE_MAX_TTL_MS) &&
            voice_rehab_action_supported(request->action, request->mode))
               ? RT_TRUE
               : RT_FALSE;
}

rt_err_t voice_rehab_ipc_bridge_init(void)
{
    rt_err_t ret;

    if (s_voice_rehab_initialized)
    {
        return RT_EOK;
    }

    rt_memset(&s_voice_rehab_diag, 0, sizeof(s_voice_rehab_diag));
    ret = rt_mq_init(&s_voice_rehab_mq,
                     "vrehab",
                     s_voice_rehab_mq_pool,
                     sizeof(voice_rehab_ipc_queue_item_t),
                     sizeof(s_voice_rehab_mq_pool),
                     RT_IPC_FLAG_FIFO);
    if (ret == RT_EOK)
    {
        s_voice_rehab_initialized = RT_TRUE;
    }
    return ret;
}

rt_err_t voice_rehab_ipc_bridge_submit(const rehab_mode_request_msg_t *request)
{
    voice_rehab_ipc_queue_item_t item;
    rt_err_t ret;
    rt_base_t level;

    level = rt_hw_interrupt_disable();
    s_voice_rehab_diag.total++;
    rt_hw_interrupt_enable(level);

    if (!s_voice_rehab_initialized || !voice_rehab_request_valid(request))
    {
        level = rt_hw_interrupt_disable();
        s_voice_rehab_diag.invalid++;
        rt_hw_interrupt_enable(level);
        return -RT_EINVAL;
    }

    item.request = *request;
    item.received_tick = rt_tick_get();
    ret = rt_mq_send(&s_voice_rehab_mq, &item, sizeof(item));

    level = rt_hw_interrupt_disable();
    s_voice_rehab_diag.last_request_id = request->request_id;
    s_voice_rehab_diag.last_receive_tick = item.received_tick;
    if (ret == RT_EOK)
    {
        s_voice_rehab_diag.accepted++;
    }
    else
    {
        s_voice_rehab_diag.queue_full++;
    }
    rt_hw_interrupt_enable(level);
    return ret;
}

void voice_rehab_ipc_bridge_diag_snapshot(voice_rehab_ipc_bridge_diag_t *out)
{
    rt_base_t level;

    if (out == RT_NULL)
    {
        return;
    }

    level = rt_hw_interrupt_disable();
    *out = s_voice_rehab_diag;
    rt_hw_interrupt_enable(level);
}
