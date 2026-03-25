# Quick reference

Keep this page open during lab when you need command reminders. It is intentionally a cheat sheet, not an onboarding walkthrough.

Assume you are on your Duke VCM inside the course Docker container unless noted. Use `$ROS_DISTRO` such as `jazzy`.

## Getting onto your VM desktop

Open **FastX 4** on your laptop, SSH to your VCM host, and use:

```bash
startxfce4
```

Window mode: **Single**

## Linux essentials

**Navigation and files**

```bash
pwd                         # where am I
ls -lah                     # list (human sizes, show dotfiles)
cd /path/to/dir             # change directory
mkdir -p my/dir/structure   # make dirs (parents)
rm -i file.txt              # remove (prompt)
rm -rI mydir                # recursive, confirm once
mv old new                  # move/rename
cp -r src/ dst/             # copy dir
```

**Viewing and searching**

```bash
less file.txt               # q quit, /pattern search
grep -R "pattern" .
find . -name "*.py"
head -n 20 file.log
tail -f file.log
```

**Editing**

```bash
nano file.txt               # Ctrl+O write, Ctrl+X exit
code .                      # open VS Code (VM GUI)
```

**Permissions and executables**

```bash
chmod +x script.sh
./script.sh
```

**Pipes, redirects, and jobs**

```bash
cmd1 | cmd2
cmd > out.txt 2>&1
```

Shortcuts: `Ctrl+C` interrupt, `Ctrl+Z` suspend, `fg`/`bg` resume

**Network and system checks**

```bash
hostname -I
ping -c 3 google.com
df -h
free -h
```

**Shell tips**

- `Ctrl+A` and `Ctrl+E` move to the start and end of a command line.
- `Alt+B` and `Alt+F` move by word.
- `Ctrl+R` searches command history.
- `!!` repeats the last command.
- `!$` inserts the last argument from the previous command.

## Git basics

**First-time SSH setup on the VM**

```bash
ssh-keygen -t ed25519 -C "netid@duke.edu"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
ssh -T git@gitlab.oit.duke.edu
```

Add the public key in GitLab before expecting `ssh -T` to succeed.

**Everyday flow**

```bash
git clone git@gitlab.oit.duke.edu:<netid>/<netid>_robotics.git
cd <netid>_robotics

git status
git add <files>
git commit -m "meaningful message"
git push origin main
```

**Branching**

```bash
git switch -c feature/x
git switch main
git merge feature/x
```

**Undo cookbook**

```bash
git restore --staged <file>
git restore <file>
git commit --amend --no-edit
```

**Useful `.gitignore` entries**

```text
*.log
__pycache__/
.vscode/
```

**When `git push` is rejected because the remote is ahead**

```bash
git status && git branch -vv
git add -A && git commit -m "WIP: lab updates"
git fetch origin
git rebase origin/main
git push origin main
```

If you hit conflicts during rebase:

```bash
git add <file>
git rebase --continue
```

**Throw away local work and match GitLab exactly**

```bash
git fetch origin
git reset --hard origin/main
```

Use that last flow only when you truly want to discard local changes.

## Docker

**Enable X11 on the VM**

```bash
xhost +local:docker
```

**Start a container**

```bash
cd ~/workspaces
docker run --rm -it --name rdev \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $PWD:/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest bash
```

Use `kinova-jazzy-latest` for Kinova labs when instructed.

**Attach another shell**

```bash
docker exec -it rdev bash
```

**Admin commands**

```bash
docker ps
docker images
docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest
```

`--rm` deletes the container when it exits. Omit it if you want to restart the same container later.

## Terminator

- Split panes horizontally: `Ctrl+Shift+O`
- Split panes vertically: `Ctrl+Shift+E`
- New tab: `Ctrl+Shift+T`
- Switch panes: `Ctrl+Shift+Arrow`

## ROS 2 essentials

**Environment**

```bash
echo $ROS_DISTRO
source /opt/ros/$ROS_DISTRO/setup.bash
printenv | grep -E "^ROS_|RMW|DOMAIN"
```

**Introspection**

```bash
ros2 --help
ros2 doctor
ros2 daemon stop && ros2 daemon start

ros2 pkg list | wc -l
ros2 pkg executables <package>

ros2 node list
ros2 topic list
ros2 service list
ros2 param list
```

**Interfaces and messages**

```bash
ros2 interface list | head
ros2 interface show std_msgs/msg/String
```

**Run, echo, and publish**

```bash
ros2 run <package> <executable>
ros2 topic echo /chatter --qos-profile system --once
ros2 topic pub /example std_msgs/msg/String '{data: "hello"}' --once
```

**Parameters**

```bash
ros2 param describe /node param_name
ros2 param get /node param_name
ros2 param set /node param_name value
```

**Launch files**

```bash
ros2 launch <package> <file>.launch.py --show-args
```

**Recording with rosbag2**

```bash
ros2 bag record /topic_a /topic_b
ros2 bag info <bag_dir>
ros2 bag play <bag_dir>
```

**Domain ID**

```bash
printenv ROS_DOMAIN_ID
export ROS_DOMAIN_ID=10
```

## Creating a ROS 2 Python package

```bash
ros2 pkg create --build-type ament_python my_pkg --license MIT --dependencies rclpy
colcon build --symlink-install
source install/setup.bash
ros2 run my_pkg my_node
```

Typical layout:

```text
my_ws/
├── src/my_pkg/
│   ├── package.xml
│   ├── setup.cfg
│   ├── setup.py
│   └── my_pkg/my_node.py
└── install/
```

Re-source `install/setup.bash` in every new terminal.

## Troubleshooting

- No GUI apps from the container: rerun `xhost +local:docker` and confirm `DISPLAY` plus `/tmp/.X11-unix` are mounted.
- `ros2` sees nothing: restart the daemon, confirm nodes are running, and confirm `ROS_DOMAIN_ID` matches.
- A script will not run: add execute permission with `chmod +x`.
- You are in the wrong shell: make sure you are typing in the container terminal you launched.
- `git push` is denied: verify the remote uses SSH and your SSH key is added to GitLab.
- Paths are confusing: check `pwd`, `PATH`, and `PYTHONPATH`.

## Quality-of-life tips

- Use the VS Code integrated terminal and Python extension.
- Search old commands with `history | grep <term>`.
- Helpful aliases for your `~/.bashrc`:

```bash
alias cb='colcon build --symlink-install'
alias srcros='source /opt/ros/$ROS_DISTRO/setup.bash'
```

- Find where a package lives with `ros2 pkg prefix <pkg>`.
- Make small Git commits with messages that explain why the change exists.
