---
title: "Lab 05: Motion Planning with MoveIt 2"
---

# Lab 05: Motion Planning with MoveIt 2

<div class="lab-content">

<h1>1 Introduction</h1>
<h2>1.1 Overview</h2>
<p>In this lab, you&rsquo;ll use <strong>MoveIt 2</strong>&mdash;ROS 2&rsquo;s primary motion-planning framework&mdash;to control a <strong>Kinova Gen3 Lite</strong> robotic arm (with gripper) <strong>in simulation</strong>. You&rsquo;ll command the arm to reach target poses via <strong>collision-free plans</strong>, operate the <strong>end-effector</strong>, and compare <strong>joint-space</strong> vs <strong>Cartesian</strong> goal specification. You&rsquo;ll also add <strong>collision objects</strong> to the planning scene and observe the planner automatically route around them. By the end, you&rsquo;ll have the core skills needed for practical manipulation.</p>
<h2>1.2 Background</h2>
<ul>
    <li><strong>What is Motion Planning?</strong> Motion planning computes a <strong>valid</strong> sequence of movements that takes the robot from a start state to a goal <strong>without collisions</strong> with itself or the environment.</li>
    <li><strong>MoveIt 2 and RViz.</strong> MoveIt 2 integrates tightly with RViz. RViz is your &ldquo;window into the planner&rsquo;s mind&rdquo;: you can inspect the robot&rsquo;s current and goal states, visualize the <strong>planned trajectory</strong>, and view the <strong>virtual world</strong> known to the planner.</li>
    <li><strong>The Planning Scene.</strong> MoveIt&rsquo;s internal world model. It contains the robot geometry plus any <strong>collision objects</strong> you add. The planner <strong>only avoids what exists in this scene</strong>&mdash;if it isn&rsquo;t added, it isn&rsquo;t avoided.</li>
    <li><strong>Joint Space vs. Cartesian Space</strong>
        <ul>
            <li><strong>Joint-Space Goal:</strong> You specify each joint angle directly. This is efficient for moving among known, safe configurations.</li>
            <li><strong>Cartesian Goal:</strong> You specify the target <strong>position (X, Y, Z)</strong> and <strong>orientation</strong> of the end-effector; MoveIt solves <strong>inverse kinematics</strong> to compute joint angles. This is essential for tasks like pick-and-place.</li>
        </ul>
    </li>
</ul>
<h1>2 Objectives</h1>
<p>By the end of this lab, you will be able to:</p>
<ul>
    <li>Launch a simulated Kinova Gen3 Lite and interact with MoveIt 2 from a <strong>Python</strong> script.</li>
    <li>Command the arm using both <strong>joint-space</strong> and <strong>Cartesian</strong> goals.</li>
    <li>Add a <strong>collision object</strong> to the planning scene and verify collision-aware planning.</li>
    <li>Control the <strong>gripper</strong> programmatically from Python.</li>
    <li>Visualize and verify planned trajectories in <strong>RViz</strong>.</li>
</ul>
<hr />
<h1>3 Pre-Lab Preparation</h1>
<p>This section walks you through preparing your environment. The key is to start <strong>one</strong> Docker container and then use a terminal multiplexer called <code>Terminator</code> <em>inside</em> that container to run all the required commands.</p>
<h3>Step 1: Pull the Docker Image</h3>
<p>Open a terminal on your <strong>host machine</strong> (your main Ubuntu desktop) and pull the latest version of the course Docker image. This command downloads all the necessary software, including ROS 2, MoveIt, and the robot simulator.</p>
<pre><code>docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest</code></pre>
<h3>Step 2: Start the ROS 2 Container</h3>
<p>Next, you will start the container that will serve as your entire workspace for this lab.</p>
<p>First, authorize your host machine to display graphical applications from the container:</p>
<pre><code>xhost +local:docker</code></pre>
<p>Now, run the following command in your host terminal to start the container. We are giving it a specific name (<code>--name ros2_lab</code>) to make it easy to manage. <strong>You will only run this command once.</strong></p>
<pre><code>docker run --rm -it \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/workspaces:/workspaces \
  --name ros2_lab \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:kinova-jazzy-latest bash</code></pre>
