---
title: "Lab 10: SLAM and Frontier Exploration in the Garage Labs"
---

# Lab 10: SLAM and Frontier Exploration in the Garage Labs

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1: Bring Up the Simulation and Nav2</a></li>
                <li><a href="#part2">Part 2: A Point Goal in the Map Frame</a></li>
                <li><a href="#part3">Part 3: Random Goals and a Free-Space Check</a></li>
                <li><a href="#part4">Part 4: Frontier Exploration</a></li>
                <li><a href="#part5">Part 5: The Saved Map and the Floor Plan</a></li>
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
    <p>A simulated TurtleBot 4 maps the Garage Labs (Wilkinson 129/133), the room this lab meets in. The simulated world was built from the building&rsquo;s floor plan and measurements taken in the room: the walls, the row of storage cages down the middle, tool room 129A, the columns, the benches and stools, and the robot cell. SLAM builds the map while the robot drives, and Nav2 plans and follows paths on that map. You send the robot to a point, then to random points, and then write the parts of a frontier explorer that decide where the robot goes next. At the end you save the map and compare it with the floor plan.</p>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>The lab at a glance</strong>
        <table style="border-collapse: collapse; width: 100%; margin-top: 0.5em;">
            <tr><td style="padding: 4px 8px;"><strong>Pre-lab</strong></td><td style="padding: 4px 8px;">Pull the image, accept, clone, build the provided package, and start the simulation and Nav2 once.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 1</strong></td><td style="padding: 4px 8px;">Three terminals: the simulation, Nav2, and your commands.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 2</strong></td><td style="padding: 4px 8px;">Convert a point on the floor plan into the map frame and send the robot there.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 3</strong></td><td style="padding: 4px 8px;">Send random goals with and without a free-space check that you write, and compare.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 4</strong></td><td style="padding: 4px 8px;">Write frontier detection and a frontier score, and compare your explorer with a nearest-frontier explorer.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 5</strong></td><td style="padding: 4px 8px;">Save the map, overlay it on the floor plan, and measure a wall.</td></tr>
        </table>
    </div>
    <h3>1.2 Background</h3>
    <p><strong>The programs.</strong> Four groups of programs are used in this lab:</p>
    <ul>
        <li><strong>Gazebo</strong> simulates the room, the robot, and its lidar.</li>
        <li><strong>slam_toolbox</strong> (SLAM, simultaneous localization and mapping) builds the map from the lidar scans and the wheel odometry, and estimates where the robot is on that map. It publishes the map on <code>/map</code>.</li>
        <li><strong>Nav2</strong> takes a goal pose, plans a path to it on the map, and drives the robot along the path while avoiding obstacles. When a goal fails, Nav2 prints the reason in its terminal.</li>
        <li><strong>Your code and the provided programs</strong> decide where the robot should go and send those goals to Nav2.</li>
    </ul>
    <p>SLAM and Nav2 run as separate programs. Nav2 plans on whatever map SLAM has published so far, so a path can change while the robot drives, as SLAM adds the space the robot has just seen.</p>
    <p><strong>The occupancy grid.</strong> The map is a grid of square cells, 0.05 m on a side. Each cell holds one number: <code>-1</code> if no scan has reached it (unknown, gray in RViz), <code>0</code> if the scans show it is empty (free, white), and <code>100</code> if the scans show something there (occupied, black). Other mapping programs also use values between 0 and 100; the SLAM in this lab writes only these three. The message carries the cells as one flat list, row after row, together with the map&rsquo;s <code>resolution</code> (meters per cell) and <code>origin</code> (the position of the corner of cell (0, 0) in the map frame).</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/d02-occupancy-grid-and-frontiers.svg" alt="A small occupancy grid with unknown cells (-1), free cells (0), and occupied cells (100) around the robot. Frontier cells are the free cells that have at least one unknown neighbor; they form a band along the edge of the explored space. The flat list stores row 0 first, so the cell in row r and column c is at index r times the width plus c." style="max-width: 100%; height: auto;" /></p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/d03-point-to-cell.svg" alt="The grid laid over the map frame. The origin is the map-frame position of the bottom-left corner of cell (0, 0), and each cell is resolution meters wide; columns count along x and rows along y. point_to_cell gives the cell that contains a map point, wherever in the cell the point lies. cell_to_point gives the point at the center of a cell, not its corner." style="max-width: 100%; height: auto;" /></p>
    <p><strong>Frontiers.</strong> A frontier cell is a free cell next to an unknown cell at the edge of the mapped space. Driving to a frontier can bring unknown space into lidar range so SLAM can map it as free or occupied. A frontier explorer repeats this until no reachable frontier is left. A goal placed on a frontier cell is in a cell marked free on the map. A free cell can still be too close to an obstacle for the robot, or have no path to it; the explorer moves each goal away from obstacles and drops goals that fail.</p>
    <p><strong>Choosing a frontier.</strong> When there are several frontiers, the explorer has to pick one. Nearest-first picks the frontier with the shortest planned path, which may be a small pocket near the robot, such as the space behind a bench. A score can combine a frontier&rsquo;s size, as a rough measure of how much new space it may reveal, with the length of the path Nav2 plans to reach it, which is longer than the straight line when a wall is in the way. You compare the rules with your own runs in Part 4.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/d04-frontier-score.svg" alt="The robot with two candidate frontiers. Candidate A is near, at the end of a short dead end, and is small. Candidate B is farther away, at the edge of a large unexplored area, and is large. A nearest-first rule chooses A, returns, and then chooses the next nearby pocket. A score that weighs frontier size against path length can choose B." style="max-width: 100%; height: auto;" /></p>
    <p><strong>The room and the two frames.</strong> The floor plan uses the <strong>world frame</strong>: its origin is at the center of the room, x points east along the long side, and y points north toward the lobby. The robot starts at world (&minus;4.2, &minus;2.95), just outside the west door of tool room 129A, facing west. SLAM starts its <strong>map frame</strong> where the robot starts: the map origin is the robot&rsquo;s start position, map x points the way the robot faced at the start, and map y points to the robot&rsquo;s left. Nav2 goals are given in the map frame. RViz draws the map frame with map x pointing up the screen, so in RViz the room appears turned 90&deg; from the floor plan, with west at the top and south on the left, and its ends can be cut off: scroll the mouse wheel over the map to zoom out until you see the whole room.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/d01-room-frames.svg" alt="Top view of the Garage Labs to scale with north up: the outer walls, the storage cage row down the middle, tool room 129A below it with a closed door in its west and east walls, the columns, the bench rows on both sides, the robot cell in the southwest corner, and the patio wall along the bottom. The world frame has its origin at the center of the room with x east and y north. The robot is drawn at world (-4.2, -2.95), outside 129A&rsquo;s west door, facing west, with the map frame&rsquo;s axes on it: map x pointing west and map y pointing south. Two points are marked: world (-4.2, -5.4), which is map (0, 2.45), and the east-door goal at world (4.2, -2.95)." style="max-width: 100%; height: auto;" /></p>
    <p><strong>What the lidar sees.</strong> The lidar measures in one horizontal plane 0.19 m above the floor (Lab 9). At that height it sees walls, the storage cages, the tool room, the columns, and the legs of benches and stools, but not the bench tops. The map shows what is in that plane.</p>
    <p><strong>The simulation and the real robot.</strong> On a real TurtleBot 4, the Create&nbsp;3 base stops itself at cliffs and on bumps. Those reflexes are turned off in this simulation, and the room has nothing to fall off.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Convert</strong> a point between the floor plan&rsquo;s frame, the SLAM map frame, and a cell of the occupancy grid.</li>
        <li><strong>Explain</strong> how Nav2 uses the map published by SLAM and how a planned path can change as the map grows.</li>
        <li><strong>Implement</strong> a free-space check for a goal and <strong>measure</strong> its effect on random goals.</li>
        <li><strong>Implement</strong> frontier detection on an occupancy grid, <strong>design</strong> a frontier score, and <strong>compare</strong> it with nearest-frontier selection from your own runs.</li>
        <li><strong>Evaluate</strong> a SLAM map against the floor plan and a measured dimension of the room.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab.</strong> Complete this section on your own time before starting Part 1 in lab. It covers the image, the repository, the build, and one start of the simulation and Nav2.</div>
    <p>VMs power off 4 hours after the reservation starts; keep your work in <code>~/workspaces</code> and push after each part with the command in Section 7.4. Git runs on the VM, ROS 2 runs in the container, and you edit in VS Code on the VM, as in Labs 4 to 9.</p>
    <ol>
        <li><strong>Check Docker&rsquo;s storage (once per VM).</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <p>Docker keeps its images on the VM&rsquo;s 25 GB main disk, which has room for about two lab images. If that disk fills, Docker and FastX can fail. This script moves Docker&rsquo;s storage to the VM&rsquo;s larger <code>/home</code> disk and keeps the images you already have. If you ran it for Lab 9 on this VM, it prints <code>already a mount; skipping</code> twice and changes nothing.</p>
            <pre><code class="language-bash">curl -fsSL -o move_docker_to_home.sh https://raw.githubusercontent.com/MEMS-Intro-to-Robotics/mems-robotics-toolkit/main/move_docker_to_home.sh &amp;&amp; bash move_docker_to_home.sh</code></pre>
            <p>Type your NetID password when <code>sudo</code> asks for it. <strong>Checkpoint:</strong> near the end of the output, the lines that start with <code>/var/lib/docker</code> and <code>/var/lib/containerd</code> both show <code>ubuntuos-home--lv</code>, or the script printed <code>already a mount; skipping</code> twice.</p>
        </li>
        <li><strong>Pull the Lab 10 image.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:tb4-jazzy-lab10-latest</code></pre>
            <p>The image is about 10 GB. If the pull stops with <code>no space left on device</code>, free space and pull again:</p>
            <pre><code class="language-bash">docker system prune -a --volumes -f</code></pre>
            <p>The prune deletes stopped containers, Docker&rsquo;s build cache, and every image that no container is using, including the images from earlier labs. Files in <code>~/workspaces</code> stay.</p>
                    </li>
        <li><strong>Accept Lab 10 and clone it.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-10</code></pre>
            <p>Your repository is named <code>intro-to-robotics-fall-2026-lab-10-</code> followed by your GitHub username. Clone it into <code>~/workspaces</code> with the clone command the accept command prints, for example:</p>
            <pre><code class="language-bash">cd ~/workspaces &amp;&amp; git clone https://github.com/MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-10-USERNAME.git</code></pre>
            <p>Use the repository URL printed by Classroom 50. If <code>gh student</code> is missing or not signed in, repeat the Lab 1 setup (<code>gh extension install foundation50/gh-student</code>, then <code>gh student login</code>).</p>
        </li>
        <li><strong>Start the container.</strong> As in Lab 9, use the command below with this lab&rsquo;s container name and image:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab10 --net=host --gpus all -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:tb4-jazzy-lab10-latest</code></pre>
            <p>Exiting this terminal deletes the container and closes every <code>docker exec</code> shell attached to it; files in <code>~/workspaces</code> stay. The welcome banner shows <code>Discovery: SUBNET</code>; that line is fixed text, and the container uses the <code>LOCALHOST</code> setting from the command. If it fails with <code>could not select device driver</code>, run it without <code>--gpus all</code> and tell a TA; the simulation still runs, more slowly.</p>
                    </li>
        <li><strong>Build the package.</strong> Build the provided package, <code>lab10_explore</code>:
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-*/ros2_ws &amp;&amp; colcon build --symlink-install &amp;&amp; source install/setup.bash &amp;&amp; ros2 pkg executables lab10_explore</code></pre>
            <p>The <code>*</code> stands for your GitHub username, and the shell fills it in. With <code>--symlink-install</code>, an edit to <code>exploration.py</code> takes effect the next time a program starts, without building again. <strong>Checkpoint:</strong> the last four lines are <code>lab10_explore explore</code>, <code>lab10_explore overlay_map</code>, <code>lab10_explore point_goal</code>, and <code>lab10_explore random_goals</code>.</p>
        </li>
        <li><strong>Start the simulation once.</strong>
            <p><strong>Location:</strong> Container Terminal (the same one)</p>
            <pre><code class="language-bash">ros2 launch lab10_explore sim.launch.py</code></pre>
            <p><strong>Checkpoint:</strong> two windows open. The Gazebo window shows the room: gray outer walls, the row of mesh storage cages down the middle, the orange tool room below the cages, benches with stools on both sides, and the TurtleBot 4 HMI and Teleop panels on the right. The robot is just west of the orange tool room. The RViz window shows the map forming around the robot: white free space and black walls in a gray unknown area. When the simulation is ready, the terminal prints <code>[lab10] Ready. Start Nav2 in a second terminal: ros2 launch lab10_explore nav2.launch.py</code>.</p>
            <p><em>Example: the Gazebo window at startup</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/s01-gazebo-room.png" alt="The Gazebo window with a view of the whole room from the southwest corner, looking down at an angle: gray outer walls, the rows of mesh storage cages down the middle, the orange tool room in front of them, benches with stools on both sides, the robot cell with its yellow frame in the near corner, and the small black TurtleBot 4 beside the tool room's west wall. The TurtleBot 4 HMI and Teleop panels fill the right side of the window." style="max-width: 100%; height: auto;" /></p>
            <p>Leave it running for the next step.</p>
        </li>
        <li><strong>Start Nav2 once.</strong> Open a second Host VM Terminal and attach it to the container:
            <p><strong>Location:</strong> Host VM Terminal (a new one)</p>
            <pre><code class="language-bash">docker exec -it lab10 bash</code></pre>
            <p><strong>Location:</strong> Container Terminal (the new shell)</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-* &amp;&amp; source ros2_ws/install/setup.bash &amp;&amp; ros2 launch lab10_explore nav2.launch.py</code></pre>
            <p><strong>Checkpoint:</strong> this terminal prints <code>[lab10] Nav2 active. Send goals from the third terminal or from RViz.</code>, and in RViz the Navigation 2 panel on the left shows <code>Navigation: active</code>. Then press <code>Ctrl+C</code> in this terminal, and then in the simulation&rsquo;s terminal.</p>
                    </li>
        <li><strong>Read Section 1.2.</strong></li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>ros2 pkg executables lab10_explore</code> lists four executables.</li>
        <li>[ ] <code>ros2 launch lab10_explore sim.launch.py</code> shows the room, the robot, and the map forming in RViz, and prints <code>[lab10] Ready</code>.</li>
        <li>[ ] <code>ros2 launch lab10_explore nav2.launch.py</code> prints <code>[lab10] Nav2 active</code>, and RViz&rsquo;s Navigation 2 panel shows <code>Navigation: active</code>.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1: Bring Up the Simulation and Nav2</h3>
        <p><strong>Goal:</strong> the simulation in one container shell, Nav2 in a second, and your commands in a third.</p>
        <p>Start the container (pre-lab step 4) and open two more shells, each from a new Host VM Terminal, with <code>docker exec -it lab10 bash</code>. <strong>Prepare</strong> all three by moving to your repository and sourcing your workspace:</p>
        <p><strong>Location:</strong> Container Terminal (all three)</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-* &amp;&amp; source ros2_ws/install/setup.bash</code></pre>
        <p>If the shell prints <code>No such file or directory</code>, check that you are in the intended repository and that the pre-lab build (step 5) completed there. If any item of the &ldquo;Ready for lab when&rdquo; list in Section 4 fails in the steps below, stop and finish the pre-lab first.</p>
        <h4>Step 1.1: Terminal 1, the simulation</h4>
        <pre><code class="language-bash">ros2 launch lab10_explore sim.launch.py</code></pre>
        <p><strong>Checkpoint:</strong> the room appears in Gazebo, the map starts to form in RViz, and Terminal 1 prints a checklist as each part starts:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[lab10] starting the simulation; this takes about a minute
