"""ROS and MoveIt 2 implementation hidden behind :class:`RukaRobot`."""

from __future__ import annotations

import math
import time
from collections.abc import Iterable, Sequence
from threading import Thread

DEFAULT_JOINT_NAMES = (
    "base_link__link_01",
    "link_01__link_02",
    "link_02__link_03",
    "link_03__link_04",
    "link_04__link_05",
    "link_05__link_06",
)


def _numbers(values: Sequence[float], length: int, name: str) -> list[float]:
    try:
        value_count = len(values)
    except TypeError as exc:
        raise ValueError(f"{name} must be a sequence of {length} numbers") from exc
    if value_count != length:
        raise ValueError(f"{name} must contain exactly {length} values")
    try:
        result = [float(value) for value in values]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain only numbers") from exc
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain only finite numbers")
    return result


def _quaternion(values: Sequence[float]) -> list[float]:
    quaternion = _numbers(values, 4, "orientation")
    norm = math.sqrt(sum(value * value for value in quaternion))
    if math.isclose(norm, 0.0, abs_tol=1e-12):
        raise ValueError("orientation quaternion cannot be zero")
    return [value / norm for value in quaternion]


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return result


def _scaling_factor(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or not 0.0 < result <= 1.0:
        raise ValueError(f"{name} must be greater than 0 and at most 1")
    return result


def _object_id(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("object_id must be a non-empty string without outer spaces")
    return value


def _duration(seconds: float):
    from builtin_interfaces.msg import Duration

    seconds = float(seconds)
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Trajectory time must be a non-negative finite number")
    whole_seconds = int(seconds)
    nanoseconds = round((seconds - whole_seconds) * 1_000_000_000)
    if nanoseconds == 1_000_000_000:
        whole_seconds += 1
        nanoseconds = 0
    return Duration(sec=whole_seconds, nanosec=nanoseconds)


class RukaRobot:
    """A high-level controller for the six-axis RUKA arm.

    Creating the object starts ROS, the MoveIt client, and its background
    executor. Using it as a context manager guarantees correct cleanup.
    """

    def __init__(
        self,
        *,
        node_name: str = "ruka_py",
        joint_names: Sequence[str] = DEFAULT_JOINT_NAMES,
        base_link_name: str = "base_link",
        end_effector_name: str = "link_06",
        group_name: str = "ruka_arm_controller",
        max_velocity: float = 0.9,
        max_acceleration: float = 0.7,
        startup_delay: float = 1.0,
    ) -> None:
        import rclpy
        from pymoveit2 import MoveIt2
        from rclpy.callback_groups import ReentrantCallbackGroup
        from rclpy.executors import MultiThreadedExecutor
        from rclpy.node import Node

        self.joint_names = tuple(joint_names)
        if not self.joint_names:
            raise ValueError("joint_names cannot be empty")
        if not node_name or node_name != node_name.strip():
            raise ValueError(
                "node_name must be a non-empty string without outer spaces"
            )
        startup_delay = float(startup_delay)
        if not math.isfinite(startup_delay) or startup_delay < 0:
            raise ValueError("startup_delay must be a non-negative finite number")
        max_velocity = _scaling_factor(max_velocity, "max_velocity")
        max_acceleration = _scaling_factor(max_acceleration, "max_acceleration")

        self._rclpy = rclpy
        self._owns_rclpy = not rclpy.ok()
        self._node = None
        self._moveit2 = None
        self._executor = None
        self._executor_thread = None
        self._closed = True

        if self._owns_rclpy:
            rclpy.init()

        try:
            self._node = Node(node_name)
            callback_group = ReentrantCallbackGroup()
            self._moveit2 = MoveIt2(
                node=self._node,
                joint_names=list(self.joint_names),
                base_link_name=base_link_name,
                end_effector_name=end_effector_name,
                group_name=group_name,
                callback_group=callback_group,
            )
            self._moveit2.max_velocity = max_velocity
            self._moveit2.max_acceleration = max_acceleration

            self._executor = MultiThreadedExecutor(num_threads=2)
            self._executor.add_node(self._node)
            self._executor_thread = Thread(
                target=self._executor.spin,
                name=f"{node_name}-executor",
                daemon=True,
            )
            self._executor_thread.start()
            self._closed = False

            if startup_delay > 0:
                time.sleep(startup_delay)
        except Exception:
            self._cleanup_failed_initialization()
            raise

    @property
    def max_velocity(self) -> float:
        self._ensure_open()
        return self._moveit2.max_velocity

    @max_velocity.setter
    def max_velocity(self, value: float) -> None:
        self._ensure_open()
        self._moveit2.max_velocity = _scaling_factor(value, "max_velocity")

    @property
    def max_acceleration(self) -> float:
        self._ensure_open()
        return self._moveit2.max_acceleration

    @max_acceleration.setter
    def max_acceleration(self, value: float) -> None:
        self._ensure_open()
        self._moveit2.max_acceleration = _scaling_factor(value, "max_acceleration")

    def move_to_angles(self, angles: Sequence[float], *, wait: bool = True) -> bool:
        """Move to one joint configuration."""

        self._ensure_open()
        goal = _numbers(angles, len(self.joint_names), "angles")
        self._moveit2.move_to_configuration(goal)
        return self._wait(wait)

    def move_to_pose(
        self,
        position: Sequence[float],
        orientation: Sequence[float],
        *,
        wait: bool = True,
    ) -> bool:
        """Move the end effector to a position and quaternion orientation."""

        self._ensure_open()
        position_values = _numbers(position, 3, "position")
        orientation_values = _quaternion(orientation)
        self._moveit2.move_to_pose(
            position=position_values, quat_xyzw=orientation_values
        )
        return self._wait(wait)

    def execute_angle_trajectory(
        self,
        points: Iterable[tuple[float, Sequence[float]]],
        *,
        wait: bool = True,
    ) -> bool:
        """Execute ``(time_from_start, joint_angles)`` points."""

        self._ensure_open()
        from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

        trajectory = JointTrajectory()
        trajectory.joint_names = list(self.joint_names)
        previous_time = -1.0

        for seconds, angles in points:
            seconds = float(seconds)
            if seconds <= previous_time:
                raise ValueError("Trajectory times must be strictly increasing")
            previous_time = seconds
            point = JointTrajectoryPoint()
            point.positions = _numbers(angles, len(self.joint_names), "angles")
            point.time_from_start = _duration(seconds)
            trajectory.points.append(point)

        self._execute(trajectory)
        return self._wait(wait)

    def execute_pose_trajectory(
        self,
        points: Iterable[tuple[float, Sequence[float], Sequence[float]]],
        *,
        wait: bool = True,
    ) -> bool:
        """Compute IK and execute ``(time, position, orientation)`` points."""

        self._ensure_open()
        from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

        trajectory = JointTrajectory()
        trajectory.joint_names = list(self.joint_names)
        previous_time = -1.0

        for seconds, position, orientation in points:
            seconds = float(seconds)
            if seconds <= previous_time:
                raise ValueError("Trajectory times must be strictly increasing")
            previous_time = seconds
            joint_state = self._moveit2.compute_ik(
                _numbers(position, 3, "position"),
                _quaternion(orientation),
            )
            if joint_state is None:
                raise RuntimeError(
                    f"MoveIt could not find an IK solution for position {position}"
                )
            point = JointTrajectoryPoint()
            joint_positions = list(joint_state.position)
            if joint_state.name and all(
                name in joint_state.name for name in self.joint_names
            ):
                positions_by_name = dict(
                    zip(joint_state.name, joint_positions, strict=True)
                )
                joint_positions = [positions_by_name[name] for name in self.joint_names]
            if len(joint_positions) != len(self.joint_names):
                raise RuntimeError(
                    "IK returned a joint state incompatible with the configured arm"
                )
            point.positions = _numbers(
                joint_positions, len(self.joint_names), "IK joint positions"
            )
            point.time_from_start = _duration(seconds)
            trajectory.points.append(point)

        self._execute(trajectory)
        return self._wait(wait)

    def add_box(
        self,
        object_id: str,
        position: Sequence[float],
        orientation: Sequence[float],
        size: Sequence[float],
    ) -> None:
        self._ensure_open()
        size_values = _numbers(size, 3, "size")
        if any(value <= 0 for value in size_values):
            raise ValueError("size values must be positive")
        self._moveit2.add_collision_box(
            id=_object_id(object_id),
            position=_numbers(position, 3, "position"),
            quat_xyzw=_quaternion(orientation),
            size=size_values,
        )

    def add_sphere(
        self, object_id: str, position: Sequence[float], radius: float
    ) -> None:
        self._ensure_open()
        self._moveit2.add_collision_sphere(
            id=_object_id(object_id),
            position=_numbers(position, 3, "position"),
            radius=_positive(radius, "radius"),
        )

    def add_cylinder(
        self,
        object_id: str,
        position: Sequence[float],
        orientation: Sequence[float],
        height: float,
        radius: float,
    ) -> None:
        self._ensure_open()
        self._moveit2.add_collision_cylinder(
            id=_object_id(object_id),
            position=_numbers(position, 3, "position"),
            quat_xyzw=_quaternion(orientation),
            height=_positive(height, "height"),
            radius=_positive(radius, "radius"),
        )

    def add_cone(
        self,
        object_id: str,
        position: Sequence[float],
        orientation: Sequence[float],
        height: float,
        radius: float,
    ) -> None:
        self._ensure_open()
        self._moveit2.add_collision_cone(
            id=_object_id(object_id),
            position=_numbers(position, 3, "position"),
            quat_xyzw=_quaternion(orientation),
            height=_positive(height, "height"),
            radius=_positive(radius, "radius"),
        )

    def move_collision_object(
        self,
        object_id: str,
        position: Sequence[float],
        orientation: Sequence[float],
    ) -> None:
        self._ensure_open()
        self._moveit2.move_collision(
            id=_object_id(object_id),
            position=_numbers(position, 3, "position"),
            quat_xyzw=_quaternion(orientation),
        )

    def remove_collision_object(self, object_id: str) -> None:
        self._ensure_open()
        self._moveit2.remove_collision_object(id=_object_id(object_id))

    def close(self) -> None:
        """Stop the executor and release ROS resources. Safe to call twice."""

        if self._closed:
            return
        self._closed = True
        if self._executor is not None:
            self._executor.shutdown(timeout_sec=5.0)
        if self._executor_thread is not None:
            self._executor_thread.join(timeout=5.0)
        if self._node is not None:
            self._node.destroy_node()
        if self._owns_rclpy and self._rclpy.ok():
            self._rclpy.shutdown()

    def __enter__(self) -> RukaRobot:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def _execute(self, trajectory) -> None:
        self._ensure_open()
        if not trajectory.points:
            raise ValueError("Trajectory must contain at least one point")
        self._moveit2.execute(trajectory)

    def _wait(self, wait: bool) -> bool:
        if not wait:
            return True
        return bool(self._moveit2.wait_until_executed())

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("RukaRobot is closed")

    def _cleanup_failed_initialization(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(timeout_sec=5.0)
        if self._executor_thread is not None:
            self._executor_thread.join(timeout=5.0)
        if self._node is not None:
            self._node.destroy_node()
        if self._owns_rclpy and self._rclpy.ok():
            self._rclpy.shutdown()
