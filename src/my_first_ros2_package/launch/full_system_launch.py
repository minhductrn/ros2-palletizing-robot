import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_first_ros2_package'

    package_share = get_package_share_directory(package_name)

    params_file = os.path.join(
        package_share,
        'config',
        'params.yaml'
    )

    gazebo_control_launch = os.path.join(
        package_share,
        'launch',
        'gazebo_control_launch.py'
    )

    gazebo_gui_launch = os.path.join(
        package_share,
        'launch',
        'gazebo_gui_launch.py'
    )

    # Launch arguments
    gui = LaunchConfiguration('gui')
    auto_publish = LaunchConfiguration('auto_publish')

    # ---------------------------------------------------------
    # Gazebo server + robot + ros2_control + controllers
    # ---------------------------------------------------------
    gazebo_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            gazebo_control_launch
        )
    )

    # ---------------------------------------------------------
    # Optional Gazebo GUI
    # ---------------------------------------------------------
    gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            gazebo_gui_launch
        ),
        condition=IfCondition(gui)
    )

    # ---------------------------------------------------------
    # Gripper service
    # ---------------------------------------------------------
    gripper_service = Node(
        package=package_name,
        executable='gripper_service_node',
        output='screen'
    )

    # ---------------------------------------------------------
    # Palletizing action server
    # ---------------------------------------------------------
    palletize_action_server = Node(
        package=package_name,
        executable='palletize_action_server',
        output='screen'
    )

    # ---------------------------------------------------------
    # High-level supervisor / FIFO queue
    # ---------------------------------------------------------
    subscriber = Node(
        package=package_name,
        executable='subscriber_node',
        output='screen',
        parameters=[params_file]
    )

    # ---------------------------------------------------------
    # Simulated box sensor / publisher
    # ---------------------------------------------------------
    publisher = Node(
        package=package_name,
        executable='publisher_node',
        output='screen',
        condition=IfCondition(auto_publish)
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'gui',
            default_value='false',
            description='Start the Gazebo GUI'
        ),

        DeclareLaunchArgument(
            'auto_publish',
            default_value='true',
            description='Automatically publish boxes to the conveyor'
        ),

        # Start simulation first
        gazebo_control,

        # GUI connects to the already-running server
        TimerAction(
            period=2.0,
            actions=[gazebo_gui]
        ),

        # Start gripper service
        TimerAction(
            period=3.0,
            actions=[gripper_service]
        ),

        # Start palletizing action server
        TimerAction(
            period=5.0,
            actions=[palletize_action_server]
        ),

        # Start supervisor and box publisher last
        TimerAction(
            period=7.0,
            actions=[
                subscriber,
                publisher
            ]
        ),
    ])
