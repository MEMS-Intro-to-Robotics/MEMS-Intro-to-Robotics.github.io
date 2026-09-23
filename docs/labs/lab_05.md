---
title: "Lab 05: Motion Planning with MoveIt 2"
---

# Lab 05: Motion Planning with MoveIt 2

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1: Readiness Check</a></li>
                <li><a href="#part2">Part 2: Bring Up the Simulation</a></li>
                <li><a href="#part3">Part 3: Milestone 1, Joint-Space Motion (Worked Example)</a></li>
                <li><a href="#part4">Part 4: Milestone 2, Cartesian Motion</a></li>
                <li><a href="#part5">Part 5: Milestone 3, The Planning Scene</a></li>
                <li><a href="#part6">Part 6: Milestone 4, The Gripper</a></li>
                <li><a href="#part7">Part 7: Milestone 5, Design a Detour</a></li>
            </ol>
        </li>
        <li><a href="#analysis">Analysis and Discussion</a></li>
        <li><a href="#troubleshooting">Troubleshooting</a></li>
        <li><a href="#references">References</a></li>
        <li><a href="#appendix">Appendix: Shared References</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>In this lab you will control a simulated <strong>Kinova Gen3 Lite</strong> arm from Python using <strong>MoveIt 2</strong>, the standard ROS 2 software for planning robot motions. You will command the arm by joint angles and by end-effector pose, add obstacles to the planning scene, open and close the gripper, and then design an obstacle that changes the planned path.</p>
    <p>A small program called the <strong>pen</strong> draws a line in RViz wherever the gripper actually travels. You will use those lines as evidence: they show whether a motion was straight or curved, and whether it went around an obstacle or through it.</p>
    <h3>1.2 Background</h3>
    <p><strong>Motion planning</strong> computes a sequence of joint positions that takes the robot from its current state to a goal without colliding with itself or with objects in the planning scene. This planned sequence is called a <strong>trajectory</strong>. MoveIt computes the trajectory; your code provides the goal and handles the result.</p>
    <p><strong>Planning and executing are separate steps.</strong> <code>plan()</code> returns a trajectory, or <code>None</code> if it found no route. This step does not move the arm. The arm moves after your program sends the trajectory to <code>execute()</code>, and the motion is complete when <code>wait_until_executed()</code> returns.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/d03-moveit-pipeline.svg" alt="Your program sends a goal to plan(); plan() returns a trajectory or None; only execute() makes the controller move the joints" style="max-width: 100%; height: auto;" /></p>
    <p><strong>Joint space and Cartesian space.</strong> A joint-space goal gives the six joint angles directly. The resulting gripper path through space is usually curved. A Cartesian goal gives the gripper&rsquo;s position and orientation; with <code>cartesian=True</code>, a valid trajectory must keep the gripper on a straight path. <code>plan()</code> returns <code>None</code> if no such path is available.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/d01-joint-vs-cartesian.svg" alt="A joint-space goal specifies joint angles and can produce a curved gripper path; a Cartesian goal constrains the gripper to a straight path and can fail" style="max-width: 100%; height: auto;" /></p>
    <p><strong>The planning scene</strong> is MoveIt&rsquo;s model of the world. The planner avoids only what is in that model. An obstacle that exists in Gazebo but not in the planning scene is invisible to the planner, and an obstacle you add to the planning scene is avoided even though nothing is there in Gazebo.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/d02-planning-scene.svg" alt="A box that exists only in Gazebo is planned through; a box added to the planning scene is routed around" style="max-width: 100%; height: auto;" /></p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Command</strong> a robot arm with joint-space and Cartesian goals through MoveIt from Python, including handling a failed plan.</li>
        <li><strong>Distinguish</strong> joint-space from Cartesian motion using the path the end effector actually traced.</li>
        <li><strong>Add</strong> an obstacle to the planning scene and verify its effect on planning.</li>
        <li><strong>Verify</strong> an actuator command, such as closing the gripper, by checking the measured joint state after the command finishes.</li>
        <li><strong>Design</strong> an obstacle and a motion that produce a detour, and <strong>justify</strong> the design with evidence from your own runs.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Accept and clone the assignment, pull the Kinova image, and create, build, and push your package before arriving at lab. The Kinova image is large, so start the pull early. During lab you will check this setup, bring up the simulation, and work on the milestones.</p>
    </div>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>VM lifetime:</strong> VMs power off automatically 4 hours after the reservation starts. Files outside <code>~/workspaces</code> are not retained. Keep your work in that folder and commit and push whenever you finish a milestone.</div>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Where to do what</strong>
        <ul>
            <li><strong>Edit code on your VM (host)</strong> in <strong>VS Code</strong>.</li>
            <li><strong>Run all ROS 2 commands inside the Docker container</strong> (build, source, launch, run).</li>
            <li><strong>Run all Git commands (clone, commit, push) on the VM host</strong>; the container has no GitHub credentials.</li>
            <li>Path mapping: <strong>VM</strong> <code>~/workspaces</code> &harr; <strong>container</strong> <code>/root/workspaces</code>.</li>
        </ul>
    </blockquote>
    <ol>
        <li><strong>Verify Docker and GitHub access.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker --version
