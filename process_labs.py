"""Process 2026 lab HTML files for the public website.

Strips:
- Instructor/professor headers
- Deliverables sections
- Submission checklists
- Grading rubrics
- TOC links to removed sections

Also applies public-site rewrites that keep shared cross-lab references in one
place instead of repeating the same material inside every generated lab page.
"""

import argparse
import re
import sys
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_LABS_SRC = REPO_ROOT.parent / "intro-to-robotics-labs" / "2026_fall_labs"
DEFAULT_LABS_DST = REPO_ROOT / "docs" / "labs"

LAB_TITLES = {
    1: "VM and Git Setup",
    2: "ROS 2 CLI Fundamentals",
    3: "Shell Scripting for Robot Control",
    4: "ROS 2 Python Nodes",
    5: "Motion Planning with MoveIt 2",
    6: "Pick-and-Place Manipulation",
    7: "Crazyflie PID Tuning",
    8: "Real Hardware Drone Control",
    9: "Autonomous SLAM-Based Exploration",
    10: "Real TurtleBot 4 Deployment",
}

# Section IDs to remove entirely (opening <section id="..."> to </section>)
REMOVE_SECTION_IDS = {
    "deliverables", "deliverables-glance", "checklist",
}

LAB4_APPENDIX_SHARED_REFS = dedent(
    """
    <section id="appendix">
        <h2>Appendix: Shared References</h2>
        <p>This lab now points to shared reference pages instead of maintaining a lab-specific embedded copy.</p>
        <ul>
            <li><strong><a href="../guides/ros2_python_nodes_reference/">Use the ROS 2 Python Nodes Reference</a></strong> for the <code>main()</code> pattern, publishers, subscribers, timers, messages, logging, and common Lab 4 mistakes.</li>
            <li><strong><a href="../guides/quick_reference/">Use the Quick Reference page</a></strong> for package creation, build/source reminders, ROS 2 CLI checks, Git commands, and Docker commands.</li>
            <li><strong><a href="../troubleshooting/">Use the Troubleshooting page</a></strong> when package discovery, workspace sourcing, container GUI, or cross-terminal environment issues break the workflow.</li>
        </ul>
        <p>Keep the ROS 2 Python nodes reference open while implementing Tasks 2-4. It is now the maintained source of truth for the core <code>rclpy</code> patterns used in this lab.</p>
        <p><a href="#toc">&uarr; Back to top</a></p>
    </section>
    """
).strip()

LAB5_PRELAB_SHARED_WORKFLOW = dedent(
    """
    <p>Starting with Lab 05, the repeated platform-lab habits live in the shared <a href="../guides/robot_platform_lab_workflow/">Robot Platform Lab Workflow</a>. Keep that guide open if you need a refresher on the one-container rule, pane roles, build/source habits, or fast debugging checks.</p>
    <h3>Step 1: Pull the Docker Image</h3>
    <p>On your <strong>host machine</strong>, pull the Kinova image for this lab.</p>
    <pre><code>docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
    <h3>Step 2: Start the ROS 2 Container</h3>
    <p>On your host machine, allow GUI forwarding and start the single container you will use for the whole lab.</p>
    <pre><code>xhost +local:docker</code></pre>
    <pre><code>docker run --rm -it \\
      --net=host \\
      -e DISPLAY=$DISPLAY \\
      -v /tmp/.X11-unix:/tmp/.X11-unix \\
      -v ~/workspaces:/workspaces \\
      --name ros2_lab \\
      gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest bash</code></pre>
    <p>Once your prompt changes (for example, to <code>root@hostname:/#</code>), you are inside the container.</p>
    <h3>Step 3: Launch Your Command Center (Terminator)</h3>
    <p>Inside the container, launch Terminator so you can keep the simulator, MoveIt, and your development pane alive side by side.</p>
    <pre><code>terminator &amp;</code></pre>
    <p>Use the first three panes as follows: <strong>Pane A</strong> for Gazebo, <strong>Pane B</strong> for MoveIt/RViz, and <strong>Pane C</strong> for your build/run workflow.</p>
    """
).strip()