<p>Your terminal prompt will change (e.g., to <code>root@hostname:/#</code>). This confirms you are now operating <strong>inside the Docker container</strong>. The original terminal is now your gateway into the container.</p>
<h3>Step 3: Launch Your Command Center (Terminator)</h3>
<p>To manage the different programs we need to run, the very next step is to launch <code>Terminator</code>, a tool that lets you have multiple terminals in one window. This will be your main workspace.</p>
<p>Inside the container's prompt, run:</p>
<pre><code>terminator &amp;</code></pre>
<blockquote>
    <p><strong>What does "<code>terminator &amp;</code>" do?</strong><br />This command starts the Terminator application. The <code>&amp;</code> symbol at the end tells the shell to run it in the background, which frees up your original terminal window. A new, separate Terminator window will appear. <strong>This new window is where you will do the rest of the lab work.</strong></p>
</blockquote>
<p>You can now minimize the original terminal window that you used to run the <code>docker run</code> command. From now on, work only within the new Terminator window.</p>
<h3>Step 4: Launch the Kinova Simulation in Gazebo</h3>
<p>In the Terminator window that just appeared, you have your first terminal pane. Use this pane to launch the robot simulation. This command starts the physics simulator (Gazebo) and the necessary ROS 2 controllers for the robot.</p>
<pre><code>ros2 launch kortex_bringup kortex_sim_control.launch.py \
  sim_gazebo:=true \
  robot_type:=gen3_lite \
  gripper:=gen3_lite_2f \
  robot_name:=gen3_lite \
  dof:=6 \
  launch_rviz:=false \
  use_sim_time:=true \
  robot_controller:=joint_trajectory_controller</code></pre>
<p>You will see a lot of output as the simulation starts. A Gazebo window showing the robot in a simple environment should also appear. <strong>Leave this terminal pane running.</strong></p>
<h3>Step 5: Open a New Terminal Pane and Launch MoveIt</h3>
<p>Now you need a second terminal to launch the motion planning software (MoveIt).</p>
<ol>
    <li>Click anywhere inside your Terminator window.</li>
    <li>
        <p>Split the terminal to create a new pane:</p>
        <ul>
            <li><strong>Split Horizontally:</strong> <code>Ctrl+Shift+O</code></li>
            <li><strong>Split Vertically:</strong> <code>Ctrl+Shift+E</code></li>
        </ul>
    </li>
</ol>
<p>You now have a second, independent command prompt right next to your first one. In this <strong>new pane</strong>:</p>
<ol>
    <li>
        <p>First, you must "source" the ROS 2 setup files. Every new terminal needs to be told where to find the ROS 2 commands.</p>
        <pre><code>source /opt/ros/jazzy/setup.bash</code></pre>
    </li>
    <li>
        <p>Now, launch the MoveIt configuration, which includes the RViz visualization tool.</p>
        <pre><code>ros2 launch kinova_gen3_lite_moveit_config sim.launch.py \
  use_sim_time:=true</code></pre>
    </li>
</ol>
<p>An RViz window will open, showing a colorful model of the robot arm. You are now fully set up! You have one pane running Gazebo and another running MoveIt/RViz. You can create even more panes later for running your own Python scripts.</p>
<h3>Step 6: Final Checks and Familiarization</h3>
<ul>
    <li>
        <p><strong>Identify TF Frames:</strong> In RViz, go to the "Displays" panel on the left. Click "Add", and select "TF". This will visualize the robot's coordinate frames. Note the names of:</p>
        <ul>
            <li><strong>Base Frame:</strong> <code>base_link</code></li>
            <li><strong>End-Effector Frame:</strong> <code>end_effector_link</code></li>
        </ul>
    </li>
    <li><strong>MotionPlanning Panel:</strong> Locate the "MotionPlanning" panel in RViz (usually at the bottom left). You will use this to plan and execute robot movements.</li>
    <li><strong>Read Appendix A:</strong> Skim the appendix on controlling the gripper to prepare for using it in the lab.</li>
</ul>
<h1>4 Lab Procedure</h1>
<h2>Part 1 &mdash; Setup and Initial Skeleton</h2>
<p>You&rsquo;ll create a new <strong>ament_python</strong> package for this lab, drop in a starter script, register it as a console entry point, and do a first build. These steps mirror Lab 4&rsquo;s workflow (workspace &rarr; package &rarr; build &rarr; source &rarr; run), but targeted at <strong>MoveIt 2</strong> and the Kinova Gen3 Lite.</p>
<blockquote>
    <p><strong>IMPORTANT: Prerequisite Check</strong><br />Before starting Part 1, make sure your simulation from the Pre-Lab section is running correctly. Your <strong>Terminator</strong> window should have at least two panes active: one running the Gazebo launch command and another running the MoveIt/RViz launch command.</p>
    <p>You will be opening a <strong>third</strong> terminal pane in this section to do your development work (building and running your new node).</p>
</blockquote>
<h3>A. Create your Lab 5 Workspace and Package</h3>
<p>First, we'll create the directory structure for your new package. These commands must be run <strong>inside the Docker container</strong>.</p>
<ol>
    <li>
        <p>Open a <strong>new, third terminal pane</strong> in your Terminator window (<code>Ctrl+Shift+O</code> or <code>Ctrl+Shift+E</code>). This new pane is where you will run the following commands.</p>
    </li>
    <li>
        <p>Navigate to your course folder and create the directory structure for this lab's workspace.</p>
        <pre><code># In your new terminal pane inside the container
cd /workspaces/[netid]_robotics_fall2025
mkdir -p lab05/ros2_ws/src
cd lab05/ros2_ws/src</code></pre>
        <p><em>Why: ROS 2 expects packages to live under a workspace&rsquo;s <code>src/</code> directory.</em></p>
    </li>
    <li>
        <p>Now, create the <code>ament_python</code> package itself.</p>
        <pre><code># Make sure you are still in lab05/ros2_ws/src
ros2 pkg create --build-type ament_python lab05_moveit</code></pre>
    </li>
    <li>
        <p>Finally, create a <code>scripts</code> directory inside your new package. This is where your Python node will live.</p>
        <pre><code># Make sure you are still in lab05/ros2_ws/src
mkdir -p lab05_moveit/lab05_moveit/scripts</code></pre>
    </li>
</ol>
<blockquote>
    <p><strong>Permission Denied?</strong><br />If you see a permissions error when creating files or folders, you can fix it by running the following command in a terminal <strong>on your host VM</strong> (not in the container):<br /><code>sudo chown -R $USER:$USER ~/workspaces/[netid]_robotics_fall2025/lab05</code></p>
</blockquote>
<h3>B. Add the Starter Script</h3>
<p>Next, you will create the main Python file for this lab. This process involves creating an empty file from your container terminal, then opening and editing that file in VS Code on your main VM.</p>
<ol>
    <li>
        <p><strong>Create an empty file:</strong> In your <strong>Docker container terminal</strong> (the third pane you created), make sure you are in the <code>lab05/ros2_ws/src</code> directory. Then, use the <code>touch</code> command to create the empty Python script:</p>
        <pre><code># Make sure you are in /workspaces/[netid]_robotics_fall2025/lab05/ros2_ws/src
touch lab05_moveit/lab05_moveit/scripts/motion_planner.py</code></pre>
    </li>
    <li>
        <p><strong>Open the file in VS Code:</strong> Now, switch over to your VS Code application (running on your VM). Use the file explorer sidebar to navigate to and open the file you just created. The full path will be:<br /><code>~/workspaces/[netid]_robotics_fall2025/lab05/ros2_ws/src/lab05_moveit/lab05_moveit/scripts/motion_planner.py</code></p>
    </li>
    <li>
        <p><strong>Copy and paste the starter code:</strong> The file will be empty. Copy the entire Python code block below.</p>
    </li>
    <li>
        <p><strong>Paste and Save:</strong> Paste the code into the <code>motion_planner.py</code> file in VS Code and save it (<code>Ctrl+S</code>).</p>
    </li>
</ol>
<h4>Starter Code for <code>motion_planner.py</code></h4>
<pre><code class="language-python">
#!/usr/bin/env python3
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from pymoveit2 import MoveIt2
from pymoveit2.gripper_interface import GripperInterface

# Geometry messages you&rsquo;ll likely need in later milestones
from geometry_msgs.msg import Pose, Quaternion

class MotionPlannerNode(Node):
    def __init__(self):
        super().__init__("motion_planner_node")

        # --- MoveIt 2 interface for the Kinova Gen3 Lite arm ---
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=["joint_1", "joint_2", "joint_3", "joint_4", "joint_5", "joint_6"],
            base_link_name="base_link",
            end_effector_name="end_effector_link",
            group_name="arm",
        )

        # --- Gripper interface for Kinova Gen3 Lite 2F gripper ---
        try:
            self.gripper = GripperInterface(
                node=self,
                gripper_joint_names=["right_finger_bottom_joint"],
                open_gripper_joint_positions=[0.8],    # "open"
                closed_gripper_joint_positions=[0.0],  # "closed"
                gripper_group_name="gripper",
                gripper_command_action_name="/gen3_lite_2f_gripper_controller/gripper_cmd",
            )
        except Exception as e:
            self.get_logger().warn(
                f"GripperInterface could not be initialized ({e}). "
                "Milestone 4 will be skipped."
            )
            self.gripper = None

    # ---------------- Milestones you will implement ----------------
    def run_milestone_1(self):
        self.get_logger().info("Running Milestone 1: Joint-Space Motion")
        # TODO: Home &rarr; Retract joints; see Part 2, Milestone 1.

    def run_milestone_2(self):
        self.get_logger().info("Running Milestone 2: Cartesian Motion")
        # TODO: Define waypoints and plan a Cartesian path.

    def run_milestone_3(self):
        self.get_logger().info("Running Milestone 3: Collision Avoidance")
        # TODO: Add a box to the planning scene and replan around it.

    def run_milestone_4(self):
        self.get_logger().info("Running Milestone 4: Gripper Control")
        # TODO: Open/close the gripper using self.gripper (Appendix A).

def main(args=None):
    rclpy.init(args=args)
    node = MotionPlannerNode()

    # Use a multithreaded executor so planning + logging don&rsquo;t block each other
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    # ---- Run the milestones sequentially ----
    node.run_milestone_1()
    time.sleep(1)
    node.run_milestone_2()
    time.sleep(1)
    node.run_milestone_3()
    time.sleep(1)
    node.run_milestone_4()

    # Give any last actions time to log/finish
    time.sleep(0.5)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
</code></pre>
<p>After running the command above, you can verify the file was created by running <code>ls -l lab05_moveit/lab05_moveit/scripts/</code>.</p>
<h3>C. Register a Console Entry Point</h3>
<p>To make your script runnable with <code>ros2 run</code>, you must register it as a "console script" entry point. Open <code>lab05/ros2_ws/src/lab05_moveit/setup.py</code> in VS Code on your VM and edit the <code>entry_points</code> block to look like this:</p>
<pre><code class="language-python">entry_points={
    'console_scripts': [
        'motion_planner = lab05_moveit.scripts.motion_planner:main',
    ],
},</code></pre>
<p><em>Reminder: The format is <code>'executable_name = package_name.module_name:function_name'</code>. Note there is no <code>.py</code> extension in the module name.</em></p>
<h3>D. Build and Source the Workspace</h3>
<p>Now, build your package and source the resulting setup files so ROS 2 can find it.</p>
<ol>
    <li>
        <p>Navigate to the <strong>root of your workspace</strong> (the folder that contains the <code>src</code> directory).</p>
        <pre><code># In your third terminal pane
cd /workspaces/[netid]_robotics_fall2025/lab05/ros2_ws</code></pre>
    </li>
    <li>
        <p>Build the workspace using <code>colcon</code>. The <code>--symlink-install</code> flag lets you edit your Python script later without needing to rebuild every time.</p>
        <pre><code>colcon build --symlink-install</code></pre>
    </li>
    <li>
        <p><strong>Source the workspace.</strong> This step tells your current terminal where to find the package you just built. <strong>You must do this in every new terminal you open.</strong></p>
        <pre><code>source install/setup.bash</code></pre>
    </li>
    <li>
        <p>As a sanity check, ask ROS 2 to list packages and confirm it can find yours:</p>
        <pre><code>ros2 pkg list | grep lab05_moveit</code></pre>
        <p>If this command prints <code>lab05_moveit</code>, you are ready to go!</p>
    </li>
