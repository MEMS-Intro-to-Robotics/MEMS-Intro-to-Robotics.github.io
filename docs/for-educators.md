# For Educators

This site publishes the public-facing lab manuals, setup guides, and technical references for Duke's Introduction to Robotics and Automation course (ECE 383 / ME 555). It is designed to serve two jobs at once:

- give enrolled students a stable technical reference during lab
- give other instructors a reusable starting point for simulation-first robotics teaching

## Start here

If you are evaluating this material for adoption, these three pages will get you oriented fastest:

- [Educator Adoption Guide](educator-adoption.md) for reuse paths, staffing assumptions, and what to replace first
- [Lab Catalog](lab-catalog.md) for a lab-by-lab view of scope, stack, and portability
- [Troubleshooting](troubleshooting.md) for the operational issues that show up repeatedly across labs

## What transfers cleanly

- The overall course arc from environment setup through ROS 2 fundamentals, manipulation, controls, SLAM, and real-hardware validation
- The simulation-first teaching pattern used in Labs 02-07 and Lab 09
- The quick-reference pages for Linux, Git, Docker, ROS 2, MoveIt 2, and `pymoveit2`
- The repeated workflow of containerized ROS 2 workspaces, pane-based debugging, and task-oriented lab scaffolding

## What is still course-specific

Several parts of the current site still assume Duke infrastructure or course operations:

- Student VMs provisioned through [Duke VCM](https://vcm.duke.edu) with FastX
- Docker images hosted in a Duke GitLab registry
- GitHub Classroom or course-managed submission flows
- Hardware labs staffed with shared lab desktops, safety supervision, and local network conventions
- Starter scripts and machine-setup scripts that are referenced from course infrastructure outside this repository

If you are adapting this for another institution, infrastructure replacement is the first step, not lab rewriting.

## Recommended reuse tiers

| Tier | Best use | Labs |
|---|---|---|
| **Fastest adoption** | Simulation-only ROS 2 module | Labs 02-05 |
| **Add controls and autonomy** | Broader simulation course or short robotics sequence | Labs 02-07 and Lab 09 |
| **Full local course** | Programs with matched hardware, staffing, and support infrastructure | Labs 01-10 |

## Current public gaps

This repository already contains substantial public course material, but a few supporting assets are not yet mirrored here:

- Lab 06 and Lab 07 starter files are documented here, but the actual scripts are still fetched from course toolkit links referenced in the lab manuals
- The machine bootstrap scripts described in the setup documentation are not currently versioned in this repository
- Some labs still contain placeholder images where the original Canvas-hosted screenshots were removed during public publishing

Those gaps do not reduce the teaching value of the written material, but they do matter for outside adoption.

## Using and citing this material

This material is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to use, adapt, and redistribute it, provided you give appropriate credit. If you reference it in a publication, the following citation format is suggested:

> Kusa, E. (2026). *MEMS Intro to Robotics: Open Lab Manuals and Technical References for Simulation-First Robotics Teaching.* Available at [https://mems-intro-to-robotics.github.io](https://mems-intro-to-robotics.github.io).

For adapted course materials, a brief attribution (e.g., "Based on materials by Evan Kusa, Duke University") is sufficient to satisfy the license. Questions and feedback are welcome via the [GitHub repository](https://github.com/MEMS-Intro-to-Robotics/MEMS-Intro-to-Robotics.github.io).
