---
title: 01 · Joints & Cartesian
---

# 01 · Joint and Cartesian motion

**What you'll do:** drive the arm two different ways: joint by joint, and along
straight Cartesian lines in space.

**The lever you're learning:** *pose*. Joint sliders move each axis directly; Cartesian
moves ask the arm to travel in a straight line, which it can only do where the geometry
allows. A **feasibility fraction** tells you how much of the requested line was actually
reachable.

**Your turn:** reach a target pose with the sliders, then push a Cartesian move past
what's reachable and watch the planner refuse. That refusal is the lesson. (Tool-down
orientation is what you'll want for grasping later.)

!!! note "Why some moves are rejected"
    Near a singular configuration the arm loses the ability to move freely in some
    directions, so a straight-line request can come back with a low feasibility fraction
    and no motion. That is expected, and it is why we start from a bent, non-singular pose.

<!-- BEGIN:rendered-notebook -->

# 01 · Joint space and Cartesian motion

Two ways to tell the arm where to go: **joint by joint** (configuration space), and **straight-line moves of the end effector** (Cartesian space). The widgets below issue real motion goals; no rclpy here.

> *Teaching note for adopters:* each panel isolates one concept and nothing else. In the student labs these are the starting point for code the students write themselves; here the code is hidden so a 2.5-hour onboarding can reach the idea directly.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import joint_panel, cartesian_panel

# Standard top cell: reconnect (idempotent) and reset to a known-good state.
# reset() cancels any in-flight goal, clears the planning scene, and re-homes,
# so this notebook is safe to start from no matter what the last one left behind.
arm = WorkshopArm.connect()
arm.reset()
```

## Panel A: joint space

Each slider is one joint angle (radians), clamped to that joint's real limits. **Execute** plans and moves to the configuration you dialed in. **Sync sliders ← arm** copies the current pose into the sliders so you start from where the arm actually is.

Concept: every reachable pose of the arm is a point in this six-dimensional *configuration space*. Joint moves are easy: there is always a plan between two valid configurations.


```python
joint_panel(arm)
```

## Panel B: relative Cartesian

Now move the **end effector** in a straight line by (dx, dy, dz), holding orientation. `max_step` is how finely the path is sampled; `fraction_thr` is how much of the straight line must be feasible for the move to run.

Concept: **straight lines are hard, IK isn't free.** The planner solves inverse kinematics at every step; near a joint limit or a singularity it can only complete part of the line. Drive `fraction_thr` up, or ask for a large move, and watch it refuse; the *achieved fraction* readout tells you how far it got.

Start by clicking **Go to a non-singular pose**: from home (arm straight up, fully extended) the Jacobian is singular and *every* direction fails at 0%, which is itself a lesson, but a frustrating place to start exploring.


```python
cartesian_panel(arm)
```

Next: **`02_planning_scene`**: add an obstacle and watch the same commanded motion bend around it.

<!-- END:rendered-notebook -->
