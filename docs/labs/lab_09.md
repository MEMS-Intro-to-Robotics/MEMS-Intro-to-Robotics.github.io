---
title: "Lab 09: Autonomous SLAM-Based Exploration"
---

# Lab 09: Autonomous SLAM-Based Exploration

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#overview">Overview</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#background">Conceptual Background</a></li>
        <li><a href="#setup">Environment Setup: Docker &amp; Simulation</a></li>
        <li><a href="#bringup">Part 1: System Bringup</a></li>
        <li><a href="#procedure">Part 2: Lab Procedure &amp; Node Development</a></li>
        <li><a href="#analysis">Part 3: Post-Lab Questions &amp; Discussion</a></li>
        <li><a href="#references">Further Reading</a></li>
        <li><a href="#troubleshooting">Debugging: An Engineer's Most Valuable Skill</a></li>
        <li><a href="#schema">Reference: The Language of Mobile Robotics</a></li>
    </ol>
</nav>
<section id="overview">
    <h2>1. Overview</h2>
    <p>How does a machine make sense of a world it has never seen? This is one of the most fundamental questions in robotics. In this lab, you will architect the logic that enables a robot to do just that. You will program a simulated TurtleBot 4 to autonomously explore an unknown maze, building a map of its environment while simultaneously tracking its own position within that map&mdash;a process known as <strong>Simultaneous Localization and Mapping (SLAM)</strong>.</p>
    <p>This entire lab is conducted within a high-fidelity simulation, allowing us to focus purely on the autonomous logic. You will write Python nodes to command the industry-standard ROS 2 Navigation Stack (Nav2), progressing from sending simple coordinate goals to implementing a complete, frontier-based exploration algorithm.</p>
    <figure style="text-align: center; margin: 2em auto; max-width: 500px;"><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">A side-by-side comparison photo of the TurtleBot 4 and the smaller TurtleBot 4 Lite mobile robots.</div>
        <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: #555; font-style: italic;">The TurtleBot 4 (left) and Lite (right). In this lab, we use a high-fidelity <strong>digital twin</strong> of the standard model, allowing us to develop and test complex software before deploying to physical hardware.</figcaption>
    </figure>
    <blockquote style="border-left: 4px solid #005a9c; padding-left: 15px; margin-left: 0; color: #555;">
        <h4 style="margin-top: 0; color: #005a9c;">🧠 The SLAM Paradox</h4>
        <p>How can a robot build a reliable map of a place it's never seen, while simultaneously using that same incomplete map to figure out where it is? This is the central "chicken-and-egg" problem of SLAM. You will solve it by programming your robot to make intelligent decisions about where to explore next.</p>
    </blockquote>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>Upon successful completion of this lab, you will be able to:</p>
    <ul>
        <li>Launch and manage a complete, multi-node robotics simulation stack (Gazebo, Nav2, SLAM, RViz).</li>
        <li>Write a ROS 2 node in Python that interfaces with the Nav2 action client to send asynchronous navigation goals.</li>
        <li>Command a robot to navigate to precise coordinates within a map that is being generated in real-time.</li>
        <li>Design and implement logic to generate and dispatch safe, randomly-generated navigation goals.</li>
        <li>Develop a frontier-based exploration algorithm that autonomously directs a robot to map an unknown environment.</li>
    </ul>
</section>
<section id="background">
    <h2>3. Conceptual Background</h2>
    <p>To engineer a solution, you first need a solid mental model of the system. A modern robotics stack isn't one program; it's a team of specialists working together. Let's meet the cast of characters you'll be directing.</p>
    <h3>The System Architecture: A Cast of Characters</h3>
    <ul>
        <li><strong>Gazebo (The Reality Engine):</strong> This is the physics simulator. It creates the virtual world, enforces the laws of physics, and generates the raw sensor data from the robot's virtual LiDAR. For our software, Gazebo <em>is</em> the real world.</li>
        <li><strong>SLAM Toolbox (The Cartographer):</strong> This node's sole job is to build the map. It listens to the robot's sensor data and wheel movements to solve the SLAM paradox, continuously publishing an updated map for others to use.</li>
        <li><strong>Nav2 (The Navigator):</strong> This is a sophisticated suite of nodes that handles all aspects of motion. It takes the map from the Cartographer and a goal from you, then calculates a safe, efficient path. Its final output is a stream of velocity commands sent to the robot's wheels.</li>
        <li><strong>Your Python Node (The Mission Commander):</strong> This is the node you will write. It represents the highest level of intelligence, making the strategic decisions. It decides <em>where</em> the robot should go and sends those goal requests to the Navigator.</li>
        <li><strong>RViz (The Mission Control Dashboard):</strong> This visualization tool is your window into the robot's mind. It overlays all the different data streams&mdash;the map, the sensor readings, the planned path&mdash;into a single, coherent view, making it an indispensable tool for debugging.</li>
    </ul>
    <blockquote style="border-left: 4px solid #ffc107; padding-left: 15px; margin-left: 0; color: #555;">
        <p><strong>The Power of Decoupling</strong><br />Notice how the Cartographer (SLAM) and the Navigator (Nav2) are separate. This is a deliberate and powerful design choice. SLAM can focus entirely on building the best possible map, and Nav2 can focus on planning the best possible path on whatever map it's given. As SLAM discovers a new hallway, Nav2 can *immediately* start planning paths through it, no questions asked. This modularity is the foundation of robust robotics.</p>
    </blockquote>
    <h3>Occupancy Grids: A Map of Probabilities</h3>
    <p>The map shared between all these nodes is a data structure called an <strong>occupancy grid</strong>. It's a 2D grid where each cell holds a value representing the system's confidence that the corresponding physical space is occupied, free, or unknown. Your node will read this map to make intelligent decisions.</p>
    <ul>
        <li><code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">-1</code> (Gray in RViz): <strong>Unknown Space</strong>. The robot's sensors have not yet seen this area.</li>
        <li><code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">0</code> (White/Light Gray): <strong>Free Space</strong>. The robot has observed this area to be clear and drivable.</li>
        <li><code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">1-100</code> (Black): <strong>Occupied Space</strong>. The robot has detected an obstacle with a given confidence level.</li>
    </ul>
    <p>The core challenge of autonomous exploration is to direct the robot to move from <em>Free Space</em> towards the boundary of <em>Unknown Space</em>, turning it into more Free or Occupied Space until the map is complete.</p>
    <figure style="text-align: center; margin: 2em auto; max-width: 500px;"><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">A real-world example of a SLAM map generated by a Roborock Q Revo robot vacuum, showing the floor plan of a house with different rooms color-coded.</div>
        <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: #555; font-style: italic;">A real-world occupancy grid generated by a robot vacuum. This is exactly the kind of map your code will enable the TurtleBot 4 to produce in this lab.</figcaption>
    </figure>
