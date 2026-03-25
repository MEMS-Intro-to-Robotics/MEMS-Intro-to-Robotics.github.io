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
                <li><a href="#part1">Part 1 &mdash; Setup and Docker Environment</a></li>
                <li><a href="#part1-5">Part 1.5 &mdash; Open the Repo in VS Code</a></li>
                <li><a href="#part2">Part 2 &mdash; Launch and Manual Control</a></li>
                <li><a href="#part3">Part 3 &mdash; Scripting Motion with Topics</a></li>
                <li><a href="#part4">Part 4 &mdash; Draw the First Letter of Your Name</a></li>
                <li><a href="#part5">Part 5 &mdash; Using Services for State Changes</a></li>
                <li><a href="#part6">Part 6 &mdash; Two-Turtle, Two-Letter Script</a></li>
            </ol>
        </li>
        <li><a href="#analysis">Analysis and Discussion</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>In this lab, you will write your first robot programs by controlling a virtual turtle in the <strong>turtlesim</strong> simulation. You will move beyond simple command-line interactions and learn how to write <strong>shell scripts</strong> to automate robot behavior.</p>
    <p>A shell script is simply a text file containing a sequence of Linux commands that can be executed together. Instead of typing <code>ros2 topic pub</code> or <code>ros2 service call</code> commands one by one, you will save them in a <code>.sh</code> file and run the whole sequence at once. This allows you to create repeatable robot behaviors and is an essential skill for testing and debugging.</p>
    <h3>1.2 Background</h3>
    <p>This lab builds directly on the concepts from Lab 2. Now you will be the one sending commands through scripts. The two primary communication methods you will use are:</p>
    <ul>
        <li><strong>Topics (Continuous Streams):</strong> Used for data that flows continuously, like sensor readings or velocity commands. You publish a constant stream of movement commands to a topic to make a robot drive.
            <pre><code class="language-bash">ros2 topic pub &lt;topic_name&gt; &lt;msg_type&gt; &lt;msg_data&gt;</code></pre>
        </li>
        <li><strong>Services (Request/Response):</strong> Used for discrete actions or questions that require an answer. You call a service to perform a one-time action, like spawning a new turtle or teleporting it, and you get a confirmation back.
            <pre><code class="language-bash">ros2 service call &lt;service_name&gt; &lt;srv_type&gt; &lt;arguments&gt;</code></pre>
        </li>
    </ul>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Concept: Topics vs. Services</strong><br /><strong>Topics</strong> are like radio broadcasts&mdash;continuous streams you can &ldquo;tune in&rdquo; to.<br /><strong>Services</strong> are like phone calls&mdash;you ask once, get an answer, then hang up.</blockquote>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>Upon successful completion of this lab, you will demonstrate the ability to:</p>
    <ul>
        <li><strong>Distinguish</strong> between the use cases for ROS 2 topics and services in a practical application.</li>
        <li><strong>Control</strong> a simulated robot programmatically by publishing messages to a topic from a shell script.</li>
        <li><strong>Modify</strong> the state of a simulation by calling services from the command line and from within a script.</li>
        <li><strong>Automate</strong> a sequence of ROS 2 commands to achieve a multi-step goal.</li>
        <li><strong>Organize</strong> your work in a GitHub Classroom repository, commit your scripts with Git, and push them.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Verify each item before arriving at lab.</p>
    </div>
    <ul>
        <li>[ ] <strong>Pull latest Docker image:</strong>
            <pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        </li>
        <li>[ ] <strong>Start your container:</strong> Use <code>docker ps</code> to check if it is running. If not, use the command in section 5.1.3 to start it.</li>
        <li>[ ] <strong>Verify turtlesim works:</strong>
            <pre><code class="language-bash">ros2 run turtlesim turtlesim_node</code></pre>
        </li>
        <li>[ ] <strong>Verify ROS 2 topics:</strong> Open a new terminal and run:
            <pre><code class="language-bash">ros2 topic list</code></pre>
            <p>You should see <code>/turtle1/cmd_vel</code> in the list.</p>
        </li>
        <li>[ ] <strong>Review Lab 2 concepts:</strong> Topics and services from the official Jazzy CLI tools tutorials.</li>
        <li>[ ] <strong>Verify GitHub SSH access:</strong>
            <pre><code class="language-bash">ssh -T git@github.com</code></pre>
            <p>You should see a message like <em>&ldquo;Hi USERNAME! You&rsquo;ve successfully authenticated...&rdquo;</em></p>
        </li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1 &mdash; Setup and Docker Environment</h3>
        <p>We will run everything <strong>inside the container</strong> for a consistent ROS 2 environment. We&rsquo;ll also <strong>name</strong> the container so we can easily open multiple terminals into it.</p>
        <h4>Step 1.1: Accept the GitHub Classroom Assignment and Clone Your Repository</h4>
        <ol>
            <li><strong>Accept the assignment:</strong> Click the following link to create your Lab 3 repository:
                <p style="margin: 1em 0;"><a class="inline_disabled" href="https://classroom.github.com/a/iXkMRhjB" target="_blank" rel="noopener">https://classroom.github.com/a/iXkMRhjB</a></p>
                <ul>
                    <li>Sign in to GitHub if prompted.</li>
                    <li>Select your name from the roster (if shown) to link your GitHub account to your identity in the course.</li>
                    <li>Accept the assignment. GitHub Classroom will create a private repository for you under the course organization.</li>
                </ul>
            </li>
            <li><strong>Accept the repository invitation:</strong> GitHub Classroom creates your repo, but you must also accept a collaboration invite before you can access it.
                <ul>
                    <li>Check your email for an invite from <strong>MEMS-Intro-to-Robotics</strong>, or</li>
                    <li>Go directly to your repo URL (see next step) and click <strong>Accept invitation</strong> on the banner at the top.</li>
                </ul>
            </li>
            <li><strong>Note your repository URL:</strong> After accepting, you&rsquo;ll see a URL like:
                <pre><code>https://github.com/MEMS-Intro-to-Robotics/lab-3-scripting-with-ros-2-topics-and-services-YOUR_GITHUB_USERNAME</code></pre>
            </li>
            <li><strong>Clone the repository into your workspace:</strong>
                <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/lab-3-scripting-with-ros-2-topics-and-services-YOUR_GITHUB_USERNAME.git
