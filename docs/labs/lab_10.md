---
title: "Lab 10: Real TurtleBot 4 Deployment"
---

# Lab 10: Real TurtleBot 4 Deployment

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#overview">Overview: From Explorer to Strategist</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#roles">From Simulation to Reality: Safety &amp; Professional Conduct</a></li>
        <li><a href="#background">Conceptual Background: Engineering a Smarter Robot</a></li>
        <li><a href="#setup">Part 1: Real TurtleBot&nbsp;4 Bring-Up (SLAM + Nav2 + RViz)</a></li>
        <li><a href="#procedure">Part 2: Engineering the Intelligent Explorer (A*)</a></li>
        <li><a href="#run">Part 2.5: Deployment &amp; Map Saving</a></li>
        <li><a href="#analysis">Part 3: Analysis &amp; Discussion</a></li>
        <li><a href="#troubleshooting">Quick Troubleshooting</a></li>
        <li><a href="#references">References &amp; Further Reading</a></li>
    </ol>
</nav>
<section id="overview">
    <h2>1. Overview: From Explorer to Strategist</h2>
    <p>In previous labs, you built an autonomous explorer in the clean, predictable world of simulation. Today, you bridge the gap to reality. Simulation is where algorithms are born, but the physical world is where they are truly tested. You will deploy your code on <strong>physical TurtleBot 4 robots</strong>, where perfect odometry is a myth, lighting conditions change, and walls are not always perfectly straight.</p>
    <p>Your core task is to upgrade your robot's "Brain." You will replace the naive "Nearest Frontier" logic with an <strong>Information Gain Strategist</strong>.</p>
    <p>You will be provided with a sophisticated navigation node that includes <strong>A* Pathfinding</strong>, <strong>Frontier Clustering</strong>, and <strong>Stuck Detection</strong>. However, the code is currently "silent." Your job is to <strong>instrument the code</strong> with logging to visualize its decision-making process, ensuring it balances the <em>Cost of Travel</em> against the <em>Reward of Discovery</em>.</p>
    <blockquote style="border-left: 4px solid #005a9c; padding-left: 1em; color: #555;"><strong>The System Stack</strong><br /><strong>Hardware:</strong> Lidar &amp; Encoders &rarr; <strong>SLAM:</strong> The Map &rarr; <strong>Your Node:</strong> The Strategy (Efficiency Score) &rarr; <strong>Nav2:</strong> The Pilot (Motion Planning).</blockquote>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>Upon successful completion of this lab, you will have moved beyond simply "running" code to "validating" it. You will demonstrate the ability to:</p>
    <ul>
        <li><strong>Architect</strong> a complete robotics software stack on physical hardware.</li>
        <li><strong>Analyze</strong> an A* implementation to understand how grid maps translate to travel costs.</li>
        <li><strong>Instrument</strong> a robot control node to log real-time decision metrics (Efficiency Scores).</li>
        <li><strong>Validate</strong> system performance by interpreting logs to explain why the robot chose specific targets.</li>
        <li><strong>Debug</strong> physical navigation issues using Stuck Detection logic and Blacklisting.</li>
    </ul>
