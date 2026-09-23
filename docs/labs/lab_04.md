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
                <li><a href="#part1">Part 1: Readiness Check</a></li>
                <li><a href="#part2">Part 2: Container Launch</a></li>
                <li><a href="#part3">Part 3: Node A (Publisher)</a></li>
                <li><a href="#part4">Part 4: Node B (Relay)</a></li>
                <li><a href="#part5">Part 5: Node C (Subscriber)</a></li>
                <li><a href="#part6">Part 6: Visualize the Graph with <code>rqt_graph</code></a></li>
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
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab04/d01-pubsub-pipeline.svg" alt="Node A publishes to topic A-to-B, Node B subscribes and republishes to topic B-to-C, and Node C plus a topic-echo terminal receive the result" width="880" height="300" style="max-width: 100%; height: auto;" /></p>
    <p>The pipeline follows a common pattern in robotics: sensors produce data, processing nodes interpret it, and actuators respond.</p>
    <h3>1.2 Background</h3>
    <p><strong>From Scripts to Python</strong></p>
    <ul>
        <li>In Lab 3, you used shell scripts to send commands like <code>ros2 topic pub</code> and <code>ros2 service call</code>. Here, you will use <code>rclpy</code> to create publishers, subscribers, and callbacks within a Python program.</li>
        <li>Python and C++ are commonly used to write ROS 2 nodes. In Python, a subscriber callback lets your node process a message when it arrives.</li>
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
        <li>Use <code>colcon build</code> to build the package you create in this lab.</li>
    </ul>
    <p><strong>Examples in Robotics:</strong></p>
    <ul>
        <li><strong>Node</strong> &ndash; The <strong>camera driver node</strong> that captures images from the robot&rsquo;s camera sensor.</li>
        <li><strong>Package</strong> &ndash; The <strong>camera package</strong> that includes the driver node, a calibration tool, and a node that publishes the images in different formats (all the software you need for the camera).</li>
        <li><strong>Workspace</strong> &ndash; The <strong>robot&rsquo;s software workspace</strong> that holds the camera package along with other packages like motor control, navigation, or perception (everything the robot needs to run).</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Create</strong> and build a ROS 2 workspace and a custom Python package.</li>
        <li><strong>Implement</strong> a publisher node in Python that publishes on a timer.</li>
        <li><strong>Implement</strong> a relay node that subscribes to a topic, modifies the data, and republishes it.</li>
        <li><strong>Implement</strong> a subscriber node in Python that receives and logs messages.</li>
        <li><strong>Use</strong> <code>colcon build</code> to build your workspace and <code>ros2 run</code> to execute your nodes.</li>
        <li><strong>Organize</strong> your work in a Classroom 50 repository, commit your package with Git, and push it.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Accept and clone the assignment, pull the course image, and create and build the empty package before arriving at lab. During lab, you will check this setup, launch the container, and write the nodes.</p>
    </div>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Important:</strong> VMs power off automatically 4 hours after the reservation starts. That stops the container and discards anything you wrote inside it outside <code>~/workspaces</code>; files on the VM itself stay where they are. Keep your work in that folder, and commit and push whenever you finish a part.</div>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Where to do what</strong>
        <ul>
            <li><strong>Edit code on your VM (host)</strong> in <strong>VS Code</strong>. Do <strong>not</strong> run VS Code inside Docker; it isn&rsquo;t installed there.</li>
            <li><strong>Run all ROS 2 commands inside the Docker container</strong> (build, source, run).</li>
            <li><strong>Run all git commands (clone, commit, push) on the VM host</strong>; the container has no GitHub credentials. The container sees your repo through the <code>~/workspaces</code> mount.</li>
            <li>Path mapping: <strong>VM</strong> <code>~/workspaces</code> &harr; <strong>container</strong> <code>/root/workspaces</code> (the container runs as root, so <code>~/workspaces</code> inside the container resolves to the same place).</li>
        </ul>
    </blockquote>
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
        <li><strong>Accept Lab 4.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-04</code></pre>
            <p>Classroom 50 accepts a pending organization invitation, creates your private repository, and prints the exact <code>git clone</code> command. If you already accepted the assignment, it leaves your repository unchanged.</p>
        </li>
        <li><strong>Clone the repository.</strong> Run the clone command printed by Classroom 50. The expected repository name is:</li>
    </ol>
    <pre><code>MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME</code></pre>
    <p><strong>Location:</strong> Host VM Terminal. Always clone and push on the VM, never inside the container.</p>
    <pre><code class="language-bash">cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME.git