</ol>
<h3>E. Final Smoke Test</h3>
<p>With everything built, let's run the node to see if it works. This command will be run in the same third terminal pane you've been using, which already has the workspace sourced.</p>
<p><strong>Required State Check:</strong></p>
<ul>
    <li>Your first terminal pane is running the <strong>Gazebo simulation launch</strong> command.</li>
    <li>Your second terminal pane is running the <strong>MoveIt and RViz launch</strong> command.</li>
    <li>Your third terminal pane has successfully built and sourced the <code>lab05/ros2_ws</code> workspace.</li>
</ul>
<p>Run your node:</p>
<pre><code>ros2 run lab05_moveit motion_planner</code></pre>
<p>You should see the node start up and print the four "Running Milestone X" log messages, one after another. If you see this, your setup is correct and you are ready to start implementing the milestone functions.</p>
<h3>F. Common Pitfalls &amp; Fixes</h3>
<ul>
    <li><strong><code>ros2 run ...</code> &rarr; &ldquo;package not found&rdquo;</strong>
        <ul>
            <li>Did you forget to <strong>source</strong> the workspace in your current terminal? Run <code>source install/setup.bash</code> from your workspace root.</li>
        </ul>
    </li>
    <li><strong><code>ros2 run ...</code> &rarr; &ldquo;executable not found&rdquo;</strong>
        <ul>
            <li>Did you edit <code>setup.py</code>? You must <strong>rebuild</strong> after changing it: <code>cd /path/to/ws &amp;&amp; colcon build --symlink-install</code>. Then re-source.</li>
            <li>Is the entry point path in <code>setup.py</code> spelled correctly? Check for typos.</li>
        </ul>
    </li>
    <li><strong>RViz shows nothing / planner can&rsquo;t connect</strong>
        <ul>
            <li>Ensure your <strong>simulation + MoveIt</strong> stack from the Pre-Lab is still running in the other terminal panes.</li>
        </ul>
    </li>
    <li><strong>Imports fail (e.g., <code>pymoveit2</code> not found)</strong>
        <ul>
            <li>You are likely running the command outside of the course Docker container. Make sure you are inside the container before sourcing and running your node.</li>
        </ul>
    </li>
</ul>
<h2>Lab Procedure Part 2 &mdash; Milestones</h2>
<hr />
<h3>Milestone 1 &mdash; Joint-Space Motion</h3>
<p><strong>Goal:</strong> Command the robot's individual joints to move to specific target angles. This is the most direct way to control a robot's configuration.</p>
<blockquote>
    <p><strong>What is Joint-Space Motion?</strong><br />Think of telling someone to "bend your elbow to 90 degrees and straighten your wrist." You are giving a command for each joint directly. You aren't telling them where their hand should end up in the room; you are defining the pose by its joint angles. This is useful for moving to known, safe configurations like "Home" or "Retract."</p>
</blockquote>
<h4>How It Works: A Step-by-Step Breakdown</h4>
<ol>
    <li><strong>Warm-up Loop:</strong> The code starts with a short loop that calls <code>compute_fk()</code>. This acts as a "warm-up," giving the MoveIt services a few seconds to fully initialize after the node starts.</li>
    <li><strong>Move to Home:</strong> The first action is to define a <code>home_pose</code> where all joint angles are <code>0.0</code>. It then calls <code>self.moveit2.move_to_configuration()</code> to plan and execute the motion. The script then pauses with <code>wait_until_executed()</code> until the robot physically stops moving.</li>
    <li><strong>Define Retract:</strong> The code then defines a custom <code>retract_joints</code> configuration. <strong>This is the part you must modify.</strong> You will use the RViz joint sliders to find your own unique set of six joint angles for a safe, tucked-in pose.</li>
    <li><strong>Move to Retract:</strong> Finally, it calls <code>move_to_configuration()</code> again to move the arm from the Home pose to your custom Retract pose.</li>
</ol>
<h4>Complete Milestone 1 Code</h4>
<p>Replace the empty <code>run_milestone_1</code> method in your <code>motion_planner.py</code> script with the following complete code block.</p>
<pre><code class="language-python">def run_milestone_1(self):
    """
    Home -&gt; Retract using joint-space motion.
    """
    import time

    self.get_logger().info("Running Milestone 1: Joint-Space Motion")

    # Warm up FK once so MoveIt services have a moment to come up.
    # (compute_fk() returns PoseStamped or None if the service isn't ready yet)
    for _ in range(30):  # ~3s max
        ps = self.moveit2.compute_fk()
        if ps is not None:
            break
        time.sleep(0.1)

    # --- Move to the "Home" configuration ---
    self.get_logger().info("Moving to Home configuration...")
    home_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # radians
    self.moveit2.move_to_configuration(joint_positions=home_pose)
    self.moveit2.wait_until_executed()

    # --- Define a custom "Retract" configuration ---
    # TODO: change these numbers to your own collision-free joints (RViz Joints tab)
    self.get_logger().info("Defining custom Retract configuration...")
    retract_joints = [0.0, -1.2, 1.4, 0.0, 1.1, 0.0]
    self.retract_joints = retract_joints  # Save for use in Milestone 3

    # --- Execute the retract motion ---
    self.get_logger().info("Moving to Retract configuration...")
    self.moveit2.move_to_configuration(joint_positions=self.retract_joints)
    self.moveit2.wait_until_executed()
</code></pre>
<h4>Checkpoint</h4>
<p><strong>What to look for:</strong> The robot in Gazebo and RViz should first move to the "Home" pose (all joints straight) and then immediately move to your custom "Retract" pose.</p>
<p>📸 <strong>Milestone 1 Screenshot:</strong> Take a screenshot of RViz showing the robot at its final "Retract" position, with the planned trajectory visible.</p>
<hr />
<h3>Milestone 2 &mdash; Cartesian Path Motion</h3>
<p><strong>Goal:</strong> Command the robot's <strong>end-effector</strong> (the gripper) to follow a specific path in 3D space, like moving in a straight line, without the planner needing to worry about the individual joint angles.</p>
<blockquote>
    <p><strong>What is Cartesian Motion?</strong><br />Instead of commanding each joint, you now command the tool. Think of telling someone, "Move your hand 10 cm forward." Your brain (the motion planner) automatically calculates the necessary elbow, shoulder, and wrist angles to make that happen. This is essential for tasks like tracing a shape or picking up an object from a known location.</p>
</blockquote>
<h4>How It Works: A Step-by-Step Breakdown</h4>
<ol>
    <li><strong>Get Current Pose:</strong> The code first calls <code>compute_fk()</code> (Forward Kinematics) to determine the current 3D position and orientation of the end-effector.</li>
    <li><strong>Define First Waypoint:</strong> It uses <code>deepcopy</code> to create an independent copy of the current pose. It then modifies this copy by adding <code>0.10</code> meters (10 cm) to its X position.</li>
    <li><strong>Plan and Execute:</strong> It calls <code>self.moveit2.plan()</code> with <code>cartesian=True</code>. This specific command computes a straight-line tool path. If a valid plan is found, it's executed.</li>
    <li><strong>Define Second Waypoint:</strong> It repeats the process, starting from the end of the first move, this time adding <code>0.05</code> meters (5 cm) to the Z position.</li>
</ol>
<h4>Complete Milestone 2 Code</h4>
<p>Replace the empty <code>run_milestone_2</code> method in your script with the following complete code block. <strong>Your task is to modify the distances in the two pre-written segments.</strong></p>
<pre><code class="language-python">def run_milestone_2(self):
    """
    Two straight-line Cartesian segments from the current EE pose.
    """
    from copy import deepcopy

    self.get_logger().info("Running Milestone 2: Cartesian Motion")

    # --- Get the current end-effector pose ---
    current_ps = self.moveit2.compute_fk(
        fk_link_names=[self.moveit2.end_effector_name]
    )[0]
    current_pose = current_ps.pose

    # --- Cartesian segment 1: +10 cm along X (EDIT ME) ---
    p1 = deepcopy(current_pose)
    p1.position.x += 0.10

    traj = self.moveit2.plan(
        pose=p1,
        cartesian=True,
        max_step=0.005,
        cartesian_fraction_threshold=0.90,
    )
    self.moveit2.execute(traj)
    self.moveit2.wait_until_executed()

    # --- Cartesian segment 2: +5 cm along Z (EDIT ME) ---
    p2 = deepcopy(p1)
    p2.position.z += 0.05

    traj = self.moveit2.plan(
        pose=p2,
        cartesian=True,
        max_step=0.005,
        cartesian_fraction_threshold=0.90,
    )
    self.moveit2.execute(traj)
    self.moveit2.wait_until_executed()