LAB5_MOVEIT_STEP = dedent(
    """
    <h3>Step 5: Open a New Terminal Pane and Launch MoveIt</h3>
    <p>Open a second pane in Terminator (<code>Ctrl+Shift+O</code> or <code>Ctrl+Shift+E</code>). In that new pane, source ROS and launch MoveIt:</p>
    <ol>
        <li>
            <pre><code>source /opt/ros/jazzy/setup.bash</code></pre>
        </li>
        <li>
            <pre><code>ros2 launch kinova_gen3_lite_moveit_config sim.launch.py \\
      use_sim_time:=true</code></pre>
        </li>
    </ol>
    <p>An RViz window should open. Keep Pane A and Pane B running while you work through the rest of the lab.</p>
    """
).strip()

LAB5_SHARED_REFERENCES = dedent(
    """
    <h1>Shared References</h1>
    <p>This lab now points to shared reference pages instead of embedding large appendices directly in the handout.</p>
    <ul>
        <li><strong><a href="../guides/pymoveit2_api_guide/">Use the <code>pymoveit2</code> API guide</a></strong> for the node/executor pattern, gripper interface, collision objects, Cartesian planning, and quick API signatures.</li>
        <li><strong><a href="../guides/kinova_gen3_lite_moveit2_guide/">Use the Kinova Gen3 Lite + MoveIt 2 guide</a></strong> for planning groups, controller bringup, RViz checks, and controller troubleshooting.</li>
        <li><strong><a href="../guides/quick_reference/">Use the Quick Reference page</a></strong> for the ROS 2 CLI, build/source reminders, package layout, and common Docker commands.</li>
        <li><strong><a href="../troubleshooting/">Use the Troubleshooting page</a></strong> when package discovery, workspace sourcing, MoveIt, controllers, or container GUI issues block progress.</li>
    </ul>
    <p>For this lab in particular, keep the Kinova and <code>pymoveit2</code> guides open while implementing Milestones 3 and 4. They are the maintained source of truth for controller checks, gripper wiring, and planning-scene inspection.</p>
    """
).strip()

LAB6_PRELAB_SHARED_WORKFLOW = dedent(
    """
    <p>From this point in the course onward, the repeated Docker, panes, build, and debugging habits live in the shared <a href="../guides/robot_platform_lab_workflow/">Robot Platform Lab Workflow</a>. This section only lists the Lab 06-specific commands and checks.</p>
    <h2>3.1 Update Your Course Repository</h2>
    <p>On your host VM, make sure your local course repo is current.</p>
    <pre><code class="language-bash"># Navigate to your main robotics workspace
    cd ~/workspaces/[netid]_robotics_fall2025

    # Pull the latest changes from the main branch
    git pull
    </code></pre>
    <h2>3.2 Pull the Docker Image</h2>
    <p>Pull the Kinova image used for this lab.</p>
    <pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
    <h2>3.3 Optional: Enable GPU Acceleration (Run Once Per VM)</h2>
    <p>If Gazebo or RViz performance is poor, run the GPU setup script once on your host VM.</p>
    <pre><code class="language-bash">cd ~
    curl -L "https://raw.githubusercontent.com/MEMS-Intro-to-Robotics/mems-robotics-toolkit/main/gpu_install.sh" -o gpu_install.sh
    chmod +x gpu_install.sh
    ./gpu_install.sh
    </code></pre>
    <p>If the script fails because you're not in the <code>docker</code> group, run this command, then log out and log back into your VM for the change to take effect:</p>
    <pre><code class="language-bash">sudo usermod -aG docker "$USER"
    </code></pre>
    <p>If you don't have a GPU, you can omit the <code>--gpus all</code> flag later, but you may need to enable software rendering if you see OpenGL errors by running <code>export LIBGL_ALWAYS_SOFTWARE=1</code> inside the container.</p>
    <h2>3.4 Start the ROS 2 Container</h2>
    <p>On your host VM, allow GUI forwarding and start the single container for this lab.</p>
    <pre><code class="language-bash">xhost +local:docker

    docker run --rm -it \\
      --net=host \\
      -e DISPLAY=$DISPLAY \\
      -v /tmp/.X11-unix:/tmp/.X11-unix \\
      -v ~/workspaces:/workspaces \\
      --gpus all \\
      --name ros2_lab06 \\
      gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest \\
      bash</code></pre>
    <h2>3.5 Launch Terminator and Create the Lab 6 Workspace</h2>
    <p>Inside the container, launch Terminator and create the directory structure for this lab.</p>
    <pre><code class="language-bash">terminator &amp;

    # In a pane inside the container
    # The [netid]_robotics_fall2025 folder should already exist
    cd /workspaces/[netid]_robotics_fall2025
    mkdir -p lab06/docs lab06/ros2_ws/src
    </code></pre>
    <h2>3.6 Recommended Pane Layout</h2>
    <ul>
        <li><strong>Pane A</strong>: Gazebo simulation for the Kinova Gen3 Lite.</li>
        <li><strong>Pane B</strong>: MoveIt and RViz for motion planning.</li>
        <li><strong>Pane C</strong>: Your development environment for building and running your Python node.</li>
        <li><strong>Pane D</strong>: Scripts for spawning objects into Gazebo.</li>
    </ul>
    <h2>3.7 Ready for Lab Checklist</h2>
    <p>You are ready to begin the <strong>Lab Procedure</strong> when you can say "yes" to all of the following:</p>
    <ul>
        <li>I have successfully run <code>git pull</code> in my course repository on the <strong>host</strong>.</li>
        <li>I have started <strong>one</strong> container and it is named <code>ros2_lab06</code>.</li>
        <li>I have launched <strong>Terminator inside the container</strong> and can open multiple panes.</li>
        <li>My Lab 6 directory structure exists at <code>/workspaces/[netid]_robotics_fall2025/lab06/</code>.</li>
    </ul>
    <hr />
    """
).strip()

