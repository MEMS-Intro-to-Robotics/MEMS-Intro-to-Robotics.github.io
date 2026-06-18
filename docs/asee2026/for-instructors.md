---
title: For Instructors
---

# For Instructors

This page is the run guide for facilitating the workshop. The attendee experience is
designed to be **self-service**: people should know what to do from the notebooks and this
site alone. Your job is to set up the stations, keep the arms safe, and judge the
challenge, not to lecture.

## Design in one sentence

Attendees never write ROS code. They turn labeled knobs (ipywidgets) that map to meaningful
robot behavior, and the `workshop_core` helper package owns all the ROS 2 and MoveIt
integration underneath. Those who want to go further can drop into Python and extend it.

## The knob ladder

Each activity introduces **one** new lever, lets attendees feel it, then ends with a small
"your turn" task. The challenge adds just one tuning knob, the release gap, and otherwise
combines levers they have already used.

| Activity | New lever | What it teaches |
|---|---|---|
| 00 Connect | velocity (gentle first knob) | connect, pre-flight, one safe motion |
| 01 Joints & Cartesian | joint sliders, Cartesian moves | reachability, the feasibility fraction |
| 02 Planning scene | obstacle placement | collision-aware planning: the planner avoids only what the scene knows |
| 03 Pick & place | pick/place coords, grip width, heights | the canonical pick → attach → place sequence (stacking is this, raised) |
| Challenge | release gap, velocity | tune a reliable, tall tower; combines pick-place and the scene |

## The challenge

A friendly tallest-standing-stack contest: teams build a tower of cubes, each placed one
block higher than the last, and the tallest tower still standing wins. The notebook builds
the stack from a few knobs. The two that decide standing height are the release gap (too
tight and the place is rejected as a collision, too loose and the cube drops and can
topple) and the velocity (gentler placements settle better). A toppled tower counts only to
the last standing block, so the contest rewards reliable tuning over ambition. Scoring is
facilitator-judged on the final standing height. The scored runs are hardware-only, since
sim has no physics and nothing topples, so sim stations are for practice and tuning.

## Stations and safety

- Each station is a mini-PC running the workshop container; attendees connect by browser
  and install nothing.
- Every station starts in **sim**, where a browser-based 3D view (RViz over noVNC) shows
  the simulated arm and the planning scene. The same box then switches to **hardware** to
  drive the real arm, which becomes the display.
- Keep the **e-stop** reachable at every arm. The red **Stop** button in each panel is a
  soft-stop that cancels the current motion. Motion is velocity-capped, and the planner is
  collision-aware as long as the table and obstacles are in the planning scene.
- Per-station setup, room layout, and recovery procedures are maintained with the workshop
  image and are rendered into this section as they are finalized.

!!! note "Hardware bring-up"
    Before a session, each arm is brought up and validated with a facilitator-only hardware
    check (gripper direction, grip tuning, table clearance, and a full pick-and-place). That
    runbook ships with the workshop repository.