</code></pre>
<h4>Checkpoint</h4>
<p><strong>What to look for:</strong> The robot's end-effector should trace two distinct straight lines in space. The green trajectory line in RViz should be perfectly straight for each segment.</p>
<p>📸 <strong>Milestone 2 Screenshot:</strong> Take a screenshot of RViz showing the complete two-segment Cartesian path and the robot at its final position.</p>
<hr />
<h3>Milestone 3 &mdash; Collision Avoidance</h3>
<p><strong>Goal:</strong> Teach the motion planner about a new obstacle in its environment and watch it automatically plan a new, safer path to avoid it.</p>
<blockquote>
    <p><strong>What is the Planning Scene?</strong><br />MoveIt maintains a "Planning Scene," which is the robot's internal 3D model of its environment. We can add virtual objects to this scene. When the planner is asked to find a path, it will treat these virtual objects as real, solid obstacles to be avoided.</p>
</blockquote>
<h4>How It Works: A Step-by-Step Breakdown</h4>
<ol>
    <li><strong>Add Obstacle:</strong> The code calls <code>self.moveit2.add_collision_box()</code> to add a virtual box to the planning scene. You must specify a unique ID, its dimensions (in meters), its position (in meters, relative to the <code>base_link</code> frame), and its orientation. <strong>You will need to edit the size and position of this box.</strong></li>
    <li><strong>Wait for Propagation:</strong> A short <code>time.sleep(1.0)</code> gives the system a moment to update the planning scene across all its components.</li>
    <li><strong>Re-run Motion:</strong> The code then runs the exact same Home &rarr; Retract sequence from Milestone 1. Because the planner is now aware of the box, it is forced to find a new, non-colliding path. The resulting trajectory will be visibly different.</li>
    <li><strong>Cleanup:</strong> Although commented out, it's good practice to use <code>remove_collision_object()</code> to clean up virtual objects when you are done with them.</li>
</ol>
<h4>Complete Milestone 3 Code</h4>
<p>Replace the empty <code>run_milestone_3</code> method in your script with the following complete code block.</p>
<pre><code class="language-python">def run_milestone_3(self):
    """
    Add an obstacle and re-run Home -&gt; Retract to observe avoidance.
    """
    import time

    self.get_logger().info("Running Milestone 3: Collision Avoidance")

    # --- Add obstacle (EDIT ME for size/position) ---
    self.moveit2.add_collision_box(
        id="obstacle_box",
        size=(0.10, 0.50, 0.10),           # (sx, sy, sz) meters
        position=(0.25, 0.00, 0.15),       # (x, y, z) meters<br />        quat_xyzw=(0.0, 0.0, 0.0, 1.0),
        frame_id=self.moveit2.base_link_name,
    )
    self.get_logger().info("Added collision box to the planning scene.")
    time.sleep(1.0)  # let PlanningScene propagate

    # --- Re-run Home -&gt; Retract with obstacle present ---
    home_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    self.moveit2.move_to_configuration(joint_positions=home_pose)
    self.moveit2.wait_until_executed()

    if not hasattr(self, "retract_joints") or self.retract_joints is None:
        self.get_logger().warn("Retract joints not set. Run Milestone 1 first.")
        return

    self.moveit2.move_to_configuration(joint_positions=self.retract_joints)
    self.moveit2.wait_until_executed()

    # --- Optional: clean up afterwards ---
    # self.moveit2.remove_collision_object("obstacle_box")
    # self.get_logger().info("Removed collision box.")
</code></pre>
<h4>Checkpoint</h4>
<p><strong>What to look for:</strong> In RViz, a green box should appear. The trajectory for the Home &rarr; Retract motion should now be a <strong>noticeably different, curved path</strong> that goes around the box.</p>
<p>📸 <strong>Milestone 3 Screenshot:</strong> Take a screenshot of RViz that clearly shows the collision box and the new, curved trajectory avoiding it.</p>
<hr />
<h3>Milestone 4 &mdash; Gripper Control</h3>
<p><strong>Goal:</strong> Use the provided high-level interface to command the gripper to open and close.</p>
<blockquote>
    <p><strong>The Gripper Interface</strong><br />The `GripperInterface` we initialized in the starter code is a convenient helper. It abstracts away the low-level ROS 2 action commands, allowing you to simply call methods like `.open()` and `.close()` without worrying about the underlying details.</p>
</blockquote>
<h4>Complete Milestone 4 Code</h4>
<p>Replace the empty <code>run_milestone_4</code> method in your script with the following complete code block. The code first checks that the gripper was initialized correctly, then calls the simple open/close commands, waiting for each to complete.</p>
<pre><code class="language-python">def run_milestone_4(self):
    """
    Open/Close the gripper with basic guards.
    """
    import time

    if self.gripper is None:
        self.get_logger().error("Gripper not initialized. Skipping milestone.")
        return

    self.get_logger().info("Running Milestone 4: Gripper Control")

    # Open
    self.get_logger().info("Opening gripper...")
    self.gripper.open()
    self.gripper.wait_until_executed()
    self.get_logger().info("Gripper is open.")
    time.sleep(1.0)

    # Close
    self.get_logger().info("Closing gripper...")
    self.gripper.close()
    self.gripper.wait_until_executed()
    self.get_logger().info("Gripper is closed.")
</code></pre>
<h4>Checkpoint</h4>
<p><strong>What to look for:</strong> Watch the robot's gripper in both Gazebo and RViz. You should see the fingers move to a fully open position, pause, and then move to a fully closed position.</p>
<p>📸 <strong>Milestone 4 Screenshot:</strong> Take a screenshot of RViz or Gazebo showing the gripper in either the fully open or fully closed state.</p>
<h1>Milestone 5 &mdash; Putting It All Together: Your Own Collision-Aware Motion</h1>
<hr />
<h2>Goal</h2>
<p>Your final task is to write a new, standalone Python script that combines the skills from the previous milestones. You will create a program that:</p>
<ol>
    <li>Adds a virtual obstacle to the robot's environment.</li>
    <li>Commands the robot to perform a motion that would normally collide with that obstacle.</li>
    <li>Relies on the MoveIt planner to automatically generate a new, safe trajectory that detours around the obstacle.</li>
</ol>
<p>&nbsp;</p>
<p>This is a capstone exercise that proves you can command motion, modify the planning scene, and correctly sequence ROS 2 actions in your own code.</p>
<h3>Choosing Your Strategy: Joint-Space vs. Cartesian</h3>
<p>You have two ways to command the detour. You should choose one.</p>
<ul>
    <li><strong>Joint-Space Detour (Recommended for simplicity):</strong> This is like the task in Milestone 3. You place an obstacle and then command the robot to move from a start configuration (e.g., Home) to an end configuration (e.g., your Retract pose). If the box is in the way of the most direct path, the planner will create a wide, sweeping curve to avoid it.
        <ul>
            <li><strong>Use this if:</strong> The exact path of the gripper doesn't matter, only that it gets from A to B without a collision.</li>
        </ul>
    </li>
    <li><strong>Cartesian Detour:</strong> This is more complex but offers more precise control. You would command the end-effector to move in a straight line that intentionally passes through the obstacle's location. The planner will refuse this impossible path. Instead, you would need to create a multi-point path (e.g., move up, move over, move down) that manually guides the gripper around the box.
        <ul>
            <li><strong>Use this if:</strong> You need precise, straight-line control to navigate a cluttered space.</li>
        </ul>
    </li>
</ul>
<h3>Step-by-Step Implementation Guide</h3>
<h4>Step 1: Create and Populate the New Script File</h4>
<p>Follow the same manual process as before to create your script for this milestone.</p>
<ol>
    <li>
        <p><strong>Create an empty file:</strong> In your <strong>Docker container terminal</strong>, use the <code>touch</code> command to create the empty script:</p>
        <pre><code># Make sure you are in /workspaces/[netid]_robotics_fall2025/lab05/ros2_ws/src
