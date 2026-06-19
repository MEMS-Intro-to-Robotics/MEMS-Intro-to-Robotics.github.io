---
title: ASEE 2026 Workshop
---

# Hardware Integration in Introductory Robotics

**ASEE 2026 · Faculty Workshop.** Kinova Gen3 Lite with ROS 2 and MoveIt 2.

Drive a real 6-DOF robot arm through a guided sequence of Jupyter notebooks. You move
sliders and click buttons; a helper package owns the ROS 2, MoveIt, and controller
plumbing underneath. **No ROS code required.** The same container runs as a simulator on
your own laptop, so the workshop is usable after ASEE too.

!!! tip "You do not need prior ROS experience"
    Every control is a labeled knob, introduced one step at a time. By the last activity
    you are combining controls you have already used, instead of learning a new interface
    under pressure.

## Live materials

| Item | Link |
|---|---|
| Site build | [GitHub Pages workflow](https://github.com/MEMS-Intro-to-Robotics/MEMS-Intro-to-Robotics.github.io/actions/workflows/docs.yml) |
| Workshop image | `ghcr.io/mems-intro-to-robotics/asee2026-workshop:latest` |
| License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Full course context | [Duke MEMS lab sequence](../labs/index.md) |

## Start here Sunday morning

<div class="grid cards" markdown>

- **[I am in the room](quickstart.md#in-the-room)**

    Open the JupyterLab URL on your table card, start `00_connect.ipynb`, and run the pre-flight before moving the arm.

- **[I am facilitating](for-instructors.md)**

    Use the run guide for timing, station checks, safety reminders, and the challenge rules.

- **[I want to take this home](quickstart.md#on-your-own-machine-take-home)**

    Run the same notebooks in simulator mode with one Docker image. No robot is required for the take-home path.

- **[I want to adopt it](adopt.md)**

    See what transfers cleanly, what you need to replace, and how to scale the workshop into a course module.

</div>

## What educators should notice

- The workshop hides ROS 2 plumbing long enough for faculty to teach manipulation concepts first.
- The same notebooks move from simulator to hardware through `WORKSHOP_MODE` and `ROBOT_IP`, not a second curriculum.
- The full Duke MEMS course removes scaffolding later: students eventually write nodes, tune controllers, and debug the stack directly.
- The take-home simulator makes the workshop usable even for programs that do not own a Kinova arm.

## The arc (about 2.5 hours)

1. **Connect:** link your notebook to the arm, run a pre-flight check, and command one safe motion.
2. **Joints & Cartesian:** drive the arm two ways and feel where it can and cannot reach.
3. **Planning scene:** drop an obstacle in the way and watch the planner route around it.
4. **Pick & place:** grasp, attach, lift, and place, the canonical manipulation sequence.
5. **Challenge:** build the tallest standing stack in a friendly hardware competition.

## Activities

<div class="grid cards" markdown>

- **[00 · Connect](00_connect.md)**

    Connect, pre-flight, and your first commanded motion.

- **[01 · Joints & Cartesian](01_joint_and_cartesian.md)**

    Joint sliders and straight-line Cartesian moves, plus the feasibility readout.

- **[02 · Planning Scene](02_planning_scene.md)**

    Add an obstacle and see collision-aware planning bend the path around it.

- **[03 · Pick & Place](03_pick_and_place.md)**

    The full pick → attach → place sequence, driven from one panel.

- **[Challenge](challenge.md)**

    Tallest standing stack: place your own cubes and stack the tallest tower that stays up.

- **[Sandbox](99_sandbox.md)**

    Every panel on one page, for free play and take-home adaptation.

</div>

## Running it

- **In the room:** open the JupyterLab URL on your table card and start with `00_connect`.
- **On your own machine (take-home):** see the [Quick Start](quickstart.md). It is one `docker` command, no arm required.
- **Materials and links:** see [Materials](materials.md) for the Docker image, notebook path, course site, citation, and related lab pages.

Instructors: the run guide, timing, and per-activity breakdown live in
[For Instructors](for-instructors.md).

## Trust signals

| Item | Current workshop target |
|---|---|
| Robot | Kinova Gen3 Lite |
| Middleware | ROS 2 with MoveIt 2 |
| Delivery | Jupyter notebooks with `ipywidgets` controls |
| Take-home path | Docker simulator mode, no arm required |
| Public course context | Duke MEMS Introduction to Robotics and Automation |
