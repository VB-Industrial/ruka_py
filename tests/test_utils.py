import unittest

import numpy as np
from sensor_msgs.msg import JointState

from ruka_py import RobotConfig, RukaRobot, euler_deg_to_quaternion
from ruka_py.robot import (
    _duration,
    _numbers,
    _quaternion,
    _scaling_factor,
)

TEST_JOINT_NAMES = ("axis_a", "axis_b", "axis_c", "axis_d", "axis_e", "axis_f")


class FakeMoveIt:
    def __init__(self):
        self.executed = None

    def execute(self, trajectory):
        self.executed = trajectory

    def compute_ik(self, position, orientation):
        state = JointState()
        state.name = list(reversed(TEST_JOINT_NAMES))
        state.position = [6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
        return state


class UtilsTest(unittest.TestCase):
    def make_robot(self):
        robot = object.__new__(RukaRobot)
        robot.joint_names = TEST_JOINT_NAMES
        robot._moveit2 = FakeMoveIt()
        robot._closed = False
        return robot

    def test_zero_euler_angles(self):
        np.testing.assert_allclose(
            euler_deg_to_quaternion(0, 0, 0), [0.0, 0.0, 0.0, 1.0]
        )

    def test_quarter_turn_around_z(self):
        np.testing.assert_allclose(
            euler_deg_to_quaternion(0, 0, 90),
            [0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)],
        )

    def test_duration_keeps_fractional_seconds(self):
        duration = _duration(4.5)
        self.assertEqual(duration.sec, 4)
        self.assertEqual(duration.nanosec, 500_000_000)

    def test_wrong_number_count(self):
        with self.assertRaises(ValueError):
            _numbers([1, 2], 3, "position")

    def test_non_finite_number(self):
        with self.assertRaises(ValueError):
            _numbers([1, float("nan"), 3], 3, "position")

    def test_zero_quaternion(self):
        with self.assertRaises(ValueError):
            _quaternion([0, 0, 0, 0])

    def test_quaternion_is_normalized(self):
        self.assertEqual(_quaternion([0, 0, 0, 2]), [0, 0, 0, 1])

    def test_invalid_scaling_factor(self):
        for value in (0, -0.1, 1.1, float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                _scaling_factor(value, "max_velocity")

    def test_robot_config_keeps_controller_joint_order(self):
        config = RobotConfig(
            joint_names=["shoulder", "elbow", "wrist"],
            base_link_name="base",
            end_effector_name="tool",
            group_name="arm",
        )

        self.assertEqual(config.joint_names, ("shoulder", "elbow", "wrist"))

    def test_robot_config_rejects_duplicate_joint_names(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            RobotConfig(
                joint_names=["joint", "joint"],
                base_link_name="base",
                end_effector_name="tool",
                group_name="arm",
            )

    def test_robot_config_rejects_string_as_joint_sequence(self):
        with self.assertRaisesRegex(ValueError, "sequence"):
            RobotConfig(
                joint_names="joint",
                base_link_name="base",
                end_effector_name="tool",
                group_name="arm",
            )

    def test_angle_trajectory_is_built_by_library(self):
        robot = self.make_robot()

        robot.execute_angle_trajectory([(0.5, [1, 2, 3, 4, 5, 6])], wait=False)

        trajectory = robot._moveit2.executed
        self.assertEqual(trajectory.joint_names, list(TEST_JOINT_NAMES))
        self.assertEqual(list(trajectory.points[0].positions), [1, 2, 3, 4, 5, 6])
        self.assertEqual(trajectory.points[0].time_from_start.nanosec, 500_000_000)

    def test_pose_trajectory_reorders_ik_joint_state(self):
        robot = self.make_robot()

        robot.execute_pose_trajectory(
            [(1.0, [0.1, 0.2, 0.3], [0, 0, 0, 1])], wait=False
        )

        positions = robot._moveit2.executed.points[0].positions
        self.assertEqual(list(positions), [1, 2, 3, 4, 5, 6])

    def test_closed_robot_rejects_commands(self):
        robot = self.make_robot()
        robot._closed = True

        with self.assertRaisesRegex(RuntimeError, "closed"):
            robot.move_to_angles([1, 2, 3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main()
