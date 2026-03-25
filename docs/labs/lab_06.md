---
title: "Lab 06: Pick-and-Place Manipulation"
---

# Lab 06: Pick-and-Place Manipulation

<div class="lab-content">

<h1>1 Introduction</h1>
<h2>1.1 Overview</h2>
<p>This lab is the culmination of your foundational robotics skills. You will implement a complete <strong>pick-and-place</strong> pipeline to stack several blocks using the Kinova Gen3 Lite arm. The core challenge is <strong>sequencing</strong> everything you learned previously&mdash;arm motion, gripper control, and planning-scene hygiene&mdash;into one robust routine. <strong>You will begin with a functional starter script that picks and places a single block, which you will then analyze, modify, and extend to achieve the full stacking task.</strong></p>
<p>The workflow and tooling are <strong>identical to the previous lab</strong> to reduce setup friction:</p>
<ul>
    <li>Docker &rarr; <strong>one</strong> container</li>
    <li>Terminator &rarr; <strong>multiple panes inside the container</strong></li>
    <li>Gazebo + MoveIt/RViz</li>
</ul>
<h2>1.2 Background: The Logic of a Pick-and-Place Task</h2>
<p>A successful pick-and-place task is more than just a sequence of movements; it's an interaction with the environment. The robot's planner must know how the world changes as you grasp and release objects. In MoveIt, this means updating the <strong>Planning Scene</strong> (its internal world model). The key new concept in this lab is mastering the <strong>attach/detach</strong> workflow, which tells the planner that a grasped object is temporarily part of the robot, so it doesn't try to "avoid" the very thing it's holding.</p>
<p>The entire process follows a clear, repeatable, and robust sequence.</p>
<p><strong>Canonical Pick-and-Place Flow:</strong></p>
<pre><code>
PICK sequence:
  1. APPROACH  (Move to a safe pre-grasp pose above the object)
  2. DESCEND   (Move in a straight line down to the grasp pose)
  3. GRASP     (Close the gripper)
  4. ATTACH    (Update planning scene: object is now part of the gripper)
  5. LIFT      (Move in a straight line up to a safe height)

PLACE sequence:
  6. APPROACH  (Move to a safe pre-place pose above the target location)
  7. DESCEND   (Move in a straight line down to the place pose)
  8. RELEASE   (Open the gripper)
  9. DETACH    (Update planning scene: object is now a world obstacle again)
  10. RETREAT  (Move in a straight line up to a safe height)
</code></pre>
<p>Your starter code implements this exact sequence for picking and placing one block in the same spot. Your first job is to understand how it works before you modify it to stack multiple blocks.</p>
<hr />
<h1>2 Objectives</h1>
<p>By the end of this lab, you will:</p>
<ul>
    <li>Implement a multi-step manipulation routine by sequencing arm and gripper commands.</li>
    <li>Use safe <strong>approach/retreat</strong> poses for straight-line grasps and releases.</li>
    <li>Dynamically manage the <strong>Planning Scene</strong> by attaching an object on grasp and detaching it on release.</li>
    <li>Modify and extend a working ROS2 Python node to perform a more complex task (stacking).</li>
    <li>(Optional) Address sim-to-real hardware differences methodically.</li>
</ul>
<hr />
<h1>3 Pre-Lab Preparation (Environment Setup)</h1>
<hr />
<p>This section guides you through setting up the exact environment needed for the lab. You will only use the command line; <strong>no code will be written yet</strong>. Follow these steps in order to ensure a smooth start.</p>
<h2>3.1 Update Your Course Repository (IMPORTANT First Step)</h2>
<p>Before you do anything else, ensure your local copy of the course repository is up-to-date.</p>
<p><strong>On your host VM (outside of Docker):</strong></p>
<pre><code class="language-bash"># Navigate to your main robotics workspace
cd ~/workspaces/[netid]_robotics_fall2025

# Pull the latest changes from the main branch
git pull
</code></pre>
<h2>3.2 The "One Container, Many Panes" Philosophy</h2>
<p>You will start <strong>exactly one</strong> Docker container for the entire lab. All your work will happen inside it. If you need another terminal, you will open a <strong>new pane or tab inside Terminator</strong>, which runs within the container.<br /><strong>Do not</strong> run the <code>docker run</code> command more than once.</p>
<hr />
<h2>3.3 Pull the Docker Image</h2>
<p>If you haven't already, pull the latest version of the course Docker image. This contains ROS2, Gazebo, and all the Kinova-specific software you'll need.</p>
<p><strong>On your host VM (outside of Docker):</strong></p>
<pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
<h2>3.4 Enable GPU Acceleration for Smooth Simulation (Run Once)</h2>
<p>To ensure Gazebo and RViz run smoothly, we need to allow Docker to access the VM's NVIDIA GPU. The following script installs the necessary tools. You only need to do this once per VM.</p>
<p><strong>On your host VM (outside of Docker):</strong></p>
<pre><code class="language-bash">cd ~
curl -L "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/gpu_install.sh" -o gpu_install.sh
chmod +x gpu_install.sh
./gpu_install.sh
</code></pre>
<p>If the script fails because you're not in the <code>docker</code> group, run this command, then log out and log back into your VM for the change to take effect:</p>
<pre><code class="language-bash">sudo usermod -aG docker "$USER"
</code></pre>
<p>If you don't have a GPU, you can omit the <code>--gpus all</code> flag later, but you may need to enable software rendering if you see OpenGL errors by running <code>export LIBGL_ALWAYS_SOFTWARE=1</code> inside the container.</p>
<hr />
<h2>3.5 Start the ROS 2 Container</h2>
<p>Now, launch the container. This command connects it to your display, mounts your workspace files, and gives it access to the GPU.</p>
<p><strong>On your host VM (outside of Docker):</strong></p>
<pre><code class="language-bash">xhost +local:docker

