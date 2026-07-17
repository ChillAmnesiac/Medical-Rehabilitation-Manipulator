#ifndef APP_BLE_DIAG_H
#define APP_BLE_DIAG_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    rt_uint32_t used_bytes;
    rt_uint32_t size_bytes;
    rt_uint32_t used_percent;
    rt_uint32_t available;
} app_ble_diag_stack_t;

typedef struct
{
    rt_uint32_t gatt_events;
    rt_uint32_t rx_drops;
    rt_uint32_t rx_queue_peak;
    rt_uint32_t tx_queue_peak;
    rt_uint32_t notify_failures;
    rt_uint32_t hci_rx_queue_last_percent;
    rt_uint32_t hci_tx_queue_last_percent;
    rt_uint32_t hci_rx_queue_sampled_peak_percent;
    rt_uint32_t hci_tx_queue_sampled_peak_percent;
    rt_uint32_t hci_rx_queue_sample_available;
    rt_uint32_t hci_tx_queue_sample_available;
    rt_uint32_t heap_free_bytes;
    rt_uint32_t heap_min_free_bytes;
    rt_uint32_t hci_tx_heap_percent;
    rt_uint32_t hci_tx_largest_free_bytes;
    rt_uint32_t gate_enabled;
    rt_uint32_t gate_state;
    rt_int32_t gate_last_error;
    app_ble_diag_stack_t hci_rx_stack;
    app_ble_diag_stack_t hci_tx_stack;
    app_ble_diag_stack_t ble_worker_stack;
    app_ble_diag_stack_t rehab_stack;
    app_ble_diag_stack_t shell_stack;
} app_ble_diag_snapshot_t;

void app_ble_diag_note_gatt_event(void);
void app_ble_diag_note_rx_drop(void);
void app_ble_diag_note_rx_queue_depth(rt_uint32_t depth);
void app_ble_diag_note_tx_queue_depth(rt_uint32_t depth);
void app_ble_diag_note_notify_failure(void);
void app_ble_diag_note_hci_queue_percent(rt_uint32_t task_id, rt_uint32_t percent);
void app_ble_diag_note_gate_state(rt_uint32_t enabled, rt_uint32_t state, rt_err_t last_error);
void app_ble_diag_snapshot(app_ble_diag_snapshot_t *out);

#ifdef __cplusplus
}
#endif

#endif
