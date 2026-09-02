---
title: "Lab 02: ROS 2 CLI Fundamentals"
---

# Lab 02: ROS 2 CLI Fundamentals

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1 &mdash; Readiness Gate</a></li>
                <li><a href="#part2">Part 2 &mdash; Container Launch</a></li>
                <li><a href="#part3">Part 3 &mdash; Working in Terminator</a></li>
                <li><a href="#part4">Part 4 &mdash; Guided CLI Baseline</a></li>
                <li><a href="#part5">Part 5 &mdash; Independent System Investigation</a></li>
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
    <p>In this lab you will work with the fundamental concepts of ROS 2, using the Jazzy release. All work is done inside the course Docker container on your VM so that everyone has the same environment.</p>
    <p>You will use turtlesim, a simple ROS 2 simulator, to see these concepts in a running system. You will first establish a guided ROS 2 command-line interface (CLI) baseline, then apply the same inspection methods to a system whose names, values, and expected behavior you define. These skills form the foundation for later labs where you will build and diagnose real robotic systems.</p>
    <h3>1.2 Background</h3>
    <p>ROS 2 (Robot Operating System 2) is a flexible framework for building robotic applications. It is built on a distributed architecture where multiple processes can run independently and communicate with each other.</p>
    <p>The core concepts you will explore are:</p>
    <ul>
        <li><strong>Nodes</strong> &ndash; The smallest unit of a ROS 2 application (like a single program). Example: one node controls a camera, another node controls wheels.</li>
        <li><strong>Topics</strong> &ndash; A one-way, many-to-many communication channel. Nodes publish messages to a topic (like broadcasting on a radio station), and subscribers receive those messages.</li>
        <li><strong>Services</strong> &ndash; A two-way request/response communication method. Example: a node provides an &ldquo;inverse kinematics&rdquo; service, and another node requests a calculation.</li>
        <li><strong>Parameters</strong> &ndash; Configurable values for a node (like max speed or sensor sensitivity), which can be changed without modifying code.</li>
    </ul>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab02/d02-four-concepts.svg" alt="Nodes, topics, services, and parameters, each with the ros2 commands that inspect it" style="max-width: 100%; height: auto;" /></p>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Why CLI tools?</strong><br />The ROS 2 CLI tools let you &ldquo;peek under the hood&rdquo; of a running system. You can see what nodes, topics, services, and parameters exist, how they interact, and even send commands without writing code.</blockquote>
    <h3>1.3 Equipment and Software</h3>
    <ul>
        <li><strong>Hardware:</strong> Your Duke VCM Ubuntu 24.04 VM.</li>
        <li><strong>Software:</strong> Docker (installed on your VM via the Lab 1 setup script); the course ROS 2 Jazzy Docker image (<code>base-jazzy-latest</code>); ROS 2 Jazzy, Terminator, and Python 3 (all inside Docker).</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you will be able to:</p>
    <ul>
        <li><strong>Launch and verify</strong> the ROS 2 Jazzy Docker environment on your VM.</li>
        <li><strong>Inspect</strong> an unfamiliar ROS 2 system to identify nodes, topics, message types, services, and parameters.</li>
        <li><strong>Select and use</strong> a topic, service, or parameter according to the interaction required.</li>
        <li><strong>Predict and validate</strong> system behavior using CLI output and a ROS graph from your own run.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Accept and clone the assignment, pull the course image, and verify the starting state before arriving at lab.</p>
    </div>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Important:</strong> VMs power off automatically 4 hours after the reservation starts, destroying the running container and everything not saved in <code>~/workspaces</code>. This lab can fill a session, so commit and push whenever you finish a part, and renew your reservation before starting the independent investigation if your session is running low.</div>
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
        <li><strong>Accept Lab 2.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-02</code></pre>
            <p>Classroom 50 accepts a pending organization invitation, creates your private repository, and prints the exact <code>git clone</code> command. If you already accepted the assignment, it leaves your repository unchanged.</p>
        </li>
        <li><strong>Clone the repository.</strong> Run the clone command printed by Classroom 50. The expected repository name is:</li>
    </ol>
    <pre><code>MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-02-YOUR_GITHUB_USERNAME</code></pre>
    <p><strong>Location:</strong> Host VM Terminal</p>
    <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-02-YOUR_GITHUB_USERNAME.git
