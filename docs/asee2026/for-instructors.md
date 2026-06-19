---
title: For Instructors
---

# For Instructors

This page is the run guide for facilitating the workshop. The attendee experience is
meant to be **self-service**: people should know what to do from the notebooks and this
site alone. Your job is to set up the stations, keep the arms safe, and judge the
challenge, not to lecture.

## Design

Attendees never write ROS code. They turn labeled knobs (ipywidgets) that map to meaningful
robot behavior, and the `workshop_core` helper package owns all the ROS 2 and MoveIt
integration underneath. Those who want to go further can drop into Python and extend it.

## Room flow

| Time | Segment | Facilitator job |
|---|---|---|
| 0:00-0:10 | Arrival and station check | Get everyone into JupyterLab and confirm the first pre-flight runs |
| 0:10-0:30 | 00 Connect | Keep first motion slow, visible, and boring |
| 0:30-0:55 | 01 Joints & Cartesian | Ask people to predict which Cartesian moves will fail before they press Execute |
| 0:55-1:20 | 02 Planning scene | Emphasize that the planner avoids only objects in the scene |
| 1:20-1:55 | 03 Pick & place | Give teams time to tune grip and height, one variable at a time |
| 1:55-2:25 | Challenge | Judge standing height and enforce station safety |
| 2:25-2:30 | Wrap | Point educators to [Materials](materials.md), [Adopt This Workshop](adopt.md), and [Sandbox](99_sandbox.md) |

The exact timing can flex, but do not rush `00_connect`. A calm first motion buys trust
for the rest of the session.

## The knob ladder

Each activity introduces **one** new lever, lets attendees feel it, then ends with a small
"your turn" task. The challenge adds no new control: teams place their own cubes and enter
coordinates, combining the skills from 00 to 03.

| Activity | New lever | What it teaches |
|---|---|---|
| 00 Connect | velocity (gentle first knob) | connect, pre-flight, one safe motion |
| 01 Joints & Cartesian | joint sliders, Cartesian moves | reachability, the feasibility fraction |
| 02 Planning scene | obstacle placement | collision-aware planning: the planner avoids only what the scene knows |
| 03 Pick & place | pick/place coords, grip width, heights | the canonical pick → attach → place sequence (stacking is this, raised) |
| Challenge | cube coordinates (team-placed) | spatial planning: lay out reachable, well-spaced cubes and stack them |

## The challenge

A friendly tallest-standing-stack contest. Teams place their own cubes inside a marked zone
on the table, measure and type each cube's (x, y), and the arm picks every cube and stacks
them into one tower. The tallest tower still standing wins. There are no sliders: the work
is spatial. Teams choose reachable, well-spaced coordinates, because with the gripper
orientation fixed, cubes set too close get rejected as collisions, and a tower from sloppy
coordinates leans and falls. A toppled tower counts only to the last standing cube, so a
clean four-cube stack beats an ambitious six that collapses. Scoring is facilitator-judged
on the final standing height. The scored runs are hardware-only, since sim has no physics,
so sim stations are for practice.

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

## Sunday morning checklist

| Check | What "ready" looks like |
|---|---|
| Station URLs | Every table has a JupyterLab URL attendees can open |
| Container mode | Sim stations start in simulator mode; hardware stations have `WORKSHOP_MODE=hardware` and the right `ROBOT_IP` |
| Pre-flight | `00_connect` shows PASS rows after one retry at most |
| Arm state | Each arm starts clear, slow, and reachable from the e-stop |
| Planning scene | Table and challenge objects appear where expected |
| Challenge supplies | Cubes, measuring tools, and marked placement zones are at each station |
| Fallback | At least one simulator-only path is ready if a hardware station drops out |

## Common room failures

| Symptom | Likely cause | First move |
|---|---|---|
| Pre-flight row is red | DDS discovery, wrong robot IP, or station not fully started | Re-run pre-flight once, then check station card values |
| Arm does not move after a valid command | Controller stack is not ready or a prior goal is stale | Run `arm.reset()` and retry the simplest `retract()` |
| Cartesian move refuses to execute | Low feasibility fraction near a singularity or joint limit | Send the arm to the non-singular pose, then try a smaller move |
| Planner drives through a fixture in simulation | Collision object is missing from the planning scene | Re-run the planning-scene cell and verify the object appears |
| Block slips or gripper faults | Grip width or place height is off | Change one value at a time and repeat the single-block pick |
| Challenge stack falls | Coordinates are noisy or cubes are too close | Count the last standing cube, then let the team adjust layout |

## What to say to educators

This workshop is intentionally more scaffolded than the student labs. The point is to let
faculty experience the full hardware integration loop quickly, then show where the full
course asks students to take ownership:

| Workshop layer | Full-course version |
|---|---|
| Sliders and buttons | Students write ROS 2 Python nodes |
| Helper-owned MoveIt calls | Students inspect and modify MoveIt scripts |
| Prebuilt planning scene | Students add and update collision objects |
| Guided challenge | Students debug sequencing, geometry, and failure modes |

That contrast is worth naming out loud. It turns the workshop from a demo into a teaching
model: show the system first, then remove scaffolding with intent.
