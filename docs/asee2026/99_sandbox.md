---
title: Sandbox
---

# Sandbox · Free play

Every panel from the workshop on one page, with no narration: dial in joint
configurations, push Cartesian moves past the feasibility threshold, toggle obstacles,
and run pick-and-place. Re-run the top cell at any time to reset.

This is also the **take-home** surface. Everything here runs against the simulator on
your own machine — no arm required — so you can adapt it to your own course or hardware.

- **Course site & lab manuals:** the full 10-lab simulation-first course is on this
  site under [Labs](../labs/lab_01.md).
- **The notebook stack** is portable to other MoveIt-supported arms; swap the robot
  model package and the named poses.

!!! note "Maximal scaffolding, on purpose"
    This workshop is a 2.5-hour onboarding floor — deliberately heavy scaffolding. The
    student-facing labs scaffold *less*: parameters become things students implement,
    not just sliders they move.

<!-- BEGIN:rendered-notebook -->

# 99 · Sandbox

Every panel from the workshop on one page, no narration. Free play: dial in joint configurations, push Cartesian moves past the feasibility threshold, toggle obstacles, run pick-and-place. Re-run the top cell any time to reset.

Same arm, same `reset()` safety net — `connect()` follows the station mode, while `connect("sim")` still forces the take-home simulator.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import joint_panel, cartesian_panel, planning_scene_panel, pick_place_panel, challenge_panel

arm = WorkshopArm.connect()
arm.reset()
```


```python
joint_panel(arm)
```


```python
cartesian_panel(arm)
```


```python
planning_scene_panel(arm)
```


```python
pick_place_panel(arm)
```


```python
challenge_panel(arm)
```

## Taking this home

Everything here runs against simulation on your own machine — no arm required — so you can adapt it to your course or hardware.

- **Course site & lab packets:** https://mems-intro-to-robotics.github.io/
- **This workshop image:** `ghcr.io/mems-intro-to-robotics/asee2026-workshop` (public; `docker pull`, then `docker compose up workshop`). The sim path is the take-home path; hardware stations use the same notebooks with `WORKSHOP_MODE=hardware` and `ROBOT_IP` set by the container.
- **Hardware:** Kinova Gen3 Lite (~$10k class). The notebook stack is portable to other MoveIt-supported arms; swap the model package and the named poses.
- **Pedagogy:** this is deliberately maximal scaffolding (a 2.5-hour onboarding floor). The student-facing labs scaffold *less* — parameters become things students implement, not just sliders they move.

Questions, or want the lab packets and rubrics? Reach the organizers via the course site.

<!-- END:rendered-notebook -->