</section>
<section id="roles">
    <h2>3. From Simulation to Reality: Safety &amp; Professional Conduct</h2>
    <p>Working with physical hardware carries a greater responsibility than simulation. The following rules are the habits of professional engineers.</p>
    <h3>Rules of Engagement</h3>
    <ul>
        <li><strong>Situational Awareness:</strong> Always know where the robot is going. Keep the area clear of backpacks and cables.</li>
        <li><strong>Hands Off:</strong> Do not push or lift the robot while it is mapping. This corrupts the SLAM estimate (Odometry vs. Map), forcing a full system restart. If a collision is imminent, use the E-Stop or Ctrl+C.</li>
        <li><strong>Teamwork:</strong> One person drives/codes, one person monitors RViz data, one person watches the physical robot. Rotate roles.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="background">
    <h2>4. Conceptual Background: Engineering a Smarter Robot</h2>
    <p>To understand the code you are working with, we must analyze the failure mode of the "Naive" explorer and the solution provided by "Information Gain."</p>
    <h3>The Flaw in the "Nearest Frontier" Heuristic</h3>
    <p>Imagine your robot is in a hallway. It identifies two unexplored frontiers:</p>
    <ul>
        <li><strong>Frontier A (The Trap):</strong> Located in the adjacent room, <strong>1 meter away</strong> through a wall.</li>
        <li><strong>Frontier B (The Goal):</strong> Located down the hall, <strong>3 meters away</strong> in clear space.</li>
    </ul>
    <p>A "Nearest Neighbor" algorithm calculates \( 1m &lt; 3m \) and chooses <strong>Frontier A</strong>. The robot then attempts to drive through the wall.</p>
    <h3>The Solution: Efficiency Scoring</h3>
    <p>The code provided uses two metrics to make a decision:</p>
    <ol>
        <li><strong>The Cost (A*):</strong> The true travel distance, respecting walls. A* will calculate that Frontier A (through the wall) is actually a 20-meter path, while Frontier B is 3 meters.</li>
        <li><strong>The Reward (Cluster Size):</strong> How much map will we reveal? A tiny gap isn't worth a long drive. A massive open room is.</li>
    </ol>
    <p>The robot minimizes an <strong>Efficiency Score</strong>: $$ \text{Score} = \frac{\text{Cost (A* Distance)}}{\text{Reward (Frontier Size)}} $$</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="setup">
    <h2>Part 1: Establishing the Mind-Body Connection</h2>
    <p>Before a pilot takes off, they run a pre-flight checklist. Before a roboticist deploys code, they run a "Bring-Up."</p>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Communal Lab PC Protocol (Read Carefully)</strong>
        <p>You are working on shared equipment today, not your personal VM.</p>
        <ul>
            <li><strong>No SSH Keys:</strong> Do not generate or copy personal SSH keys to these machines. It is a security risk.</li>
            <li><strong>Submission Strategy:</strong> You will write your code locally. To submit, log into GitLab in the <strong>Web Browser</strong>, navigate to your repository, and use the <strong>"Upload File"</strong> or <strong>"Web IDE"</strong> button to upload your <code>auto_explore.py</code> and maps.</li>
            <li><strong>Data Safety:</strong> The Docker command below has been updated to mount a local folder. Ensure you save your python file in the mounted directory, or it will vanish when the container closes.</li>
        </ul>
    </div>
    <p>In this lab, we are using a <strong>Distributed Architecture</strong>.</p>
    <ul>
        <li><strong>The Body (Server):</strong> The physical TurtleBot 4 handles the drivers (LiDAR, Motors) and publishes raw sensor data.</li>
        <li><strong>The Brain (Client):</strong> Your Lab PC runs the heavy computation (SLAM, Nav2, Your Efficiency Node).</li>
    </ul>
    <p>Your goal in Part 1 is to establish the "Nervous System" (Wi-Fi Network) that connects them.</p>
    <h3>Step 1.1: Prepare Your Terminal Workspace</h3>
    <p>Create a folder on the Lab PC to store your work safely. Open a terminal and run:</p>
    <pre><code class="language-bash">mkdir -p ~/lab10_work/src</code></pre>
    <p>Now, open a terminal manager (like <code>terminator</code>). A multi-pane layout is standard operational procedure for monitoring distributed systems.</p>
    <ul>
        <li><strong>Pane A (Mapping):</strong> Runs <code>slam_toolbox</code> to build the world model.</li>
        <li><strong>Pane B (Navigation):</strong> Runs <code>nav2</code> to plan paths through that model.</li>
        <li><strong>Pane C (Command):</strong> Runs your custom node and health checks.</li>
    </ul>
    <h3>Step 1.2: Verify the Network (The Nervous System)</h3>
    <p>First, define your target. Every robot has a unique IP address and a unique frequency channel (ROS Domain ID) labeled on its chassis. The IP address belongs to the TurtleBot 4 Raspberry Pi, not the Create 3 base.</p>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px;"><strong>CRITICAL:</strong> You must run these <code>export</code> commands in <strong>EVERY</strong> new terminal pane you open. Environment variables do not transfer between tabs.</div>
    <pre><code class="language-bash"># --- CONFIGURATION (Run in every new terminal) ---

export TB4_IP=192.168.1.XXX    # REPLACE with your robot's Raspberry Pi IP
export ROS_DOMAIN_ID=XX        # REPLACE with your robot's Domain ID (printed on the chassis)

# Check the physical link

ping -c 4 "$TB4_IP"
</code></pre>
    <blockquote style="border-left: 4px solid #d9534f; padding-left: 1em; color: #555;"><strong>Stop: Hard Down Check</strong><br />If <code>ping</code> returns <code>Destination Host Unreachable</code> or <code>100% packet loss</code>, <strong>do not proceed.</strong> You have no nervous system. Check your Wi-Fi connection and IP address.</blockquote>
    <h3>Step 1.3: Start the Container &amp; Configure Discovery</h3>
    <p>We use a Docker container to ensure all dependencies are correct. We configure ROS 2 (FastDDS) to use the TurtleBot 4's Discovery Server so the workstation can find the robot cleanly without flooding the university Wi-Fi with discovery traffic.</p>
    <p><strong>Copy-paste this block into Pane A to launch the environment.</strong><br /><em>Note the <code>-v</code> flag: This maps your local folder to the container so your code is saved to the Lab PC, not lost inside the container.</em></p>
    <pre><code class="language-bash"># 1. Export Discovery Settings (FastDDS + Discovery Server)

# TurtleBot 4 Jazzy + I.0.0.FastDDS firmware use FastDDS on all sides
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# The Raspberry Pi runs the FastDDS Discovery Server on port 11811
export ROS_DISCOVERY_SERVER=${TB4_IP}:11811