LAB7_PRELAB_SHARED_WORKFLOW = dedent(
    """
    <p>You will work entirely in <strong>simulation</strong> inside the provided Docker container. This pre-lab ensures your environment is correctly configured. The main steps are to (1) update your local course repository, (2) pull the latest Docker image, (3) launch the simulator, and (4) verify that all tools and ROS 2 topics are functioning correctly before you begin the lab procedure.</p>
    <p>The repeated post-Lab-4 workflow now lives in the shared <a href="../guides/robot_platform_lab_workflow/">Robot Platform Lab Workflow</a>. Use that page for the one-environment rule, pane roles, build/source habits, and fast debugging checks. This pre-lab keeps only the Crazyflie-specific commands.</p>
    <h2>Step 1: Setup the Host Environment</h2>
    <p>Run these commands on your host VM.</p>
    <h3>3.1 Update Your Course Repository</h3>
    <p>Ensure you have the latest lab files by pulling the latest changes from the course repository.</p>
    <pre><code class="language-bash">cd ~/workspaces/[netid]_robotics_fall2025
    git pull
    </code></pre>
    <h3>3.2 Pull the Docker Image</h3>
    <p>Pull the Crazyflie image for this lab.</p>
    <pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:crazyflie-jazzy-latest
    </code></pre>
    <h3>3.3 Configure GUI (X11) Forwarding</h3>
    <p>Allow Docker to open Gazebo windows on your host display.</p>
    <pre><code class="language-bash"># This command allows local clients (like Docker containers) to open windows on your host.
    xhost +local:
    </code></pre>
    <h2>Step 2: Launch and Verify the Container</h2>
    <h3>3.4 Start the Lab Container</h3>
    <p>Start one persistent container named <code>lab07</code>. Use the GPU option if available. If you need another shell later, reuse this same container with <code>docker start -ai lab07</code> or <code>docker exec -it lab07 bash</code>.</p>
    <h4>Option A: With NVIDIA GPU Acceleration (Recommended)</h4>
    <pre><code class="language-bash"># --name lab07:       Assigns a reusable name to the container.
    # --gpus all:         Grants the container access to the host's NVIDIA GPUs.
    # --network host:     Allows the container to share the host's network (for ROS 2).
    # -e DISPLAY=$DISPLAY: Passes the host's display variable for GUI forwarding.
    # -v [host]:[guest]:  Mounts your local workspace folder into the container. You can change this to wherever you want your files mounted

    docker run -it --name lab07 --gpus all \\
      --network host \\
      -e DISPLAY=$DISPLAY \\<br />  -e GZ_SIM_RESOURCE_PATH=/opt/cf_lab_ws/simulation_ws/crazyflie-simulation \\<br />  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \\
      -v ~/workspaces:/root/workspaces/ \\
      gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:crazyflie-jazzy-latest
    </code></pre>
    <h4>Option B: With CPU-Based Software Rendering</h4>
    <pre><code class="language-bash">docker run -it --name lab07 \\
      --network host \\
      -e DISPLAY=$DISPLAY \\<br /> &nbsp;-e GZ_SIM_RESOURCE_PATH=/opt/cf_lab_ws/simulation_ws/crazyflie-simulation \\<br /> &nbsp;-v /tmp/.X11-unix:/tmp/.X11-unix:ro \\
      -v ~/workspaces:/root/workspaces \\
      gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:crazyflie-jazzy-latest
    </code></pre>
    <p><strong>To re-enter your container later:</strong> If you exit the container, you can resume your session without losing any data using <code>docker start -ai lab07</code>.</p>
    <h3>3.5 Perform Initial Environment Checks</h3>
    <p>Once inside the container, run these quick checks to confirm the environment is set up.</p>
    <pre><code class="language-bash"># Check that the ROS 2 distribution is set correctly
    echo "ROS_DISTRO=$ROS_DISTRO"
    # Expected output: jazzy

    # Verify that key Python libraries are installed
    python3 -c "import matplotlib, numpy; print('Matplotlib/Numpy OK')"
    </code></pre>
    """
).strip()

