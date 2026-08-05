"""Движение в конфигурацию, заданную углами суставов."""

from ruka_py import RukaRobot

with RukaRobot() as robot:
    joint_goal = [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]
    robot.move_to_angles(joint_goal)