touch lab05_moveit/lab05_moveit/scripts/m5_detour.py</code></pre>
    </li>
    <li>
        <p><strong>Open the file in VS Code:</strong> Switch to VS Code on your VM and open the new, empty file.</p>
    </li>
    <li>
        <p><strong>Copy and paste the scaffold code:</strong> Copy the entire Python scaffold below and paste it into the <code>m5_detour.py</code> file in VS Code, then save it.</p>
    </li>
</ol>
<h4>Scaffold Code for <code>m5_detour.py</code></h4>
<pre><code class="language-python">
#!/usr/bin/env python3
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from pymoveit2 import MoveIt2

class M5DetourNode(Node):
    def __init__(self):
        super().__init__("m5_detour_node")

        # MoveIt 2 interface for the Kinova Gen3 Lite arm
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=["joint_1", "joint_2", "joint_3", "joint_4", "joint_5", "joint_6"],
            base_link_name="base_link",
            end_effector_name="end_effector_link",
            group_name="arm",
        )

    def run(self):
        """
        Main logic for Milestone 5.
        """
        self.get_logger().info("Milestone 5: Planning a collision-aware detour.")
        
        # --- Give MoveIt time to warm up ---
        time.sleep(1.0)

        # TODO: STEP 1 - Add a collision box
        # Hint: Look at your run_milestone_3() code.
        # Use self.moveit2.add_collision_box(...)
        # Remember to time.sleep(1.0) afterwards!

        # TODO: STEP 2 - Plan and execute a motion that detours around the box
        # Option A (Joint-Space):
        #   - Move to a starting configuration (like Home).
        #   - Move to an ending configuration (like your Retract pose).
        #   - Make sure the box is between them!
        #
        # Option B (Cartesian):
        #   - Get the current pose.
        #   - Define a series of waypoints that go *around* the box.
        #   - Plan and execute the path.

        # TODO: STEP 3 - Clean up the collision box
        # Hint: Use self.moveit2.remove_collision_object(...)

        self.get_logger().info("Milestone 5 complete.")

def main(args=None):
    rclpy.init(args=args)
    node = M5DetourNode()

    # Use a multithreaded executor
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    # Run the main logic
    node.run()

    time.sleep(1.0)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
</code></pre>
<h4>Step 2: Register the New Executable</h4>
<p>Just like before, you must tell ROS 2 that this new script is an executable. Open the <code>setup.py</code> file in VS Code and add the new entry point for <code>m5_detour</code>. <strong>Pay close attention to the comma!</strong></p>
<pre><code class="language-python"># In lab05_moveit/setup.py

entry_points={
    'console_scripts': [
        'motion_planner = lab05_moveit.scripts.motion_planner:main',
        'm5_detour = lab05_moveit.scripts.m5_detour:main',  # &lt;-- ADD THIS LINE
    ],
},
</code></pre>
<h4>Step 3: Implement Your Logic</h4>
<p>Now, open <code>m5_detour.py</code> in VS Code and fill in the <code>TODO</code> sections inside the <code>run()</code> method. You should copy and paste code you already wrote in the previous milestones!</p>
<ol>
    <li><strong>For adding the box:</strong> Copy the <code>self.moveit2.add_collision_box(...)</code> call from your <code>run_milestone_3</code> function. Choose a new size and position.</li>
    <li><strong>For the motion:</strong> Copy the relevant code from either <code>run_milestone_1</code> (for joint-space motion) or <code>run_milestone_2</code> (for Cartesian motion).</li>
    <li><strong>For cleanup:</strong> Copy the <code>self.moveit2.remove_collision_object(...)</code> call from the end of Milestone 3.</li>
</ol>
<blockquote>
    <p><strong>Planning Tip:</strong> The key to a good demonstration is placing the obstacle intelligently. Put the box directly in the way of the most obvious path between your start and end points. If the robot can still find a simple path, your box isn't positioned correctly. Make it bigger or move it until a detour is absolutely necessary.</p>
</blockquote>
<h4>Step 4: Build, Source, and Run</h4>
<p>Since you modified <code>setup.py</code>, a rebuild is required. Run the full sequence in your terminal:</p>
<pre><code class="language-bash"># From your workspace root: /workspaces/[netid]_robotics_fall2025/lab05/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 run lab05_moveit m5_detour
</code></pre>
<p>Watch RViz and your terminal. Tweak the box position or goal pose in your script and re-run until you see a clear, obvious detour trajectory.</p>
<hr />
<h3>Troubleshooting</h3>
<ul>
    <li><strong>"Executable not found":</strong> You forgot to rebuild after editing <code>setup.py</code>, or there is a typo in the entry point name.</li>
    <li><strong>Box is not visible in RViz:</strong> In the "Displays" panel on the left, make sure you have added a "PlanningScene" display and that the "Scene Geometry" checkbox is ticked. Also confirm you used <code>frame_id="base_link"</code>.</li>
    <li><strong>Path doesn't detour:</strong> Your box is not actually in the way. Move it closer to the robot's path or make it larger.</li>
    <li><strong>Planning fails completely:</strong> Your box might be making the goal unreachable. Try a smaller box or move it slightly. For Cartesian plans, remember that long, straight lines are very difficult for the planner; break them into smaller segments.</li>
</ul>
<h1>5 Analysis and Discussion</h1>
<p>Answer each prompt in <strong>2&ndash;4 sentences</strong> (brief, clear, and specific).</p>
<ol>
    <li><strong>Joint vs. Cartesian goals.</strong> In your own words, what&rsquo;s the key difference between commanding a joint-space goal and a Cartesian goal? Give one example where joint-space is preferable and one example where Cartesian is the natural choice.</li>
    <li><strong>Cartesian path &ldquo;fraction&rdquo;.</strong> What does the <code>fraction</code> returned by your Cartesian plan indicate? Name two plausible reasons it might be &lt; 1.0 and one change you would try to improve it.</li>
    <li><strong>Planning scene accuracy.</strong> Why must the planning scene reflect reality? Describe one concrete risk if it doesn&rsquo;t, and one practice you would use to keep it up to date (e.g., adding/attaching/removing objects).</li>
    <li><strong>Gripper control fit.</strong> Which ROS 2 communication type best fits the gripper&rsquo;s <code>open()</code> / <code>close()</code> behavior, and why is that a good match for this task (think: time-extended action with feedback/result vs. one-shot message)?</li>
    <li><strong>Quick troubleshooting mindset.</strong> A plan fails to execute. What are the first two checks you make in RViz or logs (keep it practical&mdash;think planning group, frames, collisions, limits, controllers)?</li>
</ol>
<hr />
<h1>Expected file tree</h1>
<pre><code>[netid]_robotics_fall2025/
└─ lab05/
   ├─ README.md
   ├─ .gitignore                      # exclude build/, install/, log/
   ├─ docs/
   │  ├─ m1_joint_home_to_retract.png
   │  ├─ m2_cartesian_path.png
   │  ├─ m3_collision_avoidance.png
   │  ├─ m4_gripper_open_close.png
   │  └─ m5_detour.png
   └─ ros2_ws/
      ├─ src/
      │  └─ lab05_moveit/
      │     ├─ package.xml
      │     ├─ setup.py               # console entries for both scripts
      │     ├─ setup.cfg
      │     ├─ lab05_moveit/
      │     │  ├─ __init__.py
      │     │  └─ scripts/
      │     │     ├─ motion_planner.py   # Milestones 1&ndash;4
      │     │     └─ m5_detour.py        # Milestone 5
      ├─ build/                       # DO NOT COMMIT
      ├─ install/                     # DO NOT COMMIT
      └─ log/                         # DO NOT COMMIT </code></pre>