docker run --rm -it \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/workspaces:/workspaces \
  --gpus all \
  --name ros2_lab06 \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest \
  bash</code></pre>
<p><strong>Understanding the command:</strong></p>
<ul>
    <li><code>--net=host</code>: Allows the container to share the host's network, which simplifies ROS2 communication.</li>
    <li><code>-e DISPLAY</code> and <code>-v /tmp/.X11-unix</code>: Forwards the display so you can run GUI applications like Gazebo and RViz.</li>
    <li><code>-v ~/workspaces:/workspaces</code>: <strong>Crucial!</strong> This mounts your local file system into the container, so any code you write is saved on your machine.</li>
    <li><code>--gpus all</code>: Enables NVIDIA GPU acceleration.</li>
</ul>
<hr />
<h2>3.6 Launch Terminator for a Multi-Pane Workflow</h2>
<p>Once inside the container, launch Terminator to manage all your terminals in one window.</p>
<p><strong>From the container prompt:</strong></p>
<pre><code class="language-bash">terminator &amp;
</code></pre>
<ul>
    <li>New pane (split <strong>horizontally</strong>): <code>Ctrl+Shift+O</code></li>
    <li>New pane (split <strong>vertically</strong>): <code>Ctrl+Shift+E</code></li>
</ul>
<blockquote>
    <p>From now on, all commands will be run in a Terminator pane <strong>inside the container</strong>.</p>
</blockquote>
<h2>3.7 Create Your Lab 6 Workspace</h2>
<p>In a Terminator pane, create the directory structure for this lab.</p>
<pre><code class="language-bash"># The [netid]_robotics_fall2025 folder should already exist
cd /workspaces/[netid]_robotics_fall2025
mkdir -p lab06/docs lab06/ros2_ws/src
</code></pre>
<h2>3.8 A Preview of Your Workspace Panes</h2>
<p>During the lab, you will organize your work into four main panes. Do not run these commands yet; this is just to familiarize you with the workflow.</p>
<ul>
    <li><strong>Pane A</strong>: Gazebo simulation for the Kinova Gen3 Lite.</li>
    <li><strong>Pane B</strong>: MoveIt and RViz for motion planning.</li>
    <li><strong>Pane C</strong>: Your development environment for building and running your Python node.</li>
    <li><strong>Pane D</strong>: Scripts for spawning objects into Gazebo.</li>
</ul>
<hr />
<h2>3.9 "Ready for Lab" Checklist</h2>
<p>You are ready to begin the <strong>Lab Procedure</strong> when you can say "yes" to all of the following:</p>
<ul>
    <li>I have successfully run <code>git pull</code> in my course repository on the <strong>host</strong>.</li>
    <li>I have started <strong>one</strong> container and it is named <code>ros2_lab06</code>.</li>
    <li>I have launched <strong>Terminator inside the container</strong> and can open multiple panes.</li>
    <li>My Lab 6 directory structure exists at <code>/workspaces/[netid]_robotics_fall2025/lab06/</code>.</li>
</ul>
<hr />
<h1>5 Lab Procedure</h1>
<hr />
<h1>5.0 Starter Code Template</h1>
<hr />
<blockquote>
    <p>You&rsquo;ll download a <strong>complete, working script</strong> that can already pick up one block and place it back in the same spot. Your main task will be to <strong>understand and modify</strong> this script to stack all three blocks.</p>
</blockquote>
<h1>5.0.1 Create the package &amp; download the script (Pane C)</h1>
<pre><code class="language-bash"># Inside the container: open a new Terminator pane (Pane C)
source /opt/ros/$ROS_DISTRO/setup.bash
cd /workspaces/[netid]_robotics_fall2025/lab06/ros2_ws/src

# Create the package (ament_python)
ros2 pkg create --build-type ament_python lab06_moveit

# Make the scripts folder
mkdir -p lab06_moveit/lab06_moveit/scripts

# Download the provided script (use the RAW link)
curl -L -o lab06_moveit/lab06_moveit/scripts/pick_and_place.py \
  "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/lab06_files/pick_and_place.py"</code></pre>
