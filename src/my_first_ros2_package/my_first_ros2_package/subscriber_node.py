import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.msg import BoxInfo
from my_robot_interfaces.srv import SetGripperStatus
from my_robot_interfaces.action import PalletizeBox


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('my_sub_node')

        # Biến cờ kiểm soát trạng thái bận của robot
        self.robot_busy = False

        # 1. Khởi tạo Subscriber lắng nghe Topic tọa độ hộp
        self.subscription = self.create_subscription(
            BoxInfo,
            'box_chatter',
            self.listener_callback,
            10
        )

        # 2. Khởi tạo Service Client điều khiển tay gắp (Gripper)
        self.gripper_client = self.create_client(SetGripperStatus, 'set_gripper_status')
        while not self.gripper_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('⏳ Waiting for Gripper Service to become available...')

        # 3. Khởi tạo Action Client điều khiển di chuyển (Palletize)
        self.action_client = ActionClient(self, PalletizeBox, 'palletize_box')
        while not self.action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info('⏳ Waiting for Palletize Action Server to become available...')
            
        self.get_logger().info('⚙️ SYSTEM READY: Subscriber, Service Client, and Action Client connected.')

    def listener_callback(self, msg):
        if self.robot_busy:
            return

        self.get_logger().info(f'📥 Detected Box #{msg.box_id} | Status: [{msg.status}]')

        # Nếu phát hiện hộp đang đợi -> Kích hoạt chuỗi tự động hóa khép kín
        if msg.status == 'In Queue':
            self.robot_busy = True
            self.get_logger().info(f'🏁 Starting automated assembly line for Box #{msg.box_id}...')
            
            # CHUỖI TỰ ĐỘNG HÓA - BƯỚC 1: Bật giác hút gắp hàng trước khi di chuyển
            self.call_gripper_service(True, msg.box_id)

    # ==================== PHẦN XỬ LÝ SERVICE (GRIPPER) ====================
    def call_gripper_service(self, activate_state, box_id):
        req = SetGripperStatus.Request()
        req.activate = activate_state
        
        future = self.gripper_client.call_async(req)
        # Truyền thêm tham số box_id vào callback bằng lambda function
        future.add_done_callback(lambda f: self.gripper_response_callback(f, activate_state, box_id))

    def gripper_response_callback(self, future, activate_state, box_id):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'🧲 Gripper Service: {response.message}')
                
                if activate_state:
                    # CHUỖI TỰ ĐỘNG HÓA - BƯỚC 2: Gắp chắc chắn rồi mới kích hoạt Action di chuyển
                    self.send_palletize_goal(box_id)
                else:
                    # CHUỖI TỰ ĐỘNG HÓA - BƯỚC 4: Đã nhả hàng thành công ➔ Kết thúc chu trình của 1 hộp
                    self.get_logger().info(f'🏁 Box #{box_id} processed completely. Standing by for next box.\n')
                    self.robot_busy = False
            else:
                self.get_logger().error('❌ Gripper failed to execute request.')
                self.robot_busy = False
        except Exception as e:
            self.get_logger().error(f'❌ Gripper service call failed: {e}')
            self.robot_busy = False

    # ==================== PHẦN XỬ LÝ ACTION (DI CHUYỂN) ====================
    def send_palletize_goal(self, box_id):
        goal_msg = PalletizeBox.Goal()
        goal_msg.box_id = box_id

        self.get_logger().info(f'📤 Kicking off Palletize Action Server for Box #{box_id}...')
        send_goal_future = self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(lambda f: self.goal_response_callback(f, box_id))

    def goal_response_callback(self, future, box_id):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('❌ Path planning goal rejected by Server.')
            self.robot_busy = False
            return

        self.get_logger().info('🎯 Robot trajectory accepted. Tracking motion...')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(lambda f: self.get_result_callback(f, box_id))

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'📊 [Motion Progress]: {feedback.progress}% | Step: {feedback.current_step}')

    def get_result_callback(self, future, box_id):
        result = future.result().result
        self.get_logger().info(f'✅ Action Complete -> Success: {result.success} | Msg: {result.message}')
        
        # CHUỖI TỰ ĐỘNG HÓA - BƯỚC 3: Robot di chuyển đến đích xong ➔ Gọi Service tắt lực hút để NHẢ HÀNG
        self.get_logger().info(f'🔓 Destination reached. Releasing Box #{box_id}...')
        self.call_gripper_service(False, box_id)


def main(args=None):
    rclpy.init(args=args)
    node = SubscriberNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
