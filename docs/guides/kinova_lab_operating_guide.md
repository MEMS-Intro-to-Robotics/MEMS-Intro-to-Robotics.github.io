# Kinova Gen3 Lite Lab Operating Guide

This guide covers simulation checks, hardware setup, and code execution on the Kinova Gen3 Lite robotic arm. It is for lab staff supervising hardware sessions and students cleared for independent use.

!!! danger "Safety First"
    The robot arm can cause injury if operated incorrectly. Always ensure the E-stop is accessible and within arm's reach. Never place hands or body parts in the robot's workspace during operation. Stop immediately if anything appears wrong.

## Equipment Checklist

- [ ] Kinova Gen3 Lite arm (powered on)
- [ ] USB cable connecting robot to lab computer
- [ ] E-stop device plugged into wall power and connected to robot
- [ ] Lab computer with Docker installed and the course Kinova image pulled (`docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest`)
- [ ] Network configured so lab computer can reach `192.168.1.10`

---

## Step 1: Verify Simulation

!!! info "Important"
    All code **must** be demonstrated in a live simulation before running on hardware. Video recordings are not accepted.

Before using the arm, check the code in simulation:

1. Run the simulation on your own computer (or have lab staff watch you run it)
2. Watch the entire execution from start to finish
3. Verify the motion paths look reasonable and stay within workspace bounds
4. If anything looks concerning, debug and fix before proceeding to hardware

---

## Step 2: Connect to Kinova Web Interface

Use the Kinova arm's built-in web interface for control and diagnostics.

1. Ensure the robot arm is powered on and the USB is connected to the lab computer
2. Verify the E-stop is connected (plugged into wall and robot)
3. Open a web browser on the lab computer
4. Navigate to `http://192.168.1.10/`
5. Log in when prompted (username and password are both `admin`)

### Using the Web Interface

- If MoveIt reports a joint state out of bounds, use the web interface to move the robot to a safe starting position
- Check the robot's current status for warnings or errors
- **Note:** Once ROS 2 connects, the robot enters low-level servoing mode and the web interface cannot be used for movement

### Connection Status Indicators

| Status | Action |
|--------|--------|
| :green_circle: **Green** | Normal operation. Proceed with setup |
| :yellow_circle: **Yellow** | Warning present. Click to view details; you may need to acknowledge it before proceeding |
| :red_circle: **Red** | Error state. Click the red button in top right corner to reset the connection |

---

## Step 3: Launch Docker Container

On the lab computer, open a terminal and run the course command:

```bash
xhost +local:docker
docker run --rm -it \
  --name kinova \
  --net=host \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest
```

**Key flags:**

| Flag | Purpose |
|------|---------|
| `--net=host` | Uses the host network so the container can reach the robot at `192.168.1.10` |
| `--gpus all` | Makes GPUs available to the container for RViz. If `docker run` reports `could not select device driver`, rerun the command without this flag. |
| `-e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` | Limits ROS 2 discovery to this computer |
| `-v ~/workspaces:/root/workspaces` | Mounts the lab computer's `~/workspaces` directory at `/root/workspaces` in the container |

---

## Step 4: Launch the Driver, MoveIt, and RViz

First, use the web interface (Step 2) to move the arm to its **Home** position. MoveIt will not plan from a start pose outside its joint limits, and the arm's built-in **Retract** pose puts joint 3 slightly past MoveIt's limit (2.62 to 2.63 rad against a 2.61 rad limit).

Then, in one terminal inside the container, run:

```bash
kinova-moveit
```

This alias runs:

```bash
ros2 launch kinova_gen3_lite_moveit_config robot.launch.py robot_ip:=$ROBOT_IP
```

This single launch starts the Kortex driver, the controllers, MoveIt, and RViz. Do not also run `kinova-driver`. It starts a second driver and controller manager, and the controllers fail.

RViz should open showing the robot model. Verify the displayed robot pose matches the physical robot's actual position.

---

## Step 5: Run Your Code

!!! warning "Dry Run First"
    If your code interacts with objects (grasping, placing, etc.), **always** perform a dry run first without those objects present. Watch the motion paths before placing objects in the workspace.

### Running the Code

1. Open a second terminal in the container (split pane or new tab)
2. Navigate to your code: `cd /root/workspaces/student_code`
3. If the code needs building: `colcon build --symlink-install`
4. Source the workspace: `source install/setup.bash`
5. Run your launch file or node

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

### Controllers fail to load or activate

- Check that only one launch is running. Stop any `kinova-driver` or `kortex_bringup` launch, stop `kinova-moveit`, and start `kinova-moveit` again by itself
- `ros2 node list | grep controller_manager` should list exactly one controller manager

### Every plan fails, or MoveIt reports the start state is out of bounds

- The arm is probably in its built-in Retract pose, which is outside MoveIt's joint limits
- Stop the launch, move the arm to **Home** in the web interface, and start `kinova-moveit` again

### RViz pose doesn't match physical robot

- The driver may not have initialized properly
- Stop the launch and start `kinova-moveit` again
- Check for error messages in the launch terminal

---

## Quick Reference: Docker Aliases

These aliases are preconfigured in the Docker container:

| Alias | Purpose |
|-------|---------|
| `kinova-moveit` | Driver, controllers, MoveIt, and RViz for the real arm, in one launch |
| `kinova-driver` | Driver and controllers only, without MoveIt. Never run it together with `kinova-moveit` |
| `kinova-fake-moveit` | Same as `kinova-moveit`, with fake hardware (testing without the arm) |
| `kinova-fake` | Driver with fake hardware, without MoveIt. Never run it together with `kinova-fake-moveit` |
| `kinova-sim` | Launch Gazebo simulation |
| `kinova-sim-moveit` | MoveIt for Gazebo simulation |
| `gzkill` | Kill zombie Gazebo processes |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ROBOT_IP` | `192.168.1.10` | Robot's IP address |
| `ROBOT` | `gen3_lite` | Robot model identifier |
| `GRIPPER` | `gen3_lite_2f` | Gripper type |
