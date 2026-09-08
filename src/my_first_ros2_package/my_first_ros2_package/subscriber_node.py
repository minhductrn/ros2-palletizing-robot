#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.msg import BoxInfo
from my_robot_interfaces.srv import SetGripperStatus
from my_robot_interfaces.action import PalletizeBox


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('my_sub_node')

        self.robot_busy = False
        self.system_initialized = False  # Cờ kiểm tra kết nối hệ thống

        # ==================== PARAMETER DECLARATIONS ====================
        self.declare_parameter('max_weight_capacity', 10.0)
        self.declare_parameter('operation_mode', 'AUTO')
        self.get_logger().info('📋 Parameters initialized. Default max weight threshold: 10.0kg')
        # ================================================================

        # 1. Initialize Clients (KHÔNG DÙNG VÒNG LẶP WHILE CHẶN LUỒNG)
        self.gripper_client = self.create_client(SetGripperStatus, 'set_gripper_status')
        self.action_client = ActionClient(self, PalletizeBox, 'palletize_box')

        # 2. Tạo một Timer chạy mỗi 1 giây để kiểm tra kết nối ngầm cho đến khi kết nối thành công
        self.connection_timer = self.create_timer(1.0, self.check_system_connections)

        # 3. Initialize Topic Subscriber
        self.subscription = self.create_subscription(
            BoxInfo,
            'box_chatter',
            self.listener_callback,
            10
        )

    def check_system_connections(self):
        """Asynchronously checks service and action servers connectivity without blocking"""
        if not self.gripper_client.service_is_ready():
            self.get_logger().info('⏳ Waiting for Gripper Service Server to come online...')
            return

        # SỬA DÒNG NÀY: Sử dụng wait_for_server với timeout bằng 0 để kiểm tra trạng thái bất đồng bộ
        if not self.action_client.wait_for_server(timeout_sec=0.0):
            self.get_logger().info('⏳ Waiting for Palletize Action Server to come online...')
            return

        # Once both distributed ends are safely registered
        self.get_logger().info('⚙️ SYSTEM READY: Distributed automation loop connected successfully.')
        self.system_initialized = True
        self.connection_timer.cancel()  # Terminate checking timer loop to release thread resources

    def listener_callback(self, msg):
        # Nếu hệ thống chưa kết nối xong với các server khác hoặc robot đang bận, bỏ qua dữ liệu
        if not self.system_initialized or self.robot_busy:
            return

        max_weight = self.get_parameter('max_weight_capacity').get_parameter_value().double_value
        op_mode = self.get_parameter('operation_mode').get_parameter_value().string_value

        self.get_logger().info(
            f'📥 Box #{msg.box_id} detected | Wt: {msg.weight}kg | '
            f'[Profile -> Mode: {op_mode}, Max Cap: {max_weight}kg]'
        )

        # Dynamic Parameters Safety Filter
                # Dynamic Parameters Safety Filter
        if msg.weight > max_weight:
            # CHANGED: .warn() is now strictly .warning() in newer ROS 2 editions
            self.get_logger().warning(
                f'⚠️ OVERLOAD DETECTED: Box #{msg.box_id} ({msg.weight}kg) exceeds '
                f'safety threshold ({max_weight}kg). Request denied!'
            )
            return

        if msg.status == 'In Queue':
            self.robot_busy = True
            self.get_logger().info(f'🏁 Executing sequential workflow under [{op_mode}] control layout...')
            self.call_gripper_service(True, msg.box_id)

    # ==================== SERVICE HANDLERS (GRIPPER) ====================
    def call_gripper_service(self, activate_state, box_id):
        req = SetGripperStatus.Request()
        req.activate = activate_state
        future = self.gripper_client.call_async(req)
        future.add_done_callback(lambda f: self.gripper_response_callback(f, activate_state, box_id))

    def gripper_response_callback(self, future, activate_state, box_id):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'🧲 Gripper Service Receipt: {response.message}')
                if activate_state:
                    self.send_palletize_goal(box_id)
                else:
                    self.get_logger().info(f'🏁 Box #{box_id} cycle accomplished successfully.\n')
                    self.robot_busy = False
            else:
                self.get_logger().error('❌ Gripper failed to execute hardware change.')
                self.robot_busy = False
        except Exception as e:
            self.get_logger().error(f'❌ Gripper communication breakdown: {e}')
            self.robot_busy = False

    # ==================== ACTION HANDLERS (MOTION) ====================
    def send_palletize_goal(self, box_id):
        goal_msg = PalletizeBox.Goal()
        goal_msg.box_id = box_id
        send_goal_future = self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(lambda f: self.goal_response_callback(f, box_id))

    def goal_response_callback(self, future, box_id):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('❌ Path planning goal rejected by Server.')
            self.robot_busy = False
            return
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(lambda f: self.get_result_callback(f, box_id))

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'📊 [Motion Progress]: {feedback.progress}% | Active Step: {feedback.current_step}')

    def get_result_callback(self, future, box_id):
        self.get_logger().info(f'🔓 Destination reached. Shutting down vacuum suction...')
        self.call_gripper_service(False, box_id)


def main(args=None):
    rclpy.init(args=args)
    node = SubscriberNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