<h1>5.0.2 Register the console entry (so <code>ros2 run</code> works)</h1>
<p>Open <code>lab06_moveit/setup.py</code> and set <strong>entry_points</strong> like this:</p>
<pre><code class="language-python">entry_points={
    'console_scripts': [
        'pick_and_place = lab06_moveit.scripts.pick_and_place:main',
    ],
},
</code></pre>
<p>Also ensure <code>package.xml</code> has these runtime deps (add if missing):</p>
<pre><code class="language-xml">&lt;exec_depend&gt;rclpy&lt;/exec_depend&gt;
&lt;exec_depend&gt;geometry_msgs&lt;/exec_depend&gt;
&lt;exec_depend&gt;pymoveit2&lt;/exec_depend&gt;
</code></pre>
<h1>5.0.3 Build &amp; Quick Sanity Check</h1>
<p>After creating the package and adding the script, perform an initial build and a simple run to make sure everything is configured correctly before launching the full simulation.</p>
<pre><code class="language-bash">cd /workspaces/[netid]_robotics_fall2025/lab06/ros2_ws
colcon build --symlink-install
source install/setup.bash

# Sanity run: This should start the node, log the default 'home' task, and exit cleanly.
# It will print errors about not being able to connect to action servers, which is EXPECTED
# because the simulation is not running yet.
ros2 run lab06_moveit pick_and_place
</code></pre>
<p><strong>What "success" looks like right now:</strong> The script runs without crashing. You will see warnings like "Waiting for action server..." because nothing is running yet, but there should be no Python exceptions. This confirms your package is built and the script is executable.</p>
<hr />
<blockquote>
    <p>Now continue to <strong>5.1 Start Simulation</strong>. You will launch Gazebo and MoveIt first, then spawn the blocks, and only then will you run the <code>add_scene</code> task to update RViz.</p>
</blockquote>
<h2>5.1 Start Simulation (Gazebo bringup) &mdash; Pane A</h2>
<blockquote>
    <p>You&rsquo;re inside the <strong>one</strong> container you started in the Pre-Lab. Open a <strong>new Terminator pane inside the container</strong> (Ctrl+Shift+O/E). This will be your <strong>Pane A</strong> for Gazebo. Do <strong>not</strong> start another container.</p>
</blockquote>
<p><strong>A) Source ROS in this pane</strong></p>
<pre><code class="language-bash">source /opt/ros/$ROS_DISTRO/setup.bash
</code></pre>
<p><strong>B) Launch the Kinova Gen3 Lite simulation in Gazebo (keep this running)</strong></p>
<pre><code class="language-bash">ros2 launch kortex_bringup kortex_sim_control.launch.py \
  sim_gazebo:=true \
  robot_type:=gen3_lite \
  gripper:=gen3_lite_2f \
  robot_name:=gen3_lite \
  dof:=6 \
  use_sim_time:=true \
  launch_rviz:=false \
  robot_controller:=joint_trajectory_controller
</code></pre>
<p><strong>Screenshot callout:</strong> Take a screenshot of <strong>Gazebo</strong> with the Gen3 Lite loaded (you&rsquo;ll submit this later).</p>
<hr />
<h2>5.2 Start Planning (MoveIt + RViz) &mdash; Pane B</h2>
<blockquote>
    <p>Open a second <strong>Terminator pane inside the same container</strong>. This will be your <strong>Pane B</strong> for MoveIt + RViz.</p>
</blockquote>
<p><strong>A) Source ROS in this pane</strong></p>
<pre><code class="language-bash">source /opt/ros/$ROS_DISTRO/setup.bash
</code></pre>
<p><strong>B) Launch MoveIt + RViz for Gen3 Lite (keep this running)</strong></p>
<pre><code class="language-bash">ros2 launch kinova_gen3_lite_moveit_config sim.launch.py use_sim_time:=true
</code></pre>
<p><strong>Screenshot callout:</strong> Take a screenshot of <strong>RViz</strong> showing the MotionPlanning panel and the robot (you&rsquo;ll submit this later).</p>
<hr />
<h1>5.3 Download &amp; Run the Gazebo Spawner &mdash; Host + Pane D</h1>
<p><strong>Goal:</strong> Download the instructor-provided <code>spawn_blocks.sh</code> into your Lab 6 workspace on the <strong>host</strong>, then run it <strong>inside the container</strong> to spawn a table and three colored cubes in Gazebo.</p>
<h2>A) Host (outside Docker): download the script</h2>
<p>Open a normal host terminal (not inside Docker):</p>
<pre><code class="language-bash"># 1) Go to your Lab 6 src folder on the HOST (this path is mounted into the container)
mkdir -p ~/workspaces/[netid]_robotics_fall2025/lab06/ros2_ws/src/mems-toolkit/lab06_files
cd ~/workspaces/[netid]_robotics_fall2025/lab06/ros2_ws/src/mems-toolkit/lab06_files

