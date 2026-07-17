#include "app_ble_worker.h"

#include <string.h>

void app_ble_reassembly_reset(app_ble_reassembly_t *state)
{
    if (state == NULL)
    {
        return;
    }

    state->length = 0u;
    state->first_fragment_ms = 0u;
    state->dropping_oversize = 0u;
}

void app_ble_reassembly_init(app_ble_reassembly_t *state)
{
    if (state == NULL)
    {
        return;
    }

    memset(state, 0, sizeof(*state));
}

void app_ble_reassembly_sync_generation(app_ble_reassembly_t *state,
                                        uint32_t generation)
{
    if ((state == NULL) || (state->generation == generation))
    {
        return;
    }

    app_ble_reassembly_reset(state);
    state->generation = generation;
}

int app_ble_reassembly_expire(app_ble_reassembly_t *state, uint32_t now_ms)
{
    uint32_t elapsed;

    if ((state == NULL) ||
        ((state->length == 0u) && (state->dropping_oversize == 0u)))
    {
        return 0;
    }

    elapsed = now_ms - state->first_fragment_ms;
    if (elapsed < APP_BLE_PARTIAL_TIMEOUT_MS)
    {
        return 0;
    }

    app_ble_reassembly_reset(state);
    return 1;
}

uint32_t app_ble_reassembly_feed(app_ble_reassembly_t *state,
                                 const uint8_t *data,
                                 uint16_t length,
                                 uint32_t now_ms,
                                 app_ble_frame_handler_t handler,
                                 void *context)
{
    uint32_t emitted = 0u;
    uint16_t i;

    if ((state == NULL) || ((length != 0u) && (data == NULL)))
    {
        return 0u;
    }

    (void)app_ble_reassembly_expire(state, now_ms);
    for (i = 0u; i < length; ++i)
    {
        uint8_t value = data[i];

        if (value == (uint8_t)'\n')
        {
            if ((state->dropping_oversize == 0u) &&
                (state->length != 0u) &&
                (handler != NULL))
            {
                uint16_t frame_length = state->length;
                if ((frame_length != 0u) &&
                    (state->data[frame_length - 1u] == (uint8_t)'\r'))
                {
                    frame_length--;
                }
                if (frame_length != 0u)
                {
                    handler(state->data, frame_length, context);
                    emitted++;
                }
            }
            app_ble_reassembly_reset(state);
            continue;
        }

        if (state->dropping_oversize != 0u)
        {
            continue;
        }
        if (state->length == 0u)
        {
            state->first_fragment_ms = now_ms;
        }
        if (state->length >= APP_BLE_FRAME_MAX)
        {
            state->length = 0u;
            state->dropping_oversize = 1u;
            continue;
        }
        state->data[state->length++] = value;
    }

    return emitted;
}

#ifdef APP_BLE_WORKER_HOST_TEST

#define APP_BLE_HOST_OK 0
#define APP_BLE_HOST_ERROR (-1)
#define APP_BLE_HOST_FULL (-2)

static app_ble_rx_message_t g_app_ble_host_queue[APP_BLE_RX_QUEUE_DEPTH];
static uint8_t g_app_ble_host_head;
static uint8_t g_app_ble_host_tail;
static uint8_t g_app_ble_host_count;
static uint32_t g_app_ble_generation;
static uint16_t g_app_ble_conn_id;
static uint32_t g_app_ble_rx_queue_drops;

static void app_ble_worker_host_clear_queue(void)
{
    g_app_ble_host_head = 0u;
    g_app_ble_host_tail = 0u;
    g_app_ble_host_count = 0u;
}

app_ble_worker_result_t app_ble_worker_init(void)
{
    app_ble_worker_host_clear_queue();
    g_app_ble_generation = 1u;
    g_app_ble_conn_id = 0u;
    g_app_ble_rx_queue_drops = 0u;
    return APP_BLE_HOST_OK;
}

