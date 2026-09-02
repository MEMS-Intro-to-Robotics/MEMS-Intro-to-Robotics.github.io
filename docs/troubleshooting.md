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

The container runs as `root` and mounts `~/workspaces` at `/root/workspaces`. A
bind mount shares ownership by numeric user ID, so any file created from a
container terminal is owned by `root` on the VM. Your NetID account cannot write
to it, and editing it or running `git add` fails with `Permission denied`.

Check the owner, then take the files back:

```bash
ls -l <file>
sudo chown -R "$USER:$USER" ~/workspaces
```

If you cloned the repository from inside the container, `.git` is root-owned too
and every Git command fails the same way. The same command fixes it.

Create and edit repository files from the host VM terminal, and use the
container terminal for `ros2` commands. This applies to every lab that mounts
`~/workspaces` into the container.

### `docker run` says the container name is already in use

A container from an earlier session is still running or still being cleaned up.
Either attach to it:

```bash
docker exec -it <name> bash
```

or remove it and start again:

```bash
docker rm -f <name>
```

### FastX connects but the screen is black or blank

Usually a stale desktop session, or one started with the wrong command or
window mode. Terminate the session in the FastX client and start a new one with
command `startxfce4` and window mode **Single**. If it persists, reboot the VM
from an SSH terminal with `sudo reboot`.

### `pytest` is not found

Course VMs install it through the setup script. If it is missing, the script did
not finish. Install it with apt:

```bash
sudo apt-get install -y python3-pytest
```

Do not use `python3 -m pip install pytest`. Ubuntu 24.04 treats the system
Python as externally managed and refuses that install.

### `ros2` says "command not found" in a terminal that worked a minute ago

That terminal is on the VM host, not inside the container. ROS 2 is only
installed in the container.

```bash
docker exec -it <container-name> bash
```

Or work in Terminator panes opened from inside the container.

### Nodes in different panes cannot see each other

A pane started with `docker run` instead of `docker exec` is a *separate
container* with its own ROS graph, and discovery is limited to localhost per
container. Close the stray pane and re-enter the original container with
`docker exec -it <container-name> bash`. Confirm with `ros2 topic list`; you
should see the topics published by the first pane.

### The image pull or container start fails with "no space left on device"

Old images and volumes have filled the VM disk.

```bash
docker system prune -a --volumes -f
```

This removes all unused images, so you will re-pull for other labs.

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

### `git push` is rejected as non-fast-forward

The message says `! [rejected]` with `fetch first` or `non-fast-forward`. The
remote holds a commit your branch does not contain, and the rejection is
protecting it.

Do not force-push. Inspect first:

```bash
git fetch origin
git log --oneline --graph --decorate --all
```

Then integrate with the strategy your lab specifies.

### `git pull` asks how to reconcile divergent branches

Both branches have new commits and Git will not guess. Unless a lab says
otherwise, replay your local commits on top of the remote ones:

```bash
git pull --rebase origin main
```

### A rebase stops with a conflict

Git found edits to the same lines on both sides and needs your decision.

```bash
git status
```

Open the file, replace the whole `<<<<<<<` / `=======` / `>>>>>>>` marker block
with the content you actually want, then:

```bash
git add <file>
GIT_EDITOR=true git rebase --continue
```

To return to the state before the rebase, run `git rebase --abort`. If you have
tried once carefully and are still stuck after about ten minutes, ask a TA
rather than reaching for force-push or a hard reset.

### `git push` prompts endlessly for a username and password

You are pushing from inside the container, which has no credentials. Always
commit and push from a host VM terminal.

### Build artifacts were committed by mistake

`build/`, `install/`, and `log/` were committed because `.gitignore` was missing
or added after the first commit. From the host:

```bash
git rm -r --cached build/ install/ log/
git commit -m "Remove build artifacts"
git push
```

Then confirm `.gitignore` lists all three directories.

## Classroom 50 and submissions

### `gh student accept` says the classroom or assignment is unavailable