</section>
<section id="setup">
    <h2>5. Environment Setup: Docker &amp; Simulation</h2>
    <p>For this lab, we use a <strong>Docker container</strong> to ensure a consistent and reliable development environment. Think of it as a perfectly preserved laboratory bench, with every specialized tool (ROS 2 Humble, Gazebo, libraries) pre-installed and configured exactly as needed. This practice eliminates "it works on my machine" issues and is standard in modern software and robotics development.</p>
    <h3>5.1 The Professional Workflow: Managing File Permissions</h3>
    <p>A critical concept when using Docker for development is managing file permissions. Files you create *inside* the container (which runs as `root`) are owned by `root`. This prevents you from saving edits to those files in VS Code on your host machine.</p>
    <p>The solution is a professional two-terminal workflow:</p>
    <ol>
        <li><strong>Terminal 1 (Inside Container):</strong> You will run the Docker container. This terminal becomes your workspace for building and running ROS 2 nodes.</li>
        <li><strong>Terminal 2 (On Host VM):</strong> You will open a <em>second, separate</em> terminal on your main VM. You will use this terminal to run a command that reclaims ownership of the files, allowing you to edit them freely in VS Code.</li>
    </ol>
    <p>You can run the ownership command from Terminal 2 at any time, even while the container is running in Terminal 1. This allows you to create files in the container and immediately make them editable in VS Code.</p>
    <h3>5.2 Start the Container (GPU Acceleration)</h3>
    <p>In your first terminal, start the container. First, on your <strong>host VM</strong>, grant Docker permission to draw graphical windows on your desktop.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>xhost +local:docker</code></pre>
    <p>Now, run the container. This command will take over your current terminal.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>docker run --rm -it \
--name lab09_tb4 \
--net=host \
-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
-v ~/workspaces:/root/workspaces \
--gpus all \
gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:tb4-humble-latest</code></pre>
    <p>Note: if the command above does not successfully install all required packages, free up storage by running this command:</p>
    <p><strong></strong><code>docker system prune -a --volumes -f</code></p>
    <h3>5.3 Fix File Permissions (In a Second Terminal)</h3>
    <p><strong>Open a new terminal tab or window on your host VM.</strong> Use this terminal to run the `chown` (change owner) command. You can run this command whenever you create new files inside the container that you want to edit with VS Code.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>sudo chown -R $USER:$USER ~/workspaces/[netid]_robotics_fall2025/lab09</code></pre>
    <ul>
        <li><strong><code>sudo chown</code></strong>: The "change owner" command, run with administrator privileges.</li>
        <li><strong><code>-R</code></strong>: Makes the command "recursive" to apply to the directory and everything inside it.</li>
        <li><strong><code>$USER:$USER</code></strong>: A system variable that automatically uses your current username and group.</li>
        <li><strong><code>.../lab09</code></strong>: The specific path to your lab work.</li>
    </ul>
    <h3>5.4 Fallback: CPU Rendering</h3>
    <p>If you encounter graphics errors, use the Docker command from Step 5.2 but <strong>omit the <code>--gpus all</code> line</strong>. You can still use the same `chown` command from Step 5.3 in a second terminal to manage file permissions.</p>
