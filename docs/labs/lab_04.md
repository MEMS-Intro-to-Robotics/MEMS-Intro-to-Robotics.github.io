---
title: "Lab 04: ROS 2 Python Nodes"
---

# Lab 04: ROS 2 Python Nodes

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#task1">Task 1 &mdash; Create the Workspace and Package</a></li>
                <li><a href="#task2">Task 2 &mdash; Node A (Publisher)</a></li>
                <li><a href="#task3">Task 3 &mdash; Node B (Relay)</a></li>
                <li><a href="#task4">Task 4 &mdash; Node C (Subscriber)</a></li>
            </ol>
        </li>
        <li><a href="#analysis">Analysis and Discussion</a></li>
        <li><a href="#appendix">Appendix: ROS 2 Python API Reference</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>In this lab, you will transition from shell scripting ROS 2 commands in the terminal to <strong>writing your own ROS 2 nodes in Python</strong>. Instead of calling <code>ros2 topic pub</code> from a script, you&rsquo;ll write Python programs that do the same thing automatically.</p>
    <p>You will:</p>
    <ul>
        <li>Create a <strong>ROS 2 workspace</strong> and a <strong>package</strong> from scratch.</li>
        <li>Implement a three-node pipeline:
            <ol>
                <li>A <strong>publisher node</strong> creates data.</li>
                <li>A <strong>relay node</strong> subscribes, transforms the data, and republishes it.</li>
                <li>A <strong>subscriber node</strong> listens to the final topic and logs results.</li>
            </ol>
        </li>
    </ul>
    <p>This workflow mirrors how real robotic systems are built: sensors produce data, processing nodes interpret it, and actuators respond. This lab is your <strong>first step into true robotics software development</strong>.</p>
    <h3>1.2 Background</h3>
    <p><strong>From Scripts to Python</strong></p>
    <ul>
        <li>In Lab 3, you used shell scripts to send commands like <code>ros2 topic pub</code> and <code>ros2 service call</code>. This worked for automation, but had no ability to &ldquo;think&rdquo;&mdash;no variables, conditions, or loops.</li>
        <li>Python fills that gap. It is one of the primary languages for ROS 2 (along with C++) and allows you to implement real robot logic.</li>
    </ul>
    <p><strong>Workspaces and Packages</strong></p>
    <ul>
        <li>ROS 2 offers <strong>nodes</strong> which allow you to publish and subscribe to topics.</li>
        <li>ROS 2 organizes code into <strong>packages</strong> (folders containing your code, <code>package.xml</code> metadata, and build instructions).</li>
        <li>Multiple packages live inside a <strong>workspace</strong> (usually created with <code>ros2_ws</code> or <code>colcon_ws</code> naming).</li>
        <li>You build a workspace with <code>colcon build</code>, which:
            <ul>
                <li>Detects packages,</li>
                <li>Compiles or registers them,</li>
                <li>Makes your executables available to <code>ros2 run</code>.</li>
            </ul>
        </li>
        <li>You&rsquo;ll use the <strong>colcon tool</strong> for every project that contains source code.</li>
    </ul>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Analogy</strong><br />Think of a <strong>workspace</strong> as a toolbox. Each <strong>package</strong> is one tool in that toolbox. <code>colcon build</code> is what sharpens all the tools and puts them in the right slots so you can actually use them.</blockquote>
    <p><strong>Examples in Robotics:</strong></p>
    <ul>
        <li><strong>Node</strong> &ndash; The <strong>camera driver node</strong> that actually grabs images from the robot&rsquo;s camera sensor.</li>
        <li><strong>Package</strong> &ndash; The <strong>camera package</strong> that includes the driver node, a calibration tool, and a node that publishes the images in different formats (all the software you need for the camera).</li>
        <li><strong>Workspace</strong> &ndash; The <strong>robot&rsquo;s software workspace</strong> that holds the camera package along with other packages like motor control, navigation, or perception (everything the robot needs to run).</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you will be able to:</p>
    <ul>
        <li>Create and build a ROS 2 workspace and a custom Python package.</li>
        <li>Implement a <strong>publisher node</strong> in Python that publishes on a timer.</li>
        <li>Implement a <strong>relay node</strong> that subscribes to a topic, modifies the data, and republishes it.</li>
        <li>Implement a <strong>subscriber node</strong> in Python that receives and logs messages.</li>
        <li>Use <code>colcon build</code> to compile your workspace and <code>ros2 run</code> to execute your nodes.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Verify each item before arriving at lab.</p>
    </div>
    <ul>
        <li>[ ] <strong>Docker Environment:</strong> You can start the course Docker container with your repo mounted at <code>~/workspaces</code>.
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab04 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/workspaces:/root/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest bash</code></pre>
        </li>
        <li>[ ] <strong>ROS 2 Tutorial:</strong> Review the official ROS 2 tutorial <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html" target="_blank" rel="noopener">&ldquo;Writing a simple publisher and subscriber (Python)&rdquo;</a>. This is the direct foundation for this lab.</li>
        <li>[ ] <strong>Verify GitHub SSH access:</strong>
            <pre><code class="language-bash">ssh -T git@github.com</code></pre>
            <p>You should see a message like <em>&ldquo;Hi USERNAME! You&rsquo;ve successfully authenticated...&rdquo;</em></p>
        </li>
        <li>[ ] <strong>Understand where to do what:</strong>
            <ul>
                <li><strong>Edit code on your VM (host)</strong> in <strong>VS Code</strong>. Do <strong>not</strong> run VS Code inside Docker&mdash;it isn&rsquo;t installed there.</li>
                <li><strong>Run all ROS 2 commands inside the Docker container</strong> (build, source, run).</li>
                <li>Path mapping: <strong>VM</strong> <code>~/workspaces</code> &harr; <strong>container</strong> <code>~/workspaces</code>.</li>
            </ul>
        </li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <h3>The Core ROS 2 Development Workflow</h3>
    <p><strong>Memorize this 3-step loop.</strong> You&rsquo;ll use it constantly.</p>
    <ol>
        <li><strong>Edit Code (on your VM in VS Code)</strong><br />Modify your Python files (e.g., <code>node_a.py</code>) <strong>in your package&rsquo;s source folder.</strong></li>
        <li><strong>Build Workspace (from the workspace root, not <code>src/</code>)</strong>
            <pre><code class="language-bash">colcon build --symlink-install</code></pre>
            <p>This discovers packages, registers Python entry points, and updates executables.</p>
        </li>
        <li><strong>Source Workspace (in every new terminal)</strong>
            <pre><code class="language-bash">source ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws/install/setup.bash</code></pre>
            <p>This tells the shell where to find your newly built nodes.</p>
        </li>
    </ol>
    <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Why things break:</strong>
        <ul>
            <li>If you <strong>forget to build</strong>, you&rsquo;ll run old code.</li>
            <li>If you <strong>forget to source</strong> in a <em>new</em> terminal (e.g., after <code>docker exec</code>), you&rsquo;ll see &ldquo;command not found&rdquo; or &ldquo;package not found.&rdquo;</li>
        </ul>
    </blockquote>
    <section id="task1">
        <h3>Task 1 &mdash; Create the Workspace and Package</h3>
        <p><strong>Goal:</strong> Create a minimal ROS 2 Python package inside a new workspace and confirm the build/sourcing cycle works.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> All commands below are run <strong>inside the container</strong>.</blockquote>
        <h4>Step 1.1: Accept the GitHub Classroom Assignment and Clone Your Repository</h4>
        <ol>
            <li><strong>Accept the assignment:</strong> Click the following link to create your Lab 4 repository:
                <p style="margin: 1em 0;"><a style="font-size: 1.1em;" href="https://classroom.github.com/a/4qSQp5NH" target="_blank" rel="noopener">https://classroom.github.com/a/4qSQp5NH</a></p>
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
                <pre><code>https://github.com/MEMS-Intro-to-Robotics/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME</code></pre>
            </li>
            <li><strong>Clone the repository into your workspace:</strong>
                <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME.git
