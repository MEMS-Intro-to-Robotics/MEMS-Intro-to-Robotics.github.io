---
title: "Lab 07: Crazyflie PID Tuning"
---

# Lab 07: Crazyflie PID Tuning

<div class="lab-content">

<div class="lab-manual-container">
<h2>Table of Contents</h2>
    <ul>
        <li><a href="#sec-1">1. Introduction &amp; Background</a></li>
        <li><a href="#sec-2">2. Conceptual Overview</a></li>
        <li><a href="#sec-3">3. Pre-Lab Preparation</a></li>
        <li><a href="#sec-5">5. Lab Procedure</a></li>
        <li><a href="#sec-6">6. Analysis and Discussion Questions</a></li>
        <li><a href="#sec-7">7. References and Further Reading</a></li>
        <li><a href="#appendix">Appendix: Beyond the Basics</a></li>
    </ul>
    <h1 id="sec-1">1.1 Overview</h1>
    <p>In this lab you will tune a PID (Proportional&ndash;Integral&ndash;Derivative) controller for a simulated Crazyflie micro-quadrotor to fly a fixed sequence of waypoints. Your job is to shape the controller&rsquo;s response so the drone tracks the commanded path accurately and quickly, without oscillation or excessive overshoot. You&rsquo;ll start from a working baseline, then iteratively adjust gains, fly the course, and analyze performance with the provided plotting script that overlays actual trajectories (x, y, z and top-down x&ndash;y) against the goal path. The entire lab runs in simulation to let you explore aggressive/poor tuning safely while learning how each PID term affects flight behavior and course time.</p>
    <div class="lab-manual-container">
        <h2><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:341px;min-height:150px;margin:1em auto;">Image placeholder</div></h2>
        <h2>1.2 Background</h2>
        <h3>What is a PID Controller?</h3>
        <p>At its core, a PID controller is a widely used feedback control mechanism. Its fundamental purpose is to make a system (like our drone) reach a desired state (a "setpoint") and maintain it by continuously correcting for any differences, or "errors." It works by calculating a corrective action based on three terms:</p>
        <ul>
            <li>The <strong>Proportional (P)</strong> term considers the <strong>present</strong> error. A larger error results in a larger corrective force.</li>
            <li>The <strong>Integral (I)</strong> term considers the <strong>past</strong> error, accumulating it over time to eliminate any small, persistent biases.</li>
            <li>The <strong>Derivative (D)</strong> term considers the <strong>future</strong> error by looking at its rate of change, which helps to dampen oscillations and prevent overshoot.</li>
        </ul>
        <p>By adjusting the "gains" (weights) of these three terms, you can shape the controller's behavior to be fast, smooth, and precise. Because of its simplicity and effectiveness, the PID controller is a workhorse in industrial automation, robotics, and process control.</p>
        <h3>Why PID for Micro-Aerial Vehicles?</h3>
        <p>Multirotors are underactuated, nonlinear systems&mdash;meaning they have fewer independent actuators (motors) than degrees of freedom (e.g., x, y, z, roll, pitch, yaw), making them inherently unstable. However, for small motions around a stable hover, their dynamics can be effectively approximated by linear models. This is why cascaded linear controllers are standard: an outer <strong>position loop</strong> computes velocity/attitude setpoints from position error, and inner <strong>attitude/rate loops</strong> track those setpoints at high bandwidth. In our simulation, you will tune the <strong>outer position PID</strong> (<span class="math-inline" data-latex="x,y,z"></span>). Good tuning yields fast rise to each waypoint, minimal overshoot, and small steady-state error; poor tuning yields sluggish drift (low gains), ringing/oscillation (excess P or D imbalance), or slow bias removal and &ldquo;wind-up&rdquo; (misused I).</p>
        <p><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:342px;min-height:150px;margin:1em auto;">Crazyflie Drone</div></p>
        <h3>PID in One Equation (Continuous and Discrete)</h3>
        <p>Let the setpoint be <span class="math-inline" data-latex="r(t)"></span>, the measured position be <span class="math-inline" data-latex="y(t)"></span>, and the error be <span class="math-inline" data-latex="e(t)=r(t)-y(t)"></span>. The ideal continuous-time PID is:</p>
        <p><span class="math-display" data-latex="u(t)=K_p\,e(t)+K_i\!\int_{0}^{t} e(\tau)\,d\tau+K_d\,\frac{de(t)}{dt}"></span></p>
        <p>In software we implement a discrete-time version with sample period <span class="math-inline" data-latex="T_s"></span> (the control loop&rsquo;s timer):</p>
        <p><span class="math-display" data-latex="u[k]=K_p\,e[k]+K_i\,T_s\!\sum_{i=0}^{k} e[i]+K_d\,\frac{e[k]-e[k-1]}{T_s}"></span></p>
        <p>In this control architecture, the output <span class="math-inline" data-latex="u[k]"></span> for each axis represents the <strong>commanded velocity</strong> sent to the drone's low-level flight controller. Your PID's job is to calculate the appropriate velocity vector needed to drive the position error to zero.</p>
        <h3>Common Refinements in PID Control</h3>
        <p>While the PID controller you will tune is built on the fundamental equations, most industrial or production-grade controllers include important refinements to improve performance and safety. Though not implemented in the baseline code for this lab, two critical concepts to be aware of are:</p>
        <ul>
            <li><strong>Derivative filter</strong> to avoid amplifying sensor noise. The simple derivative term is often replaced with a low-pass filter (sometimes called a "dirty derivative"):
                <p><span class="math-inline" data-latex="d[k]=\alpha\,d[k-1]+(1-\alpha)\,\frac{e[k]-e[k-1]}{T_s}"></span></p>
                Then we use <span class="math-inline" data-latex="d[k]"></span> as the <span class="math-inline" data-latex="K_d"></span> term. This smooths out the derivative calculation, making the controller less sensitive to measurement noise.
            </li>
            <li><strong>Integrator anti-windup</strong> so the I-term stops accumulating when actuators saturate or the system cannot respond. If the error is large for a long time, the integral sum can "wind up" to a huge value, which can cause a large, sustained overshoot. This is often prevented by <em>clamping</em> the integral sum to a reasonable maximum value.</li>
        </ul>
        <p>You will tune three independent SISO PIDs (one each for <span class="math-inline" data-latex="x"></span>, <span class="math-inline" data-latex="y"></span>, and <span class="math-inline" data-latex="z"></span>). Yaw control is disabled for this lab to let you focus on position.</p>
        <h3>What Each Term Does (and what &ldquo;too much&rdquo; looks like)</h3>
        <ul>
            <li><strong>P (Proportional)</strong>: The main &ldquo;stiffness.&rdquo; Higher <span class="math-inline" data-latex="K_p"></span> reduces position error and shortens rise time, but too high invites overshoot and oscillation (ringing around waypoints).</li>
            <li><strong>I (Integral)</strong>: Removes steady-state bias (e.g., small constant drift). Too high <span class="math-inline" data-latex="K_i"></span> causes sluggish waves, long settling times, and windup when the output saturates. Use it sparingly.</li>
            <li><strong>D (Derivative)</strong>: Adds predictive damping&mdash;it reduces overshoot and helps &ldquo;stick the landing&rdquo; at waypoints. Too high <span class="math-inline" data-latex="K_d"></span> can amplify noise and cause twitchy, hesitant movements.<br /><br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:485px;min-height:150px;margin:1em auto;">PID with varying P</div></li>
        </ul>
        <h3>A Simple, Effective Tuning Playbook</h3>
        <ol>
            <li><strong>Start with P-only.</strong> Set <span class="math-inline" data-latex="K_i=0, K_d=0"></span>. Increase <span class="math-inline" data-latex="K_p"></span> until you get a brisk response with mild overshoot or a hint of oscillation; then back off ~10&ndash;20%.</li>
            <li><strong>Add D to damp.</strong> Increase <span class="math-inline" data-latex="K_d"></span> until overshoot and oscillation are controlled and the path &ldquo;snaps&rdquo; cleanly to setpoints.</li>
            <li><strong>Add a little I to kill residual bias.</strong> Only if needed, introduce a small <span class="math-inline" data-latex="K_i"></span> to eliminate any steady-state error (e.g., finishing 2&ndash;3 cm off target).</li>
            <li><strong>Balance speed vs. smoothness.</strong> If the course time is good but the plot shows snaking, reduce <span class="math-inline" data-latex="K_p"></span> slightly or increase <span class="math-inline" data-latex="K_d"></span>. If it&rsquo;s too slow, nudge <span class="math-inline" data-latex="K_p"></span> up.</li>
            <li><strong>Retune Z separately.</strong> Vertical dynamics differ due to gravity. Expect different gains for the z-axis.</li>
        </ol>
        <blockquote><strong>Tip:</strong> Keep a log of your gains and results. Change one knob at a time, re-fly, and inspect the plots before moving on.</blockquote>
    </div>
    <h2><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:453px;min-height:150px;margin:1em auto;">PID Controller Diagram from REALPARS</div></h2>
    <h1 id="sec-2">2. Conceptual Overview: How It All Works</h1>
    <h3>An Intuitive Look at PID</h3>
    <p>Imagine you're trying to hold a drone perfectly still at 1 meter high. A PID controller's logic can be broken down into three core functions:</p>
    <ul>
        <li><strong>P (Proportional): "How far am I from my goal <em>right now</em>?"</strong> This term provides a corrective action proportional to the current error. Functionally, it acts like a <strong>virtual spring</strong>. The larger the position error (the more the spring is "stretched"), the stronger the restoring force pulling the drone back towards the setpoint. It is the primary driver of the system's response.</li>
        <li><strong>I (Integral): "Have I been consistently off-target for a while?"</strong> This term accumulates past errors over time. Its purpose is to eliminate <strong>steady-state error</strong>, which can be caused by unmodeled system biases or persistent disturbances (e.g., a slight aerodynamic drift). By integrating the error, it ensures that even a small, persistent error will eventually generate a significant corrective action.</li>
        <li><strong>D (Derivative): "How fast am I approaching (or leaving) my goal?"</strong> This term's action is proportional to the rate of change of the error. It provides <strong>damping</strong> to the system, acting like a virtual shock absorber or dashpot. By opposing rapid changes in the error, it reduces overshoot and suppresses the oscillations caused by an aggressive P-term, leading to a more stable and settled response.<br /><br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:406px;min-height:150px;margin:1em auto;">Mass Spring Damper System</div></li>
    </ul>
    <h3>Our System Architecture</h3>
    <p>We will run three separate programs (ROS 2 Nodes) that communicate with each other to make the drone fly.</p>
    <pre><code>