cd intro-to-robotics-fall-2026-lab-02-YOUR_GITHUB_USERNAME</code></pre>
    <p>Use the URL printed by Classroom 50 if it differs from the example.</p>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code> succeeds.</li>
        <li>[ ] <code>git status</code> reports a clean working tree on <code>main</code>.</li>
        <li>[ ] <code>git remote -v</code> points to your Lab 2 repository.</li>
        <li>[ ] <code>ls -la</code> shows <code>README.md</code>, <code>docs/</code>, <code>ros2_cli_record.md</code>, and <code>test_lab_2.py</code>.</li>
        <li>[ ] You skimmed the <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html" target="_blank" rel="noopener">ROS 2 Jazzy Beginner CLI Tools tutorial index</a>.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1 &mdash; Readiness Gate</h3>
        <p><strong>Goal:</strong> Confirm that the assignment repository and container image are ready before starting ROS 2 processes.</p>
        <p><strong>Location:</strong> Host VM Terminal, from the Lab 2 repository.</p>
        <pre><code class="language-bash">git status
git remote -v
ls -la
docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest &gt; /dev/null</code></pre>
        <p><strong>Checkpoint:</strong> The working tree is clean on <code>main</code>, the remote is your private Lab 2 repository, all starter files are present, and the image-inspection command exits without an error. Stop here and finish the pre-lab if any check fails.</p>
    </section>
    <section id="part2">
        <h3>Part 2 &mdash; Container Launch</h3>
        <p><strong>Goal:</strong> Start the course container with GUI support and your workspace mounted, and verify the ROS 2 environment.</p>
        <ol>
            <li><strong>Allow GUI Connections:</strong><br />On your VM, before starting the container, run the following command. This grants Docker permission to draw graphical windows (like the turtle simulator) on your VM&rsquo;s desktop:
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">xhost +local:docker</code></pre>
            </li>
            <li><strong>Run the Course Container:</strong><br />This is the standard course <code>docker run</code> command from Lab 1 with the container name changed to <code>lab02</code>. It mounts your whole <code>workspaces</code> folder so that all of your repositories are available inside the container.
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">docker run --rm -it \
  --name lab02 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
                <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;">Inside the container, your VM&rsquo;s <code>~/workspaces</code> directory appears at <code>/root/workspaces</code>. The container runs as the <code>root</code> user, so <code>~/workspaces</code> <em>inside the container</em> is that same place, and the file paths stay the same across labs.</blockquote>
                <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Discovery range:</strong> The <code>-e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST</code> flag keeps your ROS 2 traffic on your own VM. On the shared campus network you could otherwise see, and control, other students&rsquo; turtles. The <code>docker run</code> command sets it every time, so you do not need to edit any <code>.bashrc</code>.</blockquote>
                <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Warning:</strong> Because of <code>--rm</code>, the container is destroyed the moment you exit the original shell, along with any terminals attached via <code>docker exec</code>. Keep your files in <code>~/workspaces</code>, which lives on the VM and is not affected.</blockquote>
            </li>
            <li><strong>Verify Environment:</strong><br />Inside the container, confirm you are running the correct ROS 2 distribution:
                <p><strong>Location:</strong> Container Terminal</p>
                <pre><code class="language-bash">echo $ROS_DISTRO</code></pre>
                <p><strong>Checkpoint:</strong> You should see:</p>
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>jazzy</code></pre>
                </div>
                <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Sourcing note:</strong> The course image&rsquo;s <code>~/.bashrc</code> already sources ROS 2 Jazzy, so <code>ros2</code> commands work in every container shell without any extra setup. No workspace sourcing is needed in this lab.</blockquote>
            </li>
            <li><strong>Launch Terminator:</strong><br />Inside the container, launch a multi-pane terminal:
                <p><strong>Location:</strong> Container Terminal</p>
                <pre><code class="language-bash">terminator</code></pre>
                <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;">You will need multiple panes open simultaneously for these tutorials. A good setup is one pane split into two.</blockquote>
            </li>
        </ol>
        <p>All subsequent ROS 2 commands for this lab should be run inside the panes of this Terminator window.</p>
    </section>
    <section id="part3">
        <h3>Part 3 &mdash; Working in Terminator</h3>
        <p>When you run <code>terminator</code> inside the container, your current shell stops taking input because it is now busy running the Terminator program itself. A new Terminator window opens, and that is the window you use for the rest of the lab.</p>
        <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Key point:</strong> All commands for this lab should be run inside panes of the new Terminator window, not the original shell where you typed <code>terminator</code>.</blockquote>
        <h4>Why we use Terminator</h4>
        <ul>
            <li><strong>Multiple panes/tabs inside one window:</strong> ROS 2 development often needs multiple terminals at the same time (for example, one running <code>ros2 run turtlesim turtlesim_node</code> and another running <code>ros2 node list</code>). Terminator makes this easy by letting you split your window or open tabs instead of juggling lots of separate terminal windows.</li>
            <li><strong>Consistent environment:</strong> Every pane/tab you open inside that Terminator window is automatically inside the Docker container, so you don&rsquo;t have to re-attach or run <code>docker exec</code> for each new terminal.</li>
        </ul>
        <h4>How to Use Terminator Effectively</h4>
        <ol>
            <li><strong>Open Terminator:</strong> From inside the container:
                <pre><code class="language-bash">terminator</code></pre>
                <p>Don&rsquo;t type anything else in the original shell. It is now just running Terminator.</p>
            </li>
            <li><strong>Split panes:</strong>
                <ul>
                    <li>Right-click &rarr; <em>Split Horizontally</em> or <em>Split Vertically</em></li>
                    <li>Or use shortcuts:
                        <ul>
                            <li><code>Ctrl+Shift+O</code> &rarr; split horizontally</li>
                            <li><code>Ctrl+Shift+E</code> &rarr; split vertically</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><strong>Create tabs:</strong> Press <code>Ctrl+Shift+T</code> for a new tab. Each tab is also inside the container.</li>
            <li><strong>Switch focus:</strong>
                <ul>
                    <li>Use the mouse to click into a pane/tab</li>
                    <li>Or use <code>Ctrl+Tab</code> (for tabs) and <code>Ctrl+Shift+Arrow keys</code> (for panes)</li>
                </ul>
            </li>
        </ol>
        <h4>If You Want to Use Another Terminal</h4>
        <p>If you close Terminator or open a new terminal window in your VM, that new terminal is not inside the container. If you want it linked, you need to re-attach manually. Since we started the container with <code>--name lab02</code>, run:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">docker exec -it lab02 bash</code></pre>
        <p>This drops you back into the running container from any new terminal. If you ever forget the container&rsquo;s name, run <code>docker ps</code> on the VM to list the running containers and their names.</p>
    </section>
    <section id="part4">
        <h3>Part 4 &mdash; Guided CLI Baseline</h3>
        <p><strong>Goal:</strong> Establish a known-good turtlesim system and connect ROS 2 names and interfaces to evidence from the CLI and <code>rqt_graph</code>.</p>
        <h4>Step 4.1: Choose a route</h4>
        <p>Both routes produce the same baseline evidence and receive the same credit.</p>
        <p><strong>Fast route:</strong> If you already know the ROS 2 CLI, create a running system with <code>turtlesim_node</code> and <code>turtle_teleop_key</code>. Use CLI commands to identify both node names, the velocity topic, its message type, and the publisher/subscriber relationship. Then complete Step 4.2.</p>
        <p><strong>Guided route:</strong> Work through these official ROS 2 Jazzy tutorials, running each example as you go:</p>
        <ol>
            <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html" target="_blank" rel="noopener">Introducing Turtlesim</a></li>
            <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html" target="_blank" rel="noopener">Understanding ROS 2 Nodes</a></li>
            <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html" target="_blank" rel="noopener">Understanding ROS 2 Topics</a></li>
            <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.html" target="_blank" rel="noopener">Understanding ROS 2 Services</a></li>
            <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.html" target="_blank" rel="noopener">Understanding ROS 2 Parameters</a></li>
        </ol>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Using AI tools:</strong> AI assistance is optional and is not needed for these foundational commands. Try the CLI help, inspection commands, and official documentation first. If you use AI, inspect every command before running it and verify its claims against your actual ROS graph and terminal output.</blockquote>
        <h4>Step 4.2: Record the known-good baseline</h4>
        <p>In <code>ros2_cli_record.md</code>, complete the Known-Good Baseline section using output from your running system. Do not copy the tutorial&rsquo;s summary; record the names, type, and publisher/subscriber counts you observed.</p>
        <p>The baseline system has two nodes connected by one topic:</p>
        <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab02/d01-turtlesim-node-graph.svg" alt="teleop_turtle publishes geometry_msgs/Twist on /turtle1/cmd_vel; turtlesim subscribes" style="max-width: 100%; height: auto;" /></p>
        <p>Open <code>rqt_graph</code>, select <em>Nodes/Topics (all)</em>, and refresh the graph. Capture the graph with the simulator and teleop connected through the velocity topic. Save it as <code>docs/baseline_graph.png</code>.</p>
        <p><strong>Checkpoint:</strong> Your record and graph agree on the two nodes, the command topic, and the direction of message flow.</p>
    </section>
    <section id="part5">
        <h3>Part 5 &mdash; Independent System Investigation</h3>
        <p><strong>Goal:</strong> Apply the CLI in a changed context without following a command-by-command solution.</p>
        <h4>Step 5.1: Return to a clean ROS graph</h4>
        <p>Stop the tutorial nodes with <code>Ctrl+C</code> in their panes, close <code>rqt_graph</code>, and run:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">ros2 node list</code></pre>
        <p><strong>Checkpoint:</strong> No tutorial nodes remain. If a node remains, find its pane and stop that process before continuing.</p>
        <h4>Step 5.2: Define your system before launching it</h4>
        <p>Complete the choices and prediction in the Independent System Contract section of <code>ros2_cli_record.md</code> before running the new system. Use ROS-compatible names made from lowercase letters, digits, and underscores, beginning with a letter.</p>
        <ul>
            <li>Choose a simulator node name other than <code>turtlesim</code> or <code>my_turtle</code>.</li>
            <li>Choose a second turtle name and a spawn pose that does not overlap <code>turtle1</code>.</li>
            <li>Choose non-default red, green, and blue background values.</li>
            <li>Choose one velocity command with nonzero linear <em>and</em> angular components, then predict the resulting path.</li>
        </ul>
        <h4>Step 5.3: Build and inspect the system</h4>
        <p>Using the techniques from Part 4, complete all of the following:</p>
        <ol>
            <li>Launch <code>turtlesim_node</code> under your chosen node name.</li>
            <li>Use inspection commands to discover the active node, command topic and message type, spawn service and service type, and background parameters. Record the commands and relevant output.</li>
            <li>Spawn the second turtle with your chosen name and pose.</li>
            <li>Set the background to your chosen RGB values.</li>
            <li>Publish your chosen velocity command once and compare the observed path with your prediction.</li>
            <li>Open and refresh <code>rqt_graph</code>. Save the graph as <code>docs/independent_graph.png</code>.</li>
            <li>Capture the turtlesim window showing both turtles and the changed background. Save it as <code>docs/independent_result.png</code>.</li>
        </ol>
        <details>
            <summary>Hint 1: Identify the relevant CLI families</summary>
            <p>You will need commands from <code>ros2 node</code>, <code>ros2 topic</code>, <code>ros2 service</code>, and <code>ros2 param</code>. Use <code>--help</code> to inspect a command family.</p>
        </details>
        <details>
            <summary>Hint 2: Find interface types before constructing data</summary>
            <p>List interfaces with their types, then inspect the selected topic or service. Do not guess the message or service type.</p>
        </details>
        <details>
            <summary>Hint 3: Return to the matching worked example</summary>
            <p>Use the relevant official tutorial from Part 4 as a pattern, replacing its names and values with those in your independent contract.</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> First compare <code>ros2 node list</code> and <code>ros2 topic list -t</code> with the state you expected. Then inspect the specific node or interface. If the graph still contains stale processes, stop all turtlesim and teleop panes and restart Step 5.1. After one clean retry or 10 minutes without progress, ask a TA and show the command and output that disagree.</blockquote>
        <h4>Step 5.4: Finish the record and run the checks</h4>
        <p>Complete the Inspection Evidence, Validation, and Recovery sections of <code>ros2_cli_record.md</code>. Tie each explanation to your chosen names, values, output, and screenshots.</p>
        <p><strong>Location:</strong> Host VM Terminal, from the Lab 2 repository.</p>
        <p><code>pytest</code> is the Python test runner that <code>test_lab_2.py</code> is written for, and the setup script from Lab 1 already installed it on your VM.</p>
        <pre><code class="language-bash">pytest -v
