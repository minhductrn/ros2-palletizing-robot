#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from rclpy.action import (
    ActionClient,
    ActionServer,
    CancelResponse,
    GoalResponse,
)

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

from my_robot_interfaces.action import PalletizeBox


class PalletizeActionServer(Node):

    def __init__(self):
        super().__init__('my_action_server_node')

        # Action client for the real ros2_control trajectory controller
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )

        # Custom palletizing action server
        self._action_server = ActionServer(
            self,
            PalletizeBox,
            'palletize_box',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info(
            'Palletize Action Server connected to ros2_control.'
        )

    def goal_callback(self, goal_request):
        self.get_logger().info(
            f'Received palletize request for box {goal_request.box_id}'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT

    async def move_robot(
        self,
        torso_angle,
        arm_angle,
        duration_sec=2
    ):
        """
        Send a trajectory goal to the real JointTrajectoryController
        and wait asynchronously for completion.
        """

        if not self.arm_client.server_is_ready():
            self.get_logger().error(
                'arm_controller action server is not available.'
            )
            return False

        goal_msg = FollowJointTrajectory.Goal()

        goal_msg.trajectory.joint_names = [
            'base_to_torso',
            'torso_to_arm',
        ]

        point = JointTrajectoryPoint()

        point.positions = [
            float(torso_angle),
            float(arm_angle),
        ]

        point.time_from_start.sec = int(duration_sec)

        goal_msg.trajectory.points = [point]

        self.get_logger().info(
            f'Moving robot -> '
            f'torso={torso_angle:.2f}, '
            f'arm={arm_angle:.2f}'
        )

        trajectory_goal_handle = await self.arm_client.send_goal_async(
            goal_msg
        )

        if trajectory_goal_handle is None:
            self.get_logger().error(
                'Failed to receive trajectory goal response.'
            )
            return False

        if not trajectory_goal_handle.accepted:
            self.get_logger().error(
                'Trajectory goal was rejected by arm_controller.'
            )
            return False

        self.get_logger().info(
            'Trajectory goal accepted by arm_controller.'
        )

        result_response = await trajectory_goal_handle.get_result_async()

        if result_response is None:
            self.get_logger().error(
                'No trajectory result received.'
            )
            return False

        if result_response.result.error_code != 0:
            self.get_logger().error(
                'Trajectory failed: '
                f'{result_response.result.error_string}'
            )
            return False

        self.get_logger().info(
            'Trajectory completed successfully.'
        )

        return True

    async def execute_callback(self, goal_handle):

        box_id = goal_handle.request.box_id

        feedback_msg = PalletizeBox.Feedback()

        # progress, step, base rotation, arm angle
        steps = [
            (10, 'Picking', 0.0, -1.2),
            (40, 'Moving to pallet', 1.57, 0.2),
            (70, 'Placing', 1.57, -0.9),
            (90, 'Returning', 0.0, 0.0),
            (100, 'Complete', 0.0, 0.0),
        ]

        for progress, step, torso_angle, arm_angle in steps:

            if goal_handle.is_cancel_requested:

                goal_handle.canceled()

                result = PalletizeBox.Result()
                result.success = False
                result.message = (
                    f'Box {box_id} palletizing canceled.'
                )

                return result

            feedback_msg.progress = float(progress)
            feedback_msg.current_step = step

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Box {box_id}: {progress}% - {step}'
            )

            success = await self.move_robot(
                torso_angle,
                arm_angle,
                duration_sec=2
            )

            if not success:

                goal_handle.abort()

                result = PalletizeBox.Result()
                result.success = False
                result.message = (
                    f'Box {box_id} failed during step: {step}'
                )

                return result

        goal_handle.succeed()

        result = PalletizeBox.Result()
        result.success = True
        result.message = f'Box {box_id} complete.'

        self.get_logger().info(
            f'Box {box_id}: palletizing sequence complete.'
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