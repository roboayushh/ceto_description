cmake_minimum_required(VERSION 3.8)
project(ceto_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(
  ament_cmake REQUIRED
  ament_cmake_python REQUIRED
  rclcpp REQUIRED
  rclpy REQUIRED
	ros_gz REQUIRED
)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  models
  worlds
  config
  urdf
  rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
