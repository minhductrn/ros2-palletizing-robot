from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_first_ros2_package',
            executable='publisher_node',
            name='my_pub_node',
            output='screen'
        ),
        Node(
            package='my_first_ros2_package',
            executable='subscriber_node',
            name='my_sub_node',
            output='screen'
        )
    ])
