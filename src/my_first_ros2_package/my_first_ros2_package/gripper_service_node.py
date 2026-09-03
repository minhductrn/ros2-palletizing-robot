#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
# Import service vừa tạo
from my_robot_interfaces.srv import SetGripperStatus


class GripperServiceNode(Node):

    def __init__(self):
        super().__init__('gripper_service_node')
        
        # Khởi tạo Service Server
        self.srv = self.create_service(
            SetGripperStatus, 
            'set_gripper_status', 
            self.set_gripper_callback
        )
        self.get_logger().info('🤖 Gripper Service Server has been started.')

    def set_gripper_callback(self, request, response):
        # Xử lý logic đóng/mở dựa trên request.activate
        if request.activate:
            self.get_logger().info('🧲 Request received: ACTIVATE GRIPPER (Gắp hàng)')
            response.success = True
            response.message = "Gripper suction ON. Box secured."
        else:
            self.get_logger().info('🔓 Request received: DEACTIVATE GRIPPER (Nhả hàng)')
            response.success = True
            response.message = "Gripper suction OFF. Box released."
            
        return response


def main(args=None):
    rclpy.init(args=args)
    node = GripperServiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
