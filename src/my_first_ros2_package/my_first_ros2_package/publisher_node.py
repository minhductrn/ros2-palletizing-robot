#!/usr/bin/env python3
import random
import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import BoxInfo

# IMPORT THE CORE GEOMETRY, TF2, AND MARKER MESSAGES
from geometry_msgs.msg import TransformStamped
from visualization_msgs.msg import Marker
from tf2_ros import TransformBroadcaster


class PublisherNode(Node):

    def __init__(self):
        super().__init__('my_pub_node')

        # 1. Telemetry Publisher
        self.publisher = self.create_publisher(BoxInfo, 'box_chatter', 10)

        # 2. RViz 3D Marker Publisher (Visualizes the physical box shape)
        self.marker_pub = self.create_publisher(Marker, 'visualization_marker', 10)

        # 3. TF2 Broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        self.counter = 0
        # Tăng thời gian lên 4.0 giây để tương thích với chu trình gắp 4 giây của Action Server
        self.timer = self.create_timer(4.0, self.publish_message)
        
        # Biến lưu trữ vị trí cố định của hộp hiện tại trên băng tải
        self.current_box_x = 0.0
        self.current_box_y = 0.0
        self.is_box_spawned = False

        self.get_logger().info('📦 Telemetry Publisher, TF2 Broadcaster, and Marker Engine initialized.')

    def publish_message(self):
        msg = BoxInfo()

        # Tạo một vị trí ngẫu nhiên cố định cho chiếc hộp mới trên băng tải
        msg.box_id = self.counter
        self.current_box_x = round(random.uniform(-0.05, 0.05), 3)       
        self.current_box_y = round(random.uniform(-0.1, 0.1), 3)  # Nằm chuẩn tầm với đầu gắp
        msg.z = 0.1                                       
        msg.weight = round(random.uniform(2.0, 15.0), 2)
        msg.status = 'In Queue'

        msg.x = self.current_box_x
        msg.y = self.current_box_y

        # Lưu trạng thái đã sinh hộp để kích hoạt bộ phát liên tục
        self.is_box_spawned = True

        # Layer 1: Phát thông tin chuỗi lên Topic chatter
        self.publisher.publish(msg)
        self.get_logger().info(f'📦 New Box #{msg.box_id} spawned on conveyor belt.')

        # Phát liên tục TF và Marker trong nền để đảm bảo RViz2 không bị mất hình ảnh
        self.broadcast_conveyor_box()
        self.counter += 1

    def broadcast_conveyor_box(self):
        """Hàm phát dữ liệu hình học liên tục không bị ngắt quãng"""
        if not self.is_box_spawned:
            return

        # Layer 2: Broadcast hệ trục tọa độ TF2
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'conveyor_link'  
        t.child_frame_id = 'box_frame'       
        t.transform.translation.x = self.current_box_x
        t.transform.translation.y = self.current_box_y
        t.transform.translation.z = 0.1
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

        # Layer 3: Phát hình dáng khối hình lập phương màu đỏ 3D
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

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.w = 1.0  

        self.marker_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = PublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
