# ros2-palletizing-robot
ROS 2 robotics learning project
ROS 2 Palletizing Robot Learning

Name: Minh Duc Tran - Robots Operator @ tutorintelligence.com

This is my hands-on robotics learning project using Python, ROS 2, and robotics simulation, with the long-term goal of working with palletizing robots.

Development Environment

    OS: Ubuntu 26.04.1 LTS (Resolute)
    Environment: Windows 11 + WSL2
    ROS 2: Lyrical Luth
    Programming: Python 3
    IDE: Visual Studio Code
    Build System: Colcon
    Version Control: Git + GitHub

Workspace

    ~/ros2_ws

ROS 2 Packages

1. **`my_robot_interfaces`**: An `ament_cmake` package dedicated to compiling custom ROS 2 messages, services, and actions.
2. **`my_first_ros2_package`**: An `ament_python` package containing the execution scripts for our simulation nodes.

Current package structure:

    ros2_ws/
    ├── src/
    │   ├── my_robot_interfaces/
    │   │   ├── msg/
    │   │   │   └── BoxInfo.msg
    │   │   ├── CMakeLists.txt
    │   │   └── package.xml
    │   │
    │   └── my_first_ros2_package/
    │       ├── my_first_ros2_package/
    │       │   ├── __init__.py
    │       │   ├── hello_node.py
    │       │   ├── publisher_node.py
    │       │   └── subscriber_node.py
    │       │
    │       ├── launch/
    │       │   └── my_nodes_launch.py
    │       │
    │       ├── package.xml
    │       ├── setup.py
    │       └── setup.cfg
    │
    ├── build/
    ├── install/
    └── log/

What I Have Learned
1. ROS 2 Node

Created my first Python ROS 2 node:

`hello_node`

The node uses rclpy and runs inside the ROS 2 system.

2. Custom Message Interface (`BoxInfo.msg`)

Designed a custom interface layout to handle industrial telemetry data rather than simple string streams. The packet structural layout contains:
```text
int32 box_id       # Sequence unique counter
float64 x          # 3D position coordinate (X-axis in meters)
float64 y          # 3D position coordinate (Y-axis in meters)
float64 z          # 3D position coordinate (Z-axis in meters)
float64 weight     # Package mass payload (in kg)
string status      # Operational cycle flag ('In Queue' / 'Placed on Pallet')
```

3. Publisher

Created a Python publisher node:

`/my_pub_node`

The publisher generates real-time randomized box geometry configurations and streams them to:

`/box_chatter`

Example payload log output:
```text
📦 Published Box #0 | Pos: (0.355, -0.231, 0.432) | Wt: 12.83kg | Status: In Queue
📦 Published Box #1 | Pos: (0.311, 0.415, 1.259) | Wt: 3.29kg | Status: Placed on Pallet
```

4. Subscriber

Created a Python subscriber node:

`/my_sub_node`

The subscriber securely receives, unpacks, and processes telemetry fields from:

`/box_chatter`

5. ROS 2 Communication Graph

The system communication pipeline verified and visualised using **`rqt_graph`**:

![ROS 2 Network Graph](rosgraph.png)

6. ROS 2 Launch

Created:

`my_nodes_launch.py`

The launch file starts the publisher and subscriber together.

Instead of starting each node separately, I can start the system with one command:

    ros2 launch my_first_ros2_package my_nodes_launch.py

Useful Commands
Source ROS 2

    source /opt/ros/lyrical/setup.bash

Build workspace

    cd ~/ros2_ws
    colcon build --symlink-install

Source workspace

    source install/setup.bash

Run publisher

    ros2 run my_first_ros2_package publisher_node

Run subscriber

    ros2 run my_first_ros2_package subscriber_node

Start the complete system

    ros2 launch my_first_ros2_package my_nodes_launch.py

Inspect custom interfaces

    ros2 interface show my_robot_interfaces/msg/BoxInfo

Inspect topics

    ros2 topic list

    ros2 topic info /box_chatter

    ros2 topic echo /box_chatter

Inspect nodes

    ros2 node list

Learning Roadmap

My current learning path:

        Python
        ↓
        ROS 2 Fundamentals
        ↓
        Nodes
        ↓
        Topics
        ↓
        Publishers / Subscribers
        ↓
        Custom Messages (.msg)
        ↓
        Services
        ↓
        Actions
        ↓
        Parameters
        ↓
        Launch Files
        ↓
        TF2
        ↓
        URDF
        ↓
        Gazebo Simulation
        ↓
        ros2_control
        ↓
        MoveIt 2
        ↓
        Computer Vision
        ↓
        Palletizing Robot

Goal

The long-term goal of this project is to develop practical robotics skills that can be applied to industrial palletizing robots, including:

    Robot operation
    ROS 2 programming
    Robot communication
    Sensor integration
    Computer vision
    Robot motion planning
    Simulation
    Robot control
    Troubleshooting and system monitoring

Progress
ROS 2 Fundamentals

    ☑ Install ROS 2 Lyrical
    ☑ Configure ROS 2 in WSL2
    ☑ Create ROS 2 workspace
    ☑ Create Python ROS 2 package
    ☑ Create ROS 2 node
    ☑ Create publisher
    ☑ Create subscriber
    ☑ Understand topics
    ☑ View ROS 2 communication graph
    ☑ Create launch file
    ☑ Create Custom Message (.msg) interface package
    ☑ Build and run ROS 2 package
    ☑ Push project to GitHub

Next

    ☐ ROS 2 Services (Client/Server Gripper control)
    ☐ ROS 2 Actions
    ☐ Parameters
    ☐ Launch file improvements
    ☐ TF2
    ☐ URDF
    ☐ Gazebo
    ☐ ros2_control
    ☐ MoveIt 2
    ☐ Computer vision
    ☐ Palletizing robot simulation

Learning by building — Python → ROS 2 → Robotics.
