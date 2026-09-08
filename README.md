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

1. **`my_robot_interfaces`**: An `**ament_cmake**` package dedicated to compiling custom ROS 2 messages, services, and actions.
2. **`my_first_ros2_package`**: An `**ament_python**` package containing execution scripts for our synchronized simulation nodes.

Current package structure:

    ros2_ws/
    ├── src/
    │   ├── my_robot_interfaces/
    │   │   ├── msg/
    │   │   │   └── BoxInfo.msg
    │   │   ├── srv/
    │   │   │   └── SetGripperStatus.srv
    │   │   ├── action/
    │   │   │   └── PalletizeBox.action
    │   │   ├── CMakeLists.txt
    │   │   └── package.xml
    │   │
    │   └── my_first_ros2_package/
    │       ├── my_first_ros2_package/
    │       │   ├── __init__.py
    │       │   ├── hello_node.py
    │       │   ├── publisher_node.py
    │       │   ├── subscriber_node.py
    │       │   ├── gripper_service_node.py
    │       │   └── palletize_action_server.py
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

4. Custom Action Interface (`PalletizeBox.action`)

Built a high-level asynchronous long-running task to manage path-planning cycles with real-time state feedback feedback tracking:
```text
int32 box_id               # Goal: Identifier target of the box
---
bool success               # Result: Cycle accomplishment validation
string message             # Result: Complete process summary status
---
float32 progress           # Feedback: Completion status scale (0% - 100%)
string current_step        # Feedback: Current execution phase ('Picking', 'Moving to pallet', etc.)
```

5. Autonomous Closed-Loop Event-Driven Pipeline

Integrated **Topics**, **Services**, and **Actions** into a single fully-automated logistics design containing **4 concurrent processes**:
*   **`my_pub_node`**: Spawns real-time randomized box geometry configurations and streams them over the `/box_chatter` topic.
*   **`my_sub_node`**: Acts as the central pipeline controller. When a box has a status of `In Queue`, it locks the system cflags, triggers the **Service Client** to engage the gripper, and kicks off the **Action Client** to orchestrate path-planning telemetry.
*   **`my_gripper_srv_node`**: Operates as a Service Server controlling vacuum suction keps and responds instantly to activation requests.
*   **`my_action_server_node`**: Functions as an Action Server, executing the sequential kinematic progression (`Picking` ➔ `Moving to pallet` ➔ `Placing` ➔ `Returning`) and feeding back active step milestones.

### 🔄 Sequential Automation Loop Workflow

```text
       [ my_pub_node ]
              │
              │  (Topic: /box_chatter)
              ▼  Publishes: Box #ID [Status: In Queue]
       [ my_sub_node ] (Central Controller)
              │
              ├─► [Step 1: SERVICE CALL] ──► [ gripper_service_node ] (Suction ON)
              │   ▲ Wait for Response: "Box secured" ◄────┘
              │
              ├─► [Step 2: ACTION GOAL] ───► [ palletize_action_server ] (Robot Motion)
              │   ▲ Track Progress Feedback (10% ➔ 90%) ◄─┘
              │   │
              │   ▼ (On Goal Achieved: 100% Progress)
              │
              └─► [Step 3: SERVICE CALL] ──► [ gripper_service_node ] (Suction OFF)
                  ▲ Wait for Response: "Box released" ◄───┘
                  │
                  ▼ (System State Reset: robot_busy = False)
         [ READY FOR NEXT CYCLE ]
```

![Sequential Automation Loop](ros2-sequential-automation-loop.png)


6. ROS 2 Communication Graph

The system communication pipeline verified and visualised using **`rqt_graph`**:

![ROS 2 Network Graph](rosgraph.png)

7. Automated Orchestrated Launch Control

Utilized a centralized `my_nodes_launch.py` script to orchestrate and safely map the lifecycles of all 4 nodes simultaneously within a single terminal environment:

    ros2 launch my_first_ros2_package my_nodes_launch.py

Useful Commands
Source ROS 2

    source /opt/ros/lyrical/setup.bash

Build workspace

    cd ~/ros2_ws
    colcon build --symlink-install

Source workspace

    source install/setup.bash

Start the complete autonomous assembly line

    ros2 launch my_first_ros2_package my_nodes_launch.py

Inspect custom interfaces

    ros2 interface show my_robot_interfaces/msg/BoxInfo
    ros2 interface show my_robot_interfaces/srv/SetGripperStatus
    ros2 interface show my_robot_interfaces/action/PalletizeBox

Trigger action manually from CLI

    ros2 action send_goal /palletize_box my_robot_interfaces/action/PalletizeBox "{box_id: 42}" --feedback

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
        Actions (.action)  [COMPLETED]
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
    ☑ Implement ROS 2 Actions (Closed-loop trajectory feedback pipeline)
    ☑ Implement ROS 2 Parameters (Dynamic tuning of velocity bounds & weights)
    ☑ Launch file improvements (Automated central config mapping via share directory)
    ☑ Build and run ROS 2 package
    ☑ Push project to GitHub

Next
    ☐ TF2
    ☐ URDF
    ☐ Gazebo
    ☐ ros2_control
    ☐ MoveIt 2
    ☐ Computer vision
    ☐ Palletizing robot simulation

Learning by building — Python → ROS 2 → Robotics.