cd ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME</code></pre>
                <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your actual GitHub username.</p>
            </li>
        </ol>
        <h4>Step 1.2: Make the workspace skeleton inside your repo</h4>
        <pre><code class="language-bash"># From inside your cloned repo
mkdir -p ros2_ws/src docs
cd ros2_ws/src</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> <code>src/</code> is where your packages live. The <strong>workspace root</strong> is <code>ros2_ws</code>.<br />❌ Don&rsquo;t build from <code>src/</code>&mdash;always build from the <strong>workspace root</strong>.</blockquote>
        <h4>Step 1.3: Create a new Python package</h4>
        <pre><code class="language-bash">ros2 pkg create --build-type ament_python lab04_pub_sub --dependencies rclpy std_msgs</code></pre>
        <p><strong>Understanding the Command:</strong></p>
        <ul>
            <li><code><strong>ros2 pkg create</strong></code> &ndash; The ROS 2 CLI tool to generate a new package with the right folder structure and metadata files.</li>
            <li><code><strong>--build-type ament_python</strong></code> &ndash; ROS 2 packages can be built with different systems depending on whether they&rsquo;re C++ or Python. Here you&rsquo;re saying <em>&ldquo;this will be a Python package.&rdquo;</em></li>
            <li><code><strong>lab04_pub_sub</strong></code> &ndash; This is the name of your package. ROS 2 will create a folder with this name and set up the required files inside it.</li>
            <li><code><strong>--dependencies rclpy std_msgs</strong></code> &ndash; Declares dependencies on the <strong>ROS 2 Python API</strong> (<code>rclpy</code>) and common message types (<code>std_msgs</code>) in <code>package.xml</code>.</li>
        </ul>
        <h4>Step 1.4: Build the (currently empty) package</h4>
        <pre><code class="language-bash"># Go to the workspace root in your docker container
cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
# Build everything in the workspace
colcon build --symlink-install</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>About <code>--symlink-install</code>:</strong><br />This is a time-saving trick for you. For Python, this creates symlinks so you can edit .py files and run your nodes again without rebuilding (<code>colcon build</code>)&mdash;as long as you don&rsquo;t add new files or change package metadata. If you add a new Python file or entry point, then you need to rebuild.</blockquote>
        <p><strong>Expected output (excerpt):</strong></p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>Starting &gt;&gt;&gt; lab04_pub_sub
Finished &lt;&lt;&lt; lab04_pub_sub
Summary: 1 package finished</code></pre>
        </div>
        <h4>Step 1.5: Source and verify ROS 2 can see your package</h4>
        <pre><code class="language-bash"># Source the workspace (do this in every new terminal)
source install/setup.bash
# Confirm the package is discoverable
ros2 pkg list | grep lab04_pub_sub</code></pre>
        <p><strong>Checkpoint:</strong> You should see <code>lab04_pub_sub</code> printed.<br /><em>(It&rsquo;s normal that <code>ros2 pkg executables lab04_pub_sub</code> shows nothing yet&mdash;we haven&rsquo;t added nodes.)</em></p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Pro tips</strong>
            <ul>
                <li>If you open another shell with <code>docker exec -it lab04 bash</code>, you must <strong>source again</strong> in that new shell. That&rsquo;s because when you run <code>docker exec</code> you&rsquo;re creating a <strong>new shell process</strong> inside the running container. Each new shell starts with a &ldquo;clean slate&rdquo; in terms of environment variables.</li>
                <li>If <code>ros2 pkg list</code> doesn&rsquo;t show your package, check:
                    <ul>
                        <li>Did you build from the <strong>workspace root</strong> (<code>ros2_ws</code>, not <code>src/</code>)?</li>
                        <li>Did the build succeed with no errors?</li>
                        <li>Did you run <code>source install/setup.bash</code> in the <strong>same terminal</strong>?</li>
                    </ul>
                </li>
            </ul>
        </blockquote>
    </section>
    <section id="task2">
        <h3>Task 2 &mdash; Node A (Publisher)</h3>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Editing vs. running:</strong> Create/edit files on the VM in VS Code; build/source/run inside the Docker container.</blockquote>
        <p><strong>Goal:</strong> Create a Python node that publishes a string message every 2 seconds.</p>
        <h4>Step 2.1: Open the repo in VS Code</h4>
        <p>On your VM (<strong>not inside the Docker container</strong>):</p>
        <pre><code class="language-bash">code ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME</code></pre>
        <h4>Step 2.2: Create the Python file</h4>
        <p>So far you have created your ROS 2 package, but it doesn&rsquo;t actually contain any code yet. Every ROS 2 node you write in Python lives inside a <strong>.py file</strong> within your package&rsquo;s source directory.</p>
        <p>In VS Code, create a new file named <strong>node_a.py</strong> inside the directory <code>ros2_ws/src/lab04_pub_sub/lab04_pub_sub/</code></p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Tip:</strong> If you see a permissions error, you can fix it by running the following on your VM:
            <pre><code class="language-bash">sudo chown -R $USER:$USER ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME</code></pre>
        </blockquote>
        <h4>Step 2.3: Write the publisher node code</h4>
        <p>In this step, you&rsquo;ll write the <strong>actual Python code</strong> for your first ROS 2 node. This node will act as a <strong>publisher</strong>:</p>
        <ul>
            <li>A <strong>publisher node</strong> is a program that sends out messages on a topic at some rate.</li>
            <li>Other nodes (subscribers) can connect to that topic and react to the data.</li>
            <li>In our case, Node A will publish the string message <code>"Hello from Node A!"</code> every 2 seconds on the topic <code>/topic_a_to_b</code>.</li>
        </ul>
        <p>Use the following scaffold. <strong>This is not a completed version&mdash;you need to fill in the TODOs yourself.</strong></p>
        <pre><code class="language-python">import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PubNodeA(Node):
    def __init__(self):
        super().__init__('node_a')
        
        # TODO: Create a publisher for String messages
        # - Use topic: '/topic_a_to_b'
        # - Message type: String
        # - Queue size: 10
        self.pub = None   # Replace None with your publisher

        # TODO: Create a timer that calls self.timer_callback every 2.0 seconds
        self.timer = None # Replace None with your timer

        self.get_logger().info("Node A has started. Publishing...")

    def timer_callback(self):
        msg = String()
        msg.data = "Hello from Node A!"
        
        # TODO: Publish msg using your publisher
        # self.pub.____(msg)

        self.get_logger().info(f'Publishing: "{msg.data}"')

