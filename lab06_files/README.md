# Lab 06: Pick & Place with Kinova Gen3 Lite

Starter code for programming a robotic arm to pick up and place objects using MoveIt2.

## Files

| File | Description |
|------|-------------|
| `pick_and_place.py` | Student-facing starter script for one-block and stack-three tasks |
| `gripper_runtime.py` | Instructor/runtime helper for robust gripper command execution |
| `spawn_blocks.sh` | Gazebo helper script to spawn table and colored blocks |

## Quick Start

1. **Launch the Kinova simulation** (in one terminal):
   ```bash
   ros2 launch kortex_bringup kortex_sim_control.launch.py start_rviz:=true
   ```

2. **Spawn the scene objects** (in another terminal):
   ```bash
   ./spawn_blocks.sh
   ```

3. **Add collision objects to MoveIt planning scene**:
   ```bash
   ros2 run lab06_moveit pick_and_place --ros-args -p task:=add_scene
   ```

4. **Run the one-block starter task**:
   ```bash
   ros2 run lab06_moveit pick_and_place --ros-args -p task:=pick_place_one
   ```

5. **Run the stack-three task**:
   ```bash
   ros2 run lab06_moveit pick_and_place --ros-args -p task:=stack_three
   ```

## Available Tasks

Pass these via `--ros-args -p task:=<name>`:

- `home` - Move to home joint configuration
- `retract` - Move to retracted position
- `add_scene` - Add table and blocks to the planning scene
- `pick_place_one` - Execute the basic one-block pick and place sequence
- `stack_three` - Stack all three blocks (edit stack x/y in script)

## Related Guides

- [pymoveit2 API Guide](../guides/pymoveit2_api_guide.md) - Core MoveIt2 Python reference
- [Kinova Gen3 Lite Guide](../guides/kinova_gen3_lite_moveit2_guide.md) - Robot-specific setup and configuration
- [Quick Reference](../guides/quick_reference.md) - Linux, Docker, ROS 2 basics

## Suggested 2.5 Hour Lab Flow

- 0-45 min: Run `pick_place_one`, verify scene and baseline motion.
- 45-105 min: Run `stack_three` and tune stack x/y for stability.
- 105-135 min: Tune approach/grasp heights and improve repeatability.
- 135-150 min: TA sign-off and short demo.