# Optional but recommended: match the namespace configured with turtlebot4-setup
# Example: if this is robot with Domain ID 2, use /tb4_2
export TB4_NAMESPACE=/tb4_${ROS_DOMAIN_ID}

# 2. Run the Container (Jazzy TB4 Workstation)

docker run --rm -it --name tb4_nav_jazzy \
  --net=host \
  --privileged \
  -e DISPLAY="$DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e ROS_DOMAIN_ID \
  -e RMW_IMPLEMENTATION \
  -e ROS_DISCOVERY_SERVER \
  -e TB4_NAMESPACE \
  -v ~/workspaces:/root/workspaces \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:tb4-jazzy-lab10-latest
</code></pre>
    <ul>
        <ul>
            <li><strong><code>--net=host</code>:</strong> Bypasses Docker's network isolation. This allows the container to use the Lab PC's real network card to talk to the robot and the Discovery Server.</li>
            <li><strong><code>-v ~/workspaces:/root/workspaces</code>:</strong> This acts as a "bridge." Any file you save into <code>/root/workspaces</code> inside the container will appear in <code>~/workspaces</code> on the Lab PC, ensuring your code is safe.</li>
        </ul>
    </ul>
    <h3>Step 1.4: Launch SLAM &amp; Nav2 (The Brain)</h3>
    <p>Inside the container, you will launch the two hemispheres of the robot's brain using the <code>turtlebot4_navigation</code> package. These launch files are configured specifically for TurtleBot&nbsp;4 and handle frames, topics, and parameters for you.</p>
    <pre><code class="language-bash"># Optional but recommended: namespace for this robot
# Match this to the value you set with `turtlebot4-setup` on the robot.
# Example: /tb4_02 or /robot1
export TB4_NAMESPACE=/tb4_${ROS_DOMAIN_ID}

# --- PANE A: The Cartographer (SLAM) ---
# Listens to /scan + /odom &rarr; Builds /map
ros2 launch turtlebot4_navigation slam.launch.py \
  ${TB4_NAMESPACE:+namespace:=${TB4_NAMESPACE}}

# --- PANE B: The Pilot (Nav2) ---
# Listens to /map + /goal_pose &rarr; Computes /cmd_vel
# (Remember to run the Step 1.2 exports first!)
ros2 launch turtlebot4_navigation nav2.launch.py \
  ${TB4_NAMESPACE:+namespace:=${TB4_NAMESPACE}}</code></pre>
    <blockquote style="border-left: 4px solid #005a9c; padding-left: 1em; color: #555;"><strong>Why not use <code>slam_toolbox</code> + <code>nav2_bringup</code> directly?</strong><br />Those generic launch files do not know about TurtleBot&nbsp;4's frames, topics, or namespacing. Using <code>turtlebot4_navigation</code> ensures the correct transforms, topic remaps, and Nav2 configuration are loaded for the real robot (and keeps you out of TF debugging purgatory).</blockquote>
    <h3>Step 1.5: RViz Pre-Flight Checklist (Go / No-Go)</h3>
    <p>Launch the visualization tool in Pane C (remember your exports!):</p>
    <pre><code class="language-bash">ros2 launch turtlebot4_viz view_navigation.launch.py</code></pre>
    <p><strong>You are ready to fly ONLY if all items below are checked:</strong></p>
    <ul>
        <ul>
            <ul>
                <li>[ ] <strong>Time Sync:</strong> The "Last Received Message" time in RViz is less than 1 second ago. (If it says "X seconds ago" and X is growing, your PC clock and Robot clock are out of sync. Restart Docker).</li>
                <li>[ ] <strong>Transforms (TF):</strong> You see a connected tree: <code>map</code> &rarr; <code>odom</code> &rarr; <code>base_link</code>. No red errors.</li>
                <li>[ ] <strong>LaserScan:</strong> You see red dots in RViz matching the walls of your room.</li>
                <li>[ ] <strong>Global Costmap:</strong> As you teleop the robot slightly, white/black pixels appear in the <code>map</code> display.</li>
                <li>[ ] <strong>Local Costmap:</strong> You see a small colored box (the rolling window) around the robot. This indicates Nav2 is active and ready to plan.</li>
            </ul>
        </ul>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>Part 2: Programming the Intelligent Explorer</h2>
    <p>In previous labs, your robot likely drove blindly or struggled to choose between multiple open paths. Today, we are giving the robot a significant "brain upgrade." We are moving from simple geometry to <strong>Information Gain Navigation</strong>.</p>
    <p>Instead of just finding the <em>closest</em> unknown area (Frontier), your robot will now calculate an <strong>Efficiency Score</strong> for every potential target.</p>
    <div style="background: #f4f4f4; padding: 15px; border-left: 5px solid #337ab7; margin: 20px 0;">
        <p style="font-size: 1.2em; margin-bottom: 5px;"><strong>The Efficiency Equation:</strong></p>
        <p>$$ \text{Score} = \frac{\text{Cost (A* Distance)}}{\text{Reward (Frontier Size)}} $$</p>
        <p><em>We want to minimize this score. We prefer short trips (low Cost) that reveal huge amounts of the map (high Reward).</em></p>
    </div>
    <h3>Step 2.1: Package Setup</h3>
    <p>Create your package if you haven't already:</p>
    <pre><code class="language-bash">cd /root/workspaces/[netid]_robotics_fall2025/lab10/ros2_ws/src
