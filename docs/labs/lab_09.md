---
title: "Lab 09: TurtleBot 4 Sensors"
---

# Lab 09: TurtleBot 4 Sensors

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1: Bring Up the Simulation</a></li>
                <li><a href="#part2">Part 2: Sensor Survey and the Lidar Frame (Worked Example)</a></li>
                <li><a href="#part3">Part 3: Sensor Noise</a></li>
                <li><a href="#part4">Part 4: One Detector per Sensor</a></li>
                <li><a href="#part5">Part 5: Thresholds for the Four Lanes</a></li>
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
    <p>You work with the sensors of a simulated TurtleBot 4: a lidar, a depth camera, a color webcam, an IMU, and the infrared (IR) proximity, cliff, and bump sensors of its Create&nbsp;3 base. You find out what each one publishes, measure how much its readings scatter, write a function that detects a hazard from each sensor&rsquo;s data, and then choose which sensors stop the robot in front of four different hazards, and at what thresholds.</p>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>The lab at a glance</strong>
        <table style="border-collapse: collapse; width: 100%; margin-top: 0.5em;">
            <tr><td style="padding: 4px 8px;"><strong>Pre-lab</strong></td><td style="padding: 4px 8px;">Move Docker&rsquo;s storage to /home, pull the image, accept, clone, build the provided package, and start the simulation once.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 1</strong></td><td style="padding: 4px 8px;">Three terminals: the simulation, your commands, and the hazard monitor.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 2</strong></td><td style="padding: 4px 8px;">Record each sensor&rsquo;s message type, rate, and frame. Predict which sensors can see a low box. Measure how the lidar is mounted and write <code>range_at_bearing</code>.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 3</strong></td><td style="padding: 4px 8px;">Park the robot at four distances from a wall and measure the scatter in each sensor.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 4</strong></td><td style="padding: 4px 8px;">Write a detector for each sensor and watch each one stop the robot.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 5</strong></td><td style="padding: 4px 8px;">Choose sensors and thresholds that stop the robot in front of all four hazards at two speeds, and justify them.</td></tr>
        </table>
    </div>
    <h3>1.2 Background</h3>
    <p><strong>The sensors.</strong> In Part 2, use the topics below to find each sensor message&rsquo;s type, rate, and frame. The table lists what each sensor measures and its limits.</p>
    <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 0.5em;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ccc; padding: 6px;">Sensor</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Topic</th>
                <th style="border: 1px solid #ccc; padding: 6px;">What it measures</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Limits</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">Lidar</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/scan</code></td><td style="border: 1px solid #ccc; padding: 6px;">Distance to the nearest surface in 640 directions around the robot, in one horizontal plane</td><td style="border: 1px solid #ccc; padding: 6px;">0.164 to 12 m; the plane is 0.19 m above the floor</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">Color camera (webcam)</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/webcam/image_raw</code></td><td style="border: 1px solid #ccc; padding: 6px;">A 320 &times; 240 color image</td><td style="border: 1px solid #ccc; padding: 6px;">Front of the top plate, 0.37 m above the floor, tilted 26&deg; down; its view reaches the floor about 0.2 m ahead of the bumper</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">Depth camera (OAK-D)</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/oakd/rgb/preview/depth</code></td><td style="border: 1px solid #ccc; padding: 6px;">A 320 &times; 240 depth image: each valid pixel gives a distance in meters along the camera&rsquo;s forward axis</td><td style="border: 1px solid #ccc; padding: 6px;">Looks straight ahead from 0.24 m above the floor; no readings closer than 0.3 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">IMU</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/imu</code></td><td style="border: 1px solid #ccc; padding: 6px;">Rotation rate (gyroscope) and acceleration</td><td style="border: 1px solid #ccc; padding: 6px;">Measures motion, not position</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">IR proximity</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/ir_intensity</code></td><td style="border: 1px solid #ccc; padding: 6px;">Seven readings around the front bumper; larger when an object is closer</td><td style="border: 1px solid #ccc; padding: 6px;">Only objects within about 0.2 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">Cliff and bump</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/hazard_detection</code></td><td style="border: 1px solid #ccc; padding: 6px;">A list of current hazards: type 1 is a bump, type 2 a cliff</td><td style="border: 1px solid #ccc; padding: 6px;">A cliff is reported when the floor drops away under the front of the robot; a bump when the bumper is pressed</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">Wheel odometry</td><td style="border: 1px solid #ccc; padding: 6px;"><code>/odom</code></td><td style="border: 1px solid #ccc; padding: 6px;">The robot&rsquo;s position estimated from its wheel rotation</td><td style="border: 1px solid #ccc; padding: 6px;">Errors build up as the robot drives</td></tr>
        </tbody>
    </table>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/d01-tb4-sensor-placement.svg" alt="Side view of the TurtleBot 4 to scale: the OAK-D depth camera 0.24 m above the floor looking straight ahead, with no depth readings closer than 0.3 m; the webcam on the front of the top plate 0.37 m above the floor, tilted 26 degrees down, its view reaching the floor about 0.2 m ahead of the bumper; the lidar scan plane 0.19 m above the floor; IR sensors on the front of the bumper reaching about 0.2 m; cliff sensors under the bumper looking down; the bumper front 0.17 m ahead of the robot's center; and the 8 cm box from lane A, lower than both the lidar plane and the OAK-D" style="max-width: 100%; height: auto;" /></p>
    <p><em>Example: the simulated TurtleBot 4 with the webcam clipped to the front of its top plate</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/s02-webcam-on-robot.png" alt="Close-up of the simulated TurtleBot 4 from the front right. A dark webcam with a round lens is mounted on a small clip at the front edge of the round top plate and tilted down toward the floor. The OAK-D is under the plate, with the lidar below the OAK-D." style="max-width: 100%; height: auto;" /></p>
    <p><strong>Frames.</strong> The header of each message names the frame its numbers are measured in (<code>header.frame_id</code>). The robot&rsquo;s own frame, <code>base_link</code>, has x pointing forward, y to the robot&rsquo;s left, and z up. A sensor&rsquo;s frame is fixed to the sensor, and a sensor can be mounted turned relative to the robot. In this lab a <strong>bearing</strong> is a direction in the robot frame: 0 is straight ahead, +&pi;/2 is the robot&rsquo;s left, and &minus;&pi;/2 its right.</p>
    <p><strong>Noise.</strong> Repeated readings from a stationary sensor can vary. Their standard deviation measures this scatter; their mean can also differ from the true value. Noise in this simulation was added by course staff, with values chosen to resemble the real sensors, not measured from them: about 1 cm for the lidar at any distance, depth error that grows with the square of the distance (as a stereo camera&rsquo;s does), a few levels out of 255 in the color image, and a gyroscope with a small constant bias.</p>
    <p><strong>The lanes.</strong> The robot drives along +x in one of four lanes, each with one hazard. Each hazard is detected by some sensors and not by others.</p>
    <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 0.5em;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ccc; padding: 6px;">Lane</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Hazard</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Where it starts</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">A</td><td style="border: 1px solid #ccc; padding: 6px;">An orange box 8 cm tall</td><td style="border: 1px solid #ccc; padding: 6px;">x = 1.2 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">B</td><td style="border: 1px solid #ccc; padding: 6px;">A pit: a 0.5 m gap in the floor</td><td style="border: 1px solid #ccc; padding: 6px;">x = 1.2 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">C</td><td style="border: 1px solid #ccc; padding: 6px;">A wall</td><td style="border: 1px solid #ccc; padding: 6px;">x = 1.5 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">D</td><td style="border: 1px solid #ccc; padding: 6px;">A red marker painted on the floor, a stop line</td><td style="border: 1px solid #ccc; padding: 6px;">x = 1.2 m</td></tr>
        </tbody>
    </table>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/d02-lab09-lanes.svg" alt="Top view of the four lanes to scale, with +x up the page: lane D at y = 1.5 m with the red marker from x = 1.2 m, lane A at y = 0 with the orange box from x = 1.2 m, lane B at y = -1.5 m with the 0.5 m pit from x = 1.2 m, and lane C at y = -3 m with the wall at x = 1.5 m; the robot is drawn at x = 0 in each lane" style="max-width: 100%; height: auto;" /></p>
    <p><strong>The simulation and the real robot.</strong> The webcam is added for this lab; a stock TurtleBot 4 does not have one. On a real TurtleBot 4 the Create&nbsp;3 base stops itself at a cliff or a bump. Those reflexes are turned off in this simulation; your detectors supply the hazard reports that trigger a stop. Three provided programs exist only in simulation: the <strong>sensor relay</strong>, which adds the camera noise and labels each IR reading with its sensor&rsquo;s name; <strong>lane_test</strong>, which measures where the robot stopped using the simulator&rsquo;s exact knowledge of its position; and <strong>record_noise</strong>, which parks the robot in front of the wall. The functions you write in <code>sensing.py</code> contain no simulation code.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Identify</strong> a sensor&rsquo;s message type, rate, and frame, and <strong>convert</strong> a lidar reading into the robot&rsquo;s frame.</li>
        <li><strong>Measure</strong> sensor noise and <strong>describe</strong> how it changes with distance.</li>
        <li><strong>Implement</strong> a hazard detector for each sensor from its raw data.</li>
        <li><strong>Predict</strong> which sensors detect a hazard from how they are mounted and their limits, and <strong>compare</strong> the prediction with what happened.</li>
        <li><strong>Choose</strong> sensors and stop thresholds and <strong>justify</strong> them from measured noise and stopping distance.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab.</strong> Complete this section on your own time before starting Part 1 in lab.</div>
    <p>VMs power off 4 hours after the reservation starts; keep your work in <code>~/workspaces</code> and push after each part with the command in Section 7.4. Git runs on the VM, ROS 2 runs in the container, and you edit in VS Code on the VM, as in Labs 4 to 7.</p>
    <ol>
        <li><strong>Move Docker&rsquo;s storage to the larger disk (once per VM).</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <p>Docker keeps its images on the VM&rsquo;s 25 GB main disk, which has room for about two lab images. If that disk fills, Docker and FastX can fail. This script moves Docker&rsquo;s storage to the VM&rsquo;s 68 GB <code>/home</code> disk and keeps the images you already have:</p>
            <pre><code class="language-bash">curl -fsSL -o move_docker_to_home.sh https://raw.githubusercontent.com/MEMS-Intro-to-Robotics/mems-robotics-toolkit/main/move_docker_to_home.sh &amp;&amp; bash move_docker_to_home.sh</code></pre>
            <p>Type your NetID password when <code>sudo</code> asks for it. Copying the images you already have can take a few minutes. <strong>Checkpoint:</strong> near the end of the output, the lines that start with <code>/var/lib/docker</code> and <code>/var/lib/containerd</code> both show <code>ubuntuos-home--lv</code>. If you run it again on the same VM, it prints <code>already a mount; skipping</code> twice and leaves the storage where it is.</p>
                    </li>
        <li><strong>Pull the TurtleBot 4 image.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:turtlebot4-jazzy-latest</code></pre>
            <p>The image is about 10 GB. If the pull stops with <code>no space left on device</code>, free space and pull again:</p>
            <pre><code class="language-bash">docker system prune -a --volumes -f</code></pre>
            <p>The prune deletes stopped containers, Docker&rsquo;s build cache, and every image that no container is using, including the Kinova and Crazyflie images. Files in <code>~/workspaces</code> stay.</p>
        </li>
        <li><strong>Accept Lab 9 and clone it.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-09</code></pre>
            <p>Clone into <code>~/workspaces</code> with the command it prints. If <code>gh student</code> is missing or not signed in, repeat the Lab 1 setup (<code>gh extension install foundation50/gh-student</code>, then <code>gh student login</code>).</p>
        </li>
        <li><strong>Start the container.</strong> Use the container command from Lab 7 with this lab&rsquo;s name and image, plus an addition at the end:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab09 --net=host --gpus all -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:turtlebot4-jazzy-latest bash -c 'echo "export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST" &gt;&gt; ~/.bashrc &amp;&amp; exec bash'</code></pre>
            <p>Without the addition, your simulation could exchange messages with simulations on other students&rsquo; VMs. The addition limits automatic ROS 2 discovery to your own VM in every shell in this container, including the ones you open later with <code>docker exec</code>. The welcome banner displays <code>Discovery: SUBNET</code>; that line is fixed text. Exiting this terminal deletes the container and closes every <code>docker exec</code> shell; files in <code>~/workspaces</code> stay. If it fails with <code>could not select device driver</code>, run it without <code>--gpus all</code> and tell a TA.</p>
        </li>
        <li><strong>Build the package.</strong> The repository already contains this lab&rsquo;s package, <code>lab09_sensors</code>, so building it with the command below is the only package setup.
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-09-*/ros2_ws &amp;&amp; colcon build --symlink-install &amp;&amp; source install/setup.bash &amp;&amp; ros2 pkg executables lab09_sensors</code></pre>
            <p>The <code>*</code> stands for your GitHub username, and the shell fills it in. With <code>--symlink-install</code>, an edit to <code>sensing.py</code> takes effect the next time a program starts, without building again. <strong>Checkpoint:</strong> the last four lines are <code>lab09_sensors hazard_monitor</code>, <code>lane_test</code>, <code>record_noise</code>, and <code>sim_sensor_relay</code>.</p>
        </li>
        <li><strong>Start the simulation once.</strong>
            <p><strong>Location:</strong> Container Terminal (the same one)</p>
            <pre><code class="language-bash">ros2 launch lab09_sensors sim.launch.py</code></pre>
            <p><strong>Checkpoint:</strong> a Gazebo window shows four lanes separated by yellow-and-black striped lines, with one hazard at the far end of each: a red mark, an orange box, a gap in the floor, and a gray wall. The TurtleBot 4 sits at the start of the box lane, and the TurtleBot 4 HMI and Teleop panels are on the right. Press <code>Ctrl+C</code> in the terminal to stop it.</p>
            <p><em>Example: the Gazebo window at startup</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/s01-lanes.png" alt="The Gazebo window looking down the lanes from behind the robot: a light floor inside gray walls, lit from one side, divided into four lanes by yellow-and-black striped lines, with the four hazards in a row at the far end, from left to right the red mark, the orange box, the dark gap in the floor, and the gray wall; the black TurtleBot 4 is in the near part of the box lane, and the TurtleBot 4 HMI and Teleop panels fill the right side of the window" style="max-width: 100%; height: auto;" /></p>
        </li>
        <li><strong>Read Section 1.2.</strong></li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>ros2 pkg executables lab09_sensors</code> lists four executables.</li>
        <li>[ ] <code>ros2 launch lab09_sensors sim.launch.py</code> shows the four lanes and the robot.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1: Bring Up the Simulation</h3>
        <p><strong>Goal:</strong> the simulation in one container shell, your commands in a second, and room for the hazard monitor in a third.</p>
        <p>Start the container (pre-lab step 4) and open two more shells, each from a new Host VM Terminal, with <code>docker exec -it lab09 bash</code>. <strong>Prepare</strong> all three by moving to your repository and sourcing your workspace:</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-09-* &amp;&amp; source ros2_ws/install/setup.bash</code></pre>
        <p>If the shell prints <code>No such file or directory</code>, check that you are in the intended repository and that the pre-lab build (step 5) completed there.</p>
        <h4>Step 1.1: Terminal 1, the simulation</h4>
        <pre><code class="language-bash">ros2 launch lab09_sensors sim.launch.py</code></pre>
        <p><strong>Checkpoint:</strong> the four lanes appear. Leave it running for the whole lab.</p>
        <p>Terminal 1 keeps printing while the simulation runs. These lines are normal and need no action: many lines of <code>Velocity command timed out. Braking.</code>, an <code>[ERROR]</code> at startup that the desired controller update period is faster than the simulation period, and <code>process has died</code> after you press <code>Ctrl+C</code>.</p>
        <details>
            <summary>What this launch starts</summary>
            <p>Gazebo with the lanes and the TurtleBot 4, with noise added to its sensors; one bridge that carries the sensor data, the velocity commands, and the simulation clock between Gazebo and ROS 2; the Create&nbsp;3 base&rsquo;s own programs, with its cliff and bump reflexes turned off; and the sensor relay, which is used only in simulation.</p>
        </details>
        <h4>Step 1.2: Terminal 2, your commands</h4>
        <p>Terminal 2 stays in the repository root, the folder that holds <code>thresholds.yaml</code>. Every command in Parts 2 to 5 runs there unless a step says otherwise.</p>
        <pre><code class="language-bash">ros2 topic list</code></pre>
        <p><strong>Checkpoint:</strong> the list includes <code>/scan</code>, <code>/imu</code>, <code>/odom</code>, <code>/ir_intensity</code>, <code>/hazard_detection</code>, and two topics starting with <code>/webcam/</code>, and three starting with <code>/oakd/rgb/preview/</code>. If the list shows only <code>/parameter_events</code> and <code>/rosout</code>, ROS 2 is still finding the simulation&rsquo;s topics: wait a few seconds and run the command again. Terminal 3 is for the hazard monitor in Part 4.</p>
    </section>
    <section id="part2">
        <h3>Part 2: Sensor Survey and the Lidar Frame (Worked Example)</h3>
        <p><strong>Goal:</strong> record each sensor&rsquo;s message type, rate, and frame; predict which sensors can see the low box; and convert a lidar reading to the robot&rsquo;s frame.</p>
        <h4>Step 2.1: The lidar, worked through</h4>
        <p>Use these commands to inspect the lidar topic. To find the message type:</p>
        <pre><code class="language-bash">ros2 topic info /scan</code></pre>
        <p>The rate. Let it print for about 10 s, then press <code>Ctrl+C</code> and read the last <code>average rate</code>:</p>
        <pre><code class="language-bash">ros2 topic hz /scan</code></pre>
        <p>The frame, from one message&rsquo;s header:</p>
        <pre><code class="language-bash">ros2 topic echo --once --field header.frame_id /scan</code></pre>
        <p>For some topics this command first prints lines that start with <code>A message was lost!!!</code> or <code>total count</code>. Skip them: the frame is the last line before the closing <code>---</code>.</p>
        <p><strong>Checkpoint:</strong> <code>Type: sensor_msgs/msg/LaserScan</code>, a rate a little under 10 Hz, and <code>rplidar_link</code>. In VS Code, fill in the <code>lidar</code> entry of <code>sensor_survey.yaml</code>:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>lidar:
  topic: /scan
  type: sensor_msgs/msg/LaserScan
  rate_hz: 9.7
  frame_id: rplidar_link</code></pre>
        </div>
        <p>Your rate may differ: rates depend on how fast the VM runs the simulation. Record the rate you measured.</p>
        <h4>Step 2.2: The other sensors</h4>
        <p><strong>Contract:</strong> fill in the remaining six entries of <code>sensor_survey.yaml</code> the same way. Some messages are lists of readings with a header of their own; record the frame in the message&rsquo;s top-level header.</p>
        <details>
            <summary>Hint 1: Seeing what a message contains</summary>
            <p><code>ros2 interface show</code> followed by the type from <code>ros2 topic info</code> lists every field of that message.</p>
        </details>
        <h4>Step 2.3: Predict</h4>
        <p>Before Part 4, decide which sensors you expect to detect the low box in lane A, using the limits in Section 1.2. List them under <code>low_box_prediction</code> in <code>sensor_survey.yaml</code>, and write one sentence per sensor in your PDF giving the reason.</p>
        <h4>Step 2.4: How the lidar is mounted</h4>
        <p>The transform between two frames gives one frame&rsquo;s position and rotation in the other:</p>
        <pre><code class="language-bash">ros2 run tf2_ros tf2_echo base_link rplidar_link</code></pre>
        <p>It may first print <code>Waiting for transform</code> with <code>frame does not exist</code> once or twice; wait for the next lines. Press <code>Ctrl+C</code> after it has printed the transform once. <strong>Checkpoint:</strong> a <code>Translation</code> line and a <code>Rotation: in RPY (degree)</code> line. The third RPY number is the lidar&rsquo;s yaw, its rotation about the vertical axis. A scan&rsquo;s angle 0 points along the lidar frame&rsquo;s x axis, so angle 0 points in the direction given by that yaw in the robot frame.</p>
        <p><strong>Contract:</strong> in <code>sensing.py</code>, set <code>LIDAR_YAW</code> to the yaw in radians and write <code>range_at_bearing</code>, which returns the range in a given robot-frame bearing. Its docstring describes the inputs. Then run its test:</p>
        <p><strong>Location:</strong> Container Terminal (Terminal 2)</p>
        <pre><code class="language-bash">python3 -m pytest test_lab_9.py -v -k range_at_bearing</code></pre>
        <details>
            <summary>Hint 1: From bearing to angle</summary>
            <p>A direction with bearing <em>b</em> in the robot frame has angle <em>b</em> &minus; <code>LIDAR_YAW</code> in the lidar frame. Its index in <code>ranges</code> is that angle&rsquo;s distance from <code>angle_min</code>, divided by <code>angle_increment</code> and rounded.</p>
        </details>
        <details>
            <summary>Hint 2: Wrapping</summary>
            <p>The scan covers a full circle, so an index past the last reading continues at the first. Python&rsquo;s <code>%</code> operator wraps an index into the range from 0 to <code>len(ranges) - 1</code>, and also wraps negative indices.</p>
        </details>
        <p><strong>For your PDF:</strong> the contents of <code>sensor_survey.yaml</code>, your prediction with its reasons, the <code>tf2_echo</code> output, and the value you chose for <code>LIDAR_YAW</code>.</p>
    </section>
    <section id="part3">
        <h3>Part 3: Sensor Noise</h3>
        <p><strong>Goal:</strong> measure how much each sensor&rsquo;s readings scatter, and how that changes with distance.</p>
        <p><code>record_noise</code> moves the robot to lane C, facing the wall, at the distance you give (from the robot&rsquo;s center to the wall), keeps it still, and records four readings: the lidar range straight ahead, the depth at the center of the depth image, the front-center-left IR reading, and the gyroscope&rsquo;s yaw rate.</p>
        <pre><code class="language-bash">ros2 run lab09_sensors record_noise --distance 1.0</code></pre>
        <p><strong>Checkpoint:</strong> after 20 s of simulation time it saves the readings and prints one line per sensor, like this (the counts depend on the sensor rates, and the gyroscope&rsquo;s mean may be negative):</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>Wrote 2147 readings to runs/noise_1.00m.csv
  depth_center_m         n=  297  mean=    1.0596  std=  0.0110
  gyro_z_rad_s           n= 1250  mean=    0.0020  std=  0.0020
  ir_front_center_left   n=  400  mean=   15.0000  std=  0.0000
  lidar_range_m          n=  200  mean=    1.0403  std=  0.0098</code></pre>
        </div>
        <p>An IR reading of 15 is the value it reports with nothing in range.</p>
        <p><strong>Contract:</strong> record at distances of 0.25, 0.5, 1.0, and 2.0 m. Make a table with the mean and standard deviation of each sensor at each distance, and a plot of the lidar and depth standard deviations against distance, saved as <code>docs/noise_vs_distance.png</code>. Any plotting tool is fine; the numbers are in the printed lines and in the files in <code>runs/</code>. To plot with Python and matplotlib in the container, run your script with <code>/usr/bin/python3</code>: in this image, <code>python3</code> alone cannot import matplotlib.</p>
        <details>
            <summary>Hint 1: Reading the trend</summary>
            <p>Compare how each standard deviation changes when the distance doubles. If it stays the same, the noise does not depend on distance; if it doubles, it grows in proportion; if it roughly quadruples, it grows with the square of the distance.</p>
        </details>
        <p>The robot is not turning during a recording, so the gyroscope&rsquo;s true yaw rate is zero. From its mean, estimate how far the robot&rsquo;s heading estimate would drift in 60 s if the heading came only from adding up the gyroscope readings.</p>
        <p><strong>For your PDF:</strong> the table, <code>docs/noise_vs_distance.png</code>, which sensors&rsquo; noise grows with distance and how, and your heading-drift estimate.</p>
    </section>
    <section id="part4">
        <h3>Part 4: One Detector per Sensor</h3>
        <p><strong>Goal:</strong> write a hazard detector for each sensor and see each one stop the robot in its lane.</p>
        <p>Each detector in <code>sensing.py</code> receives one message&rsquo;s data as numbers and arrays and returns <code>True</code> when the data meet the hazard criteria you implement. Each function&rsquo;s docstring describes its inputs. The <strong>hazard monitor</strong> calls your functions on live data: for every sensor marked <code>use: true</code> in <code>thresholds.yaml</code>, it runs that sensor&rsquo;s function on each new message, and when the function returns <code>True</code> it publishes the sensor&rsquo;s name on <code>/hazard_stop</code>. <code>lane_test</code> drives the robot along one lane and stops it when a name arrives.</p>
        <h4>Step 4.1: The lidar detector</h4>
        <p>Write <code>lidar_blocked</code>, then run its test from Terminal 2:</p>
        <pre><code class="language-bash">python3 -m pytest test_lab_9.py -v -k lidar_blocked</code></pre>
        <p>In <code>thresholds.yaml</code>, set <code>use: true</code> under <code>lidar</code> only. In Terminal 3, from the repository root, start the hazard monitor:</p>
        <pre><code class="language-bash">ros2 run lab09_sensors hazard_monitor</code></pre>
        <p><strong>Checkpoint:</strong> <code>Sensors in use: lidar.</code> Leave it running, and in Terminal 2 drive lane C:</p>
        <pre><code class="language-bash">ros2 run lab09_sensors lane_test C</code></pre>
        <p><strong>Checkpoint:</strong> the robot drives toward the wall and stops, and the output ends:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>  stopped by: lidar
  margin: +0.264 m (front edge at 1.236 m)
  added to runs/lane_results.csv</code></pre>
        </div>
        <p>The <strong>margin</strong> is the distance from the robot&rsquo;s front edge to the start of the hazard after the robot came to rest. A negative margin means the robot went past the start of the hazard. Each run adds a row to <code>runs/lane_results.csv</code> that also records the front edge&rsquo;s position when the stop signal arrived, whether the robot touched the hazard or fell, and the thresholds in use.</p>
        <details>
            <summary>How the hazard monitor and lane_test use time</summary>
            <p>Both use the simulation clock, so the robot drives at the commanded speed in simulation time even when the VM runs the simulation slower than real time. In staff runs on different machines and on different days, the same lane and speed gave margins within about 0.02 m of each other.</p>
        </details>
        <h4>Step 4.2: The other detectors</h4>
        <p><strong>Contract:</strong> write <code>ir_blocked</code>, <code>depth_blocked</code>, <code>marker_seen</code>, <code>cliff_seen</code>, and <code>bump_seen</code>, and pass each one&rsquo;s test. Then show each detector stopping the robot: with only that sensor in use, drive a lane it should detect.</p>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 0.5em;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ccc; padding: 6px;">Sensor in <code>thresholds.yaml</code></th>
                    <th style="border: 1px solid #ccc; padding: 6px;">Lane to drive</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>ir</code></td><td style="border: 1px solid #ccc; padding: 6px;">C</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>depth</code></td><td style="border: 1px solid #ccc; padding: 6px;">C</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>camera</code></td><td style="border: 1px solid #ccc; padding: 6px;">D</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>cliff</code></td><td style="border: 1px solid #ccc; padding: 6px;">B</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>bump</code></td><td style="border: 1px solid #ccc; padding: 6px;">C</td></tr>
            </tbody>
        </table>
        <p>The hazard monitor reads <code>thresholds.yaml</code> and your functions when it starts. After editing either one, stop it with <code>Ctrl+C</code> and start it again.</p>
        <details>
            <summary>Hint 1: <code>depth_blocked</code> and the floor</summary>
            <p>The bottom rows of the depth image see the floor about half a meter ahead, closer than most stop ranges. That is why the function also checks height: a pixel counts only if what it sees is higher than <code>min_height</code> above the floor. Its docstring gives the height formula.</p>
            <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/d03-depth-pixel-height.svg" alt="Side view of the camera 0.244 m above the floor with two pixel rays: one reaches the floor at depth 0.50 m, 0.244 m below the camera, so its height is 0; the other reaches the box at depth 0.70 m, 0.204 m below the camera, so its height is 0.04 m, above a min_height of 0.03 m. The formula is height = camera_height - (v - cy) * d / fy" style="max-width: 100%; height: auto;" /></p>
            <p><em>Example: the webcam image and the depth image in lane A, with the robot center at x = 0.6 m</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/s04-lane-a-webcam-depth.png" alt="Left: the webcam image of lane A shows the orange top and dark brown front face of a box on the light floor, seen from above. Right: the depth image uses dark purple for near surfaces and yellow for far surfaces, with a color bar from 0.3 to 4 m. The distance to the floor increases toward the top of the image. The box appears as a darker block 0.6 to 0.9 m ahead of the robot's center. The area at the top of the image, above the floor and walls, is black and has no depth readings." style="max-width: 100%; height: auto;" /></p>
        </details>
        <details>
            <summary>Hint 2: <code>marker_seen</code> and what counts as red</summary>
            <p>In this simulation the light comes from one side, so a surface looks darker when it faces away from the light. In red, green, blue, the floor looks about (229, 220, 199), the top of the orange box about (255, 153, 31) and its side facing the robot about (92, 51, 10), the gray wall in lane C about (61, 61, 69), the room walls between (92, 92, 88) and (147, 147, 139), and the marker about (255, 31, 31), each give or take a few levels of noise. A rule that compares the red, green, and blue values of each pixel with limits can separate the marker from the rest.</p>
            <p><em>Example: the webcam image in lane D, at the start of the lane and with the robot center at x = 0.75 m</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/s03-webcam-lane-d.png" alt="Two webcam images of lane D, each with a dashed line across the middle row. At the start of the lane, the red marker appears as a small band above the line. With the robot center at x = 0.75 m, the red marker appears as a large trapezoid on the light floor in the bottom half of the image." style="max-width: 100%; height: auto;" /></p>
        </details>
        <details>
            <summary>Hint 3: An array instead of a loop</summary>
            <p>A comparison on a NumPy array gives an array of <code>True</code> and <code>False</code> values. Use <code>.any()</code> to check whether any values are true, or <code>.mean()</code> to get the fraction that are true. This is much faster than a Python loop over the pixels.</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> read the hazard monitor&rsquo;s terminal first. <code>is not written yet</code> means that function still raises <code>NotImplementedError</code>; a traceback names the line in <code>sensing.py</code> that failed. If <code>lane_test</code> says it could not move the robot, look at Terminal 1. If the robot drives past a hazard with no stop, check that the sensor is marked <code>use: true</code> and that the monitor was restarted after the edit. After one clean retry or 10 minutes without progress, ask a TA and show the monitor&rsquo;s output.</blockquote>
        <h4>Step 4.3: Test your prediction</h4>
        <p>Drive lane A once with each of <code>lidar</code>, <code>ir</code>, <code>depth</code>, and <code>bump</code> in use on its own. Compare the sensors that stopped the robot with your Part 2 prediction.</p>
        <p><strong>For your PDF:</strong> the <code>lane_results.csv</code> rows from Steps 4.1 to 4.3 and, for lane A, which sensors detected the box compared with your prediction.</p>
    </section>
    <section id="part5">
        <h3>Part 5: Thresholds for the Four Lanes</h3>
        <p><strong>Goal:</strong> choose the sensors and thresholds you submit, so that the robot stops correctly in every lane at two speeds.</p>
        <p><code>lane_test</code> takes a speed in m/s:</p>
        <pre><code class="language-bash">ros2 run lab09_sensors lane_test A --speed 0.3</code></pre>
        <p>The targets, one per lane, judged from the <code>margin</code>, <code>touched</code>, and <code>fell</code> columns:</p>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 0.5em;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ccc; padding: 6px;">Lane</th>
                    <th style="border: 1px solid #ccc; padding: 6px;">Target</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="border: 1px solid #ccc; padding: 6px;">A, low box</td><td style="border: 1px solid #ccc; padding: 6px;">Margin from 0.05 to 0.30 m, box not touched</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;">B, pit</td><td style="border: 1px solid #ccc; padding: 6px;">Does not fall in</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;">C, wall</td><td style="border: 1px solid #ccc; padding: 6px;">Margin from 0.05 to 0.30 m, wall not touched</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;">D, red marker</td><td style="border: 1px solid #ccc; padding: 6px;">Margin from 0 to 0.30 m: stops before the line, but not far before it</td></tr>
            </tbody>
        </table>
                <p><strong>Contract:</strong></p>
        <ul>
            <li>Choose which sensors to use and set their thresholds in <code>thresholds.yaml</code>. Restart the hazard monitor and drive all four lanes at 0.2 m/s and at 0.3 m/s. All eight runs must meet the targets with the same file, and that file is the one you submit.</li>
            <li>Keep at least one earlier setting that failed a target, with its <code>lane_results.csv</code> rows. Do not delete rows from the file; the grader looks for the eight passing runs made with your submitted thresholds.</li>
        </ul>
        <p>The column <code>front_at_stop_signal</code> is where the front edge was when the stop signal arrived, and <code>front_at_rest</code> is where it came to rest. The difference is how far the robot travels after a detection, at that speed.</p>
        <details>
            <summary>Hint 1: Where to start</summary>
            <p>Begin with one sensor per hazard, chosen from Step 4.3 and Section 1.2. A sensor that sees a hazard from farther away gives more room for the stopping distance; a sensor that sees it only up close may stop too late at 0.3 m/s.</p>
        </details>
        <details>
            <summary>Hint 2: Using your noise measurements</summary>
            <p>Near a stop threshold, noise can put successive readings on opposite sides of the threshold. For approximately normally distributed noise with standard deviation &sigma;, most readings are within about &plusmn;2&sigma; of the mean. Compare this range of sensor readings with the width of the target window, allowing for the robot&rsquo;s stopping distance.</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> if a lane stops too early, find which sensor stopped it in the <code>stopped_by</code> column and change that sensor&rsquo;s threshold. If it stops too late, compare <code>front_at_stop_signal</code> with the hazard&rsquo;s start to see whether the detection or the stopping distance was the problem. After two settings that fail the same lane, ask a TA and show the rows.</blockquote>
        <p><strong>Checkpoint:</strong> the last eight rows of <code>runs/lane_results.csv</code> cover lanes A to D at 0.2 and 0.3 m/s, meet every target, and show the same <code>thresholds</code>.</p>
        <p><strong>Design justification</strong> (a short paragraph in your PDF): which sensors you used for each hazard and why; how you chose each threshold from your Part 3 noise measurements and the stopping distances in your results; one setting you rejected, with its rows; and which lane has the least room to spare. Include the eight passing rows.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p><strong>Where the answers go:</strong> in your Gradescope PDF, after the Part 5 justification. All four are graded. Answer each in a few sentences from your own runs.</p>
    <h3>Question 1: The lidar frame</h3>
    <ul>
        <li>Suppose <code>LIDAR_YAW</code> were left at 0 and the robot stood at the start of lane C. Which way would <code>range_at_bearing</code> with a bearing of 0 actually look, and what would it return? What would a hazard monitor built on it do in lane C?</li>
    </ul>
    <h3>Question 2: The low box</h3>
    <ul>
        <li>Which sensors detected the box in Step 4.3? For each sensor that did not, give the reason from where it is mounted or from its limits in Section 1.2. Where your prediction was wrong, what had you not taken into account?</li>
    </ul>
    <h3>Question 3: Noise and distance</h3>
    <ul>
        <li>From your Part 3 table: how do the lidar and depth noise compare at 0.5 m and at 2 m? What does that mean for a depth stop range set at 2 m rather than 0.5 m? From your heading-drift estimate, how far off would the robot&rsquo;s heading estimate be after 5 minutes, and what would that do to a map the robot builds while driving, as in Lab 10?</li>
    </ul>
    <h3>Question 4: The simulation and a real robot</h3>
    <ul>
        <li>Name two ways this simulation differs from a real TurtleBot 4 (Section 1.2 names some). For each, say whether your thresholds would need to move, and in which direction, to keep meeting the targets on the real robot.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Recurring setup, Docker, ROS 2, and simulation problems are on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#turtlebot-4-sensors-simulation" target="_blank" rel="noopener">Troubleshooting</a>. For this lab: a terminal that cannot find the package, a black or missing Gazebo window, a topic that shows no messages, a hazard monitor that skips a sensor or reports an error, a change to <code>thresholds.yaml</code> that has no effect, and a <code>lane_test</code> that cannot move the robot.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://turtlebot.github.io/turtlebot4-user-manual/" target="_blank" rel="noopener">TurtleBot 4 User Manual</a> (the robot&rsquo;s sensors and topics)</li>
        <li><a href="https://iroboteducation.github.io/create3_docs/" target="_blank" rel="noopener">iRobot Create&nbsp;3 documentation</a> (hazards, IR proximity, and the safety reflexes)</li>
        <li><a href="https://www.ros.org/reps/rep-0103.html" target="_blank" rel="noopener">REP 103: Standard Units of Measure and Coordinate Conventions</a> (why x is forward and y is left)</li>
        <li><a href="https://docs.luxonis.com/hardware/platform/depth/configuring-stereo-depth/" target="_blank" rel="noopener">Luxonis: Configuring Stereo Depth</a> (why stereo depth error grows with distance)</li>
    </ul>
        <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: build and source reminders, ROS 2 CLI checks, Git and Docker commands.</li>
        <li><code>ros2 run lab09_sensors lane_test --help</code> and <code>ros2 run lab09_sensors record_noise --help</code> list each tool&rsquo;s options.</li>
        <li>RViz can show the lidar scan and the depth camera&rsquo;s point cloud around the robot: <code>rviz2</code> from a container shell, Fixed Frame <code>base_link</code>, then Add a LaserScan display on <code>/scan</code> and a PointCloud2 display on <code>/oakd/rgb/preview/depth/points</code>. This is optional and not graded.<br /><em>Example: RViz with the robot in lane A at x = 0.6 m, showing the lidar scan, the depth point cloud colored by height, and axes for <code>rplidar_link</code>, <code>webcam_optical_frame</code>, and <code>oakd_rgb_camera_optical_frame</code></em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab09/s05-rviz-lane-a.png" alt="RViz window with the robot model on a grid. The lidar scan appears as a line of points along the far walls, above the box. The depth point cloud shows the floor ahead of the robot in orange, the box as a yellow block on the floor, and the far wall rising in rainbow colors. Small colored axes mark the lidar, webcam, and OAK-D frames on the robot." style="max-width: 100%; height: auto;" /></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
