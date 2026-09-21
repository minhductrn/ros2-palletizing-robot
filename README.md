# ROS 2 Palletizing Robot Learning Project

**Author:** Minh Duc Tran  
**Role:** Robot Operator @ Tutor Intelligence  
**Repository:** `ros2-palletizing-robot`

This is a hands-on robotics learning project built with **ROS 2, Python, Gazebo, and ros2_control**.

The goal is to gradually build a realistic industrial palletizing system while learning the complete ROS 2 robotics workflow:

```text
Box Detection
      ↓
Supervisor
      ↓
FIFO Queue
      ↓
ROS 2 Action
      ↓
Robot Motion
      ↓
Gripper
      ↓
Gazebo Simulation
```

---

# 1. Development Environment

- **Host OS:** Windows 11
- **Linux Environment:** WSL2
- **Ubuntu:** 26.04.1 LTS (Resolute)
- **ROS 2:** Lyrical Luth
- **Programming Language:** Python 3
- **IDE:** Visual Studio Code
- **Build System:** Colcon
- **Version Control:** Git + GitHub
- **Simulation:** Gazebo Sim 10
- **Robot Control:** ros2_control + gz_ros2_control

Workspace:

```bash
~/ros2_ws
```

ROS environment:

```bash
source /opt/ros/lyrical/setup.bash
source ~/ros2_ws/install/setup.bash
```

---

# 2. Project Architecture

Current system architecture:

```text
Publisher / Simulated Box Sensor
              |
              | BoxInfo
              v
Subscriber / Palletizing Supervisor
              |
              | FIFO Queue
              v
      PalletizeBox Action
              |
              v
     Palletize Action Server
        |               |
        |               +----> Gripper Service
        |
        +----> FollowJointTrajectory
                      |
                      v
               arm_controller
                      |
                      v
                ros2_control
                      |
                      v
               gz_ros2_control
                      |
                      v
                 Gazebo Robot
                      |
                      v
          joint_state_broadcaster
                      |
                      v
               /joint_states
                      |
                      v
          robot_state_publisher
```

The current palletizing sequence is:

```text
Move to PICK
      ↓
Gripper ON
      ↓
Move to PALLET
      ↓
Move to PLACE
      ↓
Gripper OFF
      ↓
Return HOME
```

---

# 3. ROS 2 Packages

The workspace currently contains two main packages.

## 3.1 `my_first_ros2_package`

Main Python robotics package.

Important nodes:

```text
hello_node
publisher_node
subscriber_node
gripper_service_node
palletize_action_server
```

Important directories:

```text
my_first_ros2_package/
├── config/
├── launch/
├── my_first_ros2_package/
├── urdf/
├── package.xml
├── setup.cfg
└── setup.py
```

---

## 3.2 `my_robot_interfaces`

Custom ROS 2 interfaces package.

It currently contains:

```text
msg/
srv/
action/
```

---

# 4. Custom ROS 2 Interfaces

## 4.1 `BoxInfo.msg`

```text
int32 box_id
float64 x
float64 y
float64 z
float64 weight
string status
```

This message represents information about a detected box.

---

## 4.2 `SetGripperStatus.srv`

```text
bool activate
---
bool success
string message
```

The service is used to activate or deactivate the simulated suction gripper.

---

## 4.3 `PalletizeBox.action`

```text
int32 box_id
---
bool success
string message
---
float32 progress
string current_step
```

The palletizing action sends a box ID to the robot and provides progress feedback during the palletizing cycle.

---

# 5. Publisher Node

The publisher acts as a simulated box sensor.

It currently publishes logical `BoxInfo` messages approximately every four seconds.

Topic:

```text
/box_chatter
```

Each generated box contains:

```text
box_id
x
y
z
weight
status
```

Example logical workflow:

```text
New box generated
      ↓
BoxInfo published
      ↓
Supervisor receives box
```

The publisher currently generates **logical ROS 2 boxes only**.

Physical Gazebo boxes are not yet spawned by this node.

---

# 6. Subscriber / Palletizing Supervisor

The subscriber acts as the high-level palletizing supervisor.

Its responsibilities are:

```text
Receive BoxInfo
      ↓
Validate operating mode
      ↓
Validate box weight
      ↓
Add valid box to FIFO queue
      ↓
Check robot availability
      ↓
Send PalletizeBox action
      ↓
Wait for action completion
      ↓
Process next queued box
```

The supervisor uses a FIFO queue:

```text
First In
   ↓
First Out
```

This allows new boxes to continue arriving while the robot is processing another box.

Example:

```text
Box 201 → processing
Box 202 → waiting
Box 203 → waiting

Box 201 complete
      ↓
Box 202 starts
      ↓
Box 203 remains queued
```

This prevents boxes from being discarded simply because the robot is busy.

---

# 7. Palletize Action Server

The palletize action server owns the complete robot motion and gripper sequence.

Current sequence:

```text
PICK
  ↓
GRIPPER ON
  ↓
PALLET
  ↓
PLACE
  ↓
GRIPPER OFF
  ↓
HOME
```

Current fixed robot target positions:

## PICK

```text
base_to_torso = 0.00
torso_to_arm  = -1.20
```

## PALLET

```text
base_to_torso = 1.57
torso_to_arm  = 0.20
```

## PLACE

```text
base_to_torso = 1.57
torso_to_arm  = -0.90
```

## HOME

```text
base_to_torso = 0.00
torso_to_arm  = 0.00
```

Current trajectory duration:

```text
4 seconds
```

The action server waits for every trajectory to complete successfully before starting the next stage.

---

# 8. Gripper Service

The current gripper is controlled through:

```text
SetGripperStatus
```

Current behavior:

```text
Gripper ON
      ↓
Logical suction enabled

Gripper OFF
      ↓
Logical suction disabled
```

The gripper service is currently a **logical simulation only**.

It does not yet physically attach or detach Gazebo box models.

Physical box attachment is part of the next development stage.

---

# 9. Robot URDF

The robot currently contains the following main links and joints:

```text
world
  |
  +-- base_link
       |
       +-- base_to_torso
            |
            +-- torso_link
                 |
                 +-- torso_to_arm
                      |
                      +-- arm_link
                           |
                           +-- arm_to_gripper
                                |
                                +-- gripper_link

base_link
  |
  +-- base_to_conveyor
       |
       +-- conveyor_link
```

Controlled joints:

```text
base_to_torso
torso_to_arm
```

---

# 10. ros2_control

The robot uses `gz_ros2_control` with position command interfaces.

Command interfaces:

```text
base_to_torso/position
torso_to_arm/position
```

State interfaces:

```text
base_to_torso/position
base_to_torso/velocity

torso_to_arm/position
torso_to_arm/velocity
```

Controller:

```text
joint_trajectory_controller/JointTrajectoryController
```

Controller update rate:

```text
100 Hz
```

---

# 11. Stable Controller Configuration

Current Gazebo position-control gain:

```yaml
position_proportional_gain: 0.1
```

Current trajectory controller behavior:

```yaml
interpolate_from_desired_state: true
```

Current goal constraints:

```yaml
constraints:
  stopped_velocity_tolerance: 0.02
  goal_time: 5.0

  base_to_torso:
    goal: 0.02

  torso_to_arm:
    goal: 0.02
```

The `torso_to_arm` joint currently uses:

```text
effort = 50.0 N·m
velocity = 1.0 rad/s
```

The effort limit was increased from 10 N·m because the original value was insufficient for the gravity-loaded arm.

---

# 12. Controller Configuration Files

## `config/controllers.yaml`

Current configuration:

```yaml
gz_ros_control:
  ros__parameters:
    position_proportional_gain: 0.1

controller_manager:
  ros__parameters:
    update_rate: 100

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController
      params_file: /home/dtran/ros2_ws/src/my_first_ros2_package/config/arm_controller.yaml
```

---

## `config/arm_controller.yaml`

Current configuration:

```yaml
arm_controller:
  ros__parameters:
    joints:
      - base_to_torso
      - torso_to_arm

    command_interfaces:
      - position

    state_interfaces:
      - position
      - velocity

    interpolate_from_desired_state: true

    constraints:
      stopped_velocity_tolerance: 0.02
      goal_time: 5.0

      base_to_torso:
        goal: 0.02

      torso_to_arm:
        goal: 0.02
```

---

# 13. Gazebo Simulation