cd intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME</code></pre>
    <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your GitHub username, and use the URL printed by Classroom 50 if it differs from the example.</p>
    <ol start="6">
        <li><strong>Create the workspace skeleton.</strong> The starter ships <code>README.md</code>, <code>.gitignore</code>, <code>docs/</code>, <code>node_scaffolds/</code>, <code>pytest.ini</code>, and <code>test_lab_4.py</code>. Add the ROS 2 workspace:
            <p><strong>Location:</strong> Host VM Terminal, from inside your cloned repository</p>
            <pre><code class="language-bash">mkdir -p ros2_ws/src</code></pre>
            <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> <code>src/</code> is where your packages live. The <strong>workspace root</strong> is <code>ros2_ws</code>. Do not build from <code>src/</code>; always build from the workspace root. The starter&rsquo;s <code>.gitignore</code> keeps the generated <code>build/</code>, <code>install/</code>, and <code>log/</code> directories out of Git.</blockquote>
            <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab04/d03-workspace-anatomy.svg" alt="ROS 2 workspace showing source packages under src and the generated build, install, and log directories" width="880" height="400" style="max-width: 100%; height: auto;" /></p>
        </li>
        <li><strong>Start the course container.</strong> This is the standard course <code>docker run</code> command with the container name changed to <code>lab04</code>:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it \
  --name lab04 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
            <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Warning:</strong> The <code>--rm</code> option deletes the container when you exit the original shell and closes terminals attached with <code>docker exec</code>. Files in the mounted <code>~/workspaces</code> folder remain on the VM.</blockquote>
        </li>
        <li><strong>Create the Python package.</strong>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME/ros2_ws/src
ros2 pkg create --build-type ament_python lab04_pub_sub --dependencies rclpy std_msgs</code></pre>
            <p><strong>Understanding the command:</strong></p>
            <ul>
                <li><code><strong>ros2 pkg create</strong></code> &ndash; The ROS 2 CLI tool to generate a new package with the right folder structure and metadata files.</li>
                <li><code><strong>--build-type ament_python</strong></code> &ndash; ROS 2 packages can be built with different systems depending on whether they&rsquo;re C++ or Python. Here you&rsquo;re saying <em>&ldquo;this will be a Python package.&rdquo;</em></li>
                <li><code><strong>lab04_pub_sub</strong></code> &ndash; This is the name of your package. ROS 2 will create a folder with this name and set up the required files inside it.</li>
                <li><code><strong>--dependencies rclpy std_msgs</strong></code> &ndash; Declares dependencies on the <strong>ROS 2 Python API</strong> (<code>rclpy</code>) and common message types (<code>std_msgs</code>) in <code>package.xml</code>.</li>
            </ul>
        </li>
        <li><strong>Fix file ownership (mandatory).</strong> The container runs as <strong>root</strong>, so every file <code>ros2 pkg create</code> just made is owned by root on your VM. If you skip this step, VS Code will not be able to save changes to those files. Do this <strong>every time</strong> you create files from inside the container.
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">sudo chown -R $USER:$USER ~/workspaces/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME</code></pre>
        </li>
        <li><strong>Build the (currently empty) package.</strong>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME/ros2_ws
colcon build --symlink-install</code></pre>
            <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>About <code>--symlink-install</code>:</strong><br />For Python, this creates symlinks so you can edit <code>.py</code> files and run your nodes again without rebuilding, as long as you don&rsquo;t add new files or change package metadata. If you add a new Python file or entry point, you need to rebuild.</blockquote>
            <p><strong>Expected output (excerpt):</strong></p>
            <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>Starting &gt;&gt;&gt; lab04_pub_sub
