---
title: Quick Start
---

# Quick Start

The workshop ships as one Docker image: simulator, notebooks, and a browser-based 3D
viewer in the same container. You install nothing but Docker.

## In the room

Open the JupyterLab URL printed on your table card (it looks like
`http://<station>:8888`) and open `00_connect.ipynb`. There is nothing to install;
the station is already running the container.

## On your own machine (take-home)

```bash
# Pull the image once
docker pull ghcr.io/mems-intro-to-robotics/asee2026-workshop:latest

# Run it (simulator mode is the default)
docker run --rm -d --network host --shm-size=1g \
  ghcr.io/mems-intro-to-robotics/asee2026-workshop:latest
```

Or, from the repo's `docker/` directory:

```bash
docker compose up workshop
```

Then open <http://localhost:8888> and run `00_connect.ipynb`. A green pre-flight and a
slow `retract()` motion mean you are ready.

!!! note "Simulator vs. hardware: same notebooks"
    On your laptop the container runs a **mock simulator** (no arm needed). In the
    room the station container points the *same* notebooks at a real arm via
    `WORKSHOP_MODE` / `ROBOT_IP`. You never change the notebook to switch between them.

!!! warning "Give it a moment on first launch"
    The container brings up a full ROS 2 / MoveIt stack. The first pre-flight can take
    a few seconds while controllers activate. If a row reads **FAIL**, re-run the
    pre-flight cell before anything else.
