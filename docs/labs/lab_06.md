---
title: "Lab 06: Pick-and-Place Manipulation"
---

# Lab 06: Pick-and-Place Manipulation

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1: Bring Up the Simulation</a></li>
                <li><a href="#part2">Part 2: Milestone 1, Pick (Worked Example)</a></li>
                <li><a href="#part3">Part 3: Milestone 2, Place</a></li>
                <li><a href="#part4">Part 4: Milestone 3, A Tower from a Loop</a></li>
                <li><a href="#part5">Part 5: Milestone 4, Check the Grasp and Recover</a></li>
                <li><a href="#part6">Part 6: Optional, Run on the Real Arm</a></li>
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
    <p>The simulated Kinova Gen3 Lite picks up blocks and stacks them into a tower. You write the placement and stacking routines, then use finger readings to detect a missed grasp and choose a recovery policy.</p>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>The lab at a glance</strong>
        <table style="border-collapse: collapse; width: 100%; margin-top: 0.5em;">
            <tr><td style="padding: 4px 8px;"><strong>Pre-lab</strong></td><td style="padding: 4px 8px;">Accept, clone, pull the image, create and check your package, build, push.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 1</strong></td><td style="padding: 4px 8px;">Three terminals: the simulation, MoveIt, and your code.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 1</strong></td><td style="padding: 4px 8px;">Run the worked <code>pick()</code>. Screenshot.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 2</strong></td><td style="padding: 4px 8px;">Write <code>place()</code>; put the red block on the blue one. Screenshot.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 3</strong></td><td style="padding: 4px 8px;">Stack both outer blocks on the blue one with a loop. Two screenshots.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 4</strong></td><td style="padding: 4px 8px;">Detect a missed grasp and recover. Design choice, with evidence.</td></tr>
        </table>
    </div>
    <h3>1.2 Background</h3>
    <p><strong>A pick-and-place cycle</strong> has eight steps. Six move the arm or gripper. The other two, <strong>attach</strong> and <strong>detach</strong>, update MoveIt&rsquo;s planning scene and do not move anything.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/d01-pick-place-sequence.svg" alt="The eight steps: approach, descend, close, attach, lift, transit and place, open, detach and retreat; attach and detach change the planning scene only" style="max-width: 100%; height: auto;" /></p>
    <p><strong>Attach and detach.</strong> Before a grasp, a block is part of the world, and the planner keeps the robot away from it. <code>attach_collision_object</code> makes the block part of the robot, so the planner lets the fingers touch it and keeps the block itself clear of everything else. <code>detach_collision_object</code> puts it back in the world where it was released.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/d03-attach-detach.svg" alt="Before the grasp the block is in the world; after attach it is part of the robot; after detach it is back in the world" style="max-width: 100%; height: auto;" /></p>
    <p><strong>Gazebo and the planning scene.</strong> Gazebo simulates block positions. MoveIt plans from its planning scene, which your code updates. The finger position provides a grasp check: the fingers stop early on a block and close fully on an empty grasp. Milestone 4 uses that reading.</p>
    <p><strong>The station.</strong> As at the lab benches, the arm stands on a quick mount bolted to an aluminum plate on the table, and three 50 mm blocks sit in a row in front of it: red <code>block_1</code>, blue <code>block_2</code>, and yellow <code>block_3</code>. The tower is built on the blue block where it sits.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/d02-block-layout.svg" alt="Top view: the three blocks in a row at x = 0.44 m, block_1 red at y = -0.168, block_2 blue at y = 0.012 and the tower base, block_3 yellow at y = 0.192. Side view: the tabletop at z = -0.0627 m, GRASP_HEIGHT 0.119 m and APPROACH_HEIGHT 0.274 m as heights of end_effector_link" style="max-width: 100%; height: auto;" /></p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Implement</strong> a place routine by analogy to a worked pick routine, sequencing arm motion, gripper commands, and planning-scene updates.</li>
        <li><strong>Explain</strong> what attaching and detaching an object change in the planning scene, and what fails when either is left out.</li>
        <li><strong>Generalize</strong> a hand-written placement into a loop driven by block data.</li>
        <li><strong>Compare</strong> MoveIt&rsquo;s planning scene with the block positions in Gazebo.</li>
        <li><strong>Design</strong> a grasp check and a recovery policy from measured finger positions, and <strong>justify</strong> both with evidence from your own runs.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab.</strong> Everything in this section happens on your own time. Lab time starts at Part 1.</div>
    <p>VMs power off 4 hours after the reservation starts; keep your work in <code>~/workspaces</code> and push after each milestone. Git runs on the VM, ROS 2 runs in the container, and you edit in VS Code on the VM, as in Labs 4 and 5.</p>
    <ol>
        <li><strong>Make room, then pull the course image.</strong> The Kinova image has been updated since Lab 5 and the VM cannot hold both versions.
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker system prune -a --volumes -f</code></pre>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
            <p>The prune deletes unused images and stopped containers, not your files. If the pull stops with <code>no space left on device</code>, run the prune again and pull again.</p>
                    </li>
        <li><strong>Accept Lab 6 and clone it.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-06</code></pre>
            <p>Clone into <code>~/workspaces</code> with the command it prints, and <code>cd</code> into the repository. If <code>gh student</code> is missing or not signed in, repeat the Lab 1 setup (<code>gh extension install foundation50/gh-student</code>, then <code>gh student login</code>).</p>
        </li>
        <li><strong>Start the container.</strong> The Lab 5 command, named <code>lab06</code>:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab06 --net=host --gpus all -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
            <p>Exiting this terminal deletes the container and closes every <code>docker exec</code> shell; files in <code>~/workspaces</code> stay. If it fails with <code>could not select device driver</code>, run it without <code>--gpus all</code> and tell a TA.</p>
        </li>
        <li><strong>Create the package.</strong> You did this in Labs 4 and 5. In the container, from your repository&rsquo;s <code>ros2_ws/src</code> (create the folder first), make an <code>ament_python</code> package named <code>lab06_moveit</code> with the dependencies <code>rclpy geometry_msgs sensor_msgs moveit_msgs pymoveit2</code>, and give it a <code>scripts</code> subpackage (the folder <code>lab06_moveit/lab06_moveit/scripts</code> with an empty <code>__init__.py</code>). Then fix the file ownership on the VM.
            <details>
                <summary>Hint: the commands</summary>
                <p><strong>Location:</strong> Container Terminal</p>
                <pre><code class="language-bash">mkdir -p ~/workspaces/intro-to-robotics-fall-2026-lab-06-YOUR_GITHUB_USERNAME/ros2_ws/src
