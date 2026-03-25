---
title: "Lab 02: ROS 2 CLI Fundamentals"
---

# Lab 02: ROS 2 CLI Fundamentals

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#equipment">Equipment and Software</a></li>
        <li><a href="#prelab">Prelab &mdash; Do Before Lab</a></li>
        <li><a href="#procedure">Lab Procedure</a></li>
        <li><a href="#discussion">Discussion Questions</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>In this lab, you will gain hands-on experience with the <strong>fundamental concepts of ROS 2</strong> using the <strong>Jazzy release</strong>. All work will be done <strong>inside the course Docker container</strong> on your VM to ensure a consistent environment.</p>
    <p>You will use <strong>turtlesim</strong>, a classic ROS 2 simulator, to visualize these concepts in action. Through a series of beginner-level <strong>ROS 2 command-line interface (CLI) tutorials</strong>, you will learn to inspect, interact with, and control a running ROS 2 system. These skills form the foundation for later labs where you will build and interact with real robotic systems.</p>
    <h3>1.2 Objectives</h3>
    <p>By the end of this lab, you will be able to:</p>
    <ul>
        <li>Launch and interact with the <strong>ROS 2 Jazzy Docker environment</strong> on your VM.</li>
        <li>Use the <strong>ROS 2 CLI</strong> to inspect and interact with a running system.</li>
        <li>Apply core ROS 2 concepts (nodes, topics, services, parameters) using <strong>turtlesim</strong>.</li>
        <li>Capture screenshots to document your progress and confirm milestone completion.</li>
    </ul>
    </li>
        <li><strong>Gradescope PDF (single file)</strong> including:
            <ul>
                <li>First page: your GitHub repo URL.</li>
                <li>The same 5 labeled screenshots.</li>
                <li>Written answers to the Discussion Questions.</li>
            </ul>
        </li>
    </ul>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> Refer to <strong>Section 6 &ndash; Deliverables</strong> for the required repository layout and full submission details.</blockquote>
    <h3>1.3 Background</h3>
    <p>ROS 2 (Robot Operating System 2) is a flexible framework for building robotic applications. It is built on a <strong>distributed architecture</strong> where multiple processes can run independently and communicate with each other.</p>
    <p>The core concepts you will explore are:</p>
    <ul>
        <li><strong>Nodes</strong> &ndash; The smallest unit of a ROS 2 application (like a single program). Example: one node controls a camera, another node controls wheels.</li>
        <li><strong>Topics</strong> &ndash; A one-way, many-to-many communication channel. Nodes publish messages to a topic (like broadcasting on a radio station), and subscribers receive those messages.</li>
        <li><strong>Services</strong> &ndash; A two-way request/response communication method. Example: a node provides an &ldquo;inverse kinematics&rdquo; service, and another node requests a calculation.</li>
        <li><strong>Parameters</strong> &ndash; Configurable values for a node (like max speed or sensor sensitivity), which can be changed without modifying code.</li>
    </ul>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Why CLI tools?</strong><br />The ROS 2 CLI tools let you &ldquo;peek under the hood&rdquo; of a running system. You can see what nodes, topics, services, and parameters exist, how they interact, and even send commands without writing code.</blockquote>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="equipment">
    <h2>2. Equipment and Software</h2>
    <h3>2.1 Hardware</h3>
    <ul>
        <li>Your Duke VCM <strong>Ubuntu 24.04 VM</strong>.</li>
    </ul>
    <h3>2.2 Software</h3>
    <ul>
        <li><strong>Docker</strong> (installed on your VM via the Lab 1 setup script).</li>
        <li><strong>Course ROS 2 Jazzy Docker image</strong> (<code>base-jazzy-latest</code>).</li>
        <li><strong>ROS 2 Jazzy</strong> (inside Docker).</li>
        <li><strong>Terminator</strong> (inside Docker).</li>
        <li><strong>Python 3</strong> (inside Docker).</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>3. Prelab &mdash; Do Before Lab</h2>
    <p>Before coming to lab, complete the following on your VM:</p>
    <ol>
        <li>Verify Docker is installed and running:
            <pre><code class="language-bash">docker --version</code></pre>
        </li>
        <li>Pull the latest course ROS 2 Jazzy image:
            <pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        </li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html" target="_blank" rel="noopener">Skim the ROS 2 Jazzy Beginner CLI Tools tutorial index</a></li>
    </ol>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>4. Lab Procedure</h2>
    <h3>4.1 Accept the GitHub Classroom Assignment</h3>
    <ol>
        <li><strong>Accept the assignment:</strong> Click the following link to create your Lab 2 repository:
            <p style="margin: 1em 0;"><a style="font-size: 1.1em;" href="https://classroom.github.com/a/RuisKcvX" target="_blank" rel="noopener">https://classroom.github.com/a/RuisKcvX</a></p>
            <ul>
                <li>Sign in to GitHub if prompted.</li>
                <li>Accept the assignment. GitHub Classroom will create a private repository for you.</li>
            </ul>
        </li>
        <li><strong>Accept the repository invitation:</strong> GitHub Classroom creates your repo, but you must also accept a collaboration invite before you can access it.
            <ul>
                <li>Check your email for an invite from <strong>MEMS-Intro-to-Robotics</strong>, or</li>
                <li>Go directly to your repo URL and click <strong>Accept invitation</strong> on the banner at the top.</li>
            </ul>
        </li>
        <li><strong>Clone the repository:</strong>
            <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/lab-02-ros2-cli-YOUR_GITHUB_USERNAME.git
