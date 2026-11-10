# Troubleshooting

Find the symptom you see, then follow the linked fix. Commands labeled **Host VM
Terminal** run on your VM desktop; commands labeled **Container Terminal** run
inside the course Docker container.

## Find your problem

| What you see | Start here |
| --- | --- |
| VS Code cannot save, `git add` is denied, or files belong to `root` | [Fix container-created file ownership](#files-created-in-the-container-cannot-be-edited-on-the-host) |
| A `.sh` script says `Permission denied` | [Check executable permission and ownership](#a-script-fails-with-permission-denied) |
| No GUI window, a blank FastX desktop, or Docker will not start | [Environment and access](#environment-and-access) |
| FastX says `All 399 X11 display numbers are in use`, or `no space left on device` | [Move Docker's storage to /home](#fastx-says-all-399-x11-display-numbers-are-in-use-or-docker-reports-no-space-left-on-device) |
| Push, pull, or rebase fails | [Git and repository workflow](#git-and-repository-workflow) |
| Assignment acceptance fails | [Classroom 50 and submissions](#classroom-50-and-submissions) |
| ROS commands, packages, topics, or nodes are missing | [ROS 2 basics](#ros-2-basics) |
| The turtle does not move or a pen command fails | [Turtlesim and shell scripting](#turtlesim-and-shell-scripting) |
| The arm will not plan, execute, or grip | [MoveIt 2 and Kinova workflows](#moveit-2-and-kinova-workflows) |
| Gazebo or the simulated drone misbehaves | [Gazebo and Crazyflie simulation](#gazebo-and-crazyflie-simulation) |
| Gazebo shows things from another lab | [Stop leftover containers](#gazebo-shows-a-robot-a-world-or-objects-from-another-lab) |
| Flight-log plots or metrics look wrong | [Flight log analysis](#flight-log-analysis) |
| Lab 9: the simulation, the hazard monitor, or `lane_test` fails | [TurtleBot 4 sensors (simulation)](#turtlebot-4-sensors-simulation) |
| Lab 10: the simulation, Nav2, `point_goal`, `random_goals`, `explore`, or the map save fails | [SLAM and frontier exploration (simulation)](#slam-and-frontier-exploration-simulation) |
| TurtleBot, mapping, or navigation fails | [TurtleBot, SLAM, and Nav2](#turtlebot-slam-and-nav2) |

Use the site's search for an exact error message. If you need a TA, bring the
[command, terminal location, and error output](#students-need-a-fast-escalation-path).

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

**Symptoms:** VS Code cannot save a file, `git add` reports `Permission denied`,
or `ls -l` shows `root` as the owner.

The course container runs as `root`. Files it creates under `/root/workspaces`
appear in the VM's `~/workspaces` with that same ownership. Your VM account may
be unable to edit them, even though you can see them in VS Code.

**Host VM Terminal — not inside the container:** Open a terminal on your VM
desktop. Replace `YOUR_REPOSITORY` below with the affected repository's folder
name. Confirm `pwd` prints that repository before running `chown`.

```bash
cd ~/workspaces/YOUR_REPOSITORY
pwd
ls -ld . .git
ls -l
```

Then restore ownership of this repository, including its `.git` directory:

```bash
sudo chown -R "$(id -un):$(id -gn)" .
ls -ld . .git
git status
```

**Check:** The owner is now your VM username. Retry saving the file or running
`git add`. This changes file ownership; it does not delete files or change their
contents. Running it inside the container would select `root` again.

**Prevent it:** Create and edit files in VS Code on the VM, and clone, commit,
and push from the host VM terminal. Use the container for ROS commands and
builds. If a build creates root-owned files that you later need to edit, use
the same fix on the affected repository.

**Files missing on the VM entirely?** Files created outside the container's
`/root/workspaces` mount are a different issue. Keep the container running and
ask a TA to help copy them into the mounted workspace before exiting; `chown`
cannot recover files deleted with a `--rm` container.

### A pasted command reports its own flags as `command not found`

You pasted a command that spans several lines, and it arrived broken, so the
first line ran on its own and every later line ran as a separate command:

```text
docker: 'docker run' requires at least 1 argument
bash: --name: command not found
bash: --net=host: command not found
bash: ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest: command not found
```

The lines of such a command are joined by a backslash at the end of each line,
and that backslash only works when the line break follows it immediately. If a
space slips in between, the command ends there instead.

Retype it as a single line, with one space where each line break was, and leave
out the backslashes. Pasting the same broken text again gives the same result,
so there is no point repeating it.

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

### FastX says `All 399 X11 display numbers are in use`, or Docker reports `no space left on device`

The VM's main disk holds 25 GB, and Docker keeps its images there. About two
lab images can fill it. When it is full, FastX can fail to start a desktop and
`docker pull` can stop with `no space left on device`. A script moves Docker's
storage to the VM's larger `/home` disk (68 GB) and keeps the images you
already have. After a successful move, you do not need to run it again.

If FastX cannot start a desktop, open a terminal on your own computer and
connect to the VM with `ssh yourNetID@vcm-xxxxx.vm.duke.edu`, using the VM name
from the VCM page. Check the main disk:

```bash
df -h /
```

If the `Use%` column is above about 90%, run the script:

```bash
curl -fsSL -o move_docker_to_home.sh https://raw.githubusercontent.com/MEMS-Intro-to-Robotics/mems-robotics-toolkit/main/move_docker_to_home.sh && bash move_docker_to_home.sh
```

Type your NetID password when `sudo` asks for it. After a successful move,
the lines near the end of the output that start with `/var/lib/docker` and
`/var/lib/containerd` should both
show `ubuntuos-home--lv`, and `df -h /` should show a lower `Use%`. Start a new FastX
session. If both storage locations are already mounted, the script prints
`already a mount; skipping` twice and skips those moves.

If Docker will not start afterwards, or its error mentions
`containerd.services.leases`, ask a TA to check the cause. A full disk may have
damaged Docker's records,
and recovery may require removing the images you downloaded.

If you can discard stopped containers and unused volumes, you can free space
without moving the storage by running
`docker system prune -a --volumes -f`. It deletes stopped containers, unused images,
unused networks and build cache, and unused anonymous volumes without asking
for confirmation. You will need to download deleted lab images again.

### Gazebo shows a robot, a world, or objects from another lab

A container from an earlier session is probably still running. Closing a
terminal window may leave its container running, and
`docker system prune` does not remove a running container. The containers
share the VM's network, so Gazebo in your lab's container can discover
a Gazebo instance from an earlier session. On the
VM:

```bash
docker ps
```

If it lists more than one container, stop them all, then start your lab's
container again with the course `docker run` command:

```bash
docker stop $(docker ps -q)
```

If `docker ps` lists only your lab's container, show a TA the output of these
commands before restarting anything to help diagnose the cause:

```bash
uptime
```

```bash
pgrep -af "gz sim"
```

Then, inside the container:

```bash
gz service -l | grep -E "^/world/[^/]+/create$"
```

Each line it prints is one Gazebo world your container can reach. Restarting
the VM with `sudo reboot` may clear the problem.

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
or added after the first commit. For a repository whose workspace is named
`ros2_ws`, run these commands from the repository root on the host:

```bash
git rm -r --cached ros2_ws/build/ ros2_ws/install/ ros2_ws/log/
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

If it prints nothing, or prints `SUBNET`, exit and restart the container with
the `docker run` command from your lab manual. In the TurtleBot 4 image, the
addition at the end of that command sets `LOCALHOST` in every shell, overriding
the image's `SUBNET` setting.

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

### A planning failure reports `Error code: 99999`

Every failed planning attempt logs this number, whatever the reason for the
failure. It is a placeholder MoveIt uses when it has no more specific code, so
it tells you nothing about what went wrong and there is nothing to look up.
Read the lines above it instead: they name the goal that failed, and the
planning scene at the time is what to check.

### A run ends with `terminate called without an active exception`

Sometimes followed by `[ros2run]: Aborted`. If the milestone output above it is
complete, the work finished and this came from the shutdown afterwards, when a
background thread outlived the node. Nothing is lost and the screenshot and log
are still valid evidence.

If the output above it is *not* complete, the run really did stop early. Treat
the last line of real output as where it got to.

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

The launch terminal repeats `Failed to acquire lock in 20 seconds` or
`Could not contact service /controller_manager/list_controllers`. The spawners
cannot reach the controller manager, which runs inside Gazebo. Scroll up in the
launch terminal for a line showing that Gazebo exited, such as:

```
[INFO] [gazebo-8]: process has finished cleanly
```

The number after `gazebo-` can differ. If that line is there, Gazebo has exited.
The word "cleanly" does not mean the window opened successfully. Check the lines
above it for a crash or OpenGL error. If you find one, follow
[The Gazebo window is black, or the launch stops with an OpenGL error](#the-gazebo-window-is-black-or-the-launch-stops-with-an-opengl-error).

If Gazebo is still running, a startup race or another Gazebo process may be
interfering. Stop the launch, check for other Gazebo processes, and relaunch.

```bash
pgrep -f "gz sim"
pkill -f "gz sim"
```

Before relaunching, make sure no other Gazebo instance is running.

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

These entries are for Lab 07. Terminal 1 is the container shell running
`sim.launch.py`; Terminal 2 is the one in the repository root, where flights are
started.

### `Package 'lab07_crazyflie' not found`

The terminal has not sourced your workspace, or the package has not been built.
From the repository root, in the container:

```bash
source ros2_ws/install/setup.bash
```

If that file does not exist, see the next entry.

### `ros2_ws/install/setup.bash: No such file or directory`

The setup file is missing from this repository. Check that you are in the intended repository, then run the build line from the
lab's pre-lab (step 4) in a container terminal, then the "prepare" line from
Part 1 again. If the build line itself says `No such file or directory`, the
repository is not in `~/workspaces`: `ls ~/workspaces` shows what is there.

### The Gazebo window is black, or the launch stops with an OpenGL error

GPU rendering may be unavailable or misconfigured in that shell. In Terminal 1, stop the launch
with `Ctrl+C`, run these four lines, and start the launch again:

```bash
unset __NV_PRIME_RENDER_OFFLOAD __GLX_VENDOR_LIBRARY_NAME
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=3.3
export GALLIUM_DRIVER=llvmpipe
```

If no window opens at all, see
[GUI apps do not open from the container](#gui-apps-do-not-open-from-the-container).

The lab can also be done without the window. `ros2 launch lab07_crazyflie
sim.launch.py gui:=false` runs the same simulation, and flights are recorded
and measured the same way.

### A flight prints `Waiting for the simulation`

The mission has not started. Check that `sim.launch.py` is running in
Terminal 1 and inspect its output for errors. The flight proceeds once the
simulation clock, required services, and drone position are available.

### `A flight is already running in this container`

A second flight was started while one was still flying. Wait for the first to
finish, or stop it with `Ctrl+C` in its terminal, then start the new one. The
first flight is not affected.

### `A simulation was already running in this container`

`sim.launch.py` was started while another copy was running. The new one stopped
the old one and took its place, so the terminal that held the old one shows it
shutting down. Keep the new one running and carry on.

### `Cannot find .../gains.yaml`

Terminal 2 is not in the repository root. `fly.launch.py` reads `gains.yaml`
from the folder it is run from. `cd` to the folder that holds `gains.yaml` and
run the launch again.

### `gains.yaml is not laid out the way the controller reads it`

The launch could not read the expected parameter mapping. Possible causes
include a tab, a missing colon, wrong indentation, or a changed header line. From the repository root:

```bash
python3 check_gains.py
```

It lists the problems it detects. Fix them in order and run it again.

### A change to `gains.yaml` has no effect

Check three things, in this order:

1. The file is saved. VS Code shows a dot on the tab of a file with unsaved
   changes.
2. The flight printed the gains you expect. Every flight starts with a
   `Gains at startup` block; compare it with the file.
3. Terminal 2 is in the repository you are editing. `pwd` prints the folder.

If all three checks pass and the table values remain unchanged, record the
gains and measurements. The gain may have little effect in the tested range
or the change may be smaller than the table's displayed precision.

### The drone crashed, flipped over, or left the arena

When the drone ends up on the floor, the message
`The drone is on the floor: it has crashed` appears, and the flight's rows in the
table end with `crashed`. The flight ends 2 s later and is saved; on the course, the
waypoints left count as not reached. Start the next flight: every flight begins
by putting the drone back at the origin, upright.

### `runs/NAME.csv already exists`

A flight with `run:=NAME` does not replace an earlier recording with that name.
To fly it again, delete the old recording with the `rm` command the message
prints, then repeat the flight.

### `check_gains.py` says a gain must be between 0.0 and a limit

The limits (`kp` 10, `ki` 5, `kd` 2) apply to the gains you submit. A flight
with a larger value still runs, so an experiment may use one. Bring the gains
within the limits before the final course run.

### `Waypoint N not reached in 15 s`

The drone did not reach the waypoint tolerance before the timeout. It may have
hit a hoop or a wall, oscillated, or moved too slowly. Inspect that run's plot
in `runs/` and use your step-test measurements to decide whether to change
`kp` or `kd`.

### A flight takes much longer than the times in its table

Times in the tables are simulation time. When the VM draws Gazebo on the CPU,
the simulation can run slower than real time, so a 30 s step test takes longer
than 30 s on the wall clock. The table reports elapsed simulation time. Running the simulation
with `gui:=false` removes the drawing load.

## Flight log analysis

These entries cover the Lab 8 run folder (`trajectory_log.csv`, `launch.log`,
`course_waypoints.yaml`) and the starter's `analysis/lab08_analysis.py`.

### `data/` holds only `.gitkeep`

Course staff add your run folder and the baseline folder to your repository
after your lab section. To download them to your clone, go to your
repository root on the VM and run `git pull`. If it prints `Already up to date.`
and the folders are still missing, staff may not have added them yet; ask a TA if
they are missing the day after your section.

### `git push` is rejected with `fetch first`

This can happen when course staff add files to your repository after your last pull. Run
`git pull --no-edit`, then push again.

### `No such file or directory` when the script starts

Check that the `--run` folder name matches your folder in `data/`. The folder
is named after your GitHub username. Run `ls data` from the repository root
and copy the folder name exactly.

### `split_legs` stops with `matches no remaining waypoint`

A goal in `trajectory_log.csv` does not match the waypoints in
`course_waypoints.yaml` from that point on. This can happen if the files in
`data/` were edited. Restore them with `git checkout -- data` on the VM. Do not
edit anything in `data/`; filtering and any other changes belong in your script.

### 12 segments, not 13

The goal moves on as soon as the drone is within 5 cm of a waypoint. If the
drone was already within 5 cm of waypoint 1 when recording started, the
recording begins with waypoint 2, as it does in the baseline.

### Timestamps are not uniform, or rows repeat

Rows are written about 20 times a second, and the position is updated about 10
times a second, so about half the rows repeat the previous position. Compute
every time from the `time_s` column rather than from the row count. A jump in
`time_s` larger than about 0.1 s means rows are missing; exclude that stretch
from the metric it affects and say so in your methods.

### Filtering makes the response look slower

A wide moving average can make the response appear slower, and a Butterworth
filter applied in one direction delays the response. Use a window of 3 to 5 rows, or apply the
Butterworth filter with `scipy.signal.filtfilt` and a sample rate of 20 Hz.
Compute one metric with and without the filter to check the effect.

### Overshoot is 0 on every leg, or huge on one

Overshoot is measured past the waypoint along the leg's direction of travel, so
a leg in the -x or -y direction needs its position and waypoint multiplied by
-1 first. It is measured over the leg's window, which runs to 2 s after the next
goal change, because the goal moves on before the drone stops. A huge value
usually means the window ran into a later leg, or the wrong axis was used.

### The course time cannot be found in `launch.log`

The time on each line is the third bracketed field, for example
`[trajectory_publisher-2] [INFO] [1792536265.128681509]`. The course time is the
time on the first line containing `Advancing.` after the `Goal #13/` line, minus
the time on the `Goal #2/` line. Search without the number after the slash: the
baseline's log counts its goals out of 39 and has no `All waypoints completed`
line.

### Your metrics disagree with the baseline everywhere

If you matched the two flights by `time_s`, match them by waypoint number
instead. The flights started at different moments and their legs took
different times.

## TurtleBot 4 sensors (simulation)

These entries are for Lab 9. Terminal 1 is the container shell running
`sim.launch.py`, Terminal 2 is the container shell in the repository root where
you run `lane_test`, `record_noise`, and the tests, and Terminal 3 runs the
hazard monitor. Some problems in this lab have entries elsewhere on this page:

- Gazebo shows a robot or world from another lab:
  [Gazebo shows a robot, a world, or objects from another lab](#gazebo-shows-a-robot-a-world-or-objects-from-another-lab)
- `ros2` is not found in a terminal:
  [`ros2` says "command not found" in a terminal that worked a minute ago](#ros2-says-command-not-found-in-a-terminal-that-worked-a-minute-ago)
- `git add` is denied for the files in `runs/`:
  [Files created in the container cannot be edited on the host](#files-created-in-the-container-cannot-be-edited-on-the-host)

### FastX reports `All 399 X11 display numbers are in use`, or the pull runs out of space

See [FastX says `All 399 X11 display numbers are in use`, or Docker reports `no space left on device`](#fastx-says-all-399-x11-display-numbers-are-in-use-or-docker-reports-no-space-left-on-device).
Lab 9's pre-lab step 1 runs the same script.

### `Package 'lab09_sensors' not found`

The workspace may not have been sourced in this terminal. Every new container
shell needs the prepare line from Part 1:

```bash
cd ~/workspaces/intro-to-robotics-fall-2026-lab-09-* && source ros2_ws/install/setup.bash
```

If it prints `No such file or directory`, see the next entry.

### The prepare line prints `No such file or directory`

Either the repository is not in `~/workspaces`, or the package has not been
built there. In the container:

```bash
ls ~/workspaces
```

If no folder starting with `intro-to-robotics-fall-2026-lab-09-` is listed,
clone the repository into `~/workspaces` on the VM (pre-lab step 3). If it is
listed, run the build line from pre-lab step 5, then the prepare line again:

```bash
cd ~/workspaces/intro-to-robotics-fall-2026-lab-09-*/ros2_ws && colcon build --symlink-install && source install/setup.bash && ros2 pkg executables lab09_sensors
```

### The Gazebo window is black or does not open

If no window opens, see
[GUI apps do not open from the container](#gui-apps-do-not-open-from-the-container).
If the window is black or Terminal 1 shows an OpenGL error, see
[The Gazebo window is black, or the launch stops with an OpenGL error](#the-gazebo-window-is-black-or-the-launch-stops-with-an-opengl-error).

The lab's programs read sensor data over ROS 2 and move the robot through
Gazebo's services. You can run them without the simulation window by
starting the simulation with:

```bash
ros2 launch lab09_sensors sim.launch.py gui:=false
```

`lane_test`, `record_noise`, and the hazard monitor print their results in the
terminal.

### `ros2 topic list` shows only `/parameter_events` and `/rosout`

ROS 2 has not yet found the simulation's topics. Wait a few seconds and run the
command again. If the list is still short, or if `ros2 topic echo` or
`ros2 topic hz` prints nothing for a topic that is listed:

1. Check that Terminal 1 is still running the simulation, with no error at the
   end of its output.
2. Check that this terminal was opened with `docker exec -it lab09 bash`. A
   shell started with a second `docker run` is a separate container; see
   [Nodes in different panes cannot see each other](#nodes-in-different-panes-cannot-see-each-other).

### Terminal 1 keeps printing `Velocity command timed out. Braking.`

This is normal and needs no action. So are an `[ERROR]` line at startup saying
that the desired controller update period is faster than the simulation period,
and `process has died` lines after you press `Ctrl+C`. Leave Terminal 1
running.

### `A simulation was already running in this container. It was stopped; this one replaces it.`

`sim.launch.py` was started while another copy was running in the same
container. The new copy stopped the old one, so the terminal that held the old
one shows it shutting down. Keep the new one running and carry on.

### `No thresholds.yaml in ...`

The hazard monitor, `lane_test`, and `record_noise` read and write files in the
folder they are started from. Check that you are in the repository root,
then start the program again:

```bash
cd ~/workspaces/intro-to-robotics-fall-2026-lab-09-*
```

`ls` there lists `thresholds.yaml`.

### The hazard monitor says `is not written yet`

For example: `sensing.lidar_blocked is not written yet; skipping the lidar.`
The sensor is marked `use: true` in `thresholds.yaml`, but its function in
`sensing.py` still raises `NotImplementedError`, as it does in the starter. The
monitor skips that sensor, so it will not stop the robot.

Write the function, save `sensing.py`, and run its test from Terminal 2 (the
example uses `lidar_blocked`; use your function's name):

```bash
python3 -m pytest test_lab_9.py -v -k lidar_blocked
```

Then restart the monitor: press `Ctrl+C` in Terminal 3 and run
`ros2 run lab09_sensors hazard_monitor` again. The monitor reads `sensing.py`
only when it starts.

### The hazard monitor says `raised an error; skipping the ...`

For example: `sensing.depth_blocked raised an error; skipping the depth until
you fix it and restart:` followed by a traceback. Your function stopped with an
error on live sensor data. The traceback lists the calls leading to the error,
including the line in `sensing.py`; the last line gives the error type and
message. The monitor reports each function's error once and then skips that
sensor.

Use the traceback to find and fix the cause, run the function's test as in the
previous entry, then restart the monitor.

### A change to `thresholds.yaml` or `sensing.py` has no effect

The hazard monitor reads both files only when it starts. If you change the
thresholds while it runs, `lane_test` prints `thresholds.yaml has changed since
the hazard monitor started.`, and the run uses and records the thresholds the
monitor read at startup. Check the following:

1. The file is saved. VS Code shows a dot on the tab of a file with unsaved
   changes.
2. The monitor was restarted after the edit: `Ctrl+C` in Terminal 3, then
   `ros2 run lab09_sensors hazard_monitor`.
3. The monitor's first line, `Read .../thresholds.yaml. Sensors in use: ...`,
   names the `thresholds.yaml` in your repository and lists the sensors you set
   to `use: true`. `Sensors in use: none.` means no sensor is set to
   `use: true`.

### The robot drives past the hazard with `stopped by: none`

`lane_test` stops the robot only when the hazard monitor reports a hazard.
Check the following:

1. `lane_test` did not print `No hazard monitor is running`. If it did, start
   the monitor in Terminal 3 from the repository root and drive the lane again.
   A run made without the monitor has an empty `thresholds` column and does not
   count toward Part 5.
2. The sensor is listed in the monitor's `Sensors in use` line. If not, see the
   previous entry.
3. The monitor's terminal shows no `is not written yet` or `raised an error`
   message for that sensor. If it does, see the entries above.
4. While the robot drives, the monitor prints the sensor's name followed by
   `hazard`, for example `lidar: hazard`. If it never does, your function
   returned `False` for every message from that sensor on the way to the
   hazard. Check the function and its threshold, and whether this sensor can
   detect this hazard: Section 1.2 of the lab gives each sensor's limits, and
   Step 4.3 tests which sensors detect the low box.

### Lane A or C: `stopped by: cliff`, and the robot touched the hazard

In this simulation, the cliff sensors can report a cliff shortly after the
bumper pushes into the box or the wall, and that report is what stopped the
robot. The sensor you meant to stop it did not detect the hazard before the
robot reached it, so check that sensor as in the previous entry.

### `Could not move the robot to the lane start. Is the simulation running?`

`record_noise` prints `Could not move the robot. Is the simulation running?`
for the same problem. Both programs move the robot through Gazebo, and Gazebo
did not answer within 3 s.

1. Check Terminal 1. If the simulation has stopped, start it again with
   `ros2 launch lab09_sensors sim.launch.py`.
2. If you just started it, wait until the lanes appear in the Gazebo window,
   then run the command again.
3. Check that this terminal is a container shell opened with
   `docker exec -it lab09 bash`.

### A plotting script fails with `ImportError: numpy.core.multiarray failed to import`

The error starts with `A module that was compiled using NumPy 1.x cannot be run
in NumPy 2.5.3`. In this image, `python3` runs a separate Python that has NumPy
2, and the matplotlib installed with the system was built for NumPy 1. Run your
plotting script with the system Python instead, for example:

```bash
/usr/bin/python3 plot_noise.py
```

### `test_lab_9.py` says no row was made with the thresholds now in `thresholds.yaml`

The message starts `No row of runs/lane_results.csv was made with the
thresholds now in thresholds.yaml`, or names one lane and speed with
`no run with your submitted thresholds`. Each row of `runs/lane_results.csv`
records the thresholds the hazard monitor was using, and the test counts only
rows whose thresholds match `thresholds.yaml` as it is now. This happens when
`thresholds.yaml` was edited after the Part 5 runs, or when the runs were made
with a monitor that was not restarted after an edit.

With your final `thresholds.yaml` saved, restart the hazard monitor, drive all
four lanes at 0.2 and 0.3 m/s, run the tests again, and commit both
`thresholds.yaml` and `runs/lane_results.csv`. Do not delete the earlier rows.

## SLAM and frontier exploration (simulation)

These entries are for Lab 10. Terminal 1 is the container shell running
`sim.launch.py`, Terminal 2 runs `nav2.launch.py`, and Terminal 3 is the
container shell in the repository root where you run `point_goal`,
`random_goals`, `explore`, `overlay_map`, and the tests. Some problems in this
lab have entries elsewhere on this page:

- Gazebo shows a robot or world from another lab:
  [Gazebo shows a robot, a world, or objects from another lab](#gazebo-shows-a-robot-a-world-or-objects-from-another-lab)
- The Gazebo window is black or does not open:
  [The Gazebo window is black or does not open](#the-gazebo-window-is-black-or-does-not-open)
- `ros2 topic list` shows only `/parameter_events` and `/rosout`:
  [`ros2 topic list` shows only `/parameter_events` and `/rosout`](#ros2-topic-list-shows-only-parameter_events-and-rosout)
- `git add` is denied for the files in `runs/` or `maps/`:
  [Files created in the container cannot be edited on the host](#files-created-in-the-container-cannot-be-edited-on-the-host)

### `Package 'lab10_explore' not found`

The workspace may not have been sourced in this terminal. Every new container
shell needs the prepare line from Part 1:

```bash
cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-* && source ros2_ws/install/setup.bash
```

If it prints `No such file or directory`, the repository is not in
`~/workspaces` or the package has not been built there. Run `ls ~/workspaces`
in the container. If no folder starting with
`intro-to-robotics-fall-2026-lab-10-` is listed, clone the repository into
`~/workspaces` on the VM (pre-lab step 3). If it is listed, run the build line
from pre-lab step 5, then the prepare line again:

```bash
cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-*/ros2_ws && colcon build --symlink-install && source install/setup.bash && ros2 pkg executables lab10_explore
```

### Terminal 1 prints `[lab10] PROBLEM:`

`sim.launch.py` prints a checklist, `[lab10] 1/4` to `4/4`, as each part of the
simulation starts. When a part does not start, it prints `[lab10] PROBLEM:`
with the part's name, the folder of log files, and what to do: press `Ctrl+C`
in Terminal 1 (and in Terminal 2 if Nav2 is running) and start the simulation
again. If the same line appears a second time, ask a TA and show it, together
with the log folder it names.

### Terminal 2 prints `[lab10] PROBLEM: Nav2 did not finish starting within 30 seconds.`

Press `Ctrl+C` in Terminal 2 and start Nav2 again. If it happens a second time,
restart the simulation first (`Ctrl+C` in Terminal 2, then in Terminal 1), wait
for Terminal 1 to print `[lab10] Ready`, and start Nav2 again:

```bash
ros2 launch lab10_explore nav2.launch.py
```

It is ready when it prints `[lab10] Nav2 active. Send goals from the third
terminal or from RViz.`

### `Nav2 is not active after 60 s`

`point_goal`, `random_goals`, and `explore` wait up to 60 s for Nav2, then stop
with this message. Look at Terminal 2: if Nav2 is not running, start it; if it
printed `[lab10] PROBLEM:`, see the previous entry. When it prints `[lab10] Nav2
active`, run the program again.

### Nav2 stops working after you restarted the simulation

If you restart the simulation in Terminal 1 and leave Nav2 running in Terminal 2,
Nav2 may stop working. Errors such as
`Could not find a connection between 'map' and 'odom'` may appear in Terminal 2.
You may also see `process has died` for `component_container_isolated`, and the programs may stop with
`Nav2 is not active after 60 s`. Restart both, in this order: `Ctrl+C` in
Terminal 2, then in Terminal 1; start the simulation, wait for Terminal 1 to print
`[lab10] Ready`, then start Nav2:

```bash
ros2 launch lab10_explore nav2.launch.py
```

### `No map, or no robot position on it, after 30 s`

Nav2 is active but the map or the robot's position on it is missing.
To check whether the simulation and SLAM started, look in Terminal 1 for
`[lab10] Ready`; if it did not, restart the simulation and Nav2.

### `Another program that drives the robot is already running`

`point_goal`, `random_goals`, and `explore` refuse to start while another of
them is running, because two programs sending goals cancel each other's goals.
The message names the one that is running. Stop it with `Ctrl+C` in its
terminal, then run the command again. If you closed that terminal, open a
container shell and stop it there, for example `pkill -INT -f "lab10_explore explore"`.

### `Run this from the root of your repository`

The program writes its logs to `runs/` in the repository, so it has to run
from the folder that holds `test_lab_10.py`. In Terminal 3:

```bash
cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-*
```

### `exploration.... is not written yet`

For example: `exploration.goal_is_safe is not written yet (it still raises
NotImplementedError).` The function still raises
`NotImplementedError`, as it does in the starter. Write it in
`ros2_ws/src/lab10_explore/lab10_explore/exploration.py`, run its test from
Terminal 3 (the example uses `goal_is_safe`; use your function's name), and run
the program again:

```bash
python3 -m pytest test_lab_10.py -v -k goal_is_safe
```

### A goal fails with `was outside bounds`

Terminal 2 prints a line ending in `was outside bounds` when the goal is
outside the map SLAM has built so far. Nav2 can plan only to points on the map.
In Part 2, the east door is not on the map until the robot has seen it: do
Step 2.2 first. If the robot has already been south of the tool room, check the
signs in your conversion: a sign error puts the goal outside the room.

### The robot stops under a bench, or a goal ends `TIMED OUT`

The lidar scans at the height of the bench legs, below the top, so gaps between
the legs can appear free on the map. A goal there can trap the robot among the legs and stools,
and the goal ends `TIMED OUT` or `FAILED`. In Part 3 that result goes into your
table as it is. If it happens often with the check on, compare your
`CLEARANCE_M` with the gaps between bench legs.

### `The robot has not moved for 3 goals in a row`

`random_goals` and `explore` stop with this message when three goals in a row
end without the robot moving. In this room that usually means the robot is
wedged among bench legs or stools: every move Nav2 tries collides, and Terminal 2
shows `Collision Ahead` warnings. Restart the
simulation and Nav2 (the end of Part 1), then run the program again. A new run
replaces that run's log file.

### `Set CLEARANCE_M in exploration.py`

`random_goals` without `--no-check` needs your clearance. Set `CLEARANCE_M` at
the top of `exploration.py` to a number in meters, save the file, and run the
command again.

### `goal_is_safe rejected 2000 points in a row`

No point passed your check. Check whether `goal_is_safe` returns `False` for every
cell or whether the clearance excludes the available free areas on the map. Run
`python3 -m pytest test_lab_10.py -v -k goal_is_safe`; if it passes, compare
the clearance in cells that the message prints with the widths of the white
areas in RViz.

### `prediction.yaml` stops the first score run

Before the first `explore --strategy score` run, `prediction.yaml` has to be
filled in, committed, and pushed. The message says which step is missing:

- `prediction.yaml: fill in ...`: open the file and give that entry a number
  greater than 0 (a plain number, without units).
- `prediction.yaml is not committed yet` or `has changes that are not
  committed`: in a Host VM Terminal, in your repository, run

  ```bash
  git add prediction.yaml && git commit -m "Prediction" && git push origin main
  ```

- `prediction.yaml is committed but not pushed to GitHub yet`: in a Host VM
  Terminal, in your repository, run `git push origin main`.

Then start the run again. Run the commit and push commands in a Host VM
Terminal.

### The explorer prints `No reachable frontier` several times, then stops

At the end of a run this is normal: the explorer tries several more times,
then stops with `no reachable frontier left`. At the start of a run, check whether
your `find_frontier_cells` found usable cells: run its test, and check that
RViz shows white space around the robot. Frontiers may also be excluded by
the size, clearance, or path checks.

### The map does not grow, or RViz shows no map

Check whether SLAM is running and receiving scans. Look in Terminal 1 for
`[lab10] 4/4 SLAM active; map on /map`; if it printed `[lab10] PROBLEM:`
instead, restart the simulation and Nav2: `Ctrl+C` in Terminal 2, then in
Terminal 1; start the simulation, wait for `[lab10] Ready`, then start Nav2.

### `map_saver_cli` prints `Failed to spin map subscription`

The map did not reach the save command within its wait (20 s with the command in
Step 5.1). Check that Terminal 1 is still running the simulation from your last
score run, then run the command again, from the repository root:

```bash
mkdir -p maps && ros2 run nav2_map_server map_saver_cli -f maps/wilkinson129 --ros-args -p map_subscribe_transient_local:=true -p save_map_timeout:=20.0
```

If you closed Terminal 1 after the run, the map is gone: make another score run,
then save.

### RViz's Measure tool shows no distance

RViz shows the distance in the status bar at the bottom left of its window, as
`[Length: ...m]`, not on the map. If the bottom of the RViz window is below the
edge of the screen, maximize the window, then click the two points again.
Right-click in the map to clear the measurement.

### `No map file maps/wilkinson129.yaml`

`overlay_map` did not find the saved map. Run it from the repository root, after
Step 5.1 has written `maps/wilkinson129.pgm` and `maps/wilkinson129.yaml`.

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
