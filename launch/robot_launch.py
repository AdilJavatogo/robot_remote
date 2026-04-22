from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_remote',
            executable='publisher_remote', # Navnet fra din setup.py
            name='udp_twist_bridge',
            output='screen'
        ),
        Node(
            package='robot_remote',
            executable='intersection_detector', # Navnet fra din setup.py
            name='intersection_detector',
            output='screen'
        )
    ])