ros2 pkg create --build-type ament_python turtlebot4_nav --dependencies rclpy geometry_msgs nav_msgs</code></pre>
    <p>Create a file named <code>turtlebot4_nav/turtlebot4_nav/auto_explore.py</code>.</p>
    <h3>Step 2.2: The Architecture of Autonomy</h3>
    <p>We will build this node piece by piece. This helps us understand the "Sense-Plan-Act" loop the robot performs.</p>
    <p><strong>Important:</strong> As you paste these blocks, you will see comments labeled <code># TODO: LOGGING</code>. The code works functionally, but it is silent. You must add <code>self.get_logger().info(...)</code> or <code>warn(...)</code> statements to visualize the robot's "thought process" in the terminal.</p>
    <h4>1. Imports and Configuration</h4>
    <p>First, we set up our inputs. We define constants for the map interpretation&mdash;specifically, what pixel value constitutes a "wall" (50). We also set up our "Tuning Knobs" as ROS parameters. These allow us to tweak behavior (like how long to wait before deciding we are stuck) without recompiling code.</p>
    <p><em>Copy this into the top of your file:</em></p>
    <pre><code class="language-python">import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Odometry
from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Directions, TurtleBot4Navigator

import numpy as np
import math
import heapq
import time
from collections import deque

# Constants for map analysis
OCCUPANCY_THRESHOLD = 50 # Value above which a cell is considered an obstacle
UNKNOWN_VALUE = -1 # Value representing unexplored space