LAB9_SETUP_SHARED_WORKFLOW = dedent(
    """
    <section id="setup">
        <h2>5. Environment Setup: Docker &amp; Simulation</h2>
        <p>From Lab 05 onward, the shared <a href="../guides/robot_platform_lab_workflow/">Robot Platform Lab Workflow</a> covers the repeated container, pane, build, and debugging habits. This section keeps the Lab 09-specific pieces: the TurtleBot image, the permissions fix, and the bringup commands that follow.</p>
        <h3>5.1 Start the Container (GPU Acceleration)</h3>
        <p>On your <strong>host VM</strong>, allow GUI forwarding and start the single container for this lab.</p>
        <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>xhost +local:docker</code></pre>
        <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>docker run --rm -it \\
    --name lab09_tb4 \\
    --net=host \\
    -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \\
    -v ~/workspaces:/root/workspaces \\
    --gpus all \\
    gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:tb4-humble-latest</code></pre>
        <p>Note: if the command above does not successfully install all required packages, free up storage by running this command:</p>
        <p><strong></strong><code>docker system prune -a --volumes -f</code></p>
        <h3>5.2 Fix File Permissions When Needed</h3>
        <p>If files created inside the container become read-only on the host, run this from a second host terminal:</p>
        <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>sudo chown -R $USER:$USER ~/workspaces/[netid]_robotics_fall2025/lab09</code></pre>
        <h3>5.3 Recommended Pane Layout</h3>
        <p>If you prefer panes inside the container, open Terminator after launch and use a layout like this:</p>
        <ul>
            <li><strong>Pane A</strong>: Gazebo world</li>
            <li><strong>Pane B</strong>: TurtleBot stack with SLAM, Nav2, and RViz</li>
            <li><strong>Pane C</strong>: Laser bridge</li>
            <li><strong>Pane D</strong>: Development and debugging</li>
        </ul>
        <h3>5.4 Fallback: CPU Rendering</h3>
        <p>If you encounter graphics errors, use the Docker command from Step 5.1 but <strong>omit the <code>--gpus all</code> line</strong>. You can still use the same <code>chown</code> command from Step 5.2 in a second terminal to manage file permissions.</p>
    </section>
    """
).strip()


def remove_header_block(html: str) -> str:
    """Remove <header>...</header> blocks."""
    return re.sub(r'<header>\s*.*?</header>\s*', '', html, flags=re.DOTALL)


def remove_lab7_course_info(html: str) -> str:
    """Remove the course info paragraph from lab 7's format."""
    # Pattern: <div class="lab-manual-container"> followed by <p>Course: ECE 383...
    pattern = (
        r'(<div class="lab-manual-container">)\s*'
        r'<p>Course:.*?</p>\s*'
    )
    return re.sub(pattern, r'\1\n', html, flags=re.DOTALL)


