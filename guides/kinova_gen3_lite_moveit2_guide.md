# Kinova Gen3 Lite + MoveIt 2 guide

Use this page for the parts of the course that involve the Kinova Gen3 Lite, MoveIt 2, RViz, controllers, and planning-scene debugging.

This guide is intentionally shorter than the full hardware manual. If you need the OEM-level reference, use the [Kinova Gen3 Lite user guide PDF](https://static.generation-robots.com/media/Kinova-lite-fiche-technique.pdf). The file is mirrored by Generation Robots, but the document itself is the Kinova user guide.

## What students usually need from the manual

- The arm is a 6-DOF robot that weighs 5.4 kg, reaches 760 mm, and is rated for continuous payloads of 600 g mid-range or 500 g at full reach. In practice: course blocks and light fixtures are fine, but do not improvise heavier tools or off-center loads.
- After power-on, the boot sequence should finish within about 30 seconds. Blue LED means the robot is still booting. Green LED means it is ready.
- If power is cut, the arm can fall under its own weight. Keep the workspace clear and only power up, reboot, or shut down when the robot is in a stable pose.
- The robot has two especially useful built-in poses: `home` is the ready pose, and `retract` folds the arm into a compact resting pose. On the default Xbox mapping, hold `B` for home and `A` for retract.
- The simplest direct computer connection is USB over RNDIS. The Web App defaults to `192.168.1.10` for point-to-point USB and `192.168.2.10` for the optional Ethernet adapter path. Default first-login credentials are `admin` / `admin`.
- High-level control is the right starting point for this course. It is the boot default and includes joint limits, Cartesian limits, singularity avoidance, and protection zones. Low-level 1 kHz control is for advanced hardware work and is not where students should begin.
- Wi-Fi is useful for the Web App and monitoring, but the manual does not recommend Wi-Fi for 1 kHz low-level control because of latency.

## Before you touch the physical arm

- Treat the arm and gripper as pinch hazards. Keep fingers away from joints, linkages, and the gripper when the robot is powered.
- Do not try to stop the robot by hand while it is moving.
- Do not backdrive the joints by hand while the robot is powered on. The manual only allows slow manual repositioning when the robot is powered off.
- Do not exceed the rated payload, especially near full reach.
- Mount the robot securely and make sure no person or object is in the path before powering it on.
- After powering down, wait at least five seconds before powering the arm back on.

## Practical hardware checklist

1. Confirm the robot is securely mounted and the workspace is clear.
2. Connect power, flip the switch, and wait for the LED to change from blue to green.
3. If you need manual control, use the Xbox controller, the Kortex Web App, or a high-level API path first.
4. For a direct laptop-to-robot connection, start with USB RNDIS before trying Wi-Fi.
5. Put the arm in `retract` when it will sit idle for a while.

## What most students can skip

- Detailed mounting-hole drawings and accessory hardware dimensions.
- Actuator-level IP tables and 1 kHz `BaseCyclic` control details.
- Most of the Web App administration and firmware-management pages.
- Deep API reference material unless you are doing a custom hardware integration.

## If you need the full manual, start with these sections

- Safety and handling: pages 6-8
- Power-up and operating modes: pages 35-38
- Home/retract, computer connection, and Web App access: pages 43-51
- Specs, workspace, and payload: pages 54-60

## Launch the Kinova simulation with RViz

```bash
ros2 launch kortex_bringup kortex_sim_control.launch.py start_rviz:=true
```

For most labs in this repo, start in simulation first. Move to the physical arm only when the lab or instructor explicitly asks you to.

## Make trajectories easier to see in RViz

- In **MotionPlanning**, enable **Show Trail** for the planned path.
- Consider enabling **Loop Animation** when demoing a trajectory.
- Increase trajectory line width and lower robot alpha so the arm is easier to read.
- Set the RViz fixed frame to your planning frame, usually `world` or `base_link`.

## Quick check that MoveIt is alive

```bash
ros2 node list | grep move_group
ros2 topic info /display_planned_path
```

## Discover the names you must use

**URDF**

```bash
ros2 param get /robot_state_publisher robot_description > urdf.xml
```

**SRDF**

```bash
ros2 param get /move_group robot_description_semantic > srdf.xml
```

Use those files to confirm:

- Joint order for joint arrays
- Planning groups such as `arm` and `gripper`
- Named states
- End-effector link names

**Live state**

```bash
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states
```

**TF frames**

```bash
ros2 run tf2_ros tf2_echo base_link end_effector_link
```

If available:

```bash
ros2 run tf2_tools view_frames
```

## ros2_control checks

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

You should see an active arm trajectory controller and an active gripper controller. If planning succeeds but execution never starts, the controller name or state is often the problem.

## Gripper action checks

```bash
ros2 action list | grep -i gripper
ros2 action info /PATH/TO/gripper_cmd
ros2 interface show control_msgs/action/GripperCommand
```

Use the discovered action name in your `GripperInterface` setup.

## Planning scene and Cartesian sanity checks

**Planning scene**

```bash
ros2 topic info /monitored_planning_scene
ros2 topic echo /monitored_planning_scene --once
```

**Cartesian fraction**

- `fraction` in `[0, 1]` is the portion of requested waypoints that were IK-feasible and collision-free.
- If the value is low, reduce waypoint spacing, keep orientation fixed, avoid singular stretches, and confirm obstacles are not inside your intended path.

## Colcon overlays and cleanup

**Rebuild and re-source**

```bash
colcon build --symlink-install
source install/setup.bash
```

**Last-resort cleanup**

```bash
rm -rf build/ install/ log/
colcon build --symlink-install
source install/setup.bash
```

## Handy copy block

```bash
# Models
ros2 param get /robot_state_publisher robot_description > urdf.xml
ros2 param get /move_group robot_description_semantic > srdf.xml

# Live state
ros2 topic echo /joint_states --once
ros2 run tf2_ros tf2_echo base_link end_effector_link

# MoveIt signals
ros2 topic info /display_planned_path
ros2 topic info /monitored_planning_scene

# Controllers
ros2 control list_controllers
ros2 control list_hardware_interfaces

# Gripper action
ros2 action list | grep -i gripper
ros2 action info /PATH/TO/gripper_cmd
ros2 interface show control_msgs/action/GripperCommand
```

## Related docs

- [Quick reference](quick_reference.md)
- [pymoveit2 API guide](pymoveit2_api_guide.md)
- [Lab 06 README](../lab06_files/README.md)
