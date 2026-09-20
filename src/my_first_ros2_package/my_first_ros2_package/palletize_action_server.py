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
from my_robot_interfaces.srv import SetGripperStatus


class PalletizeActionServer(Node):

    def __init__(self):
        super().__init__('my_action_server_node')

        # Real robot trajectory controller
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )

        # Gripper service client
        self.gripper_client = self.create_client(
            SetGripperStatus,
            'set_gripper_status'
        )

        # High-level palletizing action
        self._action_server = ActionServer(
            self,
            PalletizeBox,
            'palletize_box',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info(
            'Palletize Action Server connected to '
            'ros2_control and gripper service.'
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
        """Send a trajectory to JointTrajectoryController."""

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
                'Trajectory goal rejected by arm_controller.'
            )
            return False

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

    async def set_gripper(self, activate):
        """Turn the logical suction gripper ON or OFF."""

        if not self.gripper_client.service_is_ready():
            self.get_logger().error(
                'Gripper service is not available.'
            )
            return False

        request = SetGripperStatus.Request()
        request.activate = activate

        state = 'ON' if activate else 'OFF'

        self.get_logger().info(
            f'Requesting gripper {state}...'
        )

        response = await self.gripper_client.call_async(request)

        if response is None:
            self.get_logger().error(
                f'No response received for gripper {state}.'
            )
            return False

        if not response.success:
            self.get_logger().error(
                f'Gripper {state} failed: {response.message}'
            )
            return False

        self.get_logger().info(
            f'Gripper {state}: {response.message}'
        )

        return True

    async def execute_callback(self, goal_handle):

        box_id = goal_handle.request.box_id
        feedback_msg = PalletizeBox.Feedback()

        # ---------------------------------------------------------
        # STEP 1 — MOVE TO PICK
        # ---------------------------------------------------------
        feedback_msg.progress = 10.0
        feedback_msg.current_step = 'Moving to pick'
        goal_handle.publish_feedback(feedback_msg)

        self.get_logger().info(
            f'Box {box_id}: 10% - Moving to pick'
        )

        if not await self.move_robot(0.0, -1.2, 2):
            return self.abort_goal(
                goal_handle,
                box_id,
                'moving to pick'
            )

        # ---------------------------------------------------------
        # STEP 2 — GRIP BOX
        # ---------------------------------------------------------
        feedback_msg.progress = 25.0
        feedback_msg.current_step = 'Picking'
        goal_handle.publish_feedback(feedback_msg)

        self.get_logger().info(
            f'Box {box_id}: 25% - Picking'
        )

        if not await self.set_gripper(True):
            return self.abort_goal(
                goal_handle,
                box_id,
                'gripper activation'
            )

        # ---------------------------------------------------------
        # STEP 3 — MOVE TO PALLET
        # ---------------------------------------------------------
        feedback_msg.progress = 50.0
        feedback_msg.current_step = 'Moving to pallet'
        goal_handle.publish_feedback(feedback_msg)

        self.get_logger().info(
            f'Box {box_id}: 50% - Moving to pallet'
        )

        if not await self.move_robot(1.57, 0.2, 2):
            return self.abort_goal(
                goal_handle,
                box_id,
                'moving to pallet'
            )

        # ---------------------------------------------------------
        # STEP 4 — LOWER TO PLACE
        # ---------------------------------------------------------
        feedback_msg.progress = 70.0
        feedback_msg.current_step = 'Placing'
        goal_handle.publish_feedback(feedback_msg)

        self.get_logger().info(
            f'Box {box_id}: 70% - Placing'
        )

        if not await self.move_robot(1.57, -0.9, 2):
            return self.abort_goal(
                goal_handle,
                box_id,
                'placing'
            )

        # ---------------------------------------------------------
        # STEP 5 — RELEASE BOX
        # ---------------------------------------------------------
        feedback_msg.progress = 80.0
        feedback_msg.current_step = 'Releasing'
        goal_handle.publish_feedback(feedback_msg)

        self.get_logger().info(
            f'Box {box_id}: 80% - Releasing'
        )

        if not await self.set_gripper(False):
            return self.abort_goal(
                goal_handle,
                box_id,
                'gripper release'
            )

        # ---------------------------------------------------------
        # STEP 6 — RETURN HOME
        # ---------------------------------------------------------
        feedback_msg.progress = 90.0
        feedback_msg.current_step = 'Returning'
        goal_handle.publish_feedback(feedback_msg)

        self.get_logger().info(
            f'Box {box_id}: 90% - Returning'
        )

        if not await self.move_robot(0.0, 0.0, 2):
            return self.abort_goal(
                goal_handle,
                box_id,
                'returning home'
            )

        # ---------------------------------------------------------
        # COMPLETE
        # ---------------------------------------------------------
        feedback_msg.progress = 100.0
        feedback_msg.current_step = 'Complete'
        goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()

        result = PalletizeBox.Result()
        result.success = True
        result.message = f'Box {box_id} complete.'

        self.get_logger().info(
            f'Box {box_id}: palletizing cycle complete.'
        )

        return result

    def abort_goal(self, goal_handle, box_id, failed_step):

        goal_handle.abort()

        result = PalletizeBox.Result()
        result.success = False
        result.message = (
            f'Box {box_id} failed during {failed_step}.'
        )

        self.get_logger().error(result.message)

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