</section>
<section id="bringup">
    <h2>6. Part 1: System Bringup</h2>
    <p><strong>Goal:</strong> Launch the complete TurtleBot 4 simulation stack, including the simulator, core robot software, and visualization tools.</p>
    <p><strong>Strategy:</strong> We will launch each major component in its own terminal pane. This modular approach is a critical debugging skill, allowing you to isolate and diagnose problems within the three pillars of a simulation: the world (Gazebo), the robot's mind (ROS 2 nodes), and the data bridges that connect them.</p>
    <blockquote style="border-left: 4px solid #ccc; padding-left: 15px; margin-left: 0; color: #555;">
        <p><strong>Pro-Tip:</strong> Use <code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">Ctrl+Shift+O</code> to split panes horizontally and <code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">Ctrl+Shift+E</code> to split vertically in Terminator. Click a pane to focus it.</p>
    </blockquote>
    <hr style="margin: 2em 0;" />
    <h3>Step 1 (Pane A): Launch the Simulator</h3>
    <p>First, run the Gazebo simulator and load the specific world model for this lab.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>ros2 launch turtlebot4_ignition_bringup ignition.launch.py world:=maze</code></pre>
    <ul>
        <li><strong><code>ignition.launch.py</code></strong>: The primary launch file for the Gazebo simulation environment.</li>
        <li><strong><code>world:=maze</code></strong>: A parameter that specifies which 3D world to load into the simulator.</li>
    </ul>
    <p>The Gazebo GUI will appear. Ensure the simulation is running by clicking the "Play" icon in the lower-left if it is paused.</p>
    <figure style="text-align: center; margin: 2em auto; max-width: 550px;"><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">Gazebo Garden showing TurtleBot4 in the maze world.</div>
        <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: #555; font-style: italic;">Gazebo, simulating the robot's physical environment and sensors.</figcaption>
    </figure>
    <hr style="margin: 2em 0;" />
    <h3>Step 2 (Pane B): Launch the Robot's Software Stack<br /><br /></h3>
    <p>With the world running, spawn the TurtleBot 4 into it and launch its autonomous navigation and mapping software.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>ros2 launch turtlebot4_ignition_bringup turtlebot4_spawn.launch.py slam:=true nav2:=true rviz:=true</code></pre>
    <ul>
        <li><strong><code>turtlebot4_spawn.launch.py</code></strong>: This script loads the robot's model (URDF) into the running Gazebo instance.</li>
        <li><strong><code>slam:=true</code></strong>: Enables the SLAM Toolbox for map creation.</li>
        <li><strong><code>nav2:=true</code></strong>: Enables the Navigation2 stack for path planning and obstacle avoidance.</li>
        <li><strong><code>rviz:=true</code></strong>: Launches RViz with a pre-configured view for monitoring the robot's state.</li>
    </ul>
    <figure style="text-align: center; margin: 2em auto; max-width: 450px;"><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">RViz 2 before launching the bridge.</div>
        <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: #555; font-style: italic;">RViz will show errors, as well as a white robot model until you launch the bridge in step 3.</figcaption>
    </figure>
    <hr style="margin: 2em 0;" />
    <h3>Step 3 (Pane C): Bridge Sensor Data to ROS 2</h3>
    <p>Finally, connect the simulated LiDAR in Gazebo to the ROS 2 ecosystem so the SLAM and Nav2 nodes can use its data.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>ros2 run ros_gz_bridge parameter_bridge \
/world/maze/model/turtlebot4/link/rplidar_link/sensor/rplidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan \
--ros-args -r /world/maze/model/turtlebot4/link/rplidar_link/sensor/rplidar/scan:=/scan</code></pre>
    <ul>
        <li><strong><code>ros_gz_bridge parameter_bridge</code></strong>: The node that translates messages between Gazebo (Ignition) and ROS 2.</li>
        <li><strong><code>...scan@ROS_TYPE@GZ_TYPE</code></strong>: The argument defining the translation rule for the LiDAR's `LaserScan` message.</li>
        <li><strong><code>--ros-args -r ...:=/scan</code></strong>: Remaps the lengthy Gazebo topic to the standard, conventional ROS 2 topic name, <code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">/scan</code>.</li>
    </ul>
    <p>Once this is running, you should see the laser scans represented as small pink dots appear and update in RViz.</p>
    <figure style="text-align: center; margin: 2em auto; max-width: 450px;"><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">RViz 2 showing laser scan, SLAM map, and Nav2 plan.</div>
        <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: #555; font-style: italic;">RViz, visualizing the robot's data streams: LiDAR scan, SLAM map, and Nav2's planned path.</figcaption>
    </figure>
    <blockquote style="border-left: 4px solid #ffc107; padding-left: 15px; margin-left: 0; color: #555;">
        <p><strong>Verifying the System</strong><br />If the laser scan points do not appear in RViz, it signifies a communication breakdown. The bridge is the most likely culprit. Double-check that this command was typed correctly and is running without errors before proceeding.</p>
    </blockquote>
    <h3>Step 4 (Pane D): Your Development Terminal</h3>
    <p>This pane is now your workspace. Keep it free for building and running your own nodes in Part 2.</p>