ssh -T git@github.com</code></pre>
            <p>Docker should print a version. GitHub should identify your account and report successful authentication.</p>
        </li>
        <li><strong>Make room for the image.</strong> Your VM has a 25 GB system disk, and the images from Labs 1&ndash;4 leave too little space for this one. Check what is free:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">df -h /</code></pre>
            <p>The image and the workspace build together need about 11 GB. If <code>Avail</code> is smaller than that, remove unused Docker data:</p>
            <pre><code class="language-bash">docker system prune -a --volumes -f</code></pre>
            <p>This deletes stopped containers, unused images and networks, build cache, and unused Docker volumes. It does not delete files in <code>~/workspaces</code>. Make sure you do not need data stored only in a stopped container or Docker volume before running it. The image from Labs 2&ndash;4 will be removed if it is unused; you can download it again later with <code>docker pull</code>. Check <code>df -h /</code> again before continuing; a cleared VM has about 12 GB free at this point.</p>
        </li>
        <li><strong>Pull the Kinova course image.</strong> This is a different image from Labs 2&ndash;4, and it is large, so start it early.
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
            <p>If the pull ends with <code>no space left on device</code>, it ran out of disk partway. Free space as above and pull again; the layers it already fetched are kept.</p>
        </li>
        <li><strong>Install or verify the Classroom 50 student command.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh extension install foundation50/gh-student
gh student --help</code></pre>
            <p>If the extension is already installed, the first command may report that it exists. Continue when the help text is available.</p>
            <p>You signed in to <code>gh</code> during Lab 1, and that login carries over. If <code>gh student whoami</code> does not print your GitHub username (for example on a rebuilt VM), run <code>gh student login</code> before continuing.</p>
        </li>
        <li><strong>Accept Lab 5.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-05</code></pre>
            <p>Classroom 50 accepts a pending organization invitation, creates your private repository, and prints the exact <code>git clone</code> command. If you already accepted the assignment, it leaves your repository unchanged.</p>
        </li>
        <li><strong>Clone the repository.</strong> Run the clone command printed by Classroom 50. The expected repository name is:</li>
    </ol>
    <pre><code>MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME</code></pre>
    <p><strong>Location:</strong> Host VM Terminal. Always clone and push on the VM, never inside the container.</p>
    <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME.git
cd intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME</code></pre>
    <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your GitHub username, and use the URL printed by Classroom 50 if it differs from the example.</p>
    <ol start="6">
        <li><strong>Create the ROS 2 workspace.</strong> The starter repository contains <code>README.md</code>, <code>.gitignore</code>, <code>docs/</code>, <code>scaffolds/</code>, <code>lab05.rviz</code>, <code>pytest.ini</code>, and <code>test_lab_5.py</code>. Add the workspace:
            <p><strong>Location:</strong> Host VM Terminal, from inside your cloned repository</p>
            <pre><code class="language-bash">mkdir -p ros2_ws/src</code></pre>
        </li>
        <li><strong>Start the course container.</strong> The command names the container <code>lab05</code>, makes your VM&rsquo;s <code>~/workspaces</code> folder available inside it, and gives Gazebo and RViz access to the VM&rsquo;s GPU through <code>--gpus all</code>.
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab05 --net=host --gpus all -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
            <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Warning:</strong> The <code>--rm</code> option deletes the container when you exit the terminal where you started it. Any additional container terminals opened with <code>docker exec</code> will also close. Files in the shared <code>~/workspaces</code> folder remain on the VM.</blockquote>
            <p>If <code>docker run</code> fails with <code>could not select device driver "" with capabilities: [[gpu]]</code>, your VM is missing the NVIDIA software that lets Docker use the GPU. Run the command again without the <code>--gpus all</code> line; the simulation still works, only more slowly, and tell a TA.</p>
        </li>
        <li><strong>Create the Python package and its <code>scripts</code> folder.</strong>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME/ros2_ws/src
