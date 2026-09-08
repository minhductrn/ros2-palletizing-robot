import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # 1. Lấy đường dẫn tuyệt đối của thư mục cài đặt share
    package_share_dir = get_package_share_directory('my_first_ros2_package')
    
    # 2. Định nghĩa chính xác đường dẫn đến file params.yaml
    config_file_path = os.path.join(package_share_dir, 'config', 'params.yaml')

    return LaunchDescription([
        # Node 1: Phát tọa độ và thông số thùng hàng (Topic Publisher)
        Node(
            package='my_first_ros2_package',
            executable='publisher_node',
            name='my_pub_node',
            output='screen'
        ),
        # Node 2: Nhận tọa độ từ topic và tự động kích hoạt Action (ĐÃ THÊM NẠP YAML)
        Node(
            package='my_first_ros2_package',
            executable='subscriber_node',
            name='my_sub_node',
            output='screen',
            parameters=[config_file_path]  # <--- DÒNG QUAN TRỌNG NHẤT BỊ THIẾU
        ),
        # Node 3: Điều khiển cơ cấu gắp kẹp/hút (Service Server)
        Node(
            package='my_first_ros2_package',
            executable='gripper_service_node',
            name='my_gripper_srv_node',
            output='screen'
        ),
        # Node 4: Mô phỏng hành trình dịch chuyển quỹ đạo robot (Action Server)
        Node(
            package='my_first_ros2_package',
            executable='palletize_action_server',
            name='my_action_server_node',
            output='screen'
        )
    ])
