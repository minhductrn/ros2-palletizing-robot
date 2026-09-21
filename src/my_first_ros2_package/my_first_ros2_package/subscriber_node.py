#!/usr/bin/env python3

from collections import deque

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from my_robot_interfaces.msg import BoxInfo
from my_robot_interfaces.action import PalletizeBox


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('my_sub_node')

        self.robot_busy = False
        self.system_initialized = False

        # FIFO queue for boxes waiting to be processed.
        self.box_queue = deque()

        # ============================================================
        # PARAMETERS
        # ============================================================

        self.declare_parameter('max_weight_capacity', 10.0)
        self.declare_parameter('operation_mode', 'AUTO')

        max_weight = (
            self.get_parameter('max_weight_capacity')
            .get_parameter_value()
            .double_value
        )

        op_mode = (
            self.get_parameter('operation_mode')
            .get_parameter_value()
            .string_value
        )

        self.get_logger().info(
            f'📋 Parameters initialized | '
            f'Mode: {op_mode} | '
            f'Max weight: {max_weight}kg'
        )

        # ============================================================
        # PALLETIZE ACTION CLIENT
        # ============================================================

        self.action_client = ActionClient(
            self,
            PalletizeBox,
            'palletize_box'
        )

        # Check action-server availability without blocking startup.
        self.connection_timer = self.create_timer(
            1.0,
            self.check_system_connections
        )

        # ============================================================
        # BOX DETECTION SUBSCRIBER
        # ============================================================

        self.subscription = self.create_subscription(
            BoxInfo,
            'box_chatter',
            self.listener_callback,
            10
        )

    def check_system_connections(self):

        if not self.action_client.wait_for_server(timeout_sec=0.0):
            self.get_logger().info(
                '⏳ Waiting for Palletize Action Server '
                'to come online...'
            )
            return

        self.system_initialized = True

        self.get_logger().info(
            '⚙️ SYSTEM READY: Palletizing supervisor '
            'connected successfully.'
        )

        self.connection_timer.cancel()

    # ================================================================
    # BOX INPUT
    # ================================================================

    def listener_callback(self, msg):

        if not self.system_initialized:
            return

        max_weight = (
            self.get_parameter('max_weight_capacity')
            .get_parameter_value()
            .double_value
        )

        op_mode = (
            self.get_parameter('operation_mode')
            .get_parameter_value()
            .string_value
        )

        self.get_logger().info(
            f'📦 Box #{msg.box_id} detected | '
            f'Weight: {msg.weight}kg | '
            f'[Mode: {op_mode}, Max: {max_weight}kg]'
        )

        # ============================================================
        # SAFETY / WORKFLOW GATES
        # ============================================================

        if op_mode != 'AUTO':
            self.get_logger().warning(
                f'⚠️ Box #{msg.box_id} not processed because '
                f'operation mode is [{op_mode}], not [AUTO].'
            )
            return

        if msg.weight > max_weight:
            self.get_logger().warning(
                f'⚠️ OVERLOAD DETECTED: '
                f'Box #{msg.box_id} ({msg.weight}kg) exceeds '
                f'safety threshold ({max_weight}kg). '
                f'Request denied.'
            )
            return

        if msg.status != 'In Queue':
            self.get_logger().warning(
                f'⚠️ Box #{msg.box_id} ignored because '
                f'status is [{msg.status}].'
            )
            return

        # ============================================================
        # ADD VALID BOX TO FIFO QUEUE
        # ============================================================

        self.box_queue.append(msg)

        self.get_logger().info(
            f'📥 Box #{msg.box_id} added to queue | '
            f'Queue depth: {len(self.box_queue)}'
        )

        # If the robot is available, start immediately.
        self.process_next_box()

    # ================================================================
    # FIFO QUEUE PROCESSING
    # ================================================================

    def process_next_box(self):

        # Robot is already processing another box.
        if self.robot_busy:
            return

        # No boxes are waiting.
        if not self.box_queue:
            return

        # FIFO:
        # popleft() retrieves the oldest box in the queue.
        next_box = self.box_queue.popleft()

        self.robot_busy = True

        self.get_logger().info(
            f'🏁 Starting palletizing cycle for '
            f'Box #{next_box.box_id} | '
            f'Remaining queue: {len(self.box_queue)}'
        )

        self.send_palletize_goal(next_box.box_id)

    # ================================================================
    # PALLETIZE ACTION
    # ================================================================

    def send_palletize_goal(self, box_id):

        goal_msg = PalletizeBox.Goal()
        goal_msg.box_id = box_id

        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(
            lambda future:
            self.goal_response_callback(future, box_id)
        )

    def goal_response_callback(self, future, box_id):

        try:
            goal_handle = future.result()

            if not goal_handle.accepted:

                self.get_logger().error(
                    f'❌ Palletize action goal rejected '
                    f'for Box #{box_id}.'
                )

                self.robot_busy = False

                # Try the next waiting box.
                self.process_next_box()

                return

            self.get_logger().info(
                f'✅ Palletize action goal accepted '
                f'for Box #{box_id}.'
            )

            result_future = goal_handle.get_result_async()

            result_future.add_done_callback(
                lambda future:
                self.get_result_callback(future, box_id)
            )

        except Exception as exc:

            self.get_logger().error(
                f'❌ Failed to send palletize goal '
                f'for Box #{box_id}: {exc}'
            )

            self.robot_busy = False

            # Continue with the next queued box.
            self.process_next_box()

    def feedback_callback(self, feedback_msg):

        feedback = feedback_msg.feedback

        self.get_logger().info(
            f'📊 [Palletize Progress]: '
            f'{feedback.progress}% | '
            f'Active Step: {feedback.current_step}'
        )

    def get_result_callback(self, future, box_id):

        try:
            result_response = future.result()
            result = result_response.result

            if result.success:

                self.get_logger().info(
                    f'🏁 Box #{box_id} cycle accomplished '
                    f'successfully: {result.message}'
                )

            else:

                self.get_logger().error(
                    f'❌ Box #{box_id} palletizing cycle failed: '
                    f'{result.message}'
                )

        except Exception as exc:

            self.get_logger().error(
                f'❌ Failed to receive palletize result '
                f'for Box #{box_id}: {exc}'
            )

        finally:

            # Current box has finished.
            self.robot_busy = False

            self.get_logger().info(
                f'📦 Queue depth after cycle: '
                f'{len(self.box_queue)}'
            )

            # Automatically start the next waiting box.
            self.process_next_box()


def main(args=None):

    rclpy.init(args=args)

    node = SubscriberNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()