</section>
<section id="procedure">
    <h2>7. Part 2: Lab Procedure &amp; Node Development</h2>
    <p>Now we move from being system operators to system creators. In this section, you will write, build, and run your own Python nodes to serve as the "mission commander" for the TurtleBot 4. All commands should be run in your designated <strong>Development Terminal</strong> (Pane D).</p>
    <hr style="margin: 2em 0;" />
    <h3>7.1 Project Setup: Laying the Foundation</h3>
    <p>***Don't forget to change the owner of the directories if you didn't already do it above!***</p>
    <p>***Don't forget to source your ROS environment***</p>
    <p>Before writing a single line of Python, we must create a structured environment for our code. In ROS 2, this is called a <strong>workspace</strong>, and our code will live inside a <strong>package</strong> within it. This standard structure is what allows the `colcon` build system to find, build, and register our code so that ROS 2 tools like `ros2 run` can execute it.</p>
    <blockquote style="border-left: 4px solid #2e7d32; padding-left: 15px; margin-left: 0; color: #555;">
        <h4 style="margin-top: 0; color: #2e7d32;">🎯 Goal</h4>
        <p>Create a standard ROS 2 Python package that `colcon` can discover, build, and install.</p>
    </blockquote>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>cd ~/workspaces/[netid]_robotics_fall2025
mkdir -p lab09/ros2_ws/src
cd lab09/ros2_ws/src
ros2 pkg create turtlebot4_nav --build-type ament_python --dependencies rclpy geometry_msgs nav2_msgs
cd ..
colcon build --symlink-install
source install/setup.bash</code></pre>
    <ul>
        <li><strong><code>mkdir -p .../src</code></strong>: Creates the standard directory structure for a ROS 2 workspace. All of your source code will live in the <code>src</code> directory.</li>
        <li><strong><code>ros2 pkg create ...</code></strong>: This command generates the boilerplate for a Python ROS 2 package, including the crucial <code>setup.py</code> and <code>package.xml</code> files. We declare its dependencies on the message types we plan to use.</li>
        <li><strong><code>colcon build --symlink-install</code></strong>: This builds your workspace. The <code>--symlink-install</code> flag is a vital productivity tool: it creates symbolic links to your Python files instead of copying them. This means you can edit your Python scripts and run them immediately without needing to rebuild every time.</li>
        <li><strong><code>source install/setup.bash</code></strong>: This command updates your current terminal session's environment, making it aware of your new workspace and the packages within it. You must run this in any new terminal where you want to use your code.</li>
    </ul>
    <hr style="margin: 2em 0;" />
    <h3>7.2 Part A: Command and Control - Navigating to a Point</h3>
    <p>Our first task is to establish a basic command link with the Nav2 stack. We will write a simple "fire-and-forget" node that issues a single navigation goal and waits for the result.</p>
    <blockquote style="border-left: 4px solid #2e7d32; padding-left: 15px; margin-left: 0; color: #555;">
        <h4 style="margin-top: 0; color: #2e7d32;">🎯 Goal</h4>
        <p>Write a Python node that sends a single, hardcoded goal to Nav2 at map coordinates <code style="background-color: #eee; border-radius: 3px; font-family: monospace; padding: 2px 4px;">(1.0, 1.0)</code>.</p>
    </blockquote>
    <h4><strong>Step 1: Create the script file</strong></h4>
    <p>First, create the Python file inside your package and make it executable.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>cd ~/workspaces/[netid]_robotics_fall2025/lab09/ros2_ws/src/turtlebot4_nav/turtlebot4_nav
touch navigate_to_point.py
chmod +x navigate_to_point.py</code></pre>
    <h4><strong>Step 2: Implement the Node Logic</strong></h4>
    <p>Now, let's build the node. Open `navigate_to_point.py` and add the following code sections. We'll narrate the design process as we go.</p>
    <h5><strong>The Entrypoint and Core Imports</strong></h5>
    <p>Every Python script starts with imports. We need `rclpy` to talk to ROS 2, `PoseStamped` to define our goal, and the helpful `TurtleBot4Navigator` class which simplifies communication with Nav2.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import PoseStamped
from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Navigator

def main():
    rclpy.init()
    # ... Node logic will go here ...
    rclpy.shutdown()