The organization invitation is missing, one of the three arguments was
mistyped, or the Classroom 50 manifest has not finished publishing. Check the
organization, classroom short name, and assignment slug against your lab
manual. If all three are correct, send the complete error to course staff, who
need to verify the assignment and its publishing workflow.

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

### Code changes do not take effect when you run the node

Either the workspace was built without `--symlink-install`, or you added a new
file. New files always require a rebuild, and so do edits to `setup.py` and
`package.xml`, which are only read at build time.

```bash
colcon build --symlink-install
source install/setup.bash
```

Re-source in every terminal, or open a fresh one.

### `ModuleNotFoundError: No module named '<package>.scripts'`

The `scripts/` directory has no `__init__.py`, so Python does not treat it as a
package and the build system does not install it.

```bash
touch <ws>/src/<package>/<package>/scripts/__init__.py
colcon build --symlink-install
source install/setup.bash
```

Commit the `__init__.py`. An empty file is correct.

### `ros2 topic echo` prints nothing

Check, in order: the publisher is actually running, the topic names match
exactly (case matters), and the terminal running `echo` is sourced. Compare
against `ros2 node list` and `ros2 topic list`.

### A node runs but prints nothing

Either the logging calls sit outside the callback, or the subscriber callback
has the wrong signature. A callback that does not accept exactly one message
argument fails silently.

### A node is missing from `rqt_graph`

Two nodes were given the same name in `super().__init__()`, and only one appears
in the graph. Give each node a unique name.

### `rqt_graph` is blank or missing nodes you just started

The graph is a snapshot from when the window opened. Click refresh, the circular
arrows at the top left. Also confirm the dropdown is on Nodes/Topics (all) and
that the Hide options are not filtering what you are looking for.

### You see nodes, topics, or robots you never created

Your container is discovering other people's ROS 2 systems on the shared campus
network, because `ROS_AUTOMATIC_DISCOVERY_RANGE` is not set. Inside the
container:

```bash
env | grep ROS_AUTOMATIC
```

If it prints nothing, exit and restart the container with the course
`docker run` command, which sets it with `-e`.

### `No transform from [frame A] to [frame B]`

A TF error means the frame tree is broken, usually because a node that publishes
transforms has crashed. Check every pane for errors; the one full of red text is
the cause.

## Turtlesim and shell scripting

### The turtle does not move

Either `turtlesim_node` is not running, or your script is running on the host
rather than inside the container. Confirm the turtlesim window is open and run
the script from a container terminal. In another pane,
`ros2 topic echo /turtle1/cmd_vel` shows whether commands are being published.

### A script fails with `Permission denied`

The file is not marked executable. Run `chmod +x <script>.sh`.

