"""Имена из URDF/SRDF конкретного манипулятора.

Измените только этот файл, если имена суставов или звеньев вашего робота
отличаются. Порядок ``joint_names`` должен совпадать с порядком контроллера.
"""

from ruka_py import RobotConfig

ROBOT_CONFIG = RobotConfig(
    joint_names=(
        "base_link__link_01",
        "link_01__link_02",
        "link_02__link_03",
        "link_03__link_04",
        "link_04__link_05",
        "link_05__link_06",
    ),
    base_link_name="base_link",
    end_effector_name="link_06",
    group_name="ruka_arm_controller",
)