def remove_sections_by_id(html: str) -> str:
    """Remove <section id="deliverables|checklist|...">...</section> blocks."""
    for section_id in REMOVE_SECTION_IDS:
        pattern = rf'<section id="{section_id}">\s*.*?</section>\s*'
        html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_h1_deliverables_sections(html: str) -> str:
    """Remove deliverables sections that use <h1> headings (labs 5, 6).

    Removes from <h1>Deliverables...</h1> to the next <h1> or end of content.
    """
    # Match <h1> containing "Deliverables" through to next <h1> or end
    # Handle both "Deliverables" standalone sections
    patterns = [
        # <h1>Deliverables...</h1> to next <h1> or end
        r'<h1>[^<]*Deliverables[^<]*</h1>.*?(?=<h1>|\Z)',
        # <h1 id="sec-4">4. Deliverables</h1> style
        r'<h1 id="sec-\d+">\d+\.\s*Deliverables[^<]*</h1>.*?(?=<h1|\Z)',
    ]
    for pattern in patterns:
        html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_h3_deliverables_checklist(html: str) -> str:
    """Remove <h3>Deliverables Checklist</h3> subsections (lab 5)."""
    pattern = r'<h3>Deliverables Checklist</h3>.*?(?=<h[123]>|<h1|</div>\s*$|\Z)'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_toc_links(html: str) -> str:
    """Remove TOC entries linking to removed sections."""
    # Remove <li> entries containing links to deliverables, checklist, submission
    patterns = [
        r'\s*<li><a href="#deliverables[^"]*">[^<]*</a></li>',
        r'\s*<li><a href="#checklist">[^<]*</a></li>',
        # Also from sec-4 style TOC (lab 7 deliverables)
        r'\s*<li><a href="#sec-4">4\. Deliverables</a></li>',
    ]
    for pattern in patterns:
        html = re.sub(pattern, '', html)
    return html


def remove_grading_rubric(html: str) -> str:
    """Remove grading rubric subsections."""
    # <h3>6.2 Grading Rubric...</h3> to next <h2>|<h1>|</section>|end
    pattern = r'<h3>[^<]*Grading Rubric[^<]*</h3>.*?(?=<h[12]>|</section>|\Z)'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_submission_grading_section(html: str) -> str:
    """Remove 'Submission & Grading' sections (lab 10)."""
    pattern = r'<section id="checklist">\s*<h2>[^<]*Submission[^<]*Grading[^<]*</h2>.*?</section>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def require_sub(html: str, pattern: str, replacement: str, label: str, *, flags: int = re.DOTALL) -> str:
    """Replace a pattern exactly once, or fail loudly if the source drifted."""
    updated, count = re.subn(pattern, replacement, html, count=1, flags=flags)
    if count != 1:
        raise ValueError(f"{label}: expected 1 replacement, found {count}")
    return updated


def require_replace(html: str, old: str, new: str, label: str) -> str:
    """Replace an exact snippet once, or fail loudly if the source drifted."""
    if old not in html:
        raise ValueError(f"{label}: expected snippet not found")
    return html.replace(old, new, 1)


def apply_lab4_shared_references(html: str) -> str:
    """Replace Lab 4's embedded appendix with the shared reference page."""
    html = require_replace(
        html,
        '<li><a href="#appendix">Appendix: ROS 2 Python API Reference</a></li>',
        '<li><a href="#appendix">Appendix: Shared References</a></li>',
        "lab04 toc appendix",
    )
    html = require_replace(
        html,
        '<li>Utilize the <strong>Appendix section</strong> at the bottom of this document for more information about the ROS 2 functions you will use</li>',
        '<li><strong><a href="../guides/ros2_python_nodes_reference/">Use the ROS 2 Python Nodes Reference</a></strong> for more information about the ROS 2 functions you will use</li>',
        "lab04 appendix hint",
    )
    html = require_sub(
        html,
        r'<section id="appendix">\s*<h2>Appendix: ROS 2 Python API Reference</h2>.*?</section>',
        LAB4_APPENDIX_SHARED_REFS,
        "lab04 appendix section",
    )
    return html