# TODO: Write the main function boilerplate
# - Initialize rclpy
# - Create the node
# - Call rclpy.spin(node) to keep it alive
# - Destroy the node and shutdown when done</code></pre>
        <p><strong>Hints for each TODO:</strong></p>
        <ul>
            <li>Publisher: the method is <code>self.create_publisher(...)</code></li>
            <li>Timer: the method is <code>self.create_timer(...)</code></li>
            <li>Publish: the method is <code>.publish(msg)</code></li>
            <li>Main function: look back at the <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html" target="_blank" rel="noopener">ROS 2 &ldquo;Writing a Simple Publisher and Subscriber (Python)&rdquo; tutorial</a></li>
            <li>Utilize the <strong>Appendix section</strong> at the bottom of this document for more information about the ROS 2 functions you will use</li>
        </ul>
        <h4>Step 2.4: Add the entry point to <code>setup.py</code></h4>
        <p>So far, you wrote a Python script (<code>node_a.py</code>) that defines a ROS 2 node. But ROS 2 doesn&rsquo;t automatically know how to run your script. We need a way to tell ROS 2 how to run your Python script, and that&rsquo;s the job of the <code>setup.py</code> file.</p>
        <p>Open:</p>
        <pre><code>ros2_ws/src/lab04_pub_sub/setup.py</code></pre>
        <p>Find the <code>entry_points</code> section and add:</p>
        <pre><code class="language-python">entry_points={
    'console_scripts': [
        'node_a = lab04_pub_sub.node_a:main',
    ],
},</code></pre>
        <p>Where <code>lab04_pub_sub</code> is your package name, <code>node_a</code> is the name of your Python script, and <code>main</code> is the function that should be run.</p>
        <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Common pitfall:</strong> Do not write <code>.py</code> in the entry point. It&rsquo;s <code>node_a:main</code>, not <code>node_a.py:main</code>.</div>
        <h4>Step 2.5: Build and source</h4>
        <p>Now that your package has code (<code>node_a.py</code>) and an entry point in <code>setup.py</code>, ROS 2 still doesn&rsquo;t know about it yet. To make ROS 2 aware of your new package and executable, you need to:</p>
        <ol>
            <li><strong>Build the workspace</strong> &rarr; turn your package into something ROS 2 can run.</li>
            <li><strong>Source the workspace</strong> &rarr; update your environment so ROS 2 can discover what you just built.</li>
        </ol>
        <p>From the workspace root within your Docker container:</p>
        <pre><code class="language-bash">cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
colcon build --symlink-install
source install/setup.bash</code></pre>
        <h4>Step 2.6: Run Node A</h4>
        <p>You&rsquo;ve now:</p>
        <ol>
            <li>Written the code for <strong>Node A</strong> (a publisher).</li>
            <li>Registered it in <code>setup.py</code> with an <strong>entry point</strong>.</li>
            <li>Built and sourced the workspace so ROS 2 knows about it.</li>
        </ol>
        <p>The last step is to <strong>actually run the node</strong>:</p>
        <pre><code class="language-bash">ros2 run lab04_pub_sub node_a</code></pre>
        <p>You should see your logger printing &ldquo;Node A has started. Publishing...&rdquo; and &ldquo;Publishing: "Hello from Node A!"&rdquo; messages.</p>
        <h4>Step 2.7: Verify the topic</h4>
        <p>Running your node in one terminal proves that it starts up and logs messages, but how do you know that the messages are actually being sent over ROS 2?</p>
        <p>To check, open a <strong>new terminal</strong> within the Docker container (remember: <code>docker exec</code> + <code>source</code> again):</p>
        <pre><code class="language-bash">docker exec -it lab04 bash
source ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws/install/setup.bash
ros2 topic echo /topic_a_to_b</code></pre>
        <p><strong>Checkpoint:</strong></p>
        <ul>
            <li>First terminal: your node&rsquo;s logger messages.</li>
            <li>Second terminal: plain topic messages:
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>data: "Hello from Node A!"
---</code></pre>
                </div>
                every 2 seconds.
            </li>
        </ul>
    </section>
    <section id="task3">
        <h3>Task 3 &mdash; Node B (Relay)</h3>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Editing vs. running:</strong> Create/edit files on the VM in VS Code; build/source/run inside the Docker container.</blockquote>
        <p><strong>Goal:</strong> Create a node that <strong>subscribes</strong> to Node A&rsquo;s topic, <strong>modifies</strong> the message, and <strong>republishes</strong> it to a new topic.</p>
        <p>Now that Node A is publishing messages, it&rsquo;s time to create <strong>Node B</strong>, which will act as a <strong>relay node</strong>. Unlike Node A, which only sends messages, Node B will:</p>
        <ul>
            <li><strong>Subscribe</strong> to Node A&rsquo;s topic (<code>/topic_a_to_b</code>)</li>
            <li><strong>Modify</strong> the message it receives (for example, by appending extra text)</li>
            <li><strong>Republish</strong> the new message on a different topic (<code>/topic_b_to_c</code>)</li>
        </ul>
        <h4>Step 3.1: Create the Python file</h4>
        <p>In VS Code, create <strong><code>node_b.py</code></strong> in the same folder as <code>node_a.py</code>:</p>
        <pre><code>ros2_ws/src/lab04_pub_sub/lab04_pub_sub/</code></pre>
        <h4>Step 3.2: Write the relay node code (scaffold with TODOs)</h4>
        <p>Your relay must append <strong>your NetID</strong> to the relayed message so that it&rsquo;s visible in screenshots (e.g., <code>-- processed by Node B (abc123)</code>). You may hardcode it or read it from an environment variable.</p>
        <p>Paste the scaffold below and <strong>fill in the TODOs yourself</strong>:</p>
        <pre><code class="language-python">import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PubSubNodeB(Node):
    def __init__(self):
        super().__init__('node_b')

        # TODO: Set your NetID for tagging the relayed message
        # Option A (recommended for simplicity): replace 'your_netid' with your actual NetID.
        # Option B: set an env var NETID in the container and keep the fallback.
        self.netid = os.getenv("NETID", "your_netid").strip()  # &lt;-- replace 'your_netid'

        # TODO: Create a subscriber to '/topic_a_to_b'
        # - Message type: String
        # - Callback: self._on_msg
        # - Queue size: 10 (typical keep-last depth)
        self.sub = None  # Replace with create_subscription(...)

        # TODO: Create a publisher to '/topic_b_to_c'
        # - Message type: String
        # - Queue size: 10
        self.pub = None  # Replace with create_publisher(...)

        self.get_logger().info("Node B has started. Listening and relaying...")

    def _on_msg(self, msg: String):
        self.get_logger().info(f'Heard from A: "{msg.data}"')

        new_msg = String()
        # TODO: Modify the incoming message and assign to new_msg.data
        # Must append your NetID so it appears in screenshots, e.g.:
        # new_msg.data = f'{msg.data} -- processed by Node B ({self.netid})'

        # TODO: Publish the new message to '/topic_b_to_c'
        # self.pub.____(new_msg)

        self.get_logger().info(f'Relaying to C: "{new_msg.data}"')

# TODO: Add main() boilerplate:
# - rclpy.init()
# - construct PubSubNodeB
# - rclpy.spin(node)
# - destroy node and rclpy.shutdown()</code></pre>
        <p><strong>Hints:</strong></p>
        <ul>
            <li>Subscriber: <code>self.create_subscription(String, '/topic_a_to_b', self._on_msg, 10)</code></li>
            <li>Publisher: <code>self.create_publisher(String, '/topic_b_to_c', 10)</code></li>
            <li>Publish: <code>self.pub.publish(new_msg)</code></li>
            <li>The callback signature should accept one parameter: the incoming <code>String</code> message.</li>
        </ul>
        <h4>Step 3.3: Add the entry point to <code>setup.py</code></h4>
        <p>Open:</p>
        <pre><code>ros2_ws/src/lab04_pub_sub/setup.py</code></pre>
        <p>In the <code>entry_points</code> block, <strong>add a second line</strong> for <code>node_b</code>:</p>
        <pre><code class="language-python">entry_points={
    'console_scripts': [
        'node_a = lab04_pub_sub.node_a:main',
        'node_b = lab04_pub_sub.node_b:main',  # &lt;-- add this
    ],
},</code></pre>
        <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Common pitfall:</strong> It&rsquo;s <code>lab04_pub_sub.node_b:main</code> (no <code>.py</code>).</div>
        <h4>Step 3.4: Build and source (from workspace root)</h4>
        <pre><code class="language-bash">cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
colcon build --symlink-install
source install/setup.bash</code></pre>
        <h4>Step 3.5: Run the nodes (three terminals)</h4>
        <p><strong>Terminal 1 (container):</strong> run Node A</p>
        <pre><code class="language-bash">cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash
ros2 run lab04_pub_sub node_a</code></pre>
        <p><strong>Terminal 2 (container):</strong> run Node B</p>
        <pre><code class="language-bash">docker exec -it lab04 bash
cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash
ros2 run lab04_pub_sub node_b</code></pre>
        <p><strong>Terminal 3 (container):</strong> echo Node B&rsquo;s output topic</p>
        <pre><code class="language-bash">docker exec -it lab04 bash
source ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws/install/setup.bash
ros2 topic echo /topic_b_to_c</code></pre>
        <h4>Checkpoint</h4>
        <ul>
            <li><strong>Terminal 1</strong>: Node A logs its published messages.</li>
            <li><strong>Terminal 2</strong>: Node B logs &ldquo;Heard from A: ...&rdquo; and &ldquo;Relaying to C: ...&rdquo;.</li>
            <li><strong>Terminal 3</strong>: You should see the <strong>modified</strong> message content, e.g.:
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>data: "Hello from Node A! -- processed by Node B (abc123)"
---</code></pre>
                </div>
            </li>
        </ul>
        <h4>Common gotchas</h4>
        <ul>
            <li><strong>Nothing on <code>/topic_b_to_c</code></strong> &rarr; Check that Node B&rsquo;s subscriber topic name matches Node A&rsquo;s publisher (<code>/topic_a_to_b</code>) and that you <strong>published</strong> <code>new_msg</code>.</li>
            <li><strong><code>ros2 run</code> says command not found</strong> &rarr; Rebuild + re-source; confirm <code>setup.py</code> entry point lines.</li>
            <li><strong>Node B never logs</strong> &rarr; Ensure both nodes are running, both terminals sourced, and queue sizes exist (10 is fine).</li>
        </ul>
    </section>
    <section id="task4">
        <h3>Task 4 &mdash; Node C (Subscriber)</h3>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Editing vs. running:</strong> Create/edit files on the VM in VS Code; build/source/run inside the Docker container.</blockquote>
        <p><strong>Goal:</strong> Create a final node that <strong>subscribes</strong> to Node B&rsquo;s output (<code>/topic_b_to_c</code>) and <strong>logs</strong> the result.</p>
        <p>You&rsquo;ve already built a small message pipeline:</p>
        <ul>
            <li><strong>Node A</strong> publishes data on <code>/topic_a_to_b</code>.</li>
            <li><strong>Node B</strong> subscribes, modifies, and republishes on <code>/topic_b_to_c</code>.</li>
        </ul>
        <p>Now you&rsquo;ll complete the chain with <strong>Node C</strong>, a pure <strong>subscriber node</strong>.</p>
        <h4>Step 4.1: Create the Python file</h4>
        <p>Create <strong><code>node_c.py</code></strong> in the same folder as the other nodes:</p>
        <pre><code>ros2_ws/src/lab04_pub_sub/lab04_pub_sub/</code></pre>
        <h4>Step 4.2: Write the node code (scaffold with TODOs)</h4>
        <p>Paste this scaffold and <strong>fill in the TODOs yourself</strong>:</p>
        <pre><code class="language-python">import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SubNodeC(Node):
    def __init__(self):
        super().__init__('node_c')
        
        # TODO: Create a subscriber to '/topic_b_to_c'
        # - Message type: String
        # - Callback: self._on_msg
        # - Queue size: 10
        self.sub = None  # Replace with create_subscription(...)

        self.get_logger().info("Node C has started. Listening...")

    def _on_msg(self, msg: String):
        self.get_logger().info(f'Final message received: "{msg.data}"')

# TODO: Write main():
# - rclpy.init()
# - construct SubNodeC
# - rclpy.spin(node)
# - destroy node and rclpy.shutdown()</code></pre>
        <p><strong>Hints:</strong></p>
        <ul>
            <li>Subscriber creation mirrors Node B&rsquo;s subscriber, just with the topic <code>'/topic_b_to_c'</code>.</li>
            <li>Use the same <code>main()</code> boilerplate pattern as Node A/B.</li>
        </ul>
        <h4>Step 4.3: Add the entry point to <code>setup.py</code></h4>
        <p>In the <code>entry_points</code> block, add a third line:</p>
        <pre><code class="language-python">entry_points={
    'console_scripts': [
        'node_a = lab04_pub_sub.node_a:main',
        'node_b = lab04_pub_sub.node_b:main',
        'node_c = lab04_pub_sub.node_c:main',  # &lt;-- add this
    ],
},</code></pre>
        <h4>Step 4.4: Build and source (workspace root)</h4>
        <pre><code class="language-bash">cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
colcon build --symlink-install
source install/setup.bash</code></pre>
        <h4>Step 4.5: Run the full pipeline (three terminals)</h4>
        <p><strong>Terminal 1 (container):</strong> Node A</p>
        <pre><code class="language-bash">cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash
ros2 run lab04_pub_sub node_a</code></pre>
        <p><strong>Terminal 2 (container):</strong> Node B</p>
        <pre><code class="language-bash">docker exec -it lab04 bash
cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash
ros2 run lab04_pub_sub node_b</code></pre>
        <p><strong>Terminal 3 (container):</strong> Node C</p>
        <pre><code class="language-bash">docker exec -it lab04 bash