Finished &lt;&lt;&lt; lab04_pub_sub
Summary: 1 package finished</code></pre>
            </div>
        </li>
        <li><strong>Source the workspace and verify ROS 2 can see your package.</strong>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">source install/setup.bash
ros2 pkg list | grep lab04_pub_sub</code></pre>
            <p><strong>Checkpoint:</strong> You should see <code>lab04_pub_sub</code> printed. It is normal that <code>ros2 pkg executables lab04_pub_sub</code> shows nothing yet; there are no nodes.</p>
            <p>If <code>ros2 pkg list</code> does not show your package, check that you built from the <strong>workspace root</strong> (<code>ros2_ws</code>, not <code>src/</code>), that the build finished without errors, and that you ran <code>source install/setup.bash</code> in the <strong>same terminal</strong>.</p>
        </li>
        <li><strong>Commit and push the scaffolding.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">git add ros2_ws
git commit -m "Add empty lab04_pub_sub package"
git push origin main</code></pre>
        </li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code> succeeds.</li>
        <li>[ ] <code>git status</code> reports a clean working tree on <code>main</code>.</li>
        <li>[ ] <code>git remote -v</code> points to your Lab 4 repository.</li>
        <li>[ ] <code>ls -la</code> shows <code>README.md</code>, <code>.gitignore</code>, <code>docs/</code>, <code>node_scaffolds/</code>, <code>pytest.ini</code>, <code>ros2_ws/</code>, and <code>test_lab_4.py</code>.</li>
        <li>[ ] <code>ls ros2_ws/src/lab04_pub_sub</code> shows <code>package.xml</code>, <code>setup.py</code>, and the inner <code>lab04_pub_sub/</code> folder.</li>
        <li>[ ] <code>git status</code> shows no <code>build/</code>, <code>install/</code>, or <code>log/</code> directories waiting to be committed.</li>
        <li>[ ] You reviewed the ROS 2 tutorial <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html" target="_blank" rel="noopener">&ldquo;Writing a simple publisher and subscriber (Python)&rdquo;</a>, which is the direct foundation for this lab.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <h3 id="workflow">The Core ROS 2 Development Workflow</h3>
    <p>After adding a node or changing package metadata, edit, build, and source as follows. With <code>--symlink-install</code>, edits to existing Python files only require restarting the node.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab04/d02-build-source-run-loop.svg" alt="Edit, build, source, and run workflow with the failures caused by missing a required rebuild or failing to source a terminal" width="900" height="400" style="max-width: 100%; height: auto;" /></p>
    <ol>
        <li><strong>Edit code</strong> on your VM in VS Code. Modify your Python files (e.g., <code>node_a.py</code>) in your package&rsquo;s source folder.</li>
        <li><strong>Build the workspace</strong> in the container, from the workspace root (not <code>src/</code>):
            <pre><code class="language-bash">colcon build --symlink-install</code></pre>
            <p>This discovers packages, registers Python entry points, and updates executables.</p>
        </li>
        <li><strong>Source the workspace</strong> in every new terminal:
            <pre><code class="language-bash">source ~/workspaces/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME/ros2_ws/install/setup.bash</code></pre>
            <p>This tells the shell where to find your newly built nodes.</p>
        </li>
    </ol>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Sourcing the workspace</strong><br />The course image sources <code>/opt/ros/jazzy/setup.bash</code> from <code>~/.bashrc</code>, making the ROS 2 commands available in container shells. On another installation, you may need to source that file yourself.<br />Source your workspace separately in every new container terminal, including each <code>docker exec</code> shell. Run <code>source install/setup.bash</code> from the workspace root before <code>ros2 run</code>; this also sources the ROS 2 underlay.</blockquote>
    <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Build and source checks:</strong>
        <ul>
            <li>If you add a Python file or entry point without rebuilding, <code>ros2 run</code> may not find the new executable.</li>
            <li>If you <strong>forget to source</strong> in a <em>new</em> terminal (e.g., after <code>docker exec</code>), you&rsquo;ll see &ldquo;package not found.&rdquo;</li>
        </ul>
    </blockquote>
    <section id="part1">
        <h3>Part 1: Readiness Check</h3>
        <p><strong>Goal:</strong> Confirm that the assignment repository and the package you created in the pre-lab are ready before starting ROS 2 processes.</p>
        <p><strong>Location:</strong> Host VM Terminal, from the Lab 4 repository.</p>
        <pre><code class="language-bash">git status