class AutonomousExplorer(Node):
    def __init__(self):
        super().__init__('autonomous_explorer')

        # Configuration Parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                ('min_frontier_size', 10), # Minimum size of a cluster to count as a target
                ('tick_rate', 1.0),        # How often to run the control loop (Hz)
                ('stuck_timeout', 10.0),   # How long to wait before declaring "stuck"
                ('stuck_min_dist', 0.2),   # Min distance to move to reset the stuck timer
                ('blacklist_radius', 0.5)  # Radius to ignore around failed targets
            ]
        )

        self.min_frontier_size = self.get_parameter('min_frontier_size').value
        self.tick_rate = self.get_parameter('tick_rate').value
        self.stuck_timeout = self.get_parameter('stuck_timeout').value
        self.stuck_min_dist = self.get_parameter('stuck_min_dist').value
        self.blacklist_radius = self.get_parameter('blacklist_radius').value

        # State Variables
        self.map_data = None
        self.odom_data = None
        self.is_navigating = False

        # Stuck Detection &amp; History
        self.nav_start_time = 0
        self.start_pose = (0, 0)
        self.current_target = None
        self.blacklist = []

        # Initialize Navigation
        self.navigator = TurtleBot4Navigator()
        if self.navigator.getDockedStatus():
            self.navigator.undock()

        # ROS Communication
        self.create_subscription(OccupancyGrid, 'map', self.map_callback, 10)
        self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        # Main Loop Timer
        self.timer = self.create_timer(self.tick_rate, self.control_loop)

    # --------------------------------------------------------------------------
    # CALLBACKS
    # --------------------------------------------------------------------------

    def map_callback(self, msg):
        self.map_data = msg

    def odom_callback(self, msg):
        self.odom_data = msg</code></pre>
    <h4>2. The Bridge: Grid vs. World</h4>
    <p>The robot lives in the physical world (Meters), but the map lives in computer memory (Grid Indices). We need robust helpers to translate between the two. We also need a way to measure distance.</p>
    <p><em>Add these methods inside your class:</em></p>
    <pre><code class="language-python">    # --------------------------------------------------------------------------
    # COORDINATE TRANSFORMS
    # --------------------------------------------------------------------------

    def world_to_grid(self, x, y):
        """Converts real-world coordinates (meters) to map grid indices (row, col)."""
        res = self.map_data.info.resolution
        origin_x = self.map_data.info.origin.position.x
        origin_y = self.map_data.info.origin.position.y

        col = int((x - origin_x) / res)
        row = int((y - origin_y) / res)
        return row, col

    def grid_to_world(self, row, col):
        """Converts map grid indices (row, col) to real-world coordinates (meters)."""
        res = self.map_data.info.resolution
        origin_x = self.map_data.info.origin.position.x
        origin_y = self.map_data.info.origin.position.y

        x = (col * res) + origin_x + (res / 2.0)
        y = (row * res) + origin_y + (res / 2.0)
        return x, y

    def get_distance(self, p1, p2):
        """Euclidean distance between two points (x, y)."""
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])</code></pre>
    <h4>3. Pathfinding (The "A*" Algorithm)</h4>
    <p>To calculate the "Cost" in our efficiency equation, we cannot just use a straight line (Euclidean distance) because walls exist. We use <strong>A* (A-Star) Search</strong>.</p>
    <p>We also include a BFS search called <code>find_nearest_valid_point</code>. Often, the math says the center of a frontier is inside a wall (think of a donut shape). This function snaps the target to the nearest <em>reachable</em> pixel.</p>
    <p><em>Add these navigation algorithms:</em></p>
    <pre><code class="language-python">    # --------------------------------------------------------------------------
    # NAVIGATION ALGORITHMS
    # --------------------------------------------------------------------------

    def heuristic(self, a, b):
        """Manhattan distance heuristic for A*."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_nearest_valid_point(self, grid, center, max_radius=5):
        """
        Breadth-First Search (BFS) to find the nearest 'Free' cell (0)
        if the specific target is inside an obstacle or unknown space.
        """
        rows, cols = grid.shape

        # Check if center is already valid
        if 0 &lt;= center[0] &lt; rows and 0 &lt;= center[1] &lt; cols:
            if grid[center[0], center[1]] == 0:
                return center

        queue = deque([center])
        visited = {center}
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Up, Down, Left, Right

        while queue:
            r, c = queue.popleft()

            # Found a valid point
            if grid[r, c] == 0:
                return (r, c)

            # Stop searching if we go too far
            if abs(r - center[0]) &gt; max_radius or abs(c - center[1]) &gt; max_radius:
                continue

            for dr, dc in deltas:
                nr, nc = r + dr, c + dc # Neighbor Row, Neighbor Col
                if (0 &lt;= nr &lt; rows and 0 &lt;= nc &lt; cols and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return None

    def a_star_search(self, grid, start, goal):
        """
        Standard A* Pathfinding. Returns the cost (length) of the path.
        Returns infinity if no path exists.
        """
        rows, cols = grid.shape

        # If start is in a wall, we can't plan
        if grid[start[0], start[1]] &gt; OCCUPANCY_THRESHOLD:
            return float('inf')

        open_set = []
        heapq.heappush(open_set, (0, 0, start)) # (Priority, Cost, Node)
        g_score = {start: 0}
        movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while open_set:
            _, current_g, current = heapq.heappop(open_set)

            if current == goal:
                return current_g

            for dr, dc in movements:
                neighbor = (current[0] + dr, current[1] + dc)

                if 0 &lt;= neighbor[0] &lt; rows and 0 &lt;= neighbor[1] &lt; cols:
                    cell_value = grid[neighbor[0], neighbor[1]]

                    # Treat Walls (&gt;50) as impassable
                    if cell_value &gt; OCCUPANCY_THRESHOLD:
                        continue

                    tentative_g = current_g + 1
                    if tentative_g &lt; g_score.get(neighbor, float('inf')):
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + self.heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score, tentative_g, neighbor))

        return float('inf')</code></pre>
    <h4>4. Safety Mechanisms</h4>
    <p>A robust robot anticipates failure.</p>
    <ul>
        <li><strong>Stuck Condition:</strong> If the robot tries to move but the odometer doesn't change (e.g., wheel slip), we must detect this to avoid burning out motors.</li>
        <li><strong>Blacklisting:</strong> If a target was unreachable or caused us to get stuck, we add it to a "Blacklist" so we don't obsessively retry the same bad idea.</li>
    </ul>
    <p><em>Add these safety checks:</em></p>
    <pre><code class="language-python">    # --------------------------------------------------------------------------
    # SAFETY CHECKS
    # --------------------------------------------------------------------------

    def check_stuck_condition(self, current_x, current_y):
        """Returns True if the robot hasn't moved significantly in 'stuck_timeout' seconds."""
        elapsed = time.time() - self.nav_start_time
        if elapsed &gt; self.stuck_timeout:
            dist_moved = self.get_distance((current_x, current_y), self.start_pose)
            if dist_moved &lt; self.stuck_min_dist:
                # TODO: LOGGING - Warn that the robot is stuck (include distance moved)
                return True
        else:
            # Reset timer if we moved enough
            self.nav_start_time = time.time()
            self.start_pose = (current_x, current_y)
        return False

    def is_blacklisted(self, target_x, target_y):
        """Checks if a coordinate is too close to a previously failed target."""
        for bx, by in self.blacklist:
            if self.get_distance((target_x, target_y), (bx, by)) &lt; self.blacklist_radius:
                return True
        return False</code></pre>
    <h4>5. The Strategy (Frontier Detection &amp; Selection)</h4>
    <p>This is the core intelligence. <br /><strong>1. Detect:</strong> We look for edges where "Free Space" meets "Unknown Space." We group these pixels into clusters. <br /><strong>2. Decide:</strong> We loop through every cluster and apply the Efficiency Equation (Cost / Reward). We also check the blacklist here.</p>
    <p><em>Add the strategic logic. <strong>Note the heavy logging requirements here.</strong></em></p>
    <pre><code class="language-python">    # --------------------------------------------------------------------------
    # FRONTIER DETECTION
    # --------------------------------------------------------------------------

    def get_frontier_clusters(self, grid):
        """
        Identifies the boundaries between 'Free' space and 'Unknown' space.
        Returns a list of clusters (groups of frontier points).
        """
        free = (grid == 0)
        unknown = (grid == UNKNOWN_VALUE)

        # Boolean masking to find edges:
        # A pixel is a frontier if it is Free, but a neighbor is Unknown.
        mask = np.zeros_like(grid, dtype=bool)
        mask[:, :-1] |= (free[:, :-1] &amp; unknown[:, 1:])  # Check Right
        mask[:, 1:]  |= (free[:, 1:]  &amp; unknown[:, :-1])  # Check Left
        mask[:-1, :] |= (free[:-1, :] &amp; unknown[1:, :])   # Check Down
        mask[1:, :]  |= (free[1:, :]  &amp; unknown[:-1, :])  # Check Up

        # Clustering (Group adjacent frontier pixels)
        rows, cols = grid.shape
        visited = np.zeros((rows, cols), dtype=bool)
        clusters = []

        for r in range(rows):
            for c in range(cols):
                if mask[r, c] and not visited[r, c]:
                    cluster = []
                    stack = [(r, c)]
                    visited[r, c] = True

                    # Flood fill to find all connected frontier points
                    while stack:
                        curr_r, curr_c = stack.pop()
                        cluster.append((curr_r, curr_c))

                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr==0 and dc==0: continue
                                nr, nc = curr_r + dr, curr_c + dc
                                if (0 &lt;= nr &lt; rows and 0 &lt;= nc &lt; cols and 
                                    mask[nr, nc] and not visited[nr, nc]):
                                    visited[nr, nc] = True
                                    stack.append((nr, nc))

                    if len(cluster) &gt;= self.min_frontier_size:
                        clusters.append(cluster)
        return clusters

    def select_best_frontier(self, clusters, grid, robot_pos):
        """
        Evaluates all frontier clusters and selects the best one based on:
        Score = Cost (Distance) / Reward (Size of frontier)
        """
        best_centroid = None
        best_score = float('inf') # Lower score is better

        # TODO: LOGGING - Info: "Evaluating X clusters..."

        for i, cluster in enumerate(clusters):
            # 1. Calculate Centroid (Average position of the cluster)
            rs = [c[0] for c in cluster]
            cs = [c[1] for c in cluster]
            raw_centroid = (int(sum(rs)/len(rs)), int(sum(cs)/len(cs)))

            frontier_size = len(cluster) # This is our "Reward"

            # 2. Snap centroid to a valid (free) cell if it ended up in a wall
            valid_centroid = self.find_nearest_valid_point(grid, raw_centroid)
            if valid_centroid is None:
                # TODO: LOGGING - Info: "Cluster X is invalid (in wall)"
                continue

            # 3. Check if this spot is Blacklisted
            cx, cy = self.grid_to_world(valid_centroid[0], valid_centroid[1])
            if self.is_blacklisted(cx, cy):
                # TODO: LOGGING - Info: "Cluster X is blacklisted"
                continue

            # 4. Calculate Path Cost using A*
            cost = self.a_star_search(grid, robot_pos, valid_centroid)

            if cost == float('inf'):
                # TODO: LOGGING - Info: "Cluster X is unreachable"
                continue

            # 5. Calculate Efficiency Score (Cost per unit of Reward)
            score = cost / frontier_size

            # TODO: LOGGING - Info: Log the details (Size, Cost, Score) for this cluster

            if score &lt; best_score:
                best_score = score
                best_centroid = valid_centroid

        return best_centroid</code></pre>
    <h4>6. The Control Loop</h4>
    <p>Finally, the heartbeat. This function runs every tick (1.0 Hz). It functions as a State Machine:</p>
    <ol>
        <li><strong>If Moving:</strong> Check if we arrived or got stuck.</li>
        <li><strong>If Idle:</strong> Scan the map, find clusters, pick the best one, and issue a drive command.</li>
    </ol>
    <p><em>Add the control loop and the main entry point:</em></p>
    <pre><code class="language-python">    # --------------------------------------------------------------------------
    # MAIN CONTROL LOOP
    # --------------------------------------------------------------------------

    def control_loop(self):
        # Wait for data
        if self.map_data is None or self.odom_data is None:
            return

        # Get Robot Position
        robot_x = self.odom_data.pose.pose.position.x
        robot_y = self.odom_data.pose.pose.position.y

        # Case 1: Robot is currently moving
        if self.is_navigating:
            if self.navigator.isTaskComplete():
                result = self.navigator.getResult()
                if result == 4: # SUCCEEDED
                    # TODO: LOGGING - Info: Goal reached successfully
                    pass
                else:
                    # TODO: LOGGING - Warn: Navigation failed (Status X). Blacklisting target.
                    if self.current_target:
                        self.blacklist.append(self.current_target)

                self.is_navigating = False
                self.current_target = None
                return

            if self.check_stuck_condition(robot_x, robot_y):
                # TODO: LOGGING - Error: Robot is stuck. Cancelling task.
                self.navigator.cancelTask()
                if self.current_target:
                    self.blacklist.append(self.current_target)
                self.is_navigating = False
                self.current_target = None
                return
            return

        # Case 2: Robot is idle, look for new targets
        w = self.map_data.info.width
        h = self.map_data.info.height
        # Convert flat map data to 2D grid
        grid = np.array(self.map_data.data, dtype=np.int8).reshape(h, w)

        robot_grid_pos = self.world_to_grid(robot_x, robot_y)

        # Find frontiers
        clusters = self.get_frontier_clusters(grid)

        if not clusters:
            # TODO: LOGGING - Info: No frontiers left. Exploration complete.
            self.timer.cancel()
            return

        # Select best target
        target_grid = self.select_best_frontier(clusters, grid, robot_grid_pos)

        if target_grid:
            tx, ty = self.grid_to_world(target_grid[0], target_grid[1])

            # TODO: LOGGING - Info: Navigating to new target at (tx, ty)

            goal_pose = self.navigator.getPoseStamped([tx, ty], TurtleBot4Directions.NORTH)
            self.navigator.startToPose(goal_pose)

            self.is_navigating = True
            self.current_target = (tx, ty)
            self.nav_start_time = time.time()
            self.start_pose = (robot_x, robot_y)
        else:
            # TODO: LOGGING - Warn: Frontiers detected but all are unreachable/blacklisted.
            pass

