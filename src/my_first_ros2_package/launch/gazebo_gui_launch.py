from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():

    # Start only the Gazebo GUI client.
    # The Gazebo simulation server must already be running.
    gazebo_gui = ExecuteProcess(
        cmd=['gz', 'sim', '-g'],
        output='screen'
    )

    return LaunchDescription([
        gazebo_gui,
    ])