[lab10] 1/4 Gazebo is running
[lab10] 2/4 TurtleBot 4 spawned; lidar publishing on /scan
[lab10] 3/4 wheel controllers active; odometry on /odom
[lab10] 4/4 SLAM active; map on /map
[lab10] Ready. Start Nav2 in a second terminal: ros2 launch lab10_explore nav2.launch.py</code></pre>
        </div>
        <p>Leave it running. If a line starting <code>[lab10] PROBLEM:</code> appears instead, it names the part that did not start: press <code>Ctrl+C</code> and start the launch again, and if it happens again, ask a TA.</p>
        <p>The percentage at the bottom right of the Gazebo window is how fast the simulation runs compared with real time. Below 100&nbsp;%, simulation time advances more slowly than wall time. The robot, SLAM, Nav2, and the provided programs use the simulation&rsquo;s clock; limited computing resources can still affect their timing. On the course VMs it is often 50 to 75&nbsp;% while the robot explores, so the elapsed wall time is longer than the reported simulation time. Each program&rsquo;s own output goes to a log file, not to Terminal 1. After <code>Ctrl+C</code>, Terminal 1 prints one line containing <code>[lab10] stopping</code>.</p>
        <details>
            <summary>What this launch starts</summary>
            <p>Gazebo with the room and the TurtleBot 4; one bridge that carries the lidar, the clock, and the robot&rsquo;s frames between Gazebo and ROS 2; the Create&nbsp;3 base&rsquo;s own programs, with its cliff and bump reflexes turned off; slam_toolbox; and RViz with the TurtleBot 4 navigation view. If a simulation is already running in this container, the launch stops it first and prints <code>A simulation was already running in this container. It was stopped; this one replaces it.</code></p>
        </details>
        <h4>Step 1.2: Terminal 2, Nav2</h4>
        <pre><code class="language-bash">ros2 launch lab10_explore nav2.launch.py</code></pre>
        <p><strong>Checkpoint:</strong> <code>[lab10] Nav2 active. Send goals from the third terminal or from RViz.</code> in this terminal and <code>Navigation: active</code> in RViz&rsquo;s Navigation 2 panel. The same panel shows <code>Localization: inactive</code>, which is normal: SLAM supplies Nav2 with the position estimate while Nav2&rsquo;s own localizer is inactive. One warning about the dock database prints before it, and two about the goal and progress checkers with the first goal; they are normal. Keep Terminal 2 where you can see it: when a goal fails, Nav2 prints the reason here.</p>
        <p>If Terminal 2 prints <code>[lab10] PROBLEM: Nav2 did not finish starting within 30 seconds.</code>, press <code>Ctrl+C</code> in Terminal 2 and start Nav2 again. If it happens again, restart as described at the end of this part, and start Nav2 once Terminal 1 prints <code>[lab10] Ready</code>.</p>
        

        <h4>Step 1.3: Terminal 3, your commands</h4>
        <p>Terminal 3 stays in the repository root, the folder that holds <code>runs/</code> and <code>maps/</code>. Every command in Parts 2 to 5 runs there unless a step says otherwise.</p>
        <pre><code class="language-bash">ros2 topic list</code></pre>
        <p><strong>Checkpoint:</strong> the list includes <code>/map</code>, <code>/scan</code>, <code>/odom</code>, <code>/cmd_vel</code>, and <code>/plan</code>. If it shows only <code>/parameter_events</code> and <code>/rosout</code>, ROS 2 discovery may still be in progress; wait a few seconds and run the command again.</p>
        <p><strong>Restarting.</strong> Part 4 requires fresh exploration runs; Part 5 uses the map from the score run. To restart: press <code>Ctrl+C</code> in Terminal 2, then in Terminal 1; start the simulation again in Terminal 1, and when Terminal 1 prints <code>[lab10] Ready</code>, start Nav2 again in Terminal 2. Restart Nav2 whenever you restart the simulation. If you restart only the simulation, Nav2 may stop with <code>process has died</code>, and the programs may print <code>Nav2 is not active after 60 s</code>. Starting Nav2 before the simulation leaves Nav2 waiting for a map.</p>
            </section>
    <section id="part2">
        <h3>Part 2: A Point Goal in the Map Frame</h3>
        <p><strong>Goal:</strong> send the robot to a point given on the floor plan, by converting it into the map frame.</p>
        <h4>Step 2.1: One goal from RViz</h4>
        <p>In RViz, click <strong>Nav2 Goal</strong> in the toolbar, then click a white (free) spot on the map a meter or two from the robot and drag to set the direction the robot should face. <strong>Checkpoint:</strong> a path appears from the robot to the goal, the robot follows it, and the Navigation 2 panel returns to <code>Feedback: reached</code>.</p>
                <h4>Step 2.2: A worked conversion: south of the tool room</h4>
        <p>The point world (&minus;4.2, &minus;5.4) is on the open floor south of the tool room&rsquo;s southwest corner, 2.45 m due south of the robot&rsquo;s start. At the start the robot faced west, and facing west its left is south, so this point is 2.45 m along map +y and 0 m along map x: map (0.0, 2.45). Send the robot there from Terminal 3:</p>
        <p><strong>Location:</strong> Container Terminal (Terminal 3)</p>
        <pre><code class="language-bash">ros2 run lab10_explore point_goal --x 0.0 --y 2.45</code></pre>
        <p><strong>Checkpoint:</strong> the robot drives around the southwest corner of the tool room and stops on the south side of it, and Terminal 3 prints a line that starts with <code>SUCCEEDED after</code>, followed by the simulation time the drive took and the distance driven. From there the lidar sees along the tool room&rsquo;s south wall to the east end of the room, and SLAM adds that area to the map. Nav2 can only plan to a point that is inside the map.</p>
        <h4>Step 2.3: The east door of the tool room</h4>
        <p>Tool room 129A has a door in its west wall and one in its east wall. The robot started in front of the west door at world (&minus;4.2, &minus;2.95), facing west. The point in front of the east door is at world (4.2, &minus;2.95). The tool room is closed, so the robot has to drive around it.</p>
        <p><strong>Task:</strong> work out the map-frame coordinates of world (4.2, &minus;2.95) the same way, using Section 1.2 and the room figure there. Write the conversion in your PDF. Then send the goal, with your numbers in place of <code>X</code> and <code>Y</code>:</p>
        <pre><code class="language-bash">ros2 run lab10_explore point_goal --x X --y Y</code></pre>
        <p><strong>Checkpoint:</strong> RViz shows a path to a point east of the tool room; the robot drives there and stops in front of the tool room&rsquo;s east door in Gazebo; Terminal 3 prints <code>SUCCEEDED after</code> with the time and the distance driven. Watch the path in RViz while the robot drives: it can change as SLAM maps more of the room. Note whether the first path crosses gray (unknown) cells; Question 1 asks about it.</p>
                        <details>
            <summary>Hint 1: Two steps</summary>
            <p>First find where the goal is relative to the start: subtract the start position from the goal in the world frame. Then express that offset along the map&rsquo;s axes, as in Step 2.2. Map x points the way the robot faced at the start (west), and map y points to the robot&rsquo;s left at the start (south).</p>
        </details>
        <details>
            <summary>Hint 2: Check your signs</summary>
            <p>Before you send the goal, check it against the room figure. The east door is on the far side of the tool room from the start, and map x points west: should the goal&rsquo;s map x be positive or negative? How far north or south of the start is the east door, and what does that make the goal&rsquo;s map y?</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> if the robot heads west, away from the tool room, check whether you sent world coordinates or reversed a sign. If <code>point_goal</code> prints <code>FAILED</code> or <code>REJECTED</code>, read the last lines in Terminal 2 for the reason, and check in RViz where your goal landed on the map. A reason that ends in <code>was outside bounds</code> means the point is not on the map yet: run Step 2.2 first, or check your signs. After one retry or 10 minutes without progress, ask a TA and show your conversion and Terminal 2.</blockquote>
        <p><strong>Screenshot:</strong> RViz with the robot partway around the tool room and its path to the east door. Save it as <code>docs/part2_east_door.png</code>.</p>
        <p><em>Example (yours shows your own path and map)</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/s02-rviz-east-door.png" alt="RViz a few seconds after the east-door goal was sent, with west at the top of the screen. The map is white around the start and the bench rows, with black walls and the costmap's pink and blue bands; the tool room is the dark-edged corner just below and right of the robot, and its inside and the east end of the room are still gray. A thin path line runs from the robot down the screen along the tool room's south side, then turns and crosses the gray, unmapped area toward the east door." style="max-width: 100%; height: auto;" /></p>
        <p><strong>For your PDF:</strong> your conversion of world (4.2, &minus;2.95) into the map frame, the <code>point_goal</code> output, <code>docs/part2_east_door.png</code>, and two or three sentences on whether the path changed during the drive and what you observed.</p>
    </section>
    <section id="part3">
        <h3>Part 3: Random Goals and a Free-Space Check</h3>
        <p><strong>Goal:</strong> measure what happens when goals are drawn at random over the map, then filter them with a check you write.</p>
        <h4>Step 3.1: Random goals without a check</h4>
        <p>Run this right after Part 2, with the robot at the tool room&rsquo;s east door and most of the room on the map. <code>random_goals</code> draws goal points at random over the area the current map covers and sends each one to Nav2, with a time limit of 120 s of simulation time per goal. With <code>--no-check</code> it sends every point it draws. If you stop it with <code>Ctrl+C</code>, the goals already finished stay in the file.</p>
        <pre><code class="language-bash">ros2 run lab10_explore random_goals --count 10 --no-check</code></pre>
        <p><strong>Checkpoint:</strong> one line per goal, with the point and whether its map cell is free, unknown, or occupied, then Nav2&rsquo;s result (<code>SUCCEEDED</code>, <code>FAILED</code>, or <code>TIMED OUT</code>), and at the end a summary such as <code>10 goals: 6 succeeded, 3 failed, 1 timed out.</code> The rows are in <code>runs/random_goals_unchecked.csv</code>. While it runs, read the reasons Nav2 prints in Terminal 2 for the goals that fail. Two common ones: <code>Failed to create plan with tolerance of: 0.500000</code> means the planner found no path to any point within 0.5 m of the goal, for example a goal inside a closed area; <code>was outside bounds</code> means the goal is outside the map.</p>
        <h4>Step 3.2: The grid conversions</h4>
        <p>Open <code>ros2_ws/src/lab10_explore/lab10_explore/exploration.py</code> in VS Code. Each function&rsquo;s docstring describes its inputs and what it returns. The functions take the map&rsquo;s cells as a 2-D NumPy array, already reshaped so that <code>grid[row, col]</code> is one cell, row 0 at the map&rsquo;s origin.</p>
        <p><strong>Task:</strong> write <code>point_to_cell</code> and <code>cell_to_point</code>, using the second figure in Section 1.2, then run their tests:</p>
        <pre><code class="language-bash">python3 -m pytest test_lab_10.py -v -k "point_to_cell or cell_to_point"</code></pre>
        <h4>Step 3.3: The free-space check</h4>
        <p><strong>Task:</strong> write <code>goal_is_safe</code>, which returns <code>True</code> only when the goal cell and every cell in its square neighborhood extending <code>clearance_cells</code> in each direction are free. Set <code>CLEARANCE_M</code> at the top of <code>exploration.py</code> to the clearance you choose, in meters; <code>random_goals</code> converts it to cells with the map&rsquo;s resolution. Run the tests:</p>
        <pre><code class="language-bash">python3 -m pytest test_lab_10.py -v -k goal_is_safe</code></pre>
        <details>
            <summary>Hint 1: Which values count as free</summary>
            <p>Only <code>0</code> is free. <code>-1</code> is unknown and anything above 0 is at least partly occupied. A goal in unknown space may turn out to be inside a bench.</p>
        </details>
        <details>
            <summary>Hint 2: Checking the cells around a goal</summary>
            <p>Take the square of cells from <code>row - clearance_cells</code> to <code>row + clearance_cells</code> and the same for columns, with NumPy slicing, and check that every cell in it is 0. NumPy clips slice bounds without an error, and negative indices refer to positions from the end of the array. Check first whether the square reaches past the grid edge, and use the return value specified in the docstring.</p>
        </details>
        <details>
            <summary>Hint 3: Choosing the clearance</summary>
            <p>The TurtleBot 4 is about 0.34 m across. Nav2 keeps the robot&rsquo;s center away from obstacles by more than its radius. Compare your clearance with the gaps between the benches in the room: a clearance that is too large can exclude otherwise usable aisle goals. The lidar detects a bench&rsquo;s legs at scan height, so space beneath the top can appear free on the map; a goal there can leave the robot stuck among legs and stools.</p>
        </details>
        <h4>Step 3.4: Random goals with the check</h4>
        <p>An unchecked goal can leave the robot wedged among bench legs, so start this run from the start pose: restart the simulation and Nav2 as described at the end of Part 1, wait for <code>[lab10] Nav2 active</code>. To start this run with a map similar to the first run&rsquo;s, drive the robot to the east door again with the two goals of Part 2, then start the random goals. In Terminal 3, with your numbers from Step 2.3 in place of <code>X</code> and <code>Y</code>:</p>
        <pre><code class="language-bash">ros2 run lab10_explore point_goal --x 0.0 --y 2.45
