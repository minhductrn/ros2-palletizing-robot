#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action import ActionServer
from my_robot_interfaces.action import PalletizeBox

# IMPORT THƯ VIỆN PHÁT TRẠNG THÁI KHỚP ROBOT MỚI
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class PalletizeActionServer(Node):

    def __init__(self):
        super().__init__('my_action_server_node')
        
        # 1. Khởi tạo bộ phát tọa độ TF2 và Topic phát trạng thái khớp vật lý
        self.tf_broadcaster = TransformBroadcaster(self)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # 2. Khởi tạo Action Server
        self._action_server = ActionServer(
            self,
            PalletizeBox,
            'palletize_box',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        self.get_logger().info('🤖 Kinematics Action Server with Joint State Telemetry online.')

    def goal_callback(self, goal_request):
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    def publish_robot_joints(self, torso_angle, arm_angle):
        """Hàm phát góc xoay thực tế của các khớp robot lên mô phỏng 3D"""
        joint_state = JointState()
        # ĐẢM BẢO CÓ DÒNG THỜI GIAN NÀY ĐỂ RVIZ2 KHÔNG BỎ QUA GÓI TIN
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = ['base_to_torso', 'torso_to_arm']
        joint_state.position = [float(torso_angle), float(arm_angle)]
        self.joint_pub.publish(joint_state)


    def broadcast_snapped_box(self, parent_frame):
        """Hàm phát tọa độ dịch chuyển và snap (dính chặt) của chiếc hộp"""
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = parent_frame
        t.child_frame_id = 'box_frame'

        if parent_frame == 'arm_link':
            # Khi gắp: Hộp dính chặt vào đầu kẹp gắp (cách khớp cánh tay 0.8m)
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.8
        else:
            # Khi đặt: Hộp nằm cố định trên mặt pallet mục tiêu
            t.transform.translation.x = -0.5
            t.transform.translation.y = -0.5
            t.transform.translation.z = 0.1

        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

    def execute_callback(self, goal_handle):
        box_id = goal_handle.request.box_id
        feedback_msg = PalletizeBox.Feedback()
        
        # Cấu hình chu trình: (Tiến độ, Tên bước, Góc khớp thân, Góc khớp tay)
        steps = [
            (10, 'Picking', 0.0, 0.5),           # Hạ cánh tay xuống băng tải gắp hàng
            (40, 'Moving to pallet', 1.57, -0.2), # Xoay thân 90 độ và nâng cánh tay lên
            (70, 'Placing', 1.57, 0.6),           # Hạ cánh tay xuống đặt hàng vào pallet
            (90, 'Returning', 0.0, 0.0),          # Thu tay về vị trí trung gian mặc định
            (100, 'Complete', 0.0, 0.0)
        ]

        for progress, step, torso_angle, arm_angle in steps:
            feedback_msg.progress = float(progress)
            feedback_msg.current_step = step
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Box {box_id}: {progress}% - {step}')

            # Ép cập nhật hình thái chuyển động 3D lên màn hình RViz2
            self.publish_robot_joints(torso_angle, arm_angle)

            # Điều khiển logic dính hộp TF2
            if step in ['Picking', 'Moving to pallet']:
                self.broadcast_snapped_box('arm_link')
            elif step == 'Placing':
                self.broadcast_snapped_box('base_link')

            time.sleep(1.0)

        goal_handle.succeed()
        result = PalletizeBox.Result()
        result.success = True
        result.message = f'Box {box_id} completed.'
        return result


def main(args=None):
    rclpy.init(args=args)
    node = PalletizeActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
