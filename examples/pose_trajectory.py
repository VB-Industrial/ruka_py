"""Движение по траектории позиций и ориентаций."""

from ruka_py import RukaRobot

trajectory = [
    (
        0.5,
        [0.45299, -0.1015516, 0.46503],
        [0.70172, 0.010648, 0.71223, 0.014095],
    ),
    (
        4.5,
        [0.25299, 0.03015516, 0.26503],
        [0.70172, 0.010648, 0.71223, 0.014095],
    ),
    (
        6.0,
        [0.35299, -0.1015516, 0.46503],
        [0.70172, 0.010648, 0.71223, 0.014095],
    ),
]

with RukaRobot() as robot:
    _, first_position, first_orientation = trajectory[0]
    robot.move_to_pose(first_position, first_orientation)
    robot.execute_pose_trajectory(trajectory)