ros2 run lab10_explore point_goal --x X --y Y
ros2 run lab10_explore random_goals --count 10</code></pre>
        <p><strong>Checkpoint:</strong> each goal line now also shows how many points were drawn and rejected by <code>goal_is_safe</code> before one passed, and the rows are in <code>runs/random_goals_checked.csv</code>.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> if a run stops with <code>The robot has not moved for 3 goals in a row</code>, restart the simulation and Nav2 and run it again; the rows already finished stay in the file, and a new run replaces them. <code>is not written yet</code> means that function still raises <code>NotImplementedError</code>; a traceback names the line in <code>exploration.py</code> that failed. If no point ever passes the check, print the clearance in cells and compare it with the widths of the white areas in RViz. After one retry or 10 minutes without progress, ask a TA and show the output.</blockquote>
        <p><strong>For your PDF:</strong> a table with one row per run listing goals sent, succeeded, failed or timed out, and total goal time (the sum of the <code>time_s</code> column of its log); for each goal in the unchecked run that did not succeed (<code>FAILED</code> or <code>TIMED OUT</code>), the cell value at the goal and any reason Nav2 reported; your <code>CLEARANCE_M</code> and why you chose it.</p>
    </section>
    <section id="part4">
        <h3>Part 4: Frontier Exploration</h3>
        <p><strong>Goal:</strong> write frontier detection and a frontier score, and compare your explorer with a nearest-frontier explorer from the same start.</p>
        <p><code>explore</code> repeats one decision until no reachable frontier is left or its time limit runs out: it finds the frontier cells with your <code>find_frontier_cells</code>, groups touching frontier cells into frontiers and drops very small ones, asks Nav2&rsquo;s planner for the path length to the six frontiers nearest the robot in a straight line, chooses one of those, and sends the robot there. With <code>--strategy nearest</code> it chooses the frontier with the shortest path. With <code>--strategy score</code> it calls your <code>score_frontier</code> for each frontier and chooses the highest score. A goal that fails is set aside; when no other frontier is left, the explorer tries the set-aside ones once more before it stops. The time limit is in simulation minutes.</p>
        <h4>Step 4.1: Frontier detection</h4>
        <p><strong>Task:</strong> write <code>find_frontier_cells</code>, which returns an array the shape of the grid that is <code>True</code> at every free cell with at least one unknown neighbor above, below, left, or right. Run its test:</p>
        <pre><code class="language-bash">python3 -m pytest test_lab_10.py -v -k find_frontier_cells</code></pre>
        <details>
            <summary>Hint 1: Shifted array comparisons</summary>
            <p>For array-based frontier detection, make one Boolean array for &ldquo;free&rdquo; and one for &ldquo;unknown&rdquo;. Compare <code>free[:, :-1]</code> with <code>unknown[:, 1:]</code> to find free cells whose right-hand neighbor is unknown, and do the same for the other three directions.</p>
        </details>
        <h4>Step 4.2: The nearest-frontier run</h4>
        <p>Restart the simulation and Nav2 as described at the end of Part 1, so the robot starts at the tool room&rsquo;s west door with an empty map. Then:</p>
        <pre><code class="language-bash">ros2 run lab10_explore explore --strategy nearest --minutes 10</code></pre>
        <p><strong>Checkpoint:</strong> for each decision, Terminal 3 prints a line such as <code>Decision 3 at 51.2 s: 25 frontiers, 6 with a planned path</code>, then one line per planned frontier with its size in cells and its path length in meters; <code>-&gt;</code> marks the one chosen. While the robot drives to a frontier, a line starting <code>driving:</code> every 20 s of simulation time gives the distance to go and the area mapped. In RViz the gray areas shrink as the robot drives. When it stops, it prints the time, the distance driven, and the area mapped, and the decisions are in <code>runs/explore_nearest.csv</code>.</p>
                <h4>Step 4.3: Your frontier score and your prediction</h4>
        <p><strong>Task:</strong> write <code>score_frontier</code>. It receives one frontier&rsquo;s size in cells and its path length in meters and returns a number; the explorer goes to the frontier with the highest number. Choose the scoring rule. Run its test, which checks only that the function returns a finite number for the inputs the explorer can pass:</p>
        <pre><code class="language-bash">python3 -m pytest test_lab_10.py -v -k score_frontier</code></pre>
        <details>
            <summary>Hint 1: A starting point</summary>
            <p>For positive path lengths, size divided by path length increases with frontier size and decreases with path length. Look at what that rule does for a frontier the robot is almost on top of, with a path length near 0, and decide how to handle it.</p>
        </details>
        <details>
            <summary>Hint 2: Reading your nearest-frontier log</summary>
            <p>In <code>runs/explore_nearest.csv</code>, the <code>all_candidates</code> column lists each decision&rsquo;s frontiers as size/path length. Check whether a small chosen frontier was followed by travel back along the previous route, and whether your score would have chosen a different frontier there.</p>
        </details>
        <p><strong>Task:</strong> before your first score run, predict what it will do. Open <code>prediction.yaml</code> at the root of your repository and fill in the mapped area after 1 and after 2 minutes, the distance the robot will drive in the whole run, and your reasoning: where in this room your score may choose differently from nearest-first and how that would affect the numbers. If you expect the same choices, explain why. Your nearest-frontier log has the same three numbers for comparison. Then commit and push it:</p>
        <p>Git runs on the VM, not in the container, so open a new Host VM Terminal (not one of the three container shells) for this.</p>
        <p><strong>Location:</strong> Host VM Terminal (a new one)</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-10-* &amp;&amp; git add prediction.yaml &amp;&amp; git commit -m "Prediction" &amp;&amp; git push origin main</code></pre>
        <p>You are graded on how you compare the prediction with the run, regardless of prediction accuracy. Do not edit <code>prediction.yaml</code> after the push.</p>
        <h4>Step 4.4: The first run with your score</h4>
        <p>Restart the simulation and Nav2 again, then in Terminal 3:</p>
        <pre><code class="language-bash">ros2 run lab10_explore explore --strategy score --minutes 10</code></pre>
        <p><strong>Checkpoint:</strong> before it starts, it prints <code>Prediction recorded from prediction.yaml:</code> followed by the commit and your numbers. Each decision then also shows your score for each frontier, and the decisions are in <code>runs/explore_score_1.csv</code>. If it stops with a message about <code>prediction.yaml</code>, do what the message says: fill in the value it names, or commit and push from the Host VM Terminal, then start the run again.</p>
        <p><em>Example: RViz partway through an exploration run</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/s03-rviz-exploring.png" alt="RViz partway through exploration, with the room turned 90 degrees: one end of the room is mapped in white, with the walls, the columns, and the bench and stool legs ringed by the costmap's pink and blue bands; the tool room's inside and part of the far end are still gray. A thin path runs from the robot to the edge of the gray area." style="max-width: 100%; height: auto;" /></p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> if the explorer stops with <code>The robot has not moved for 3 goals in a row</code>, restart the simulation and Nav2 and start the run again. If a score run stopped before it made 5 decisions, delete its log (for example <code>rm runs/explore_score_1.csv</code>) before you start again to reuse that run number; the repository check requires at least 5 decisions in each exploration log. If the explorer prints no frontiers at the start, check that the map in RViz shows white space around the robot and run the <code>find_frontier_cells</code> test again. If the robot stops making progress, read Terminal 2 for the reason the goals fail. If the robot goes back and forth between two frontiers, compare their scores in the log. After one retry or 10 minutes without progress, ask a TA and show the explorer&rsquo;s output.</blockquote>
        <h4>Step 4.5: Choose the setting you would use on the real robot</h4>
        <p>Compare runs using two measurements from each log: the <strong>time to map 200&nbsp;m&sup2;</strong> (the <code>t_s</code> of the first row whose <code>known_m2</code> is 200 or more) and the <strong>distance driven</strong> by then (<code>driven_m</code> in that row). On a real robot, a longer drive uses more battery. Your setting is the combination of your <code>score_frontier</code> and two options of <code>explore</code>: <code>--min-cells</code>, the minimum frontier size to consider (default 12 cells), and <code>--goal-clearance</code>, how far goal points stay from obstacles (default 0.5 m). For example, with larger frontiers only:</p>
        <pre><code class="language-bash">ros2 run lab10_explore explore --strategy score --minutes 10 --min-cells 30</code></pre>
        <p><strong>Task:</strong> make at least one more score run with a different setting, restarting the simulation and Nav2 before each run. Each run writes the next file, <code>runs/explore_score_2.csv</code> and so on, and records its settings and your <code>score_frontier</code> in the <code>settings</code> column. If a run never reaches 200&nbsp;m&sup2;, give its final area and distance in the table instead and say so. Choose the run whose setting you would use on the real robot in this room, and justify the choice from both numbers.</p>
                <h4>Step 4.6: Compare the runs</h4>
        <p><strong>Task:</strong> plot the mapped area against time for the nearest-frontier run and every score run on one set of axes, from the <code>t_s</code> and <code>known_m2</code> columns, and save it as <code>docs/coverage.png</code>. Each log has a row at every decision and a <code>progress</code> row every 10 s of simulation time, so for the area at 1 minute, use the <code>known_m2</code> of the first row whose <code>t_s</code> is 60 or more, and for the area at 2 minutes, that of the first row whose <code>t_s</code> is 120 or more. Their <code>t_s</code> is usually slightly above 60 and 120. Any plotting tool is fine; Python with matplotlib runs in the container with <code>python3</code>. From <code>runs/explore_score_1.csv</code>, compare your score&rsquo;s choice at one decision with the nearest-first candidate (the <code>nearest_size</code> and <code>nearest_path_m</code> columns of the same row). Use a decision where the choices differ if there is one; otherwise, explain why they agree.</p>
        <p><strong>For your PDF:</strong> <code>score_frontier</code> as a formula or a few lines of code, with your reason for it; your prediction next to what score run 1 did, with the reason for each difference; a table with one row per run (nearest and each score run): its setting, the mapped area at 1 and 2 minutes, the time to 200&nbsp;m&sup2;, and the distance driven by then; the setting you chose and why; <code>docs/coverage.png</code>; and the decision you compared, with the candidates&rsquo; sizes, path lengths, and scores.</p>
    </section>
    <section id="part5">
        <h3>Part 5: The Saved Map and the Floor Plan</h3>
        <p><strong>Goal:</strong> save the map from your last score run, overlay it on the floor plan, and check its scale against a measured wall.</p>
        <h4>Step 5.1: Save the map</h4>
        <p>With Terminal 1 still running from your last score run, check the area the explorer printed at the end of that run: the repository check needs a saved map of at least 150&nbsp;m&sup2;. If it is less, make another score run and save after that one.</p>
        <p><strong>Location:</strong> Container Terminal (Terminal 3)</p>
        <pre><code class="language-bash">mkdir -p maps &amp;&amp; ros2 run nav2_map_server map_saver_cli -f maps/wilkinson129 --ros-args -p map_subscribe_transient_local:=true -p save_map_timeout:=20.0</code></pre>
        <p><strong>Checkpoint:</strong> the output ends with <code>Map saved successfully</code>, and <code>ls maps</code> shows <code>wilkinson129.pgm</code> and <code>wilkinson129.yaml</code>. If you closed the simulation after your last score run, the map is gone: make another score run first. If it prints <code>Failed to spin map subscription</code>, the map did not arrive within the 20 s the command waits: check that Terminal 1 is still running and run the command again.</p>
                <h4>Step 5.2: Overlay the map on the floor plan</h4>
        <pre><code class="language-bash">ros2 run lab10_explore overlay_map maps/wilkinson129.yaml</code></pre>
        <p><code>overlay_map</code> finds the rotation and offset that best line up the occupied cells of your map with the walls of the floor plan, draws one over the other, and saves the drawing as <code>maps/wilkinson129_overlay.png</code>. <strong>Checkpoint:</strong> it prints the rotation that lines the map up with the plan, the share of your map&rsquo;s obstacle cells that lie within 15 cm of a plan wall, and the difference in rotation between the north and south halves of the map, and writes the image. Open the image in VS Code. The floor plan shows only walls and columns. Furniture can account for obstacle cells away from plan walls; mapping or alignment error can also contribute.</p>
        <p><em>Example (yours shows your own map)</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab10/s04-map-overlay.png" alt="The overlay with north up. Header lines give the rotation, 180.0 degrees, the share of obstacle cells within 15 cm of a plan wall, 53 percent, and the north-half versus south-half rotation, -0.4 degrees. The plan walls are blue-gray, the SLAM obstacles red, and the SLAM free space beige. The red outer walls, cage row sides, and tool room outline lie along the blue-gray walls; the bench and stool legs appear as small red dots in the beige areas, which the plan does not have; the inside of the cage row and the tool room are not mapped." style="max-width: 100%; height: auto;" /></p>
        <h4>Step 5.3: Measure the tool room</h4>
        <p>Tool room 129A&rsquo;s two long walls, north and south, are 6.66 m long on the outside, corner to corner, in the floor plan and in the simulation. In RViz the tool room is the closed rectangle next to the robot&rsquo;s start, and its long walls run up and down the screen (Section 1.2): the south wall is on the left, the side the robot drove along in Steps 2.2 and 2.3, and the north wall is on the right, facing the storage cages. Choose the long wall that your map shows from corner to corner; the south wall is often mapped only in part. In RViz, click <strong>Measure</strong> in the toolbar (the ruler, between Focus Camera and 2D Pose Estimate), click one outside corner of that wall, then the other. RViz shows the distance in the status bar at the bottom left of its window, for example <code>[Length: 2.5895m]</code>; no distance appears on the map. If the bottom of the RViz window is below the edge of the screen, maximize the window. Right-click in the map to clear the measurement. Measure three times and record each value.</p>
                        <p><strong>For your PDF:</strong> <code>maps/wilkinson129_overlay.png</code>, the numbers <code>overlay_map</code> printed with the reason for the rotation it found (Section 1.2), which wall you measured, your three measurements with their mean and the difference from 6.66 m, and two places where your map differs from the floor plan, with the reason for each.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p>Answer all four graded questions in your Gradescope PDF after Part 5, using a few sentences per question and evidence from your own runs.</p>
    <h3>Question 1: SLAM and Nav2</h3>
    <ul>
        <li>Which program produces the map and which uses it? Describe the path Nav2 first planned to the tool room&rsquo;s east door in Part 2 and whether it changed during the drive. Were any cells along Nav2&rsquo;s initial path unknown in the map? Explain what your observation shows about how Nav2&rsquo;s planner treats unknown cells, or what remains uncertain if the path crossed only mapped cells.</li>
    </ul>
    <h3>Question 2: Random goals</h3>
    <ul>
        <li>From your Part 3 table, how many goals failed with and without the check? Group the unchecked failures by the cell value at the goal. What would happen in this room with <code>CLEARANCE_M</code> set to 0, and with it set to 1 m?</li>
    </ul>
    <h3>Question 3: Nearest-first and your score</h3>
    <ul>
        <li>From <code>docs/coverage.png</code>, which run mapped more by 1 minute and by 2 minutes, and which reached 200&nbsp;m&sup2; first? Pick one decision in your nearest-frontier log and describe where the robot went next. Do the candidates&rsquo; sizes and path lengths suggest a choice that could have saved travel? Is there a situation in this room where your score would map less or drive farther than nearest-first? Describe it, or explain why your rule would choose the same frontiers.</li>
    </ul>
    <h3>Question 4: The map and the room</h3>
    <ul>
        <li>How far was your measured wall from 6.66 m, and what in the map limits how precisely you can measure it? The bench tops are well above the lidar&rsquo;s plane: how do the benches appear in your map, and why? If a real robot mapped the real room while people walked through it, what would you expect to see in the map and in the overlay?</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Recurring setup, Docker, ROS 2, and simulation problems are on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#slam-and-frontier-exploration-simulation" target="_blank" rel="noopener">Troubleshooting</a>. For this lab: a terminal that cannot find the package, a black or missing Gazebo or RViz window, Nav2 that never becomes active, goals that Nav2 rejects or abandons, a map that is empty or stops growing, and a map that will not save.</p>
        <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://docs.nav2.org/" target="_blank" rel="noopener">Nav2 documentation</a> (planners, costmaps, and the reasons a goal fails)</li>
        <li><a href="https://github.com/SteveMacenski/slam_toolbox" target="_blank" rel="noopener">slam_toolbox</a> (the SLAM used in this lab)</li>
        <li><a href="https://turtlebot.github.io/turtlebot4-user-manual/" target="_blank" rel="noopener">TurtleBot 4 User Manual</a> (SLAM and navigation on the robot)</li>
        <li><a href="https://docs.ros.org/en/jazzy/p/nav_msgs/msg/OccupancyGrid.html" target="_blank" rel="noopener">nav_msgs/OccupancyGrid</a> (the map message)</li>
        <li>B. Yamauchi, &ldquo;A frontier-based approach for autonomous exploration,&rdquo; in <em>Proc. IEEE International Symposium on Computational Intelligence in Robotics and Automation (CIRA)</em>, 1997. The frontier definition and the explore loop in Part 4.</li>
        <li>S. Macenski and I. Jambrecic, &ldquo;SLAM Toolbox: SLAM for the dynamic world,&rdquo; <em>Journal of Open Source Software</em>, 6(61), 2783, 2021.</li>
        <li>S. Macenski, F. Mart&iacute;n, R. White, and J. Gin&eacute;s Clavero, &ldquo;The Marathon 2: A Navigation System,&rdquo; in <em>Proc. IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)</em>, 2020.</li>
    </ul>
        <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: build and source reminders, ROS 2 CLI checks, Git and Docker commands.</li>
        <li><code>ros2 run lab10_explore point_goal --help</code>, <code>random_goals --help</code>, <code>explore --help</code>, and <code>overlay_map --help</code> (each with <code>ros2 run lab10_explore</code> in front) list each tool&rsquo;s options.</li>
        <li>To run the simulation without the Gazebo and RViz windows, for example on a slow VM while you only need the logs: <code>ros2 launch lab10_explore sim.launch.py gui:=false</code>. Without RViz you cannot do Steps 2.1 and 5.3.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