if __name__ == '__main__':
    main()</code></pre>
    <h5><strong>Preparing the Robot</strong></h5>
    <p>Inside `main`, our first action is to create our `TurtleBot4Navigator` object. This object is our primary tool for interacting with Nav2. It's also good practice to ensure the robot is undocked before commanding it to move.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>    nav = TurtleBot4Navigator()
    if nav.getDockedStatus():
        nav.undock()</code></pre>
    <h5><strong>Constructing the Goal: The Model-to-Reality Link</strong></h5>
    <p>This is where we translate our abstract intent ("go to 1,1") into a concrete data structure that Nav2 understands. A `PoseStamped` message is that structure. Every field has a critical meaning.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>    goal = PoseStamped()
    goal.header.frame_id = 'map'
    goal.header.stamp = nav.get_clock().now().to_msg()
    goal.pose.position.x = 1.0
    goal.pose.position.y = 1.0
    goal.pose.orientation.w = 1.0</code></pre>
    <ul>
        <li><strong><code>goal.header.frame_id = 'map'</code></strong>: This is crucial. It tells Nav2 that the coordinates `(1.0, 1.0)` are in the fixed, global `map` frame created by SLAM, not relative to the robot's current position.</li>
        <li><strong><code>goal.pose.orientation.w = 1.0</code></strong>: This sets the orientation using a quaternion for "no rotation" (i.e., face forward along the X-axis of the map frame).</li>
    </ul>
    <h5>Sending the Goal and Awaiting the Outcome</h5>
    <p>Navigation isn't instantaneous. When we send the goal, Nav2 begins a long-running task. Our node must wait until that task is complete. A simple `while` loop achieves this, blocking further execution until Nav2 reports success or failure.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>    nav.startToPose(goal)
    nav.get_logger().info("Mission Start: Navigating to (1.0, 1.0)")
    while not nav.isTaskComplete():
        pass  # Block execution until the task is complete
    nav.get_logger().info('Mission Complete.')</code></pre>
    <h4><strong>Step 3: Register and Run the Node</strong></h4>
    <p>To make our script an executable that `ros2 run` can find, we must register it as an "entry point." Open `setup.py` in your package's root (`.../ros2_ws/src/turtlebot4_nav/`) and add the following to the `entry_points` dictionary.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>'console_scripts': [
    'navigate_to_point = turtlebot4_nav.navigate_to_point:main',
],</code></pre>
    <p>Finally, navigate to your workspace root, build to register the new entry point, source the environment, and run your node.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>cd ~workspaces/[netid]_robotics_fall2025/lab09/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 run turtlebot4_nav navigate_to_point</code></pre>
    <p>Observe RViz. You should see Nav2 generate a path (a pink line) and the robot will begin to follow it.</p>
    <hr style="margin: 2em 0;" />
    <h3>7.3 Part B: Adding Dynamic Behavior - Random Goals</h3>
    <p>A robot that only goes to one hardcoded spot isn't very useful. Let's evolve our node to send the robot on a patrol of several random points.</p>
    <blockquote style="border-left: 4px solid #2e7d32; padding-left: 15px; margin-left: 0; color: #555;">
        <h4 style="margin-top: 0; color: #2e7d32;">🎯 Goal</h4>
        <p>Modify the node to send a sequence of five randomly generated goals.</p>
    </blockquote>
    <h4><strong>Step 1: Evolve the Script</strong></h4>
    <p>Edit `navigate_to_point.py`. We will wrap our previous goal-sending logic in a `for` loop and use Python's `random` library to generate coordinates.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>#!/usr/bin/env python3
import rclpy
import random
from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Navigator, TurtleBot4Directions

def main():
    rclpy.init()
    nav = TurtleBot4Navigator()
    if nav.getDockedStatus():
        nav.undock()

    # Loop 5 times to send 5 different goals
    for i in range(5):
        # Generate a random coordinate within a 3x3 meter box around the origin
        x = random.uniform(-1.5, 1.5)
        y = random.uniform(-1.5, 1.5)
        
        # Use a helper to create the goal, commanding the robot to face North
        goal = nav.getPoseStamped([x, y], TurtleBot4Directions.NORTH)
        
        nav.get_logger().info(f"Sending goal #{i+1}: ({x:.2f}, {y:.2f})")
        nav.startToPose(goal)
        
        while not nav.isTaskComplete():
            pass # Wait for completion
            
    rclpy.shutdown()

if __name__ == '__main__':
    main()
</code></pre>
    <ul>
        <li><strong><code>for i in range(5):</code></strong>: This loop forms the core of our robot's new patrol behavior.</li>
        <li><strong><code>random.uniform(-1.5, 1.5)</code></strong>: Selects a floating-point number within the specified range. This effectively defines a "patrol box" for the robot.</li>
    </ul>
    <blockquote style="border-left: 4px solid #ffc107; padding-left: 15px; margin-left: 0; color: #555;">
        <p><strong>Common Pitfall: Unsafe Random Goals</strong><br />This simple approach is fast, but what happens if `random.uniform` picks coordinates that are inside a wall on the map? Nav2 is smart enough to report failure, but a more robust system would check if the random coordinate is in "Free Space" on the occupancy grid before sending it. This is a key concept for the next section.</p>
    </blockquote>
    <h4>Step 2: Run the Node</h4>
    <p>Thanks to our `--symlink-install` build, we don't need to rebuild. Just run the node again.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>ros2 run turtlebot4_nav navigate_to_point</code></pre>
    <p>Watch RViz as the robot completes one goal and immediately starts moving toward the next random one.</p>
    <hr style="margin: 2em 0;" />
    <h3>7.4 Part C: True Autonomy - Frontier Exploration</h3>
    <p>Now for the most exciting step: moving from a robot that follows a script to one that makes its own decisions. We will create a node that actively works to complete the map.</p>
    <blockquote style="border-left: 4px solid #2e7d32; padding-left: 15px; margin-left: 0; color: #555;">
        <h4 style="margin-top: 0; color: #2e7d32;">🎯 Goal</h4>
        <p>Create a stateful, class-based node that subscribes to the map, identifies "frontiers" (the boundary between known and unknown space), and navigates to them until the map is complete.</p>
    </blockquote>
    <h4>Step 1: Create the new script file</h4>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>cd ~workspaces/[netid]_robotics_fall2025/lab09/ros2_ws/src/turtlebot4_nav/turtlebot4_nav
touch autonomous_explore.py
chmod +x autonomous_explore.py</code></pre>
    <figure style="text-align: center; margin: 2em auto; max-width: 450px;"><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">A partially explored map in RViz.</div>
        <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: #555; font-style: italic;">A partially explored map in RViz, showing the pink navigation line.</figcaption>
    </figure>
    <h4><strong>Step 2: Implement the Explorer Node</strong></h4>
    <p>This node is more complex because it needs to maintain <strong>state</strong> (the current map) and make decisions periodically. A class is the perfect structure for this. Open `autonomous_explore.py` and we'll build it method by method.</p>
    <h5>Class Definition and `__init__`</h5>
    <p>The constructor sets up the node's components. We store the navigator as a member variable. Critically, we create a <strong>subscription</strong> to the `/map` topic to get data and a <strong>timer</strong> that will trigger our decision-making loop at a regular interval.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np
