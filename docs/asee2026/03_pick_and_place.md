---
title: 03 · Pick & Place
---

# 03 · Pick and place

**What you'll do:** run the full manipulation sequence from one panel: approach,
descend, grasp, attach, lift, place, release, retreat.

**The levers you're learning:** *pick and place coordinates*, *grip width*, and
*approach/grasp heights*. The panel also manages the **attach/detach** step that tells
the planner a grasped block is temporarily part of the arm, so it doesn't try to avoid
the thing it's holding.

**Your turn:** move one block from A to B; tune the grip so it holds without faulting;
then stack a second block on top. The pick, place, and stack you practise here is exactly
what the challenge runs.

!!! note "Grip and height are real, tunable things"
    Too loose and the block drops; too tight and the gripper faults. The right value is
    something you dial in, and on the real arm it differs from simulation, which is part of
    the point.

<!-- BEGIN:rendered-notebook -->

# 03 · Pick and place

This is where the earlier pieces come together. Joint moves, Cartesian moves, and the planning scene form the standard manipulation sequence:

> approach → descend → **grasp** → attach → lift → approach → descend → **release** → detach → retreat

The block is tracked in the planning scene the whole time: once grasped it's *attached* to the gripper (so the planner avoids the table with the block in hand), and released on placement.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import pick_place_panel

arm = WorkshopArm.connect()
arm.reset()
```

## Predict → Run → Explain

1. **Predict:** the grip-width slider is the closed-gripper target. What happens to the grasp if you set it *wider* than the block? What does the velocity slider change about how the motion *feels*?
2. **Run:** start with the defaults, then change one knob at a time.
3. **Explain:** the step list shows where time goes. Which phase dominates, and why?


```python
pick_place_panel(arm)
```

## Stretch: stack the blocks

Stacking is just pick-and-place with the place height raised one block per level. The cell below sets up three blocks and stacks them at a single (x, y), each placed `BLOCK_SIZE` higher than the last. Edit `STACK_XY` or `count` and re-run.


```python
from workshop_core import poses

arm.reset()
arm.add_box(poses.TABLE_ID, poses.TABLE_CENTER, poses.TABLE_SIZE)

count = 3
blocks = poses.DEFAULT_BLOCKS[:count]
targets = poses.stack_targets(poses.STACK_XY, count)
for i, block in enumerate(blocks, start=1):
    arm.add_box(f"block_{i}", block, (poses.BLOCK_SIZE,) * 3)

for i, (block, target) in enumerate(zip(blocks, targets), start=1):
    print(f"stacking block {i} -> {target}")
    # target is (x, y, end-effector height); pass the height as place_height
    ok = arm.pick_and_place(block, (target[0], target[1]), place_height=target[2],
                            block_id=f"block_{i}",
                            progress=lambda s, i=i: print(f"  block {i}: {s}"))
    if not ok:
        print(f"  block {i} failed; stopping")
        break
```

That is the workshop arc in one stack: configuration space, Cartesian descent, scene-aware planning, and grasping.

<!-- END:rendered-notebook -->
