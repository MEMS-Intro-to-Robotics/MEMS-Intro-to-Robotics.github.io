---
title: "Lab 08: Real Hardware Drone Control"
---

# Lab 08: Real Hardware Drone Control

<div class="lab-content">

<p><em>This lab transitions from simulation to hardware. You will provide your tuned PID gains, staff will execute a standardized drone flight, and you will receive a data package to analyze your controller's real-world performance against a baseline.</em></p>
<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#overview">Overview</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab Preparation</a></li>
        <li><a href="#safety">In-Lab Safety &amp; Operations</a></li>
        <li><a href="#trajectory">The Standardized Flight Trajectory</a></li>
        <li><a href="#procedure">In-Lab Procedure</a></li>
        <li><a href="#schema">Data Schema (CSV Columns)</a></li>
        <li><a href="#analysis">Post-Lab Analysis Guide</a></li>
    </ol>
</nav>
<section id="overview">
    <h2>1. Overview</h2>
    <p>This lab bridges simulation and hardware through empirical data analysis. You will provide your PID gains from the previous lab, and the lab staff will execute a standardized flight using a Crazyflie drone. You will then receive a data package sampled at <strong>20&nbsp;Hz</strong>.</p>
    <p>Your primary goal is to quantify your controller's tracking performance against the commanded goals and benchmark your results against a provided <em>Comparison Data</em> baseline. This process is central to validating control systems, where simulated performance must be proven on physical hardware.</p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>Upon successful completion of this lab, you will be able to:</p>
    <ul>
        <li>Validate controller stability and performance on a physical system using commanded trajectory data.</li>
        <li>Apply appropriate light filtering to 20&nbsp;Hz sensor data without distorting critical signal dynamics.</li>
        <li>Compute and interpret key quantitative performance metrics, including RMS error, overshoot, settling time, and path deviation.</li>
        <li>Systematically compare your controller's performance to a standard baseline and articulate the reasons for any differences.</li>
        <li>Propose a single, evidence-backed PID tuning refinement based on your quantitative analysis.</li>
    </ul>
</section>
<section id="prelab">
    <h2>4. Pre-Lab Preparation</h2>
    <ul>
        <li><strong>Finalize PID Gains:</strong> Have your final <code>x</code>, <code>y</code>, and <code>z</code> PID gains from the previous simulation lab ready. Fill them into the table below.</li>
        <li><strong>Download Comparison Data:</strong> Download the <strong>Comparison Data</strong> folder from Canvas. This contains the CSV file for the baseline controller performance.</li>
        <li><strong>Prepare Analysis Script:</strong> Set up a Python script or notebook that is ready to:
            <ul>
                <li>Load your CSV data and the baseline CSV data.</li>
                <li>Apply a light low-pass, median, or moving-average filter.</li>
                <li>Segment the flight data by detecting changes in the goal signals.</li>
                <li>Compute the required metrics and generate the comparison table.</li>
            </ul>
        </li>
    </ul>
    <p><strong>Your PID Gains (To provide in-lab):</strong></p>
    <table>
        <thead>
            <tr>
                <th>Axis</th>
                <th>Kp</th>
                <th>Ki</th>
                <th>Kd</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>x</strong></td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
            </tr>
            <tr>
                <td><strong>y</strong></td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
            </tr>
            <tr>
                <td><strong>z</strong></td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
            </tr>
        </tbody>
    </table>
    <div class="alert alert-info"><strong>Note:</strong> The baseline CSV file includes its own PID values. Your script should read these directly from the file for reporting and comparison.</div>