If `chmod` itself is denied, or `ls -l` shows the file owned by `root`, this is
the container ownership problem instead: see
[Files created in the container cannot be edited on the host](#files-created-in-the-container-cannot-be-edited-on-the-host).

### `set_pen` with the pen-off field fails with a YAML error

Unquoted `off` is parsed by YAML as the boolean false, not as a field name.
Quote it:

```bash
"{r: 255, g: 0, b: 0, width: 5, 'off': 1}"
```

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

### Controllers fail to load, or spawners time out

Usually a startup race, or a leftover Gazebo process holding simulation
resources. Stop the launch, check for stragglers, and relaunch.

```bash
pgrep -f "gz sim"
pkill -f "gz sim"
```

Only one Gazebo instance should ever run.

### `gz service` reset commands fail with service not found

The world is not named `empty`, so `/world/empty/set_pose` does not exist.
Discover the real name and substitute it:

```bash
gz service -l | grep set_pose
```

### Objects are knocked over or out of reach after a failed run

Expected; physics happened. Use the per-block reset commands from the lab
rather than restarting the simulation, then re-run the scene-setup task if you
also removed or re-added planning-scene objects.

## Gazebo and Crazyflie simulation

### The simulation cannot find `model.sdf`

`GZ_SIM_RESOURCE_PATH` is unset or wrong in the launch terminal. The course
`docker run` command sets it; if you started the container another way, set it
manually before relaunching.

### Gazebo renders a black window, or crashes with an OpenGL error

GPU rendering is unavailable. In the launch terminal:

```bash
export LIBGL_ALWAYS_SOFTWARE=1
```

Longer term, use the CPU variant of the `docker run` command, or drop
`--gpus all`.

### The drone does not move at all

Check that both the controller and the goal publisher are running. Gains
default to `0.0`, so a controller launched without its gain arguments commands
nothing. Confirm goals and commands are flowing:

```bash
ros2 topic echo /goal_pose --once
ros2 topic echo /crazyflie/cmd_vel --once
```

### The drone drifts or moves in the wrong direction

The TF chain from `map` to the drone base frame is wrong or stale.

```bash
ros2 run tf2_ros tf2_echo map crazyflie/base_footprint
```

If the translation does not track the drone, restart the controller node, which
bridges odometry into TF.

### The drone chatters or twitches at a waypoint

Gains are too aggressive and the controller is fighting the arrival deadband.
Reduce the proportional gain slightly, or increase the derivative gain for more
damping.

### The simulation runs but no odometry appears

The simulation is paused, or the launch did not fully start. Press play in the
Gazebo GUI, then check `ros2 topic list | grep odom`.

## Flight log analysis

### `pd.read_csv` fails, or columns load as strings

Padded column names or comment lines in the log. Read with
`skipinitialspace=True`, and print `df.columns` and `df.dtypes` before anything
else so you know what you actually loaded.

### Timestamps are not uniform

Logging rates are approximate, so never assume a fixed sample interval. Compute
metrics from the actual time column, or resample onto a uniform grid by
interpolation first.

### NaN gaps or frozen position values mid-flight

Brief tracking dropouts. Interpolate gaps of a few samples, exclude longer gaps
from metric windows, and say so in your methods. Check the run's metadata file
for logged tracking issues.

### Filtering makes the step response look slower

A wide moving average smears step edges, and a causally applied Butterworth adds
phase lag. Use a smaller window or a median filter, apply Butterworth zero-phase
with `scipy.signal.filtfilt`, and always sanity-check metrics against the raw
signal.

### Segmentation produces hundreds of tiny segments

During path-following the goal changes every sample, so a rule of "new segment
on any goal change" fires continuously. Merge contiguous runs of goal changes
into one path segment and start step segments only on isolated, large goal
jumps. A minimum segment duration also works.

### Overshoot is huge on a segment the vehicle never reached

The metric is reporting peak error rather than post-crossing error. Overshoot is
defined only after the first goal crossing; if the position never crosses the
goal, overshoot is zero.

### Settling time is never found for some segments

The vehicle never stayed inside the tolerance band before the next goal
arrived, which is common with aggressive gains on hardware. Report the segment
as not settled and discuss it. That is a legitimate result, not a number to
force.

### Your metrics disagree with the baseline everywhere

The two flights are being aligned by absolute time. They did not start at the
same instant. Align by goal-change times and match segments by label or order.

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

### The robot sits still for several seconds, then moves

Compute starvation. Search algorithms written in Python are slow when the target
is far away or the map is complex. Often acceptable, but if it trips a stuck
timeout, raise the timeout or lower the planning rate so it replans less often.

### The robot ignores a frontier that is clearly reachable

Two common causes. It may have tried that target before, failed, and blacklisted
it; check the logs for blacklist messages. Or the frontier centroid may sit
just inside a wall, and the nearest-valid-point fallback failed on a noisy map.

### The robot spins in place or wiggles without progress

Oscillation between two targets with nearly identical scores: it picks one,
moves slightly, recalculates, picks the other. Real systems add hysteresis by
sticking with a decision for a while. Usually ignorable unless it stops
exploration.

### The robot does not move when your node runs

The command is not reaching the wheels somewhere along your node, then Nav2,
then the robot. Check the Nav2 pane for errors, whether the pose on the map
indicates a localization failure, and whether a path is being drawn in RViz at
all. No path usually means the goal is unreachable or in unmapped space.

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
