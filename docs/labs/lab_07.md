---
title: "Lab 07: Crazyflie PID Tuning"
---

# Lab 07: Crazyflie PID Tuning

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
                <li><a href="#part2">Part 2: Milestone 1, A Baseline Step Test (Worked Example)</a></li>
                <li><a href="#part3">Part 3: Milestone 2, The Proportional Gain</a></li>
                <li><a href="#part4">Part 4: Milestone 3, The Derivative Gain</a></li>
                <li><a href="#part5">Part 5: Milestone 4, A Draft and the Integral Gain</a></li>
                <li><a href="#part6">Part 6: Milestone 5, Gains for the Course</a></li>
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
    <p>You tune the position controller of a simulated Crazyflie quadrotor. Each flight is recorded and measured, and you choose six gains from those measurements. The file that holds them, <code>gains.yaml</code>, is the file course staff fly on a real Crazyflie in Lab 8.</p>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>The lab at a glance</strong>
        <table style="border-collapse: collapse; width: 100%; margin-top: 0.5em;">
            <tr><td style="padding: 4px 8px;"><strong>Pre-lab</strong></td><td style="padding: 4px 8px;">Pull the image, accept, clone, build the provided package, and start the simulation once.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 1</strong></td><td style="padding: 4px 8px;">Two terminals: the simulation, and your flights.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 1</strong></td><td style="padding: 4px 8px;">Predict, then fly and measure a step test with the starting gains.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 2</strong></td><td style="padding: 4px 8px;">Raise <code>kp</code> and find gains at which rise time stops improving, overshoot occurs, and the response fails to settle.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 3</strong></td><td style="padding: 4px 8px;">Add <code>kd</code> to an overshooting response.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 4</strong></td><td style="padding: 4px 8px;">Fly in a draft. Measure the offset, then test <code>ki</code>.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Milestone 5</strong></td><td style="padding: 4px 8px;">Choose gains for the hoop course and justify them using your measurements.</td></tr>
        </table>
    </div>
    <h3>1.2 Background</h3>
    <p><strong>The control loop.</strong> Ten times a second, the controller compares the drone&rsquo;s position with the goal and computes a velocity command from the error, separately for x and for y:</p>
    <pre><code>command = kp &times; error  +  ki &times; (error added up over time)  +  kd &times; (rate of change of error)</code></pre>
    <p>The command is limited to 0.707 m/s on each axis. The drone&rsquo;s flight controller turns the command into motion and holds the height on its own, so height has no gains for you to tune.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab07/d01-pid-control-loop.svg" alt="The control loop: the goal position minus the measured position gives the error; the proportional, integral, and derivative terms are summed into a velocity command with a limit of 0.707 meters per second; the drone moves; the measured position is fed back" style="max-width: 100%; height: auto;" /></p>
    <p><strong>The numbers you will read.</strong> A step test moves the goal 0.6 m at once and holds it for 6 s. Four numbers describe the response: <strong>rise time</strong> (from 10% to 90% of the step), <strong>overshoot</strong> (how far past the goal, as a percentage of the step), <strong>settling time</strong> (when the drone last enters a band of 5 cm around the goal and stays there), and <strong>steady-state error</strong> (the magnitude of the mean position error over the last second of the hold).</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab08/d01-metrics-on-step-response.svg" alt="Two step responses. One crosses the goal: its overshoot is the peak beyond the goal and its settling time is when it stays within 5 centimeters. One never crosses the goal: its overshoot is zero and it still has a settling time" style="max-width: 100%; height: auto;" /></p>
    <p>The figure also shows RMS error, which Lab 8 uses and this lab does not.</p>
    <p><strong>What each fault looks like.</strong></p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab07/d02-tuning-failure-signatures.svg" alt="Four step responses: sluggish, which never reaches the goal in the time allowed; overshoot and ringing; settles short of the goal with a constant offset; and twitchy" style="max-width: 100%; height: auto;" /></p>
    <p><strong>The simulation and the real drone.</strong> Lab 8 flies your <code>gains.yaml</code> through a controller of the same kind: one PID per horizontal axis, at the same rate and with the same output limit. In the simulation, Gazebo and a provided node stand in for the real drone and its flight controller. The simulated drone approximates the real one, so the measurements may differ in Lab 8. Question 4 asks you to predict those differences.</p>
    <p><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab07/d03-simulation-and-real-drone.svg" alt="The mission node and the goal controller with your gains.yaml are the same in both labs. In Lab 7 the velocity command goes to the hover bridge and Gazebo; in Lab 8 it goes to the firmware of a real Crazyflie" style="max-width: 100%; height: auto;" /></p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Predict</strong> the response of a proportional position controller from its gain and its output limit, and <strong>compare</strong> the prediction with a measured step response.</li>
        <li><strong>Measure</strong> rise time, overshoot, settling time, and steady-state error from recorded flights.</li>
        <li><strong>Explain</strong> what the proportional, derivative, and integral terms each change in a step response, from your own measurements.</li>
        <li><strong>Choose</strong> gains for a timed course and <strong>justify</strong> the choice against an alternative you tested.</li>
        <li><strong>Predict</strong> how gains tuned in simulation will behave on the real drone.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab.</strong> Complete this section on your own time before starting Part 1 in lab.</div>
    <p>VMs power off 4 hours after the reservation starts; keep your work in <code>~/workspaces</code> and push after each milestone with the command in Section 7.4. Git runs on the VM, ROS 2 runs in the container, and you edit in VS Code on the VM, as in Labs 4 to 6.</p>
    <ol>
        <li><strong>Pull the Crazyflie image.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:crazyflie-jazzy-latest</code></pre>
            <p>If the pull stops with <code>no space left on device</code>, free space and pull again:</p>
            <pre><code class="language-bash">docker system prune -a --volumes -f</code></pre>
            <p>The prune deletes stopped containers, Docker&rsquo;s build cache, and every image that no container is using, including the Kinova image. Files in <code>~/workspaces</code> stay. Pull the Kinova image again when you next need it.</p>
                    </li>
        <li><strong>Accept Lab 7 and clone it.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-07</code></pre>
            <p>Clone into <code>~/workspaces</code> with the command it prints. If <code>gh student</code> is missing or not signed in, repeat the Lab 1 setup (<code>gh extension install foundation50/gh-student</code>, then <code>gh student login</code>).</p>
        </li>
        <li><strong>Start the container.</strong> Use the container command from Lab 6 with this lab&rsquo;s name and image:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab07 --net=host --gpus all -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:crazyflie-jazzy-latest</code></pre>
            <p>Exiting this terminal deletes the container and closes every <code>docker exec</code> shell; files in <code>~/workspaces</code> stay. If it fails with <code>could not select device driver</code>, run it without <code>--gpus all</code> and tell a TA. Each container shell opens with a banner about radios, USB, and Jupyter; this lab uses none of them.</p>
        </li>
        <li><strong>Build the package.</strong> The repository already contains this lab&rsquo;s package, <code>lab07_crazyflie</code>, complete. The line below is the whole of the package setup for this lab.
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-07-*/ros2_ws &amp;&amp; colcon build --symlink-install &amp;&amp; source install/setup.bash &amp;&amp; ros2 pkg executables lab07_crazyflie</code></pre>
            <p>The <code>*</code> stands for your GitHub username, and the shell fills it in. <strong>Checkpoint:</strong> the prompt shows your repository&rsquo;s <code>ros2_ws</code> folder, and the last four lines are <code>lab07_crazyflie analyze</code>, <code>goal_controller</code>, <code>hover_bridge</code>, and <code>mission</code>.</p>
        </li>
        <li><strong>Start the simulation once.</strong>
            <p><strong>Location:</strong> Container Terminal (the same one)</p>
            <pre><code class="language-bash">ros2 launch lab07_crazyflie sim.launch.py</code></pre>
            <p><strong>Checkpoint:</strong> a Gazebo window shows an arena with see-through walls, six red hoops, and a small drone on the floor at the center, and the terminal prints <code>Hover bridge ready</code>. Press <code>Ctrl+C</code> in the terminal to stop it. The lines it prints while stopping include <code>[ERROR] [gazebo-1]: process has died</code>; that is how the launch reports that Gazebo was stopped.</p>
            <p><em>Example:</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab07/s01-arena.png" alt="The Gazebo window: an arena with see-through walls, six red hoops at different heights, and the Crazyflie on the floor at the center" style="max-width: 100%; height: auto;" /></p>
        </li>
        <li><strong>Check the starting gains.</strong> In VS Code on the VM, open <code>gains.yaml</code> at the root of your repository. You tune the six gains in this file during the lab. Then check it:
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-07-* &amp;&amp; python3 check_gains.py</code></pre>
            <p><strong>Checkpoint:</strong> <code>gains.yaml looks right.</code></p>
        </li>
        <li><strong>Read Section 1.2.</strong></li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] <code>ros2 pkg executables lab07_crazyflie</code> lists four executables.</li>
        <li>[ ] <code>ros2 launch lab07_crazyflie sim.launch.py</code> shows the arena and prints <code>Hover bridge ready</code>.</li>
        <li>[ ] <code>python3 check_gains.py</code> prints <code>gains.yaml looks right.</code></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1: Bring Up the Simulation</h3>
        <p><strong>Goal:</strong> the simulation in one container shell and a shell for your flights in another.</p>
        <p>Start the container (pre-lab step 3) and open a second shell from a new Host VM Terminal with <code>docker exec -it lab07 bash</code>. <strong>Prepare</strong> both by moving to your repository and sourcing your workspace:</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-07-* &amp;&amp; source ros2_ws/install/setup.bash</code></pre>
        <p>If the shell prints <code>No such file or directory</code>, check that you are in the intended repository and that the pre-lab build (step 4) completed there. Complete the build if needed.</p>
        <h4>Step 1.1: Terminal 1, the simulation</h4>
        <pre><code class="language-bash">ros2 launch lab07_crazyflie sim.launch.py</code></pre>
        <p><strong>Checkpoint:</strong> the arena appears and the terminal prints <code>Hover bridge ready</code>. Leave it running for the whole lab.</p>
        <details>
            <summary>Why? What this launch starts</summary>
            <p>Gazebo with the arena and the Crazyflie; a bridge that carries velocity commands, the drone&rsquo;s position, and the simulation clock between ROS 2 and Gazebo; and the <strong>hover bridge</strong>. The hover bridge stands in for parts of the real system: it holds the height the controller asks for, as the real drone&rsquo;s firmware does, and it publishes the drone&rsquo;s position, as the lab&rsquo;s positioning system does. It is not run in Lab 8.</p>
        </details>
        <h4>Step 1.2: Terminal 2, your flights</h4>
        <p>Terminal 2 stays in the repository root, the folder that holds <code>gains.yaml</code>. Every command in Parts 2 to 6 runs there. Check the starting gains:</p>
        <pre><code class="language-bash">python3 check_gains.py</code></pre>
        <p><strong>Checkpoint:</strong> <code>gains.yaml looks right.</code> followed by <code>kp = 0.4  ki = 0  kd = 0</code> for x and for y.</p>
    </section>
    <section id="part2">
        <h3>Part 2: Milestone 1, A Baseline Step Test (Worked Example)</h3>
        <p><strong>Goal:</strong> predict the response with the starting gains, fly a step test, and compare the measurements with your prediction.</p>
        <p><strong>Predict first.</strong> With <code>kp = 0.4</code> and the other gains zero, the command is 0.4 m/s for each meter of error. For a 0.6 m step, write down the speed commanded at the start, the speed commanded when half the distance is left, and whether you expect the drone to be within 5 cm of the goal after 6 s.</p>
        <details>
            <summary>Hint 1: A model for the last part</summary>
            <p>If the drone moved at exactly the commanded speed, the error would shrink as 0.6 &times; e<sup>&minus;kp &times; t</sup> meters, with t in seconds.</p>
        </details>
        <h4>Step 2.1: Fly</h4>
        <pre><code class="language-bash">ros2 launch lab07_crazyflie fly.launch.py course:=step</code></pre>
        <p><strong>Checkpoint:</strong> the drone takes off, moves 0.6 m along x and back, then along y and back, and lands. The terminal lists five waypoints. Near the end, just above the lines saying the two processes have finished, it prints:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>[mission-2] Saved runs/step_01.csv (660 samples)