app_ble_worker_result_t app_ble_worker_start(void)
{
    return APP_BLE_HOST_OK;
}

app_ble_worker_result_t app_ble_worker_begin_session(uint16_t conn_id)
{
    if (conn_id == 0u)
    {
        return APP_BLE_HOST_ERROR;
    }
    app_ble_worker_host_clear_queue();
    g_app_ble_generation++;
    g_app_ble_conn_id = conn_id;
    return APP_BLE_HOST_OK;
}

void app_ble_worker_reset_session(uint16_t conn_id)
{
    if ((conn_id != 0u) && (conn_id != g_app_ble_conn_id))
    {
        return;
    }
    g_app_ble_generation++;
    g_app_ble_conn_id = 0u;
    app_ble_worker_host_clear_queue();
}

app_ble_worker_result_t app_ble_worker_enqueue(uint16_t conn_id,
                                               const uint8_t *data,
                                               uint16_t length)
{
    app_ble_rx_message_t *message;

    if ((conn_id == 0u) || (conn_id != g_app_ble_conn_id) ||
        (data == NULL) || (length == 0u) ||
        (length > APP_BLE_RX_FRAGMENT_MAX))
    {
        return APP_BLE_HOST_ERROR;
    }
    if (g_app_ble_host_count >= APP_BLE_RX_QUEUE_DEPTH)
    {
        g_app_ble_rx_queue_drops++;
        return APP_BLE_HOST_FULL;
    }

    message = &g_app_ble_host_queue[g_app_ble_host_tail];
    message->generation = g_app_ble_generation;
    message->conn_id = conn_id;
    message->length = length;
    memcpy(message->data, data, length);
    g_app_ble_host_tail = (uint8_t)((g_app_ble_host_tail + 1u) % APP_BLE_RX_QUEUE_DEPTH);
    g_app_ble_host_count++;
    return APP_BLE_HOST_OK;
}

int app_ble_worker_host_dequeue(app_ble_rx_message_t *message)
{
    if ((message == NULL) || (g_app_ble_host_count == 0u))
    {
        return 0;
    }
    *message = g_app_ble_host_queue[g_app_ble_host_head];
    g_app_ble_host_head = (uint8_t)((g_app_ble_host_head + 1u) % APP_BLE_RX_QUEUE_DEPTH);
    g_app_ble_host_count--;
    return (int)sizeof(*message);
}

int app_ble_worker_session_is_current(uint32_t generation, uint16_t conn_id)
{
    return ((generation == g_app_ble_generation) &&
            (conn_id != 0u) &&
            (conn_id == g_app_ble_conn_id));
}

uint32_t app_ble_worker_drop_count(void)
{
    return g_app_ble_rx_queue_drops;
}

#else

#include "app_ble_diag.h"
#include "app_ble_service.h"

typedef struct
{
    uint32_t generation;
    uint16_t conn_id;
} app_ble_frame_context_t;

static struct rt_messagequeue g_app_ble_rx_mq;
static rt_uint8_t g_app_ble_rx_mq_pool[
    RT_MQ_BUF_SIZE(sizeof(app_ble_rx_message_t), APP_BLE_RX_QUEUE_DEPTH)];
static struct rt_thread g_app_ble_worker_thread;
static rt_uint8_t g_app_ble_worker_stack[APP_BLE_WORKER_STACK_SIZE];
static volatile rt_uint32_t g_app_ble_generation;
static volatile rt_uint16_t g_app_ble_conn_id;
static volatile rt_uint32_t g_app_ble_rx_queue_drops;
static rt_bool_t g_app_ble_worker_initialized;
static rt_bool_t g_app_ble_worker_started;

static rt_uint32_t app_ble_worker_next_generation(rt_uint32_t generation)
{
    generation++;
    return generation == 0u ? 1u : generation;
}

