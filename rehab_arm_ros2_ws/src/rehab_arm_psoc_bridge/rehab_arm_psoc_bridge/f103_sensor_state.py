from __future__ import annotations


F103_SENSOR_ID_HEX = '0x7C2'
F103_HEALTH_ID_HEX = '0x7C3'
ADC_MAX = 4095
ADC_REF_VOLTAGE = 3.3

EMG4_CHANNEL_MAP = (
    ('ch1', 0, 'biceps', 'biceps_brachii'),
    ('ch2', 1, 'triceps', 'triceps_brachii'),
    ('ch3', 2, 'anterior_deltoid', 'anterior_deltoid'),
    ('ch4', 3, 'forearm_extensor', 'forearm_extensor'),
)


def _u16_le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 2], 'little', signed=False)


def _activation(raw_adc: int) -> float:
    clamped = max(0, min(int(raw_adc), ADC_MAX))
    return round(clamped / ADC_MAX, 6)


def _voltage(raw_adc: int) -> float:
    clamped = max(0, min(int(raw_adc), ADC_MAX))
    return round(clamped * ADC_REF_VOLTAGE / ADC_MAX, 6)


def _emg_channel(channel: str, adc_index: int, muscle: str, muscle_name: str, raw_adc: int) -> dict[str, object]:
    activation = _activation(raw_adc)
    voltage = _voltage(raw_adc)
    return {
        'channel': channel,
        'name': channel,
        'channel_id': f'f103_adc{adc_index}',
        'adc_index': adc_index,
        'muscle': muscle,
        'muscle_name': muscle_name,
        'raw_adc': raw_adc,
        'value': activation,
        'activation': activation,
        'unit': 'adc_counts',
        'raw_adc_unit': 'adc_counts',
        'voltage_v': voltage,
        'value_v': voltage,
        'voltage_unit': 'V',
        'voltage_reference_v': ADC_REF_VOLTAGE,
        'range': [0, ADC_MAX],
        'signal_quality': 'ok',
    }


def parse_f103_sensor_payload(data: bytes) -> dict[str, object]:
    payload: dict[str, object] = {
        'schema_version': 'rehab_arm_sensor_state_v1',
        'source': 'f103_sensor',
        'sensor_node': 'stm32_f103_emg3',
        'physical_source': 'stm32_f103_emg3_can_0x7c2',
        'payload_format': 'adc4_le_u16_v1',
        'id_hex': F103_SENSOR_ID_HEX,
        'data': data.hex().upper(),
        'valid': len(data) >= 8,
        'control_boundary': 'telemetry_only_not_motion_permission',
    }
    if len(data) < 8:
        payload['detail'] = 'short_frame'
        payload['dlc'] = len(data)
        return payload

    adc_raw = [_u16_le(data, offset) for offset in (0, 2, 4, 6)]
    channels = [
        _emg_channel(channel, adc_index, muscle, muscle_name, adc_raw[adc_index])
        for channel, adc_index, muscle, muscle_name in EMG4_CHANNEL_MAP
    ]
    muscle_signals = {
        str(channel['muscle']): channel['activation']
        for channel in channels
    }
    payload.update({
        'detail': 'ok',
        'adc_raw': adc_raw,
        'emg4_raw': adc_raw[:4],
        'emg3_raw': adc_raw[:3],
        'debug_adc_raw': adc_raw[3],
        'emg_raw': adc_raw[0],
        'emg': {
            'schema_version': 'rehab_arm_emg4_adc_v1',
            'source': 'stm32_f103_emg3_can_0x7c2',
            'channels': channels,
            'channel_count': len(channels),
            'sample_unit': 'adc_counts',
            'adc_range': [0, ADC_MAX],
            'voltage_reference_v': ADC_REF_VOLTAGE,
            'voltage_unit': 'V',
            'debug_adc_raw': adc_raw[3],
            'signal_quality': {
                'status': 'ok',
                'reason': 'direct_can_frame_received',
                'valid_channel_count': len(channels),
            },
            'control_boundary': 'telemetry_only_not_motion_permission',
        },
        'emg_channels': channels,
        'muscle_signals': muscle_signals,
        'signal_quality': 'ok',
    })
    return payload


def parse_f103_health_payload(data: bytes) -> dict[str, object]:
    payload: dict[str, object] = {
        'schema_version': 'rehab_arm_sensor_health_v1',
        'source': 'f103_health',
        'sensor_node': 'stm32_f103_emg3',
        'physical_source': 'stm32_f103_health_can_0x7c3',
        'id_hex': F103_HEALTH_ID_HEX,
        'data': data.hex().upper(),
        'valid': len(data) >= 4,
        'control_boundary': 'telemetry_only_not_motion_permission',
    }
    if len(data) < 4:
        payload['detail'] = 'short_frame'
        payload['dlc'] = len(data)
        return payload

    state_code = data[0]
    error_count = int.from_bytes(data[1:3], 'little', signed=False)
    queue_fill = data[3]
    payload.update({
        'detail': 'ok',
        'state_code': state_code,
        'state': f103_health_state_name(state_code),
        'error_count': error_count,
        'queue_fill': queue_fill,
        'queue_fill_percent': round(queue_fill * 100.0 / 255.0, 2),
    })
    return payload


def f103_health_state_name(state_code: int) -> str:
    return {
        0: 'boot',
        1: 'ok',
        2: 'streaming',
        3: 'limited',
        4: 'fault',
    }.get(state_code, 'unknown')