import random
from nav_msgs.msg import OccupancyGrid
from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Navigator, TurtleBot4Directions

class AutonomousExplorer(Node):
    def __init__(self):
        super().__init__('autonomous_explorer')
        self.nav = TurtleBot4Navigator()
        if self.nav.getDockedStatus():
            self.nav.undock()
        
        self.map_data = None # Will hold the processed OccupancyGrid
        
        # Create a subscriber to the /map topic
        self.create_subscription(OccupancyGrid, 'map', self.map_callback, 10)
        # Create a timer to trigger the exploration logic every 5 seconds
        self.create_timer(5.0, self.explore_loop)</code></pre>
    <h5><strong>The `map_callback`: Giving the Node Eyes</strong></h5>
    <p>This function is the node's connection to the outside world. Whenever SLAM Toolbox publishes a new map, this callback fires. We process the raw 1D array from the message into a 2D NumPy array, which is much easier to work with for finding frontiers.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>    def map_callback(self, msg: OccupancyGrid):
        # Reshape the 1D map data into a 2D numpy array
        self.map_data = np.array(msg.data, dtype=np.int16).reshape(msg.info.height, msg.info.width)
        self.map_resolution = msg.info.resolution
        self.map_origin = msg.info.origin.position
        self.get_logger().info('Map data updated.', once=True)</code></pre>
    <h5><strong>The `find_frontiers`: The Core Algorithm</strong></h5>
    <p>This is the "intelligence" of our node. A frontier cell is an "unknown" cell that is adjacent to a "free" cell. This simple algorithm finds them by sampling unknown cells and checking their neighbors.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>    def find_frontiers(self):
        if self.map_data is None: return []
        
        # Find all unknown cells (-1)
        rows, cols = np.where(self.map_data == -1)
        
        frontiers = []
        # Check the 8 neighbors of each unknown cell
        for r, c in zip(rows, cols):
            is_frontier = False
            for i in range(max(0, r-1), min(self.map_data.shape[0], r+2)):
                for j in range(max(0, c-1), min(self.map_data.shape[1], c+2)):
                    if self.map_data[i, j] == 0: # If a neighbor is free space
                        is_frontier = True
                        break
                if is_frontier:
                    frontiers.append((r, c))
                    break
        return frontiers</code></pre>
    <h5><strong>The `explore_loop`: The Decision Cycle</strong></h5>
    <p>Triggered by our timer, this loop executes the main logic. It checks if the robot is idle, finds frontiers, and if any exist, it picks one, converts its cell coordinates to world coordinates, and sends it as the next goal.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>    def explore_loop(self):
        # Don't do anything if we don't have a map yet or if the robot is busy
        if self.map_data is None or not self.nav.isTaskComplete():
            return
            
        frontiers = self.find_frontiers()
        if not frontiers:
            self.get_logger().info('No frontiers found. Exploration complete.')
            return
            
        # Pick a random frontier
        r, c = random.choice(frontiers)
        
        # Convert cell coordinates (r, c) to world coordinates (x, y)
        x = self.map_origin.x + (c + 0.5) * self.map_resolution
        y = self.map_origin.y + (r + 0.5) * self.map_resolution
        
        self.get_logger().info(f"Navigating to frontier at ({x:.2f}, {y:.2f})")
        goal = self.nav.getPoseStamped([x, y], TurtleBot4Directions.NORTH)
        self.nav.startToPose(goal)</code></pre>
    <h5><strong>The Main Execution Block</strong></h5>
    <p>Finally, we add the standard main function to initialize `rclpy`, create an instance of our class, and `spin` it. `rclpy.spin()` is an event loop that keeps the node alive, allowing its subscribers and timers to execute.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>def main():
    rclpy.init()
    node = AutonomousExplorer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()</code></pre>
    <h4>Step 3: Register and Run the Explorer</h4>
    <p>Open `setup.py` again and add the new entry point for our explorer node.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>'console_scripts': [
    'navigate_to_point = turtlebot4_nav.navigate_to_point:main',
    'auto_explore = turtlebot4_nav.autonomous_explore:main',
],</code></pre>
    <p>Build, source, and run your new autonomous node.</p>
    <pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; white-space: pre-wrap;"><code>cd ~workspaces/[netid]_robotics_fall2025/lab09/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 run turtlebot4_nav auto_explore</code></pre>
    <p>Watch RViz. The robot should now intelligently move towards the gray "unknown" areas on the map, methodically filling them in. You have now built a truly autonomous system.</p>