(Trajectory Publisher) --&gt; /goal_pose --&gt; (PID Controller) --&gt; /cmd_vel --&gt; (Drone Sim)
        ^                                        |
        |                                        | reads current position
        +----------------------------------------+ (via /tf)
    </code></pre>
    <ol>
        <li><strong>Trajectory Publisher:</strong> Acts as the "mission planner." It reads a list of 3D waypoints and publishes them one by one to a topic called <code>/goal_pose</code>.</li>
        <li><strong>PID Controller:</strong> This is the node you will be tuning! It subscribes to <code>/goal_pose</code> to know where it <em>should</em> be and uses TF to find out where it <em>actually</em> is. It then calculates the error and publishes velocity commands to the drone.</li>
        <li><strong>Plotting Node:</strong> Our analysis tool. It records the drone's position and its goal over time, saving graphs so you can visualize your tuning performance.</li>
    </ol>
</div>
<h1 id="sec-3">3. Pre-Lab Preparation</h1>
<p>You will work entirely in <strong>simulation</strong> inside the provided Docker container. This pre-lab ensures your environment is correctly configured. The main steps are to (1) update your local course repository, (2) pull the latest Docker image, (3) launch the simulator, and (4) verify that all tools and ROS 2 topics are functioning correctly before you begin the lab procedure.</p>
<h2>Step 1: Setup the Host Environment</h2>
<p>These commands should be run in a terminal on your host virtual machine.</p>
<h3>3.1 Update Your Course Repository</h3>
<p>📍 <strong>Location:</strong> Host VM Terminal</p>
<p>Ensure you have the latest lab files by pulling the latest changes from the course repository.</p>
<pre><code class="language-bash">cd ~/workspaces/[netid]_robotics_fall2025
git pull
</code></pre>
<h3>3.2 Pull the Docker Image</h3>
<p>📍 <strong>Location:</strong> Host VM Terminal</p>
<p>Download the specific Docker image for this lab, which contains ROS 2, the Crazyflie simulator, and all necessary Python libraries.</p>
<pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:crazyflie-jazzy-latest
</code></pre>
<h3>3.3 Configure GUI (X11) Forwarding</h3>
<p>📍 <strong>Location:</strong> Host VM Terminal</p>
<p>To view the Gazebo simulator GUI running inside the container, you must grant Docker permission to connect to your host's display server.</p>
<pre><code class="language-bash"># This command allows local clients (like Docker containers) to open windows on your host.
xhost +local:
</code></pre>
<h2>Step 2: Launch and Verify the Container</h2>
<h3>3.4 Start the Lab Container</h3>
<p>📍 <strong>Location:</strong> Host VM Terminal</p>
<p>This command will start a persistent container named <code>lab07</code>. Choose the option that matches your system's hardware configuration. Be sure to replace <code>[netid]</code> with your own NetID.</p>
<h4>Option A: With NVIDIA GPU Acceleration (Recommended)</h4>
<pre><code class="language-bash"># --name lab07:       Assigns a reusable name to the container.
# --gpus all:         Grants the container access to the host's NVIDIA GPUs.
# --network host:     Allows the container to share the host's network (for ROS 2).
# -e DISPLAY=$DISPLAY: Passes the host's display variable for GUI forwarding.
# -v [host]:[guest]:  Mounts your local workspace folder into the container. You can change this to wherever you want your files mounted

