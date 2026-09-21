import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_first_ros2_package'

    package_share = get_package_share_directory(package_name)

    urdf_file = os.path.join(
        package_share,
        'urdf',
        'palletizing_robot.urdf'
    )

    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    # Start Gazebo in headless/server-only mode.
    # This avoids the Gazebo GUI / WSLg display instability.
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', 'empty.sdf'],
        output='screen'
    )

    # Publish robot_description and TF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description,
                'use_sim_time': True
            }
        ]
    )

    # Spawn robot into Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'empty',
            '-file', urdf_file,
            '-name', 'palletizing_robot',
            '-x', '0',
            '-y', '0',
            '-z', '0'
        ],
        output='screen'
    )

    # Bridge Gazebo simulation clock to ROS 2
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    # Load + configure + activate joint_state_broadcaster
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    # Load + configure + activate arm_controller
    arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'arm_controller',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        clock_bridge,
        joint_state_broadcaster,
        arm_controller,
    ])