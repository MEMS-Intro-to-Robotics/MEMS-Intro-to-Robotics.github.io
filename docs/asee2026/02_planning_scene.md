---
title: 02 · Planning Scene
---

# 02 · The planning scene

**What you'll do:** add an obstacle to the arm's world model and watch the motion
planner route around it.

**The lever you're learning:** *the planning scene*, the planner's internal model of
what's in the world. Add a collision object and the planner treats it as something to
avoid; remove it and the path goes straight again. It is also one of the challenge's
traps: cubes you set too close to grasp get rejected as collisions.

**Your turn:** drop an obstacle into the arm's path, replan, and compare the trajectory
with and without it. The path bending around the box is collision-aware planning doing
its job.

!!! tip "This shows up in the challenge"
    In the challenge, the planner's collision check is what rejects cubes you place too
    close to grasp. Understanding the scene here pays off when you lay out your cubes.

<!-- BEGIN:rendered-notebook -->

# 02 · The planning scene

The motion planner doesn't see the world; it sees a *model* of the world that you give it. Anything you don't put in the scene, it will happily drive straight through. This notebook makes that consequence visible.

> *Teaching note:* this is the cheapest, highest-leverage safety concept in the whole stack. "The arm hit the fixture" is almost never a planner bug; it's a missing collision object.


```python
from workshop_core import WorkshopArm
from workshop_core.widgets import planning_scene_panel

arm = WorkshopArm.connect()
arm.reset()
```

## Predict → Run → Explain

The button below replans the **same** home→retract motion every time. The toggle adds or removes a box sitting in the arm's path.

1. **Predict:** with the obstacle OFF, run it once and note the path. Now turn the obstacle ON. *Before* you replan: will the arm still reach retract? Will the path be longer, shorter, or the same?
2. **Run:** toggle the obstacle ON and replan.
3. **Explain:** the commanded endpoints never changed. Why did the motion?


```python
planning_scene_panel(arm)
```

The planner found a longer path around a box you declared, and would have found *nothing to avoid* if you hadn't. Scene fidelity is safety: the model's accuracy is the arm's safety margin.

Next: **`03_pick_and_place`** (the payoff), where the scene holds a table to avoid and a block to grasp.

<!-- END:rendered-notebook -->
