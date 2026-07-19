from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from rehab_arm_control.medical_arm_kinematics import (
    MEDICAL_ARM_JOINT_NAMES,
    clamp_to_limits,
    end_effector_position,
    numerical_position_jacobian,
)


@dataclass(frozen=True)
class IKResult:
    success: bool
    positions: list[float]
    iterations: int
    error_norm: float
    target_position: tuple[float, float, float]


def _validate_target(target_xyz: Sequence[float]) -> tuple[float, float, float]:
    if len(target_xyz) != 3:
        raise ValueError('target_xyz must contain exactly three values')
    return (float(target_xyz[0]), float(target_xyz[1]), float(target_xyz[2]))


def _norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def _solve_3x3(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    augmented = [list(row) + [rhs] for row, rhs in zip(matrix, vector)]
    size = 3

    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            return None
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]

        pivot_value = augmented[column][column]
        for index in range(column, size + 1):
            augmented[column][index] /= pivot_value

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            for index in range(column, size + 1):
                augmented[row][index] -= factor * augmented[column][index]

    return [augmented[row][size] for row in range(size)]


def _damped_least_squares_step(
    jacobian: list[list[float]],
    error: list[float],
    damping: float,
) -> list[float]:
    rows = 3
    cols = len(jacobian[0])
    normal = [[0.0 for _ in range(rows)] for _ in range(rows)]
    for row in range(rows):
        for column in range(rows):
            normal[row][column] = sum(jacobian[row][joint] * jacobian[column][joint] for joint in range(cols))
            if row == column:
                normal[row][column] += damping * damping

    solved = _solve_3x3(normal, error)
    if solved is None:
        return [0.0] * cols
    return [
        sum(jacobian[row][joint] * solved[row] for row in range(rows))
        for joint in range(cols)
    ]


def _limit_joint_step(delta: list[float], max_step: float) -> list[float]:
    largest = max((abs(value) for value in delta), default=0.0)
    if largest <= max_step:
        return delta
    scale = max_step / largest
    return [value * scale for value in delta]


def solve_position_ik(
    target_xyz: Sequence[float],
    *,
    seed: Sequence[float] | None = None,
    max_iterations: int = 120,
    tolerance: float = 1e-3,
    damping: float = 0.04,
    step_scale: float = 0.8,
    max_joint_step: float = 0.12,
) -> IKResult:
    target = _validate_target(target_xyz)
    if max_iterations < 0:
        raise ValueError('max_iterations must be non-negative')
    if tolerance <= 0.0:
        raise ValueError('tolerance must be positive')
    if damping <= 0.0:
        raise ValueError('damping must be positive')

    if seed is None:
        positions = [0.0] * len(MEDICAL_ARM_JOINT_NAMES)
    else:
        positions = clamp_to_limits(seed)

    best_positions = list(positions)
    best_error_norm = float('inf')

    for iteration in range(max_iterations + 1):
        current = end_effector_position(positions)
        error = [target[index] - current[index] for index in range(3)]
        error_norm = _norm(error)
        if error_norm < best_error_norm:
            best_error_norm = error_norm
            best_positions = list(positions)
        if error_norm <= tolerance:
            return IKResult(True, list(positions), iteration, error_norm, target)
        if iteration == max_iterations:
            break

        jacobian = numerical_position_jacobian(positions)
        delta = _damped_least_squares_step(jacobian, error, damping)
        delta = _limit_joint_step([value * step_scale for value in delta], max_joint_step)
        positions = clamp_to_limits([
            position + change
            for position, change in zip(positions, delta)
        ])

    return IKResult(False, best_positions, max_iterations, best_error_norm, target)