docker run -it --name lab07 --gpus all \
  --network host \
  -e DISPLAY=$DISPLAY \<br />  -e GZ_SIM_RESOURCE_PATH=/opt/cf_lab_ws/simulation_ws/crazyflie-simulation \<br />  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces/ \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:crazyflie-jazzy-latest
</code></pre>
<h4>Option B: With CPU-Based Software Rendering</h4>
<pre><code class="language-bash">docker run -it --name lab07 \
  --network host \
  -e DISPLAY=$DISPLAY \<br /> &nbsp;-e GZ_SIM_RESOURCE_PATH=/opt/cf_lab_ws/simulation_ws/crazyflie-simulation \<br /> &nbsp;-v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:crazyflie-jazzy-latest
</code></pre>
<p><strong>To re-enter your container later:</strong> If you exit the container, you can resume your session without losing any data using <code>docker start -ai lab07</code>.</p>
<h3>3.5 Perform Initial Environment Checks</h3>
<p>📍 <strong>Location:</strong> Docker Container Terminal</p>
<p>Once inside the container, your terminal prompt will change. Run these quick checks to confirm the environment is set up.</p>
<pre><code class="language-bash"># Check that the ROS 2 distribution is set correctly
echo "ROS_DISTRO=$ROS_DISTRO"
# Expected output: jazzy