ros2 pkg create --build-type ament_python lab05_moveit --dependencies rclpy geometry_msgs sensor_msgs std_msgs std_srvs visualization_msgs tf2_ros moveit_msgs pymoveit2
mkdir -p lab05_moveit/lab05_moveit/scripts
touch lab05_moveit/lab05_moveit/scripts/__init__.py</code></pre>
            <p>The empty <code>scripts/__init__.py</code> tells Python that <code>scripts/</code> is part of your package. Without it, ROS 2 cannot find your programs after the build, and they fail with <code>ModuleNotFoundError: No module named 'lab05_moveit.scripts'</code>.</p>
        </li>
        <li><strong>Fix file ownership (mandatory).</strong> The container runs as <strong>root</strong>, so the files it just created are owned by root on your VM, and VS Code cannot save them until you run this.
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">sudo chown -R $USER:$USER ~/workspaces/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME</code></pre>
        </li>
        <li><strong>Copy the four starter files into the package.</strong> Leave the originals in <code>scaffolds/</code> as a clean copy to fall back on.
            <p><strong>Location:</strong> Host VM Terminal, from your repository root</p>
            <pre><code class="language-bash">cp scaffolds/motion_planner.py scaffolds/m5_detour.py scaffolds/pen.py scaffolds/table.py ros2_ws/src/lab05_moveit/lab05_moveit/scripts/</code></pre>
            <ul>
                <li><code>motion_planner.py</code>: milestones 1&ndash;4. Milestone 1 is complete; you will implement milestones 2&ndash;4.</li>
                <li><code>m5_detour.py</code>: milestone 5, which you design.</li>
                <li><code>pen.py</code>: complete. It draws the gripper&rsquo;s path in RViz. Do not edit it.</li>
                <li><code>table.py</code>: complete. Your scripts call it to place the table under the arm, in Gazebo and in MoveIt&rsquo;s planning scene. Do not edit it.</li>
            </ul>
        </li>
        <li><strong>Register the three entry points.</strong>
            <p><strong>Location:</strong> File Editor (VS Code on the VM), editing <code>ros2_ws/src/lab05_moveit/setup.py</code></p>
            <p>Replace the empty <code>entry_points</code> block with:</p>
            <pre><code class="language-python">entry_points={
    'console_scripts': [
        'motion_planner = lab05_moveit.scripts.motion_planner:main',
        'm5_detour = lab05_moveit.scripts.m5_detour:main',
        'pen = lab05_moveit.scripts.pen:main',
    ],
},</code></pre>
        </li>
        <li><strong>Build, source, and check the executables.</strong>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 pkg executables lab05_moveit</code></pre>
            <p><strong>Checkpoint:</strong></p>
            <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>lab05_moveit m5_detour
lab05_moveit motion_planner
lab05_moveit pen</code></pre>
            </div>
        </li>
        <li><strong>Commit and push the starter package.</strong>
            <p><strong>Location:</strong> Host VM Terminal, from your repository root</p>
            <pre><code class="language-bash">git add ros2_ws
git commit -m "Add lab05_moveit package with starter scripts"
git push origin main</code></pre>
        </li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest</code> succeeds.</li>
        <li>[ ] <code>df -h /</code> shows at least 1 GB free. About 1.5 GB is normal once the image is pulled and the workspace is built, and it stays flat while you work. If you have less than 1 GB, run the prune from step 2 again.</li>
        <li>[ ] <code>git status</code> reports a clean working tree on <code>main</code>, and <code>git remote -v</code> points to your Lab 5 repository.</li>
        <li>[ ] <code>ls ros2_ws/src/lab05_moveit/lab05_moveit/scripts</code> shows <code>__init__.py</code>, <code>m5_detour.py</code>, <code>motion_planner.py</code>, <code>pen.py</code>, and <code>table.py</code>.</li>
        <li>[ ] <code>ros2 pkg executables lab05_moveit</code>, run in the container after sourcing, lists all three executables.</li>
        <li>[ ] <code>git status</code> shows no <code>build/</code>, <code>install/</code>, or <code>log/</code> directories waiting to be committed.</li>
        <li>[ ] You read Section 1.2 and skimmed the <a href="https://mems-intro-to-robotics.github.io/guides/pymoveit2_api_guide/" target="_blank" rel="noopener">pymoveit2 API guide</a>.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1: Readiness Check</h3>
        <p><strong>Goal:</strong> Confirm that your repository, package, and image are ready before starting the simulation.</p>
        <p><strong>Location:</strong> Host VM Terminal, from the Lab 5 repository.</p>
        <pre><code class="language-bash">git status