<pre></pre>
<hr />
<h1>Appendix A &mdash; Reference for <code>pymoveit2</code> (conceptual + API guide)</h1>
<p>Use this as a reference, not a drop-in solution. It explains what each interface does, how to wire it up, and the typical call shapes. Wherever you see <code>...</code> or UPPER_SNAKE_CASE, you must fill in values from <strong>your robot</strong> (URDF/SRDF, RViz, TF tree, controller names).</p>
<hr />
<h2>A.1 Node + executor pattern</h2>
<p><strong>Purpose:</strong> keep callbacks (planning scene updates, action feedback, logs) responsive while you run synchronous milestone code.</p>
<p><strong>Key points</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Use a <code>MultiThreadedExecutor</code> in a background thread.</p>
                </li>
                <li>
                    <p>Put your interfaces (MoveIt, gripper) on a subclass of <code>Node</code>.</p>
                </li>
                <li>
                    <p>Call your &ldquo;milestone&rdquo; methods in order after <code>spin</code> starts.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Skeleton (fill in names; don&rsquo;t copy-paste blindly):</strong></p>
<pre><code class="language-python">class YourNode(rclpy.node.Node):
    def __init__(self):
        super().__init__("YOUR_NODE_NAME")
        # self.moveit2 = ...
        # self.gripper = ...
        # optional: self.retract_joints = None

def main():
    rclpy.init()
    node = YourNode()
    exec = MultiThreadedExecutor(num_threads=2)
    exec.add_node(node)
    threading.Thread(target=exec.spin, daemon=True).start()

    # node.run_milestone_1()
    # node.run_milestone_2()
    # node.run_milestone_3()
    # node.run_milestone_4()

    rclpy.shutdown()
</code></pre>
<h2>A.2 MoveIt2 arm interface</h2>
<p>Constructs the planner/controller wrapper for your arm group.</p>
<p><strong>Minimum fields</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>joint_names</code>: ordered list of arm joints (<strong>SRDF order</strong>).</p>
                </li>
                <li>
                    <p><code>base_link_name</code>: your planning frame (often <code>base_link</code>).</p>
                </li>
                <li>
                    <p><code>end_effector_name</code>: tool frame (e.g., <code>end_effector_link</code>).</p>
                </li>
                <li>
                    <p><code>group_name</code>: the MoveIt planning group (e.g., <code>arm</code>).</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Typical call shape:</strong></p>
<pre><code class="language-python">self.moveit2 = MoveIt2(
    node=self,
    joint_names=["JOINT_1","JOINT_2","JOINT_3","JOINT_4","JOINT_5","JOINT_6"],
    base_link_name="BASE_LINK",
    end_effector_name="EE_LINK",
    group_name="ARM_GROUP",
    execute_via_moveit=False,           # default: execute directly via controller
    ignore_new_calls_while_executing=False,
    use_move_group_action=False,        # if True (and not cartesian), uses move_group action
)
# Optional tuning (properties; 0.0&ndash;1.0 scales)
self.moveit2.max_velocity = 0.5
self.moveit2.max_acceleration = 0.5

# Optional planner hints (properties)
self.moveit2.num_planning_attempts = 10
self.moveit2.allowed_planning_time = 5.0
self.moveit2.planner_id = "RRTConnectkConfigDefault"  # if exposed by your setup
# self.moveit2.pipeline_id = "ompl"
</code></pre>
<p><strong>Gotchas</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><strong>Joint order matters.</strong> Use SRDF order from RViz &rarr; MotionPlanning &rarr; <strong>Joints</strong>.</p>
                </li>
                <li>
                    <p><strong>Names must match</strong> your robot setup (frames, group).</p>
                </li>
                <li>
                    <p>Units: positions in <strong>meters</strong>, angles in <strong>radians</strong>; quaternions <code>(x, y, z, w)</code>.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<h2>A.3 Joint-space planning</h2>
<p><strong>When to use:</strong> moving between known, safe configurations (e.g., Home &rarr; a tucked pose).</p>
<p><strong>Core methods</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>move_to_configuration(joint_positions: list[float], joint_names: list[str] = None, tolerance=..., weight=...)</code><br />Plans <strong>and executes</strong> to an explicit joint array.</p>
                </li>
                <li>
                    <p><code>wait_until_executed()</code> &mdash; blocks until the controller reports done.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<blockquote>
    <p><strong>Note:</strong> <code>move_to_configuration()</code> does <strong>not</strong> take named targets; pass a 6-element joint array (SRDF order).</p>
</blockquote>
<p><strong>Typical flow (pseudocode):</strong></p>
<pre><code class="language-python"># Explicit joint array
user_pose = [J1, J2, J3, J4, J5, J6]  # radians, SRDF order
self.moveit2.move_to_configuration(joint_positions=user_pose)
self.moveit2.wait_until_executed()
</code></pre>
<p><strong>Checks</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>If motion aborts instantly, look for joint limits or self-collisions.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<h2>A.4 Cartesian motion (single-pose segments)</h2>
<p><strong>When to use:</strong> straight-line end-effector motion in the planning frame.</p>
<p><strong>Core methods</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>compute_fk(joint_state=None, fk_link_names=None) -&gt; PoseStamped | list[PoseStamped]</code><br />Returns EE pose (defaults to end-effector). Use <code>.pose</code>.</p>
                </li>
                <li>
                    <p><code>plan(..., cartesian=True, max_step=..., cartesian_fraction_threshold=...) -&gt; JointTrajectory | None</code><br />Returns <code>None</code> if achieved fraction &lt; threshold.</p>
                </li>
                <li>
                    <p><code>execute(trajectory)</code> &mdash; executes a planned trajectory.</p>
                </li>
                <li>
                    <p><em>(Convenience)</em> <code>move_to_pose(..., cartesian=False/True, cartesian_max_step=..., cartesian_fraction_threshold=...)</code><br />Plans <strong>and executes</strong> in one call (internally calls <code>plan()</code> + <code>execute()</code>).</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<blockquote>
    <p><strong>Param name gotcha:</strong></p>
    <ul>
        <li>
            <p>In <code>plan(...)</code>, the interpolation step is named <strong><code>max_step</code></strong>.</p>
        </li>
        <li>
            <p>In <code>move_to_pose(...)</code>, it&rsquo;s named <strong><code>cartesian_max_step</code></strong>.<br />They are the same concept; mind the different parameter names.</p>
        </li>
    </ul>
</blockquote>
<p><strong>Two common patterns</strong></p>
<ul>
    <ul>
        <ol>
            <ol>
                <li>
                    <p><strong>Plan + execute</strong> (explicit control)</p>
                </li>
            </ol>
        </ol>
    </ul>
</ul>
<pre><code class="language-python">from copy import deepcopy

start_ps = self.moveit2.compute_fk()
start = start_ps.pose

# Example: +10 cm in X
p1 = deepcopy(start); p1.position.x += 0.10
traj = self.moveit2.plan(
    pose=p1,
    cartesian=True,
    max_step=0.005,                      # smaller step &rarr; easier IK
    cartesian_fraction_threshold=0.90,   # require &ge;90% of path to be valid
)
if traj is not None:
    self.moveit2.execute(traj)
    self.moveit2.wait_until_executed()
else:
    self.get_logger().warn("Cartesian planning failed (low fraction). Try smaller steps or adjust direction.")
</code></pre>
<ul>
    <ul>
        <ol>
            <ol start="2">
                <li>
                    <p><strong>One-shot</strong> (plan+execute together)</p>
                </li>
            </ol>
        </ol>
    </ul>
</ul>
<pre><code class="language-python"># Same target pose, but let move_to_pose do plan+execute internally
self.moveit2.move_to_pose(
    pose=p1,
    cartesian=True,
    cartesian_max_step=0.005,
    cartesian_fraction_threshold=0.90,
)
self.moveit2.wait_until_executed()
</code></pre>
<p><strong>Fraction meaning (how failure is decided)</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Internally, <code>plan(...)</code> uses <code>plan_async(...)</code> &rarr; <code>get_trajectory(...)</code>.</p>
                </li>
                <li>
                    <p>For Cartesian plans, <code>get_trajectory</code> compares <code>res.fraction</code> vs your <code>cartesian_fraction_threshold</code>; if fraction is lower, it <strong>returns <code>None</code></strong> (plan rejected).</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Tips</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Start with small translations (5&ndash;10 cm).</p>
                </li>
                <li>
                    <p>Keep orientation fixed initially.</p>
                </li>
                <li>
                    <p>If available, reduce interpolation step (<code>max_step</code> / <code>cartesian_max_step</code>) to improve IK continuity.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<h2>A.5 Planning scene: collision objects</h2>
