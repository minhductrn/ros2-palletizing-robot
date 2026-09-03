from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Node 1: Phát tọa độ và thông số thùng hàng (Topic Publisher)
        Node(
            package='my_first_ros2_package',
            executable='publisher_node',
            name='my_pub_node',
            output='screen'
        ),
        # Node 2: Nhận và xử lý dữ liệu thùng hàng (Topic Subscriber)
        Node(
            package='my_first_ros2_package',
            executable='subscriber_node',
            name='my_sub_node',
            output='screen'
        ),
        # Node 3: Điều khiển cơ cấu gắp kẹp/hút (Service Server)
        Node(
            package='my_first_ros2_package',
            executable='gripper_service_node',
            name='my_gripper_srv_node',
            output='screen'
        )
    ])