git remote -v
ls ros2_ws/src/lab05_moveit/lab05_moveit/scripts
docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest &gt; /dev/null</code></pre>
        <p><strong>Checkpoint:</strong> The working tree is clean on <code>main</code>, the remote is your private Lab 5 repository, the listing shows the five files in <code>scripts/</code>, and the image-inspection command exits without an error. Stop here and finish the pre-lab if any check fails.</p>
    </section>
    <section id="part2">
        <h3>Part 2: Bring Up the Simulation</h3>
        <p><strong>Goal:</strong> Run Gazebo, MoveIt, RViz, and the pen, each in its own terminal, and confirm the arm is ready to plan.</p>
        <h4>Step 2.1: Start the container and open four terminals</h4>
        <p>Start the container with the <code>docker run</code> command from pre-lab step 7. This lab needs four container shells at once. Open each additional one from a new Host VM Terminal with:</p>
        <pre><code class="language-bash">docker exec -it lab05 bash</code></pre>
        <p>The course image sources ROS 2 and the Kinova packages in every shell. Your own workspace must be sourced separately in each shell that runs your code. Later steps call this <strong>preparing a terminal</strong>:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash</code></pre>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 1em;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ccc; padding: 8px;">Terminal</th>
                    <th style="border: 1px solid #ccc; padding: 8px;">Runs</th>
                    <th style="border: 1px solid #ccc; padding: 8px;">Prepare it?</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="border: 1px solid #ccc; padding: 8px;">1</td><td style="border: 1px solid #ccc; padding: 8px;">Gazebo simulation</td><td style="border: 1px solid #ccc; padding: 8px;">No</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 8px;">2</td><td style="border: 1px solid #ccc; padding: 8px;">MoveIt and RViz</td><td style="border: 1px solid #ccc; padding: 8px;">No</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 8px;">3</td><td style="border: 1px solid #ccc; padding: 8px;">The pen</td><td style="border: 1px solid #ccc; padding: 8px;">Yes</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 8px;">4</td><td style="border: 1px solid #ccc; padding: 8px;">Your milestone scripts</td><td style="border: 1px solid #ccc; padding: 8px;">Yes</td></tr>
            </tbody>
        </table>
        <h4>Step 2.2: Launch the Gazebo simulation</h4>
        <p><strong>Location:</strong> Container Terminal 1</p>
        <pre><code class="language-bash">ros2 launch kortex_bringup kortex_sim_control.launch.py sim_gazebo:=true robot_type:=gen3_lite gripper:=gen3_lite_2f robot_name:=gen3_lite dof:=6 launch_rviz:=false use_sim_time:=true robot_controller:=joint_trajectory_controller</code></pre>
        <p>A Gazebo window with the arm opens. Leave it running. One red line in this terminal is expected and harmless:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[ERROR] [gz_ros_control.GZResourceManager]: The plugin failed to load for some reason.