<p><strong>When to use:</strong> make the planner aware of obstacles/fixtures.</p>
<p><strong>Core methods</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>add_collision_box(id, size, pose=None, position=None, quat_xyzw=None, frame_id=None, operation=ADD)</code></p>
                </li>
                <li>
                    <p><em>(Often handy)</em> <code>remove_collision_object(id)</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<blockquote>
    <p><strong>Safer to use named args</strong> to avoid misordering.</p>
</blockquote>
<p><strong>Typical flow (pseudocode):</strong></p>
<pre><code class="language-python">obj_id = "UNIQUE_ID"
self.moveit2.add_collision_box(
    id=obj_id,
    size=(sx, sy, sz),                # meters
    position=(X, Y, Z),               # meters, in frame_id
    quat_xyzw=(qx, qy, qz, qw),
    frame_id="FRAME",
)
time.sleep(1.0)  # let scene propagate
</code></pre>
<p><strong>Tips</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>frame_id</code> should be your planning frame (commonly the base link).</p>
                </li>
                <li>
                    <p>Make objects large enough to be visible but not impossible to route around.</p>
                </li>
                <li>
                    <p>If you grasp something, consider attaching it (out of scope here but same idea).</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<h2>A.6 Path orientation constraints (optional)</h2>
<p><strong>When to use:</strong> keep tool orientation within bounds during a move.</p>
<p><strong>Core method (pattern)</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>set_path_orientation_constraint(quat_xyzw, frame_id=None, target_link=None, tolerance=..., weight=1.0, parameterization=0)</code></p>
                    <ul>
                        <li>
                            <p><code>parameterization</code>: <code>0</code> Euler angles, <code>1</code> rotation vector</p>
                        </li>
                    </ul>
                </li>
                <li>
                    <p><code>clear_path_constraints()</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Important</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Constraints persist until cleared; restore defaults after constrained motion.</p>
                </li>
                <li>
                    <p>Tight tolerances reduce planning success; widen first, then tighten.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Pattern (pseudocode):</strong></p>
<pre><code class="language-python">self.moveit2.set_path_orientation_constraint(
    quat_xyzw=(qx, qy, qz, qw),
    frame_id="BASE_LINK",
    target_link="EE_LINK",
    tolerance=(roll_tol, pitch_tol, yaw_tol),  # or a single float
    weight=1.0,
    parameterization=0,
)
# ... issue your motion that must obey the constraint ...
self.moveit2.clear_path_constraints()
</code></pre>
<h2>A.7 Gripper interface</h2>
<p><strong>Purpose:</strong> high-level open/close control backed by a ROS 2 Action (e.g., <code>control_msgs/action/GripperCommand</code>).</p>
<p><strong>Initialization fields (robot-specific&mdash;discover these on your system)</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>gripper_joint_names=[PRIMARY_ACTUATED_JOINT]</code></p>
                </li>
                <li>
                    <p><code>open_gripper_joint_positions=[OPEN_TARGET]</code></p>
                </li>
                <li>
                    <p><code>closed_gripper_joint_positions=[CLOSE_TARGET]</code></p>
                </li>
                <li>
                    <p><code>gripper_group_name="YOUR_GRIPPER_GROUP"</code></p>
                </li>
                <li>
                    <p><code>gripper_command_action_name="/PATH/TO/gripper_cmd"</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Usage (pseudocode):</strong></p>
<pre><code class="language-python">self.gripper.open()
self.gripper.wait_until_executed()

self.gripper.close()
self.gripper.wait_until_executed()
</code></pre>
<p><strong>How to discover values</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>List actions: <code>ros2 action list | grep -i gripp</code></p>
                </li>
                <li>
                    <p>Inspect action type: <code>ros2 interface show control_msgs/action/GripperCommand</code></p>
                </li>
                <li>
                    <p>Confirm group &amp; joint names in RViz (MotionPlanning &rarr; Groups/Joints) or SRDF.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Gotchas</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Many grippers use mimic joints; you command only the <strong>primary</strong> actuator.</p>
                </li>
                <li>
                    <p>If nothing moves, verify action server name and that the gripper controller is <strong>active</strong>.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<h2>A.8 Quick diagnostics + best practices</h2>
<p><strong>RViz visualization</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Displays &rarr; MotionPlanning &rarr; Planned Path: enable <em>Show Trail</em>, set a visible line width.</p>
                </li>
                <li>
                    <p>Scene visibility: enable <em>PlanningScene</em> / <em>Collision</em> displays and set alpha (0.3&ndash;0.6).</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Sanity checks (common failures)</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p>Wrong group or frames: planning &ldquo;succeeds&rdquo; but execution fails/does nothing.</p>
                </li>
                <li>
                    <p>Self-collision/limits: joint goals outside bounds or paths passing through the robot.</p>
                </li>
                <li>
                    <p>Missing controllers: plan exists but execution never starts&mdash;check controller manager logs.</p>
                </li>
                <li>
                    <p>Stale scene: obstacles not added &rarr; &ldquo;valid&rdquo; path collides in reality.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<h2>A.9 Signature cheat-sheet (summary)</h2>
<p><strong>Joint goals</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>move_to_configuration(joint_positions: list[float], joint_names: list[str] = None, tolerance=..., weight=...) -&gt; None</code></p>
                </li>
                <li>
                    <p><code>wait_until_executed() -&gt; None</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Cartesian</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>compute_fk(joint_state=None, fk_link_names=None) -&gt; PoseStamped | list[PoseStamped]</code></p>
                </li>
                <li>
                    <p><code>plan(pose|position+quat_xyzw|joint_positions, frame_id=None, target_link=None, cartesian=True/False, max_step=..., cartesian_fraction_threshold=...) -&gt; JointTrajectory | None</code></p>
                </li>
                <li>
                    <p><code>execute(trajectory) -&gt; None</code></p>
                </li>
                <li>
                    <p><code>move_to_pose(pose|position+quat_xyzw, frame_id=None, target_link=None, cartesian=False/True, cartesian_max_step=..., cartesian_fraction_threshold=...) -&gt; None</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Scene</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>add_collision_box(id: str, size: tuple[3], pose: Pose|PoseStamped = None, position: tuple[3] = None, quat_xyzw: tuple[4] = None, frame_id: str = None, operation=CollisionObject.ADD) -&gt; None</code></p>
                </li>
                <li>
                    <p><code>(optional) remove_collision_object(id: str) -&gt; None</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Constraints</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>set_path_orientation_constraint(quat_xyzw: tuple[4], frame_id: str = None, target_link: str = None, tolerance: float|tuple[3] = 0.001, weight: float = 1.0, parameterization: int = 0) -&gt; None</code></p>
                </li>
                <li>
                    <p><code>clear_path_constraints() -&gt; None</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Gripper</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>open() -&gt; None</code></p>
                </li>
                <li>
                    <p><code>close() -&gt; None</code></p>
                </li>
                <li>
                    <p><code>wait_until_executed() -&gt; None</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<p><strong>Planner &amp; execution tuning (properties)</strong></p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><code>max_velocity: float</code> (0&ndash;1)</p>
                </li>
                <li>
                    <p><code>max_acceleration: float</code> (0&ndash;1)</p>
                </li>
                <li>
                    <p><code>num_planning_attempts: int</code></p>
                </li>
                <li>
                    <p><code>allowed_planning_time: float</code></p>
                </li>
                <li>
                    <p><code>planner_id: str</code></p>
                </li>
                <li>
                    <p><code>pipeline_id: str</code></p>
                </li>
                <li>
                    <p><em>(Cartesian helpers)</em> <code>cartesian_avoid_collisions: bool</code>, <code>cartesian_jump_threshold: float</code>, <code>cartesian_prismatic_jump_threshold: float</code>, <code>cartesian_revolute_jump_threshold: float</code></p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<blockquote>
    <p><strong>Remember:</strong> this appendix explains <strong>how</strong> to use the APIs and what to watch for. It intentionally avoids robot-specific numbers and names&mdash;pull those from <strong>your</strong> RViz/TF/driver so your solution reflects your own setup.</p>
