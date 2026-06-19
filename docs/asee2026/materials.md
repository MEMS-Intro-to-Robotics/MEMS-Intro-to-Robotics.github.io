---
title: Materials
---

# Materials

This page collects the links and artifacts educators usually ask for after the workshop.

## Workshop links

| Need | Where to go |
|---|---|
| Start the workshop in the room | [Quick Start](quickstart.md#in-the-room) |
| Run the take-home simulator | [Quick Start](quickstart.md#on-your-own-machine-take-home) |
| Facilitate the session | [For Instructors](for-instructors.md) |
| Free-play with every panel | [Sandbox](99_sandbox.md) |
| Reuse the workshop elsewhere | [Adopt This Workshop](adopt.md) |

## Docker image

```bash
docker pull ghcr.io/mems-intro-to-robotics/asee2026-workshop:latest
```

The image contains the simulator, notebooks, ROS 2 / MoveIt support, and a browser-based
3D viewer. In the room, station containers point the notebooks at hardware. On your own
machine, the same image runs in simulator mode.

## Notebook sequence

| Notebook | Purpose |
|---|---|
| `00_connect.ipynb` | Connect, pre-flight, and one safe motion |
| `01_joint_and_cartesian.ipynb` | Joint-space and Cartesian motion |
| `02_planning_scene.ipynb` | Collision objects and scene-aware planning |
| `03_pick_and_place.ipynb` | Pick, attach, place, release, and retreat |
| `challenge.ipynb` | Team-placed cubes and tallest standing stack |
| `99_sandbox.ipynb` | All panels together for practice and adaptation |

## Related Duke MEMS course pages

- [Full lab sequence](../labs/index.md)
- [Lab 05: Motion Planning with MoveIt 2](../labs/lab_05.md)
- [Lab 06: Pick-and-Place Manipulation](../labs/lab_06.md)
- [Kinova Gen3 Lite + MoveIt 2 guide](../guides/kinova_gen3_lite_moveit2_guide.md)
- [pymoveit2 API guide](../guides/pymoveit2_api_guide.md)
- [Educator adoption guide](../educator-adoption.md)
- [Lab catalog](../lab-catalog.md)

## Citation

If you reference the public course materials, use:

> Kusa, E. (2026). *Duke MEMS Intro to Robotics: Open Lab Manuals and Technical References for Simulation-First Robotics Teaching.* Available at [https://mems-intro-to-robotics.github.io](https://mems-intro-to-robotics.github.io).

For adapted course materials, a short attribution such as "Based on materials by Evan
Kusa, Duke University" is enough for the CC BY 4.0 license.
