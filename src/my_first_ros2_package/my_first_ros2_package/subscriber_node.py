import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('subscriber_node')

        # Tạo subscriber lắng nghe từ topic 'chatter'
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )
        self.subscription  # Ngăn chặn cảnh báo biến không sử dụng

    def listener_callback(self, msg):
        # Hàm này tự động kích hoạt mỗi khi nhận được dữ liệu từ publisher
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)

    node = SubscriberNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
