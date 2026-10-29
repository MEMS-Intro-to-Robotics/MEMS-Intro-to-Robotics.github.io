---
title: "Lab 08: Real Hardware Drone Control"
---

# Lab 08: Real Hardware Drone Control

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Checklist</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1: Your Flight</a></li>
                <li><a href="#part2">Part 2: Load and Filter the Recording</a></li>
                <li><a href="#part3">Part 3: Split the Flight into Legs</a></li>
                <li><a href="#part4">Part 4: Measure Each Leg</a></li>
                <li><a href="#part5">Part 5: Compare with the Baseline</a></li>
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
    <p>Course staff fly the <code>gains.yaml</code> from your Lab 7 repository on a real Crazyflie 2.1 through a fixed waypoint course. You receive the recording of that flight and the recording of a baseline flight that staff flew over the same course. You measure both flights, compare them, and check the predictions you made in Lab 7 Question 4.</p>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>The lab at a glance</strong>
        <table style="border-collapse: collapse; width: 100%; margin-top: 0.5em;">
            <tr><td style="padding: 4px 8px;"><strong>Pre-lab</strong></td><td style="padding: 4px 8px;">Check the gains that will fly, accept and clone Lab 8, and check the analysis tools.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 1</strong></td><td style="padding: 4px 8px;">Staff fly your gains. You receive your run folder and the baseline folder.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 2</strong></td><td style="padding: 4px 8px;">Load the recording and filter the position.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 3</strong></td><td style="padding: 4px 8px;">Split the flight into one leg per waypoint.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 4</strong></td><td style="padding: 4px 8px;">Measure leg time, overshoot, and off-path distance for each leg.</td></tr>
            <tr><td style="padding: 4px 8px;"><strong>Part 5</strong></td><td style="padding: 4px 8px;">Compare with the baseline and recommend one gain change.</td></tr>
        </table>
    </div>
        <h3>1.2 Background</h3>
    <p><strong>What flies your gains.</strong> The controller is the same kind as in Lab 7: a node called <code>goal_controller</code>, one PID per horizontal axis, running ten times a second, with each velocity command limited to 0.707 m/s. It runs on the lab PC, not on the drone. Each cycle it reads the drone&rsquo;s position, computes a velocity command for x and y from your gains, and sends that command over the radio together with the height of the current waypoint. The drone&rsquo;s own firmware, unchanged from the manufacturer&rsquo;s, turns the command into motion and holds the height with its own control loops. As in Lab 7, your gains set only the horizontal velocity command.</p>
    <p><strong>Where the position comes from.</strong> Two Lighthouse base stations on stands sweep the flight area with infrared light. A sensor deck on the drone detects the sweeps, and the drone&rsquo;s onboard estimator combines them with its motion sensors to estimate its position. The estimate reaches the lab PC over the radio ten times a second. In Lab 7 the controller read the simulator&rsquo;s exact position; here it reads a measurement that has noise and arrives with a delay.</p>
    <p><strong>What changes between Lab 7 and Lab 8.</strong> Staff divide each <code>kp</code> by 1.9 before the flight; <code>ki</code> and <code>kd</code> fly as you submitted them. In Lab 7 the simulated drone moved at about half the commanded speed (about 0.365 m/s when the controller asked for 0.707 m/s). Dividing <code>kp</code> by 1.9 compensates approximately for that, assuming the real drone follows the velocity command more closely. It does not account for differences in delay or noise, and <code>ki</code> and <code>kd</code> are not adjusted. Question 3 asks how well your flight supports that assumption. No other change is made: your gains are not clamped, and the Lab 7 submission limits (<code>kp</code> 10, <code>ki</code> 5, <code>kd</code> 2) are the only bounds on them. Before each flight the TA reads the gains that will fly and confirms them.</p>
    <p><strong>The course.</strong> The drone takes off to 0.3 m above the origin mark, and then the course starts. The goal moves to the next waypoint when the drone is within 5 cm of the current one on every axis, and a waypoint not reached in 15 s is skipped, as in the Lab 7 hoop course. The goal also waits for the drone&rsquo;s heading to be within 0.1 rad of facing +x, which it usually already is. After waypoint 13 the drone lands. The origin is the mark the drone takes off from, and +x is the direction it faces at takeoff.</p>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 1em;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ccc; padding: 6px;">Waypoint</th>
                <th style="border: 1px solid #ccc; padding: 6px;">x (m)</th>
                <th style="border: 1px solid #ccc; padding: 6px;">y (m)</th>
                <th style="border: 1px solid #ccc; padding: 6px;">z (m)</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Leg to this waypoint</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">1</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0.30</td><td style="border: 1px solid #ccc; padding: 6px;">start: hold over the origin</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">2</td><td style="border: 1px solid #ccc; padding: 6px;">0.447</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0.30</td><td style="border: 1px solid #ccc; padding: 6px;">+x, 0.45 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">3</td><td style="border: 1px solid #ccc; padding: 6px;">0.447</td><td style="border: 1px solid #ccc; padding: 6px;">0.650</td><td style="border: 1px solid #ccc; padding: 6px;">0.33</td><td style="border: 1px solid #ccc; padding: 6px;">+y, 0.65 m (and 3 cm up)</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">4</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0.650</td><td style="border: 1px solid #ccc; padding: 6px;">0.33</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;x, 0.45 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">5</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.568</td><td style="border: 1px solid #ccc; padding: 6px;">0.33</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;y, 1.22 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">6</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;1.12</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.568</td><td style="border: 1px solid #ccc; padding: 6px;">0.33</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;x, 1.12 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">7</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;1.12</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.20</td><td style="border: 1px solid #ccc; padding: 6px;">0.33</td><td style="border: 1px solid #ccc; padding: 6px;">+y, 0.37 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">8</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.648</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.20</td><td style="border: 1px solid #ccc; padding: 6px;">0.33</td><td style="border: 1px solid #ccc; padding: 6px;">+x, 0.47 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">9</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.648</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.20</td><td style="border: 1px solid #ccc; padding: 6px;">1.00</td><td style="border: 1px solid #ccc; padding: 6px;">climb, 0.67 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">10</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.648</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.76</td><td style="border: 1px solid #ccc; padding: 6px;">1.00</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;y, 0.56 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">11</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">&minus;0.76</td><td style="border: 1px solid #ccc; padding: 6px;">1.00</td><td style="border: 1px solid #ccc; padding: 6px;">+x, 0.65 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">12</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">1.00</td><td style="border: 1px solid #ccc; padding: 6px;">+y, 0.76 m</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;">13</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0</td><td style="border: 1px solid #ccc; padding: 6px;">0.30</td><td style="border: 1px solid #ccc; padding: 6px;">descent, 0.70 m</td></tr>
        </tbody>
    </table>
    <p>Each horizontal leg moves the goal along one horizontal axis (leg 3 also raises it 3 cm). The climb (leg 9) and the descent (leg 13) move only the height. The firmware controls height throughout the course, and your gains control horizontal position, including holding it during the climb and the descent. You did not tune height in Lab 7 and do not tune it in this lab; your <code>gains.yaml</code> has gains for x and y only. Height error RMS measures how closely the recorded height follows the height goal.</p>
    <p>Baseline flight path viewed from above, with numbered waypoints:<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab08/s01-course-from-above.png" alt="Top-down plot of the course: dashed straight lines join the 13 numbered waypoints, which form a rectangle at positive x and y and a second loop at negative x and y, joined at the origin; the measured path follows the lines and runs past each corner before turning" style="max-width: 100%; height: auto;" /></p>
        <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>By the end of this lab, you should be able to:</p>
    <ul>
        <li><strong>Filter</strong> a recorded position signal and <strong>justify</strong> the filter from its effect on the data.</li>
        <li><strong>Split</strong> a waypoint flight into legs from the recorded goal and <strong>measure</strong> leg time, rise time, overshoot, and off-path distance for each.</li>
        <li><strong>Compare</strong> your flight with a baseline flight leg by leg and <strong>explain</strong> the largest differences.</li>
        <li><strong>Evaluate</strong> your Lab 7 predictions against the measured flight.</li>
        <li><strong>Explain</strong> how the hardware setup (position measurement, the controller rate, the <code>kp</code> division) affects the conclusions you can draw about your tuning.</li>
        <li><strong>Recommend</strong> one gain change and support it with your measurements.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Checklist</h2>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab.</strong> Complete this section on your own time before your flight.</div>
    <p>VMs power off 4 hours after the reservation starts; keep your work in <code>~/workspaces</code>. Git runs on the VM, Python runs in the container, and you edit in VS Code on the VM, as in Lab 7.</p>
    <ol>
        <li><strong>Check the gains that will fly.</strong> Before the flight sessions, staff copy the latest <code>gains.yaml</code> from your Lab 7 repository, and that copy is what flies. You may still change it: run <code>python3 check_gains.py</code> as in Lab 7 and push the change before the sessions. Lab 7 is graded from your repository as it was at its due date, so a later change does not affect your Lab 7 grade. You do not send your gains to anyone. After the flight, <code>pid_flown.yaml</code> in your run folder shows the values that flew, with each <code>kp</code> divided by 1.9. If you have no Lab 7 repository, staff fly the Lab 7 starting gains (<code>kp</code> 1.0, <code>ki</code> 0, <code>kd</code> 0 on x and y).
                                </li>
        <li><strong>Find your Lab 7 Question 4 answer</strong> (your two predictions for the real drone) and the table and plot of your Lab 7 step test with gains closest to your final ones. Question 1 uses both.</li>
        <li><strong>Accept Lab 8 and clone it.</strong>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-08</code></pre>
            <p>Clone into <code>~/workspaces</code> with the command it prints. The repository is named <code>intro-to-robotics-fall-2026-lab-08-</code> followed by your GitHub username. If <code>gh student</code> is missing or not signed in, repeat the Lab 1 setup (<code>gh extension install foundation50/gh-student</code>, then <code>gh student login</code>).</p>
        </li>
        <li><strong>Start the container and check the analysis tools.</strong> Use the Lab 7 image (pull it again if you pruned it for another lab):
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">xhost +local:docker
docker run --rm -it --name lab08 --net=host -e DISPLAY=$DISPLAY -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v ~/workspaces:/root/workspaces ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:crazyflie-jazzy-latest</code></pre>
            <p>This is the Lab 7 command without <code>--gpus all</code>, which this lab does not need.</p>
            <p><strong>Location:</strong> Container Terminal</p>
            <pre><code class="language-bash">python3 -c "import numpy, pandas, scipy, matplotlib, yaml; print('ok')"</code></pre>
            <p><strong>Checkpoint:</strong> <code>ok</code>. Exiting this terminal deletes the container; files in <code>~/workspaces</code> stay.</p>
            <p>If you see <code>ModuleNotFoundError</code> or the container fails to start, exit the container if it is running, pull the image again, and repeat this step:</p>
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:crazyflie-jazzy-latest</code></pre>
            <p>If it still fails, ask a TA and show the command and its output.</p>
                    </li>
    </ol>
    <p><strong>Ready for lab when:</strong></p>
    <ul>
        <li>[ ] Your Lab 8 repository is cloned into <code>~/workspaces</code>.</li>
        <li>[ ] <code>python3 -c "import numpy, pandas, scipy, matplotlib, yaml; print('ok')"</code> prints <code>ok</code> in the container.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1: Your Flight</h3>
        <p><strong>Goal:</strong> your gains flown once through the course, and your run folder and the baseline folder in your repository.</p>
        <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;">Staff fly every flight. Stay outside the netting around the flight area whenever the drone is switched on.</div>
        <h4>Step 1.1: What happens at the flight</h4>
        <ol>
            <li>The TA places the drone on the origin mark facing +x and starts the flight script with your <code>gains.yaml</code>.</li>
            <li>The script prints a table of your submitted gains and the gains it will fly. Check that it matches the <code>gains.yaml</code> in your Lab 7 repository.</li>
            <li>The script checks the battery and reads the drone&rsquo;s position from the Lighthouse. It prevents takeoff if the battery is low or the measured position is too far from the origin.</li>
            <li>When everyone is outside the flight area, the TA confirms. The drone takes off to 0.3 m, flies the course, and lands.</li>
        </ol>
        <p>The TA stops the flight and lands the drone if it leaves the course area or wobbles badly. The script also ends an unfinished course after 120 s. The recording up to the stop is kept.</p>
                <h4>Step 1.2: If your flight was stopped</h4>
        <p>If the flight was stopped for a reason unrelated to your gains, such as lost tracking, a low battery, or a lost radio link, staff fly your gains again. If it was stopped because of how the drone responded to your gains, you analyze the partial recording: measure the legs that were completed, and describe what happened in the leg where it was stopped. Your metrics table then covers only the completed legs, and the missing legs cost no points. The TA who stopped the flight decides which case it was, and writes the reason in <code>notes.txt</code> in your run folder.</p>
                
        <h4>Step 1.3: Get the folders</h4>
        <p>After your lab section, course staff add two folders to <code>data/</code> in your Lab 8 repository: your run folder, named with your GitHub username, and the baseline folder, named <code>baseline</code>. Your clone on the VM does not have them until you pull. Before you start Part 2, run:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-08-* &amp;&amp; git pull</code></pre>
        <p>If <code>git pull</code> prints <code>Already up to date.</code> and <code>data/</code> holds only <code>.gitkeep</code>, staff have not added your folders yet; check again later, and ask a TA if they are still missing the day after your section.</p>
        
        <p><strong>Checkpoint:</strong> <code>data/YOUR_GITHUB_USERNAME/</code> and <code>data/baseline/</code> each hold these files (the baseline folder also has a <code>README.md</code>, described in Part 5):</p>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 0.5em;">
            <tbody>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>trajectory_log.csv</code></td><td style="border: 1px solid #ccc; padding: 6px;">the recording (columns in Part 2)</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>traj_xyz_time.png</code>, <code>traj_xy_path.png</code></td><td style="border: 1px solid #ccc; padding: 6px;">quick-look plots of position against time and of the path seen from above</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>gains_submitted.yaml</code></td><td style="border: 1px solid #ccc; padding: 6px;">the <code>gains.yaml</code> staff received</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>pid_flown.yaml</code></td><td style="border: 1px solid #ccc; padding: 6px;">the gains the controller used (<code>kp</code> already divided by 1.9) and its other settings</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>course_waypoints.yaml</code></td><td style="border: 1px solid #ccc; padding: 6px;">the waypoints of the course that was flown, in order, as <code>[x, y, z, yaw]</code></td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>battery.txt</code></td><td style="border: 1px solid #ccc; padding: 6px;">the battery voltage before takeoff and after landing</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>notes.txt</code></td><td style="border: 1px solid #ccc; padding: 6px;">the TA&rsquo;s reason for stopping the flight; included only if it was stopped</td></tr>
                <tr><td style="border: 1px solid #ccc; padding: 6px;"><code>launch.log</code></td><td style="border: 1px solid #ccc; padding: 6px;">the controller&rsquo;s messages: each <code>Goal #N/13</code>, a <code>Goal timeout. Advancing.</code> line for each skipped waypoint, and a summary</td></tr>
            </tbody>
        </table>
        <p>The summary at the end of <code>launch.log</code> includes an RMS error measured from the current waypoint. After a goal change, this error includes the distance to the new waypoint, even if the drone is on the intended path. This lab uses the leg-by-leg metrics defined below.</p>
    </section>
    <section id="part2">
        <h3>Part 2: Load and Filter the Recording</h3>
        <p><strong>Goal:</strong> the recording loaded in Python, with a light filter on the position that you can justify.</p>
        <p><code>trajectory_log.csv</code> has seven columns:</p>
        <ul>
            <li><code>time_s</code>: seconds since the course started, shortly after takeoff. Recording may begin a second or two later.</li>
            <li><code>x</code>, <code>y</code>, <code>z</code>: the drone&rsquo;s measured position in meters.</li>
            <li><code>gx</code>, <code>gy</code>, <code>gz</code>: the waypoint the drone was flying to, in meters. After the drone reaches waypoint 13 they are empty (<code>NaN</code>).</li>
        </ul>
        <p>Rows are recorded about 20 times a second, and the position is updated about 10 times a second, so consecutive rows often hold the same position. Use <code>time_s</code> for every time measurement rather than assuming a fixed interval between rows. There are no attitude or battery columns.</p>
        
        <h4>Step 2.1: Load</h4>
        <p>Your repository&rsquo;s <code>analysis/lab08_analysis.py</code> already has <code>load_run</code>, which reads the CSV and drops the rows whose goal is empty, and <code>split_legs</code> (Part 3). Run the script once in the container started in pre-lab step 4, with your GitHub username in place of <code>YOUR_GITHUB_USERNAME</code>:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-08-* &amp;&amp; python3 analysis/lab08_analysis.py --run data/YOUR_GITHUB_USERNAME --baseline data/baseline --outdir docs</code></pre>
        <p><strong>Checkpoint:</strong> two lines, <code>your flight: [1, 2, ..., 13]</code> (or starting at 2) and <code>baseline:    [2, 3, ..., 13]</code>. If the script reports <code>No such file or directory</code>, check that <code>data/</code> holds your folders (Step 1.3) and that you typed your username as the folder is named.</p>
        <h4>Step 2.2: Filter</h4>
        <p>Write <code>apply_filter</code>. Apply one light filter to <code>x</code>, <code>y</code>, and <code>z</code>: a median or moving-average filter over 3 to 5 rows, or a second-order Butterworth low-pass filter with a cutoff of about 3 Hz and a sample rate of 20 Hz. Apply the Butterworth filter with <code>scipy.signal.filtfilt</code> for zero-phase filtering. Filtering can still alter peaks and the ends of the recording. Use filtered position for the position-based metrics in Part 4; use the recorded times and goal changes for leg times and skipped waypoints.</p>
        <p>The drone&rsquo;s estimator already smooths position, so filtering may have little effect. Compute one metric with and without the filter. A small change is an acceptable justification if you report its size.</p>
        <p><strong>For your PDF:</strong> one plot of raw and filtered position for one axis over one leg, saved as <code>docs/03_raw_vs_filtered.png</code>, and one or two sentences justifying your filter choice using the plot and metric comparison.</p>
    </section>
    <section id="part3">
        <h3>Part 3: Split the Flight into Legs</h3>
        <p><strong>Goal:</strong> the flight split into one segment per waypoint, each labeled with its waypoint number and the axis that moves.</p>
        <p>Read <code>split_legs</code> in the starter before using it. It starts a new segment at each row where <code>gx</code>, <code>gy</code>, or <code>gz</code> differs from the row before, so each segment is the leg flown to one waypoint, including a waypoint that was skipped. It numbers each segment by matching its goal to <code>course_waypoints.yaml</code>, working through the list in order, because waypoints 1 and 13 are the same point. For each segment it returns the waypoint number, the axis that moves, the direction of travel (+1 or &minus;1), and the segment&rsquo;s first and last rows.</p>
        <p>If the drone came within 5 cm of waypoint 1 before recording started, the recording begins with waypoint 2 and has no segment for waypoint 1, as in the baseline.</p>
        <p><strong>Checkpoint:</strong> the segment numbers printed in Step 2.1 increase in order and end with 13. A complete course has 12 or 13 segments; a flight that was stopped may have fewer. If <code>split_legs</code> stops with <code>matches no remaining waypoint</code>, the files in <code>data/</code> may have been changed. Restore them with <code>git checkout -- data</code> on the VM, and ask a TA if the message remains.</p>
        <p><em>Example: the baseline flight</em><br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab08/s02-baseline-position.png" alt="x, y, and z of the baseline flight against time, each with the goal as a dashed line and a grey vertical line at every goal change, the segments numbered 2 to 13 along the top (this recording starts at waypoint 2). After most goal changes the position on the axis that just finished keeps going past its goal for a few centimeters before settling, and z rises to about 1.15 m after the climb to 1.0 m" style="max-width: 100%; height: auto;" /></p>
        <p>Use the ten horizontal legs (2 to 8 and 10 to 12) for the metrics in Part 4.</p>
    </section>
    <section id="part4">
        <h3>Part 4: Measure Each Leg</h3>
        <p><strong>Goal:</strong> five numbers for each horizontal leg, and two for the whole course.</p>
        <p>The goal advances when the drone first meets the waypoint conditions, including being within 5 cm on every axis. The drone is usually still moving, so measure overshoot and rise time over a <em>window</em> from the leg&rsquo;s first row to 2 s after the next goal change, or the next segment&rsquo;s end, whichever comes first. The goal on the leg&rsquo;s axis stays unchanged throughout this window.</p>
        <p>For each horizontal leg:</p>
        <ul>
            <li><strong>Leg time (s):</strong> the length of the segment, from its goal change to the next one. A leg lasting about 15 s may have timed out. Confirm skipped waypoints from the timeout messages in the log and mark them as skipped in your table.</li>
            <li><strong>Rise time (s):</strong> the time between the first rows reaching 10% and 90% of the leg&rsquo;s length within the window, as in Lab 7.</li>
            <li><strong>Overshoot (cm):</strong> the farthest distance past the waypoint along the leg&rsquo;s direction within the window. If the drone never passed the waypoint, the overshoot is 0.</li>
            <li><strong>Off-path RMS (cm):</strong> the RMS of the position error on the other horizontal axis during the leg. This measures the horizontal distance from the intended line of travel. Overshoot from the previous leg can contribute to this error at the start of the leg.</li>
            <li><strong>Height error RMS (cm):</strong> the RMS of the difference between <code>z</code> and <code>gz</code> during the leg. You do not tune height; the firmware controls it with the same settings in every flight, including the baseline. This metric measures how closely the recorded height followed the height goal, including any response to a height change. Use it as a reference when assessing proposed physical causes in Question 2.</li>
        </ul>
        <p>Leg 2 starts just after takeoff. In the Part 3 example, height is still recovering from a dip of up to about 15 cm. Account for any such recovery in your flight when comparing leg 2&rsquo;s height error and timing.</p>
        <p>For the whole course: the <strong>course time</strong> and the <strong>number of skipped waypoints</strong>. Course time runs from advancing past waypoint 1 to reaching waypoint 13. Read it from <code>launch.log</code>, using the third bracketed field as the time in seconds, for example <code>[trajectory_publisher-2] [INFO] [1792536265.128681509]</code>. Course time is the time on the first <code>Advancing.</code> line after <code>Goal #13/</code>, minus the time on <code>Goal #2/</code>. Reaching a waypoint requires being within 5 cm on every axis. Search for <code>Goal #2/</code> and <code>Goal #13/</code> without a number after the slash to handle the baseline log, which counts goals out of 39.</p>
                <details>
            <summary>Hint 1: Overshoot for a leg in the &minus;x or &minus;y direction</summary>
            <p>Multiply both the position along the leg&rsquo;s axis and the waypoint coordinate by the sign of the leg&rsquo;s direction (+1 or &minus;1). Overshoot occurs when the transformed position exceeds the transformed waypoint coordinate.</p>
        </details>
        <details>
            <summary>Hint 2: Checking a leg by eye</summary>
            <p>Plot one axis against time with its goal and mark the start of each segment with a vertical line. Look for the position crossing the goal line in the direction of travel, usually just after the next segment starts. Part 3 shows this plot for the baseline flight.</p>
        </details>
        <p><strong>Checkpoint:</strong> the number of skipped waypoints matches the number of <code>Goal timeout</code> lines in <code>launch.log</code>, and each overshoot you computed matches what the plot in Hint 2 shows for that leg.</p>
    </section>
    <section id="part5">
        <h3>Part 5: Compare with the Baseline</h3>
        <p><strong>Goal:</strong> a leg-by-leg table of your flight against the baseline, and one recommended gain change.</p>
        <p>The baseline folder has the same files as yours. Its gains were <code>kp</code> 2.5, <code>ki</code> 0, and <code>kd</code> 0.05 on x and y, without division by 1.9. Read them from its <code>pid_flown.yaml</code>. Staff flew the baseline gains eight times around the course. The course times ranged from 18.2 to 19.8 s, with a mean of 19.2 s; the baseline folder contains data from a lap with a course time of 19.3 s. That flight completed the course three times without landing. The baseline folder contains its first lap, so its <code>launch.log</code> differs from yours. The <code>README.md</code> in the folder explains the differences. All eight times were within 1 s of 19.2 s, so a course time within about a second of 19.2 s is consistent with the baseline gains. Run your script on it unchanged and compute the same metrics for the same legs. Match the two flights by leg number. Their leg boundaries can occur at different values of <code>time_s</code> because the leg durations can differ.</p>
        <p><strong>Metrics table:</strong> one row per metric and leg, plus the two course rows, with the columns <em>Baseline</em>, <em>Yours</em>, <em>&Delta;</em> (Yours &minus; Baseline), and <em>%&Delta;</em> (100 &times; &Delta; / Baseline), all with units. A negative &Delta; means your value is lower. Interpret leg and course times alongside skipped waypoints and tracking errors; a shorter time alone does not establish better tracking. Where the baseline value is 0, write &ldquo;n/a&rdquo; for %&Delta;.</p>
        <p><strong>Recommendation:</strong> propose one gain change on one axis in your <code>gains.yaml</code> and justify it in one or two sentences with numbers from your table. For example: &ldquo;Lower <code>kp</code> on x from 3.0 to 2.5. On legs 4, 8, and 11 my overshoot averaged 12 cm against 6 cm for the baseline, while my rise times were within 0.1 s of the baseline&rsquo;s.&rdquo;</p>
        <h4>Step 5.1: The script</h4>
        <p>Complete <code>analysis/lab08_analysis.py</code>: write the functions marked <code>TODO</code> (<code>apply_filter</code>, <code>leg_metrics</code>, <code>course_time</code>, and <code>metrics_table</code>) and finish <code>main</code>, so that one run of the command in Step 2.1 loads both folders, filters, splits, measures, and saves the table and the three figures of your flight in <code>docs/</code>. You may organize it differently, as long as that one command does all of it.</p>
        <p><strong>Checkpoint:</strong> the table prints and the three figures appear in <code>docs/</code>. Put the command in your <code>README.md</code>.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p><strong>Where the answers go:</strong> in your Gradescope PDF, after the metrics table. All four are graded. Answer each in a few sentences and cite numbers from your table.</p>
    <h3>Question 1: Your Lab 7 predictions</h3>
    <ul>
        <li>Restate your two Lab 7 Question 4 predictions. Compare rise time and overshoot (as a percentage of leg length) for legs 4, 8, and 11 with your Lab 7 step test. These legs move 0.45 to 0.65 m along x at a constant height goal, the nearest match to Lab 7&rsquo;s 0.6 m step. The flown <code>kp</code> is your Lab 7 <code>kp</code> divided by 1.9 (see Question 3). Steady-state error cannot be measured here, because the goal moves on as soon as the drone is within 5 cm of the waypoint; for a prediction about it, explain why it cannot be checked. For a prediction about settling time, compare it with leg time, which ends the first time the drone is within 5 cm rather than when it stays there. Use your data to judge each prediction and explain any disagreement.</li>
    </ul>
    <h3>Question 2: Where the hardware differed most</h3>
    <ul>
        <li>Which leg and metric differ most between your flight and the baseline, or between your flight and your Lab 7 simulation? Propose a physical cause (for example noise or delay in the position measurement, the 10 Hz position updates, air moving near the floor or walls, or the firmware&rsquo;s own response to velocity commands). Then compare the height error RMS on that leg between your flight and the baseline. You do not tune height; the firmware controls it the same way in both flights. If the height error also differs, consider a cause that affects every axis, such as the position measurement or the air around the drone; if it does not, a cause in your x and y gains is more likely.</li>
    </ul>
    <h3>Question 3: The gain transfer</h3>
    <ul>
        <li>From <code>pid_flown.yaml</code>, report the flown <code>kp</code> on each axis. Over the middle one second of leg 5 (the 1.22 m leg), measure speed as the distance traveled along y in that second and find the mean distance to the goal along y (the error). Estimate commanded speed as flown <code>kp</code> &times; error minus <code>kd</code> &times; measured speed plus <code>ki</code> &times; error added up over time since the leg began (zero if your <code>ki</code> is 0), limited to 0.707 m/s. Use the direction of travel as positive for this calculation. Divide the measured speed by the commanded speed. In Lab 7 that ratio was about 0.52 (0.365 m/s at a command of 0.707 m/s), and dividing <code>kp</code> by 1.9 assumes the real drone&rsquo;s ratio is near 1. Does your ratio support that assumption? Describe how your flight would likely have differed without the division.</li>
    </ul>
    <h3>Question 4: Tuning recommendation</h3>
    <ul>
        <li>Your one recommended change from Part 5, with its justification.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>For help analyzing recorded flights, see the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/#flight-log-analysis" target="_blank" rel="noopener">Troubleshooting</a>. It covers an empty <code>data/</code> folder, a push rejected with <code>fetch first</code>, a run folder the script cannot find, a <code>split_legs</code> error, 12 segments in place of 13, repeated rows and gaps in <code>time_s</code>, a filter that slows the response, overshoot that is 0 everywhere or too large, a course time that cannot be found in <code>launch.log</code>, and metrics that disagree with the baseline on every leg.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://github.com/foundation50/classroom50/wiki/CLI-Student-Guide" target="_blank" rel="noopener">Classroom 50 CLI Student Guide</a></li>
        <li><a href="https://www.bitcraze.io/documentation/system/positioning/ligthouse-positioning-system/" target="_blank" rel="noopener">Bitcraze, Lighthouse Positioning System</a> (how the drone measures its position)</li>
        <li><a href="https://imrclab.github.io/crazyswarm2/" target="_blank" rel="noopener">Crazyswarm2 documentation</a> (the ROS 2 driver between the lab PC and the drone)</li>
        <li><a href="https://fbswiki.org/wiki/index.php/Main_Page" target="_blank" rel="noopener">&Aring;str&ouml;m and Murray, <em>Feedback Systems</em></a> (free online; the PID control chapter)</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="appendix">
    <h2>11. Appendix: Shared References</h2>
    <ul>
        <li><a href="https://mems-intro-to-robotics.github.io/guides/quick_reference/" target="_blank" rel="noopener">Quick Reference</a>: Git and Docker commands.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