git remote -v
ls ros2_ws/src/lab04_pub_sub
docker image inspect ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest &gt; /dev/null</code></pre>
        <p><strong>Checkpoint:</strong> The working tree is clean on <code>main</code>, the remote is your private Lab 4 repository, the package listing shows <code>package.xml</code> and <code>setup.py</code>, and the image-inspection command exits without an error. Stop here and finish the pre-lab if any check fails.</p>
    </section>
    <section id="part2">
        <h3>Part 2: Container Launch</h3>
        <p><strong>Goal:</strong> Start a named course container with your workspace mounted, open a second shell into it, and open the repository in VS Code.</p>
        <h4>Step 2.1: Start the named container</h4>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">xhost +local:docker
docker run --rm -it \
  --name lab04 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Keep this shell open:</strong> With <code>--rm</code>, exiting the original shell deletes the container and ends its attached <code>docker exec</code> sessions.</div>
        <h4>Step 2.2: Open additional terminals</h4>
        <p>This lab needs up to four container shells at once. Open each one with:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">docker exec -it lab04 bash</code></pre>
        <p>Each <code>docker exec</code> starts a <strong>new shell process</strong> inside the running container, with its own environment, so every one of them needs your workspace sourced:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME/ros2_ws
source install/setup.bash</code></pre>
        <p>Later parts of this lab call these two lines <strong>preparing a terminal</strong>. Run them once in each shell you open.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Alternative: Terminator</strong><br />You can also open Terminator inside the container and split it into panes:
            <pre><code class="language-bash">terminator</code></pre>
        </blockquote>
        <h4>Step 2.3: Open the repo in VS Code</h4>
        <p><strong>Location:</strong> Host VM Terminal (<strong>not inside the Docker container</strong>)</p>
        <pre><code class="language-bash">code ~/workspaces/intro-to-robotics-fall-2026-lab-04-YOUR_GITHUB_USERNAME</code></pre>
        <ul>
            <li>Edit files normally in VS Code. Because the repo is bind-mounted into the container at <code>~/workspaces</code>, your changes appear instantly inside the container.</li>
            <li>Use the container terminals from Step 2.2 to build, source, and run.</li>
        </ul>
    </section>
    <section id="part3">
        <h3>Part 3: Node A (Publisher)</h3>
        <p><strong>Goal:</strong> Create a Python node that publishes a string message every 2 seconds.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Editing vs. running:</strong> Create and edit files on the VM in VS Code; build, source, and run inside the Docker container.</blockquote>
        <h4>Step 3.1: Copy the scaffold into your package</h4>
        <p>Your package builds, but it contains no code yet. Every ROS 2 node you write in Python lives in a <code>.py</code> file inside your package&rsquo;s source directory.</p>
        <p>The starter repository ships a scaffold for each node in <code>node_scaffolds/</code>. Each scaffold has the class, the callback, and the log lines already in place, and <code>TODO</code> comments marking the parts you write. Copy the Node A scaffold into your package:</p>
        <p><strong>Location:</strong> Host VM Terminal, from your repository root</p>
        <pre><code class="language-bash">cp node_scaffolds/node_a.py ros2_ws/src/lab04_pub_sub/lab04_pub_sub/</code></pre>
        <p>Leave <code>node_scaffolds/</code> as it shipped, so you keep a clean copy to fall back on. The graded file is the one inside the package.</p>
        <h4>Step 3.2: Fill in the TODOs</h4>
        <p><strong>Location:</strong> File Editor (VS Code on the VM), editing <code>ros2_ws/src/lab04_pub_sub/lab04_pub_sub/node_a.py</code></p>
        <p>Node A has to do three things, and the scaffold leaves each one to you:</p>
        <ul>
            <li>Create a <strong>publisher</strong> for <code>String</code> messages on <code>/topic_a_to_b</code> with a queue size of 10. The method is <code>self.create_publisher(...)</code>.</li>
            <li>Create a <strong>timer</strong> that calls <code>self.timer_callback</code> every 2.0 seconds. The method is <code>self.create_timer(...)</code>.</li>
            <li>Publish the message inside the callback, and write the <code>main()</code> function that initializes <code>rclpy</code>, spins the node, and shuts it down.</li>
        </ul>
        <p>The <a href="https://mems-intro-to-robotics.github.io/guides/ros2_python_nodes_reference/" target="_blank" rel="noopener">ROS 2 Python Nodes Reference</a> gives the signature and a worked example for each of these, including the <code>main()</code> pattern. The <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html" target="_blank" rel="noopener">ROS 2 publisher and subscriber tutorial</a> you read in the pre-lab covers the same ground.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Tip:</strong> If VS Code refuses to save with a permissions error, re-run the <code>chown</code> command from pre-lab step 9 on your VM host.</blockquote>
        <h4>Step 3.3: Add the entry point to <code>setup.py</code></h4>
        <p>Add a console-script entry point in <code>setup.py</code> so <code>ros2 run</code> can launch the <code>main()</code> function in <code>node_a.py</code>.</p>
        <p><strong>Location:</strong> File Editor (VS Code on the VM)</p>
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
        <h4>Step 3.4: Build and source</h4>
        <p>Build to register the new entry point, then source the workspace so your shell can find it. Follow <a href="#workflow">The Core ROS 2 Development Workflow</a>:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">colcon build --symlink-install