Gazebo is currently separated into a simulation server and an optional GUI client.

This architecture improves stability when running Gazebo through WSL2 / WSLg.

---

## 13.1 Headless Gazebo

Run:

```bash
ros2 launch my_first_ros2_package gazebo_control_launch.py
```

This starts:

```text
Gazebo simulation server
robot_state_publisher
robot spawn
/clock bridge
joint_state_broadcaster
arm_controller
```

The Gazebo GUI is not displayed.

This is the most stable mode for development and testing.

---

## 13.2 Separate Gazebo GUI

The Gazebo graphical client can be started separately:

```bash
ros2 launch my_first_ros2_package gazebo_gui_launch.py
```

Architecture:

```text
Gazebo Server
      |
      +------ Gazebo GUI Client
```

If the GUI has a WSLg display problem, the simulation server can continue running independently.

---

# 14. One-Command Full System Launch

The entire palletizing project can now be started through:

```text
full_system_launch.py
```

This starts:

```text
Gazebo server
      ↓
Robot model
      ↓
ros2_control
      ↓
Controllers
      ↓
Gripper service
      ↓
Palletize action server
      ↓
Subscriber / FIFO supervisor
      ↓
Publisher
      ↓
Optional Gazebo GUI
```

---

# 15. Manual Development Mode

Recommended for development and debugging:

```bash
ros2 launch my_first_ros2_package full_system_launch.py \
  gui:=true \
  auto_publish:=false
```

This starts the complete system but disables automatic box publishing.

A manual palletizing action can then be sent:

```bash
ros2 action send_goal \
  /palletize_box \
  my_robot_interfaces/action/PalletizeBox \
  "{box_id: 307}" \
  --feedback
```

This mode is useful for testing one robot cycle at a time.

---

# 16. Automatic FIFO Demonstration Mode

To run the automatic supervisor and FIFO system:

```bash
ros2 launch my_first_ros2_package full_system_launch.py \
  gui:=true \
  auto_publish:=true
```

The publisher automatically generates boxes.

Example:

```text
Box 0
      ↓
Robot starts processing

Box 1
      ↓
FIFO Queue

Box 2
      ↓
FIFO Queue

Box 3
      ↓
FIFO Queue
```

When the robot finishes one box, the next box is automatically taken from the queue.

Because the publisher currently generates boxes approximately every four seconds while a palletizing cycle takes much longer, the queue can grow during this demonstration.

This is currently intentional for FIFO testing.

---

# 17. Headless Full System

For maximum simulation stability:

```bash
ros2 launch my_first_ros2_package full_system_launch.py \
  gui:=false \
  auto_publish:=false
```

This is useful when the Gazebo graphical interface is not required.

---

# 18. Important Debugging Milestones

Several major issues were identified and corrected during development.

---

## 18.1 Insufficient Joint Effort

Initial joint effort:

```text
10 N·m
```

The gravity-loaded arm could not reliably follow larger commands.

The effort limit was increased to:

```text
50 N·m
```

After this change, the arm correctly tracked larger positive and negative joint positions.

---

## 18.2 Gazebo Position Tracking

Initial configuration:

```yaml
position_proportional_gain: 0.01
```

This caused significant physical tracking lag.

Current configuration:

```yaml
position_proportional_gain: 0.1
```

This significantly improved Gazebo joint tracking.

---

## 18.3 Sequential Trajectory Transition Errors

During sequential palletizing movements, `gz_ros_control` originally generated warnings such as:

```text
Command of at least one joint is out of limits
```

The issue occurred when a new trajectory began while the measured joint state was slightly behind the previous commanded state.

The controller was updated with:

```yaml
interpolate_from_desired_state: true
```

along with explicit goal and stopped-velocity tolerances.

After this change, sequential palletizing movements completed without the previous joint-limit warnings.

---

## 18.4 Gazebo GUI Stability

Running Gazebo server and GUI together under WSLg produced GUI-related crashes.

The architecture was changed to:

```text
Gazebo Server
    |
    +---- Headless simulation

Gazebo GUI
    |
    +---- Separate optional client
```

This allows the simulation to remain alive independently of the GUI.

---

## 18.5 Duplicate ROS / Gazebo Processes

When the new full-system launcher was started while older ROS and Gazebo processes were still running, errors appeared such as:

