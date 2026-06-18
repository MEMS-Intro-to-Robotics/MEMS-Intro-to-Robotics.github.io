---
title: Challenge
---

# Challenge · Tallest standing stack

**What you'll do:** combine everything from `00` to `03` into a competition. The arm builds
a tower of cubes, one block per level, and the tallest tower still standing wins.

**The levers you're learning:** the **release gap** (how far above the block below each cube
is dropped) and **velocity**. Together they decide whether the tower stays up on the real
arm. Too tight a gap and the place is rejected as a collision; too loose and the cube drops
and topples.

**Your turn:** find the gap that never gets rejected and never topples, then push the block
count. A reliable 4-stack beats a 6-stack in pieces.

!!! note "Practice in sim, win on hardware"
    Sim has no physics, so nothing topples there. Use it to dial in the motion and watch it
    in the 3D view, then run the scored attempts on the real arm.

<!-- BEGIN:rendered-notebook -->

# Challenge: tallest standing stack

**ASEE 2026, Hardware Integration in Introductory Robotics.** Kinova Gen3 Lite.

This is the competition. Everything from `00` through `03` comes together here: you set a few knobs and the arm builds a tower of cubes, one block per level. The tallest tower still standing wins. If it topples, you only get credit up to the last block left standing.

Two knobs decide whether the tower stays up on the real arm. The **release gap** is how far above the block below each cube gets dropped: set it too tight and the place reads as a collision and gets rejected, too loose and the cube falls the last few millimetres and can knock the tower over. **Velocity** is the other one, since a gentler placement settles better.

> **Safety.** The table e-stop is your real safety layer. The red Stop button is a soft-stop: it cancels the current motion and leaves the arm where it is. Start slow.

> **Sim has no physics.** Nothing topples in sim and every placement "succeeds" there, so use sim to get the motion right and watch it in the 3D view. Then switch the station to hardware and tune the gap and velocity until the tower actually stands.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import challenge_panel

arm = WorkshopArm.connect()
arm.reset()
```

## Predict → Run → Explain

1. **Predict:** which knob most affects whether the tower stays standing, and which way? What do you think happens at `release gap = 0`?
2. **Run:** start at 3 blocks with the defaults, watch it in the 3D view, then change one knob at a time and add a block.
3. **Explain:** when a place gets rejected, what does that tell you about the gap versus the block below? When a tower topples on hardware even though every place succeeded, what does that tell you about release height and velocity?


```python
challenge_panel(arm)
```

## Scoring and strategy

Your score is the standing height of the tower: the number of cubes still up, times 5 cm per cube. The panel reports how many levels it placed and the height if they all stand, but a judge counts what is actually still standing.

A reliable 4-stack beats an ambitious 6-stack lying in pieces. Find a gap that never gets rejected and never topples, then push the count up from there.

The tower is tracked in the planning scene as it grows, so each higher place plans around the cubes already down.

## Optional: script your own strategy

The panel above is enough to compete. If your team would rather write the strategy yourselves, with a different stacking order, custom positions, or a per-level gap, the cell below is the same loop the panel runs, opened up for you to edit.


```python
from workshop_core import poses

n = 4                      # how many to stack (cap 6)
base_xy = poses.STACK_XY   # where the tower goes (x, y)
gap = 0.004                # release gap (m); tune for a standing tower on hardware
arm.velocity_scaling = 0.25

sources = poses.staging_row(n)
targets = poses.stack_targets(base_xy, n, gap=gap)

arm.reset()
arm.add_box(poses.TABLE_ID, poses.TABLE_CENTER, poses.TABLE_SIZE)
for i, src in enumerate(sources, start=1):
    arm.add_box(f"cube_{i}", src, (poses.BLOCK_SIZE,) * 3)

for i, (src, tgt) in enumerate(zip(sources, targets), start=1):
    ok = arm.pick_and_place((src[0], src[1]), (tgt[0], tgt[1]),
                            place_height=tgt[2], block_id=f"cube_{i}")
    print(f"level {i}: {'placed' if ok else 'rejected, stopping'}")
    if not ok:
        break
```

That is the whole workshop in one tower: configuration space, Cartesian descent, scene-aware planning, and grasping, all composed into something you can compete with. Good luck.

<!-- END:rendered-notebook -->