cd lab-02-ros2-cli-YOUR_GITHUB_USERNAME</code></pre>
            <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your actual GitHub username.</p>
        </li>
        <li><strong>Create the docs directory:</strong>
            <pre><code class="language-bash">mkdir -p docs</code></pre>
        </li>
    </ol>
    <h3>4.2 Container Launch</h3>
    <ol>
        <li><strong>Allow GUI Connections:</strong><br />On your VM, before starting the container, run the following command. This grants Docker permission to draw graphical windows (like the turtle simulator) on your VM&rsquo;s desktop:
            <pre><code class="language-bash">xhost +local:docker</code></pre>
        </li>
        <li><strong>Run the Course Container:</strong><br />On your VM, run the container using the command below. We mount your <strong>entire <code>workspaces</code> folder</strong> so that all your repos are accessible in one place.
            <pre><code class="language-bash">cd ~/workspaces
docker run --rm -it \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/workspaces:~/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest bash</code></pre>
            <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;">Inside the container, your VM&rsquo;s <code>~/workspaces</code> directory will appear as <code>/workspaces</code>. This keeps the file paths consistent across labs.</blockquote>
        </li>
        <li><strong>Verify Environment:</strong><br />Inside the container, confirm you are running the correct ROS 2 distribution:
            <pre><code class="language-bash">echo $ROS_DISTRO</code></pre>
            <p>You should see:</p>
            <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>jazzy</code></pre>
            </div>
        </li>
        <li><strong>Launch Terminator:</strong><br />Inside the container, launch a multi-pane terminal:
            <pre><code class="language-bash">terminator</code></pre>
            <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;">You will need multiple panes open simultaneously for these tutorials. A good setup is one pane split into two.</blockquote>
        </li>
    </ol>
    <p>All subsequent ROS 2 commands for this lab should be run inside the panes of this Terminator window.</p>
    <h3>4.3 Using Terminator in the Container</h3>
    <p>When you run <code>terminator</code> inside the container, your <strong>current shell stops taking input</strong> because it is now busy running the Terminator program itself. A <strong>new Terminator window</strong> opens up &mdash; this is the window you actually use for the rest of the lab.</p>
    <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Key point:</strong> All commands for this lab should be run inside panes of the <strong>new Terminator window</strong>, not the original shell where you typed <code>terminator</code>.</blockquote>
    <h4>Why we use Terminator</h4>
    <ul>
        <li><strong>Multiple panes/tabs inside one window:</strong> ROS 2 development often needs multiple terminals at the same time (for example, one running <code>ros2 run turtlesim turtlesim_node</code> and another running <code>ros2 node list</code>). Terminator makes this easy by letting you split your window or open tabs instead of juggling lots of separate terminal windows.</li>
        <li><strong>Consistent environment:</strong> Every pane/tab you open inside that Terminator window is automatically inside the Docker container, so you don&rsquo;t have to re-attach or run <code>docker exec</code> for each new terminal.</li>
        <li><strong>Cleaner workflow:</strong> This setup mirrors how real robotics development is done &mdash; multiple processes running side by side, easy to monitor and control.</li>
    </ul>
    <h4>How to Use Terminator Effectively</h4>
    <ol>
        <li><strong>Open Terminator:</strong> From inside the container:
            <pre><code class="language-bash">terminator</code></pre>
            <p>Don&rsquo;t type anything else in the original shell &mdash; it&rsquo;s now just running Terminator.</p>
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
    <p>If you close Terminator or open a <strong>new terminal window in your VM</strong>, that new terminal is <strong>not inside the container</strong>. If you want it linked, you need to re-attach manually:</p>
    <pre><code class="language-bash">docker exec -it &lt;container_name&gt; bash</code></pre>
    <p>For example, if your container is named <code>lab02</code>:</p>
    <pre><code class="language-bash">docker exec -it lab02 bash</code></pre>
    <p>This drops you back into the running container from any new terminal.</p>
    <h3>4.4 ROS 2 Environment Setup (One-Time)</h3>
    <p>Inside a <strong>terminal connected to the Docker container</strong>, run the following commands to update your <code>~/.bashrc</code>:</p>
    <pre><code class="language-bash">echo "export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST" &gt;&gt; ~/.bashrc
