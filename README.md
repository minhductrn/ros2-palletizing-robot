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
2. **`my_first_ros2_package`**: An `ament_python` package containing execution scripts for our synchronized simulation nodes.

Current package structure:

    ros2_ws/
    ├── src/
    │   ├── my_robot_interfaces/
    │   │   ├── msg/
    │   │   │   └── BoxInfo.msg
    │   │   ├── srv/
    │   │   │   └── SetGripperStatus.srv
    │   │   ├── CMakeLists.txt
    │   │   └── package.xml
    │   │
    │   └── my_first_ros2_package/
    │       ├── my_first_ros2_package/
    │       │   ├── __init__.py
    │       │   ├── hello_node.py
    │       │   ├── publisher_node.py
    │       │   ├── subscriber_node.py
    │       │   └── gripper_service_node.py
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

Created standard Python ROS 2 execution targets using `rclpy` to compartmentalize robot software features.

2. Custom Message Interface (`BoxInfo.msg`)

Designed a custom interface layout to handle industrial telemetry data streams containing kinematics payloads:
```text
int32 box_id       # Sequence unique counter
float64 x          # 3D position coordinate (X-axis in meters)
float64 y          # 3D position coordinate (Y-axis in meters)
float64 z          # 3D position coordinate (Z-axis in meters)
float64 weight     # Package mass payload (in kg)
string status      # Operational cycle flag ('In Queue' / 'Placed on Pallet')
```

3. Custom Service Interface (`SetGripperStatus.srv`)

Developed a Request-Response interaction architecture to safely change the pneumatic end-effector state:
```text
bool activate      # Request: True to engage suction, False to release
---
bool success       # Response: Execution outcome affirmation
string message     # Response: Status log breakdown text
```

4. Autonomous Event-Driven Control Pipeline

Integrated both **Topics** and **Services** into a single closed-loop automated logistics design:
*   **`my_pub_node`**: Generates real-time randomized box geometry configurations and streams them over the `/box_chatter` topic.
*   **`my_sub_node`**: Evaluates incoming telemetry fields. If a box has a status of `In Queue`, it instantly acts as a **Service Client**, auto-triggering an asynchronous call to the gripper controller.
*   **`my_gripper_srv_node`**: Processes the incoming state-change requests to engage/disengage vacuum suction and sends back execution receipts.

5. ROS 2 Communication Graph

The system communication pipeline verified and visualised using **`rqt_graph`**:

![ROS 2 Network Graph](rosgraph.png)

6. Automated Multi-Node Launch Execution

Utilized a centralized `my_nodes_launch.py` script to orchestrate and bring up the complete 3-node lifecycle concurrently inside a single shell:

    ros2 launch my_first_ros2_package my_nodes_launch.py

Useful Commands
Source ROS 2

    source /opt/ros/lyrical/setup.bash

Build workspace

    cd ~/ros2_ws
    colcon build --symlink-install

Source workspace

    source install/setup.bash

Start the complete autonomous system

    ros2 launch my_first_ros2_package my_nodes_launch.py

Inspect custom interfaces

    ros2 interface show my_robot_interfaces/msg/BoxInfo
    ros2 interface show my_robot_interfaces/srv/SetGripperStatus

Trigger gripper manually

    ros2 service call /set_gripper_status my_robot_interfaces/srv/SetGripperStatus "{activate: true}"

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
        Services (.srv)
        ↓
        Actions (.action)
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
    ☑ Implement Request-Response Gripper Services (.srv)
    ☑ Build and run ROS 2 package
    ☑ Push project to GitHub

Next

    ☐ ROS 2 Actions (Trajectory and path planning execution tracking)
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