source install/setup.bash</code></pre>
        <p>Both commands run from the workspace root, <code>ros2_ws</code>, not from <code>src/</code>.</p>
        <h4>Step 3.5: Run Node A</h4>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">ros2 run lab04_pub_sub node_a</code></pre>
        <p><strong>Checkpoint:</strong> Your logger prints &ldquo;Node A has started. Publishing...&rdquo; followed by &ldquo;Publishing: "Hello from Node A!"&rdquo; every 2 seconds.</p>
        <h4>Step 3.6: Verify the topic</h4>
        <p>Use <code>ros2 topic echo</code> to verify that Node A publishes messages on its topic.</p>
        <p>Open and prepare a second container terminal (Step 2.2), then listen to the topic directly:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">ros2 topic echo /topic_a_to_b</code></pre>
        <p><strong>Checkpoint:</strong></p>
        <ul>
            <li>First terminal: your node&rsquo;s logger messages.</li>
            <li>Second terminal: plain topic messages:
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>data: Hello from Node A!
---</code></pre>
                </div>
                every 2 seconds.
            </li>
        </ul>
    </section>
    <section id="part4">
        <h3>Part 4: Node B (Relay)</h3>
        <p><strong>Goal:</strong> Create a node that <strong>subscribes</strong> to Node A&rsquo;s topic, <strong>modifies</strong> the message, and <strong>republishes</strong> it to a new topic.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Editing vs. running:</strong> Create and edit files on the VM in VS Code; build, source, and run inside the Docker container.</blockquote>
        <p>Node B relays messages between two topics:</p>
        <ul>
            <li><strong>Subscribe</strong> to Node A&rsquo;s topic (<code>/topic_a_to_b</code>)</li>
            <li><strong>Modify</strong> the message it receives (for example, by appending extra text)</li>
            <li><strong>Republish</strong> the new message on a different topic (<code>/topic_b_to_c</code>)</li>
        </ul>
        <h4>Step 4.1: Copy the scaffold into your package</h4>
        <p><strong>Location:</strong> Host VM Terminal, from your repository root</p>
        <pre><code class="language-bash">cp node_scaffolds/node_b.py ros2_ws/src/lab04_pub_sub/lab04_pub_sub/</code></pre>
        <h4>Step 4.2: Fill in the TODOs</h4>
        <p><strong>Location:</strong> File Editor (VS Code on the VM), editing <code>ros2_ws/src/lab04_pub_sub/lab04_pub_sub/node_b.py</code></p>
        <p>Complete these parts of the Node B scaffold:</p>
        <ul>
            <li>A <strong>subscriber</strong> to <code>/topic_a_to_b</code> for <code>String</code> messages, with <code>self._on_msg</code> as the callback and a queue size of 10.</li>
            <li>A <strong>publisher</strong> to <code>/topic_b_to_c</code>, also <code>String</code>, queue size 10.</li>
            <li>The body of <code>_on_msg</code>: build the outgoing message from the one that arrived, publish it, and write the <code>main()</code> boilerplate as you did for Node A.</li>
        </ul>
        <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Required:</strong> Include <strong>your NetID</strong> in the relayed message and make sure it is legible in your screenshot. For example: <code>Hello from Node A! -- processed by Node B (abc123)</code>. The scaffold reads the NetID from a <code>NETID</code> environment variable with a placeholder fallback; either replace the placeholder or export the variable in your container.</div>
        <p>ROS 2 calls this subscriber callback with the incoming message each time one arrives. The <a href="https://mems-intro-to-robotics.github.io/guides/ros2_python_nodes_reference/" target="_blank" rel="noopener">ROS 2 Python Nodes Reference</a> has the subscriber and publisher signatures.</p>
        <h4>Step 4.3: Add the entry point to <code>setup.py</code></h4>
        <p><strong>Location:</strong> File Editor (VS Code on the VM)</p>
        <p>Open:</p>
        <pre><code>ros2_ws/src/lab04_pub_sub/setup.py</code></pre>
        <p>Add a second line to the <code>console_scripts</code> list, following the same <code>executable = package.module:main</code> pattern you used for Node A:</p>
        <pre><code class="language-python">'node_b = lab04_pub_sub.node_b:main',</code></pre>
        <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Common pitfall:</strong> It&rsquo;s <code>lab04_pub_sub.node_b:main</code> (no <code>.py</code>).</div>
        <h4>Step 4.4: Build and source</h4>
        <p>You added a file and an entry point, so a rebuild is required even with <code>--symlink-install</code>. From the workspace root:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">colcon build --symlink-install
