#!/usr/bin/env python3
from __future__ import annotations

import math
import struct


PSOC_CMD_ID = 0x320
CMD_SET_TARGET = 0x03

JOINT_NAMES = [
    'elbow_lift_joint',
    'shoulder_abduction_joint',
    'upper_arm_rotation_joint',
]

JOINT_IDS = {name: index for index, name in enumerate(JOINT_NAMES)}
JOINT_NAMES_BY_ID = {index: name for name, index in JOINT_IDS.items()}

LIMITS = {
    'elbow_lift_joint': (0.00, 1.80),
    'shoulder_abduction_joint': (0.00, math.radians(150.0)),
    'upper_arm_rotation_joint': (-1.20, 1.20),
}


def rpm_to_velocity_rad_s(rpm: int | float) -> float:
    return abs(float(rpm)) * 2.0 * math.pi / 60.0


def rpm_from_velocity_rad_s(velocity_rad_s: float, default_rpm: int) -> int:
    velocity = float(velocity_rad_s)
    if not math.isfinite(velocity):
        raise ValueError('velocity_rad_s must be finite')
    if velocity == 0.0:
        return int(default_rpm)
    return max(1, int(round(abs(velocity) * 60.0 / (2.0 * math.pi))))


def encode_target(joint_name: str, position_rad: float, rpm: int, torque_ma: int) -> bytes:
    if joint_name not in JOINT_IDS:
        known = ', '.join(JOINT_IDS)
        raise ValueError(f'unknown joint {joint_name!r}; known joints: {known}')
    return encode_target_by_joint_id(JOINT_IDS[joint_name], position_rad, rpm, torque_ma)


def encode_target_by_joint_id(
    joint_id: int,
    position_rad: float,
    rpm: int,
    torque_ma: int,
) -> bytes:
    joint_name = JOINT_NAMES_BY_ID.get(int(joint_id))
    if joint_name is None:
        known = ', '.join(str(item) for item in sorted(JOINT_NAMES_BY_ID))
        raise ValueError(f'unknown joint_id {joint_id!r}; known ids: {known}')
    if not math.isfinite(position_rad):
        raise ValueError('position_rad must be finite')
    low, high = LIMITS[joint_name]
    if position_rad < low or position_rad > high:
        raise ValueError(
            f'{joint_name} position {position_rad:.5f} rad outside [{low:.5f}, {high:.5f}]'
        )
    deg_x10 = int(math.degrees(position_rad) * 10.0)
    return bytes([CMD_SET_TARGET, int(joint_id) & 0xFF]) + struct.pack(
        '<hhh',
        deg_x10,
        int(rpm),
        int(torque_ma),
    )