```text
Another world of the same name is running
```

and:

```text
There may be more than one action server
```

The solution is to ensure that only one copy of the palletizing system is running.

The master launch should replace manually starting each component separately.

---

# 19. Verified Palletizing Cycle

The following sequence has been successfully tested:

```text
HOME
  ↓
PICK
  ↓
Gripper ON
  ↓
PALLET
  ↓
PLACE
  ↓
Gripper OFF
  ↓
HOME
```

Verified result:

```text
success: true
Goal finished with status: SUCCEEDED
```

Recent stable tests completed without the previous `gz_ros_control` joint-limit errors.

---

# 20. Current Project Status

Completed:

```text
ROS 2 workspace
Python ROS 2 package
Custom ROS 2 interface package
Publisher / subscriber communication
Custom BoxInfo message
Custom SetGripperStatus service
Custom PalletizeBox action
ROS 2 parameters
ROS 2 launch system
URDF robot model
TF / robot_state_publisher
Gazebo simulation
gz_ros2_control integration
joint_state_broadcaster
JointTrajectoryController
Robot trajectory execution
Logical gripper service
Palletize action server
FIFO supervisor queue
Sequential palletizing automation
Controller tracking improvements
Goal tolerances
Trajectory interpolation fix
Stable headless Gazebo
Separate Gazebo GUI client
One-command full-system launch
Manual development mode
Automatic FIFO demonstration mode
```

---

# 21. Current Limitation

The current system has a working robot-control architecture, but the boxes are still logical ROS 2 data.

Current behavior:

```text
Logical BoxInfo
      ↓
Supervisor
      ↓
FIFO Queue
      ↓
Palletize Action
      ↓
Robot moves
      ↓
Logical Gripper
```

Gazebo does **not yet** show physical cases:

```text
moving along conveyor
      ↓
being picked by robot
      ↓
moving with gripper
      ↓
being released
      ↓
remaining on pallet
```

The Gazebo robot moves, but the material-handling side of the simulation has not yet been implemented.

---

# 22. Next Development Milestone

The next major goal is to build a physical material-handling simulation.

---

## Stage 1 — Physical Box and Conveyor Simulation

Next tasks:

```text
Spawn physical boxes in Gazebo
      ↓
Assign unique box IDs
      ↓
Move boxes along conveyor
      ↓
Track box position
      ↓
Detect box at pickup location
      ↓
Connect physical box with BoxInfo
```

Target:

```text
Gazebo Box
      ↓
Moving Conveyor
      ↓
Pickup Position
```

---

## Stage 2 — Physical Pick and Place

Implement:

```text
Robot reaches PICK
      ↓
Gripper ON
      ↓
Physical box attaches to gripper
      ↓
Robot transports box
      ↓
Robot reaches PLACE
      ↓
Gripper OFF
      ↓
Physical box detaches
      ↓
Box remains on pallet
```

---

## Stage 3 — Pallet Stacking

Instead of placing every box at the same position, calculate pallet slots.

Example:

```text
Layer 1

+-----+-----+-----+
| Box | Box | Box |
+-----+-----+-----+
| Box | Box | Box |
+-----+-----+-----+

Layer 2

+-----+-----+-----+
| Box | Box | Box |
+-----+-----+-----+
| Box | Box | Box |
+-----+-----+-----+
```

Future pallet logic will calculate:

```text
row
column
layer
x position
y position
z position
```

for each box.

---

# 23. Future Architecture

Target system:

```text
Physical Box Generator
          ↓
Gazebo Conveyor
          ↓
Sensor / Detection
          ↓
BoxInfo
          ↓
Supervisor
          ↓
FIFO Queue
          ↓
PalletizeBox Action
          ↓
Motion Planning
          ↓
Robot Controller
          ↓
Physical Gripper
          ↓
Pick Box
          ↓
Transport Box
          ↓
Place Box
          ↓
Pallet Pattern Generator
```

---

# 24. Future Development Areas

Planned learning and development areas include:

```text
Physical Gazebo boxes
Conveyor movement
Gazebo contact / attachment
Dynamic pick coordinates
Dynamic place coordinates
Pallet pattern generation
TF2
Sensor integration
Computer vision
MoveIt 2
Collision checking
Motion planning
ros2_control improvements
Fault handling
Recovery states
Queue backpressure
Production state machine
Robot monitoring
Observability
```

