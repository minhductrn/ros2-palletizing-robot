import time

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.node import Node

from my_robot_interfaces.action import PalletizeBox


class PalletizeActionServer(Node):

    def __init__(self):
        super().__init__('palletize_action_server')

        self._action_server = ActionServer(
            self,
            PalletizeBox,
            'palletize_box',
            self.execute_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info(
            'Palletize Action Server is ready.'
        )

    def cancel_callback(self, goal_handle):
        self.get_logger().info(
            'Cancel request received.'
        )

        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):

        box_id = goal_handle.request.box_id

        self.get_logger().info(
            f'Starting palletizing for Box {box_id}'
        )

        feedback_msg = PalletizeBox.Feedback()

        steps = [
            (10.0, 'Picking'),
            (40.0, 'Moving to pallet'),
            (70.0, 'Placing'),
            (90.0, 'Returning'),
            (100.0, 'Complete')
        ]

        for progress, current_step in steps:

            # Check whether the client requested cancellation
            if goal_handle.is_cancel_requested:

                goal_handle.canceled()

                result = PalletizeBox.Result()
                result.success = False
                result.message = (
                    f'Palletizing Box {box_id} was cancelled.'
                )

                self.get_logger().warn(
                    f'Box {box_id} palletizing cancelled.'
                )

                return result

            feedback_msg.progress = progress
            feedback_msg.current_step = current_step

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Box {box_id}: '
                f'{progress:.0f}% - {current_step}'
            )

            # Simulate robot movement
            time.sleep(2)

        goal_handle.succeed()

        result = PalletizeBox.Result()
        result.success = True
        result.message = (
            f'Box {box_id} successfully palletized.'
        )

        self.get_logger().info(
            f'Box {box_id} palletizing completed.'
        )

        return result


def main(args=None):

    rclpy.init(args=args)

    node = PalletizeActionServer()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()