from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Oversætter din Windows-sti til en WSL-sti, som ROS kan forstå
    world_file_path = '/mnt/c/Projekter/ros2_ws/src/stage_ros2/world/lines.world'

    return LaunchDescription([
        # 1. Stage Simulator (Starter den virtuelle verden)
        Node(
            package='stage_ros2',
            executable='stage_ros2',
            name='stage',
            parameters=[{'world_file': world_file_path}],
            output='screen'
        ),

        # 2. Din UDP Bridge (Forbindelse til telefonen)
        Node(
            package='robot_remote',
            executable='publisher_remote',
            name='udp_twist_bridge',
            output='screen'
        ),

        # 3. Din Intersection Detector (Lidar-hjernen)
        Node(
            package='robot_remote',
            executable='intersection_detector',
            name='intersection_detector',
            output='screen'
        )
    ])