# 2) Download the script (use the RAW link)
curl -L -o spawn_blocks.sh \
  "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/lab06_files/spawn_blocks.sh"

# 3) Make it executable
chmod +x spawn_blocks.sh
</code></pre>
<blockquote>
    <p>If you prefer, you can simply open the provided URL in a browser and save the file into the path above as <code>spawn_blocks.sh</code>.</p>
</blockquote>
<h2>B) Pane D (inside the container): run the spawner</h2>
<p>Open a new Terminator pane <strong>inside the container</strong> (Ctrl+Shift+O/E). This is Pane D.</p>
<pre><code class="language-bash"># 1) Confirm the script is visible inside the container (mounted path)
ls /workspaces/[netid]_robotics_fall2025/lab06/ros2_ws/src/mems-toolkit/lab06_files/spawn_blocks.sh

# 2) Make sure Gazebo is already running in Pane A

# 3) Run the spawner (auto-detects the world name, cleans old entities, spawns table + 3 cubes)
cd /workspaces/[netid]_robotics_fall2025/lab06/ros2_ws/src/mems-toolkit/lab06_files
./spawn_blocks.sh
</code></pre>
<p><strong>What you should see:</strong> In Gazebo (Pane A), a <strong>static gray table</strong> and three <strong>40 mm cubes</strong> colored <strong>red / blue / yellow</strong> will appear. They&rsquo;ll drop ~1 cm and settle.</p>
<hr />
<h3>Troubleshooting quickies</h3>
<ul>
    <li>
        <p><strong>Nothing spawns:</strong> Is Gazebo running in Pane A? Are you running the script <strong>inside the container</strong>? Try specifying the world name with <code>WORLD=empty ./spawn_blocks.sh</code>.</p>
    </li>
    <li>
        <p><strong>Path not found in container:</strong> Verify you saved the script on the <strong>host</strong> in the correct mounted directory.</p>
    </li>
</ul>
<hr />
<h3>Resetting Block Positions (If You Knock Them Over)</h3>
<p>It's very common to knock blocks over while testing your code. Instead of restarting the entire simulation, you can reset a block's position with a single command. Run these from <strong>Pane D</strong> (or any pane inside the container).</p>
<p>These commands will place the block slightly above the table, letting it settle into place.</p>
<p><strong>To reset the RED block (left):</strong></p>
<pre><code class="language-bash">gz service -s /world/empty/set_pose \
  --reqtype gz.msgs.Pose --reptype gz.msgs.Boolean --timeout 2000 \
  --req 'name: "lab06_block_red",
         position: {x: 0.45, y: -0.08, z: 0.31},
         orientation: {x: 0, y: 0, z: 0, w: 1}'
</code></pre>
<p><strong>To reset the BLUE block (center):</strong></p>
<pre><code class="language-bash">gz service -s /world/empty/set_pose \
  --reqtype gz.msgs.Pose --reptype gz.msgs.Boolean --timeout 2000 \
  --req 'name: "lab06_block_blue",
         position: {x: 0.45, y: 0.00, z: 0.31},
         orientation: {x: 0, y: 0, z: 0, w: 1}'
</code></pre>
<p><strong>To reset the YELLOW block (right):</strong></p>
<pre><code class="language-bash">gz service -s /world/empty/set_pose \
  --reqtype gz.msgs.Pose --reptype gz.msgs.Boolean --timeout 2000 \
  --req 'name: "lab06_block_yellow",
         position: {x: 0.45, y: 0.08, z: 0.31},
         orientation: {x: 0, y: 0, z: 0, w: 1}'
</code></pre>
<blockquote>
    <p><em>Note: If your Gazebo world is not named "empty", replace <code>/world/empty/set_pose</code> with the correct world name.</em></p>
</blockquote>
<h1>5.4 Mirror the Gazebo Blocks into the Planning Scene &mdash; Pane C</h1>
<p><strong>Goal:</strong> Add collision objects to MoveIt's <strong>Planning Scene</strong> that match the objects in Gazebo.</p>
<p>Your starter code has a task for this. Run it in Pane C:</p>
<pre><code class="language-bash"># Make sure you have built and sourced your workspace
source /workspaces/[netid]_robotics_fall2025/lab06/ros2_ws/install/setup.bash