def apply_lab5_shared_references(html: str) -> str:
    """Replace Lab 5's repeated setup prose and giant appendices with shared references."""
    html = require_sub(
        html,
        r'<p>This section walks you through preparing your environment\..*?(?=<h3>Step 4: Launch the Kinova Simulation in Gazebo</h3>)',
        LAB5_PRELAB_SHARED_WORKFLOW + "\n",
        "lab05 shared prelab",
    )
    html = require_sub(
        html,
        r'<h3>Step 5: Open a New Terminal Pane and Launch MoveIt</h3>.*?(?=<h3>Step 6: Final Checks and Familiarization</h3>)',
        LAB5_MOVEIT_STEP + "\n",
        "lab05 moveit step",
    )
    html = require_replace(
        html,
        '<li><strong>Read Appendix A:</strong> Skim the appendix on controlling the gripper to prepare for using it in the lab.</li>',
        '<li><strong>Skim the shared references:</strong> Review the gripper and controller sections in the public <code>pymoveit2</code> and Kinova guides before starting the milestones.</li>',
        "lab05 appendix reminder",
    )
    html = require_replace(
        html,
        '# TODO: Open/close the gripper using self.gripper (Appendix A).',
        '# TODO: Open/close the gripper using self.gripper (see shared pymoveit2 guide).',
        "lab05 gripper comment",
    )
    html = require_sub(
        html,
        r'<h1>Appendix A &mdash; Reference for <code>pymoveit2</code> \(conceptual \+ API guide\)</h1>.*\Z',
        LAB5_SHARED_REFERENCES,
        "lab05 shared references block",
    )
    return html


def apply_lab6_shared_workflow(html: str) -> str:
    """Replace Lab 6's repeated setup tutorial with the shared workflow pointer."""
    html = require_sub(
        html,
        r'<p>This section guides you through setting up the exact environment needed for the lab\..*?(?=<h1>5 Lab Procedure</h1>)',
        LAB6_PRELAB_SHARED_WORKFLOW + "\n",
        "lab06 shared prelab",
    )
    return html


def apply_lab7_shared_workflow(html: str) -> str:
    """Replace Lab 7's repeated setup tutorial with the shared workflow pointer."""
    html = require_sub(
        html,
        r'<p>You will work entirely in <strong>simulation</strong> inside the provided Docker container\..*?(?=<h2>Step 3: Launch and Verify the Simulation</h2>)',
        LAB7_PRELAB_SHARED_WORKFLOW + "\n",
        "lab07 shared prelab",
    )
    html = require_replace(
        html,
        '<p>For the following steps, you may want to open a second terminal into the same running container (e.g., using <code>tmux</code>, splitting your terminal, or running <code>docker exec -it lab07 bash</code> from your host) so you can leave the simulation running while you run verification commands.</p>',
        '<p>Leave the simulator running in one shell and use another shell in the same container for checks or later launch commands.</p>',
        "lab07 simulation shell note",
    )
    return html


def apply_lab9_shared_workflow(html: str) -> str:
    """Replace Lab 9's repeated setup prose with the shared workflow pointer."""
    html = require_sub(
        html,
        r'<section id="setup">\s*<h2>5\. Environment Setup: Docker &amp; Simulation</h2>.*?</section>',
        LAB9_SETUP_SHARED_WORKFLOW,
        "lab09 setup section",
    )
    html = require_sub(
        html,
        r'<p>\*\*\*Don.*?change the owner of the directories.*?</p>\s*'
        r'<p>\*\*\*Don.*?source your ROS environment\*\*\*</p>\s*'
        r'<p>Before writing a single line of Python.*?</p>',
        '<p>Create the package in your development pane. If you need the shared explanation of workspaces, <code>colcon build --symlink-install</code>, or when to rebuild versus simply rerun, see the <a href="../guides/robot_platform_lab_workflow/">Robot Platform Lab Workflow</a>.</p>',
        "lab09 project setup intro",
    )
    html = require_sub(
        html,
        r'<ul>\s*<li><strong><code>mkdir -p \.\.\./src</code></strong>:.*?</ul>\s*(?=<hr style="margin: 2em 0;" />)',
        '',
        "lab09 project setup explainer list",
    )
    return html


