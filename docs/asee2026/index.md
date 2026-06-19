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

Instructors: the run guide, timing, and per-activity breakdown live in
[For Instructors](for-instructors.md).
