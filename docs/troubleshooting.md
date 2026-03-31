# Troubleshooting

This page collects the issues that show up across multiple labs so students, TAs, and adopters do not have to rediscover the same fixes in separate handouts.

## Environment and access

### GUI apps do not open from the container

Check these first:

- Run `xhost +local:docker` on the host machine or VM
- Confirm `DISPLAY` is set in the shell launching Docker
- Confirm `/tmp/.X11-unix` is mounted into the container
- If you reopened the desktop session, run the `xhost` command again

Relevant pages:

- [Quick Start](guides/quick_start.md)
- [Quick Reference](guides/quick_reference.md)

### `docker` fails with a permissions error

Likely cause:

- The user is not yet in the `docker` group for the current login session

Try:

- Reboot or log out and back in after running the machine setup script
- Confirm you are on the intended student VM or lab desktop image

### Files created in the container cannot be edited on the host

This usually means the container wrote files as `root`.

Try:

- Use the documented host-side `chown` flow in labs that mount host workspaces
- Decide on one ownership strategy for your course and document it consistently

This is especially relevant in the TurtleBot and some simulation workflows.

## Git and repository workflow

### `git push` is denied

Check:

- The remote URL uses the intended host and protocol
- Your SSH key is loaded and added to the hosting provider
- You accepted any repository invitation required by your course workflow

### The remote is ahead of local work

Safe path:

```bash
git status
git fetch origin
git rebase origin/main
```

Only use destructive reset flows when you explicitly want to discard local work.

## ROS 2 basics

### `ros2` cannot see expected nodes, topics, or services

Check:

- The relevant launch files are still running
- You sourced the correct setup file in the current terminal
- `ROS_DOMAIN_ID` matches across terminals and machines when applicable
- Restart the daemon if discovery looks stale:

```bash
ros2 daemon stop
ros2 daemon start
```

### `ros2 run ...` says "package not found"

Check:

- You built the workspace successfully
- You sourced `install/setup.bash` in the current terminal
- The package name in `ros2 run <package> <executable>` matches the actual package

### `ros2 run ...` says "executable not found"

Check:

- The console entry is registered in `setup.py`
- You rebuilt after changing `setup.py`
- The module path in the entry point matches the file layout

## MoveIt 2 and Kinova workflows

### RViz launches but planning does not work

Check:

- `move_group` is running
- The simulation and MoveIt bring-up are both active
- The planning group, frames, and joint names match the robot model

Useful commands:

```bash
ros2 node list | grep move_group
ros2 param get /move_group robot_description_semantic > srdf.xml
```

### Planning succeeds but execution never starts

Likely cause:

- A controller is inactive, missing, or mismatched with the expected joint names

Check:

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

### Cartesian path fraction is very low

Try:

- Reduce waypoint spacing
- Keep orientation fixed first
- Confirm the planning scene and obstacle poses are correct
- Avoid singular stretches or near-limit poses

### Gripper commands do nothing

Check:

- The gripper action server name is correct
- The gripper controller is active
- The configured joint names and open/closed targets match the robot model

Useful commands:

```bash
ros2 action list | grep -i gripper
ros2 action info /PATH/TO/gripper_cmd
```

## TurtleBot, SLAM, and Nav2

### RViz shows disconnected frames or stale data

Check:

- The robot and workstation share the same `ROS_DOMAIN_ID`
- The discovery configuration is present in every new terminal
- SLAM, Nav2, and visualization were launched in the intended order
- The fixed frame is correct and the TF tree is connected

### The explorer does not choose sensible targets

Check:

- Frontier points may be unreachable, blacklisted, or snapped into invalid cells
- A noisy or incomplete map can make cost estimates unstable
- In the real robot workflow, stale networking or namespace mistakes can make the system appear idle

### The real TurtleBot 4 is not discovered from the lab workstation

Check:

- `TB4_IP` and `ROS_DOMAIN_ID` are correct
- `ROS_DISCOVERY_SERVER` is exported in every terminal pane
- You can `ping` the robot before launching the container

## Hardware session hygiene

### Shared lab machine workflows are confusing

A good operating pattern is:

- one pane for bring-up
- one pane for planning or navigation
- one pane for your own node
- one written checklist for environment variables that must be exported in every terminal

### Students need a fast escalation path

Capture these details before asking for help:

- image tag
- exact command run
- current terminal context: host or container
- relevant log output
- whether the issue is reproducible in a fresh terminal

## Known public-doc limitations

- Some labs still contain placeholder images where the original screenshots were removed during public export
- Lab 06 and Lab 07 starter scripts are documented here, but are still referenced from external course toolkit links
- The setup-script guide describes environment ownership, but the scripts themselves are not yet mirrored in this repository

## Related pages

- [Quick Start](guides/quick_start.md)
- [Quick Reference](guides/quick_reference.md)
- [Kinova Gen3 Lite + MoveIt 2 Guide](guides/kinova_gen3_lite_moveit2_guide.md)
- [pymoveit2 API Guide](guides/pymoveit2_api_guide.md)
