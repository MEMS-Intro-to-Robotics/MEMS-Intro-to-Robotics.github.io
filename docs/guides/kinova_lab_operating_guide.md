# Kinova Gen3 Lite — Lab Operating Guide

This guide walks lab staff through the complete procedure for allowing students to run code on the Kinova Gen3 Lite robotic arm. The process involves simulation verification, hardware setup, Docker container launch, and supervised code execution.

!!! danger "Safety First"
    The robot arm can cause injury if operated incorrectly. Always ensure the E-stop is accessible and within arm's reach. Never place hands or body parts in the robot's workspace during operation. Stop immediately if anything appears wrong.

## Equipment Checklist

- [ ] Kinova Gen3 Lite arm (powered on)
- [ ] USB cable connecting robot to lab computer
- [ ] E-stop device plugged into wall power and connected to robot
- [ ] Lab computer with Docker installed and Kinova image built
- [ ] Network configured so lab computer can reach `192.168.1.10`

---

## Step 1: Verify Student Simulation

!!! info "Important"
    Students **must** show a live simulation on their computer. Do **not** accept video recordings — robotic programs are non-deterministic, so only a live run demonstrates the code currently works.

Before touching any hardware, have the student demonstrate their code in simulation:

1. Ask the student to run their simulation on their own computer
2. Watch the entire execution from start to finish
3. Verify the motion paths look reasonable and stay within workspace bounds
4. If anything looks concerning, ask the student to explain or modify before proceeding

---

## Step 2: Connect to Kinova Web Interface

The Kinova arm has a built-in web interface for direct control and diagnostics.

1. Ensure the robot arm is powered on and the USB is connected to the lab computer
2. Verify the E-stop is connected (plugged into wall and robot)
3. Open a web browser on the lab computer
4. Navigate to `http://192.168.1.10/`
5. Log in when prompted (username and password are both `admin`)

### Using the Web Interface

- You can manually move the robot to a safe starting position if needed, such as when MoveIt reports a joint state out of bounds
- Check the robot's current status — look for any warnings or errors
- **Note:** Once ROS 2 connects, the robot enters low-level servoing mode and the web interface cannot be used for movement

### Connection Status Indicators

| Status | Action |
|--------|--------|
| :green_circle: **Green** | Normal operation — proceed with setup |
| :yellow_circle: **Yellow** | Warning present — click to view details, may need to acknowledge before proceeding |
| :red_circle: **Red** | Error state — click the red button in top right corner to reset the connection |

---

## Step 3: Launch Docker Container

Open a terminal on the lab computer and run:

```bash
docker run -it --rm \
  --net=host \
  --privileged \
  --device=/dev/ttyACM0 \
  --gpus all \
  -e NVIDIA_DRIVER_CAPABILITIES=graphics,compute,utility \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -e QT_QPA_PLATFORM=xcb \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v ~/workspaces:/root/workspaces/ \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest
```

**Key flags:**

| Flag | Purpose |
|------|---------|
| `--privileged` | Required for USB device access |
| `--network host` | Allows container to reach robot at `192.168.1.10` |
| `-v ~/workspaces:...` | Mount student code into the container |

---

## Step 4: Launch Robot Drivers and MoveIt

You need two terminal windows inside the container. The Docker container will open with Terminator, which supports split panes.

### Terminal 1: Launch the Kortex Driver

```bash
kinova-driver
```

This is an alias that expands to:

```bash
ros2 launch kortex_bringup gen3_lite.launch.py \
  robot_ip:=$ROBOT_IP gripper:=$GRIPPER launch_rviz:=false
```

Wait until you see messages indicating the driver has connected to the robot. You should see joint states being published.

### Terminal 2: Launch MoveIt / RViz

```bash
kinova-moveit
```

This is an alias that expands to:

```bash
ros2 launch kinova_gen3_lite_moveit_config robot.launch.py \
  robot_ip:=$ROBOT_IP launch_driver:=false
```

RViz should open showing the robot model. Verify the displayed robot pose matches the physical robot's actual position.

---

## Step 5: Run Student Code

!!! warning "Dry Run First"
    If the student's code interacts with objects (grasping, placing, etc.), **always** perform a dry run first without those objects present. This verifies the motion paths are correct before introducing potential collision hazards.

### Running the Code

1. Open a third terminal in the container (split pane or new tab)
2. Navigate to the student's code: `cd /root/workspaces/student_code`
3. If the code needs building: `colcon build --symlink-install`
4. Source the workspace: `source install/setup.bash`
5. Run the student's launch file or node

### During Execution

- Keep your hand near the E-stop at all times
- Watch both the physical robot and RViz visualization
- If anything looks wrong, hit the E-stop immediately
- After a successful dry run, add objects and run again

---

## Troubleshooting

### Cannot connect to robot at 192.168.1.10

- Verify the USB cable is connected
- Check the lab computer's network configuration
- Try: `ping 192.168.1.10`

### Web interface shows error (red button)

- Click the red button in the top right corner to reset
- If the error persists, power cycle the robot
- Check E-stop is not engaged (pull/twist to release if so)

### Driver fails to connect

- Close the web interface before launching the driver
- Kill any existing ROS nodes: `pkill -9 ros`
- Restart the Docker container

### RViz pose doesn't match physical robot

- The driver may not have initialized properly
- Restart both the driver and MoveIt
- Check for error messages in the driver terminal

---

## Quick Reference: Docker Aliases

These aliases are preconfigured in the Docker container:

| Alias | Purpose |
|-------|---------|
| `kinova-driver` | Launch Kortex driver for real hardware |
| `kinova-moveit` | Launch MoveIt and RViz for real hardware |
| `kinova-fake-driver` | Driver with fake/mock hardware (testing) |
| `kinova-fake-moveit` | MoveIt with fake hardware (testing) |
| `kinova-sim-gz` | Launch Gazebo simulation |
| `kinova-sim-moveit` | MoveIt for Gazebo simulation |
| `gzkill` | Kill zombie Gazebo processes |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ROBOT_IP` | `192.168.1.10` | Robot's IP address |
| `ROBOT` | `gen3_lite` | Robot model identifier |
| `GRIPPER` | `gen3_lite_2f` | Gripper type |