</section>
<section id="analysis">
    <h2>8. Part 3: Post-Lab Questions &amp; Discussion</h2>
    <p>Please provide thoughtful and detailed answers to the following questions in your PDF submission. The goal is to connect the core concepts to the code you wrote and the robot behaviors you observed.</p>
    <ol>
        <li><strong>System Symbiosis: SLAM and Nav2</strong><br />In this lab, SLAM Toolbox and Nav2 operate in a tightly coupled, symbiotic relationship.
            <ul>
                <li><strong>A)</strong> Describe this relationship: Which system is the "producer" of the map, and which is the "consumer"?</li>
                <li><strong>B)</strong> Recall your experience in Part 7.2 when you first sent a navigation goal while the map was still largely incomplete. Describe what you observed about Nav2's initial path. How did the path planning change in real-time as the SLAM system mapped more of the maze?</li>
            </ul>
        </li>
        <li><strong>Engineering Safer Randomness</strong><br />In Part 7.3, your node sent goals to random coordinates. This is a fast but potentially unsafe approach.
            <ul>
                <li><strong>A)</strong> What is the primary risk of sending a goal to a random coordinate within a large bounding box before the map is fully explored?</li>
                <li><strong>B)</strong> Propose a code-level improvement to this node. In pseudocode or a clear English description, explain how you would use the data from the <code>/map</code> topic (an <code>OccupancyGrid</code> message) to <em>validate</em> a randomly generated point. Specifically, which cell value(s) (`-1`, `0`, `100`) would you check for at the proposed coordinate to ensure the goal is both safe and useful?</li>
            </ul>
        </li>
        <li><strong>Critiquing Your Exploration Algorithm</strong><br />Analyze the behavior of your `autonomous_explore` node from Part 7.4, which used a random-frontier selection strategy.
            <ul>
                <li><strong>A)</strong> In the context of an <code>OccupancyGrid</code>, what defines a "frontier" cell? Why is navigating to these cells an effective strategy for exploration?</li>
                <li><strong>B)</strong> Describe an instance where you observed this simple random strategy being inefficient. For example, did the robot ever travel a long distance to explore a tiny dead-end, when a large, promising, unexplored area was much closer?</li>
                <li><strong>C)</strong> Propose a more intelligent strategy for <em>selecting</em> which frontier to navigate to. What are the engineering trade-offs between choosing, for example, the <strong>closest</strong> frontier versus the <strong>largest</strong> frontier (one with the most free-space neighbors)?</li>
            </ul>
        </li>
        <li><strong>Handling Dynamic Obstacles</strong><br />Our simulation environment was static. Imagine a dynamic obstacle (like a person walking) is introduced.
            <ul>
                <li><strong>A)</strong> Nav2 uses different costmaps for safety. Explain how the <strong><code>local_costmap</code></strong> (responsible for immediate, short-term collision avoidance) and the <strong><code>global_costmap</code></strong> (responsible for long-term path planning) would react differently as the person walks in front of the robot.</li>
                <li><strong>B)</strong> Would this person eventually become a permanent "wall" in the main map generated by the SLAM Toolbox? Explain why or why not, considering that SLAM algorithms build their maps based on probabilistic observations over time.</li>
            </ul>
        </li>
    </ol>
</section>
<section id="references">
    <h2>9. Further Reading</h2>
    <p>The concepts you've implemented are foundational in robotics. A key trait of an expert engineer is the drive to understand the principles "under the hood." These resources are your next step in that journey, connecting the code you wrote to the research that made it possible.</p>
    <h3>Official Documentation</h3>
    <ul>
        <li><strong><a href="https://docs.nav2.org/" target="_blank" rel="noopener">Official Nav2 Documentation</a>:</strong> The definitive guide for the navigation stack you commanded in this lab.</li>
        <li><strong><a href="https://github.com/SteveMacenski/slam_toolbox" target="_blank" rel="noopener">SLAM Toolbox Repository</a>:</strong> The source code and documentation for the mapping system you used.</li>
        <li><strong><a href="https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html" target="_blank" rel="noopener">Writing a Simple ROS 2 Python Node</a>:</strong> The official tutorial for the core skills you applied.</li>
    </ul>
    <h3>Key Research Papers</h3>
    <ul>
        <li><strong>[1] B. Yamauchi, "A frontier-based approach for autonomous exploration," 1997.</strong>
            <blockquote><strong>Relevance:</strong> This is the foundational paper that introduced the concept of "frontier-based exploration." The core logic you implemented in your <code>autonomous_explore.py</code> node is a direct application of the strategy proposed here.</blockquote>
        </li>
        <li><strong>[2] G. Grisetti, et al., "Improved techniques for grid mapping with Rao-Blackwellized particle filters," 2007.</strong>
            <blockquote><strong>Relevance:</strong> This paper details one of the most influential algorithms in the history of SLAM. The SLAM Toolbox you used is a modern descendant of the core principles proven in this research.</blockquote>
        </li>
        <li><strong>[3] S. Macenski, et al., "The Marathon 2: A Navigation System," 2020.</strong>
            <blockquote><strong>Relevance:</strong> This paper describes the architecture of Nav2, the system your <code>TurtleBot4Navigator</code> class commands. It explains how complex navigation behaviors are managed using advanced techniques like Behavior Trees.</blockquote>
        </li>
    </ul>
