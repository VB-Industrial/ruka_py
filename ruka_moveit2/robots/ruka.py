from typing import List

MOVE_GROUP_ARM: str = "ruka_arm_controller"
MOVE_GROUP_GRIPPER: str = "ruka_hand_controller"

OPEN_GRIPPER_JOINT_POSITIONS: List[float] = [0.01, 0.01]
CLOSED_GRIPPER_JOINT_POSITIONS: List[float] = [0.0, 0.0]


def joint_names(prefix = "ruka"):
    joint_names=["base_link__link_01", 
                "link_01__link_02", 
                "link_02__link_03", 
                "link_03__link_04", 
                "link_04__link_05", 
                "link_05__link_06"]
    return joint_names


def base_link_name(prefix: str = "base_link"):
    return prefix


def end_effector_name(prefix: str = "ruka_hand_controller"):
    return prefix


def gripper_joint_names(prefix = "ruka_hand"):
    return [
        "link_hand_cyl__first_fin",
        "link_hand_cyl__second_fin",
    ]
