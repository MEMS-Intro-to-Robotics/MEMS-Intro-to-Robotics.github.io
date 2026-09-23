---
title: "Lab 03: Shell Scripting for Robot Control"
---

# Lab 03: Shell Scripting for Robot Control

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1 &mdash; Container Launch</a></li>
                <li><a href="#part1-5">Part 1.5 &mdash; Open the Repo in VS Code</a></li>
                <li><a href="#part2">Part 2 &mdash; Launch and Manual Control</a></li>
                <li><a href="#part3">Part 3 &mdash; Scripting Motion with Topics</a></li>
                <li><a href="#part4">Part 4 &mdash; Draw the First Letter of Your Name</a></li>
                <li><a href="#part5">Part 5 &mdash; Using Services for State Changes</a></li>
                <li><a href="#part6">Part 6 &mdash; Two-Turtle, Two-Letter Script</a></li>
            </ol>
        </li>
        <li><a href="#analysis">Analysis and Discussion</a></li>
        <li><a href="#troubleshooting">Troubleshooting</a></li>
        <li><a href="#references">References</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>In this lab, you will control a virtual turtle in turtlesim using shell scripts. You will use topics to send motion commands and services to change the state of the simulation.</p>
    <p>A shell script is a text file containing a sequence of Linux commands. Saving <code>ros2 topic pub</code> and <code>ros2 service call</code> commands in a <code>.sh</code> file lets you run, adjust, and repeat the same motion sequence.</p>
    <h3>1.2 Background</h3>
    <p>This lab uses two ROS 2 communication methods introduced in Lab 2:</p>
    <ul>
        <li><strong>Topics (Continuous Streams):</strong> Topics carry data such as sensor readings or velocity commands. In this lab, you will publish velocity commands to make a turtle move.
            <pre><code class="language-bash">ros2 topic pub &lt;topic_name&gt; &lt;msg_type&gt; &lt;msg_data&gt;</code></pre>
        </li>
        <li><strong>Services (Request/Response):</strong> A service handles a request and returns a response. In this lab, you will use services for one-time actions such as spawning or teleporting a turtle.
            <pre><code class="language-bash">ros2 service call &lt;service_name&gt; &lt;srv_type&gt; &lt;arguments&gt;</code></pre>
        </li>
    </ul>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Concept: Topics vs. Services</strong><br /><strong>Topics</strong> are like radio broadcasts: continuous streams you can &ldquo;tune in&rdquo; to.<br /><strong>Services</strong> are like phone calls: you ask once, get an answer, then hang up.</blockquote>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab03/d01-topics-vs-services.svg" alt="A topic as a continuous broadcast many nodes receive; a service as one request and one reply" style="max-width: 100%; height: auto;" /></p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Distinguish</strong> between the use cases for ROS 2 topics and services in a practical application.</li>
        <li><strong>Control</strong> a simulated robot programmatically by publishing messages to a topic from a shell script.</li>
        <li><strong>Modify</strong> the state of a simulation by calling services from the command line and from within a script.</li>
        <li><strong>Automate</strong> a sequence of ROS 2 commands to achieve a multi-step goal.</li>
        <li><strong>Organize</strong> your work in a Classroom 50 repository, commit your scripts with Git, and push them.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Accept and clone the assignment and pull the course image before arriving at lab. Lab time starts with the container launch in Part 1.</p>
    </div>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Important:</strong> VMs power off automatically 4 hours after the reservation starts. That stops the container and discards anything you wrote inside it outside <code>~/workspaces</code>; files on the VM itself stay where they are. Keep your work in that folder, and commit and push regularly: until you push, it exists only on the VM.</div>
    <ol>
        <li><strong>Verify Docker and GitHub access.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker --version
ssh -T git@github.com</code></pre>
            <p>Docker should print a version. GitHub should identify your account and report successful authentication.</p>
        </li>
        <li><strong>Pull the latest course image.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        </li>
        <li><strong>Install or verify the Classroom 50 student command.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh extension install foundation50/gh-student