# Run the add_scene task
ros2 run lab06_moveit pick_and_place --ros-args -p task:=add_scene
</code></pre>
<p><strong>What you should see:</strong> In RViz, a "table" and three small cubes appear. The planner will now be able to avoid them.</p>
<hr />
<h1>5.5 Analyze and Run the Starter Code</h1>
<p><strong>Goal:</strong> Understand how the provided <code>pick_and_place.py</code> script works. It contains a complete sequence to pick up <code>block_1</code> and place it back down. Open the script in your editor and examine its structure.</p>
<h3>A) Code Analysis: Key Sections</h3>
<p>Look for these parts inside the <code>PickAndPlaceNode</code> class:</p>
<ol>
    <li>
        <p><strong><code>__init__(self)</code> (The Constructor):</strong> This is where all the setup happens.</p>
        <ul>
            <li>Notice how <code>self.moveit2</code> and <code>self.gripper</code> are initialized.</li>
            <li>Find the hard-coded pose definitions: <code>self.pre_grasp_pose</code>, <code>self.grasp_pose</code>, <code>self.pre_place_pose</code>, and <code>self.place_pose</code>. <strong>Crucially, note that the "place" poses are currently identical to the "grasp" poses. This is why it places the block back where it started.</strong></li>
        </ul>
    </li>
    <li>
        <p><strong>Wrapper Functions (<code>move_to_pose</code>, <code>open_gripper</code>, etc.):</strong> These are helper functions that make the main logic easier to read.</p>
    </li>
    <li>
        <p><strong><code>task_pick_place_one(self)</code> (The Main Logic):</strong> This function contains the step-by-step sequence of the robot's actions. Read through it to understand the flow:</p>
        <ol>
            <li>Move to a starting pose (<code>j_retract</code>).</li>
            <li>Open the gripper.</li>
            <li><strong>Approach:</strong> Move to <code>pre_grasp_pose</code> (above the block).</li>
            <li><strong>Descend:</strong> Move straight down to <code>grasp_pose</code>.</li>
            <li><strong>Grasp:</strong> Call <code>close_gripper()</code> and then <code>self.moveit2.attach_collision_object(...)</code>. Attaching the object tells the planner that the block is now part of the robot, so it doesn't try to plan around it.</li>
            <li><strong>Lift:</strong> Move straight up back to <code>pre_grasp_pose</code>.</li>
            <li><strong>Lower:</strong> Move to <code>pre_place_pose</code> and then descend to <code>place_pose</code>.</li>
            <li><strong>Release:</strong> Call <code>open_gripper()</code> and then <code>self.moveit2.detach_collision_object(...)</code>. Detaching returns the block to the world, so the planner will avoid it again.</li>
            <li><strong>Retract:</strong> Move away to a final pose.</li>
        </ol>
    </li>
</ol>
<h3>B) Run the Base Task (Pane C)</h3>
<p>Execute the main task from your terminal.</p>
<pre><code class="language-bash"># In Pane C
ros2 run lab06_moveit pick_and_place --ros-args -p task:=pick_place_one
</code></pre>
<p><strong>What you should see:</strong></p>
<ul>
    <li>In <strong>Gazebo</strong>, the robot arm will perform the full sequence: it will descend, grasp the first block, lift it up, lower it back down, release it, and move away.</li>
    <li>In <strong>RViz</strong>, you will see the plan being visualized. Watch the <strong>PlanningScene</strong> display: the block should move from "Collision Objects" to "Attached Objects" when grasped, and back again when released.</li>
</ul>
<p><strong>Verification:</strong> The robot successfully picks and places the block without errors. If the gripper hangs, ensure you are using the latest version of the code, which uses non-blocking gripper calls.</p>
<hr />
<h1>5.6 Main Task: Implement Block Stacking</h1>
<p><strong>Goal:</strong> Modify the starter code to stack all three blocks in a tower at a new location.</p>
<h3>A) Part 1: Place One Block in a New Location</h3>
<p>Your first task is to modify the code so it places <code>block_1</code> on top of <code>block_2</code>.</p>
<ol>
    <li>
        <p><strong>In <code>__init__</code>, find the pose definitions.</strong> You need to change <code>self.pre_place_pose</code> and <code>self.place_pose</code>.</p>
    </li>
    <li>
        <p><strong>Calculate the new target coordinates.</strong> The new location will have the same X and Y as <code>block_2</code>. The new Z height will be higher. Remember that the pose defines the <strong>center</strong> of the end-effector.</p>
        <ul>
            <li>The Z for <code>place_pose</code> should be roughly the height of <code>block_2</code> plus the height of <code>block_1</code>.</li>
            <li>The Z for <code>pre_place_pose</code> should be that height plus some clearance (e.g., <code>self.approach_height</code>).</li>
        </ul>
    </li>
    <li>
        <p>Update the lines that define `self.pre_place_pose` and `self.place_pose` with your new calculated values.</p>
    </li>
    <li>
        <p><strong>Build and run:</strong></p>
        <pre><code class="language-bash">colcon build --symlink-install
source install/setup.bash
ros2 run lab06_moveit pick_and_place --ros-args -p task:=pick_place_one
</code></pre>
    </li>