# Verify that key Python libraries are installed
python3 -c "import matplotlib, numpy; print('Matplotlib/Numpy OK')"
</code></pre>
<h2>Step 3: Launch and Verify the Simulation</h2>
<p>For the following steps, you may want to open a second terminal into the same running container (e.g., using <code>tmux</code>, splitting your terminal, or running <code>docker exec -it lab07 bash</code> from your host) so you can leave the simulation running while you run verification commands.</p>
<h3>3.6 Launch the Crazyflie Simulator</h3>
<p>📍 <strong>Location:</strong> Docker Container Terminal</p>
<p>In a container terminal, source the ROS 2 environment and launch the simulation.</p>
<pre><code class="language-bash">source /opt/ros/$ROS_DISTRO/setup.bash
ros2 launch ros_gz_crazyflie_bringup crazyflie_simulation.launch.py
</code></pre>
<p><strong>Expected Outcome:</strong> The Gazebo Harmonic GUI window should appear on your desktop, displaying the Crazyflie in a simple world. If it fails with an OpenGL error, stop the launch (Ctrl-C), run <code>export LIBGL_ALWAYS_SOFTWARE=1</code> in the same terminal, and try the `ros2 launch` command again.</p>
<blockquote>
    <h3>📝 Note on Potential <code>model.sdf</code> Loading Errors</h3>
    <p>You might encounter an error where the simulation fails to load the Crazyflie model, indicating that the <code>model.sdf</code> file cannot be found. This can be caused by the <code>GZ_SIM_RESOURCE_PATH</code> environment variable not being correctly set within the Docker container. This variable tells Gazebo where to look for simulation models and other resources.</p>
    <p>There are a couple of ways to resolve this:</p>
    <ol>
        <li>
            <p><strong>Relaunch the Docker Container</strong></p>
            <p>In some cases, simply stopping and relaunching the Docker container can resolve the issue. This might be due to a timing issue in the container's startup script where the environment variables are not set correctly on the first run.</p>
        </li>
        <li>
            <p><strong>Manually Set the Resource Path</strong></p>
            <p>If relaunching doesn't work, or you don't wish to relaunch, you can manually set the <code>GZ_SIM_RESOURCE_PATH</code> before launching the simulation. You can run the following command in the same terminal where you will run the <code>ros2 launch</code> command:</p>
            <pre><code class="language-bash">export GZ_SIM_RESOURCE_PATH=/opt/cf_lab_ws/simulation_ws/crazyflie-simulation/simulator_files/gazebo</code></pre>
            <p>After running this export command, proceed with launching the simulation as described in section 3.6.</p>
        </li>
    </ol>
</blockquote>
<h2>Pre-Lab Complete</h2>
<p>At this point, you have confirmed that:</p>
<ul>
    <li>Your named container (<code>lab07</code>) is running and accessible.</li>
    <li>The Gazebo simulation launches and displays correctly.</li>
    <li>Core ROS 2 topics (<code>/crazyflie/odom</code>, <code>/cmd_vel</code>) and TF transforms are active.</li>
    <li>Plotting libraries are working correctly.</li>
</ul>
<p>You are now ready to proceed with the main lab procedure.</p>
<h1 id="sec-5">5. Lab Procedure</h1>
<p>In this section, you will create a ROS 2 package from scratch, configure it with the provided Python scripts, build it, and learn the workflow for launching the complete system for tuning.</p>
<h3>Phase 1: Create the ROS 2 Package</h3>
<p>First, we will create the standard directory structure for a ROS 2 Python package. All commands in this section should be run inside your Docker container.</p>
<h4>5.1 Create Directories and Package</h4>
<p>📍 <strong>Location:</strong> Docker Container Terminal</p>
<pre><code class="language-bash"># 1. Create the workspace and source directory structure.
# Replace [netid] with your actual NetID.
mkdir -p ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/src
cd ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/src

# 2. Create a ROS 2 Python package.
# The 'ament_python' build type is standard for Python-based nodes.
ros2 pkg create --build-type ament_python lab07_crazyflie

# 3. Create the 'scripts' folder where your nodes will live.
mkdir -p lab07_crazyflie/lab07_crazyflie/scripts
</code></pre>
<h4>5.2 Download the Provided Scripts</h4>
<p>📍 <strong>Location:</strong> Docker Container Terminal (from within `ros2_ws/src`)</p>
<p>Use <code>curl</code> to download the three node scripts directly into the `scripts` directory you just created.</p>
<pre><code class="language-bash"># Define the destination directory for convenience
SCRIPTS_DIR="lab07_crazyflie/lab07_crazyflie/scripts"

# Download the PID controller node
curl -L -o "$SCRIPTS_DIR/3d_goal_control.py" \
  "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/lab07_files/3d_goal_control.py"

# Download the arrival-based trajectory publisher
curl -L -o "$SCRIPTS_DIR/trajectory_publisher.py" \
  "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/lab07_files/trajectory_publisher.py"

# Download the plotting utility
curl -L -o "$SCRIPTS_DIR/plotting.py" \
  "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/lab07_files/plotting.py"

