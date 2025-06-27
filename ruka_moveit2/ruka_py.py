import rclpy
from ruka_moveit2 import MoveIt2

class RobotArm():
    def __new__(self):
        rclpy.init()
        self.node = rclpy.create_node("ruka_pymoveit2")
        ruka = MoveIt2(
            node=self.node,
            joint_names=["base_link__link_01", 
                                    "link_01__link_02", 
                                    "link_02__link_03", 
                                    "link_03__link_04", 
                                    "link_04__link_05", 
                                    "link_05__link_06"],
            base_link_name="base_link",
            end_effector_name="link_06",
            group_name="ruka_arm_controller"
        )
        ruka.shutdown = self.shutdown
        return ruka
    
    def shutdown():
        rclpy.shutdown()
