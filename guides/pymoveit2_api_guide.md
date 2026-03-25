# `pymoveit2` API guide

Use this page when you are writing or debugging Python code that talks to MoveIt 2 through `pymoveit2`.

Values shown as `...` or `UPPER_SNAKE_CASE` must be replaced with names from your robot model. Distances are in meters, angles are in radians, and quaternions use `(x, y, z, w)`.

## Node + executor pattern

Keep callbacks responsive while your task code runs sequentially.

```python
class YourNode(rclpy.node.Node):
    def __init__(self):
        super().__init__("YOUR_NODE_NAME")
        # self.moveit2 = ...
        # self.gripper = ...

def main():
    rclpy.init()
    node = YourNode()
    executor = rclpy.executors.MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    threading.Thread(target=executor.spin, daemon=True).start()

    # node.run_task()

    rclpy.shutdown()
```

Why this pattern helps:

- Actions, TF, and planning-scene updates keep moving in the background.
- Your milestone code can still run in a simple sequential order.
- `rclpy.spin(node)` on the main thread will block the rest of your task logic.

## Arm interface

```python
from pymoveit2 import MoveIt2

self.moveit2 = MoveIt2(
    node=self,
    joint_names=["JOINT_1", "JOINT_2", "JOINT_3", "JOINT_4", "JOINT_5", "JOINT_6"],
    base_link_name="BASE_LINK",
    end_effector_name="EE_LINK",
    group_name="ARM_GROUP",
)

self.moveit2.max_velocity = 0.5
self.moveit2.max_acceleration = 0.5
# self.moveit2.planner_id = "RRTConnectkConfigDefault"
```

What each field means:

- `joint_names`: ordered list in SRDF joint order
- `base_link_name`: planning frame
- `end_effector_name`: EE link used for pose queries and IK
- `group_name`: MoveIt planning group

Common mistakes:

- Wrong joint order causes nonsense planning or motion.
- Frame and group names must exactly match the model.
- Velocity and acceleration settings are scales from `0.0` to `1.0`.

## Joint-space planning

```python
self.moveit2.move_to_configuration("home")
self.moveit2.wait_until_executed()

retract = [J1, J2, J3, J4, J5, J6]
self.moveit2.move_to_configuration(retract)
self.moveit2.wait_until_executed()
```

Check these first:

- Named targets must exist in the SRDF.
- Explicit joint lists must match the joint count and order.
- Values must stay inside joint limits.

## Cartesian waypoints

```python
from copy import deepcopy

start = self.moveit2.get_current_pose()
waypoints = [deepcopy(start)]

p1 = deepcopy(start)
p1.position.x += 0.10
waypoints.append(p1)

p2 = deepcopy(p1)
p2.position.z += 0.05
waypoints.append(p2)

plan, fraction = self.moveit2.plan_cartesian_path(waypoints=waypoints)
if fraction > 0.90:
    self.moveit2.execute(plan)
    self.moveit2.wait_until_executed()
```

What `fraction` means:

- `1.0` means the whole path was feasible.
- Lower values usually mean the waypoints are too far apart, the orientation is hard to maintain, the path intersects obstacles, or the arm is near a singularity or limit.

Helpful habits:

- Keep orientation fixed first.
- Use small waypoint steps.
- Recheck the planning scene when a path should be simple but still fails.

## Planning scene objects

```python
obj_id = "UNIQUE_ID"
self.moveit2.add_collision_box(
    id=obj_id,
    position=(X, Y, Z),
    quat_xyzw=(qx, qy, qz, qw),
    size=(sx, sy, sz),
    frame_id="FRAME",
)
time.sleep(1.0)
# self.moveit2.remove_collision_object(obj_id)
```

Remember:

- `position` is the box center.
- `size` is the full box dimensions.
- `frame_id` must match the frame you are expressing the pose in.
- Give the planning scene a short moment to propagate before planning.

## Orientation constraints

```python
self.moveit2.set_path_orientation_constraint(
    quat_xyzw=(qx, qy, qz, qw),
    tolerance=(roll_tol, pitch_tol, yaw_tol),
    parameterization=1,
)
```

Tips:

- Start with loose tolerances.
- Tight constraints reduce planning success rates.
- Clear or relax the constraint after the move if you do not want it to affect later plans.

## Gripper interface

```python
from pymoveit2.gripper_interface import GripperInterface

self.gripper = GripperInterface(
    node=self,
    gripper_joint_names=[PRIMARY_ACTUATED_JOINT],
    open_gripper_joint_positions=[OPEN_TARGET],
    closed_gripper_joint_positions=[CLOSE_TARGET],
    gripper_group_name="GRIPPER_GROUP",
    gripper_command_action_name="/PATH/TO/gripper_cmd",
)

self.gripper.open()
self.gripper.wait_until_executed()
self.gripper.close()
self.gripper.wait_until_executed()
```

Supply:

- The primary actuated joint
- Valid open and closed target values
- The correct gripper group
- The correct action server name

If nothing happens:

- Confirm the action exists with `ros2 action info`
- Confirm the gripper controller is active with `ros2 control list_controllers`

## Minimal API signatures

### Joint goals

`move_to_configuration(target: str | list[float]) -> None`

- A string target is a named state from the SRDF.
- A list target is a full joint vector in SRDF order.
- The call plans and starts execution, then returns immediately.

`wait_until_executed() -> None`

- Blocks until the most recent arm or gripper action finishes.

### Cartesian

`get_current_pose() -> geometry_msgs.msg.Pose`

- Returns the end-effector pose in the planning frame.

`plan_cartesian_path(waypoints: list[Pose]) -> (plan, fraction: float)`

- Takes waypoints in the planning frame.
- Returns a plan plus the feasible fraction.
- Does not execute automatically.

`execute(plan) -> None`

- Sends a previously computed plan to the controller.

### Scene

`add_collision_box(id, position, quat_xyzw, size, frame_id) -> None`

- Adds or updates a collision box in the planning scene.

`remove_collision_object(id: str) -> None`

- Removes the named collision object.

### Constraints

`set_path_orientation_constraint(quat_xyzw, tolerance, parameterization) -> None`

- Applies an orientation constraint to subsequent plans.

### Gripper

`open() -> None` and `close() -> None`

- Send the configured gripper action goal.

`wait_until_executed() -> None`

- Blocks until that gripper action finishes.

## Fast checks

- Nothing executes: check controller state with `ros2 control list_controllers`.
- Motion looks wrong: verify group names, frames, and SRDF joint order.
- Cartesian fraction is low: reduce step size and confirm obstacles are not blocking the route.
- Scene updates are missing: confirm RViz visibility, `frame_id`, and propagation time.

## Related docs

- [Quick reference](quick_reference.md)
- [Kinova Gen3 Lite + MoveIt 2 guide](kinova_gen3_lite_moveit2_guide.md)
- [Lab 06 README](../lab06_files/README.md)