def apply_lab10_shared_workflow(html: str) -> str:
    """Link Lab 10 back to the shared workflow guide and fix the build note."""
    html = require_replace(
        html,
        '<p>Create a folder on the Lab PC to store your work safely. Open a terminal and run:</p>',
        '<p>Create a folder on the Lab PC to store your work safely. The shared <a href="../guides/robot_platform_lab_workflow/">Robot Platform Lab Workflow</a> still applies here for pane discipline, build/source habits, and fast debugging; the main difference is that Lab 10 also requires network exports in every pane.</p>',
        "lab10 workspace intro",
    )
    html = require_replace(
        html,
        '<p>Now, open a terminal manager (like <code>terminator</code>). A multi-pane layout is standard operational procedure for monitoring distributed systems.</p>',
        '<p>Open a terminal manager such as <code>terminator</code> and reserve the panes below for the rest of the lab.</p>',
        "lab10 pane intro",
    )
    html = require_replace(
        html,
        '<li>[ ] <strong>Build:</strong> <code>colcon build --symlink-install</code> (Do this after <em>every</em> change to the Python file).</li>',
        '<li>[ ] <strong>Build:</strong> <code>colcon build --symlink-install</code> after package metadata, dependency, or entry-point changes. For ordinary edits to an existing Python file, save and rerun.</li>',
        "lab10 build checklist",
    )
    html = require_replace(
        html,
        '<li>[ ] <strong>Source:</strong> <code>source install/setup.bash</code>.</li>',
        '<li>[ ] <strong>Source:</strong> <code>source install/setup.bash</code> in any pane where you want to run the node.</li>',
        "lab10 source checklist",
    )
    return html


def apply_public_site_dedup(html: str, lab_num: int) -> str:
    """Apply shared-reference rewrites that should survive regeneration."""
    if lab_num == 4:
        html = apply_lab4_shared_references(html)
    elif lab_num == 5:
        html = apply_lab5_shared_references(html)
    elif lab_num == 6:
        html = apply_lab6_shared_workflow(html)
    elif lab_num == 7:
        html = apply_lab7_shared_workflow(html)
    elif lab_num == 9:
        html = apply_lab9_shared_workflow(html)
    elif lab_num == 10:
        html = apply_lab10_shared_workflow(html)
    return html


def replace_canvas_images(html: str) -> str:
    """Replace Canvas-hosted images with grey placeholder divs."""
    def make_placeholder(match):
        full_tag = match.group(0)
        # Extract alt text
        alt_match = re.search(r'alt="([^"]*)"', full_tag)
        alt = alt_match.group(1) if alt_match else "Image"
        # Extract width/height if present
        w_match = re.search(r'width="(\d+)"', full_tag)
        h_match = re.search(r'height="(\d+)"', full_tag)
        width = w_match.group(1) if w_match else "400"
        height = h_match.group(1) if h_match else "200"
        # Also check for equation images - keep alt text as-is for context
        if 'equation_image' in full_tag:
            # For LaTeX equations rendered as images, use proper MathJax delimiters
            eq_match = re.search(r'data-equation-content="([^"]*)"', full_tag)
            eq = eq_match.group(1).strip() if eq_match else alt
            # Multi-line or long equations get display mode, short ones inline
            if '\n' in eq or len(eq) > 60:
                # Store LaTeX in data attribute to survive markdown processing
                import html as html_mod
                escaped_attr = html_mod.escape(eq, quote=True)
                return (
                    f'<span class="math-display" '
                    f'data-latex="{escaped_attr}">'
                    f'</span>'
                )
            import html as html_mod
            escaped_attr = html_mod.escape(eq, quote=True)
            return (
                f'<span class="math-inline" '
                f'data-latex="{escaped_attr}">'
                f'</span>'
            )
        # Skip empty alt text placeholders
        if not alt or alt.strip() == "":
            alt = "Image placeholder"
        return (
            f'<div class="image-placeholder" style="'
            f'background:#e0e0e0;border:2px dashed #999;border-radius:8px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'color:#666;font-style:italic;text-align:center;padding:1em;'
            f'max-width:{width}px;min-height:{min(int(height), 150)}px;'
            f'margin:1em auto;">'
            f'{alt}</div>'
        )

    # Match img tags with canvas.duke.edu URLs
    html = re.sub(
        r'<img[^>]*src="https://canvas\.duke\.edu/[^"]*"[^>]*/?>',
        make_placeholder,
        html,
    )
    return html