source install/setup.bash</code></pre>
        <h4>Step 4.5: Run the nodes (three terminals)</h4>
        <p>Open and prepare three container terminals (Step 2.2), then run one command in each:</p>
        <ul>
            <li><strong>Terminal 1:</strong> <code>ros2 run lab04_pub_sub node_a</code></li>
            <li><strong>Terminal 2:</strong> <code>ros2 run lab04_pub_sub node_b</code></li>
            <li><strong>Terminal 3:</strong> <code>ros2 topic echo /topic_b_to_c</code></li>
        </ul>
        <p><strong>Checkpoint:</strong></p>
        <ul>
            <li><strong>Terminal 1</strong>: Node A logs its published messages.</li>
            <li><strong>Terminal 2</strong>: Node B logs &ldquo;Heard from A: ...&rdquo; and &ldquo;Relaying to C: ...&rdquo;.</li>
            <li><strong>Terminal 3</strong>: You should see the <strong>modified</strong> message content, e.g.:
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>data: Hello from Node A! -- processed by Node B (abc123)
---</code></pre>
                </div>
            </li>
        </ul>
    </section>
    <section id="part5">
        <h3>Part 5: Node C (Subscriber)</h3>
        <p><strong>Goal:</strong> Create a final node that <strong>subscribes</strong> to Node B&rsquo;s output (<code>/topic_b_to_c</code>) and <strong>logs</strong> the result.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Editing vs. running:</strong> Create and edit files on the VM in VS Code; build, source, and run inside the Docker container.</blockquote>
        <h4>Step 5.1: Copy the scaffold into your package</h4>
        <p><strong>Location:</strong> Host VM Terminal, from your repository root</p>
        <pre><code class="language-bash">cp node_scaffolds/node_c.py ros2_ws/src/lab04_pub_sub/lab04_pub_sub/</code></pre>
        <h4>Step 5.2: Fill in the TODOs</h4>
        <p><strong>Location:</strong> File Editor (VS Code on the VM), editing <code>ros2_ws/src/lab04_pub_sub/lab04_pub_sub/node_c.py</code></p>
        <p>Node C needs a <strong>subscriber</strong> to <code>/topic_b_to_c</code> and the same <code>main()</code> boilerplate as the others; the callback that logs the message is already written for you. The subscriber is the one you wrote in Node B with a different topic name.</p>
        <h4>Step 5.3: Add the entry point to <code>setup.py</code></h4>
        <p><strong>Location:</strong> File Editor (VS Code on the VM)</p>
        <p>Add a third line to the <code>console_scripts</code> list:</p>
        <pre><code class="language-python">'node_c = lab04_pub_sub.node_c:main',</code></pre>
        <p>All three executables should now be listed. Confirm with <code>ros2 pkg executables lab04_pub_sub</code> after the next build.</p>
        <h4>Step 5.4: Build and source</h4>
        <p><strong>Location:</strong> Container Terminal, from the workspace root</p>
        <pre><code class="language-bash">colcon build --symlink-install
