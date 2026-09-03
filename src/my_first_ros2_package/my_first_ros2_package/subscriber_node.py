import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import BoxInfo
from my_robot_interfaces.srv import SetGripperStatus


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('my_sub_node')

        # 1. Tạo subscriber lắng nghe thông tin thùng hàng từ topic
        self.subscription = self.create_subscription(
            BoxInfo,
            'box_chatter',
            self.listener_callback,
            10
        )

        # 2. Tạo Service Client để kết nối với cụm điều khiển tay gắp
        self.cli = self.create_client(SetGripperStatus, 'set_gripper_status')
        
        # Chờ cho đến khi Service Server trực tuyến mới bắt đầu chạy node
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('⏳ Waiting for gripper service to become available...')
            
        self.get_logger().info('🚀 Subscriber & Gripper Client connected successfully.')

    def listener_callback(self, msg):
        self.get_logger().info(
            f'📥 Heard Box #{msg.box_id} -> Status: [{msg.status}]'
        )

        # Nếu phát hiện thùng hàng đang ở trong hàng đợi (In Queue) -> Tự động ra lệnh gắp!
        if msg.status == 'In Queue':
            self.get_logger().info(f'🤖 Box #{msg.box_id} is ready! Automatically sending grasp command...')
            self.send_gripper_request(True)

    def send_gripper_request(self, activate_state):
        req = SetGripperStatus.Request()
        req.activate = activate_state
        
        # Gửi yêu cầu bất đồng bộ (Asynchronous Call) để tránh làm nghẽn luồng nhận dữ liệu
        self.future = self.cli.call_async(req)
        # Thêm hàm callback xử lý khi nhận lời phản hồi từ phía Server
        self.future.add_done_callback(self.gripper_response_callback)

    def gripper_response_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'✅ Gripper Response -> Success: {response.success} | Msg: {response.message}')
        except Exception as e:
            self.get_logger().error(f'❌ Automatic service call failed: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = SubscriberNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
