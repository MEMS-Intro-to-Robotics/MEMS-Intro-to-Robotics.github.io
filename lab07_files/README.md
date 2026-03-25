# Lab 07: 3D Goal Control and Trajectory Evaluation

Starter code for a simple 3D position controller, waypoint publisher, and trajectory plotting workflow.

## Files

| File | Description |
|---|---|
| `3d_goal_control.py` | Student-facing 3D PID controller that tracks a `PoseStamped` goal |
| `trajectory_publisher.py` | Publishes a sequence of waypoint goals and advances after arrival |
| `plotting.py` | Records actual versus commanded motion and saves a CSV plus plots |

## Typical workflow

1. Launch your simulator or robot stack so odometry and TF are available.
2. Run the controller and tune the `kp_*`, `ki_*`, and `kd_*` gains.
3. Run the trajectory publisher to send waypoint goals.
4. Run the plotting node while testing so you save tracking data and figures.

## Example commands

The package name depends on how you install these files into your ROS 2 workspace, so replace `<your_pkg>` with your package name.

**Run the controller**

```bash
ros2 run <your_pkg> goal_3d_controller --ros-args \
  -p kp_x:=0.6 -p kd_x:=0.12 \
  -p kp_y:=0.6 -p kd_y:=0.12 \
  -p kp_z:=1.2 -p kd_z:=0.25
```

**Run the waypoint publisher**

```bash
ros2 run <your_pkg> trajectory_publisher
```

**Run the plotter**

```bash
ros2 run <your_pkg> trajectory_plotter
```

## Outputs from the plotter

When you stop the plotter, it writes:

- `trajectory_log.csv`
- `traj_xyz_timeplots.png`
- `traj_xy_traj.png`

## Tuning notes

- Start with proportional gain only.
- Add a small amount of derivative gain to reduce oscillation.
- Keep maximum velocities conservative at first.
- Confirm your odometry and TF frames match the frame used for goals.

## Related guides

- [Quick reference](../guides/quick_reference.md)
- [For educators](../for-educators.md)
