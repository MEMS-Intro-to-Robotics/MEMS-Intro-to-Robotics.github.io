---
title: Challenge
---

# Challenge · Tallest standing stack

**What you'll do:** combine everything from `00` to `03` into a competition. You place your
own cubes inside a marked zone, type each cube's (x, y), and the arm picks them and stacks
them into one tower. The tallest tower still standing wins.

**The skills you're using:** coordinate measurement and spatial planning. There are no
sliders. You read where each cube sits, enter it, and choose where the tower builds, all
inside a small zone. The gripper orientation is fixed, so cubes set too close cannot be
grasped, and the planner rejects the pick.

**Your turn:** lay out your cubes so every one is reachable and far enough apart to grab,
then build the tallest tower that still stands. A clean four-cube stack beats an ambitious
six that collapses.

!!! note "Practice in sim, win on hardware"
    Sim has no physics, so nothing topples there, but the coordinate entry, the zone limits,
    and the spacing rejections all behave the same. Dial in your layout in sim, then run the
    scored attempts on the real arm.

<!-- BEGIN:rendered-notebook -->

# Challenge: tallest standing stack

**ASEE 2026, Hardware Integration in Introductory Robotics.** Kinova Gen3 Lite.

This is the competition. You set out your own cubes inside a marked zone on the table, measure where each one is, and type its (x, y) into the panel. The arm picks every cube from where you said it is and stacks them into one tower. The tallest tower still standing wins. If it topples, you only get credit up to the last cube left standing.

There are no sliders to nudge here. The work is spatial: you choose where the cubes go and where the tower builds, all inside a small zone, and you read and enter real coordinates. Two things make it hard. The gripper orientation is fixed, so cubes set too close together cannot be grasped, because the fingers would hit the neighbour and the planner rejects the pick. And every coordinate has to be inside the zone and reachable, or the build stops.

> **Safety.** The table e-stop is your real safety layer. The red Stop button is a soft-stop: it cancels the current motion and leaves the arm where it is. Start slow.

> **Practice in sim first.** Sim has no physics, so nothing topples, but the coordinate entry, the zone limits, and the spacing rejections all behave the same. Get your layout working in sim, then run it on the real arm.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import challenge_panel

arm = WorkshopArm.connect()
arm.reset()
```

## Predict → Run → Explain

1. **Predict:** before you run, sketch your cube layout on the graph paper. How far apart do two cubes need to be for the gripper to grab one without hitting the other? Where will you build the tower so the arm can reach every cube and the growing stack?
2. **Run:** enter your cubes' coordinates and a stack location, then Build. Watch which picks succeed.
3. **Explain:** if a pick is rejected, was the cube too close to a neighbour, outside the zone, or just hard to reach? Move it and try again.


```python
challenge_panel(arm)
```

## Scoring and strategy

Your score is the standing height of the tower: the number of cubes still up, times 5 cm per cube. A judge counts what is actually still standing on the real arm.

The temptation is to pack cubes in for a tall tower, but cubes set too close cannot be picked, and a tower built from sloppy coordinates leans and falls. A clean four-cube stack from well-measured, well-spaced positions beats an ambitious six that collapses. Measure carefully, give each cube room, and put the tower somewhere the arm can reach as it grows.

## Optional: script it instead

The panel is enough to compete. If your team would rather write the layout in code, the cell below does the same thing: a list of cube coordinates, a stack location, and the pick-and-place loop, open for you to edit. Coordinates here are in metres (the panel uses inches for convenience).


```python
from workshop_core import poses

# Where you set each cube, (x, y) in metres, inside the zone. Measure and enter
# these; the arm picks from exactly here.
sources = [
    (0.33, -0.12),
    (0.33,  0.12),
    (0.45, -0.12),
    (0.45,  0.12),
]
stack_xy = (0.39, 0.0)   # where the tower goes
gap = 0.004
arm.velocity_scaling = 0.25

targets = poses.stack_targets(stack_xy, len(sources), gap=gap)
arm.reset()
arm.add_box(poses.TABLE_ID, poses.TABLE_CENTER, poses.TABLE_SIZE)
for i, (x, y) in enumerate(sources, start=1):
    assert poses.in_zone(x, y), f"cube {i} at ({x}, {y}) is outside the zone"
    arm.add_box(f"cube_{i}", (x, y, poses.BLOCK_CENTER_Z), (poses.BLOCK_SIZE,) * 3)

for i, ((x, y), tgt) in enumerate(zip(sources, targets), start=1):
    ok = arm.pick_and_place((x, y), (tgt[0], tgt[1]),
                            place_height=tgt[2], block_id=f"cube_{i}")
    print(f"cube {i}: {'stacked' if ok else 'could not place, stopping'}")
    if not ok:
        break
```

That is the workshop in one tower: configuration space, Cartesian descent, scene-aware planning, and grasping. Place well, measure carefully, and good luck.

<!-- END:rendered-notebook -->