def redact_secrets(html: str) -> str:
    """Redact license keys and similar credentials before public export."""
    html = re.sub(
        r'FASTX_ACTIVATION_KEY="[^"]*"',
        'FASTX_ACTIVATION_KEY="&lt;key-from-course-staff&gt;"',
        html,
    )
    html = re.sub(
        r'Enter the license key when prompted: <code>[^<]*</code>',
        'Enter the license key provided by course staff when prompted.',
        html,
    )
    # Backstop: never let a FastX-style key (4x4 digit groups) reach the site.
    html = re.sub(r'\b\d{4}-\d{4}-\d{4}-\d{4}\b', '&lt;redacted&gt;', html)
    return html


def clean_lab(html: str, lab_num: int) -> str:
    """Apply all cleaning transformations."""
    # 0. Redact credentials, then replace Canvas-hosted images with placeholders
    html = redact_secrets(html)
    html = replace_canvas_images(html)

    # 1. Remove instructor headers
    html = remove_header_block(html)

    # Lab 7 has a different header format
    if lab_num == 7:
        html = remove_lab7_course_info(html)

    # 2. Remove section-based deliverables/checklists
    html = remove_sections_by_id(html)

    # 3. Remove h1-based deliverables (labs 5, 6)
    if lab_num in (5, 6):
        html = remove_h1_deliverables_sections(html)
        html = remove_h3_deliverables_checklist(html)

    # Lab 7 uses h1 id="sec-4" for deliverables
    if lab_num == 7:
        html = remove_h1_deliverables_sections(html)

    # 4. Remove grading rubrics
    html = remove_grading_rubric(html)

    # 5. Remove TOC links to removed sections
    html = remove_toc_links(html)

    # 6. Remove inline "Deliverables (at a glance)" subsections
    # These are <h4>Deliverables...</h4> followed by lists and notes
    # Consume through any nested lists and trailing blockquotes up to the next
    # heading/section boundary (a lazy <ul>.*?</ul> stops at the first nested
    # </ul> and strands the outer list's tail).
    html = re.sub(
        r'<h4>Deliverables[^<]*</h4>.*?(?=<h[1-6][ >]|<section\b|</section)',
        '', html, flags=re.DOTALL,
    )
    # Also remove "Deliverables At a Glance" as <h1> in labs 5/6 intro areas
    # (already handled by remove_h1_deliverables_sections)

    # 7. Clean up excess whitespace
    html = re.sub(r'\n{3,}', '\n\n', html)

    # 8. Apply public-site dedup so regeneration preserves shared references
    html = apply_public_site_dedup(html, lab_num)
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()


def wrap_in_markdown(html: str, lab_num: int) -> str:
    """Wrap cleaned HTML in a markdown page."""
    title = LAB_TITLES[lab_num]
    return f"""---
title: "Lab {lab_num:02d}: {title}"
---

# Lab {lab_num:02d}: {title}

<div class="lab-content">

{html}

</div>
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--src",
        type=Path,
        default=DEFAULT_LABS_SRC,
        help="Path to the source lab HTML directory",
    )
    parser.add_argument(
        "--dst",
        type=Path,
        default=DEFAULT_LABS_DST,
        help="Path to the destination markdown directory",
    )
    parser.add_argument(
        "--labs",
        type=int,
        nargs="+",
        default=list(range(1, 11)),
        help="Lab numbers to process (default: all)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    labs_src = args.src.resolve()
    labs_dst = args.dst.resolve()

    if not labs_src.exists():
        raise SystemExit(f"Source lab directory not found: {labs_src}")

    labs_dst.mkdir(parents=True, exist_ok=True)

    for lab_num in args.labs:
        src = labs_src / f"lab_{lab_num}.html"
        if not src.exists():
            print(f"WARNING: {src} not found, skipping")
            continue

        html = src.read_text(encoding="utf-8")
        cleaned = clean_lab(html, lab_num)
        md = wrap_in_markdown(cleaned, lab_num)

        dst = labs_dst / f"lab_{lab_num:02d}.md"
        dst.write_text(md, encoding="utf-8", newline="\n")
        print(f"Processed lab {lab_num:02d} -> {dst.name} ({len(html)} -> {len(cleaned)} chars)")

    print("\nDone! All labs processed.")


if __name__ == "__main__":
    main(sys.argv[1:])
