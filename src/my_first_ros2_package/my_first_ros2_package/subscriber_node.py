import rclpy
from rclpy.node import Node
# Import custom message giống như bên phía publisher
from my_robot_interfaces.msg import BoxInfo


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('my_sub_node')

        # Lắng nghe dữ liệu BoxInfo trên topic 'box_chatter'
        self.subscription = self.create_subscription(
            BoxInfo,
            'box_chatter',
            self.listener_callback,
            10
        )
        self.subscription

    def listener_callback(self, msg):
        # Tách nhỏ các biến trong gói tin để xử lý logic hoặc in ra màn hình
        self.get_logger().info(
            f'📥 Heard Box #{msg.box_id} -> '
            f'X: {msg.x}m, Y: {msg.y}m, Z: {msg.z}m | '
            f'Weight: {msg.weight}kg | Status: [{msg.status}]'
        )


def main(args=None):
    rclpy.init(args=args)
    node = SubscriberNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