Error: According to the loaded plugin descriptions the class gz_ros2_control/GzSimSystem ...</code></pre>
        </div>
        <p>The arm&rsquo;s ros2_control system drives the gripper joint instead, and the gripper opens and closes normally.</p>
        <h4>Step 2.3: Launch MoveIt and RViz</h4>
        <p><strong>Location:</strong> Container Terminal 2</p>
        <pre><code class="language-bash">ros2 launch kinova_gen3_lite_moveit_config sim.launch.py use_sim_time:=true</code></pre>
        <p>Wait for <code>MoveGroup context initialization complete</code> in this terminal. An RViz window opens showing the robot.</p>
        <p>One red line in this terminal is expected too: <code>[ERROR] ... occupancy_map_monitor]: No 3D sensor plugin(s) defined for octomap updates</code>. This lab uses no depth camera.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Do not add <code>launch_rviz:=false</code> here.</strong> In this MoveIt configuration that flag also stops MoveIt itself from starting: the launch exits with nothing running and no error.</blockquote>
        <h4>Step 2.4: Load the lab&rsquo;s RViz layout</h4>
        <p>In the RViz window, choose <strong>File &rarr; Open Config</strong> and open <code>lab05.rviz</code> from your repository (under <code>/root/workspaces/intro-to-robotics-fall-2026-lab-05-YOUR_GITHUB_USERNAME/</code>). RViz asks whether to save changes to the configuration it had open; choose <strong>Discard</strong>.</p>
        <p>The supplied layout adds a <strong>PenTrail</strong> display, disables continuous replay of the last plan, and hides the orange goal robot. Load it again each time you restart MoveIt.</p>
        <h4>Step 2.5: Start the pen</h4>
        <p><strong>Location:</strong> Container Terminal 3, after preparing it</p>
        <pre><code class="language-bash">ros2 run lab05_moveit pen</code></pre>
        <p><strong>Checkpoint:</strong> Terminal 3 prints <code>Pen ready: tracing end_effector_link in base_link. Pen is up; call /pen/down to start drawing.</code> The Gazebo arm and the RViz arm are in the same pose. In Terminal 4 (prepared), <code>ros2 control list_controllers</code> shows <code>joint_trajectory_controller</code>, <code>joint_state_broadcaster</code>, and <code>gen3_lite_2f_gripper_controller</code> as <code>active</code>.</p>
        <p>The table under the arm appears the first time you run one of your scripts, not at bringup: the scripts call a provided helper that puts it in Gazebo and in the planning scene. In RViz it is a green slab level with the base of the arm.</p>
        <p>Set your NetID once in Terminal 4 so it appears in your scripts&rsquo; output (or edit the <code>NETID</code> line at the top of each script instead):</p>
        <pre><code class="language-bash">export NETID=abc123</code></pre>
    </section>
    <section id="part3">
        <h3>Part 3: Milestone 1, Joint-Space Motion (Worked Example)</h3>
        <p><strong>Goal:</strong> Move the arm from Home to a retract configuration you choose, and see the path the gripper takes.</p>
        <h4>Step 3.1: Read the worked example</h4>
        <p><strong>Location:</strong> File Editor, <code>ros2_ws/src/lab05_moveit/lab05_moveit/scripts/motion_planner.py</code></p>
        <p>Read <code>run_milestone_1</code> and the helpers it calls. The pattern repeats in every milestone:</p>
        <ul>
            <li><code>wait_until_ready()</code> waits until MoveIt answers. MoveIt takes several seconds to start, and a script that plans too early gets <code>None</code> back.</li>
            <li><code>move_to_joints()</code> calls <code>plan()</code>, checks for <code>None</code>, calls <code>execute()</code>, and waits with <code>wait_until_executed()</code>. It tries up to three times, because the planner is randomized and a request can fail once and succeed on the next attempt.</li>
            <li><code>self.pen.down()</code> and <code>self.pen.up()</code> bracket the motion you want drawn.</li>
            <li><code>joint_position()</code> reads the measured angle of a joint from <code>/joint_states</code>, which is what the simulated robot actually did.</li>
        </ul>
        <h4>Step 3.2: Choose your retract configuration</h4>
        <p>The scaffold ships the Gen3 Lite&rsquo;s own retract pose, the one the real arm folds into. Choose your own instead: in RViz, open the <strong>MotionPlanning</strong> panel&rsquo;s <strong>Joints</strong> tab and move the sliders to a folded, compact pose that keeps the whole gripper above the tabletop. The sliders show degrees; convert to radians. Replace the six values in <code>self.retract_joints</code> with yours.</p>
        <p>The table is in the planning scene, so a pose that dips into it cannot be planned: all three attempts fail and the arm stays at Home. If that happens, raise the gripper and try again.</p>
        <h4>Step 3.3: Run milestone 1</h4>
        <p><strong>Location:</strong> Container Terminal 4</p>
        <pre><code class="language-bash">ros2 run lab05_moveit motion_planner 1</code></pre>
        <p>The number after <code>motion_planner</code> selects milestones: <code>1</code> runs only milestone 1, <code>2 3</code> runs 2 and 3, and no number runs all four. With <code>--symlink-install</code>, edits to the script take effect on the next run without rebuilding.</p>
        <p><strong>Checkpoint:</strong> The arm moves to Home and then to your retract pose in both Gazebo and RViz. RViz shows a blue curved line from Home to Retract. The terminal ends with a line like:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[INFO] [motion_planner_node]: Retract reached. Measured joint positions: -0.053, +0.367, +2.589, -1.535, -0.700, -1.518</code></pre>
        </div>
        <p><strong>Screenshot:</strong> RViz showing the arm at your retract pose and the pen line from Home. Save it as <code>docs/m1_joint_home_to_retract.png</code>.</p>
        <p><em>Example (yours shows your own pose, path, and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/s01-m1-joint-retract.png" alt="RViz after milestone 1: the pen line from Home to the retract pose, with the table below the arm" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part4">
        <h3>Part 4: Milestone 2, Cartesian Motion</h3>
        <p><strong>Goal:</strong> Move the gripper along two straight lines in space.</p>
        <p><strong>Requirements for <code>run_milestone_2</code>:</strong></p>
        <ul>
            <li>Start from the arm&rsquo;s current pose. Read the end-effector pose once and build both targets from it.</li>
            <li>Segment 1: at least 0.20 m along one axis of <code>base_link</code>. Segment 2: at least 0.10 m along a different axis, starting where segment 1 ended. Keep the gripper&rsquo;s orientation unchanged. If the planner refuses a segment of that length from your retract pose, shorten it until it plans, and say in your PDF what length you used.</li>
            <li>Plan each segment with <code>cartesian=True</code>. If the planner returns <code>None</code>, log which segment failed and stop, without executing anything.</li>
            <li>Draw both segments with the pen.</li>
        </ul>
        <details>
            <summary>Hint 1: Where the current pose comes from</summary>
            <p><code>self.moveit2.compute_fk()</code> returns a <code>PoseStamped</code> for the end effector at the arm&rsquo;s current joint positions. Its <code>.pose</code> has <code>.position.x</code>, <code>.y</code>, <code>.z</code> and an <code>.orientation</code>. Build each target from a copy (<code>copy.deepcopy</code>) so that changing the target does not change the original.</p>
        </details>
        <details>
            <summary>Hint 2: The planning call</summary>
            <p>Cartesian planning uses the same <code>plan()</code> as milestone 1, with a pose instead of joint positions:</p>
            <pre><code class="language-python">trajectory = self.moveit2.plan(
    pose=target_pose,
    cartesian=True,
    max_step=0.005,
    cartesian_fraction_threshold=0.9,
)</code></pre>
            <p>It returns <code>None</code> when less than 90% of the straight line is achievable. Execute and wait as <code>move_to_joints</code> does.</p>
        </details>
        <details>
            <summary>Hint 3: Seeing the second segment</summary>
            <p>The pen traces <code>end_effector_link</code>, which sits inside the gripper. A segment along the wrist axis can be hidden by the gripper model while the arm is parked at its endpoint. Choose a second axis that moves the gripper sideways, or take the screenshot after the arm has moved away from that corner.</p>
        </details>
        <p><strong>Checkpoint:</strong> RViz shows two straight pen segments meeting at a corner. Run milestone 2 after milestone 1 (<code>motion_planner 1 2</code>) so it starts from your retract pose.</p>
        <p>Compare the new segments with the milestone 1 line in the same window. The milestone 1 line curves because a joint-space plan moves the joints without constraining the gripper to a straight path. A Cartesian segment is straight. At the lengths this milestone asks for, a joint-space plan of the same move misses the straight line by about 18 mm over 0.20 m, which is visible next to a Cartesian one. If your new segments curve, check that the <code>plan()</code> call received <code>cartesian=True</code>; the terminal output does not distinguish the two cases.</p>
        <p><strong>Screenshot:</strong> RViz showing both straight segments. Save it as <code>docs/m2_cartesian_path.png</code>.</p>
        <p><em>Example (yours shows your own pose, path, and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/s02-m2-cartesian.png" alt="RViz after milestone 2: two straight pen segments meeting at a corner" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part5">
        <h3>Part 5: Milestone 3, The Planning Scene</h3>
        <p><strong>Goal:</strong> Demonstrate that planning fails when the goal lies inside a collision object and succeeds after the object is removed.</p>
        <p><strong>Requirements for <code>run_milestone_3</code>:</strong></p>
        <ul>
            <li>Move the arm to Home.</li>
            <li>Add a collision box to the planning scene that occupies the space where the gripper would be at your retract configuration.</li>
            <li>Try to move to your retract configuration. Planning should fail. Log the failure.</li>
            <li>Remove the box, wait for the scene to update, and move to your retract configuration again. Log that it succeeded.</li>
        </ul>
        <details>
            <summary>Hint 1: Where the gripper will be</summary>
            <p><code>compute_fk()</code> also accepts joint positions, and then returns the end-effector pose for those joints without moving the arm: <code>self.moveit2.compute_fk(joint_state=self.retract_joints)</code>. Milestone 1 sets <code>self.retract_joints</code>, so run <code>motion_planner 1 3</code> or set it again inside milestone 3.</p>
        </details>
        <details>
            <summary>Hint 2: Adding and removing the box</summary>
            <pre><code class="language-python">self.moveit2.add_collision_box(
    id="blocker",
    size=(0.10, 0.10, 0.10),              # meters
    position=(x, y, z),                   # meters, in base_link
    quat_xyzw=(0.0, 0.0, 0.0, 1.0),
    frame_id="base_link",
)
time.sleep(1.0)                           # let the planning scene update

self.moveit2.remove_collision_object("blocker")
time.sleep(1.0)</code></pre>
        </details>
        <details>
            <summary>Hint 3: Reading the failure</summary>
            <p><code>move_to_joints()</code> returns <code>False</code> after three failed attempts, and Terminal 2 shows MoveIt&rsquo;s reason, for example <code>Unable to sample any valid states for goal tree</code>. Log the return value in your own words.</p>
        </details>
        <p><strong>Checkpoint:</strong> RViz shows the green box at the gripper&rsquo;s retract position while the planning attempts fail, then the arm reaches Retract after the box disappears. Your terminal output shows the failure and the success.</p>
        <p><strong>Screenshot:</strong> RViz with the box in the scene and the arm at Home, taken while the planning attempts are failing. Save it as <code>docs/m3_planning_scene.png</code>. Copy the milestone 3 terminal output into your PDF.</p>
        <p><em>Example (yours shows your own pose, path, and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/s03-m3-planning-scene.png" alt="RViz during milestone 3: the arm at Home and the green box where the gripper would be at the retract pose" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part6">
        <h3>Part 6: Milestone 4, The Gripper</h3>
        <p><strong>Goal:</strong> Open and close the gripper, and verify its motion from the measured joint state.</p>
        <p><strong>Requirements for <code>run_milestone_4</code>:</strong></p>
        <ul>
            <li>Open the gripper, wait for it to finish, and log the measured position of <code>right_finger_bottom_joint</code>.</li>
            <li>Close it, wait, and log the measured position again.</li>
            <li>Log whether each measurement is within 0.05 of what was commanded. The gripper interface does not check this for you: it can report success when the finger did not move.</li>
        </ul>
        <details>
            <summary>Hint 1: The gripper calls</summary>
            <p><code>self.gripper.open()</code> and <code>self.gripper.close()</code> send the commands configured in <code>__init__</code>: 0.0 is fully open and 0.8 is closed. <code>self.gripper.wait_until_executed()</code> waits for the motion to finish. The first call may log <code>Unable to determine the appropriate interface for gripper</code>; the interface checks again when it is used, so that line alone is not a problem.</p>
        </details>
        <details>
            <summary>Hint 2: Reading the finger</summary>
            <p><code>self.joint_position(GRIPPER_JOINT)</code> returns the latest measured value from <code>/joint_states</code>. Give the reading a moment after <code>wait_until_executed()</code> returns, for example with <code>time.sleep(0.5)</code>.</p>
        </details>
        <p><strong>Checkpoint:</strong> The fingers open and close in Gazebo and in RViz, in the same direction in both. Your log shows a measured value near 0.0 after opening and near 0.8 after closing.</p>
        <p><strong>Screenshot:</strong> RViz or Gazebo with the gripper closed, zoomed so the fingers are clear. Save it as <code>docs/m4_gripper.png</code>. Copy the milestone 4 terminal output into your PDF.</p>
        <p><em>Example (yours shows your own pose, path, and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/s04-m4-gripper.png" alt="RViz during milestone 4: the gripper closed" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part7">
        <h3>Part 7: Milestone 5, Design a Detour</h3>
        <p><strong>Goal:</strong> Design an obstacle and a motion so the planner must take a different path to reach the same goal, and show the difference.</p>
        <p>Choose the start and goal, the obstacle&rsquo;s position and size, and whether the motion is joint-space or Cartesian. Designs are graded against the requirements below using your run evidence and justification.</p>
        <p><strong>Requirements for <code>m5_detour.py</code>:</strong></p>
        <ul>
            <li>Run a motion from a start to a goal with no obstacle, with the pen down in one color.</li>
            <li>Add a collision box that blocks the path that motion took. Run the same motion again, from the same start to the same goal, in a second pen color.</li>
            <li>Keep the box visible long enough to take the screenshot, then remove it so the next run starts with a clean scene. Before removing it, either log a message and wait several seconds or pause and remove it on a separate run.</li>
            <li>Log, for each of the two motions: whether it succeeded, how many planning attempts it needed, and how long the motion took (time it with <code>time.time()</code> around the call).</li>
        </ul>
        <p><strong>Design justification</strong> (in your PDF, a short paragraph):</p>
        <ul>
            <li>Why you placed and sized the box where you did, using your first pen line.</li>
            <li>Why you chose joint-space or Cartesian motion for this task, and what the other choice would have done.</li>
            <li>What your logged attempts and durations show about the cost of the detour.</li>
        </ul>
        <p>Change the pen color between the two motions with <code>self.pen.set_color(red, green, blue)</code>, each value from 0 to 1, for example <code>self.pen.set_color(0.9, 0.1, 0.1)</code> for red. The new color takes effect at the next <code>self.pen.down()</code>.</p>
        <details>
            <summary>Hint 1: Where the box has to go</summary>
            <p>Draw the no-obstacle path first, then place the box across the middle of it. The pen traces <code>end_effector_link</code> at the base of the gripper, while the fingers extend about 0.1 m farther. A box can therefore block the gripper while sitting a few centimeters from the pen line.</p>
        </details>
        <details>
            <summary>Hint 2: Sizing it</summary>
            <p>If the box is small, the planner can pass it with a path that barely changes. If it covers the goal or leaves no route, planning fails on every attempt. Start with a box a few centimeters thick and wide enough to span the line, then adjust it using what each run shows.</p>
        </details>
        <details>
            <summary>Hint 3: Failures that come and go</summary>
            <p>Because the planner is randomized, an attempt can fail even when a detour exists. <code>move_to_joints()</code> retries three times; if all three fail on several runs in a row, reduce or reposition the box.</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> First check that the box appears in RViz where you intended. Then check the no-obstacle run on its own. If the arm does not move, read Terminal 2 for MoveIt&rsquo;s reason. If Gazebo and RViz disagree about the arm&rsquo;s pose, stop your script, restart Terminals 1 and 2, and reload <code>lab05.rviz</code>. After one clean restart or 10 minutes without progress, ask a TA and show the log line that disagrees with what you expected.</blockquote>
        <p><strong>Location:</strong> Container Terminal 4</p>
        <pre><code class="language-bash">ros2 run lab05_moveit m5_detour</code></pre>
        <p><strong>Checkpoint:</strong> RViz shows two pen lines in different colors between the same start and goal, one of them bending around the box. Your terminal output reports both motions with their attempts and durations.</p>
        <p><strong>Screenshot:</strong> RViz with both pen lines and the box visible. Save it as <code>docs/m5_detour.png</code>. Copy the milestone 5 terminal output into your PDF.</p>
        <p><em>Example (yours shows your own pose, path, and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab05/s05-m5-detour.png" alt="RViz after milestone 5: the direct path in blue, the detour around the box in red" style="max-width: 100%; height: auto;" /></p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p><strong>Where the answers go:</strong> this lab has no record file in the repository. Write your answers to the four questions below in your Gradescope PDF (see &sect;7.2), after your milestone 5 justification. All four are graded there.</p>
    <p>Answer each in a few sentences, using your own runs.</p>
    <h3>Question 1: Joint space and Cartesian space</h3>
    <ul>
        <li>Compare your milestone 1 and milestone 2 pen lines. What does each show about how the gripper moved between its start and goal?</li>
        <li>Give one task where the straight Cartesian path matters, and one where only the destination matters.</li>
    </ul>
    <h3>Question 2: When a Cartesian plan fails</h3>
    <ul>
        <li>Change one of your milestone 2 segments to a length the arm cannot reach in a straight line (0.60 m along x works from the shipped retract pose) and run it. What did the planner return, and what did MoveIt log?</li>
        <li>Why can a straight line fail when a joint-space move to the same pose would succeed?</li>
    </ul>
    <h3>Question 3: The planning scene</h3>
    <ul>
        <li>In milestone 3, the box existed only in MoveIt&rsquo;s planning scene. What would have happened if it had existed only in Gazebo?</li>
        <li>Name one way a real robot&rsquo;s planning scene could be wrong, and what the consequence would be.</li>
    </ul>
    <h3>Question 4: Verifying a command</h3>
    <ul>
        <li>Your milestone 4 checked the finger&rsquo;s measured position instead of trusting that <code>close()</code> returned. Describe a failure that the measurement would catch and the return value would not.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Setup, Docker, ROS 2, and MoveIt problems that recur across labs are collected on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#moveit-2-and-kinova-workflows" target="_blank" rel="noopener">Troubleshooting</a>. For this lab, the page covers an image pull that stops with <code>no space left on device</code>, <code>Error code: 99999</code> in a planning failure, <code>terminate called without an active exception</code> at the end of a run, RViz opening when planning is not available, a plan that is created but never moves the arm, repeated Cartesian-planning failures, gripper commands that do not move the fingers, controllers that fail to start, a black Gazebo window, and <code>ModuleNotFoundError: No module named 'lab05_moveit.scripts'</code>.</p>
    <p>Check the relevant troubleshooting entry before asking a TA.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://moveit.picknik.ai/main/doc/concepts/concepts.html" target="_blank" rel="noopener">MoveIt 2: Concepts</a></li>
        <li><a href="https://moveit.picknik.ai/main/doc/concepts/planning_scene_monitor.html" target="_blank" rel="noopener">MoveIt 2: Planning Scene Monitor</a></li>
        <li><a href="https://github.com/AndrejOrsula/pymoveit2" target="_blank" rel="noopener">pymoveit2</a></li>
        <li><a href="https://github.com/Kinovarobotics/ros2_kortex" target="_blank" rel="noopener">Kinova ros2_kortex</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/index.html" target="_blank" rel="noopener">ROS 2 Jazzy Documentation</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <p>Use these references for the <code>pymoveit2</code> calls and the inspection commands in Parts 3&ndash;7.</p>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/pymoveit2_api_guide/" target="_blank" rel="noopener">pymoveit2 API guide</a>: joint-space and Cartesian planning, collision objects, orientation constraints, the gripper interface, and signatures.</li>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/kinova_gen3_lite_moveit2_guide/" target="_blank" rel="noopener">Kinova Gen3 Lite MoveIt 2 guide</a>: the robot&rsquo;s groups, joints, frames, and controllers, and how to inspect them.</li>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: build and source reminders, ROS 2 CLI checks, Git commands, and Docker commands.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