</ol>
<p><strong>Milestone 1 (success):</strong> The robot picks up <code>block_1</code> and successfully places it on top of <code>block_2</code> in Gazebo.</p>
<p><strong>Screenshot:</strong> A <strong>Gazebo</strong> image showing <code>block_1</code> stacked on <code>block_2</code>.</p>
<h3>B) Part 2: Create a New Task to Stack All Three Blocks</h3>
<p>Now, create a new task that picks each block in sequence and places it into a three-block tower.</p>
<ol>
    <li>
        <p><strong>Create a new function</strong> in your class called <code>def task_stack_all(self):</code>.</p>
    </li>
    <li>
        <p>Inside this new function, you will need a <strong><code>for</code> loop</strong> that iterates three times (for each block/layer).</p>
    </li>
    <li>
        <p><strong>Copy the logic</strong> from <code>task_pick_place_one</code> into your loop. You will need to adapt it.</p>
    </li>
    <li>
        <p><strong>Generalize the Poses:</strong> Instead of using hard-coded poses like <code>self.pre_grasp_pose</code>, you will need to calculate the pick-and-place poses dynamically inside the loop for each block and each stack layer.</p>
        <ul>
            <li><strong>Pick Poses:</strong> Use the block ID (e.g., <code>"block_1"</code>, <code>"block_2"</code>) to look up its starting XYZ coordinates from <code>self.blocks_xyz</code>.</li>
            <li><strong>Place Poses:</strong> Calculate the target XYZ for each layer of the stack. The X and Y will be constant, but the Z coordinate will increase by <code>block_size</code> for each iteration of the loop.</li>
        </ul>
    </li>
    <li>
        <p><strong>Update the <code>main</code> function</strong> to recognize your new task:</p>
        <pre><code class="language-python"># In main()
elif task == "stack_all":
    node.task_stack_all()
</code></pre>
    </li>
    <li>
        <p><strong>Build and run your new task:</strong></p>
        <pre><code class="language-bash">colcon build --symlink-install
source install/setup.bash
ros2 run lab06_moveit pick_and_place --ros-args -p task:=stack_all
</code></pre>
    </li>
</ol>
<p><strong>Milestone 2 (success):</strong> The robot successfully picks all three blocks, one by one, and creates a stable three-block tower in Gazebo.</p>
<p><strong>Screenshots:</strong></p>
<ol>
    <li>RViz with the final planning scene (three stacked blocks).</li>
    <li>Gazebo with the finished three-block stack.</li>
</ol>
<hr />
<h1>5.7 Robustness &amp; Recovery (Mini-Playbook)</h1>
<p><strong>Planning failure on transit (pose-goal):</strong></p>
<ul>
    <li>Increase clearance: Adjust <code>self.approach_height</code>.</li>
    <li>Adjust end-effector orientation in the <code>make_pose()</code> helper if you suspect an IK failure.</li>
</ul>
<p><strong>Cartesian fraction too low on vertical moves:</strong></p>
<ul>
    <li>This happens when MoveIt cannot find a valid straight-line path. Ensure the start and end poses for Cartesian moves are vertically aligned (same x,y).</li>
    <li>Slightly raise/lower the target z by 1&ndash;2 mm.</li>
</ul>
<p><strong>Object slip / physics jitter in Gazebo:</strong></p>
<ul>
    <li>Ensure there are small <code>time.sleep()</code> pauses after gripper actions to let physics settle.</li>
    <li>Make sure your grasp/place poses are slightly above the target surface, not intersecting it.</li>
</ul>
<p><strong>Deliverable note:</strong><br />In your short write-up, include <strong>one issue</strong> you hit and exactly how you fixed it (what you changed and why it worked).</p>
<hr />
<p>✅ With a working three-block stack, you have completed the core objectives for Lab 6!</p>
<h2>5.8 (Optional) Hardware Deployment &mdash; <strong>Lab Computers Only</strong></h2>
<blockquote>
    <p><strong>You will use the assigned lab desktop</strong> that&rsquo;s hard-wired to the robot. Do <strong>not</strong> use your personal laptop/VM for this section. Keep motions slow and stop if anything looks off.</p>
</blockquote>
<h3>A) Before you start (lab PC basics)</h3>
<ul>
    <li>
        <p><strong>Who uses the station?</strong> Only your team at your assigned robot PC.</p>
    </li>
    <li>
        <p><strong>Files:</strong> You&rsquo;ll need your Lab 6 repo on the lab PC. From the lab PC (host):</p>
        <pre><code class="language-bash">mkdir -p ~/workspaces
cd ~/workspaces
# Option 1: fresh clone of your repo
git clone https://&lt;your-remote&gt;/[netid]_robotics_fall2025.git
# Option 2: if already cloned earlier on this lab PC
cd [netid]_robotics_fall2025 &amp;&amp; git pull
</code></pre>
    </li>
    <li>
        <p><strong>Container:</strong> On the lab PC (host), start <strong>one</strong> container with host networking &amp; your workspaces mounted:</p>
        <pre><code class="language-bash">xhost +local:docker

docker run --rm -it \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/workspaces:/workspaces \
  --name ros2_lab \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest bash
</code></pre>
        <p>Then launch <strong>Terminator inside the container</strong>:</p>
        <pre><code class="language-bash">terminator &amp;
</code></pre>
        <p>Use panes (Ctrl+Shift+O/E). Do <strong>not</strong> start a second container.</p>
    </li>
