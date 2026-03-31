# Robot platform lab workflow

Use this page as the shared refresher for the platform-focused labs that come after Lab 4. Lab 05, Lab 06, Lab 07, Lab 09, and Lab 10 use different robots and launch commands, but the working rhythm is intentionally similar.

## The recurring pattern

1. Prepare the host first.
   - Update your course repo if the lab expects new starter files.
   - Pull the correct image or collect any robot-specific network details.
   - Run host-side setup such as `xhost +local:docker`, GPU setup, or robot IP/domain exports.
2. Start one lab environment.
   - Usually this means one Docker container for the entire lab.
   - If you need another terminal, attach to the same environment with panes, `docker exec`, or another shell.
   - Do not start duplicate containers unless the lab explicitly tells you to.
3. Assign clear pane roles.
   - launcher pane: simulator, driver, or mapping stack
   - visualizer pane: RViz, MoveIt, Nav2, plots, or status tools
   - development pane: `colcon build`, `source install/setup.bash`, `ros2 run`
   - utility pane: spawn/reset helpers, topic inspection, logs, screenshots
4. Keep long-running panes alive.
   - If Gazebo, RViz, MoveIt, SLAM, or Nav2 die, fix that first before debugging your own node.

## Recommended pane layouts

| Lab | Pane A | Pane B | Pane C | Pane D |
|---|---|---|---|---|
| Lab 05 | Kinova Gazebo | MoveIt + RViz | Development | Optional scratch |
| Lab 06 | Kinova Gazebo | MoveIt + RViz | Development | Block spawn/reset |
| Lab 07 | Crazyflie simulation | Controller / trajectory | Plotting / checks | Optional scratch |
| Lab 09 | Gazebo world | TurtleBot stack | Laser bridge | Development |
| Lab 10 | SLAM | Nav2 | RViz / command | Optional health checks |

## Build and source loop

Run this from your development pane after you create a workspace or change package metadata:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
cd /workspaces/[netid]_robotics_fall2025/labXX/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Rebuild when you:

- create a new package
- edit `setup.py`, `package.xml`, or dependencies
- add or rename a console entry point
- add new Python modules that need to be installed
- change message, service, or action definitions
- change compiled code or build-system files

With `--symlink-install`, you usually do not need to rebuild after editing an existing Python file. Save the file and rerun the node. If `ros2 run` cannot find your node, rebuild and re-source.

## Host files vs container files

- Keep your work inside the mounted workspace path so it persists after the container closes.
- If files created inside the container become read-only on the host, fix ownership from a host terminal with a lab-specific `chown`, for example:

```bash
sudo chown -R $USER:$USER ~/workspaces/[netid]_robotics_fall2025/lab09
```

- If a lab uses a communal machine, assume anything outside the mounted workspace is disposable unless the handout says otherwise.

## Quick failure checks

- Are you in the correct pane for this command?
- Did you run `source /opt/ros/$ROS_DISTRO/setup.bash` or `source install/setup.bash` in this pane?
- Is the simulator, driver, or visualization pane still running?
- Did you rerun the lab-specific host command that this shell depends on, such as `xhost`, `export ROS_DOMAIN_ID`, or `export TB4_IP`?
- Are your files editable on the host, or do you need a permissions fix?
- If the shared workflow looks right but the stack still misbehaves, use [Troubleshooting](../troubleshooting.md).

## Lab-specific differences to remember

- Lab 05 and Lab 06 use the Kinova image and usually work best with Terminator inside the container.
- Lab 07 still follows the one-environment rule, but you may use `docker exec -it lab07 bash`, terminal splitting, or `tmux` instead of Terminator.
- Lab 09 often needs a host-side `chown` after creating files inside the container.
- Lab 10 uses a communal lab PC and requires network/export variables in every new pane because you are talking to a real robot.

## Keep these open

- Use [Quick start](quick_start.md) if you need the Duke VM container basics again.
- Use [Quick reference](quick_reference.md) for command lookups during lab.
- Use [Troubleshooting](../troubleshooting.md) when the shared workflow is correct but the robot stack still does not behave the way you expect.