cd ~/workspaces/intro-to-robotics-fall-2026-lab-06-YOUR_GITHUB_USERNAME/ros2_ws/src
ros2 pkg create --build-type ament_python lab06_moveit --dependencies rclpy geometry_msgs sensor_msgs moveit_msgs pymoveit2
mkdir -p lab06_moveit/lab06_moveit/scripts
touch lab06_moveit/lab06_moveit/scripts/__init__.py</code></pre>
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">sudo chown -R $USER:$USER ~/workspaces/intro-to-robotics-fall-2026-lab-06-YOUR_GITHUB_USERNAME</code></pre>
            </details>
        </li>
        <li><strong>Copy in the starter files and register three entry points.</strong> Copy the five files from <code>scaffolds/</code> into the package&rsquo;s <code>scripts</code> folder, and add console-script entry points named <code>pick_and_place</code>, <code>blocks</code>, and <code>grasp_watcher</code>, each pointing at the <code>main</code> function of the script with the same name.
            <details>
                <summary>Hint: the copy command and the setup.py block</summary>
                <p><strong>Location:</strong> Host VM Terminal, repository root</p>
                <pre><code class="language-bash">cp scaffolds/*.py ros2_ws/src/lab06_moveit/lab06_moveit/scripts/</code></pre>
                <p><strong>Location:</strong> File Editor, <code>ros2_ws/src/lab06_moveit/setup.py</code>:</p>
                <pre><code class="language-python">entry_points={
    'console_scripts': [
        'pick_and_place = lab06_moveit.scripts.pick_and_place:main',
        'blocks = lab06_moveit.scripts.blocks:main',
        'grasp_watcher = lab06_moveit.scripts.grasp_watcher:main',
    ],
},</code></pre>
            </details>
            <p>Only <code>pick_and_place.py</code> is yours to edit. <code>arm.py</code>, <code>blocks.py</code>, <code>grasp_watcher.py</code>, and <code>table.py</code> are complete; the manual explains each where you first use it.</p>
        </li>
        <li><strong>Check the package before building.</strong>
            <p><strong>Location:</strong> Host VM Terminal, repository root</p>
            <pre><code class="language-bash">python3 check_package.py</code></pre>
            <p><strong>Checkpoint:</strong> <code>Package setup looks right.</code> If it lists problems, each one comes with the command or edit that fixes it. Fix them in order and run it again.</p>
        </li>
        <li><strong>Build, then push.</strong>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-06-YOUR_GITHUB_USERNAME/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 pkg executables lab06_moveit</code></pre>
            <p><strong>Checkpoint:</strong> three lines, <code>lab06_moveit blocks</code>, <code>lab06_moveit grasp_watcher</code>, and <code>lab06_moveit pick_and_place</code>. Then commit and push <code>ros2_ws</code> from the Host VM Terminal.</p>
        </li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>python3 check_package.py</code> prints <code>Package setup looks right.</code></li>
        <li>[ ] <code>ros2 pkg executables lab06_moveit</code> lists all three executables.</li>
        <li>[ ] <code>git status</code> is clean on <code>main</code>, and <code>df -h /</code> shows at least 1 GB free.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1: Bring Up the Simulation</h3>
        <p><strong>Goal:</strong> the simulation, MoveIt, and a terminal for your code, each in its own container shell.</p>
        <p>Start the container (pre-lab step 3) and open two more shells from new Host VM Terminals with <code>docker exec -it lab06 bash</code>. <strong>Prepare</strong> Terminals 1 and 3 by sourcing your workspace:</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-06-YOUR_GITHUB_USERNAME/ros2_ws &amp;&amp; source install/setup.bash</code></pre>
        <h4>Step 1.1: Terminal 1, the simulation</h4>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-06-YOUR_GITHUB_USERNAME &amp;&amp; ros2 launch lab06_sim.launch.py</code></pre>
        <p><strong>Checkpoint:</strong> Gazebo shows the arm on its mount and plate on the table, and the terminal prints <code>Grasp watcher ready</code>. Leave it running. If <code>ros2 launch</code> says it cannot find the file, the terminal is not in the repository root; run the line above as written.</p>
        <details>
            <summary>Why? What this launch starts</summary>
            <p>It starts the Lab 5 Gazebo launch with the lab&rsquo;s arguments, adds the station (table, plate, and quick mount, modeled from the real parts), and starts the <strong>grasp watcher</strong>. In simulation, fingers alone do not hold a block well: it slips while the arm moves and is pushed sideways when the fingers open. The watcher holds the block instead: when the fingers stop partway closed on a block, it fixes the block to the gripper in Gazebo, and when they open it releases the block. It changes Gazebo only. Your code attaches and detaches in the planning scene exactly as it would on the real arm, where the watcher is not run.</p>
        </details>
        <h4>Step 1.2: Terminal 2, MoveIt and RViz</h4>
        <pre><code class="language-bash">ros2 launch kinova_gen3_lite_moveit_config sim.launch.py use_sim_time:=true</code></pre>
        <p><strong>Checkpoint:</strong> <code>MoveGroup context initialization complete</code>. In RViz, choose <strong>File &rarr; Open Config</strong>, open <code>lab06.rviz</code> from your repository, and choose <strong>Discard</strong>. When a plan fails, MoveIt logs the reason in this terminal.</p>
        <h4>Step 1.3: Terminal 3, the blocks</h4>
        <pre><code class="language-bash">ros2 run lab06_moveit blocks reset</code></pre>
        <pre><code class="language-bash">ros2 run lab06_moveit blocks where</code></pre>
        <p><strong>Checkpoint:</strong> three blocks in Gazebo and three cubes in RViz, red, blue, and yellow like the Gazebo blocks, and <code>blocks where</code> prints each block&rsquo;s position in Gazebo beside its position in the planning scene. They agree to a millimeter or two. Terminal 3 is where you run everything else in this lab. Set your NetID in <code>pick_and_place.py</code> (the <code>NETID</code> line at the top).</p>
    </section>
    <section id="part2">
        <h3>Part 2: Milestone 1, Pick (Worked Example)</h3>
        <p><strong>Goal:</strong> pick up <code>block_1</code> and see what attaching it changes.</p>
        <p>Read <code>pick()</code> and <code>run_milestone_1()</code> in <code>pick_and_place.py</code>. Note which moves are straight lines, and where <code>attach_collision_object</code> is called relative to the close.</p>
        <details>
            <summary>Why? The helpers pick() calls (arm.py)</summary>
            <ul>
                <li><code>start()</code> folds the arm to <code>RETRACT</code> (the arm&rsquo;s own parked pose) and then moves to <code>WORK</code>, a pose from which the blocks can be reached.</li>
                <li><code>move_to_pose(x, y, z)</code> moves the gripper, pointing down, to a point. <code>cartesian=True</code> requires a straight line; <code>speed=</code> (0.01 to 1.0) slows the motion. It retries a failed plan three times and returns <code>False</code> if all fail.</li>
                <li><code>open_gripper()</code> and <code>close_gripper()</code> return the <strong>measured</strong> finger position once the fingers stop.</li>
                <li><code>APPROACH_HEIGHT</code> and <code>GRASP_HEIGHT</code> are heights of <code>end_effector_link</code> above the arm&rsquo;s base. At <code>GRASP_HEIGHT</code> the fingertips are level with the middle of a block on the table. They are the heights the real arm uses at the lab stations.</li>
            </ul>
        </details>
        <pre><code class="language-bash">ros2 run lab06_moveit pick_and_place 1</code></pre>
        <p><strong>Checkpoint:</strong> the arm picks up the red block and holds it for 15 seconds. In RViz the red block moves with the gripper. The terminal shows both finger readings, the second after the script closes the empty gripper for comparison:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[INFO] [pick_and_place]: block_1: fingers closed at 0.431
[INFO] [pick_and_place]: Empty gripper: fingers closed at 0.800</code></pre>
        </div>
        <p>A line <code>Action '/gen3_lite_2f_gripper_controller/gripper_cmd' was unsuccessful: 5</code> when the gripper opens is expected: a close that is pressing on a block never reports success, so opening cancels it.</p>
        <p><strong>Screenshot:</strong> RViz and Gazebo side by side while the block is held. Save it as <code>docs/m1_holding.png</code>. Copy the terminal output into your PDF.</p>
        <p><em>Example (yours shows your own NetID and timing):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/s01-m1-holding.png" alt="Milestone 1: Gazebo on the left and RViz on the right, the arm holding the red block above the table" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part3">
        <h3>Part 3: Milestone 2, Place</h3>
        <p><strong>Goal:</strong> write <code>place()</code> and use it to put <code>block_1</code> on top of <code>block_2</code>.</p>
        <p><strong>Contract for <code>place(block_id, x, y, layer)</code>:</strong> the gripper holds <code>block_id</code> at <code>APPROACH_HEIGHT</code>. Lower it, in a straight line at <code>speed=PLACE_SPEED</code>, until its bottom is <code>PLACE_CLEARANCE</code> above the surface <code>layer</code> blocks up (0 is the table). Release it, update the planning scene, and return to <code>APPROACH_HEIGHT</code> in a straight line. Return <code>False</code> as soon as a motion fails, <code>True</code> otherwise.</p>
        <p><strong>Contract for <code>run_milestone_2</code>:</strong> pick <code>block_1</code> and place it on <code>block_2</code> (at <code>TOWER_XY</code>, layer 1). Log an error and stop if a step fails.</p>
        <details>
            <summary>Hint 1: Read pick() backwards</summary>
            <p><code>pick()</code> ends holding a block at <code>APPROACH_HEIGHT</code>; <code>place()</code> starts there. Write the steps of <code>pick()</code> in reverse and decide what changes in each.</p>
        </details>
        <details>
            <summary>Hint 2: The release height</summary>
            <p>At <code>GRASP_HEIGHT</code>, a held block&rsquo;s bottom is level with the table. Each block below adds <code>BLOCK_SIZE</code>.</p>
        </details>
        <details>
            <summary>Hint 3: The planning-scene call</summary>
            <pre><code class="language-python">self.moveit2.detach_collision_object(block_id)
time.sleep(0.5)   # let the planning scene update</code></pre>
            <p>Open the fingers first; until then the block is still in the gripper.</p>
        </details>
        <pre><code class="language-bash">ros2 run lab06_moveit pick_and_place 2</code></pre>
        <p><strong>Checkpoint:</strong> the red block sits on the blue one in Gazebo and in RViz.</p>
        <p><strong>Screenshot:</strong> Gazebo showing the two-block stack. Save it as <code>docs/m2_two_block_stack.png</code>.</p>
        <p><em>Example (yours shows your own NetID and timing):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/s02-m2-two-block-stack.png" alt="Gazebo after milestone 2: the red block on top of the blue block, the yellow block still at its start" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part4">
        <h3>Part 4: Milestone 3, A Tower from a Loop</h3>
        <p><strong>Goal:</strong> replace the hand-written placement with a loop.</p>
        <p><strong>Contract for <code>run_milestone_3</code>:</strong> stack <code>block_1</code> and then <code>block_3</code> on <code>block_2</code> using <code>pick()</code> and your <code>place()</code> in a loop. Take each block&rsquo;s position from <code>BLOCKS</code> and its layer from the loop, not from numbers typed in per block. Stop with an error message if a step fails, and log how many blocks were placed.</p>
        <details>
            <summary>Hint 1: What the loop needs</summary>
            <p>Each time around: the block&rsquo;s id, its (<em>x</em>, <em>y</em>) from <code>BLOCKS[block_id][1]</code>, and its layer. <code>for layer, block_id in enumerate(order, start=1):</code> gives both.</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> print the id, position, and layer your loop produces and compare them with milestone 2. If a block lands off the tower, run <code>blocks where</code>. If a plan fails, read Terminal 2. After one clean retry with <code>blocks reset</code> or 10 minutes without progress, ask a TA and show the log line that disagrees with what you expected.</blockquote>
        <pre><code class="language-bash">ros2 run lab06_moveit pick_and_place 3</code></pre>
        <p><strong>Checkpoint:</strong> a three-block tower in Gazebo and in RViz, and a final line saying 2 of 2 blocks were placed.</p>
        <p><strong>Screenshots:</strong> Gazebo showing the tower, saved as <code>docs/m3_tower_gazebo.png</code>, and RViz showing it, saved as <code>docs/m3_tower_rviz.png</code>. Then run <code>ros2 run lab06_moveit blocks where</code> and copy its output into your PDF; Question 2 uses it.</p>
        <p><em>Example (yours shows your own NetID and timing):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/s03-m3-tower-gazebo.png" alt="Gazebo after milestone 3: a tower of blue, red, and yellow blocks" style="max-width: 100%; height: auto;" /></p>
        <p><em>Example (yours shows your own NetID and timing):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab06/s04-m3-tower-rviz.png" alt="RViz after milestone 3: the same tower in the planning scene, blue, red, and yellow" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part5">
        <h3>Part 5: Milestone 4, Check the Grasp and Recover</h3>
        <p><strong>Goal:</strong> detect a missed grasp in the tower routine and choose a recovery policy.</p>
        <p><code>pick()</code> attaches whether or not the fingers caught anything. After a miss, MoveIt plans with a block attached to an empty gripper. Your milestone 1 output has a reading with a block and a reading with nothing; run milestone 1 two or three more times to see how much each varies.</p>
        <p><strong>Contract for <code>run_milestone_4</code>:</strong></p>
        <ul>
            <li>Build the tower as in milestone 3, but after each close decide whether the gripper holds a block, from the finger reading and a threshold you chose from your measurements. Attach only if it does.</li>
            <li>When it does not, carry out a recovery policy of your choice: retry the same spot, find the block and retry there (<code>gazebo_position(block_id)</code> from <code>blocks.py</code> stands in for a camera), skip it, or stop at <code>WORK</code>. MoveIt must never plan with a block attached when the gripper is not holding it.</li>
            <li>Log each decision with the reading that caused it.</li>
        </ul>
        <details>
            <summary>Hint 1: Where the check goes</summary>
            <p>Between the close and the attach. Write a new method, for example <code>pick_checked()</code>, so milestones 1&ndash;3 keep working.</p>
        </details>
        <details>
            <summary>Hint 2: Correcting the planning scene before a retry</summary>
            <pre><code class="language-python">self.moveit2.move_collision(block_id, (x, y, z), (0.0, 0.0, 0.0, 1.0), "base_link")</code></pre>
        </details>
        <p>Milestone 4 does not reset the blocks, so you can set up a miss first. Run it twice, and run <code>blocks where</code> after each run:</p>
        <pre><code class="language-bash">ros2 run lab06_moveit blocks reset</code></pre>
        <pre><code class="language-bash">ros2 run lab06_moveit pick_and_place 4</code></pre>
        <p>and again after <code>blocks reset</code> followed by <code>ros2 run lab06_moveit blocks nudge block_3</code>, which moves the yellow block aside in Gazebo only.</p>
        <p><strong>Checkpoint:</strong> without the nudge, a three-block tower; with it, the miss on <code>block_3</code> logged with its reading, then your recovery. In both runs, <code>blocks where</code> lists no block as <code>attached to the gripper</code>.</p>
        <p><strong>Design justification</strong> (a short paragraph in your PDF): the threshold and the readings it separates; the policy you chose, one alternative you rejected, and why (consider a block that fell off the table); and one failure your check would not catch. Copy both runs&rsquo; terminal output and <code>blocks where</code> output into your PDF.</p>
    </section>
    <section id="part6">
        <h3>Part 6: Optional, Run on the Real Arm</h3>
        <p>Optional and not graded, at a lab station with a TA present. The station matches the simulation (same mount, plate, heights, and block positions), so your code runs unchanged.</p>
                <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Safety:</strong> only your team at your station. One operator; everyone else stands back. Hands, bodies, and loose items stay out of the workspace while the arm is powered. Find the emergency stop before the first motion and keep a hand near it. Run one milestone at a time; stop at anything unexpected.</blockquote>
        <ol>
            <li>On the lab PC, clone or pull your repository and start the container with the pre-lab command. Do not start the simulation launch or the grasp watcher.</li>
            <li><code>ping -c 2 ROBOT_IP</code> with the IP posted at the station. If it fails, tell a TA.</li>
            <li>In two container terminals: <code>ros2 launch kortex_bringup gen3_lite.launch.py robot_ip:=ROBOT_IP gripper:=gen3_lite_2f launch_rviz:=false</code> and <code>ros2 launch kinova_gen3_lite_moveit_config robot.launch.py robot_ip:=ROBOT_IP launch_driver:=false</code>.</li>
            <li>Place the blocks on the marked positions and run <code>blocks reset</code> (it updates only the planning scene when there is no Gazebo). Run milestone 1, watching the whole approach. Then milestone 2 or 3.</li>
            <li>Shut down: check that RViz shows nothing attached, stop both launches, follow the station&rsquo;s power-down procedure, and push from the host.</li>
        </ol>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p><strong>Where the answers go:</strong> in your Gradescope PDF, after the milestone 4 justification. All four are graded. Answer each in a few sentences from your own runs.</p>
    <h3>Question 1: Leaving out the attach</h3>
    <ul>
        <li>Comment out the <code>attach_collision_object</code> line in <code>pick()</code> and run milestone 1. What happened, and what did Terminal 2 log? Restore the line afterwards. Explain the result from what the planning scene contained.</li>
    </ul>
        <h3>Question 2: The planning scene and Gazebo</h3>
    <ul>
        <li>From your <code>blocks where</code> output after milestone 3: how far is each block in Gazebo from where the planning scene has it, where does the difference come from, and how large would it have to be to make the next pick or place fail?</li>
    </ul>
    <h3>Question 3: Straight lines and free paths</h3>
    <ul>
        <li>In <code>pick()</code> and your <code>place()</code>, which moves are straight lines and which let MoveIt choose the path? Why each?</li>
    </ul>
    <h3>Question 4: What a camera would add</h3>
    <ul>
        <li>In milestone 4, <code>gazebo_position()</code> returned a block&rsquo;s position in Gazebo. What would a real robot need instead, and what would it have to report for your recovery policy to work?</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Recurring setup, Docker, ROS 2, and MoveIt problems are on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#moveit-2-and-kinova-workflows" target="_blank" rel="noopener">Troubleshooting</a>. For this lab: package setup problems (run <code>check_package.py</code> first), <code>Error code: 99999</code> on a failed plan, <code>terminate called without an active exception</code> at the end of a run, controllers that do not start, and a black Gazebo window.</p>
        <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://moveit.picknik.ai/main/doc/examples/planning_scene/planning_scene_tutorial.html" target="_blank" rel="noopener">MoveIt 2: Planning Scene tutorial</a> (attached objects)</li>
        <li><a href="https://github.com/AndrejOrsula/pymoveit2" target="_blank" rel="noopener">pymoveit2</a></li>
        <li><a href="https://github.com/Kinovarobotics/ros2_kortex" target="_blank" rel="noopener">Kinova ros2_kortex</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/pymoveit2_api_guide/" target="_blank" rel="noopener">pymoveit2 API guide</a>: planning, collision objects, attaching and detaching.</li>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/kinova_gen3_lite_moveit2_guide/" target="_blank" rel="noopener">Kinova Gen3 Lite MoveIt 2 guide</a>: groups, joints, frames, and controllers.</li>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: build and source reminders, ROS 2 CLI checks, Git and Docker commands.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
