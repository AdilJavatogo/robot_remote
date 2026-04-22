from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    lab_file_path = '/mnt/c/Projekter/ros2_ws/src/stage_ros2/world/lab.world'

    return LaunchDescription([
        Node(
            package='stage_ros2',
            executable='stageros',
            name='stage',
            parameters=[{'lab_file': lab_file_path}],
            output='screen'
        ),
        Node(
            package='robot_remote',
            executable='publisher_remote',
            name='udp_twist_bridge',
            output='screen'
        ),
        Node(
            package='robot_remote',
            executable='intersection_detector',
            name='intersection_detector',
            output='screen'
        )
    ])