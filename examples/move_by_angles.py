"""Движение в конфигурацию, заданную углами суставов."""

from robot_config import ROBOT_CONFIG

from ruka_py import RukaRobot

with RukaRobot(ROBOT_CONFIG) as robot:
    joint_goal = [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]
    robot.move_to_angles(joint_goal)
