cmake_minimum_required(VERSION 3.8)
project(my_robot_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Tìm các gói phụ thuộc bắt buộc để biên dịch msg
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Khai báo file msg cần biên dịch
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BoxInfo.msg"
)

ament_package()