source install/setup.bash</code></pre>
        <p><strong>Screenshot:</strong> Capture the terminal showing this successful <code>colcon build</code> output and save it as <code>docs/colcon_build.png</code> in your Lab 4 repository.</p>
        <p><em>Example (yours shows your own GitHub username and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab04/s01-colcon-build.png" alt="Example terminal after a successful colcon build" width="650" height="230" style="max-width: 100%; height: auto;" /></p>
        <h4>Step 5.5: Run the full pipeline (four terminals)</h4>
        <p>Open and prepare <strong>four</strong> container terminals (Step 2.2): one for each node, plus a fourth that echoes the final topic. Arrange the windows so all four are visible at once, because you need them in a single screenshot.</p>
        <ul>
            <li><strong>Terminal 1:</strong> <code>ros2 run lab04_pub_sub node_a</code></li>
            <li><strong>Terminal 2:</strong> <code>ros2 run lab04_pub_sub node_b</code></li>
            <li><strong>Terminal 3:</strong> <code>ros2 run lab04_pub_sub node_c</code></li>
            <li><strong>Terminal 4:</strong> <code>ros2 topic echo /topic_b_to_c</code></li>
        </ul>
        <p>Start them in this order. Node C only prints once Node B is relaying, and Node B only relays once Node A is publishing.</p>
        <p><strong>Checkpoint:</strong></p>
        <ul>
            <li>Node A logs what it&rsquo;s publishing.</li>
            <li>Node B logs what it heard from A and what it relays to C.</li>
            <li><strong>Node C logs the final processed message</strong> (the one B modified). Expect something like:
                <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                    <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[INFO] [node_c]: Final message received: "Hello from Node A! -- processed by Node B (abc123)"</code></pre>
                </div>
            </li>
            <li>Terminal 4 shows the raw modified messages arriving on <code>/topic_b_to_c</code>.</li>
        </ul>
        <p><strong>Screenshot:</strong> Arrange all four terminals so they are simultaneously visible (nodes A, B, and C running, plus the <code>ros2 topic echo /topic_b_to_c</code> output) and capture one composite image. Save it as <code>docs/nodes_running.png</code> in your Lab 4 repository.</p>
        <p><em>Example (yours shows your own GitHub username and NetID):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab04/s02-nodes-running.png" alt="Example four-pane terminal with node_a, node_b, node_c, and the topic echo" width="960" height="500" style="max-width: 100%; height: auto;" /></p>
    </section>
    <section id="part6">
        <h3>Part 6: Visualize the Graph with <code>rqt_graph</code></h3>
        <p><strong>Goal:</strong> See the pipeline you built as a node graph, with the three nodes connected by the two topics.</p>
        <p>Leave all three nodes running from Part 5.</p>
        <h4>Step 6.1: Launch <code>rqt_graph</code></h4>
        <p><strong>Location:</strong> Host VM Terminal (first line), then Container Terminal</p>
        <pre><code class="language-bash">docker exec -it lab04 bash
rqt_graph</code></pre>
        <p>The graph opens in <em>Nodes only</em> view and may be empty. Select <em>Nodes/Topics (active)</em> from the drop-down at the top left, then click the refresh button beside it.</p>
        <p><strong>Checkpoint:</strong> You should see nodes <strong>A</strong>, <strong>B</strong>, and <strong>C</strong> connected by the topics:</p>
        <pre><code>/topic_a_to_b
/topic_b_to_c</code></pre>
        <p><strong>Screenshot:</strong> Capture the graph and save it as <code>docs/rqt_graph.png</code> in your Lab 4 repository.</p>
        <p><em>Example (your graph should have the same shape):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab04/s03-rqt-graph.png" alt="Example rqt_graph showing node_a, node_b, and node_c connected by two topics" width="585" height="225" style="max-width: 100%; height: auto;" /></p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p>Write your answers to all four questions in your Gradescope PDF (see &sect;7.2).</p>
    <p>Keep your responses concise and support them with specific observations from running your pipeline.</p>
    <h3>Question 1: Node relationships</h3>
    <ul>
        <li>Looking at the <code>rqt_graph</code> output, describe how the three nodes are connected.</li>
        <li>How does this reflect the flow of data in a real robotic system?</li>
    </ul>
    <h3>Question 2: Subscriber callbacks</h3>
    <ul>
        <li>In Node B, what role does the subscriber callback (<code>_on_msg</code>) play in processing messages?</li>
        <li>Why is this event-driven design important in robotics?</li>
    </ul>
    <h3>Question 3: Build and source cycle</h3>
    <ul>
        <li>Why does ROS 2 require both <code>colcon build</code> and <code>source install/setup.bash</code>?</li>
        <li>What common mistakes occur if you skip one of these steps?</li>
    </ul>
    <h3>Question 4: Extending the pipeline</h3>
    <ul>
        <li>Imagine you wanted to add a <strong>Node D</strong> that filters out certain messages (for example, only passing along messages containing a keyword).</li>
        <li>Where would it connect in the pipeline, and how would it change the overall system?</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Setup, Docker, ROS 2, and Git problems that recur across labs are collected on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#ros-2-basics" target="_blank" rel="noopener">Troubleshooting</a>. For this lab it covers code changes that do not take effect without a rebuild, <code>ImportError</code> from an unsourced workspace, <code>ros2 run</code> reporting that an executable was not found, a topic that echoes nothing, a node that prints nothing, duplicate node names, and files created as root inside the container.</p>
    <p>Check the relevant troubleshooting entry before asking a TA.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html" target="_blank" rel="noopener">ROS 2 Jazzy: Writing a Simple Publisher and Subscriber (Python)</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html" target="_blank" rel="noopener">ROS 2 Jazzy: Creating Your First ROS 2 Package</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/index.html" target="_blank" rel="noopener">ROS 2 Jazzy Documentation</a></li>
        <li><a href="https://colcon.readthedocs.io/en/released/" target="_blank" rel="noopener">colcon Documentation</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Topic-Statistics.html" target="_blank" rel="noopener">ROS 2 Jazzy: Topics and QoS Concepts</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <p>Use these references for the <code>rclpy</code> patterns and commands in Parts 3&ndash;5.</p>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/ros2_python_nodes_reference/" target="_blank" rel="noopener">ROS 2 Python Nodes Reference</a>: the <code>main()</code> pattern, publishers, subscribers, timers, messages, logging, and the package and build mistakes that come up in this lab.</li>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: package creation, build and source reminders, ROS 2 CLI checks, Git commands, and Docker commands.</li>
        <li><a href="https://mems-intro-to-robotics.github.io/troubleshooting/#ros-2-basics" target="_blank" rel="noopener">Troubleshooting</a>: package discovery, workspace sourcing, container GUI, and cross-terminal environment problems.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