</blockquote>
<h1>Appendix B &mdash; ROS 2 CLI cheat sheet</h1>
<p>Use these commands to <strong>inspect</strong> your system while you work. They help you find joint names, frames, groups, actions, and controller status without guessing. Names may differ on your setup&mdash;treat the examples as hints.</p>
<hr />
<h2>1) Nodes, topics, actions (what&rsquo;s running?)</h2>
<p><strong>List nodes</strong></p>
<pre><code class="language-bash">ros2 node list
</code></pre>
<p><strong>Inspect a node (params, pubs/subs, services, actions)</strong></p>
<pre><code class="language-bash">ros2 node info /move_group
ros2 node info /robot_state_publisher
</code></pre>
<p><strong>List topics / actions</strong></p>
<pre><code class="language-bash">ros2 topic list
ros2 action list
</code></pre>
<p><strong>See a topic&rsquo;s type &amp; publishers/subscribers</strong></p>
<pre><code class="language-bash">ros2 topic info /joint_states
ros2 topic info /display_planned_path
</code></pre>
<p><strong>Peek one message</strong></p>
<pre><code class="language-bash">ros2 topic echo /joint_states --once
</code></pre>
<p><strong>Show an interface (message/action definition)</strong></p>
<pre><code class="language-bash">ros2 interface show sensor_msgs/msg/JointState
ros2 interface show geometry_msgs/msg/Pose
ros2 interface show control_msgs/action/GripperCommand
</code></pre>
<hr />
<h2>2) URDF &amp; SRDF (robot &amp; planning model)</h2>
<p><strong>URDF (robot model) &mdash; usually a parameter of <code>robot_state_publisher</code></strong></p>
<pre><code class="language-bash">ros2 param get /robot_state_publisher robot_description &gt; urdf.xml
</code></pre>
<p><strong>SRDF (MoveIt planning groups, kinematic chains, etc.) &mdash; usually on <code>move_group</code></strong></p>
<pre><code class="language-bash">ros2 param get /move_group robot_description_semantic &gt; srdf.xml
</code></pre>
<p>Open these files in your editor to confirm:</p>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><strong>Joint names &amp; order</strong> (SRDF matches the joint order your code must use)</p>
                </li>
                <li>
                    <p><strong>Planning groups</strong> (e.g., <code>arm</code>, <code>gripper</code>)</p>
                </li>
                <li>
                    <p><strong>End-effector links</strong> and tip frames</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<blockquote>
    <p>Tip: If a param isn&rsquo;t found, run <code>ros2 node list</code> and try the correct node name/namespace for your MoveIt stack.</p>
</blockquote>
<hr />
<h2>3) Joints &amp; states (live values)</h2>
<p><strong>Watch joint positions stream</strong></p>
<pre><code class="language-bash">ros2 topic echo /joint_states
</code></pre>
<p><strong>Check rate / liveness</strong></p>
<pre><code class="language-bash">ros2 topic hz /joint_states
</code></pre>
<p>Use this to verify the names you see in SRDF actually appear in <code>/joint_states</code> and to confirm the sim is publishing.</p>
<hr />
<h2>4) TF frames (planning frame, EE frame)</h2>
<p><strong>Echo a transform (continuous)</strong></p>
<pre><code class="language-bash">ros2 run tf2_ros tf2_echo base_link end_effector_link
</code></pre>
<p><strong>Generate a frames diagram (if available in your image)</strong></p>
<pre><code class="language-bash">ros2 run tf2_tools view_frames
# produces frames.pdf; open it to inspect the TF tree
</code></pre>
<blockquote>
    <p>If <code>tf2_tools</code> isn&rsquo;t available, rely on RViz&rsquo;s <strong>TF</strong> display and <code>tf2_echo</code>.</p>
</blockquote>
<hr />
<h2>5) MoveIt-specific signals (planned paths, planning scene)</h2>
<p><strong>Planned paths</strong></p>
<pre><code class="language-bash">ros2 topic list | grep display
ros2 topic info /display_planned_path
ros2 topic echo /display_planned_path --once
</code></pre>
<p><strong>Planning scene stream (verbose but useful to confirm scene updates)</strong></p>
<pre><code class="language-bash">ros2 topic info /monitored_planning_scene
# (You can echo once, but it&rsquo;s large XML/msgs)
</code></pre>
<hr />
<h2>6) Controllers (ros2_control) &mdash; is execution possible?</h2>
<p><strong>List controllers</strong></p>
<pre><code class="language-bash">ros2 control list_controllers
</code></pre>
<p>You should see an arm trajectory controller (e.g., <code>follow_joint_trajectory</code>) <strong>active</strong>, and a gripper controller.</p>
<p><strong>Hardware interfaces</strong></p>
<pre><code class="language-bash">ros2 control list_hardware_interfaces
</code></pre>
<blockquote>
    <p>If execution never starts, a controller may be <strong>inactive</strong> or mismatched with your joint names.</p>
</blockquote>
<hr />
<h2>7) Gripper action (discover and validate)</h2>
<p><strong>Find the action name</strong></p>
<pre><code class="language-bash">ros2 action list | grep gripper
</code></pre>
<p><strong>Inspect the gripper action server</strong></p>
<pre><code class="language-bash">ros2 action info /GEN3_GRIPPER_PATH/gripper_cmd
ros2 interface show control_msgs/action/GripperCommand
</code></pre>
<p>You should see goal fields (e.g., position/effort) and feedback/result. This confirms the <strong>Action</strong> your <code>GripperInterface</code> must target.</p>
<hr />
<h2>8) Parameters (quick checks)</h2>
<p><strong>List parameters on a node</strong></p>
<pre><code class="language-bash">ros2 param list /move_group
</code></pre>
<p><strong>Get a specific parameter</strong></p>
<pre><code class="language-bash">ros2 param get /move_group planning_pipelines
ros2 param get /move_group robot_description_semantic
</code></pre>
<hr />
<h2>9) Sanity &amp; environment</h2>
<p><strong>Verify package visibility</strong></p>
<pre><code class="language-bash">ros2 pkg list | grep lab05_moveit
</code></pre>
<p><strong>Check your ROS domain (must match across terminals)</strong></p>
<pre><code class="language-bash">echo $ROS_DOMAIN_ID
</code></pre>
<p><strong>Run RViz with a saved config</strong></p>
<pre><code class="language-bash">ros2 run rviz2 rviz2 -d /path/to/lab5.rviz
</code></pre>
<hr />
<h2>10) Practical &ldquo;when X breaks, try Y&rdquo;</h2>
<ul>
    <ul>
        <ol>
            <ul>
                <li>
                    <p><strong>No motion on execute:</strong><br /><code>ros2 control list_controllers</code> &rarr; controller active?<br /><code>ros2 node info /move_group</code> &rarr; is it running?<br />RViz Planning panel &rarr; correct <strong>Planning Group</strong>?</p>
                </li>
                <li>
                    <p><strong>Named target fails:</strong><br />Dump <strong>SRDF</strong> and verify the named pose exists; otherwise use explicit joint arrays.</p>
                </li>
                <li>
                    <p><strong>Cartesian path fraction low:</strong><br /><code>ros2 topic echo /monitored_planning_scene --once</code> to ensure your obstacle is present; then reduce waypoint spacing or keep orientation fixed.</p>
                </li>
                <li>
                    <p><strong>Gripper doesn&rsquo;t move:</strong><br />Confirm action server name with <code>ros2 action list</code>; echo one result with <code>ros2 action info &hellip;</code>; check logs on the controller node.</p>
                </li>
            </ul>
        </ol>
    </ul>
</ul>
<hr />
<h3>Quick copy block</h3>
<pre><code class="language-bash"># Models
ros2 param get /robot_state_publisher robot_description &gt; urdf.xml
ros2 param get /move_group robot_description_semantic &gt; srdf.xml

# Live state
ros2 topic echo /joint_states --once
ros2 run tf2_ros tf2_echo base_link end_effector_link

# MoveIt signals
ros2 topic info /display_planned_path
ros2 topic info /monitored_planning_scene

# Controllers
ros2 control list_controllers
ros2 control list_hardware_interfaces

# Gripper action
ros2 action list | grep gripper
ros2 action info /GEN3_GRIPPER_PATH/gripper_cmd
ros2 interface show control_msgs/action/GripperCommand
</code></pre>
<p>Use this sheet alongside Appendix A so you can <strong>discover</strong> the exact names/frames/groups for your system and wire your code correctly without guesswork.</p>
<p>&nbsp;</p>

</div>
