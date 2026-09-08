#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action import ActionServer
from my_robot_interfaces.action import PalletizeBox

# IMPORT CENTRAL GEOMETRY, SENSOR, AND MARKER UTILITIES
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from visualization_msgs.msg import Marker
from tf2_ros import TransformBroadcaster


class PalletizeActionServer(Node):

    def __init__(self):
        super().__init__('my_action_server_node')
        
        self.tf_broadcaster = TransformBroadcaster(self)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # Initialize marker re-publisher pipeline inside action thread limits
        self.marker_pub = self.create_publisher(Marker, 'visualization_marker', 10)

        self._action_server = ActionServer(
            self,
            PalletizeBox,
            'palletize_box',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        self.get_logger().info('🤖 Kinematics Action Server with Marker Synchronization online.')

    def goal_callback(self, goal_request):
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    def publish_robot_joints(self, torso_angle, arm_angle):
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = ['base_to_torso', 'torso_to_arm']
        joint_state.position = [float(torso_angle), float(arm_angle)]
        self.joint_pub.publish(joint_state)

    def broadcast_snapped_box(self, parent_frame):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = parent_frame
        t.child_frame_id = 'box_frame'

        if parent_frame == 'arm_link':
            # Khối hộp đỏ cao 0.2m, đầu kẹp cao 0.8m -> Đặt Z = 0.7 để hộp nằm khít ngay dưới tấm gắp gold
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.7  
        else:
            # Dropped storage array targets: Nằm yên vị tại trung tâm Pallet mục tiêu sau khi nhả kẹp
            t.transform.translation.x = 0.0
            t.transform.translation.y = -0.8  # Đặt tại vị trí Pallet đối xứng qua trục xoay của robot
            t.transform.translation.z = 0.1

        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

        # Refresh the active rendering dimensions of the visual block mesh frame link
        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = 'box_frame'
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        
        # Explicitly initialize separate components inside geometry Pose 
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0
        
        self.marker_pub.publish(marker)

    def execute_callback(self, goal_handle):
        box_id = goal_handle.request.box_id
        feedback_msg = PalletizeBox.Feedback()
        
        steps = [
            (10, 'Picking', 0.0, -1.2),           
            (40, 'Moving to pallet', 1.57, 0.2),  
            (70, 'Placing', 1.57, -0.9),          
            (90, 'Returning', 0.0, 0.0),
            (100, 'Complete', 0.0, 0.0)
        ]

        for progress, step, torso_angle, arm_angle in steps:
            feedback_msg.progress = float(progress)
            feedback_msg.current_step = step
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Box {box_id}: {progress}% - {step}')

            self.publish_robot_joints(torso_angle, arm_angle)

            # SỬA ĐỔI LOGIC PHÁT CHUẨN XÁC:
            # Hộp đỏ phải bám theo arm_link xuyên suốt cả quá trình hạ tay xuống đặt hàng (Placing)
            if step in ['Picking', 'Moving to pallet', 'Placing']:
                self.broadcast_snapped_box('arm_link')
            # Chỉ buông nhả hộp sang hệ tọa độ sàn nhà (base_link) khi robot bắt đầu rút tay về (Returning/Complete)
            elif step in ['Returning', 'Complete']:
                self.broadcast_snapped_box('base_link')

            time.sleep(1.0)

        goal_handle.succeed()
        result = PalletizeBox.Result()
        result.success = True
        result.message = f'Box {box_id} complete.'
        return result


def main(args=None):
    rclpy.init(args=args)
    node = PalletizeActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
