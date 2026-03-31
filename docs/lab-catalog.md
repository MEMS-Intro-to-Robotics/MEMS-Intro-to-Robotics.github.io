# Lab Catalog

This page summarizes what each lab is trying to teach, what stack it depends on, and how portable it is outside the original course environment.

Portability ratings are practical adoption guidance, not a judgment of lab quality:

- **High** means the learning goals transfer cleanly once you provide a standard ROS 2 environment.
- **Medium** means the lab is reusable but depends on specific starter assets, robot stacks, or heavier setup.
- **Low** means the lab is tightly coupled to local infrastructure, staffing, or live hardware operations.

## Lab matrix

| Lab | Core outcome | Main stack | Portability | Notes |
|---|---|---|---|---|
| **Lab 01** | Student onboarding into Linux, Git, Docker, and ROS 2 workflow | VM access, FastX, Docker, Git, ROS 2 | Low | Strong onboarding pattern, but currently tied to Duke VCM, FastX, and course-specific account setup |
| **Lab 02** | Learn ROS 2 CLI concepts with `turtlesim` | `base-jazzy` image, ROS 2 CLI, `turtlesim` | High | Good first reusable ROS 2 lab once infrastructure references are swapped |
| **Lab 03** | Automate robot behavior with shell scripts | `base-jazzy`, topics, services, `turtlesim`, Git | High | Transfers cleanly to nearly any intro ROS 2 environment |
| **Lab 04** | Build ROS 2 Python nodes and workspaces | `base-jazzy`, `ament_python`, topics, subscriptions | High | One of the most portable labs in the set |
| **Lab 05** | Use MoveIt 2 and RViz for Kinova motion planning | `kinova-jazzy`, Gazebo, RViz, MoveIt 2, `pymoveit2` | Medium | Excellent public reference value, but depends on the Kinova stack and a heavier simulation image |
| **Lab 06** | Implement pick-and-place logic and planning-scene workflows | Kinova sim, MoveIt 2, lab starter script, block spawner | Medium | Reusable, but current public packaging still points to externally hosted starter files |
| **Lab 07** | Tune a 3D PID controller in simulation | Crazyflie sim, ROS 2 Python nodes, plotting workflow | Medium | Strong controls lab, but current public repo documents the files more than it bundles them |
| **Lab 08** | Analyze real hardware controller performance from logged flight data | Staff-run hardware flight, CSV analysis, notebook or script tooling | Low | Useful as a validation lab, but depends on local operations and baseline data packaging |
| **Lab 09** | Build frontier-based exploration in simulation | TurtleBot 4 sim, SLAM, Nav2, Gazebo, RViz | Medium | Strong autonomy capstone with good transfer potential if you already support the TurtleBot 4 sim stack |
| **Lab 10** | Deploy exploration logic on real TurtleBot 4 hardware | Shared lab PCs, robot networking, SLAM, Nav2, RViz | Low | High instructional value, but tightly coupled to local hardware operations and supervision |

## Suggested prerequisite ladder

Use this when mixing and matching labs into a smaller course module:

1. Labs 02-04 for ROS 2 fundamentals
2. Lab 05 before Lab 06
3. Lab 07 before Lab 08
4. Lab 09 before Lab 10

Lab 01 is best treated as an environment template rather than a mandatory public reuse target.

## Best adoption bundles

### Portable ROS 2 core

- Labs 02-04
- Optional extension: Lab 05

### Simulation-first manipulation sequence

- Labs 04-06

### Controls sequence

- Labs 07-08 if you can provide either live flight support or a curated analysis dataset

### Mobile autonomy sequence

- Lab 09 in simulation
- Lab 10 only when you have real TurtleBot 4 support

## Public packaging notes

- Labs 06 and 07 currently expose their workflows publicly, but the actual starter scripts are still fetched from course toolkit links referenced inside the lab manuals.
- The setup-script guide documents environment ownership, but the scripts themselves are not currently tracked in this repository.
- Several labs still rely on placeholder images because the original Canvas-hosted screenshots were removed during public export.

## Related pages

- [Educator Adoption Guide](educator-adoption.md)
- [For Educators](for-educators.md)
- [Troubleshooting](troubleshooting.md)
