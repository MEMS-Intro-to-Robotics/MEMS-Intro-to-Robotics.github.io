# Quick start

Use this page when you want the fastest path from logging into a Duke VCM to running the course container.

## Who this is for

- Students working on labs in a Duke VCM FastX session.
- TAs helping students get into the standard ROS 2 environment quickly.

## 1. Open a GUI session on your VCM

Open **FastX 4** on your laptop, SSH to your VCM host, and launch your desktop with:

```bash
startxfce4
```

Once you are on the VM desktop, allow Docker containers to open GUI apps:

```bash
xhost +local:docker
```

## 2. Pull the course image

Pull the image you need for the lab:

```bash
docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest
docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest
```

Use `base-jazzy-latest` for general ROS 2 work unless the lab explicitly tells you to use the Kinova image.

## 3. Start a container with your workspace mounted

From your VM:

```bash
cd ~/workspaces
docker run --rm -it --name rdev \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $PWD:/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest bash
```

When the lab is Kinova-specific, switch the image tag to `kinova-jazzy-latest`.

## Attach another shell to the same container

```bash
docker exec -it rdev bash
```

## Good to know

- Avoid `apt install` inside the course containers unless the lab instructions explicitly tell you to.
- Keep your personal lab repo separate under `~/workspaces/`.
- If GUI apps do not open from the container, run `xhost +local:docker` again on the VM and confirm `DISPLAY` plus `/tmp/.X11-unix` are mounted.
- Pull the same image tag again later to refresh your toolchain.

## What to open next

- For command lookups during lab, use [Quick reference](quick_reference.md).
- For Kinova work, continue to [Kinova Gen3 Lite + MoveIt 2 guide](kinova_gen3_lite_moveit2_guide.md).
- For lab-specific starter assets, open [lab06_files/README.md](../lab06_files/README.md) or [lab07_files/README.md](../lab07_files/README.md).

## Getting help

1. Check the relevant lab handout first.
2. Check the course communication channels for known issues.
3. If you still need help, open an issue with the image tag, the command you ran, and the log output you saw.