</ul>
<h3>B) Safety first (read this)</h3>
<ul>
    <li>
        <p><strong>Clear workspace.</strong> No clutter, keep fingers and sleeves clear.</p>
    </li>
    <li>
        <p><strong>One operator.</strong> Others stand back.</p>
    </li>
    <li>
        <p><strong>E-stop.</strong> Locate it and be ready to press.</p>
    </li>
    <li>
        <p><strong>Conservative motion.</strong> Larger clearances, shorter moves, slow sequences.</p>
    </li>
</ul>
<h3>C) Station/IP specifics</h3>
<ul>
    <li>
        <p>Each robot has a posted IP (default often <code>192.168.1.10</code>, but <strong>use your station&rsquo;s label</strong>).</p>
    </li>
    <li>
        <p>Quick reachability check <strong>inside the container</strong>:</p>
        <pre><code class="language-bash">ping -c 2 &lt;ROBOT_IP&gt;
</code></pre>
        <p>If ping fails, tell your TA&mdash;don&rsquo;t troubleshoot cabling.</p>
    </li>
</ul>
<h3>D) Pane A &mdash; Launch the <strong>hardware driver</strong> (no Gazebo)</h3>
<p>Inside the container, open a new pane (Pane A), source ROS, and launch the real driver:</p>
<pre><code class="language-bash">source /opt/ros/$ROS_DISTRO/setup.bash

ros2 launch kortex_bringup gen3_lite.launch.py \
  robot_ip:=&lt;ROBOT_IP&gt; \
  gripper:=gen3_lite_2f \
  launch_rviz:=false
</code></pre>
<p>Keep Pane A <strong>running</strong>. You should see successful connection logs.</p>
<h3>E) Pane B &mdash; Launch <strong>MoveIt + RViz</strong> for hardware</h3>
<p>Open another pane (Pane B), source ROS, and bring up MoveIt for the same robot IP:</p>
<pre><code class="language-bash">source /opt/ros/$ROS_DISTRO/setup.bash

ros2 launch kinova_gen3_lite_moveit_config robot.launch.py \
  robot_ip:=&lt;ROBOT_IP&gt; \
  launch_driver:=false
</code></pre>
<p>RViz should open and show the robot. (No <code>use_sim_time</code> on hardware.)</p>
<h3>F) Pane C &mdash; Build your Lab 6 node and set <strong>real</strong> block poses</h3>
<p>Open Pane C (inside the container):</p>
<pre><code class="language-bash">source /opt/ros/$ROS_DISTRO/setup.bash
cd /workspaces/[netid]_robotics_fall2025/lab06/ros2_ws
colcon build --symlink-install
source install/setup.bash
</code></pre>
<p><strong>Update positions for real blocks:</strong></p>
<ul>
    <li>
        <p>Place 1&ndash;3 real blocks where you want them.</p>
    </li>
    <li>
        <p>Measure/estimate each block&rsquo;s <strong>(x, y)</strong> from the base; set <strong>z_center = table_height + BLOCK_SIZE/2</strong>.</p>
    </li>
    <li>
        <p>Edit <code>pick_and_place.py</code>:</p>
        <ul>
            <li>
                <p><code>self.block_centers["block_1/2/3"] = (x, y, z_center)</code></p>
            </li>
            <li>
                <p><code>self.stack_base_center = (x_stack, y_stack, z_center_layer0)</code></p>
            </li>
        </ul>
    </li>
    <li>
        <p>Rebuild + <code>source</code> again in Pane C.</p>
    </li>
</ul>
<p><strong>Gripper gentleness:</strong> If closing crushes the block, increase the <strong>closed</strong> joint value in your <code>GripperInterface(...)</code> init slightly (e.g., 0.02&ndash;0.05), rebuild, and retry. Keep <code>SURFACE_OFFSET</code> small (1&ndash;2 mm).</p>
<h3>G) First hardware run &mdash; one safe cycle</h3>
<p>Run a <strong>single</strong> pick&rarr;place on <code>block_1</code>:</p>
<pre><code class="language-bash">ros2 run lab06_moveit pick_and_place --ros-args -p task:=pick_place_demo -p target_id:=block_1
</code></pre>
<p>Watch the approach closely. If anything looks unsafe, <strong>Ctrl-C</strong> (Pane C) or hit the <strong>E-stop</strong>.</p>
<p><strong>Milestone 4 (optional):</strong> One safe pick&rarr;place on hardware.<br /><strong>Deliverable:</strong> screenshot or 20&ndash;40 s clip of the full cycle.</p>
<p><strong>Common quick fixes</strong></p>
<ul>
    <li>
        <p><strong>Height off:</strong> adjust <code>z_center</code> and/or <code>SURFACE_OFFSET</code>.</p>
    </li>
    <li>
        <p><strong>Near collisions:</strong> increase <code>CLEARANCE_Z</code>, move the stack target farther out, slow the sequence (add short sleeps).</p>
    </li>
    <li>
        <p><strong>Gripper no-go:</strong> <code>ros2 action list | grep gripper</code> to confirm the action name; match it in your <code>GripperInterface(...)</code>.</p>
    </li>
