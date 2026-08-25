"""Robot-specific configuration for :mod:`ruka_py`."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


def _ros_name(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError(f"{field_name} must be a non-empty string without whitespace")
    return value


@dataclass(frozen=True, slots=True)
class RobotConfig:
    """Names that connect :class:`RukaRobot` to a particular MoveIt setup.

    Joint order must match the order expected by the arm controller. No joint,
    link, or planning-group names are assumed by the library.
    """

    joint_names: Sequence[str]
    base_link_name: str
    end_effector_name: str
    group_name: str

    def __post_init__(self) -> None:
        if isinstance(self.joint_names, (str, bytes)):
            raise ValueError("joint_names must be a sequence of joint names")
        joint_names = tuple(self.joint_names)
        if not joint_names:
            raise ValueError("joint_names cannot be empty")

        validated_names = tuple(
            _ros_name(name, f"joint_names[{index}]")
            for index, name in enumerate(joint_names)
        )
        if len(set(validated_names)) != len(validated_names):
            raise ValueError("joint_names must be unique")

        object.__setattr__(self, "joint_names", validated_names)
        object.__setattr__(
            self,
            "base_link_name",
            _ros_name(self.base_link_name, "base_link_name"),
        )
        object.__setattr__(
            self,
            "end_effector_name",
            _ros_name(self.end_effector_name, "end_effector_name"),
        )
        object.__setattr__(
            self,
            "group_name",
            _ros_name(self.group_name, "group_name"),
        )
