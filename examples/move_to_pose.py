"""Движение по координате и ориентации."""

from ruka_py import RukaRobot, euler_deg_to_quaternion

with RukaRobot() as robot:
    position = [0.256, 0.0, 0.5628]
    orientation = euler_deg_to_quaternion(0, 0, 0)
    robot.move_to_pose(position, orientation)