</section>
<section id="safety">
    <h2>5. In-Lab Safety &amp; Operations</h2>
    <div class="alert alert-warning">All flights are conducted by lab staff. Students must remain outside the flight enclosure at all times.</div>
    <h3>Flight System Safety Limits</h3>
    <p>To ensure safety, the flight controller firmware will clamp any provided gains that are outside the allowed ranges. Clamped values will be noted in your metadata file.</p>
    <ul>
        <li><strong>Proportional Gain (Kp):</strong> Clamped to <code>[0.5, 4.0]</code></li>
        <li><strong>Integral Gain (Ki):</strong> Clamped to <code>[0.0, 1.0]</code></li>
        <li><strong>Derivative Gain (Kd):</strong> Clamped to <code>[0.0, 1.0]</code></li>
    </ul>
    <h3>Automatic Flight Abort Triggers</h3>
    <p>The flight will be automatically aborted if any of the following conditions occur:</p>
    <ul>
        <li><strong>Position Error:</strong> Significant deviation from the commanded position.</li>
        <li><strong>Attitude Instability:</strong> Roll or pitch angle exceeds 35 degrees.</li>
        <li><strong>Low Battery:</strong> Battery voltage (<code>vbat</code>) drops below 3.4V.</li>
        <li><strong>System Failure:</strong> Loss of radio link or position tracking.</li>
    </ul>
</section>
<section id="trajectory">
    <h2>6. The Standardized Flight Trajectory</h2>
    <p>The drone will execute a pre-programmed trajectory designed to test key performance aspects, such as step response and path tracking. The total flight duration is approximately <strong>40&ndash;60 seconds</strong>.</p>
    <ol>
        <li>Automated takeoff to a stable hover at a designated starting point.</li>
        <li>A series of point-to-point <strong>step commands</strong> along the primary X and Y axes.</li>
        <li>Short path-following segments.</li>
        <li>Automated landing at the origin.</li>
    </ol>
    <div class="alert alert-info"><strong>Analysis Note:</strong> Your data file contains the precise reference trajectory in the <code>goal_x, goal_y, goal_z</code> columns. You do not need to manually reconstruct the path.</div>
</section>
<section id="procedure">
    <h2>7. In-Lab Procedure</h2>
    <p>Your only responsibility during the lab session is to provide your nine PID gain values. The lab staff will manage all hardware and flight operations.</p>
    <h3>Workflow</h3>
    <ol>
        <li>Check in with the lab staff and provide your PID gains.</li>
        <li>Staff will load your gains onto the drone and verify a stable hover.</li>
        <li>The standardized flight trajectory will be executed while logging data at 20&nbsp;Hz.</li>
        <li>After the automated landing, logging will be stopped.</li>
        <li>You will receive your complete data package (CSV, plots, metadata).</li>
    </ol>
    <div class="alert alert-warning"><strong>Policy:</strong> Each student is allocated one standard flight run. Live retuning or multiple attempts are not permitted.</div>
    <h3>Your Data Package</h3>
    <ul>
        <li><code>lab08log_&lt;netid&gt;_&lt;timestamp&gt;.csv</code>: Your primary data file with measured and goal positions.</li>
        <li><code>_step.png</code>: A quick-look plot of X/Y/Z position vs. time.</li>
        <li><code>_xy.png</code>: A quick-look plot of the XY flight path.</li>
        <li><code>_meta.txt</code>: A metadata file listing any gain clamps, abort reasons, or other flight notes.</li>
    </ul>
</section>
<section id="schema">
    <h2>8. Data Schema (CSV Columns)</h2>
    <p>All data is sampled at approximately <strong>20&nbsp;Hz</strong> (&Delta;t &asymp; 0.05&nbsp;s). For precise analysis, consider resampling your data to a uniform 20&nbsp;Hz time grid to handle any minor jitter.</p>
    <h3>Your Run CSV (<code>lab08log_...csv</code>)</h3>
    <ul>
        <li><strong><code>t</code></strong> &mdash; Time (seconds)</li>
        <li><strong><code>x</code>, <code>y</code>, <code>z</code></strong> &mdash; Measured position (meters)</li>
        <li><strong><code>goal_x</code>, <code>goal_y</code>, <code>goal_z</code></strong> &mdash; Commanded goal position (meters)</li>
        <li><strong><code>roll</code>, <code>pitch</code>, <code>yaw</code></strong> &mdash; Measured attitude (degrees)</li>
        <li><strong><code>vbat</code></strong> &mdash; Battery voltage (Volts)</li>
    </ul>
    <h3>Comparison Data CSV (from Canvas)</h3>
    <ul>
        <li><strong><code>t</code></strong> &mdash; Time (seconds)</li>
        <li><strong><code>x</code>, <code>y</code>, <code>z</code></strong> &mdash; Measured position of the baseline controller (meters)</li>
        <li><strong><code>goal_x</code>, <code>goal_y</code>, <code>goal_z</code></strong> &mdash; Commanded goal position (meters)</li>
        <li><strong><code>pid_x_kp, pid_x_ki, ...</code></strong> &mdash; The PID gains used for the baseline run. Read these directly for your report.</li>
    </ul>