echo "export ROS_STATIC_PEERS='192.168.0.1;remote.com'" &gt;&gt; ~/.bashrc
source ~/.bashrc</code></pre>
    <p>This ensures ROS 2 uses localhost discovery and sets static peers for networking.</p>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;">You only need to run this once per Docker session. Close and reopen the terminal <em>within</em> Docker (or run <code>source ~/.bashrc</code>) for the changes to take effect.</blockquote>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Note:</strong> Future Docker images will have these variables preconfigured &mdash; you do not need to repeat this step in later labs.</div>
    <h3>4.5 Complete Jazzy Beginner CLI Tutorials</h3>
    <p>Inside the container&rsquo;s <strong>Terminator</strong> panes, follow these tutorials from the official ROS 2 documentation <strong>in order</strong>. As you work through them, focus not just on typing commands, but on understanding what each tells you about the ROS 2 system.</p>
    <p>You must capture <strong>one screenshot per tutorial</strong> for your deliverables:</p>
    <ol>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html" target="_blank" rel="noopener">Introducing Turtlesim</a>
            <ul>
                <li>📸 <strong>Screenshot:</strong> both <strong>turtle1</strong> and <strong>turtle2</strong> visible, each controlled by a different teleop terminal (after remapping).</li>
            </ul>
        </li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html" target="_blank" rel="noopener">Understanding ROS 2 Nodes</a>
            <ul>
                <li>📸 <strong>Screenshot:</strong> terminal output of <code>ros2 node info /my_turtle</code> after remapping the node name.</li>
            </ul>
        </li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html" target="_blank" rel="noopener">Understanding ROS 2 Topics</a>
            <ul>
                <li>📸 <strong>Screenshot:</strong> <strong>rqt_graph</strong> showing <code>/teleop_turtle</code> publishing to <code>/turtle1/cmd_vel</code> and <code>/turtlesim</code> subscribing.</li>
            </ul>
        </li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.html" target="_blank" rel="noopener">Understanding ROS 2 Services</a>
            <ul>
                <li>📸 <strong>Screenshot:</strong> turtlesim window after spawning a new turtle using the <code>/spawn</code> service.</li>
            </ul>
        </li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.html" target="_blank" rel="noopener">Understanding ROS 2 Parameters</a>
            <ul>
                <li>📸 <strong>Screenshot:</strong> turtlesim window with <strong>modified background color</strong> (e.g., after <code>ros2 param set</code>).</li>
            </ul>
        </li>
    </ol>
    <h3>4.6 Stretch Goal (Optional)</h3>
    <p>To prepare for Lab 3, create a simple Bash script that automates one of the commands you used in this lab. For example:</p>
    <pre><code class="language-bash">#!/bin/bash
# Move the turtle forward once
ros2 topic pub -1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 0.0}}"</code></pre>
    <ul>
        <li>Save your script as <code>move_turtle.sh</code> inside your repository.</li>
        <li>Make it executable: <code>chmod +x move_turtle.sh</code>.</li>
        <li>Run it inside your container to verify it moves the turtle.</li>
    </ul>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;">This is optional, but it will help you transition from using the CLI to writing scripts in the next lab.</blockquote>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="discussion">
    <h2>5. Discussion Questions</h2>
    <p>Answer the following in complete sentences. Your responses should be included <strong>only in the Gradescope PDF</strong> (not pushed to GitHub).</p>
    <ol>
        <li>What challenges, if any, did you encounter running a graphical ROS 2 application (Turtlesim) inside Docker? How did you resolve them?</li>
        <li>Explain how the <code>turtle_teleop_key</code> node communicates with the <code>turtlesim_node</code> to make the turtle move. Use the terms <strong>node</strong>, <strong>topic</strong>, and <strong>publish/subscribe</strong>.</li>
        <li>Give an example from this lab where using a <strong>service</strong> was more appropriate than using a topic. Why was the request/response model necessary?</li>
        <li>Why are <strong>parameters</strong> valuable for making nodes flexible? Explain using the background color change as a specific example.</li>
    </ol>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