</section>
<section id="troubleshooting">
    <h2>10. Debugging: An Engineer's Most Valuable Skill</h2>
    <p>Debugging is not guesswork; it is a systematic process of deduction based on your mental model of the system. When something goes wrong, ask "Which component is responsible for this behavior?" and check its terminal pane first.</p>
    <blockquote style="border-left: 4px solid #c62828; padding-left: 15px; margin-left: 0; color: #555;">
        <p><strong>The Golden Rule of ROS 2 Debugging</strong><br />If your node isn't found or can't launch, your first instinct should always be: "Did I <code>source install/setup.bash</code> in this terminal?" This single step solves the vast majority of "command not found" errors.</p>
    </blockquote>
    <ul>
        <li><strong>Symptom: Blank or extremely slow GUI windows (Gazebo/RViz).</strong>
            <ul>
                <li><strong>Diagnosis:</strong> The system is failing at graphics rendering. The bridge between the host GPU and the container is likely misconfigured.</li>
                <li><strong>Solution:</strong> Restart the container using the CPU-based <strong>No-GPU Fallback</strong> instructions from Section 5.2.</li>
            </ul>
        </li>
        <li><strong>Symptom: Error: <code>Executable '...' not found</code>.</strong>
            <ul>
                <li><strong>Diagnosis:</strong> The ROS 2 environment in your current terminal doesn't know about your node. This can have two causes: (1) You forgot to <code>source</code> the workspace after building, or (2) The executable was never registered correctly during the build.</li>
                <li><strong>Solution:</strong> First, run <code>source install/setup.bash</code>. If that doesn't work, double-check for typos in your <code>setup.py</code> `entry_points` and run <code>colcon build</code> again.</li>
            </ul>
        </li>
        <li><strong>Symptom: Your node crashes with an <code>ImportError</code>.</strong>
            <ul>
                <li><strong>Diagnosis:</strong> The Python interpreter cannot find the script file it's trying to import. This is almost always a file structure problem.</li>
                <li><strong>Solution:</strong> Ensure your Python scripts are inside the nested package directory (e.g., <code>src/turtlebot4_nav/turtlebot4_nav/</code>), which is where Python's module discovery system expects them to be.</li>
            </ul>
        </li>
        <li><strong>Symptom: Error: <code>No transform from [frame A] to [frame B]</code>.</strong>
            <ul>
                <li><strong>Diagnosis:</strong> This is a TF (Transform) error, meaning the system has lost its spatial awareness. TF is the "skeleton" that connects all coordinate frames. This error means a critical bone is missing, usually because a core node like SLAM or the <code>robot_state_publisher</code> has crashed.</li>
                <li><strong>Solution:</strong> Check all your terminal panes for error messages. The pane that is full of red text is your source of the problem.</li>
            </ul>
        </li>
        <li><strong>Symptom: You run your node, but the robot doesn't move.</strong>
            <ul>
                <li><strong>Diagnosis:</strong> The command from your node is not reaching the robot's wheels. The problem lies somewhere in the chain of command: Your Node -&gt; Nav2 -&gt; Gazebo.</li>
                <li><strong>Solution:</strong> Check Pane B for Nav2 errors. Is the robot's position on the map shown in red? This indicates a localization failure. In RViz, is a path being generated? If not, the goal may be unreachable or in an unknown part of the map.</li>
            </ul>
        </li>
    </ul>
</section>
<section id="schema">
    <h2>11. Reference: The Language of Mobile Robotics</h2>
    <p>Effective engineers share a common vocabulary. These are the core coordinate frames and topics that define our system's architecture.</p>
    <h3>Coordinate Frames (The System's Sense of Space)</h3>
    <ul>
        <li><code>map</code>: <strong>The Global Frame of Reference.</strong> A static, unchanging frame that is the source of all truth for navigation. It's created by SLAM. Your navigation goals *must* be expressed in this frame.</li>
        <li><code>odom</code>: <strong>The Continuous Motion Frame.</strong> This frame tracks the robot's movement based on wheel encoders. It's smooth and continuous but will drift over time. SLAM's job is to calculate the correction between <code>odom</code> and <code>map</code>.</li>
        <li><code>base_link</code>: <strong>The Robot's Egocentric Frame.</strong> This frame is rigidly attached to the center of the robot. Data from sensors, like the LiDAR, is usually published relative to this frame.</li>
    </ul>
    <h3>Key Topics (The System's Communication Channels)</h3>
    <ul>
        <li><code>/map</code> (<code>nav_msgs/msg/OccupancyGrid</code>): The live data feed of the world map.
            <ul>
                <li><em>Published By:</em> <code>slam_toolbox</code></li>
                <li><em>Consumed By:</em> <code>nav2</code>, your <code>autonomous_explore</code> node, <code>rviz</code></li>
            </ul>
        </li>
        <li><code>/scan</code> (<code>sensor_msgs/msg/LaserScan</code>): The raw distance measurements from the LiDAR.
            <ul>
                <li><em>Published By:</em> Gazebo (via the <code>ros_gz_bridge</code>)</li>
                <li><em>Consumed By:</em> <code>slam_toolbox</code>, <code>nav2</code> (for obstacle avoidance)</li>
            </ul>
        </li>
        <li><code>/tf</code> and <code>/tf_static</code>: The broadcast channels for all coordinate frame relationships (transforms).
            <ul>
                <li><em>Published By:</em> Many nodes (<code>robot_state_publisher</code>, <code>slam_toolbox</code>, etc.)</li>
                <li><em>Consumed By:</em> Almost every node in the system, especially <code>rviz</code>.</li>
            </ul>
        </li>
    </ul>
</section>

</div>