cd lab-3-scripting-with-ros-2-topics-and-services-YOUR_GITHUB_USERNAME</code></pre>
                <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your actual GitHub username.</p>
            </li>
        </ol>
        <h4>Step 1.2: Prepare repository layout</h4>
        <p>From inside your cloned repo folder:</p>
        <pre><code class="language-bash">mkdir -p docs scripts</code></pre>
        <p><em><code>-p</code> lets you run this even if folders already exist.</em></p>
        <h4>Step 1.3: Start the named container</h4>
        <p>Navigate to your repo root on the VM, then bind-mount it into the container:</p>
        <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab03 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/workspaces:/root/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest bash</code></pre>
        <ul>
            <li><code>--name lab03</code> gives the container a memorable name.</li>
            <li><code>-v ~/workspaces:/root/workspaces</code> mounts your repo so the container sees your files.</li>
            <li><code>xhost</code> + <code>DISPLAY</code> allows the turtlesim GUI to show on your desktop.</li>
        </ul>
        <h4>Step 1.4: Open a second terminal</h4>
        <p>Get another shell <strong>into the same container</strong>:</p>
        <pre><code class="language-bash">docker exec -it lab03 bash</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Tip: Using Terminator</strong><br />Alternatively, open a terminator terminal instance in your Docker container:
            <pre><code class="language-bash">terminator</code></pre>
        </blockquote>
    </section>
    <section id="part1-5">
        <h3>Part 1.5 &mdash; Open the Repo in VS Code</h3>
        <p>On the VM, run:</p>
        <pre><code class="language-bash">code ~/workspaces/lab-3-scripting-with-ros-2-topics-and-services-YOUR_GITHUB_USERNAME</code></pre>
        <ul>
            <li>Edit files normally in VS Code. Because the repo is bind-mounted into the container at <code>~/workspaces</code>, your changes appear instantly inside the container.</li>
            <li>Use the <strong>VM terminals</strong> you opened in Part 1 to run commands.</li>
        </ul>
    </section>
    <section id="part2">
        <h3>Part 2 &mdash; Launch and Manual Control</h3>
        <h4>Step 2.1: Start turtlesim (Terminal 1, inside container)</h4>
        <pre><code class="language-bash">ros2 run turtlesim turtlesim_node</code></pre>
        <p>A blue GUI window should appear.</p>
        <h4>Step 2.2: Start keyboard teleop (Terminal 2, inside container)</h4>
        <pre><code class="language-bash">ros2 run turtlesim turtle_teleop_key</code></pre>
        <p>Click Terminal 2 to focus it; use arrow keys to drive. This publishes to <strong>/turtle1/cmd_vel</strong>, which the simulator subscribes to.</p>
    </section>
    <section id="part3">
        <h3>Part 3 &mdash; Scripting Motion with Topics</h3>
        <p>We&rsquo;ll publish velocity commands from a script instead of pressing keys.</p>
        <h4>Step 3.1: Create the script file in VS Code</h4>
        <p>In the Explorer, go to: <code>scripts</code> &rarr; <strong>New File</strong> &rarr; <code>turtleletter.sh</code></p>
        <p>Paste:</p>
        <pre><code class="language-bash">#!/usr/bin/env bash
set -euo pipefail

# Move forward for 1 second
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once
sleep 1

# Turn for 1 second
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}" --once
sleep 1