</section>
<section id="analysis">
    <h2>9. Post-Lab Analysis Guide</h2>
    <p>Follow these steps to structure your analysis and generate the required deliverables.</p>
    <h3>A) Data Cleaning and Filtering</h3>
    <p>Raw position data can be noisy. Apply a light filter to the <code>x, y, z</code> signals to reduce this noise while preserving the dynamics of the step responses.</p>
    <ul>
        <li><strong>Acceptable filters:</strong> A median filter (window size 3&ndash;5), a moving average filter (window size 3&ndash;5), or a low-order Butterworth filter (e.g., 2nd-order with a 3&ndash;5&nbsp;Hz cutoff).</li>
        <li>In your report, briefly justify your choice of filter and show a small plot of raw vs. filtered data for one axis to illustrate its effect.</li>
    </ul>
    <h3>B) Flight Segmentation</h3>
    <p>To analyze performance metrics for different maneuvers, you must segment the data. Identify segment boundaries by detecting significant changes in the goal signals.</p>
    <ul>
        <li>A new segment begins when any of <code>goal_x, goal_y, goal_z</code> changes value.</li>
        <li>Programmatically label these segments for analysis (e.g., <em>Hover 1</em>, <em>+X Step</em>, <em>Path Leg 1</em>, etc.).</li>
    </ul>
    <h3>C) Metric Computation</h3>
    <p>For each relevant segment, compute the following metrics:</p>
    <ul>
        <li><strong>RMS Tracking Error (m):</strong> The root-mean-square of the error signals (e.g., <code>e_x(t) = x(t) - goal_x(t)</code>). Report per-axis RMS error and a combined <strong>RMS XY Error</strong> using <code>sqrt(e_x&sup2; + e_y&sup2;)</code>.</li>
        <li><strong>Step Response Metrics (for &plusmn;X/&plusmn;Y step segments):</strong>
            <ul>
                <li><strong>Overshoot (m):</strong> The maximum error in the direction of the step after crossing the goal for the first time.</li>
                <li><strong>Settling Time (s):</strong> The time it takes for the drone to enter and remain within a &plusmn;0.05&nbsp;m band of the final goal position.</li>
            </ul>
        </li>
        <li><strong>Path Following Error (m):</strong> The mean absolute deviation from the straight-line path during path-following segments.</li>
        <li><strong>Effort Proxy (deg):</strong> The standard deviation of the <code>roll</code> or <code>pitch</code> signal during a maneuver. A higher value suggests more aggressive control effort. State which angle you used.</li>
    </ul>
    <h3>D) Baseline Comparison</h3>
    <p>The core of this lab is comparing your controller to the baseline.</p>
    <ol>
        <li>Load the baseline CSV and read its PID values directly from the appropriate columns.</li>
        <li>Compute the exact same set of metrics (RMS Error, Overshoot, etc.) for the baseline data over the same flight segments.</li>
        <li>In your metrics table, calculate the absolute difference (<code>&Delta; = Yours &minus; Baseline</code>) and the percent difference (<code>%&Delta; = 100 &times; &Delta; / Baseline</code>).</li>
        <li>Remember that for error-based metrics (like RMS error or overshoot), a <strong>negative &Delta;</strong> indicates an improvement over the baseline.</li>
    </ol>
    <h3>E) Tuning Recommendation</h3>
    <p>Based on your quantitative results, propose <strong>one specific change</strong> to a single PID parameter on one axis. Your justification must be tied directly to your data.</p>
    <p><strong>Example:</strong> <em>&ldquo;Decrease the Kp gain on the X-axis. My controller had a 25% larger overshoot (0.15m vs 0.12m) than the baseline during the +X step, and this change should reduce that overshoot while likely maintaining an acceptable settling time.&rdquo;</em></p>
</section>

</div>