static void app_ble_worker_snapshot_session(rt_uint32_t *generation,
                                            rt_uint16_t *conn_id)
{
    rt_base_t level = rt_hw_interrupt_disable();
    if (generation != RT_NULL)
    {
        *generation = g_app_ble_generation;
    }
    if (conn_id != RT_NULL)
    {
        *conn_id = g_app_ble_conn_id;
    }
    rt_hw_interrupt_enable(level);
}

int app_ble_worker_session_is_current(uint32_t generation, uint16_t conn_id)
{
    rt_uint32_t current_generation;
    rt_uint16_t current_conn_id;

    app_ble_worker_snapshot_session(&current_generation, &current_conn_id);
    return ((generation == current_generation) &&
            (conn_id != 0u) &&
            (conn_id == current_conn_id));
}

static void app_ble_worker_handle_frame(const uint8_t *frame,
                                        uint16_t length,
                                        void *context)
{
    app_ble_frame_context_t *frame_context = (app_ble_frame_context_t *)context;
    app_ble_command_t command;
    char ascii_frame[APP_BLE_FRAME_MAX + 1u];

    if ((frame_context == RT_NULL) ||
        !app_ble_worker_session_is_current(frame_context->generation,
                                           frame_context->conn_id))
    {
        return;
    }

    rt_memcpy(ascii_frame, frame, length);
    ascii_frame[length] = '\0';
    if (app_ble_service_parse_ascii_frame(ascii_frame, &command) != RT_EOK)
    {
        return;
    }
    if (!app_ble_worker_session_is_current(frame_context->generation,
                                           frame_context->conn_id))
    {
        return;
    }
    (void)app_ble_service_submit_rx_command(&command,
                                            frame_context->generation,
                                            frame_context->conn_id);
}

static void app_ble_worker_entry(void *parameter)
{
    app_ble_reassembly_t reassembly;
    app_ble_rx_message_t message;
    app_ble_frame_context_t frame_context;
    rt_ssize_t recv_len;

    RT_UNUSED(parameter);
    app_ble_reassembly_init(&reassembly);
    while (1)
    {
        rt_uint32_t current_generation;

        app_ble_worker_snapshot_session(&current_generation, RT_NULL);
        app_ble_reassembly_sync_generation(&reassembly, current_generation);

        recv_len = rt_mq_recv(&g_app_ble_rx_mq,
                              &message,
                              sizeof(message),
                              rt_tick_from_millisecond(50u));
        if (recv_len > 0)
        {
            if ((recv_len != (rt_ssize_t)sizeof(message)) ||
                !app_ble_worker_session_is_current(message.generation,
                                                   message.conn_id))
            {
                continue;
            }
            app_ble_reassembly_sync_generation(&reassembly,
                                                message.generation);
            frame_context.generation = message.generation;
            frame_context.conn_id = message.conn_id;
            (void)app_ble_reassembly_feed(&reassembly,
                                          message.data,
                                          message.length,
                                          (uint32_t)rt_tick_get_millisecond(),
                                          app_ble_worker_handle_frame,
                                          &frame_context);
        }
        else
        {
            (void)app_ble_reassembly_expire(
                &reassembly,
                (uint32_t)rt_tick_get_millisecond());
        }
    }
}

app_ble_worker_result_t app_ble_worker_init(void)
{
    rt_err_t result;

    if (g_app_ble_worker_initialized)
    {
        return RT_EOK;
    }

    result = rt_mq_init(&g_app_ble_rx_mq,
                        "ble_rx",
                        g_app_ble_rx_mq_pool,
                        sizeof(app_ble_rx_message_t),
                        sizeof(g_app_ble_rx_mq_pool),
                        RT_IPC_FLAG_FIFO);
    if (result != RT_EOK)
    {
        return result;
    }

    result = rt_thread_init(&g_app_ble_worker_thread,
                            "ble_work",
                            app_ble_worker_entry,
                            RT_NULL,
                            g_app_ble_worker_stack,
                            sizeof(g_app_ble_worker_stack),
                            APP_BLE_WORKER_PRIORITY,
                            APP_BLE_WORKER_TICK);
    if (result != RT_EOK)
    {
        (void)rt_mq_detach(&g_app_ble_rx_mq);
        return result;
    }

    g_app_ble_generation = 1u;
    g_app_ble_conn_id = 0u;
    g_app_ble_rx_queue_drops = 0u;
    g_app_ble_worker_initialized = RT_TRUE;
    return RT_EOK;
}