---

# 25. Build the Workspace

From the workspace:

```bash
cd ~/ros2_ws
```

Source ROS 2:

```bash
source /opt/ros/lyrical/setup.bash
```

Build:

```bash
colcon build
```

Source the workspace:

```bash
source ~/ros2_ws/install/setup.bash
```

---

# 26. Build Only the Main Package

```bash
cd ~/ros2_ws

source /opt/ros/lyrical/setup.bash

colcon build --packages-select my_first_ros2_package

source ~/ros2_ws/install/setup.bash
```

---

# 27. Recommended Daily Development Workflow

Open a WSL terminal:

```bash
cd ~/ros2_ws
source /opt/ros/lyrical/setup.bash
source ~/ros2_ws/install/setup.bash
```

For controlled development:

```bash
ros2 launch my_first_ros2_package full_system_launch.py \
  gui:=true \
  auto_publish:=false
```

For automatic FIFO testing:

```bash
ros2 launch my_first_ros2_package full_system_launch.py \
  gui:=true \
  auto_publish:=true
```

For stable headless testing:

```bash
ros2 launch my_first_ros2_package full_system_launch.py \
  gui:=false \
  auto_publish:=false
```

---

# 28. Useful ROS 2 Commands

List nodes:

```bash
ros2 node list
```

List topics:

```bash
ros2 topic list
```

List services:

```bash
ros2 service list
```

List actions:

```bash
ros2 action list
```

Check controllers:

```bash
ros2 control list_controllers
```

Expected:

```text
arm_controller          joint_trajectory_controller/JointTrajectoryController  active
joint_state_broadcaster joint_state_broadcaster/JointStateBroadcaster          active
```

Check hardware interfaces:

```bash
ros2 control list_hardware_interfaces -v
```

Expected command interfaces:

```text
base_to_torso/position
torso_to_arm/position
```

Expected state interfaces:

```text
base_to_torso/position
base_to_torso/velocity
torso_to_arm/position
torso_to_arm/velocity
```

---

# 29. Manual Palletize Action Test

Example:

```bash
ros2 action send_goal \
  /palletize_box \
  my_robot_interfaces/action/PalletizeBox \
  "{box_id: 307}" \
  --feedback
```

Expected feedback:

```text
10%  - Moving to pick
25%  - Picking
50%  - Moving to pallet
70%  - Placing
80%  - Releasing
90%  - Returning
100% - Complete
```

Expected final result:

```text
success: true
Goal finished with status: SUCCEEDED
```

---

# 30. Git Workflow

Check project status:

```bash
git status
```

Review changes:

```bash
git diff
```

Stage selected files:

```bash
git add <file>
```

Commit:

```bash
git commit -m "Describe the project update"
```

Push:

```bash
git push origin main
```

Backup and experimental files should not be committed unless intentionally required.

---

# 31. Project Learning Roadmap

The project is being developed incrementally.

```text
ROS 2 Fundamentals
      ↓
Topics
      ↓
Services
      ↓
Actions
      ↓
Parameters
      ↓
Launch Files
      ↓
Custom Interfaces
      ↓
URDF
      ↓
TF2
      ↓
Gazebo
      ↓
ros2_control
      ↓
Trajectory Control
      ↓
FIFO Automation
      ↓
Physical Box Simulation
      ↓
Physical Pick and Place
      ↓
Pallet Stacking
      ↓
MoveIt 2
      ↓
Computer Vision
      ↓
Advanced Automation
```

---

# 32. Long-Term Project Goal

The long-term goal is to evolve this project from a ROS 2 learning environment into a more realistic palletizing automation architecture:

```text
Perception
      ↓
Detection
      ↓
Supervisory Control
      ↓
Queue Management
      ↓
Motion Planning
      ↓
Robot Control
      ↓
Physical Pick and Place
      ↓
Pallet Pattern Generation
      ↓
Monitoring
      ↓
Fault Detection
      ↓
Recovery
```

Each stage is implemented and tested before moving to the next layer.

The next development milestone is:

> **Physical boxes moving on the Gazebo conveyor, followed by physical gripper attachment and pallet stacking.**