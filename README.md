# ceto_description

The **ceto_description** package provides the SAUVC simulation environment and robot description for the BlueROV2 platform, integrated with **ROS 2 Humble** and **Ign Gazebo Fortress** (Ignition).

This package contains:
* URDF/Xacro descriptions for the BlueROV2 robot.
* Launch files to start the Gazebo simulation, spawn the robot, and bridge ROS-Gazebo communications.
* Teleoperation scripts for keyboard control.
* World files for the SAUVC competition environment.

## Prerequisites

Ensure you have the following installed:
* **ROS 2 Humble**
* **Ign Gazebo Fortress (v6.17)**
* **ROS-Gazebo Bridge** (`ros-humble-ros-gz-bridge`, `ros-humble-ros-gz-sim`, `ros-humble-ros-gz-image`)

## Build Instructions

1.  Create a colcon workspace (if you haven't already):
    ```bash
    mkdir -p ~/ceto_ws/src
    cd ~/ceto_ws/src
    ```

2.  Clone/Place this package into `src`.

3.  Install dependencies:
    ```bash
    cd ~/ceto_ws
    rosdep install --from-paths src -y --ignore-src
    ```

4.  Build the package:
    ```bash
    colcon build --symlink-install --packages-select ceto_description
    ```

5.  Source the setup script:
    ```bash
    source install/setup.bash
    ```

## Usage

### 1. Launching the Simulation

To launch the SAUVC world, spawn the BlueROV2 robot, and start the ROS-Gazebo bridge:

```
ros2 run sauvc_sim teleop.py
```