cd ~/workspaces/ros2-publisher-and-subscriber-in-python-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash
ros2 run lab04_pub_sub node_c</code></pre>
        <h4>Final Checkpoint</h4>
        <ul>
            <li>Node A logs what it&rsquo;s publishing.</li>
            <li>Node B logs what it heard from A and what it relays to C.</li>
            <li><strong>Node C logs the final processed message</strong> (the one B modified). Expect something like:
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[INFO] [node_c]: Final message received: "Hello from Node A! -- processed by Node B (abc123)"</code></pre>
                </div>
            </li>
        </ul>
        <h4>Visualize Nodes &amp; Topics with <code>rqt_graph</code></h4>
        <ol>
            <li>In a <strong>new terminal on your VM (host)</strong>, attach to the running Docker container:
                <pre><code class="language-bash">docker exec -it lab04 bash</code></pre>
            </li>
            <li>Inside the <strong>container</strong>, launch the ROS 2 graph:
                <pre><code class="language-bash">rqt_graph</code></pre>
            </li>
            <li>You should see nodes <strong>A</strong>, <strong>B</strong>, and <strong>C</strong> connected by the topics:
                <pre><code>/topic_a_to_b
/topic_b_to_c</code></pre>
            </li>
            <li>📸 <strong>Screenshot Requirement:</strong> Take a screenshot of this graph and include it in your submission.</li>
        </ol>
        <h4>Quick Troubleshooting</h4>
        <ul>
            <li><strong><code>ros2 run lab04_pub_sub node_c</code> &rarr; command not found</strong>
                <ul>
                    <li>Recheck <code>setup.py</code> entry point and <strong>rebuild + source</strong>.</li>
                </ul>
            </li>
            <li><strong>Node C shows nothing</strong>
                <ul>
                    <li>Confirm A and B are running and their terminal windows are sourced.</li>
                    <li>Verify topic names: A &rarr; <code>/topic_a_to_b</code>, B subscribes that and publishes <code>/topic_b_to_c</code>, C subscribes <code>/topic_b_to_c</code>.</li>
                </ul>
            </li>
        </ul>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion Questions</h2>
    <p>Answer these in your Gradescope submission. Aim for <strong>short but thoughtful</strong> responses.</p>
    <ol>
        <li><strong>Node Relationships</strong>
            <ul>
                <li>Looking at the <code>rqt_graph</code> output, describe how the three nodes are connected.</li>
                <li>How does this reflect the flow of data in a real robotic system?</li>
            </ul>
        </li>
        <li><strong>Subscriber Callbacks</strong>
            <ul>
                <li>In Node B, what role does the subscriber callback (<code>_on_msg</code>) play in processing messages?</li>
                <li>Why is this event-driven design important in robotics?</li>
            </ul>
        </li>
        <li><strong>Build and Source Cycle</strong>
            <ul>
                <li>Why does ROS 2 require both <code>colcon build</code> and <code>source install/setup.bash</code>?</li>
                <li>What common mistakes occur if you skip one of these steps?</li>
            </ul>
        </li>
        <li><strong>Extending the Pipeline</strong>
            <ul>
                <li>Imagine you wanted to add a <strong>Node D</strong> that filters out certain messages (e.g., only passes along messages containing a keyword).</li>
                <li>Where would it connect in the pipeline, and how would it change the overall system?</li>
            </ul>
        </li>
    </ol>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>Appendix: ROS 2 Python API Reference</h2>
    <p>This reference contains everything you need for Lab 4. You&rsquo;re welcome to use outside resources if necessary, but the reference below is comprehensive.</p>
    <h3>Node Creation &amp; Main Function</h3>
    <p>Every node file must include a <code>main()</code> function. This handles <strong>initialization, spinning, and cleanup</strong>.</p>
    <pre><code class="language-python">def main(args=None):
    rclpy.init(args=args)
    my_node = PubNodeA()   # Replace with your class name
    rclpy.spin(my_node)    # Keeps the node alive
    my_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()</code></pre>
    <h3>Publisher</h3>
    <p><strong>Method:</strong></p>
    <pre><code class="language-python">self.create_publisher(msg_type, topic_name, queue_size)</code></pre>
    <ul>
        <li><code>msg_type</code> &rarr; the message type (e.g., <code>String</code>)</li>
        <li><code>topic_name</code> &rarr; the topic to publish on (string, e.g., <code>'/topic_a_to_b'</code>)</li>
        <li><code>queue_size</code> &rarr; how many messages to buffer if the subscriber is slow (use <code>10</code>)</li>
    </ul>
    <p><strong>Example:</strong></p>
    <pre><code class="language-python">self.pub = self.create_publisher(String, '/topic_a_to_b', 10)
