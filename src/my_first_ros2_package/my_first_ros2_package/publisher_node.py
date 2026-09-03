import random
import rclpy
from rclpy.node import Node
# Import custom message bạn vừa tạo
from my_robot_interfaces.msg import BoxInfo


class PublisherNode(Node):

    def __init__(self):
        super().__init__('my_pub_node')  # Đổi tên node đồng bộ với file Launch

        # Khai báo publisher sử dụng kiểu dữ liệu BoxInfo trên topic 'box_chatter'
        self.publisher = self.create_publisher(
            BoxInfo,
            'box_chatter',
            10
        )

        self.counter = 0
        self.timer = self.create_timer(1.0, self.publish_message)

    def publish_message(self):
        msg = BoxInfo()

        # Giả lập dữ liệu ngẫu nhiên cho thùng hàng xếp lên pallet
        msg.box_id = self.counter
        msg.x = round(random.uniform(-1.0, 1.0), 3)       # Tọa độ X từ -1m đến 1m
        msg.y = round(random.uniform(-1.0, 1.0), 3)       # Tọa độ Y từ -1m đến 1m
        msg.z = round(random.uniform(0.0, 1.5), 3)        # Chiều cao Z từ 0m đến 1.5m
        msg.weight = round(random.uniform(2.0, 15.0), 2)  # Trọng lượng từ 2kg đến 15kg

        # Cập nhật trạng thái dựa trên số thứ tự
        if self.counter % 2 == 0:
            msg.status = 'In Queue'
        else:
            msg.status = 'Placed on Pallet'

        # Phát dữ liệu lên mạng ROS 2
        self.publisher.publish(msg)

        # In log trực quan ra màn hình Terminal
        self.get_logger().info(
            f'📦 Published Box #{msg.box_id} | Pos: ({msg.x}, {msg.y}, {msg.z}) | '
            f'Wt: {msg.weight}kg | Status: {msg.status}'
        )

        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = PublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