app_ble_worker_result_t app_ble_worker_start(void)
{
    rt_err_t result;

    if (!g_app_ble_worker_initialized)
    {
        return -RT_ERROR;
    }
    if (g_app_ble_worker_started)
    {
        return RT_EOK;
    }

    result = rt_thread_startup(&g_app_ble_worker_thread);
    if (result == RT_EOK)
    {
        g_app_ble_worker_started = RT_TRUE;
    }
    return result;
}

app_ble_worker_result_t app_ble_worker_begin_session(uint16_t conn_id)
{
    rt_base_t level;
    rt_err_t result;

    if (!g_app_ble_worker_initialized || (conn_id == 0u))
    {
        return -RT_ERROR;
    }

    result = rt_mq_control(&g_app_ble_rx_mq, RT_IPC_CMD_RESET, RT_NULL);
    if (result != RT_EOK)
    {
        return result;
    }

    level = rt_hw_interrupt_disable();
    g_app_ble_generation = app_ble_worker_next_generation(g_app_ble_generation);
    g_app_ble_conn_id = conn_id;
    rt_hw_interrupt_enable(level);
    return RT_EOK;
}

void app_ble_worker_reset_session(uint16_t conn_id)
{
    rt_base_t level;

    if (!g_app_ble_worker_initialized)
    {
        return;
    }

    level = rt_hw_interrupt_disable();
    if ((conn_id != 0u) && (conn_id != g_app_ble_conn_id))
    {
        rt_hw_interrupt_enable(level);
        return;
    }
    g_app_ble_generation = app_ble_worker_next_generation(g_app_ble_generation);
    g_app_ble_conn_id = 0u;
    rt_hw_interrupt_enable(level);
    (void)rt_mq_control(&g_app_ble_rx_mq, RT_IPC_CMD_RESET, RT_NULL);
}

app_ble_worker_result_t app_ble_worker_enqueue(uint16_t conn_id,
                                               const uint8_t *data,
                                               uint16_t length)
{
    app_ble_rx_message_t message;
    rt_base_t level;
    rt_err_t result;
    rt_uint32_t queue_depth;

    if (!g_app_ble_worker_initialized || (conn_id == 0u) ||
        (data == RT_NULL) || (length == 0u) ||
        (length > APP_BLE_RX_FRAGMENT_MAX))
    {
        return -RT_EINVAL;
    }

    level = rt_hw_interrupt_disable();
    if (conn_id != g_app_ble_conn_id)
    {
        rt_hw_interrupt_enable(level);
        return -RT_ERROR;
    }
    message.generation = g_app_ble_generation;
    message.conn_id = conn_id;
    rt_hw_interrupt_enable(level);
    message.length = length;
    rt_memcpy(message.data, data, length);

    result = rt_mq_send(&g_app_ble_rx_mq, &message, sizeof(message));
    if (result != RT_EOK)
    {
        level = rt_hw_interrupt_disable();
        g_app_ble_rx_queue_drops++;
        rt_hw_interrupt_enable(level);
        app_ble_diag_note_rx_drop();
    }
    else
    {
        level = rt_hw_interrupt_disable();
        queue_depth = g_app_ble_rx_mq.entry;
        rt_hw_interrupt_enable(level);
        app_ble_diag_note_rx_queue_depth(queue_depth);
    }
    return result;
}

uint32_t app_ble_worker_drop_count(void)
{
    rt_uint32_t drops;
    rt_base_t level = rt_hw_interrupt_disable();
    drops = g_app_ble_rx_queue_drops;
    rt_hw_interrupt_enable(level);
    return drops;
}

#endif