def main(args=None):
    rclpy.init(args=args)
    node = AutonomousExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()</code></pre>
</section>
<h3>Step 2.4: Build and Run</h3>
<p>Before running, ensure your <code>setup.py</code> is updated. In the <code>console_scripts</code> list, add:</p>
<pre><code class="language-python">'auto_explore = turtlebot4_nav.auto_explore:main'</code></pre>
<p>Then build and run:</p>
<pre><code class="language-bash">colcon build --symlink-install
source install/setup.bash
ros2 run turtlebot4_nav auto_explore
</code></pre>
<p><strong>Verification:</strong> If you implemented your logs correctly, you should see a stream of data in the terminal telling you exactly why the robot picked a specific frontier over another!</p>
<section id="analysis">
    <h2>Part 3: Analysis &amp; Discussion</h2>
    <p>Engineering is not just about building; it is about validation. You have replaced a "naive" geometric explorer with a "deliberative" Information Gain strategist. Now, you must prove that this extra computational effort actually results in smarter physical behavior.</p>
    <h3>3.1 Required Evidence: The Data from the Field</h3>
    <ol>
        <li><strong>Decision Log (Instrumentation):</strong>
            <p>The code provided in Part 2 logs the <em>final</em> decision, but to analyze the system, you need to see the <em>rejected</em> options too. Your <code>select_best_frontier</code> function should be logging the candidates it evaluates.</p>
            <p>Include a screenshot of a log entry where the robot evaluates at least two distinct clusters. It should look something like this:</p>
            <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[INFO] [auto_explore]: Evaluating 3 clusters...