git add README.md ros2_cli_record.md docs/
git commit -m "Complete ROS 2 CLI investigation"
git push origin main</code></pre>
        <p><strong>Final checkpoint:</strong> All tests pass locally, Classroom 50 reports a passing automated result, and GitHub contains the record plus all three PNG files.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p>Your analysis is the completed <code>ros2_cli_record.md</code>. A strong record lets another person reconstruct what you observed and why your commands fit the task. It must:</p>
    <ul>
        <li>compare your velocity prediction with the observed motion;</li>
        <li>interpret the direction of communication shown in your graph;</li>
        <li>explain why motion used a topic, spawning used a service, and background configuration used parameters; and</li>
        <li>describe one actual mismatch and diagnosis, or one likely mismatch and the first CLI command you would use to inspect it.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Setup, Docker, ROS 2, and Git problems that recur across labs are collected on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/" target="_blank" rel="noopener">Troubleshooting</a>. For this lab it covers the container name already being in use, a GUI application that cannot open a display, a stale <code>rqt_graph</code>, seeing turtles you never created, <code>ros2</code> reporting <code>command not found</code> in a terminal that is on the VM rather than in the container, and files created in the container that cannot be edited on the VM.</p>
    <p>That page is maintained across semesters, so check it before asking a TA.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html" target="_blank" rel="noopener">ROS 2 Jazzy &mdash; Beginner CLI Tools Tutorials</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/index.html" target="_blank" rel="noopener">ROS 2 Jazzy Documentation</a></li>
        <li><a href="https://wiki.ros.org/turtlesim" target="_blank" rel="noopener">turtlesim Package Documentation</a></li>
        <li><a href="https://docs.docker.com/engine/reference/run/" target="_blank" rel="noopener">Docker <code>run</code> Reference</a></li>
        <li><a href="https://gnome-terminator.org/" target="_blank" rel="noopener">Terminator Terminal Documentation</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