# IMPORTANT: Make all downloaded scripts executable
chmod +x $SCRIPTS_DIR/*.py
</code></pre>
<blockquote>
    <p><strong>Node Descriptions:</strong></p>
    <ul>
        <li><code>3d_goal_control.py</code>: The core PID controller. It subscribes to <code>/goal_pose</code>, calculates error, and publishes velocity commands to <code>/crazyflie/cmd_vel</code>.</li>
        <li><code>trajectory_publisher.py</code>: An intelligent waypoint sequencer. It publishes a goal and waits until the drone's position is within a specified tolerance (<code>arrival_tol_m</code>) for a certain number of messages (<code>arrival_hits</code>) before publishing the next waypoint.</li>
        <li><code>plotting.py</code>: A utility node that logs the drone's position and goal, and generates the final plots for your report.</li>
    </ul>
</blockquote>
<h3>Phase 2: Configure the Package</h3>
<p>Next, you must edit two configuration files to declare your package's dependencies and expose your scripts as runnable commands.</p>
<h4>5.3 Configure <code>package.xml</code> (Dependencies)</h4>
<p>📍 <strong>Location:</strong> File Editor</p>
<p>Open <code>~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/src/lab07_crazyflie/package.xml</code>. This file declares the ROS 2 packages your nodes depend on. Add the following lines inside the <code>&lt;package&gt;</code> tag:</p>
<pre><code>&lt;depend&gt;rclpy&lt;/depend&gt;
&lt;depend&gt;geometry_msgs&lt;/depend&gt;
&lt;depend&gt;nav_msgs&lt;/depend&gt;
&lt;depend&gt;tf2_ros&lt;/depend&gt;
</code></pre>
<h4>5.4 Configure <code>setup.py</code> (Entry Points)</h4>
<p>📍 <strong>Location:</strong> File Editor</p>
<p>Open <code>~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/src/lab07_crazyflie/setup.py</code>. The <code>entry_points</code> section creates runnable console commands for your Python scripts. This allows you to run your node with a simple command like <code>ros2 run lab07_crazyflie goal_3d_controller</code>. Modify the <code>entry_points</code> dictionary to match this exactly:</p>
<pre><code>entry_points={
    'console_scripts': [
        'goal_3d_controller = lab07_crazyflie.scripts.3d_goal_control:main',
        'trajectory_publisher = lab07_crazyflie.scripts.trajectory_publisher:main',
        'plotting = lab07_crazyflie.scripts.plotting:main',
    ],
},
</code></pre>
<h3>Phase 3: Build and Launch</h3>
<p>With the package created and configured, you can now build the workspace and launch the full system.</p>
<h4>5.5 Build and Source the Workspace</h4>
<p>📍 <strong>Location:</strong> Docker Container Terminal</p>
<pre><code># Navigate to the root of your workspace
cd ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws

# Build the workspace using colcon
# --symlink-install allows you to edit Python scripts and have the
# changes take effect without needing to rebuild. This is very useful.
colcon build --symlink-install

# Source the local setup file to add your new package to the environment
source install/setup.bash
</code></pre>
<blockquote>
    <p><strong>Crucial Step:</strong> Any time you open a new terminal to work in your workspace, you <strong>must</strong> source the local setup file again: <code>source ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/install/setup.bash</code></p>
</blockquote>
<h4>5.6 Launch the System (Multi-Terminal Workflow)</h4>
<p>For this lab, you will need to run three commands concurrently in separate terminals (or in terminal panes using a tool like <code>tmux</code>). The image below illustrates this setup.</p>
<p><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:553px;min-height:150px;margin:1em auto;">Crazyflie Drone in Gazebo Sim</div></p>
<p>Launch the nodes in the following order.</p>
<h5>Pane 1 &mdash; Start the Simulation</h5>
<pre><code class="language-bash"># Source the base ROS 2 environment
source /opt/ros/$ROS_DISTRO/setup.bash

# Launch the Gazebo simulation for the Crazyflie
ros2 launch ros_gz_crazyflie_bringup crazyflie_simulation.launch.py
</code></pre>
<h5>Pane 2 &mdash; Start the PID Controller</h5>
<p>In your second terminal, source your workspace and run the PID controller node. We will start with safe, baseline gains and tune them live.</p>
<pre><code class="language-bash"># Source your local workspace to find your package
source ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/install/setup.bash

# Run the controller with initial gains.
# -p kp_*, kd_*, ki_*: These are your PID gains per axis.
# -p max_v_*: These parameters cap the maximum commanded velocity.
ros2 run lab07_crazyflie goal_3d_controller --ros-args \
  -p kp_x:=0.6 -p kd_x:=0.12 -p ki_x:=0.0 \
  -p kp_y:=0.6 -p kd_y:=0.12 -p ki_y:=0.0 \
  -p kp_z:=1.2 -p kd_z:=0.25 -p ki_z:=0.0 \
  -p max_v_x:=0.5 -p max_v_y:=0.5 -p max_v_z:=0.4
</code></pre>
<h5>Pane 3 &mdash; Start the Trajectory Publisher</h5>
<p>In your third terminal, source your workspace and run the trajectory publisher. By default, it will command the drone to fly the simple "Tuning Course."</p>
<pre><code class="language-bash"># Source your local workspace in this terminal as well
source ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/install/setup.bash

# Run the publisher for the Tuning Course.
# -p loop:=true:  Useful for continuous tuning without restarting.
# -p arrival_tol_m:=0.10: Sets a generous tolerance for the tuning phase.
ros2 run lab07_crazyflie trajectory_publisher --ros-args \
  -p loop:=true -p repub_sec:=0.5 -p arrival_tol_m:=0.10 -p arrival_hits:=5
</code></pre>
<h5>System Health Check</h5>
<p>Before proceeding, quickly verify that all parts of the system are communicating:</p>
<ul>
    <li>Is the drone receiving goals? Run <code>ros2 topic echo /goal_pose --once</code>. You should see a `PoseStamped` message.</li>
    <li>Is the controller sending commands? Run <code>ros2 topic echo /crazyflie/cmd_vel --once</code>. You should see a `Twist` message with non-zero values.</li>
    <li>Is the simulation publishing odometry? Run <code>ros2 topic echo /crazyflie/odom --once</code>.</li>
</ul>
<h3>5.7 The Iterative Tuning Workflow</h3>
<p><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">PID Controller in 1D for a Quadcopter</div></p>
<p>With the system running the looping "Tuning Course," you can now adjust the PID gains in real-time from any terminal. Use the <code>ros2 param set</code> command to change the controller's parameters. The general strategy is to <strong>make one change at a time, observe the result, and iterate.</strong></p>
<h4>Step 1: Tune the Z-Axis (Vertical Control)</h4>
<p>Tune the vertical axis first, as its dynamics are different due to gravity. Your goal is a brisk ascent/descent with minimal overshoot.</p>
<ol>
    <li><strong>Tune Proportional (Kp):</strong> Start by increasing <code>kp_z</code> until the drone responds quickly to height changes. A small amount of overshoot is expected. <br /><code>ros2 param set /goal_3d_controller kp_z 1.5</code></li>
    <li><strong>Tune Derivative (Kd):</strong> Add <code>kd_z</code> to act as a damper, reducing the overshoot and "bounce" at the top and bottom waypoints. <br /><code>ros2 param set /goal_3d_controller kd_z 0.3</code></li>
    <li><strong>Tune Integral (Ki):</strong> Only if you notice a persistent steady-state error (e.g., always hovering 2cm below the target), add a very small amount of <code>ki_z</code>. <br /><code>ros2 param set /goal_3d_controller ki_z 0.02</code></li>
</ol>
<h4>Step 2: Tune the X/Y-Axes (Planar Control)</h4>
<p>Once the Z-axis is stable, tune the X and Y gains. For this lab, you can generally keep the X and Y gains symmetric.</p>
<ol>
    <li><strong>Tune Proportional (Kp):</strong> Increase <code>kp_x</code> and <code>kp_y</code> together. Higher values will make the drone follow the path more tightly, but too high will cause it to overshoot corners and oscillate ("snaking").<br /><code>ros2 param set /goal_3d_controller kp_x 0.8</code><br /><code>ros2 param set /goal_3d_controller kp_y 0.8</code></li>
    <li><strong>Tune Derivative (Kd):</strong> Increase <code>kd_x</code> and <code>kd_y</code> to dampen the oscillations and help the drone "stick" its corners more cleanly.<br /><code>ros2 param set /goal_3d_controller kd_x 0.15</code><br /><code>ros2 param set /goal_3d_controller kd_y 0.15</code></li>
</ol>
<h3>5.8 Final Course and Performance Evaluation</h3>
<p>After you are satisfied with your gains on the tuning course, you will run the official "Final Course" for your timed attempt.</p>
<p><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:656px;min-height:150px;margin:1em auto;">Sample solution for a poorly tuned controller</div></p>
<h4>Step 1: Switch to the Final Course</h4>
<ol>
    <li><strong>Stop the Publisher:</strong> In Pane 3, press <code>Ctrl+C</code> to stop the trajectory publisher.</li>
    <li><strong>Edit the Script:</strong> Open <code>~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/src/lab07_crazyflie/lab07_crazyflie/scripts/trajectory_publisher.py</code>. Comment out the "Tuning Course" waypoint list and uncomment the "Final Course" list.</li>
    <li><strong>Relaunch Publisher for Timed Run:</strong> In Pane 3, relaunch the publisher with <code>loop</code> set to <code>false</code> and a tighter arrival tolerance. The node will print the total time upon completion.
        <pre><code class="language-bash"># Relaunch with final parameters. Target time is &lt;= 70.0s.
ros2 run lab07_crazyflie trajectory_publisher --ros-args \
  -p loop:=false -p repub_sec:=0.5 -p arrival_tol_m:=0.07 -p arrival_hits:=5
</code></pre>
    </li>
</ol>
<h4>Step 2: Generate the Required Plots</h4>
<p>For your final, graded run, you must also run the plotting node to record the trajectory.</p>
<ol>
    <li><strong>Start the Plotting Node:</strong> In an available terminal (e.g., Pane 3 after the timed run finishes, or a new Pane 4), start the plotter:
        <pre><code class="language-bash">source ~/workspaces/[netid]_robotics_fall2025/lab07/ros2_ws/install/setup.bash
ros2 run lab07_crazyflie plotting
</code></pre>
    </li>
    <li><strong>Run the Final Course Again:</strong> Relaunch the trajectory publisher (as in the previous step) to perform one complete, non-looping run of the Final Course.</li>
    <li><strong>Stop the Plotting Node:</strong> Once the course is complete, press <code>Ctrl+C</code> in the plotting terminal. It will automatically save two plot files (<code>xy_vs_goal.png</code> and <code>xyz_traces.png</code>) to your current directory.</li>
    <li><strong>Organize Your Files:</strong> Move the generated images into your lab07/docs/ folder and rename them according to the deliverables checklist.</li>
</ol>
<p><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:677px;min-height:150px;margin:1em auto;">Sample solution for a well tuned controller</div></p>
<h3>5.9 Troubleshooting and Common Issues</h3>
<ul>
    <li><strong>Symptom:</strong> Drone does not move at all.<br /><em>Suggestion:</em> Check that the controller (Pane B) and publisher (Pane C) are both running. Use <code>ros2 topic echo /goal_pose --once</code> to ensure goals are being sent.</li>
    <li><strong>Symptom:</strong> Drone drifts or moves in the wrong direction.<br /><em>Suggestion:</em> Verify that the TF transform from <code>map</code> to <code>crazyflie/base_footprint</code> is correct using <code>ros2 run tf2_ros tf2_echo map crazyflie/base_footprint</code>.</li>
    <li><strong>Symptom:</strong> Drone chatters or is "twitchy" when it reaches a waypoint.<br /><em>Suggestion:</em> Your gains are likely too aggressive. Try reducing <code>kp</code> slightly or increasing <code>kd</code> to add more damping.</li>
    <li><strong>Symptom:</strong> The simulation is running, but you see no odometry data.<br /><em>Suggestion:</em> Confirm the simulation is not paused. Use <code>ros2 topic list | grep odom</code> to ensure the topic is being published. If not, restart the simulation launch script (Pane A).</li>
</ul>
<h1 id="sec-6">6. Analysis and Discussion Questions</h1>
<p>Your PDF report must include thoughtful, well-written answers to the following questions. Your responses should go beyond simple observations and demonstrate an understanding of the underlying control principles and their practical implications.</p>
<h3>6.1 Tuning Narrative and Gain Selection</h3>
<p>As specified in the Deliverables section, first provide a concise narrative (3-5 sentences) describing your iterative tuning process. Explain how you arrived at your final gains. For instance, describe the visual behavior that prompted you to increase a P-term, add D-term damping, or introduce a small I-term.</p>
<hr />
<h3>6.2 Discussion Questions</h3>
<p>Please answer the following questions in your report.</p>
<ol>
    <li><strong>The Role of the Derivative (D) Term:</strong> The derivative term provides predictive damping. Describe the trade-offs you observed when tuning the <code>kd</code> gains. What was the drone's behavior when <code>kd</code> was too low relative to <code>kp</code>? Conversely, what happens if <code>kd</code> is set excessively high (even if not required for this lab, what would you expect)?</li>
    <li><strong>Integral (I) Term and System Bias:</strong> In a perfect simulation without external disturbances, one might assume the integral term is unnecessary (<code>ki=0</code>). In practice, a small <code>ki</code> can still be useful. Based on your observations, why might a small steady-state error persist that requires an integral term to correct? Furthermore, explain why a large <code>ki</code> value is often detrimental to performance, referencing the concept of "integrator windup."<br /><br /></li>
    <li><strong>Independent Axis Tuning (Z vs. X/Y):</strong> The lab procedure recommends tuning the Z-axis separately from the X and Y axes. Were your final optimal gains for Z significantly different from those for X/Y? Explain from a dynamics perspective why this is expected. What primary physical force affects the drone's vertical motion that has less impact on its planar motion?<br /><br /></li>
    <li><strong>System Parameters Beyond PID:</strong> The <code>trajectory_publisher</code> node had its own parameters, such as <code>arrival_tol_m</code> (arrival tolerance). How does this parameter create an interplay between the "mission planner" and the "controller"? Describe the trade-off in performance (course time vs. accuracy) when setting this tolerance. What would happen if the tolerance was set extremely small (e.g., 1 mm)?<br /><br /></li>
    <li><strong>From Simulation to Reality:</strong> Imagine you were tasked with deploying your PID gains on a real Crazyflie drone. What real-world factors, not present in our Gazebo simulation, would make tuning more challenging? Name at least two factors and explain how they would likely affect the drone's performance and your tuning strategy.</li>
</ol>
<p>&nbsp;</p>
<h1 id="sec-7">7. References and Further Reading</h1>
<p>This lab provides a practical introduction to PID control, but the field of control theory is deep and fascinating. The following resources are highly recommended for students who wish to explore these topics further.</p>
<hr />
<h3>7.1 Foundational PID and Control Theory</h3>
<ul>
    <li><strong>Control System Lectures by Brian Douglas</strong><br />This is perhaps one of the most highly-regarded, free resources for learning control theory. Brian Douglas provides exceptionally clear and intuitive video explanations of fundamental concepts, from transfer functions to state-space. His videos are an ideal supplement to a traditional textbook.
        <ul>
            <li><a href="https://www.youtube.com/user/ControlLectures" target="_blank" rel="noopener">Main YouTube Channel</a></li>
        </ul>
    </li>
</ul>
<p>&nbsp;</p>
<ul>
    <li><strong><em>Feedback Systems: An Introduction for Scientists and Engineers</em> by &Aring;str&ouml;m and Murray</strong><br />Often considered the modern "bible" of control theory, this entire textbook is available for free online from the authors. It provides a rigorous, comprehensive, and up-to-date look at the field.
        <ul>
            <li><a href="https://fbswiki.org/wiki/index.php/Main_Page" target="_blank" rel="noopener">Feedback Systems Wiki (with full PDF)</a></li>
        </ul>
    </li>
</ul>
<hr />
<h3>7.2 Practical Tuning and Implementation</h3>
<ul>
    <li><strong>Control Tutorials for MATLAB and Simulink (University of Michigan)</strong><br />While based in MATLAB, these tutorials provide excellent, step-by-step examples of modeling and tuning PID controllers for common systems (like motors, aircraft pitch, etc.). The underlying principles are universal and directly applicable to your Python implementation.
        <ul>
            <li><a href="https://ctms.engin.umich.edu/CTMS/index.php?example=Introduction&amp;section=ControlPID" target="_blank" rel="noopener">PID Controller Tutorials</a></li>
        </ul>
    </li>
</ul>
<p>&nbsp;</p>
<ul>
    <li><strong>"PID Tuning for Robotics" and Stack Exchange Discussions</strong><br />Sometimes the best advice comes from practitioners. These links offer practical tips, heuristics, and discussions about the nuances of tuning PID controllers specifically for robotic systems, where things rarely behave as cleanly as they do in textbooks.
        <ul>
            <li><a href="https://robotics.stackexchange.com/questions/167/what-are-good-strategies-for-tuning-pid-loops" target="_blank" rel="noopener">Robotics Stack Exchange: "What are good strategies for tuning PID loops?"</a></li>
        </ul>
    </li>
</ul>
<hr />
<h3>7.3 ROS 2 Resources</h3>
<ul>
    <li><strong>Official ROS 2 Documentation &amp; Tutorials</strong><br />The official documentation is the definitive source for learning about the ROS 2 ecosystem. The tutorials are an essential resource for mastering the tools and client libraries you've used in this lab.
        <ul>
            <li><a href="https://docs.ros.org/en/jazzy/Tutorials.html" target="_blank" rel="noopener">ROS 2 Jazzy Tutorials (Beginner CLI and Client Libraries)</a></li>
            <li><a href="https://docs.ros.org/en/jazzy/Concepts.html" target="_blank" rel="noopener">ROS 2 Core Concepts</a></li>
        </ul>
    </li>
</ul>
<h1 id="sec-8">Appendix: Beyond the Basics - Implementing a Robust PID Controller</h1>
<p>The PID controller used in the main lab procedure is intentionally straightforward to keep the focus on the fundamentals of tuning. However, production-grade controllers used in real-world robotics incorporate several refinements for safety, reliability, and performance. This appendix uses the provided <code>3d_goal_control_pro.py</code> script as a case study to explore some of these advanced techniques.</p>
<p>The goal here is not for you to replace your lab code, but to understand <em>why</em> these features exist and see <em>how</em> they can be implemented in ROS 2.</p>
<hr />
<h2>A. The Problem of Integrator Windup</h2>
<p>One of the most common failure modes for a simple PID controller occurs when the integral term becomes excessively large, a phenomenon known as <strong>integrator windup</strong>.</p>
<p><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:523px;min-height:150px;margin:1em auto;">Image placeholder</div></p>
<h4>The Scenario:</h4>
<p>Imagine your drone is commanded to move to a waypoint above a table, but it accidentally gets stuck underneath it. The position error in Z is large and persistent. As long as it's stuck, the integral term (<code>&int;e dt</code>) accumulates this large error, "winding up" to a massive value.</p>
<p>When the drone finally gets free, this huge accumulated value in the I-term results in a powerful, sustained command to move upwards. It doesn't just return to the setpoint; it dramatically overshoots it, potentially hitting the ceiling.</p>
<h4>The Solution: Integral Clamping (Anti-Windup)</h4>
<p>The solution is to prevent the integral term from growing beyond a reasonable limit. This is called <strong>integral clamping</strong>. In the <code>3d_goal_control_pro.py</code> script, this is handled inside the dedicated <code>PIDController</code> class.</p>
<ol>
    <li><strong>Initialization:</strong> The controller is initialized with an absolute clamp value.
        <pre><code class="language-python"># In the PIDController __init__ method:
self.i_clamp_abs = i_clamp_abs  # e.g., a value like 0.5
</code></pre>
    </li>
    <li><strong>Computation:</strong> During each computation step, after the integral is updated, it is immediately clamped to the range <code>[-i_clamp_abs, +i_clamp_abs]</code>.
        <pre><code class="language-python"># In the PIDController compute method:
self.integral += error * max(dt, 0.0)

# The clamping logic:
if self.i_clamp_abs is not None:
    self.integral = max(-self.i_clamp_abs, min(self.integral, self.i_clamp_abs))
</code></pre>
    </li>
</ol>
<p>This simple addition ensures the integral term provides enough force to overcome steady-state error but never accumulates to a dangerous level, making the controller far more reliable.</p>
<hr />
<h2>B. Other Features of a Robust Controller</h2>
<p>Beyond anti-windup, the advanced script demonstrates several other best practices for writing clean, configurable, and reliable ROS 2 nodes.</p>
<h4>1. A Reusable PID Class</h4>
<p>Instead of mixing the PID logic directly into the main control loop, the logic is encapsulated in its own <code>PIDController</code> class. This is a fundamental software engineering principle.</p>
<ul>
    <li><strong>Separation of Concerns:</strong> The class handles the math of PID control. The ROS 2 node handles the communication (topics, TF) and timing.</li>
    <li><strong>Reusability:</strong> This <code>PIDController</code> class could be imported and used in any other project (a line-following robot, a temperature controller, etc.) without modification.</li>
</ul>
<h4>2. Full ROS 2 Parameterization</h4>
<p>Notice that nearly every magic number&mdash;gains, topic names, frame IDs, velocity limits&mdash;is declared as a ROS 2 parameter using <code>self.declare_parameter(...)</code>.</p>
<ul>
    <li><strong>Configurability:</strong> This allows you (or another user) to change the behavior of the node from the command line or a launch file without ever editing the Python code. This is the standard, expected behavior for flexible ROS 2 nodes.</li>
</ul>
<h4>3. State Resets on New Goals</h4>
<p>When the controller receives a new waypoint, the accumulated error from tracking the <em>previous</em> waypoint is no longer relevant. In fact, it's harmful. The advanced script explicitly resets the PID state upon receiving a new goal.</p>
<pre><code class="language-python"># In the goal_callback method:
self.pid_x.reset()
self.pid_y.reset()
self.pid_z.reset()
self.pid_yaw.reset()
</code></pre>
<p>This prevents a "hangover" from the previous goal from corrupting the response to the new one.</p>
<h4>4. Robust Time Handling and Safety Defaults</h4>
<ul>
    <li><strong>Safe <code>dt</code> Handling:</strong> The control loop includes a check: <code>if dt &lt;= 0.0 or dt &gt; 1.0: dt = 0.0</code>. This prevents crashes or massive derivative spikes if the simulation time jumps or glitches, which can happen.</li>
    <li><strong>Safety Features:</strong> The node includes a <code>hover_on_tf_loss</code> parameter. If the drone's position in the world becomes unknown (e.g., TF data stops), the controller defaults to publishing zero velocity commands. This "fail-safe" behavior is critical for real-world systems.</li>
</ul>

</div>