</ul>
<blockquote>
    <p><strong>Do not</strong> run Gazebo or the spawner during hardware use. Only Panes A (driver), B (MoveIt/RViz), and C (your node) should be active.</p>
</blockquote>
<hr />
<h2>5.9 Tear-Down &amp; Cleanup (Lab PCs)</h2>
<h3>Pane C &mdash; Planning-scene hygiene</h3>
<ul>
    <li>
        <p>Confirm <strong>Attached Objects</strong> is empty in RViz.</p>
    </li>
    <li>
        <p>If you added world objects for testing and want to clear them, remove via RViz Scene Objects or your helper (optional).</p>
    </li>
</ul>
<h3>Panes A &amp; B &mdash; Stop bring-ups</h3>
<ul>
    <li>
        <p><strong>Hardware:</strong> Ctrl-C in Pane A (driver) and Pane B (MoveIt/RViz). Follow lab policy for safing the arm (power/enable state).</p>
    </li>
</ul>
<h3>Container &mdash; exit &amp; verify</h3>
<p>From the container shell:</p>
<pre><code class="language-bash">exit
</code></pre>
<p>From the lab PC (host), confirm no stray containers:</p>
<pre><code class="language-bash">docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
</code></pre>
<p>If you still see <code>ros2_lab</code> and meant to stop it:</p>
<pre><code class="language-bash">docker stop ros2_lab
</code></pre>
<h3>Files &amp; repo</h3>
<ul>
    <li>
        <p>Push any code changes you made on the lab PC back to your repo:</p>
        <pre><code class="language-bash">cd ~/workspaces/[netid]_robotics_fall2025
git status
git add -A
git commit -m "Lab 6 hardware adjustments"
git push</code></pre>
    </li>
</ul>
<hr />
<h1>6 Analysis &amp; Discussion</h1>
<p>Answer each question in <strong>2&ndash;4 clear sentences</strong>. Your answers should be based on your experience running the lab and observing the provided code.</p>
<ol>
    <li>
        <p><strong>Straight-Line vs. Flexible Moves.</strong><br />In the lab's code, the robot moves in a straight line (a "Cartesian" path) for the final descent to grasp a block. Why is a straight-line motion essential for this specific action? In contrast, why is a more flexible, non-Cartesian plan perfectly acceptable for the first big movement from the robot's starting position to the pre-grasp pose above the block?</p>
    </li>
    <li>
        <p><strong>Why Plans Can Fail.</strong><br />A straight-line (Cartesian) motion plan isn't always successful. Based on your experience in this lab, describe two different reasons why a plan might fail while the robot is trying to pick up or place a block (e.g., colliding with something, or the arm being unable to reach). What is the first thing you would try to adjust in the code to fix such a failure?</p>
    </li>
    <li>
        <p><strong>The Importance of "Attaching" an Object.</strong><br />The commands <code>attach_collision_object</code> and <code>detach_collision_object</code> don't move the real robot at all, but they are critical for success. First, explain in your own words what "attaching" an object tells the MoveIt planner. Then, describe what would likely go wrong if you forgot to call <code>attach_collision_object</code> right after the gripper closed on the block.</p>
    </li>
    <li>
        <p><strong>Keeping the Planner Honest.</strong><br />At the start of the lab, you ran the <code>add_scene</code> task to put a table and blocks into RViz. What is the purpose of adding these "collision objects" to the planning scene? If you forgot this step and tried to run the pick-and-place task, what disastrous thing might the robot arm try to do, and why would this be dangerous?</p>
    </li>
    <li>
        <p><strong>Beyond Hard-Coded Poses.</strong><br />In the starter code, the exact XYZ coordinates of the blocks are hard-coded. While this works for our controlled lab environment, it's not a robust solution for the real world. Describe one reason why hard-coding positions is risky or limiting. If you could add a camera to the robot, what information would you want the camera to provide to make the grasping code more reliable?</p>
    </li>
</ol>
<hr />
<h1>8 Expected Final File Tree</h1>
<p>Your final pushed repository for Lab 6 should look like this:</p>
<pre><code>[netid]_robotics_fall2025/
└─ lab06/
   ├─ README.md
   ├─ .gitignore
   ├─ docs/
   │  ├─ 01_environment_setup.png
   │  ├─ 02_single_stack.png
   │  ├─ 03_final_stack_gazebo.png
   │  └─ 04_final_stack_rviz.png
   └─ ros2_ws/
      ├─ src/
      │  └─ lab06_moveit/
      │     ├─ package.xml
      │     ├─ setup.py
      │     ├─ setup.cfg
      │     └─ lab06_moveit/
      │        ├─ __init__.py
      │        └─ scripts/
      │           └─ pick_and_place.py
      ├─ build/                      # DO NOT COMMIT
      ├─ install/                    # DO NOT COMMIT
      └─ log/                        # DO NOT COMMIT
</code></pre>

</div>