# Stop the turtle (good practice)
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once</code></pre>
        <h4>Step 3.2: Make it executable &amp; run it (inside container)</h4>
        <p>From a container terminal:</p>
        <pre><code class="language-bash">cd ~/workspaces/lab-3-scripting-with-ros-2-topics-and-services-YOUR_GITHUB_USERNAME/scripts
chmod +x turtleletter.sh
./turtleletter.sh</code></pre>
    </section>
    <section id="part4">
        <h3>Part 4 &mdash; Draw the First Letter of Your Name</h3>
        <p>Extend <code>turtleletter.sh</code> to trace the <strong>first letter of your name</strong> by chaining <code>ros2 topic pub</code> + <code>sleep</code>.</p>
        <ul>
            <li>Break the letter into <strong>straight segments</strong> + <strong>turns</strong>.</li>
            <li>Tune <code>linear.x</code> (speed), <code>angular.z</code> (turn rate), and <code>sleep</code> (duration).</li>
            <li>Expect trial &amp; error&mdash;that&rsquo;s the point.</li>
        </ul>
    </section>
    <section id="part5">
        <h3>Part 5 &mdash; Using Services for State Changes</h3>
        <p>Use services for <strong>one-time actions</strong>:</p>
        <h4>1. Spawn a second turtle</h4>
        <pre><code class="language-bash">ros2 service call /spawn turtlesim/srv/Spawn "{x: 1.0, y: 1.0, name: 'turtle2'}"</code></pre>
        <h4>2. Change pen color of the first turtle</h4>
        <pre><code class="language-bash">ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 5}"</code></pre>
        <p><code>r,g,b</code> are 0&ndash;255; add <code>'off': 1</code> to lift the pen.</p>
        <h4>3. Teleport (instant move)</h4>
        <pre><code class="language-bash">ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute "{x: 5.5, y: 5.5, theta: 0.0}"</code></pre>
        <h4>4. Control turtle2 with keyboard (remap topic)</h4>
        <pre><code class="language-bash">ros2 run turtlesim turtle_teleop_key --ros-args --remap /turtle1/cmd_vel:=/turtle2/cmd_vel</code></pre>
    </section>
    <section id="part6">
        <h3>Part 6 &mdash; Two-Turtle, Two-Letter Script</h3>
        <p>Create <code>turtleletterstwo.sh</code> that draws the first <strong>two</strong> letters of your name <strong>simultaneously</strong>.</p>
        <h4>Requirements:</h4>
        <ol>
            <li>Call <code>/clear</code> to reset the canvas.</li>
            <li>Spawn the second turtle.</li>
            <li>Set unique pen colors for each turtle.</li>
            <li>Publish to <strong>/turtle1/cmd_vel</strong> and <strong>/turtle2/cmd_vel</strong> so each draws one letter.</li>
        </ol>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Hints</strong><br />
            <ul>
                <li>Use <code>teleport_absolute</code> and <code>set_pen off: 1</code> to stage turtles before drawing.</li>
                <li>Organize your script: <strong>setup first</strong> (clear, spawn, colors, teleports), then draw.</li>
            </ul>
        </blockquote>
        <p>📸 <strong>Screenshot Requirement:</strong> Capture the turtlesim window after running your two-letter script. Save as <code>turtlesim_letters.png</code>.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p>Answer the following questions in your Gradescope submission. Be clear and specific&mdash;we&rsquo;re interested in your reasoning process, not just the final answer.</p>
    <h3>Question 1: Drawing your first letter</h3>
    <ul>
        <li>What was your process for figuring out the correct values for <code>linear.x</code>, <code>angular.z</code>, and <code>sleep</code> duration?</li>
        <li>What challenges did you encounter (e.g., overshooting turns, uneven line lengths, trial-and-error)?</li>
    </ul>
    <h3>Question 2: Topics vs. Services</h3>
    <ul>
        <li>In your own words, why was a <strong>service</strong> the right tool for spawning a new turtle, while a <strong>topic</strong> was the right tool for controlling its ongoing movement?</li>
        <li><em>Hint: Think about &ldquo;one-time request&rdquo; vs. &ldquo;continuous stream of data.&rdquo;</em></li>
    </ul>
    <h3>Question 3: Remapping with <code>--remap</code></h3>
    <ul>
        <li>In Part 5, you used the <code>--remap</code> argument. What problem did this solve?</li>
        <li>How does this example demonstrate the flexibility of ROS 2&rsquo;s communication system?</li>
    </ul>
    <h3>Question 4: Scaling your drawing</h3>
    <ul>
        <li>Look at your final script, <code>turtleletterstwo.sh</code>.</li>
        <li>If you wanted the turtles to draw their letters <strong>twice as large but in the same amount of time</strong>, which values would you change and why?</li>
        <li><em>Consider <code>linear.x</code> (forward speed), <code>angular.z</code> (turn rate), and <code>sleep</code> duration.</em></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
