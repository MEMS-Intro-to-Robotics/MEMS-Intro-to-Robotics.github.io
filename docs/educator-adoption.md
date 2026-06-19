# Educator Adoption Guide

Use this page when you want to turn the site into a course, module, or workshop rather than just browse the labs.

## Choose an adoption scope

| Scope | Best for | Recommended labs |
|---|---|---|
| **Simulation-first ROS 2 module** | A short unit that teaches ROS 2 tools, scripting, and Python nodes without requiring specialized hardware | Labs 02-05 |
| **Manipulation and controls extension** | Courses that already teach ROS 2 basics and want more manipulation or controls work | Labs 05-07 |
| **Mobile autonomy extension** | Courses with Nav2, SLAM, or autonomous exploration goals | Lab 09, then Lab 10 if hardware is available |
| **Full sequence** | Programs that can support onboarding, simulation, and multiple hardware platforms | Labs 01-10 |

## Minimum viable platform

If you are building a portable version of this course, define these pieces first:

- A standard student compute environment: Linux workstation, VM, or managed lab machine
- A public image registry for ROS 2 course containers
- One canonical submission workflow: GitHub Classroom, plain GitHub repos, GitLab, or LMS upload
- A reproducible editor and terminal story: VS Code, plain terminal, or remote desktop
- A single documented owner for environment setup and image maintenance

You do not need Duke VCM, FastX, or Duke GitLab to reuse the academic core of the labs.

## Hardware and staffing assumptions

| Area | Needed for | What to plan for |
|---|---|---|
| **General course support** | All offerings | TAs who can debug Docker, Git, Linux, and ROS 2 fundamentals |
| **Kinova manipulation** | Labs 05-06 hardware variants | Safe robot workspace, controller bring-up familiarity, and supervision during motion planning exercises |
| **Crazyflie controls** | Labs 07-08 | Tracking setup or equivalent staff-run flight workflow, plus safety boundaries for live flight |
| **TurtleBot 4 autonomy** | Labs 09-10 | Reliable robot networking, Nav2/SLAM support, and in-room staff during deployment |

If your program is short-staffed, the most practical version is still simulation-only.

## Replace these Duke-specific dependencies first

1. Replace VCM and FastX references with your own workstation or VM onboarding path.
2. Replace Duke GitLab container image names with a public registry you control.
3. Replace GitHub Classroom or course invite flows with your preferred assignment pattern.
4. Mirror starter scripts and machine bootstrap scripts into a public repo under your control.
5. Swap Duke-specific communication, safety, and lab-computer instructions for your own operating procedures.

## Suggested teaching bundles

### Four-lab ROS 2 core

- Lab 02: ROS 2 CLI Fundamentals
- Lab 03: Shell Scripting for Robot Control
- Lab 04: ROS 2 Python Nodes
- Lab 05: Motion Planning with MoveIt 2

This bundle gives students a coherent ROS 2 progression without depending on live hardware.

### Controls and manipulation block

- Lab 05: MoveIt 2 and manipulation foundations
- Lab 06: Pick-and-place workflow
- Lab 07: PID tuning in simulation
- Lab 08: Hardware validation or recorded-data analysis

This works well when you want students to compare planning-heavy and feedback-heavy robotics workflows.

### Mobile autonomy block

- Lab 09: Autonomous SLAM-based exploration in simulation
- Lab 10: Real TurtleBot 4 deployment

Treat Lab 10 as optional unless you already have the hardware and staffing to support it safely.

## Practical improvements if you fork this site

- Mirror starter code into the same public repo as the docs
- Replace placeholder screenshots with local assets or original diagrams
- Split course-specific operating procedures from broadly reusable technical content
- Add a lab metadata table with prerequisites, stack, and expected outputs
- Keep infrastructure setup docs honest about which scripts are actually in-repo

## Related pages

- [For Educators](for-educators.md)
- [Lab Catalog](lab-catalog.md)
- [Troubleshooting](troubleshooting.md)
- [Setup Scripts](guides/setup_scripts.md)
