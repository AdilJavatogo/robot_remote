# Vi starter med et fuldt funktionelt ROS2 Jazzy image
FROM ros:jazzy-ros-base

# Sæt arbejdsmappen inde i containeren
WORKDIR /app/ros2_ws

# Kopiér dit workspace fra din PC og ind i containeren
COPY src/ /app/ros2_ws/src/

# Byg din Python pakke
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build"

# Åbn port 5000, så containeren kan lytte efter MAUI-appens UDP
EXPOSE 5000/udp

# Fortæl containeren hvad den skal køre, når den starter
CMD ["/bin/bash", "-c", "source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 run robot_remote udp_twist_bridge"]