self.pub.publish(msg)</code></pre>
    <h3>Subscriber</h3>
    <p><strong>Method:</strong></p>
    <pre><code class="language-python">self.create_subscription(msg_type, topic_name, callback, queue_size)</code></pre>
    <ul>
        <li>The <strong>callback</strong> runs whenever a message arrives.</li>
        <li>The callback must accept <strong>exactly one argument</strong> (the incoming message).</li>
    </ul>
    <p><strong>Example:</strong></p>
    <pre><code class="language-python">self.sub = self.create_subscription(String, '/topic_a_to_b', self._on_msg, 10)

def _on_msg(self, msg):
    self.get_logger().info(f'Received: "{msg.data}"')</code></pre>
    <h3>Timer</h3>
    <p><strong>Method:</strong></p>
    <pre><code class="language-python">self.create_timer(period_seconds, callback)</code></pre>
    <ul>
        <li>Calls the given method periodically.</li>
        <li>The callback takes <strong>no arguments</strong>.</li>
    </ul>
    <p><strong>Example:</strong></p>
    <pre><code class="language-python">self.timer = self.create_timer(2.0, self._tick)

def _tick(self):
    self.get_logger().info("Timer fired!")</code></pre>
    <h3>Messages</h3>
    <p>We&rsquo;ll use the <strong>String</strong> message type in this lab.</p>
    <pre><code class="language-python">from std_msgs.msg import String

msg = String()
msg.data = "your content here"</code></pre>
    <h3>Logging</h3>
    <p>Inside a node, use the built-in logger:</p>
    <pre><code class="language-python">self.get_logger().info("Plain message")
self.get_logger().info(f'Value is: {my_var}')</code></pre>
    <h3>Troubleshooting</h3>
    <ul>
        <li><strong><code>ros2 run</code> says &ldquo;command not found&rdquo;</strong>
            <ul>
                <li>Did you add an entry point in <code>setup.py</code>?</li>
                <li>Did you rebuild with <code>colcon build</code>?</li>
                <li>Did you <code>source install/setup.bash</code> in this terminal?</li>
            </ul>
        </li>
        <li><strong>Code changes not showing up</strong>
            <ul>
                <li>If you didn&rsquo;t use <code>--symlink-install</code>, you must rebuild after every change.</li>
                <li>If you add a <strong>new file</strong> (e.g., <code>node_b.py</code>), you must always rebuild.</li>
            </ul>
        </li>
        <li><strong>No messages on a topic</strong>
            <ul>
                <li>Double-check topic names&mdash;they must match exactly.</li>
                <li>Use <code>ros2 topic list</code> to confirm active topics.</li>
                <li>Use <code>ros2 topic echo &lt;topic&gt;</code> to see if anything is publishing.</li>
            </ul>
        </li>
        <li><strong><code>ImportError</code> when running a node (e.g., &ldquo;No module named lab04_pub_sub&rdquo;)</strong>
            <ul>
                <li>You probably ran <code>ros2 run</code> without sourcing the workspace (<code>source install/setup.bash</code>).</li>
                <li>Or, you created the <code>.py</code> file but didn&rsquo;t rebuild (<code>colcon build</code>).</li>
            </ul>
        </li>
        <li><strong>Changes to <code>setup.py</code> not taking effect</strong>
            <ul>
                <li>Any time you change <code>setup.py</code>, <code>package.xml</code>, or add a <strong>new node file</strong>, you must rebuild with <code>colcon build</code>.</li>
                <li>After rebuilding, open a new terminal (or re-<code>source</code>) before running again.</li>
            </ul>
        </li>
        <li><strong>Accidentally committing giant build files to GitHub</strong>
            <ul>
                <li>Only commit files inside <code>src/</code> and <code>docs/</code> (and your README).</li>
                <li>If you already committed <code>build/</code> or <code>install/</code>, run:
                    <pre><code class="language-bash">git rm -r --cached build/ install/ log/
git commit -m "Remove build artifacts"
git push</code></pre>
                </li>
            </ul>
        </li>
        <li><strong><code>ros2 topic echo</code> shows nothing</strong>
            <ul>
                <li>Make sure the publisher node is running.</li>
                <li>Check the topic spelling (case matters).</li>
                <li>Use <code>ros2 node list</code> and <code>ros2 topic list</code> to confirm active nodes/topics.</li>
            </ul>
        </li>
        <li><strong>Node runs but prints nothing</strong>
            <ul>
                <li>Check your logger calls (<code>self.get_logger().info</code>) are actually inside the method.</li>
                <li>If your subscriber callback has the wrong signature (e.g., missing the <code>msg</code> argument), it will silently fail.</li>
            </ul>
        </li>
        <li><strong>Multiple nodes with same name</strong>
            <ul>
                <li>Each node must have a unique name (the string you pass to <code>super().__init__()</code>). If two nodes share a name, only one will appear in the graph.</li>
            </ul>
        </li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