gh student --help</code></pre>
            <p>If the extension is already installed, the first command may report that it exists. Continue when the help text is available.</p>
            <p>You signed in to <code>gh</code> during Lab 1, and that login carries over. If <code>gh student whoami</code> does not print your GitHub username (for example on a rebuilt VM), run <code>gh student login</code> before continuing.</p>
        </li>
        <li><strong>Accept Lab 3.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-03</code></pre>
            <p>Classroom 50 accepts a pending organization invitation, creates your private repository, and prints the exact <code>git clone</code> command. If you already accepted the assignment, it leaves your repository unchanged.</p>
        </li>
        <li><strong>Clone the repository.</strong> Run the clone command printed by Classroom 50. The expected repository name is:</li>
    </ol>
    <pre><code>MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-03-YOUR_GITHUB_USERNAME</code></pre>
    <p><strong>Location:</strong> Host VM Terminal. Always clone and push on the VM, never inside the container.</p>
    <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-03-YOUR_GITHUB_USERNAME.git
cd intro-to-robotics-fall-2026-lab-03-YOUR_GITHUB_USERNAME</code></pre>
    <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your GitHub username, and use the URL printed by Classroom 50 if it differs from the example. The starter already contains the empty <code>docs/</code> and <code>scripts/</code> folders you will fill during lab.</p>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code> succeeds.</li>
        <li>[ ] <code>git status</code> reports a clean working tree on <code>main</code>.</li>
        <li>[ ] <code>git remote -v</code> points to your Lab 3 repository.</li>
        <li>[ ] <code>ls -la</code> shows <code>README.md</code>, <code>docs/</code>, <code>scripts/</code>, and <code>test_lab_3.py</code>.</li>
        <li>[ ] You reviewed the topics and services pages of the <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html" target="_blank" rel="noopener">ROS 2 Jazzy Beginner CLI Tools tutorials</a> from Lab 2.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1 &mdash; Container Launch</h3>
        <p><strong>Goal:</strong> Start a named course container with your workspace mounted, and open a second shell into it.</p>
        <p>Run the ROS 2 commands inside the course container. The container name <code>lab03</code> will let you open additional terminals in the same environment. Complete any unfinished pre-lab checks before continuing.</p>
        <h4>Step 1.1: Start the named container</h4>
        <p>Start the standard course container. This is the same command shape as Labs 1 and 2, with the container name changed to <code>lab03</code>:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab03 --net=host -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        <ul>
            <li><code>--name lab03</code> sets the name used by the <code>docker exec</code> command in Step 1.2.</li>
            <li><code>-v ~/workspaces:/root/workspaces</code> makes your VM&rsquo;s <code>~/workspaces</code> folder available inside the container at <code>/root/workspaces</code>.</li>
            <li><code>xhost</code> + <code>DISPLAY</code> allows the turtlesim GUI to show on your desktop.</li>
            <li><code>-e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST</code> keeps your ROS 2 traffic on your own VM. The <code>docker run</code> command sets it every time, so you do not need to edit any <code>.bashrc</code>.</li>
        </ul>
        <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Warning:</strong> The <code>--rm</code> option deletes the container when you exit the original shell and closes terminals attached with <code>docker exec</code>. Files in the mounted <code>~/workspaces</code> folder remain on the VM.</blockquote>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Sourcing note:</strong> The course image&rsquo;s <code>~/.bashrc</code> already sources ROS 2 Jazzy, so <code>ros2</code> commands work in every container shell without any extra setup. No workspace sourcing is needed in this lab.</blockquote>
        <h4>Step 1.2: Open a second terminal</h4>
        <p>Get another shell into the same container:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">docker exec -it lab03 bash</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Alternative: Terminator</strong><br />You can also open Terminator inside the container:
            <pre><code class="language-bash">terminator</code></pre>
        </blockquote>
    </section>
    <section id="part1-5">
        <h3>Part 1.5 &mdash; Open the Repo in VS Code</h3>
        <p>On the VM, run:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">code ~/workspaces/intro-to-robotics-fall-2026-lab-03-YOUR_GITHUB_USERNAME</code></pre>
        <ul>
            <li>Edit files normally in VS Code. Because the repo is bind-mounted into the container at <code>~/workspaces</code>, your changes appear instantly inside the container.</li>
            <li>Use the VM terminals you opened in Part 1 to run commands.</li>
        </ul>
    </section>
    <section id="part2">
        <h3>Part 2 &mdash; Launch and Manual Control</h3>
        <p><strong>Goal:</strong> Start turtlesim, verify its topics are visible, and drive the turtle manually.</p>
        <h4>Step 2.1: Start turtlesim</h4>
        <p><strong>Location:</strong> Container Terminal (Terminal 1)</p>
        <pre><code class="language-bash">ros2 run turtlesim turtlesim_node</code></pre>
        <p><strong>Checkpoint:</strong> A blue GUI window should appear.</p>
        <h4>Step 2.2: Verify topics</h4>
        <p><strong>Location:</strong> Container Terminal (Terminal 2 &mdash; from Step 1.2)</p>
        <pre><code class="language-bash">ros2 topic list</code></pre>
        <p><strong>Checkpoint:</strong> You should see <code>/turtle1/cmd_vel</code> in the list.</p>
        <h4>Step 2.3: Start keyboard teleop</h4>
        <p><strong>Location:</strong> Container Terminal (Terminal 2)</p>
        <pre><code class="language-bash">ros2 run turtlesim turtle_teleop_key</code></pre>
        <p>Click Terminal 2 to focus it; use arrow keys to drive. This publishes to /turtle1/cmd_vel, which the simulator subscribes to.</p>
    </section>
    <section id="part3">
        <h3>Part 3 &mdash; Scripting Motion with Topics</h3>
        <p><strong>Goal:</strong> Publish velocity commands from a script instead of pressing keys.</p>
        <h4>Step 3.1: Create the script file in VS Code</h4>
        <p><strong>Location:</strong> File Editor (VS Code on the VM)</p>
        <p>In the Explorer, go to: <code>scripts</code> &rarr; <strong>New File</strong> &rarr; <code>turtleletter.sh</code></p>
        <p>Paste:</p>
        <pre><code class="language-bash">#!/usr/bin/env bash
