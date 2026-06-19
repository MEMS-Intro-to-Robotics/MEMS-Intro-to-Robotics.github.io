---
title: Home
hide:
  - toc
---

<div class="toolkit-hero">
  <div class="toolkit-hero__copy">
    <p class="toolkit-kicker">Duke MEMS Robotics Course Website</p>
    <h1>Duke MEMS Robotics Toolkit</h1>
    <p class="toolkit-lede">
      ROS 2 setup guides, lab manuals, and technical references for simulation-first robotics courses.
    </p>
    <div class="toolkit-actions">
      <a class="md-button md-button--primary" href="asee2026/">ASEE 2026 Workshop</a>
      <a class="md-button" href="guides/quick_start/">Launch a Lab Session</a>
      <a class="md-button" href="guides/pymoveit2_api_guide/">Browse the Technical References</a>
      <a class="md-button" href="for-educators/">See the Educator View</a>
    </div>
  </div>
  <div class="toolkit-hero__panel">
    <p class="toolkit-panel__title">Built for</p>
    <ul>
      <li>Students who need to get into a working ROS 2 environment fast</li>
      <li>TAs who need a dependable troubleshooting and reference surface</li>
      <li>Educators who want reusable robotics lab infrastructure and examples</li>
    </ul>
  </div>
</div>

## Explore the site

<div class="grid cards" markdown>

- **ASEE 2026 workshop**

  Start with the [faculty workshop landing page](asee2026/index.md) for the in-room path, take-home simulator, instructor run guide, and adoption package.

- **Start a lab session**

  Use the [Quick Start](guides/quick_start.md) page to get from login to a running course container.

- **Use the post-Lab-4 workflow**

  The [Robot Platform Workflow](guides/robot_platform_lab_workflow.md) page collects the Docker, pane, build, and debugging habits used across the robot-platform labs.

- **Keep a practical cheat sheet open**

  The [Quick Reference](guides/quick_reference.md) page is designed to stay open during lab for Linux, Git, Docker, and ROS 2 commands.

- **Run structured labs**

  Browse all 10 [lab manuals](labs/lab_01.md) — from VM setup and ROS 2 basics through MoveIt 2 manipulation, PID control, and autonomous SLAM exploration.

- **Look up robot-specific details**

  The [Kinova Gen3 Lite + MoveIt 2 guide](guides/kinova_gen3_lite_moveit2_guide.md) and [pymoveit2 API guide](guides/pymoveit2_api_guide.md) cover the deeper technical reference material.

- **Adapt this material for another course**

  The [For Educators](for-educators.md) and [Educator Adoption Guide](educator-adoption.md) pages explain what transfers cleanly and what you should replace first.

- **Maintain the course environments**

  The [Setup Scripts](guides/setup_scripts.md) page explains which machine bootstrap script should own which environment.

- **Jump to recurring fixes**

  The [Troubleshooting](troubleshooting.md) page collects the issues that appear across multiple labs and setup paths.

- **See the whole course at a glance**

  The [Lab Catalog](lab-catalog.md) page summarizes the purpose, stack, and portability of each lab.

</div>

## What this toolkit contains

- Shared setup guidance for student VMs, developer VMs, and lab desktops
- Course-facing quick references for Linux, Git, Docker, and ROS 2
- Ten complete lab manuals covering VM setup, ROS 2 CLI, shell scripting, Python nodes, MoveIt 2, pick-and-place, PID control, hardware validation, SLAM, and autonomous exploration
- Lab-specific starter assets for Kinova manipulation and 3D goal control
- Reference material suitable for handouts, troubleshooting, and external instructor reuse
- Adoption-oriented pages for instructors evaluating how portable each lab is

## Suggested reading paths

### Students

1. Start with [Quick Start](guides/quick_start.md).
2. If you are in Lab 05 or later, keep [Robot Platform Workflow](guides/robot_platform_lab_workflow.md) open while you work.
3. Keep [Quick Reference](guides/quick_reference.md) open during lab.
4. Open the lab page you are actively working from.

### Educators and maintainers

1. Read [For Educators](for-educators.md) for reuse and adaptation guidance.
2. Review the [Educator Adoption Guide](educator-adoption.md) and [Lab Catalog](lab-catalog.md) to scope what you want to reuse.
3. Review [Setup Scripts](guides/setup_scripts.md) to understand the machine assumptions and current public gaps.
4. Use the technical reference pages as the stable public material you can point to from handouts or papers.
