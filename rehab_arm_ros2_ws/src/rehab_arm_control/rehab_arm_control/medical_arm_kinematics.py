from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


MEDICAL_ARM_JOINT_NAMES = (
    'jian_hengxiang_joint',
    'jian_zongxiang_joint',
    'jian_xuanzhuan_joint',
    'zhou_zongxiang_joint',
    'wanbu_zongxiang_joint',
    'wanbu_hengxiang_joint',
)


@dataclass(frozen=True)
class JointLimit:
    lower: float
    upper: float
    velocity: float


@dataclass(frozen=True)
class Pose:
    position: tuple[float, float, float]
    orientation: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]


JOINT_LIMITS: dict[str, JointLimit] = {
    'jian_hengxiang_joint': JointLimit(-0.7854, 1.5708, 0.35),
    'jian_zongxiang_joint': JointLimit(-0.5236, 1.7453, 0.35),
    'jian_xuanzhuan_joint': JointLimit(-1.0472, 1.0472, 0.45),
    'zhou_zongxiang_joint': JointLimit(0.0, 2.3562, 0.45),
    'wanbu_zongxiang_joint': JointLimit(-0.7854, 0.7854, 0.60),
    'wanbu_hengxiang_joint': JointLimit(-0.3491, 0.5236, 0.60),
}

_BASE_POSITION = (0.0, 0.0, 0.8)
_BODY_TRANSLATIONS = (
    (0.0, 0.0, 0.0),
    (0.24, 0.0, 0.0),
    (0.18, 0.0, 0.0),
    (0.28, 0.0, 0.0),
    (0.12, 0.0, 0.0),
    (0.10, 0.0, 0.0),
)
_JOINT_AXES = (
    (0.0, 0.0, 1.0),
    (0.0, 1.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)
_END_EFFECTOR_SITE = (0.10, 0.0, 0.0)


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)


def _validate_positions(positions: Sequence[float]) -> list[float]:
    if len(positions) != len(MEDICAL_ARM_JOINT_NAMES):
        raise ValueError(f'expected {len(MEDICAL_ARM_JOINT_NAMES)} joint positions, got {len(positions)}')
    return [float(position) for position in positions]


def clamp_to_limits(positions: Sequence[float]) -> list[float]:
    values = _validate_positions(positions)
    clamped: list[float] = []
    for value, name in zip(values, MEDICAL_ARM_JOINT_NAMES):
        limit = JOINT_LIMITS[name]
        clamped.append(_clamp(value, limit.lower, limit.upper))
    return clamped


def _identity_matrix() -> list[list[float]]:
    return [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [
            sum(left[row][k] * right[k][column] for k in range(3))
            for column in range(3)
        ]
        for row in range(3)
    ]


def _matvec(matrix: list[list[float]], vector: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        sum(matrix[0][i] * vector[i] for i in range(3)),
        sum(matrix[1][i] * vector[i] for i in range(3)),
        sum(matrix[2][i] * vector[i] for i in range(3)),
    )


def _add(left: tuple[float, float, float], right: tuple[float, float, float]) -> tuple[float, float, float]:
    return (left[0] + right[0], left[1] + right[1], left[2] + right[2])


def _rotation(axis: tuple[float, float, float], angle: float) -> list[list[float]]:
    x, y, z = axis
    c = math.cos(angle)
    s = math.sin(angle)
    one_minus_c = 1.0 - c
    return [
        [c + x * x * one_minus_c, x * y * one_minus_c - z * s, x * z * one_minus_c + y * s],
        [y * x * one_minus_c + z * s, c + y * y * one_minus_c, y * z * one_minus_c - x * s],
        [z * x * one_minus_c - y * s, z * y * one_minus_c + x * s, c + z * z * one_minus_c],
    ]


def _round_pose_position(position: tuple[float, float, float]) -> tuple[float, float, float]:
    rounded = tuple(0.0 if abs(value) < 1e-12 else round(value, 12) for value in position)
    return rounded  # type: ignore[return-value]


def _freeze_matrix(matrix: list[list[float]]) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    return tuple(tuple(0.0 if abs(value) < 1e-12 else value for value in row) for row in matrix)  # type: ignore[return-value]


def forward_kinematics(positions: Sequence[float]) -> Pose:
    values = clamp_to_limits(positions)
    origin = _BASE_POSITION
    orientation = _identity_matrix()

    for value, translation, axis in zip(values, _BODY_TRANSLATIONS, _JOINT_AXES):
        origin = _add(origin, _matvec(orientation, translation))
        orientation = _matmul(orientation, _rotation(axis, value))

    origin = _add(origin, _matvec(orientation, _END_EFFECTOR_SITE))
    return Pose(position=_round_pose_position(origin), orientation=_freeze_matrix(orientation))


def end_effector_position(positions: Sequence[float]) -> tuple[float, float, float]:
    return forward_kinematics(positions).position


def numerical_position_jacobian(positions: Sequence[float], step: float = 1e-5) -> list[list[float]]:
    if step <= 0.0:
        raise ValueError('step must be positive')
    values = clamp_to_limits(positions)
    jacobian = [[0.0 for _ in values] for _ in range(3)]

    for joint_index in range(len(values)):
        plus = list(values)
        minus = list(values)
        plus[joint_index] += step
        minus[joint_index] -= step
        upper = end_effector_position(plus)
        lower = end_effector_position(minus)
        for axis_index in range(3):
            jacobian[axis_index][joint_index] = (upper[axis_index] - lower[axis_index]) / (2.0 * step)

    return jacobian