set -euo pipefail

# Send a forward velocity pulse (turtlesim times out after about 1 second)
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once
sleep 1

# Send a turning velocity pulse
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}" --once
sleep 1

# Stop the turtle
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once</code></pre>
        <h4>Step 3.2: Make it executable &amp; run it</h4>
        <p><strong>Location:</strong> Container Terminal (Terminal 2). Stop the teleop node from Step 2.3 with <code>Ctrl+C</code> first. To open an additional container shell, run <code>docker exec -it lab03 bash</code> from a <strong>Host VM Terminal</strong>.</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-03-YOUR_GITHUB_USERNAME/scripts
chmod +x turtleletter.sh
./turtleletter.sh</code></pre>
        <p><strong>Checkpoint:</strong> The turtle drives forward, turns, and stops.</p>
        <p><strong>Timing in Jazzy:</strong> <code>--once</code> publishes one message and returns; turtlesim stops the turtle after about one second without a new velocity command. <code>sleep</code> pauses your script, not the simulator, so increasing <code>sleep</code> beyond one second does not extend a single pulse. Each CLI command also takes time to start and discover the turtle, so <code>sleep</code> is not an exact motion timer.</p>
    </section>
    <section id="part4">
        <h3>Part 4 &mdash; Draw the First Letter of Your Name</h3>
        <p><strong>Goal:</strong> Extend <code>turtleletter.sh</code> to trace the first letter of your name by chaining <code>ros2 topic pub</code> + <code>sleep</code>.</p>
        <ul>
            <li>Break the letter into straight segments + <strong>turns</strong>.</li>
            <li>Tune <code>linear.x</code> (forward speed, turtlesim units/s) and <code>angular.z</code> (turn rate, radians/s). Positive <code>angular.z</code> turns counterclockwise. Use <code>sleep</code> to space commands, remembering the one-second timeout above.</li>
            <li>For a longer segment, repeat velocity pulses or use a finite stream with <code>--rate 10 --times N</code> instead of <code>--once</code> (replace <code>N</code> with a positive message count). Send a zero-velocity command afterward; the last nonzero command otherwise persists until the timeout.</li>
            <li>Test the script and adjust these values until the turtle traces the letter.</li>
        </ul>
        <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab03/d02-script-timing.svg" alt="A velocity pulse and the sleep that follows it, showing why sleeping longer does not travel further" style="max-width: 100%; height: auto;" /></p>
        <p><em>Example of a finished letter:</em> the Duke &ldquo;D&rdquo; below was traced from an outline with <code>teleport_absolute</code> calls, so it is more exact than a letter drawn with velocity commands. Your letter only needs to be recognizable.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab03/s01-turtlesim-duke-d.png" alt="Example turtlesim window showing a white outline of the Duke D drawn by the turtle" width="350" height="350" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part5">
        <h3>Part 5 &mdash; Using Services for State Changes</h3>
        <p><strong>Goal:</strong> Use services for one-time actions.</p>
        <p><strong>Location:</strong> Container Terminal (Terminal 2) for every command in this part.</p>
        <h4>1. Spawn a second turtle</h4>
        <pre><code class="language-bash">ros2 service call /spawn turtlesim/srv/Spawn "{x: 1.0, y: 1.0, name: 'turtle2'}"</code></pre>
        <h4>2. Change pen color of the first turtle</h4>
        <pre><code class="language-bash">ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 5}"</code></pre>
        <p><code>r,g,b</code> are 0&ndash;255; add <code>'off': 1</code> inside the request to lift the pen. Keep the single quotes around <code>'off'</code>: unquoted YAML <code>off</code> can be interpreted as a boolean. To resume drawing, call <code>set_pen</code> again with the desired color, width, and <code>'off': 0</code>.</p>
        <h4>3. Teleport (instant move)</h4>
        <pre><code class="language-bash">ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute "{x: 5.5, y: 5.5, theta: 0.0}"</code></pre>
        <p><code>theta</code> is in radians; zero faces right. Teleporting with the pen down draws a connecting line, so lift the pen first when repositioning without drawing.</p>
        <h4>4. Control turtle2 with keyboard (remap topic)</h4>
        <pre><code class="language-bash">ros2 run turtlesim turtle_teleop_key --ros-args --remap /turtle1/cmd_vel:=/turtle2/cmd_vel</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Tip: Discovering a service&rsquo;s type</strong><br />If you know a service&rsquo;s name but not what type it uses, ask ROS 2:
            <pre><code class="language-bash">ros2 service type /clear</code></pre>
            <p>Then inspect the request/response fields with <code>ros2 interface show &lt;type&gt;</code>. You&rsquo;ll need this for the <code>/clear</code> service in Part 6.</p>
        </blockquote>
    </section>
    <section id="part6">
        <h3>Part 6 &mdash; Two-Turtle, Two-Letter Script</h3>
        <p><strong>Goal:</strong> Create <code>turtleletterstwo.sh</code> that draws the first two letters of your name simultaneously.</p>
        <p><strong>Before each run:</strong> Stop keyboard teleop with <code>Ctrl+C</code>. In Container Terminal 2, run the following to restore one centered turtle and remove <code>turtle2</code> from the previous run:</p>
        <pre><code class="language-bash">ros2 service call /reset std_srvs/srv/Empty "{}"</code></pre>
        <p><code>/clear</code> only erases the trails; it does not remove turtles or reset their positions or pens. Spawning another turtle named <code>turtle2</code> fails if that name already exists. Your script must still call <code>/clear</code> as required below.</p>
        <h4>Requirements:</h4>
        <ol>
            <li>Call <code>/clear</code> to reset the canvas. <em>(Hint: discover its service type with <code>ros2 service type /clear</code>.)</em></li>
            <li>Spawn the second turtle.</li>
            <li>Set unique pen colors for each turtle.</li>
            <li>Publish to /turtle1/cmd_vel and /turtle2/cmd_vel so each draws one letter.</li>
        </ol>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Hints</strong><br />
            <ul>
                <li>Use <code>teleport_absolute</code> and <code>set_pen 'off': 1</code> to stage turtles before drawing.</li>
                <li>Organize your script: <strong>setup first</strong> (clear, spawn, colors, teleports), then draw.</li>
                <li>For simultaneous drawing, run each turtle&rsquo;s motion sequence in a separate Bash background group, <code>( ... ) &amp;</code>, then use <code>wait</code> after starting both groups. Keep each turtle&rsquo;s commands in order within its group, and finish each sequence with a zero-velocity command.</li>
            </ul>
        </blockquote>
        <p>Save the second script in <code>scripts/</code>. From that directory in Container Terminal 2, run <code>chmod +x turtleletterstwo.sh</code>, then <code>./turtleletterstwo.sh</code>.</p>
        <p><strong>Screenshot:</strong> After running the two-letter script, capture the turtlesim window and save the image as <code>docs/turtlesim_letters.png</code> in your Lab 3 repository.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p><strong>Where the answers go:</strong> this lab has no record file in the repository. Write your answers to the four questions below in your Gradescope PDF (see &sect;7.2); all four are graded there.</p>
    <p>Support each answer with specific observations from running your scripts.</p>
    <h3>Question 1: Drawing your first letter</h3>
    <ul>
        <li>What was your process for figuring out the correct values for <code>linear.x</code>, <code>angular.z</code>, and <code>sleep</code> duration?</li>
        <li>What challenges did you encounter (e.g., overshooting turns, uneven line lengths, trial-and-error)?</li>
    </ul>
    <h3>Question 2: Topics vs. Services</h3>
    <ul>
        <li>In your own words, why was a service the right tool for spawning a new turtle, while a topic was the right tool for controlling its ongoing movement?</li>
        <li><em>Hint: Think about &ldquo;one-time request&rdquo; vs. &ldquo;continuous stream of data.&rdquo;</em></li>
    </ul>
    <h3>Question 3: Remapping with <code>--remap</code></h3>
    <ul>
        <li>In Part 5, you used the <code>--remap</code> argument. What problem did this solve?</li>
        <li>Where did the teleop node send its velocity commands before and after remapping?</li>
    </ul>
    <h3>Question 4: Scaling your drawing</h3>
    <ul>
        <li>If you wanted the turtles to draw their letters twice as large but in the same amount of time, which values would you change and why?</li>
        <li><em>Consider <code>linear.x</code> (forward speed), <code>angular.z</code> (turn rate), and <code>sleep</code> duration.</em></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Setup, Docker, ROS 2, and Git problems that recur across labs are collected on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#turtlesim-and-shell-scripting" target="_blank" rel="noopener">Troubleshooting</a>. For this lab it covers the container name already being in use, a GUI application that cannot open a display, a turtle that will not move, a script that fails with <code>Permission denied</code>, and the YAML quoting trap in <code>set_pen</code>.</p>
    <p>Check that page first when you encounter one of these problems.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html" target="_blank" rel="noopener">ROS 2 Jazzy &mdash; Beginner CLI Tools Tutorials</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/index.html" target="_blank" rel="noopener">ROS 2 Jazzy Documentation</a></li>
        <li><a href="https://wiki.ros.org/turtlesim" target="_blank" rel="noopener">turtlesim Package Documentation</a></li>
        <li><a href="http://linuxcommand.org/lc3_learning_the_shell.php" target="_blank" rel="noopener"><em>Learning the Shell</em></a></li>
        <li><a href="https://docs.docker.com/engine/reference/run/" target="_blank" rel="noopener">Docker <code>run</code> Reference</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