[INFO] [auto_explore]: &gt; Cluster 0: Size 15 | Cost 45 | Score 3.00
[INFO] [auto_explore]: &gt; Cluster 1: Size 200 | Cost 100 | Score 0.50
[INFO] [auto_explore]: &gt; Cluster 2: Size 50 | Cost inf | Score inf
[INFO] [auto_explore]: Navigating to (1.25, 0.50) (Best Score: 0.50)</code></pre>
            </div>
            <p><em>Note how in the example above, the robot chose Cluster 1 (Score 0.50) even though Cluster 0 was much closer (Cost 45 vs 100). It correctly decided the long trip was worth the massive discovery.</em></p>
        </li>
        <li><strong>The "Intelligent Choice" Moment:</strong>
            <p>Capture a specific event where the robot's behavior differed from a naive explorer. Find a scenario where the robot ignored a <strong>close</strong> frontier (High Efficiency Score or Unreachable) for a <strong>better</strong> frontier (Low Efficiency Score). Provide an annotated screenshot or sketch of this scenario.</p>
        </li>
    </ol>
    <h3>3.2 Quantitative Analysis</h3>
    <p><strong>Table 1: Efficiency Analysis.</strong> Analyze 3 distinct decisions from your log. Compare the chosen target against the "Next Best" alternative.</p>
    <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 1em;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ccc; padding: 8px;">Decision #</th>
                <th style="border: 1px solid #ccc; padding: 8px;">Chosen Target (Score)</th>
                <th style="border: 1px solid #ccc; padding: 8px;">Rejected Target (Score)</th>
                <th style="border: 1px solid #ccc; padding: 8px;">Engineering Rationale</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;">1</td>
                <td style="border: 1px solid #ccc; padding: 8px;">0.45</td>
                <td style="border: 1px solid #ccc; padding: 8px;">2.10</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Chose large frontier further away over tiny frontier nearby.</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;">2</td>
                <td style="border: 1px solid #ccc; padding: 8px;">1.2</td>
                <td style="border: 1px solid #ccc; padding: 8px;">inf</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Rejected closest target because it was behind a wall (Cost=inf).</td>
            </tr>
        </tbody>
    </table>
    <h3>3.3 Short-Answer Design Review</h3>
    <p>Answer as if you are in a technical interview. Justify your answers with evidence from your code and run.</p>
    <ol>
        <li><strong>The Efficiency Metric:</strong> Your code minimizes the score \( S = \frac{\text{Cost}}{\text{Reward}} \).
            <ul>
                <li>Why is this superior to simply minimizing Cost (A*)? Give a specific example of a "Trap" that pure A* falls into that this metric avoids.</li>
                <li>Why is this superior to simply maximizing Reward (Frontier Size)? Give a specific example of a behavior this prevents.</li>
            </ul>
        </li>
        <li><strong>Heuristics vs. Reality:</strong> Your code uses the Manhattan distance (<code>abs(dx) + abs(dy)</code>) as the heuristic \( h(n) \).
            <ul>
                <li>Why is Manhattan distance appropriate for a grid-based map?</li>
                <li>Describe a map shape (e.g., a U-shape or a maze) where this heuristic vastly underestimates the true travel cost. How does this underestimation affect the performance of the A* search?</li>
            </ul>
        </li>
        <li><strong>Failure Recovery (The Blacklist):</strong>
            <ul>
                <li>The code includes a <code>blacklist</code> and a <code>check_stuck_condition</code>. Why are these necessary in the real world?</li>
                <li>If you removed the blacklist logic, what exactly would the robot do if it tried to navigate to a phantom frontier (a sensor glitch) that it couldn't physically reach?</li>
            </ul>
        </li>
        <li><strong>Algorithmic Complexity:</strong> A* is computationally expensive.
            <ul>
                <li>If your map size doubled (e.g., from 400x400 to 800x800), roughly how much slower would your worst-case pathfinding become?</li>
                <li>Propose one optimization to speed up your Python A* implementation (e.g., Downsampling? Limiting search depth?).</li>
            </ul>
        </li>
    </ol>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>4. Troubleshooting: The Engineering Diagnostic Process</h2>
    <p>Your robot now has a complex "brain." When it misbehaves, you must use your <strong>Mental Model</strong> of the algorithms to diagnose the root cause.</p>
    <h3>4.1 Common Failure Modes</h3>
    <ul>
        <li><strong>Symptom:</strong> The robot sits still for 5-10 seconds, then finally moves.
            <ul>
                <li><strong>Diagnosis:</strong> <strong>Compute Starvation.</strong> The A* algorithm is computationally heavy in Python. If the target is far away or inside a complex maze, the loop takes seconds to finish.</li>
                <li><strong>Solution:</strong> This is often acceptable for a lab. If it triggers the "Stuck" timeout, increase <code>stuck_timeout</code> or decrease the <code>tick_rate</code> so the robot plans less often.</li>
            </ul>
        </li>
        <li><strong>Symptom:</strong> The robot ignores a frontier that is clearly visible and reachable in RViz.
            <ul>
                <li><strong>Diagnosis A:</strong> <strong>The Blacklist.</strong> The robot likely tried to go there previously, failed (stuck or nav error), and has now banned that target. Check your logs for "Blacklisted" messages.</li>
                <li><strong>Diagnosis B:</strong> <strong>Invalid Centroid.</strong> The center of the frontier might be slightly inside a wall. The <code>find_nearest_valid_point</code> function attempts to fix this, but if the map is very noisy, it might fail.</li>
            </ul>
        </li>
        <li><strong>Symptom:</strong> The robot spins in place or "wiggles" without making progress.
            <ul>
                <li><strong>Diagnosis:</strong> <strong>Oscillation.</strong> Two frontiers have nearly identical Efficiency Scores. The robot picks Target A, moves 1cm, recalculates, picks Target B, moves 1cm, and repeats.</li>
                <li><strong>Solution:</strong> This is a classic robotics problem. In a real product, we would add "hysteresis" (sticking to a decision). For this lab, you can ignore it unless it prevents exploration.</li>
            </ul>
        </li>
    </ul>
    <h3>4.2 Pre-Flight Checklist</h3>
    <ul>
        <li>[ ] <strong>Build:</strong> <code>colcon build --symlink-install</code> (Do this after <em>every</em> change to the Python file).</li>
        <li>[ ] <strong>Source:</strong> <code>source install/setup.bash</code>.</li>
        <li>[ ] <strong>Reset:</strong> If the map gets messy, restart SLAM. A bad map makes A* fail because it hallucinates walls that don't exist.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