[mission-2]   gains: pid_x.kp=0.4  pid_x.ki=0  pid_x.kd=0  pid_y.kp=0.4  pid_y.ki=0  pid_y.kd=0</code></pre>
        </div>
        <details>
            <summary>Why? What one flight does</summary>
            <p>The launch puts the drone back at the origin, starts the controller with the gains in <code>gains.yaml</code>, flies the course, lands, and stops. Each flight is saved in <code>runs/</code> under the next free number, with the latest gains recorded at the top of the file. Recorded times use the simulation clock, so they measure elapsed simulation time even when the VM runs the simulation slower than real time.</p>
        </details>
        <h4>Step 2.2: Measure</h4>
        <pre><code class="language-bash">ros2 run lab07_crazyflie analyze</code></pre>
        <p><strong>Checkpoint:</strong> one row for x and one for y, and a plot saved as <code>runs/step_01.png</code>:</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>Step tests (band = 5 cm)
run           axis       kp     ki     kd  draft   rise s  overshoot %  settle s  ss error cm
step_01       x         0.4      0      0      0        -          0.0         -         14.8
step_01       y         0.4      0      0      0        -          0.0         -         14.8</code></pre>
        </div>
        <p>A dash means the run does not contain that number. Here the drone never reached 90% of the step, so there is no rise time, and it never stayed within the band, so there is no settling time. Open <code>runs/step_01.png</code> in VS Code and compare it with your prediction.</p>
        <p><em>Example (your numbers should match these closely):</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab07/s02-baseline-step.png" alt="The baseline step test: x and y against time with the goal as a dashed line and a 5 centimeter band. Each response climbs slowly toward the goal and is still about 15 centimeters short when the goal moves back" style="max-width: 100%; height: auto;" /></p>
        <p><strong>For your PDF:</strong> your prediction, the table, the plot, and one or two sentences on where the prediction and the measurement agree or differ.</p>
    </section>
    <section id="part3">
        <h3>Part 3: Milestone 2, The Proportional Gain</h3>
        <p><strong>Goal:</strong> measure how raising <code>kp</code> changes the response and find where rise time stops improving.</p>
        <p>To change a gain, edit <code>gains.yaml</code>, save it, and fly the step test again. Keep the x and y gains equal and keep <code>ki</code> and <code>kd</code> at <code>0.0</code> in this milestone; milestone 5 lifts both restrictions.</p>
        <p><strong>Contract:</strong> choose different values of <code>kp</code> and fly at least five step tests that together show:</p>
        <ul>
            <li>(a) the smallest <code>kp</code>, to one significant figure, above which doubling it changes the rise time by less than 0.05 s;</li>
            <li>(b) a <code>kp</code> whose overshoot is more than 3%;</li>
            <li>(c) a <code>kp</code> that never settles.</li>
        </ul>
        <p>Experiments may use gains above the submission limits. <code>check_gains.py</code> reports gains above <code>kp</code> 10, <code>ki</code> 5, or <code>kd</code> 2 as problems, because those limits apply to the file you submit in milestone 5; a flight with a larger value still runs.</p>
        <p>If the simulated drone oscillates or crashes, record the gain and the observed behavior. A crash is reported in the terminal and marked in the table, and the next flight resets the drone to the origin.</p>
        <details>
            <summary>Hint 1: Choosing values</summary>
            <p>Roughly double <code>kp</code> each time until the behavior changes, then fill in between the last two values.</p>
        </details>
        <details>
            <summary>Hint 2: Why the rise time stops improving</summary>
            <p>The velocity command cannot exceed 0.707 m/s. For what size of error does <code>kp &times; error</code> reach that limit at each of your gains?</p>
        </details>
        <p>Measure all the runs:</p>
        <pre><code class="language-bash">ros2 run lab07_crazyflie analyze</code></pre>
        <p>Then overlay the three runs that show (a), (b), and (c). Put your own run names, such as <code>step_04</code>, in place of <code>RUN_A</code>, <code>RUN_B</code>, and <code>RUN_C</code>:</p>
        <pre><code class="language-bash">ros2 run lab07_crazyflie analyze runs/RUN_A.csv runs/RUN_B.csv runs/RUN_C.csv --compare docs/kp_sweep.png</code></pre>
        <p><strong>Checkpoint:</strong> <code>docs/kp_sweep.png</code> shows the responses on one set of axes, each labeled with its gains.</p>
        <p><strong>For your PDF:</strong> the table, <code>docs/kp_sweep.png</code>, and the values you found for (a), (b), and (c).</p>
    </section>
    <section id="part4">
        <h3>Part 4: Milestone 3, The Derivative Gain</h3>
        <p><strong>Goal:</strong> test how <code>kd</code> changes overshoot and identify a value that worsens the response.</p>
        <p><strong>Contract:</strong> start from your <code>kp</code> from (b). Fly step tests that show:</p>
        <ul>
            <li>the smallest <code>kd</code> you can find for which the table shows an overshoot of 2.0% or less;</li>
            <li>a larger <code>kd</code> that makes the response worse than that one, and what &ldquo;worse&rdquo; looks like in the table and the plot.</li>
        </ul>
        <details>
            <summary>Hint 1: Where to start</summary>
            <p>Try <code>kd</code> near one twentieth of your <code>kp</code>, then double it or halve it according to what the overshoot does.</p>
        </details>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> if a change to <code>gains.yaml</code> seems to do nothing, read the <code>Gains at startup</code> lines the flight prints and compare them with the file. If <code>fly.launch.py</code> says it cannot find <code>gains.yaml</code>, Terminal 2 is not in the repository root. If it says it is waiting for the simulation, look at Terminal 1. After one clean retry or 10 minutes without progress, ask a TA and show the line that disagrees with what you expected.</blockquote>
        <p><strong>For your PDF:</strong> the table rows for these runs and two or three sentences on what <code>kd</code> changed in rise time, overshoot, and settling time.</p>
    </section>
    <section id="part5">
        <h3>Part 5: Milestone 4, A Draft and the Integral Gain</h3>
        <p><strong>Goal:</strong> measure the offset a steady disturbance causes, and test what <code>ki</code> does about it.</p>
        <p>Adding <code>draft:=0.15</code> to a flight adds a steady world-frame velocity command of 0.15 m/s along both +x and +y. For this milestone set <code>kp</code> to <code>3.0</code> and <code>kd</code> to <code>0.0</code> on both axes.</p>
        <p><strong>Predict first.</strong> With <code>ki = 0</code>, a steady position requires the controller&rsquo;s command to cancel the draft. Predict the distance from the goal at that position.</p>
        <pre><code class="language-bash">ros2 launch lab07_crazyflie fly.launch.py course:=step draft:=0.15</code></pre>
        <p><strong>Contract:</strong> in the draft, fly one step test with <code>ki = 0.0</code> and at least two with different non-zero values of <code>ki</code>. For each, record the steady-state error and the overshoot. Then open the plot of one run with <code>ki</code> (its <code>runs/step_NN.png</code>) and compare two parts of the x trace: while y steps and the x goal stays where it is, and just after x steps.</p>
        <details>
            <summary>Hint 1: Choosing values</summary>
            <p>Start with a <code>ki</code> near half of <code>kp</code>, then try a value several times smaller or larger. You may test both if needed.</p>
        </details>
        <details>
            <summary>Hint 2: Reading one plot two ways</summary>
            <p>During a y step the x goal does not move, so the x trace shows how the controller holds a position in the draft. After an x step it shows the response to a changed position goal. Compare how the accumulated error affects the response in each case. The controller clears the accumulated error on both axes whenever either goal changes, so each part starts from zero.</p>
        </details>
        <p>Overlay a draft run without <code>ki</code> and one with it. Put your own run names in place of <code>NO_KI</code> and <code>WITH_KI</code>:</p>
        <pre><code class="language-bash">ros2 run lab07_crazyflie analyze runs/NO_KI.csv runs/WITH_KI.csv --compare docs/draft_ki.png</code></pre>
        <p><strong>For your PDF:</strong> the prediction and the measured steady-state error, the table rows, <code>docs/draft_ki.png</code>, and what you saw in the two parts of the x trace.</p>
    </section>
    <section id="part6">
        <h3>Part 6: Milestone 5, Gains for the Course</h3>
        <p><strong>Goal:</strong> choose the gains you will submit, by flying the hoop course.</p>
        <p>The course passes through the hoops and returns to the start. The mission advances when the position error is less than 5 cm on every axis; a waypoint not reached in 15 s is skipped and counted. Fly it without a draft:</p>
        <pre><code class="language-bash">ros2 launch lab07_crazyflie fly.launch.py course:=course</code></pre>
        <pre><code class="language-bash">ros2 run lab07_crazyflie analyze</code></pre>
        <p>The course table gives each run&rsquo;s gains, its time, <code>off path</code> (the largest horizontal distance between the drone and the straight line joining the waypoints it was flying between), and <code>not reached</code> (the number of waypoints skipped).</p>
        <p><strong>Contract:</strong></p>
        <ul>
            <li>Fly the course with at least three different sets of gains, including one that does not reach every waypoint. The x and y gains may differ, and any of the three terms may be used.</li>
            <li>Put your chosen gains in <code>gains.yaml</code> and fly the course with them once more, adding <code>run:=final</code> to the launch command. That run must reach every waypoint and take 45 s or less.</li>
            <li><code>python3 check_gains.py</code> prints <code>gains.yaml looks right.</code> The submission limits are <code>kp</code> 10, <code>ki</code> 5, and <code>kd</code> 2, because the submitted file is used on a real drone.</li>
        </ul>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> <code>Waypoint N not reached in 15 s</code> means the drone did not reach the waypoint tolerance before the timeout; collision or oscillation may be the cause. Open that run&rsquo;s plot in <code>runs/</code> and inspect the motion near the skipped waypoint. Use your measurements from milestones 2 to 4 to decide which gain to change. After two attempts without a complete course, ask a TA and show the plot.</blockquote>
        <p><strong>Checkpoint:</strong> the <code>final</code> row of the course table shows your gains, a time of 45 s or less, and <code>0</code> under <code>not reached</code>. Copy its plot for your report:</p>
        <pre><code class="language-bash">cp runs/final.png docs/course_final.png</code></pre>
        <p><strong>Design justification</strong> (a short paragraph in your PDF): the gains you chose; one set you rejected, with its numbers from the course table; how far your gains are from the ones that failed; and what you gave up for that margin. Include the course table and <code>docs/course_final.png</code>.</p>
            </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p><strong>Where the answers go:</strong> in your Gradescope PDF, after the milestone 5 justification. All four are graded. Answer each in a few sentences from your own runs.</p>
    <h3>Question 1: The velocity limit</h3>
    <ul>
        <li>In milestone 2, above some <code>kp</code> the rise time stopped improving. From the 0.707 m/s limit and the 0.6 m step, estimate the shortest possible rise time and compare it with your fastest measured one. Then, from the plot of one of your fastest runs, measure the drone&rsquo;s speed in the middle of the step and compare it with the limit. What do the two comparisons tell you about the simulated drone, and what did raising <code>kp</code> further still change?</li>
    </ul>
    <h3>Question 2: The integral term</h3>
    <ul>
        <li>From your milestone 4 runs: how did the same <code>ki</code> affect the offset while the drone held position and the overshoot after a step? Explain any difference. What change to the controller could preserve offset correction while reducing overshoot?</li>
    </ul>
    <h3>Question 3: Course time and gains</h3>
    <ul>
        <li>From your course table: how much did the course time change between your working sets of gains, and why so little or so much? What ended the run for the gains that failed?</li>
    </ul>
    <h3>Question 4: Prediction for Lab 8</h3>
    <ul>
        <li>Your <code>gains.yaml</code> will be flown on a real Crazyflie. Name two things about the real drone or the room that this simulation leaves out. For each, predict which of the four step-response numbers it changes and in which direction. Keep your answer; Lab 8 asks you to check it against the measured flight.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Recurring setup, Docker, ROS 2, and simulation problems are on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#gazebo-and-crazyflie-simulation" target="_blank" rel="noopener">Troubleshooting</a>. For this lab: a terminal that cannot find the package, a black or missing Gazebo window, a flight that waits for the simulation, a change to <code>gains.yaml</code> that has no effect, a drone that crashed, a waypoint that was not reached, and a <code>gains.yaml</code> the launch will not accept (run <code>check_gains.py</code> first).</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://fbswiki.org/wiki/index.php/Main_Page" target="_blank" rel="noopener">&Aring;str&ouml;m and Murray, <em>Feedback Systems</em></a> (free online; the PID control chapter covers windup)</li>
        <li><a href="https://www.youtube.com/user/ControlLectures" target="_blank" rel="noopener">Brian Douglas, Control System Lectures</a></li>
        <li><a href="https://github.com/bitcraze/crazyflie-simulation" target="_blank" rel="noopener">Bitcraze crazyflie-simulation</a> (the simulated drone)</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: build and source reminders, ROS 2 CLI checks, Git and Docker commands.</li>
        <li><code>ros2 run lab07_crazyflie analyze --help</code> lists the options of the measuring tool, including <code>--band</code> for a different settling band.</li>
        <li>A gain can also be changed during a flight, for example <code>ros2 param set /goal_controller pid_x.kp 2.5</code> from a third container shell. If it answers <code>Node not found</code>, run <code>ros2 node list</code> once and try again. The recording keeps the gains in use when the flight ended. <code>gains.yaml</code> is not changed, so put a value you want to keep into the file.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
