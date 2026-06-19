---
title: Adopt This Workshop
---

# Adopt this workshop

Use this page if you want to run the ASEE activity at your own institution or turn it
into a short robotics module.

## What transfers cleanly

- The notebook sequence: connect, joint motion, Cartesian motion, planning scene, pick-and-place, challenge.
- The scaffolding pattern: participants use labeled controls first, then can inspect or edit Python.
- The simulator path: the same notebooks run without a physical arm.
- The teaching arc: each activity adds one new lever and ends with a small "your turn" task.

## What you need to provide

| Area | Minimum requirement |
|---|---|
| Student machines | Docker-capable laptops or lab machines for simulator mode |
| Hardware session | One supported arm per station, with an e-stop and supervised workspace |
| Network | Stable access between each station container and its robot controller |
| Staff | One facilitator who can recover ROS 2 / MoveIt issues and enforce safety |
| Materials | Table cards or local instructions with each station URL and recovery contact |

## What is Duke-specific

- The exact workshop station setup and table-card details.
- Hardware IP addresses, `ROS_DOMAIN_ID` values, and room layout.
- Any facilitator-only recovery file packaged with the workshop image.
- Local safety procedures for the physical arms.

Replace those pieces first. The notebook sequence and simulator path are the portable core.

## Adoption paths

| Path | Best fit | What to change |
|---|---|---|
| **One-session faculty workshop** | Professional development, outreach, ASEE-style sessions | Keep the notebooks heavily scaffolded; replace station setup and room logistics |
| **Two-week manipulation module** | Intro robotics course with simulation-first labs | Pair this workshop with Lab 05 and Lab 06 so students later write more of the code |
| **Hardware practicum** | Course with a shared Kinova or similar arm | Keep the challenge, add stricter pre-lab safety and station qualification checks |
| **No-hardware module** | Programs without a robot arm | Run simulator mode and assess planning-scene reasoning rather than tower stability |

## Pedagogical pattern

The workshop starts with high scaffolding on purpose. Faculty see the full manipulation
loop in one sitting: connect, command, plan, avoid collisions, grasp, attach, place, and
compete. In the full Duke MEMS course, that scaffolding is gradually removed. Students
move from panels to scripts to their own ROS 2 nodes.

That progression is the reusable idea: use the workshop to make the system visible, then
use the labs to make students responsible for pieces of the system.

## First changes to make in a fork

1. Replace the station setup instructions with your own hardware and network details.
2. Decide whether participants will use hardware, simulator mode, or both.
3. Replace the challenge scoring rules if your robot, gripper, or blocks differ.
4. Add your institution's safety policy and facilitator recovery steps.
5. Link the workshop to your own LMS, GitHub Classroom, or submission process if you turn it into a graded activity.

## Good assessment prompts

- Explain why the planner avoids an obstacle only after it is added to the planning scene.
- Compare a joint-space move with a Cartesian move that fails because the feasibility fraction is low.
- Describe what "attaching" a block tells MoveIt after the gripper closes.
- Explain why a cube layout that works in simulation may still fail physically.
- Identify which parts of the workshop are scaffolding and which concepts students should eventually implement themselves.
