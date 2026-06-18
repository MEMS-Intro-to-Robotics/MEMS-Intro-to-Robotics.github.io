---
title: 00 · Connect
---

# 00 · Connect to the arm

**What you'll do:** link your notebook's kernel to the arm, run a pre-flight check, and
command one slow, safe motion.

**The lever you're learning:** *velocity*, and the bigger idea that every behavior in
this workshop is a knob you control. Motion runs slowly on purpose, slow enough to
watch and stop, with the table e-stop as the real safety layer.

**Your turn:** after the arm retracts, you have confirmed the whole stack works end to
end (connection, planning, controllers, motion) from one `import` and one `connect()`.

!!! tip "If a pre-flight row is red"
    Re-run the pre-flight cell first. A FAIL is almost always a network/discovery issue,
    not your code. On a station, your table card has the details a facilitator needs.

<!-- BEGIN:rendered-notebook -->

# 00 · Connect to the arm

**ASEE 2026 · Hardware Integration in Introductory Robotics**, Kinova Gen3 Lite

This notebook connects your kernel to the arm and runs a pre-flight check before the first motion.

> **A note to faculty evaluating this for adoption.** Everything underneath these cells (the rclpy node, DDS discovery, the MoveIt move_group, the controllers) is owned by the `workshop_core` package. You are issuing high-level goals; the stack pilots execution. This is *maximal scaffolding on purpose*: the goal is a working pick-and-place in one sitting, not to teach rclpy. The student-facing labs this is drawn from deliberately scaffold **less**; this is the floor, not the calibration the course actually uses. What it costs to run is exactly what you see: one `import`, one `connect()`, no terminals.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import preflight

# Idempotent: re-running this cell reuses the same connection, then reset()
# cancels any stale goal and clears the planning scene. The station container
# sets WORKSHOP_MODE/ROBOT_IP, so this cell works unchanged in sim or hardware.
arm = WorkshopArm.connect()
arm.reset()
```

## Pre-flight

Every row should read **PASS** before we rely on the arm: joint states are streaming, MoveIt answers, and the key topics exist. A **FAIL** row is almost always a network/DDS problem. Flag a facilitator (recovery steps are in `facilitator/recovery.md`; your table card has the `ROS_DOMAIN_ID` and arm IP).


```python
preflight(arm)
```

## Your first commanded motion

`connect()` + `reset()` above already moved the arm once. `reset()` returns it to **home** (all joints zero, reaching straight up) to establish a known starting state. Now issue one explicit goal and watch it: **retract** to the tucked pose.

Motion runs at **velocity scaling 0.25**, slow enough to watch and stop, with the table e-stop as the real safety layer. The call blocks until the arm stops, then returns `True`.


```python
arm.retract()
```

A green pre-flight and a successful `retract()` mean you're ready for **`01_joint_and_cartesian`**.

If the arm didn't move or a row shows **FAIL**: re-run pre-flight. If it still fails, flag a facilitator; don't restart the kernel first. `facilitator/recovery.md` lists faster fixes.

<!-- END:rendered-notebook -->
