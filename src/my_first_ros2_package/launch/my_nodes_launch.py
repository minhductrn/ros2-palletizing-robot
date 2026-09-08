import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # 1. Fetch absolute paths from the central system installation directory
    package_share_dir = get_package_share_directory('my_first_ros2_package')
    
    config_file_path = os.path.join(package_share_dir, 'config', 'params.yaml')
    urdf_file_path = os.path.join(package_share_dir, 'urdf', 'palletizing_robot.urdf')
    rviz_file_path = os.path.join(package_share_dir, 'rviz', 'robot_config.rviz')

    # 2. Read URDF contents directly to serve as the structural robot_description parameter
    with open(urdf_file_path, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # --- CORE WORKFLOW NODES ---
        # Node 1: Telemetry Publisher and TF2 Broadcaster
        Node(
            package='my_first_ros2_package',
            executable='publisher_node',
            name='my_pub_node',
            output='screen'
        ),
        # Node 2: Central Controller with dynamically loaded YAML parameters
        Node(
            package='my_first_ros2_package',
            executable='subscriber_node',
            name='my_sub_node',
            output='screen',
            parameters=[config_file_path]
        ),
        # Node 3: End-Effector Gripper Service Server
        Node(
            package='my_first_ros2_package',
            executable='gripper_service_node',
            name='my_gripper_srv_node',
            output='screen'
        ),
        # Node 4: Kinematic Path Planning Trajectory Action Server (Drives joint positions dynamically)
        Node(
            package='my_first_ros2_package',
            executable='palletize_action_server',
            name='my_action_server_node',
            output='screen'
        ),

        # --- GRAPHICAL 3D VISUALIZATION PIPELINE ---
        # Node 5: Joint State Publisher (Cấu hình lắng nghe góc khớp từ Action Server)
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{'source_list': ['/joint_states']}] # <--- DÒNG ÉP LẮNG NGHE QUAN TRỌNG
        ),

        # Node 6: Robot State Publisher (Calculates and broadcasts robot links and joints kinematics)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        # Node 7: RViz2 3D Interface (Automatically opens and maps our custom robot viewport profile)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_file_path]
        )
    ])
