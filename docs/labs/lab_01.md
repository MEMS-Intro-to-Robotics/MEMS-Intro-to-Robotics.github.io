---
title: "Lab 01: VM and Git Setup"
---

# Lab 01: VM and Git Setup

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#objectives">Learning Objectives</a></li>
        <li><a href="#prelab">Pre-Lab &mdash; Do Before Lab</a></li>
        <li><a href="#procedure">Lab Procedure</a>
            <ol>
                <li><a href="#part1">Part 1 &mdash; Connect to Your VM and Verify Tools</a></li>
                <li><a href="#part2">Part 2 &mdash; Git and GitHub Setup</a></li>
                <li><a href="#part3">Part 3 &mdash; Docker-based ROS 2 Environment</a></li>
                <li><a href="#part4">Part 4 &mdash; Command Line Practice</a></li>
                <li><a href="#part5">Part 5 &mdash; Git Synchronization and Recovery</a></li>
            </ol>
        </li>
        <li><a href="#analysis">Analysis and Discussion</a></li>
        <li><a href="#troubleshooting">Troubleshooting</a></li>
        <li><a href="#references">References</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>In this lab, you will reserve your virtual machine (VM), configure the course development environment, and use the Linux command line. You will also practice the pull&ndash;commit&ndash;push cycle and recover when your local repository and GitHub do not match.</p>
    <h3>1.2 Background</h3>
    <p>The course VM and Docker image provide a common Ubuntu and ROS 2 environment. Git tracks another set of states: the files and commits on your VM can differ from those on GitHub. In this lab, you will create remote-ahead and diverged repositories, inspect each state, and recover without discarding either version of the work.</p>
    <h4>How the Tools Fit Together</h4>
    <ul>
        <li><strong>Linux (Ubuntu):</strong> The course VM runs Ubuntu, a supported platform for ROS 2 Jazzy.</li>
        <li><strong>Git:</strong> Git is the version control system we use to track code, collaborate, and submit work.</li>
        <li><strong>Docker:</strong> Docker runs applications in isolated environments called containers. The course image contains ROS 2 and its dependencies.</li>
        <li><strong>ROS 2 (Robot Operating System):</strong> ROS is the framework we use for robot software. It provides tools, libraries, and conventions for connecting sensors, planners, controllers, and user code.</li>
    </ul>
    <h3>1.3 Equipment and Software</h3>
    <ul>
        <li><strong>Hardware:</strong> A personal computer capable of running the FastX client and connecting to the course VM.</li>
        <li><strong>Software (on the VM):</strong> Course VM image (Ubuntu), VS Code, Docker (installed via provided script), Git (SSH configured), ROS 2 Jazzy (inside the course Docker image).</li>
    </ul>
    <h3>1.4 Where You Type Commands</h3>
    <p>This lab uses three different command lines. Every code block in this manual is labeled with the one it belongs to. Check the label before you type, and use the prompt to confirm where you are.</p>
    <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 1em;">
        <caption style="margin-bottom: 0.5em;">Command-line locations used in this manual</caption>
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ccc; padding: 8px;">Label</th>
                <th style="border: 1px solid #ccc; padding: 8px;">Where it runs</th>
                <th style="border: 1px solid #ccc; padding: 8px;">How to open it</th>
                <th style="border: 1px solid #ccc; padding: 8px;">Prompt looks like</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;"><strong>Laptop Terminal</strong></td>
                <td style="border: 1px solid #ccc; padding: 8px;">Your own computer</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Windows: open <strong>PowerShell</strong> from the Start menu. macOS: open <strong>Terminal</strong> from Applications &rarr; Utilities.</td>
                <td style="border: 1px solid #ccc; padding: 8px;"><code>PS C:\Users\you&gt;</code> or <code>you@your-mac ~ %</code></td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;"><strong>Host VM Terminal</strong></td>
                <td style="border: 1px solid #ccc; padding: 8px;">Your Duke course VM</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Run <code>ssh netid@vcm-xxxxx.vm.duke.edu</code> from a Laptop Terminal, or open a terminal in the XFCE desktop you reach through FastX.</td>
                <td style="border: 1px solid #ccc; padding: 8px;"><code>netid@vcm-xxxxx:~$</code></td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;"><strong>Container Terminal</strong></td>
                <td style="border: 1px solid #ccc; padding: 8px;">Inside the Docker container running on the VM</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Opens for you when you run the <code>docker run</code> command in Part 3 from a Host VM Terminal.</td>
                <td style="border: 1px solid #ccc; padding: 8px;"><code>root@vcm-xxxxx:/#</code></td>
            </tr>
        </tbody>
    </table>
    <p>The container shares the VM&rsquo;s network, so the machine name in the prompt is the same in the last two rows. What changes is the user and the last character: inside the container you are <code>root</code> and the prompt ends in <code>#</code>, while on the VM you are your NetID and the prompt ends in <code>$</code>. If you are unsure, run <code>whoami</code>. It prints <code>root</code> inside the container and your NetID on the VM.</p>
    <!-- TODO(instructor): confirm the container prompt string and whoami output against the course image. -->
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="objectives">
    <h2>2. Learning Objectives</h2>
    <p>After completing this lab, you should be able to:</p>
    <ul>
        <li><strong>Set up</strong> a complete robotics development environment, starting with a Virtual Machine running Ubuntu, and including VS Code, Docker, and a ROS 2 workspace.</li>
        <li><strong>Operate and verify</strong> a Linux shell, SSH connection, and containerized development environment.</li>
        <li><strong>Use</strong> Git and GitHub to clone, fetch, pull, commit, and push course work.</li>
        <li><strong>Diagnose and recover</strong> when a remote repository is ahead, a push is rejected, or two commits conflict.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>4. Pre-Lab &mdash; Do Before Lab</h2>
    <h3>4.1 Readings</h3>
    <ul>
        <li><a href="https://git-scm.com/book/en/v2" target="_blank" rel="noopener"><strong><em>Pro Git</em></strong> by Scott Chacon and Ben Straub</a> &mdash; Chapters 1 and 2<br /><em>Focus on repositories, commits, and branches &mdash; no need to memorize every command.</em></li>
        <li><a href="http://linuxcommand.org/lc3_learning_the_shell.php" target="_blank" rel="noopener"><em>Learning the Shell</em></a> &mdash; Sections 1&ndash;10</li>
    </ul>
    <h3>4.2 Reserve Your Course VM</h3>
    <p>You will use a <strong>virtual machine (VM)</strong> throughout the course. The VM runs Ubuntu remotely and is accessible from a Windows or macOS laptop.</p>
    <ol>
        <li>Go to the <a href="https://vcm.duke.edu" target="_blank" rel="noopener">VCM Portal</a> and sign in with your Duke NetID.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/01-vcm-portal-sign.png" alt="VCM Portal sign in" width="446" height="101" /></li>
        <li>Select <strong>Reserve a VM</strong> and choose the <strong>ROS VM</strong> for this course.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/02-reserve-vm-option.png" alt="Reserve a VM option" width="350" height="100" /></li>
        <li>Note your VM&rsquo;s hostname (e.g., <code>vcm-xxxxx.vm.duke.edu</code>).</li>
        <li>To start your VM, click <em>Book now</em>.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/03-book-now-button.png" alt="Book now button" width="364" height="117" /></li>
        <li>VMs run for up to <strong>4 hours per reservation</strong> and then power off automatically. You can renew or reserve a new session if needed.</li>
    </ol>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Important:</strong> VMs power off automatically 4 hours after the reservation starts. Commit and push your work before the session ends.</div>
    <p>If you need to power down (not delete) your VM, click the red trash can.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/04-power-down-vm.png" alt="Power down VM" /></p>
    <h3>4.3 Add Your SSH Key to the Duke Directory</h3>
    <p>An SSH key pair authenticates your computer without sending a password during each login. Keep the private key on your computer and add the public key to the Duke Directory.</p>
    <p>This key identifies your laptop to Duke&rsquo;s VM system. Generate it once in a <strong>Laptop Terminal</strong> (Section 1.4 shows how to open one) and paste the public half into the Duke Directory. In Part 2 you will generate a second key on the VM itself for GitHub. The two are separate because a key lives on one machine, and the VM cannot use the key stored on your laptop.</p>
    <ol>
        <li><strong>Generate a new SSH key</strong> (replace with your Duke email):
            <p><strong>Location:</strong> Laptop Terminal</p>
            <pre><code class="language-bash">ssh-keygen -t ed25519 -C "netid@duke.edu"</code></pre>
            Accept the default location when prompted. You&rsquo;ll get two files: <code>id_ed25519</code> (private key) and <code>id_ed25519.pub</code> (public key).
        </li>
        <li><strong>Copy the public key to your clipboard:</strong>
            <ul>
                <li><strong>Linux:</strong>
                    <pre><code class="language-bash">xclip -sel clip &lt; ~/.ssh/id_ed25519.pub</code></pre>
                </li>
                <li><strong>macOS:</strong>
                    <pre><code class="language-bash">pbcopy &lt; ~/.ssh/id_ed25519.pub</code></pre>
                </li>
                <li><strong>Windows (PowerShell):</strong>
                    <pre><code class="language-bash">type $env:USERPROFILE\.ssh\id_ed25519.pub | clip</code></pre>
                </li>
                <li><strong>Windows (Git Bash):</strong>
                    <pre><code class="language-bash">cat ~/.ssh/id_ed25519.pub | clip</code></pre>
                </li>
                <li>If none of the above work, display and copy manually:
                    <pre><code class="language-bash">cat ~/.ssh/id_ed25519.pub</code></pre>
                </li>
            </ul>
        </li>
        <li><strong>Paste your public key into the Duke Directory:</strong> <a href="https://idms-web-selfservice.oit.duke.edu/advanced" target="_blank" rel="noopener">Advanced User Options &rarr; SSH Public Keys</a></li>
    </ol>
    <blockquote style="border-left: 4px solid #d9534f; padding-left: 1em; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Warning:</strong> Do not add your private key. Only add the <code>.pub</code> file contents.</blockquote>
    <p>Click on "+ See More about SSH keys" button to show the box to enter your SSH key.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/05-ssh-key-entry.png" alt="SSH key entry" width="475" height="90" /></p>
    <p><em>Additional resources: <a href="https://vcm.duke.edu/help/23" target="_blank" rel="noopener">VCM SSH Key Guide</a></em></p>
    <h3>4.4 Configure Your VM Environment</h3>
    <ol>
        <li>SSH into your VM from your laptop:
            <p><strong>Location:</strong> Laptop Terminal</p>
            <pre><code class="language-bash">ssh yourNetID@vcm-xxxxx.vm.duke.edu</code></pre>
        </li>
        <li>Download the setup script:
            <p><strong>Location:</strong> Host VM Terminal (the SSH session you just opened)</p>
            <pre><code class="language-bash">cd ~
curl -L "https://raw.githubusercontent.com/MEMS-Intro-to-Robotics/mems-robotics-toolkit/main/vm_setup.sh" -o vm_setup.sh
chmod +x vm_setup.sh</code></pre>
        </li>
        <li>Run the setup script with the provided license key:
            <pre><code class="language-bash">FASTX_ACTIVATION_KEY="&lt;key-from-course-staff&gt;" ./vm_setup.sh</code></pre>
        </li>
    </ol>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Notes on Using the Terminal</strong><br />
        <ul>
            <li>The setup script uses <code>sudo</code>, which runs a command with administrator privileges and asks for your NetID password first. When you type that password nothing appears on screen, not even dots or asterisks. This is normal; type it and press <strong>Enter</strong>.</li>
            <li>You may see messages like <code>SyntaxWarning: invalid escape sequence</code> when Terminator installs. These warnings are harmless and can be ignored.</li>
        </ul>
    </blockquote>
    <ol start="4">
        <li>If the setup script does not fully activate FastX, run the following command manually:
            <pre><code class="language-bash">sudo -u fastx /usr/lib/fastx/4/install/activate</code></pre>
            <p>Enter the license key provided by course staff when prompted.</p>
            <p>Enter 1 for number of seats to activate. When activation succeeds, you should see confirmation messages about the license being applied.</p>
        </li>
        <li>Confirm the script installed the core tools before you log out:
            <p><strong>Location:</strong> Host VM Terminal</p>
            <pre><code class="language-bash">docker --version
git --version
gh --version
pytest --version</code></pre>
            <p>All four should print a version number. The script itself finishes by printing <code>===== Setup complete! =====</code> followed by a note about the <code>docker</code> group; if you did not see that line, it stopped early. If <code>docker</code> reports a permissions error, reboot with <code>sudo reboot</code>, wait about a minute, reconnect over SSH, and check again. If any command reports <code>command not found</code>, re-run the script and keep the last 20 lines of output to show a TA.</p>
        </li>
        <li>Log out of the SSH session by typing <code>exit</code> in the terminal.</li>
    </ol>
    <h3>4.5 Install &amp; Configure FastX Desktop Client</h3>
    <p><strong>FastX</strong> provides the graphical desktop used to run applications on the course VM.</p>
    <ol>
        <li>Download and install the <a href="https://www.starnet.com/download-fastx-client/" target="_blank" rel="noopener"><strong>FastX 4 Desktop Client</strong></a> (not the Server).</li>
        <li>Add a new <strong>SSH Connection</strong>:<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/06-add-ssh-connection.png" alt="Add SSH connection" width="166" height="98" />
            <ul>
                <li><strong>Host:</strong> <code>vcm-xxxxx.vm.duke.edu</code></li>
                <li><strong>User:</strong> your NetID</li>
                <li><strong>Port:</strong> <code>22</code> (default, don&rsquo;t change)</li>
            </ul>
            <img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/07-ssh-connection-settings.png" alt="SSH connection settings" width="268" height="326" />
        </li>
        <li>Create a new session:<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/08-create-new-session.png" alt="Create new session" width="363" height="129" />
            <ul>
                <li><strong>Command:</strong> <code>startxfce4</code></li>
                <li><strong>Window Mode:</strong> <strong>Single</strong> (not Multiple)</li>
            </ul>
            <img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/09-session-settings.png" alt="Session settings" width="457" height="96" />
        </li>
        <li>Launch the session. On first run, if prompted, choose the <strong>default XFCE panel layout</strong>.<br /><img src="https://mems-intro-to-robotics.github.io/assets/labs/lab01/10-xfce-panel-layout.png" alt="XFCE panel layout" width="277" height="262" /></li>
    </ol>
    <p>📸 <strong>Screenshot Requirement:</strong> Take a screenshot showing your VM desktop running through FastX. <strong>Save it as <code>vm_desktop.png</code></strong>. You will create your Lab 1 repository and its <code>docs/</code> folder in Part 2, and move this file into <code>docs/</code> then.</p>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>How to take screenshots (this applies to every 📸 in this lab):</strong> use one of the following methods. The steps for moving the file depend on whether you save it on the VM or your laptop.
        <ul>
            <li><strong>On the VM (recommended):</strong> inside the FastX desktop, use Applications &rarr; Accessories &rarr; Screenshot and save to the <code>Pictures</code> folder. The file is then on the VM, where the <code>cp ~/Pictures/...</code> commands in Part 2 expect it.</li>
            <li><strong>On your laptop:</strong> your laptop&rsquo;s screenshot tool also works, but the file is saved on your laptop, so the VM&rsquo;s <code>cp</code> commands cannot access it. Once your repository exists (Step 2.3), upload it through the GitHub website: open your repository, open the <code>docs/</code> folder, and use Add file &rarr; Upload files. This creates a commit on GitHub that is not yet on the VM. Run <code>git pull</code> on the VM before your next commit.</li>
        </ul>
    </blockquote>
    <h3>4.6 Pre-Lab Checklist</h3>
    <div class="alert alert-info" style="background-color: #d9edf7; border-color: #bce8f1; color: #31708f; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>Complete Before Lab</strong>
        <p>Verify each item before arriving at lab.</p>
    </div>
    <ul>
        <li>[ ] Readings skimmed (<em>Pro Git</em> Ch. 1&ndash;2, <em>Learning the Shell</em> Sec. 1&ndash;10).</li>
        <li>[ ] Course VM reserved on the VCM portal; hostname noted.</li>
        <li>[ ] Laptop SSH key added to the Duke Directory.</li>
        <li>[ ] VM setup script run successfully; FastX activated.</li>
        <li>[ ] FastX Desktop Client installed and a session launched.</li>
        <li>[ ] <code>vm_desktop.png</code> screenshot captured.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>5. Lab Procedure</h2>
    <section id="part1">
        <h3>Part 1 &mdash; Connect to Your VM and Verify Tools</h3>
        <p><strong>Goal:</strong> Open a desktop session on your VM and confirm the core tools are installed.</p>
        <h4>Step 1.1: Connect to Your VM</h4>
        <ol>
            <li><strong>Open the FastX Desktop Client</strong> on your laptop.</li>
            <li><strong>Connect to your VM</strong> using the SSH connection you created in the pre-lab:
                <ul>
                    <li><strong>Host:</strong> <code>vcm-xxxxx.vm.duke.edu</code></li>
                    <li><strong>User:</strong> your Duke NetID</li>
                    <li><strong>Port:</strong> <code>22</code></li>
                </ul>
            </li>
            <li><strong>Start a desktop session</strong> with:
                <ul>
                    <li><strong>Command:</strong> <code>startxfce4</code></li>
                    <li><strong>Window Mode:</strong> <strong>Single</strong></li>
                </ul>
            </li>
            <li>If prompted, choose the <strong>default XFCE panel layout</strong>.</li>
        </ol>
        <h4>Step 1.2: Verify Access</h4>
        <ol>
            <li>Open a terminal inside your XFCE desktop (from the <strong>Applications</strong> menu or by right-clicking the desktop &rarr; <strong>Open Terminal</strong>).</li>
            <li>Run the following commands to confirm key tools are installed:
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">docker --version
git --version
code --version</code></pre>
                <p><code>code</code> is the command that launches VS Code.</p>
            </li>
        </ol>
        <p><strong>Checkpoint:</strong> You should see output similar to the following (exact numbers may differ):</p>
        <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
            <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>Docker version XX.X.X, build XXXXXXX
git version X.XX.X
1.10X.X
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
x64</code></pre>
        </div>
        <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Stop:</strong> If <code>docker</code> commands fail with a permissions error, you likely need to <strong>reboot your VM once</strong> after running the setup script. Run <code>sudo reboot</code> in your VM&rsquo;s terminal to restart.</blockquote>
        <p>📸 <strong>Screenshot Requirement:</strong> Capture your VM desktop with the terminal open, showing the version checks above. <strong>Save it as <code>version_check.png</code></strong>. You will move it into your repo&rsquo;s <code>docs/</code> folder in Part 2.</p>
    </section>
    <section id="part2">
        <h3>Part 2 &mdash; Git and GitHub Setup</h3>
        <p><strong>Goal:</strong> Authenticate your VM with GitHub, create your Lab 1 repository through Classroom 50, and make your first commit and push.</p>
        <h4>Step 2.1: Create or Access Your GitHub Account</h4>
        <p>We use <strong>Classroom 50</strong> for assignment submissions. Each lab has its own <strong>assignment slug</strong>, a short identifier such as <code>lab-01</code> that names the assignment and becomes part of your repository name. Accepting an assignment creates a private repository for you. Your repositories are only visible to you and the teaching staff.</p>
        <ol>
            <li>If you don&rsquo;t already have a GitHub account, create one at <a href="https://github.com/signup" target="_blank" rel="noopener">https://github.com/signup</a>.</li>
            <li>If you already have a GitHub account, you can use your existing account.</li>
        </ol>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> Course materials (the robotics toolkit scripts and reference code) are hosted on <strong>GitHub</strong> under the <strong>MEMS-Intro-to-Robotics</strong> organization. The course <strong>Docker images</strong> come from the same organization&rsquo;s public GitHub Container Registry (<code>ghcr.io</code>), with no login needed. Your <em>submissions</em> go to Classroom 50. You do not need any account besides GitHub.</blockquote>
        <h4>Step 2.2: Generate an SSH Key on Your VM and Add it to GitHub</h4>
        <p>Generate a new SSH key <strong>inside your VM</strong> so the VM can authenticate with GitHub. Course ROS 2 development takes place in the VM environment.</p>
        <ol>
            <li>In your VM terminal, generate a key pair (use your email):
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">ssh-keygen -t ed25519 -C "your_email@example.com"</code></pre>
                Press <kbd>Enter</kbd> to accept the default location (<code>~/.ssh/id_ed25519</code>), then press <kbd>Enter</kbd> twice more at the passphrase prompts to leave the passphrase empty. This creates two files:
                <ul>
                    <li><code>id_ed25519</code> &rarr; your <strong>private key</strong> (never share this).</li>
                    <li><code>id_ed25519.pub</code> &rarr; your <strong>public key</strong> (safe to share with GitHub).</li>
                </ul>
            </li>
            <li>Start the SSH agent and add your key:
                <pre><code class="language-bash">eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519</code></pre>
            </li>
            <li>Display your public key:
                <pre><code class="language-bash">cat ~/.ssh/id_ed25519.pub</code></pre>
                Copy the full output (it should begin with <code>ssh-ed25519</code>).
            </li>
            <li>In GitHub, go to <strong>Settings &rarr; SSH and GPG keys &rarr; New SSH key</strong>. Paste your public key and give it a title like <em>&ldquo;Duke VM&rdquo;</em>.</li>
            <li>Test the connection from your VM:
                <pre><code class="language-bash">ssh -T git@github.com</code></pre>
                The first time you connect, SSH asks <em>&ldquo;Are you sure you want to continue connecting (yes/no/[fingerprint])?&rdquo;</em> because it has never seen GitHub&rsquo;s server before. Type <code>yes</code> and press <kbd>Enter</kbd>. You should then see a message like <em>&ldquo;Hi username! You&rsquo;ve successfully authenticated...&rdquo;</em>
            </li>
        </ol>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> You may also add your <strong>laptop&rsquo;s</strong> SSH key to GitHub if you want to work directly from your laptop. The VM key is still required for course ROS 2 development.</blockquote>
        <p>📸 <strong>Screenshot Requirement:</strong> Capture the terminal output confirming that you can connect to GitHub (the <code>ssh -T git@github.com</code> success message; do not include your key contents). <strong>Save it as <code>ssh_github_test.png</code></strong>; you will move it into <code>docs/</code> in the next step.</p>
        <h4>Step 2.3: Accept the Lab 1 Assignment with Classroom 50 and Clone Your Repository</h4>
        <ol>
            <li><strong>Install or verify the Classroom 50 student command:</strong>
                <p><code>gh</code> is GitHub&rsquo;s command-line tool, installed on your VM by the setup script in section 4.4. The first command below adds the Classroom 50 student extension to it, which is what provides <code>gh student</code>.</p>
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">gh extension install foundation50/gh-student
gh student --help</code></pre>
                <p>If the extension is already installed, the first command may report that it exists. Continue when the help text is available.</p>
            </li>
            <li><strong>Sign in to GitHub from the command line:</strong>
                <p>The SSH key you added in Step 2.2 lets <code>git</code> push and pull. It does not sign in the <code>gh</code> command itself, which keeps its own GitHub login. Do this step before you accept the assignment, or the next command cannot look you up on the roster.</p>
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">gh student login</code></pre>
                <p>The command prints a one-time code, then waits for you to press Enter before opening <code>https://github.com/login/device</code>. If no browser opens on the VM, open that address on your laptop instead and type the code there. Approve the permissions it requests; <code>gh student</code> needs them to read the class roster and create your repository.</p>
                <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> After you approve in the browser, the terminal can sit with a spinning cursor for several minutes before it finishes. This is normal. Do not press <code>Ctrl+C</code>. Cancelling leaves you signed out and uses up the one-time code, so you would have to start the step over.</blockquote>
                <p><strong>Checkpoint:</strong> <code>gh student whoami</code> prints your GitHub username.</p>
            </li>
            <li><strong>Accept the assignment:</strong>
                <p><strong>Location:</strong> Host VM Terminal</p>
                <pre><code class="language-bash">gh student accept MEMS-Intro-to-Robotics intro-to-robotics-fall-2026 lab-01</code></pre>
                <p>The three arguments are the GitHub organization (<code>MEMS-Intro-to-Robotics</code>), the classroom short name (<code>intro-to-robotics-fall-2026</code>), and the assignment slug (<code>lab-01</code>). Only the slug changes from lab to lab.</p>
                <p>Course staff add your GitHub username to the class roster, which sends your account an invitation to the <code>MEMS-Intro-to-Robotics</code> organization. This command accepts that pending invitation, creates your private repository, and prints the exact <code>git clone</code> command. If you already accepted the assignment, it leaves your repository unchanged.</p>
                <p>If the command reports that you are not on the roster, your GitHub username has not been registered for the course. Contact the teaching staff before continuing.</p>
                <!-- TODO(instructor): state here how students submit their GitHub username for the roster import. -->
            </li>
            <li><strong>Note your repository URL:</strong> After accepting, you&rsquo;ll see a URL like:
                <pre><code>https://github.com/MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-01-YOUR_GITHUB_USERNAME</code></pre>
            </li>
            <li><strong>Clone the repository into your workspace:</strong>
                <p><strong>Location:</strong> Host VM Terminal. Always clone and push on the VM, never inside the container.</p>
                <pre><code class="language-bash">mkdir -p ~/workspaces
cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/intro-to-robotics-fall-2026-lab-01-YOUR_GITHUB_USERNAME.git
cd intro-to-robotics-fall-2026-lab-01-YOUR_GITHUB_USERNAME</code></pre>
                <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your actual GitHub username. Use the URL printed by Classroom 50 if it differs from the example.</p>
                <p><strong>Checkpoint:</strong> <code>ls -la</code> (a long listing that includes hidden files, the ones whose names begin with a dot) should show the starter files, including <code>.github/</code>, <code>.gitignore</code>, <code>README.md</code>, <code>docs/</code>, and <code>test_lab_1.py</code>. Do not delete the grading files.</p>
            </li>
            <li><strong>Configure Git identity:</strong>
                <pre><code class="language-bash">git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"</code></pre>
            </li>
            <li><strong>Copy your screenshots into <code>docs/</code>:</strong>
                <pre><code class="language-bash">mkdir -p docs
cp ~/Pictures/vm_desktop.png docs/vm_desktop.png
cp ~/Pictures/version_check.png docs/version_check.png
cp ~/Pictures/ssh_github_test.png docs/ssh_github_test.png</code></pre>
                <p>Run <code>ls ~/Pictures</code> first to confirm the screenshots are there, and adjust each source path if your screenshot tool saved them somewhere else. If a source file is missing, correct its path. If you uploaded a screenshot through the GitHub website instead, run <code>git pull</code> to bring it down and skip the <code>cp</code> for that file. Confirm the result with <code>ls -l docs/</code>.</p>
            </li>
            <li><strong>Update the README and push:</strong>
                <ol>
                    <li>Open the README in nano:
                        <pre><code class="language-bash">nano README.md</code></pre>
                    </li>
                    <li>Update it with your information. A suggested format:
                        <p><strong>Location:</strong> File Editor</p>
                        <pre><code># Lab 01: VM and Git Setup &mdash; [Your Name]
ECE 383 / ME 555: Introduction to Robotics and Automation (Fall 2026)
## Contents
- `docs/` &mdash; Screenshots and documentation
- `git_recovery.md` &mdash; Git synchronization and recovery record
- `sync_conflict.txt` &mdash; Resolved Git conflict exercise</code></pre>
                    </li>
                    <li>Save and exit nano:
                        <ul>
                            <li>Press <strong>Ctrl+O</strong> (write out), hit <strong>Enter</strong> to confirm.</li>
                            <li>Press <strong>Ctrl+X</strong> to exit.</li>
                        </ul>
                    </li>
                    <li>Stage, commit, and push your changes:
                        <p><strong>Location:</strong> Host VM Terminal</p>
                        <pre><code class="language-bash">git add README.md docs/
git commit -m "Update README and add setup screenshots"
git push origin main</code></pre>
                    </li>
                </ol>
            </li>
        </ol>
        <p><strong>Checkpoint:</strong> Visit your repository on GitHub in a browser. You should see your updated <code>README.md</code> and a <code>docs/</code> folder containing three screenshots.</p>
    </section>
    <section id="part3">
        <h3>Part 3 &mdash; Docker-based ROS 2 Environment</h3>
        <p><strong>Goal:</strong> Pull the course Docker image, start a container with your workspace mounted, and verify ROS 2 runs (Python and C++).</p>
        <p>You will do all your ROS 2 development <strong>inside the course Docker container</strong>.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Image vs. Container</strong><br />
            <ul>
                <li>A <strong>Docker image</strong> is a blueprint: a read-only package that includes the operating system, software, and configurations needed for a project.</li>
                <li>A <strong>Docker container</strong> is a running instance of that image. You can think of it as &ldquo;launching&rdquo; the image so you can interact with it, make changes, and run programs inside it.</li>
                <li>Multiple containers can be created from the same image, and each container is isolated from your host system.</li>
            </ul>
        </blockquote>
        <h4>Step 3.1: Prepare</h4>
        <ol>
            <li>Open a terminal on your VM.</li>
            <li>If you haven&rsquo;t already, ensure the VM setup script from section 4.4 has been run.</li>
            <li>You should already have a <code>~/workspaces</code> directory from cloning your Lab 1 repo. We&rsquo;ll use that same folder for all ROS 2 development.</li>
        </ol>
        <h4>Step 3.2: Pull the Course Image</h4>
        <p>Pull the prebuilt course image from the course GitHub Container Registry:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">docker pull ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        <h4>Step 3.3: Allow GUI Connections</h4>
        <p>On your VM, before starting the container, run the following command. This grants Docker permission to draw graphical windows (like the turtle simulator) on your VM&rsquo;s desktop:</p>
        <p><strong>Location:</strong> Host VM Terminal, specifically a terminal <em>inside the FastX desktop</em>. In a plain SSH session this command reports <code>unable to open display</code>, because there is no desktop for it to talk to.</p>
        <pre><code class="language-bash">xhost +local:docker</code></pre>
        <h4>Step 3.4: Run the Container (mount your workspace)</h4>
        <p>Start an interactive container with your <code>~/workspaces</code> folder mounted and X11 passthrough so graphical applications can launch. This is the <strong>standard course <code>docker run</code> command</strong>. You will use this same shape in every lab, changing only the <code>--name</code> and the image tag:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">docker run --rm -it \
  --name lab01 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong><code>docker run</code> options:</strong>
            <ul>
                <li><code>--rm</code>: Automatically removes the container when you exit.</li>
                <li><code>-it</code>: Runs the container in interactive mode and gives you a terminal.</li>
                <li><code>--name lab01</code>: Gives the container a memorable name so you can open extra terminals into it later with <code>docker exec -it lab01 bash</code>.</li>
                <li><code>--net=host</code>: Shares the VM&rsquo;s network with the container, so ROS 2 nodes inside and outside the container can find each other.</li>
                <li><code>-e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST</code>: Restricts ROS 2 discovery to your VM and prevents discovery of other students&rsquo; nodes on the shared network.</li>
                <li><code>-e DISPLAY=$DISPLAY</code> and <code>-v /tmp/.X11-unix:/tmp/.X11-unix:ro</code>: These allow graphical applications to run from inside the container.</li>
                <li><code>-v ~/workspaces:/root/workspaces</code>: Mounts your VM&rsquo;s <code>~/workspaces</code> directory into the container. The container runs as the <code>root</code> user, so inside the container <code>~/workspaces</code> is the <em>same folder</em>, and your files appear in both places.</li>
            </ul>
        </blockquote>
        <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Warning:</strong> Because of <code>--rm</code>, the container is <strong>destroyed</strong> the moment you exit the original shell, along with any terminals attached to it via <code>docker exec</code>. Anything saved <em>outside</em> the mounted <code>~/workspaces</code> folder is lost. Keep your work in <code>~/workspaces</code>.</blockquote>
        <p>Once inside the container, confirm that ROS 2 Jazzy is available:</p>
        <p><strong>Location:</strong> Container Terminal</p>
        <pre><code class="language-bash">echo $ROS_DISTRO</code></pre>
        <p>This should return <code>jazzy</code>.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Sourcing note:</strong> The course image&rsquo;s <code>~/.bashrc</code> already sources ROS 2 Jazzy, so <code>ros2</code> commands work in every container shell without any extra setup. No workspace sourcing is needed in this lab.</blockquote>
        <p>Next, check that ROS 2 commands work properly by listing nodes:</p>
        <pre><code class="language-bash">ros2 node list</code></pre>
        <p>If no nodes are running yet, the command returns an empty list, which is expected.</p>
        <p>📸 <strong>Screenshot Requirement:</strong> Capture the output of both commands (<code>echo $ROS_DISTRO</code> and <code>ros2 node list</code>) in your terminal. <strong>Save it as <code>docs/ros2_check.png</code></strong> in your Lab 1 repository.</p>
        <h4>Step 3.5: Run a Talker/Listener Demo (test Python and C++)</h4>
        <ol>
            <li>Inside the container, launch a multi-pane terminal:
                <p><strong>Location:</strong> Container Terminal</p>
                <pre><code class="language-bash">terminator</code></pre>
                <p>To create multiple panes, right-click inside the Terminator window and select <strong>Split Horizontally</strong> or <strong>Split Vertically</strong>.</p>
            </li>
            <li>In <strong>pane A</strong>, run a C++ talker node:
                <pre><code class="language-bash">ros2 run demo_nodes_cpp talker</code></pre>
            </li>
            <li>In <strong>pane B</strong>, run a Python listener node:
                <pre><code class="language-bash">ros2 run demo_nodes_py listener</code></pre>
            </li>
        </ol>
        <p><strong>Checkpoint:</strong> The listener should print the string messages published by the talker. This confirms that both C++ and Python ROS 2 nodes work correctly.</p>
        <p>📸 <strong>Screenshot Requirement:</strong> Capture both panes in the same window, with the listener actively printing messages. <strong>Save it as <code>docs/talker_listener.png</code></strong> in your Lab 1 repository.</p>
        <h4>Step 3.6: Exit the Docker Container</h4>
        <p>Once you have verified the demo, close the <code>terminator</code> window, then type <code>exit</code> in the terminal where you ran <code>docker run</code>. Because of <code>--rm</code>, this destroys the container. Your screenshots are in the mounted <code>~/workspaces</code> folder and stay on the VM.</p>
    </section>
    <section id="part4">
        <h3>Part 4 &mdash; Command Line Practice</h3>
        <p><strong>Goal:</strong> Use core Linux commands to navigate directories and manage files.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Terminal Tip: Tab Auto-Completion</strong><br />Start typing a command, file, or directory name and press Tab, and the terminal completes it. If more than one name matches, press Tab twice to list the possibilities. Using Tab routinely avoids most path and filename typos.</blockquote>
        <h4>Step 4.1: Work Through Examples</h4>
        <p>Run the examples in <em>Learning the Shell</em> (sections 1&ndash;10) in a terminal.</p>
        <h4>Step 4.2: Set Up the Practice Folder</h4>
        <p>Create a practice directory with the files used in the exercises below:</p>
        <p><strong>Location:</strong> Host VM Terminal</p>
        <pre><code class="language-bash">mkdir -p ~/cli_practice
cd ~/cli_practice
echo "Hello from the command line." &gt; file.txt
printf '#!/usr/bin/env bash\necho "myprog ran successfully"\n' &gt; myprog
chmod +x myprog</code></pre>
        <p><strong>Checkpoint:</strong> <code>ls</code> in <code>~/cli_practice</code> should show <code>file.txt</code> and <code>myprog</code>.</p>
        <h4>Step 4.3: Directory and File Practice</h4>
        <p>Try the following exercises in your VM terminal:</p>
        <ol>
            <li>Change into the directory called <code>cli_practice</code>:
                <pre><code class="language-bash">cd ~/cli_practice</code></pre>
            </li>
            <li>Make a copy of <code>file.txt</code> named <code>newfile.txt</code>:
                <pre><code class="language-bash">cp file.txt newfile.txt</code></pre>
            </li>
            <li>Rename the original <code>file.txt</code> to <code>oldfile.txt</code>:
                <pre><code class="language-bash">mv file.txt oldfile.txt</code></pre>
            </li>
            <li>Run the executable <code>myprog</code> and redirect its output to <code>output.txt</code>:
                <pre><code class="language-bash">./myprog &gt; output.txt</code></pre>
            </li>
            <li>List every file with a <code>.txt</code> extension in the current directory:
                <pre><code class="language-bash">ls *.txt</code></pre>
            </li>
        </ol>
        <p><strong>Checkpoint:</strong> The final <code>ls *.txt</code> should list <code>newfile.txt</code>, <code>oldfile.txt</code>, and <code>output.txt</code>, and <code>cat output.txt</code> should print <code>myprog ran successfully</code>.</p>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; margin-top: 1em;">
            <caption style="margin-bottom: 0.5em;">Common Command-Line Commands</caption>
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ccc; padding: 8px;">Command</th>
                    <th style="border: 1px solid #ccc; padding: 8px;">Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>pwd</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Print Working Directory (shows your current location)</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>cd &lt;directory&gt;</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Change to specified directory</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>ls</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">List directory contents</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>ls -a</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">List all contents, including hidden files</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>ls -l</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">List one file per line with size, owner, and permissions (combine as <code>ls -la</code>)</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>cp &lt;source&gt; &lt;destination&gt;</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Copy files or directories</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>mv &lt;source&gt; &lt;destination&gt;</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Move or rename files or directories</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>./&lt;executable&gt;</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Run an executable file</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;"><code>&gt; &lt;file&gt;</code></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Redirect output to a file</td>
                </tr>
            </tbody>
        </table>
    </section>
    <section id="part5">
        <h3>Part 5 &mdash; Git Synchronization and Recovery</h3>
        <p><strong>Goal:</strong> Practice the Git workflow used throughout this course, including what to do when work was changed on GitHub and your VM no longer matches it.</p>
        <h4>5.1 Mental Model and Safety Rules</h4>
        <p>There are four related states to keep straight:</p>
        <ul>
            <li><strong>Working tree:</strong> files currently visible on your VM.</li>
            <li><strong>Local <code>main</code>:</strong> commits stored in the repository on your VM.</li>
            <li><strong><code>origin/main</code>:</strong> your VM&rsquo;s last fetched record of the remote branch.</li>
            <li><strong>GitHub <code>main</code>:</strong> the current branch stored on GitHub.</li>
        </ul>
        <p><code>git fetch origin</code> updates your knowledge of GitHub but does not change your working files. This is why <code>git status</code> can report that you are up to date before a fetch even when GitHub has a newer commit.</p>
        <blockquote style="border-left: 4px solid #a94442; padding: 1em; background-color: #f2dede; border-radius: 4px;"><strong>Recovery rule:</strong> Do not use <code>git push --force</code> or <code>git reset --hard</code> in this exercise. Both can discard work. Inspect the state first; if you become unsure during a rebase, use <code>git rebase --abort</code> and ask a TA.</blockquote>
        <h4>5.2 Readiness Gate</h4>
        <p><strong>Location:</strong> Host VM Terminal, inside your Classroom 50 repository.</p>
        <pre><code class="language-bash">cd ~/workspaces/intro-to-robotics-fall-2026-lab-01-YOUR_GITHUB_USERNAME
git status
git remote -v
git log --oneline --decorate -n 5</code></pre>
        <p>Do not continue until <code>git status</code> shows no modified files on <code>main</code> (the two Part 3 screenshots in <code>docs/</code> still appear as untracked files, which is expected; they are committed in Step 5.7), <code>origin</code> points to your Classroom repository, and the README commit from Part 2 appears in the log.</p>
        <h4>5.3 Choose a Route</h4>
        <p>Both routes have the same required repository history and deliverables.</p>
        <p><strong>Fast route:</strong> If you already understand Git synchronization, complete this contract without the command-by-command walkthrough:</p>
        <ol>
            <li>Create and commit <code>git_recovery.md</code> using the evidence prompts in Step 5.4.</li>
            <li>Create a remote-ahead state by editing <code>README.md</code> on GitHub. Fetch, inspect the graph, and fast-forward your local branch.</li>
            <li>Create and push a common version of <code>sync_conflict.txt</code>. Then edit its same line differently on GitHub and on your VM. Diagnose the rejected push, inspect the divergence, rebase, resolve the conflict, and push normally.</li>
            <li>Finish the recovery record and satisfy the final checkpoint in Step 5.7.</li>
        </ol>
        <p><strong>Guided route:</strong> Use Steps 5.4&ndash;5.7 below. The commands are given. The predictions, inspection, resolution, and explanations are yours to write.</p>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Using AI tools:</strong> AI assistance is optional and is not needed for this exercise. Make each prediction and your first diagnostic attempt on your own: these Git operations are basic vocabulary for later labs. If you use an AI tool, inspect every command before running it and verify its advice against your actual <code>git status</code> and commit graph.</blockquote>
        <h4>5.4 Start the Recovery Record</h4>
        <p>Create <code>git_recovery.md</code> in your Classroom repository. Use the following headings, but answer the prediction prompts in your own words <strong>before</strong> creating each Git state:</p>
        <pre><code># Git Synchronization and Recovery Record

## Case 1: Remote Ahead
Prediction before fetch:
What `git status` reported before and after fetch:
Relevant graph output:
Recovery command and why it was safe:

## Case 2: Diverged with a Conflict
Prediction before push:
Push rejection diagnosis:
Relevant graph output:
Conflict observed and resolution chosen:
Why the recovery preserved both lines of work:

## Final Verification
Final `git status`:
Final graph output:</code></pre>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Copying and pasting in the terminal:</strong> <kbd>Ctrl+C</kbd> and <kbd>Ctrl+V</kbd> do not work in the VM terminal (<kbd>Ctrl+C</kbd> means &ldquo;interrupt the running program&rdquo; there). Use <kbd>Ctrl+Shift+C</kbd> to copy and <kbd>Ctrl+Shift+V</kbd> to paste, or right-click and choose Copy/Paste. These shortcuts work in the shell and in <code>nano</code>.</blockquote>
        <pre><code class="language-bash">nano git_recovery.md
git add git_recovery.md
git commit -m "Start Git recovery record"
git push origin main</code></pre>
        <p><strong>Checkpoint:</strong> GitHub shows the new recovery-record commit and <code>git status</code> is clean.</p>
        <h4>5.5 Case 1 &mdash; GitHub Is Ahead</h4>
        <ol>
            <li>In your browser, open your Classroom repository on GitHub. Click <code>README.md</code>, then the pencil icon (Edit this file) near the top right of the file view. Add the line <code>- Git synchronization and recovery practice</code> under <code>## Contents</code>. Click the green <strong>Commit changes...</strong> button; in the dialog, replace the suggested commit message with <code>Add remote sync note</code>, leave <strong>Commit directly to the main branch</strong> selected, and confirm.</li>
            <li>Before contacting GitHub from the VM, run <code>git status</code>. Compare the output with your prediction. Your local record of the remote has not been refreshed yet.</li>
            <li>Refresh the remote-tracking branch and inspect the result:
                <pre><code class="language-bash">git fetch origin
git status
git log --oneline --graph --decorate --all -n 8 | tee /tmp/lab1_remote_ahead.txt</code></pre>
                <p>The <code>| tee /tmp/...</code> part prints the output on screen as usual <em>and</em> saves a copy to the named file, so you can paste it into <code>git_recovery.md</code> later with <code>cat</code> instead of retyping it.</p>
                <p>Your output will look similar to this (commit numbers and dates will differ):</p>
                <pre><code>* a1b2c3d (origin/main, origin/HEAD) Add remote sync note
* e4f5a6b (HEAD -&gt; main, tag: submit/2026-09-01T15-04-11Z-e4f5a6b) Start Git recovery record
* c7d8e9f (tag: submit/2026-09-01T14-58-02Z-c7d8e9f) Update README and add setup screenshots
* 1a2b3c4 [Classroom 50] Open Feedback PR (gh student accept)
* 5d6e7f8 (origin/feedback) [Classroom 50] Initialize .classroom50.yaml and autograde workflow (gh student accept)</code></pre>
                <p>The course grading system creates the <code>tag: submit/...</code> labels and the <code>origin/feedback</code> branch automatically when you push; you do not need to inspect them in this exercise. Identify <code>HEAD -&gt; main</code> (your VM&rsquo;s branch) and <code>origin/main</code> (your VM&rsquo;s record of GitHub) before continuing. In this example, they point to different commits because GitHub is one commit ahead.</p>
            </li>
            <li>Bring the remote commit into your local branch without creating a merge commit:
                <pre><code class="language-bash">git pull --ff-only origin main
git status</code></pre>
            </li>
            <li>Update Case 1 in <code>git_recovery.md</code>. Include the relevant lines from the saved graph, then commit and push:
                <pre><code class="language-bash">cat /tmp/lab1_remote_ahead.txt
nano git_recovery.md
git add git_recovery.md
git commit -m "Document remote-ahead recovery"
git push origin main</code></pre>
            </li>
        </ol>
        <p><strong>Checkpoint:</strong> <code>git status</code> reports that local <code>main</code> is up to date with <code>origin/main</code>, and the GitHub README contains the remote edit.</p>
        <h4>5.6 Case 2 &mdash; Rejected Push, Divergence, and Conflict</h4>
        <ol>
            <li>Create a shared starting point and push it:
                <pre><code class="language-bash">printf "sync-state: BASE\n" &gt; sync_conflict.txt
git add sync_conflict.txt
git commit -m "Add sync conflict baseline"
git push origin main</code></pre>
            </li>
            <li>On GitHub, open <code>sync_conflict.txt</code> and edit it the same way you edited the README in Step 5.5 (pencil icon, then <strong>Commit changes...</strong>). Change its only line to <code>sync-state: REMOTE change made on GitHub</code>, set the commit message to <code>Edit sync state on GitHub</code>, and commit directly to <code>main</code>.</li>
            <li>Without pulling, make a different change to the same line on your VM and commit it:
                <pre><code class="language-bash">printf "sync-state: LOCAL change made on VM\n" &gt; sync_conflict.txt
git add sync_conflict.txt
git commit -m "Edit sync state on VM"</code></pre>
            </li>
            <li>Predict what the push will do, then run it and retain the output:
                <pre><code class="language-bash">git push origin main 2&gt;&amp;1 | tee /tmp/lab1_push_rejection.txt</code></pre>
                <p>The <code>2&gt;&amp;1</code> part sends error messages through the pipe along with normal output; without it, the rejection message you are trying to save would go only to the screen. <code>tee</code> saves the output to a file, as in Step 5.5.</p>
                <p>The push should be rejected because neither branch contains the other branch&rsquo;s newest commit. If it succeeds, stop: you likely edited the wrong repository or branch.</p>
            </li>
            <li>Fetch and inspect before choosing a recovery:
                <pre><code class="language-bash">git fetch origin
git status
git log --oneline --graph --decorate --all -n 10 | tee /tmp/lab1_divergence.txt</code></pre>
                <p>Your graph should show <code>main</code> and <code>origin/main</code> on separate commits descended from the conflict baseline.</p>
            </li>
            <li>Choose a recovery that preserves both commits and ends with a linear history. Write down why your choice fits the graph before running it.
                <details>
                    <summary>Hint 1: Identify the required history shape</summary>
                    <p>The GitHub commit should remain where it is, and your local commit should be replayed after it. A merge commit is not needed.</p>
                </details>
                <details>
                    <summary>Hint 2: Show the Git command</summary>
                    <pre><code class="language-bash">git pull --rebase origin main</code></pre>
                </details>
                <p>Run your selected recovery. Git should stop at <code>sync_conflict.txt</code> because it cannot decide which same-line edit to keep.</p>
            </li>
            <li>Inspect the conflict:
                <pre><code class="language-bash">git status
cat sync_conflict.txt</code></pre>
                <p>The <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code>, <code>=======</code>, and <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code> lines delimit the two versions. Replace the entire marker block with one valid line beginning with <code>sync-state:</code> that states how you reconciled the local and remote edits. This resolution is your decision.</p>
            </li>
            <li>Edit the file, mark it resolved, continue the rebase, inspect the result, and push normally.
                <pre><code class="language-bash">nano sync_conflict.txt</code></pre>
                <details>
                    <summary>Hint: Continue after resolving the file</summary>
                    <pre><code class="language-bash">git add sync_conflict.txt
GIT_EDITOR=true git rebase --continue</code></pre>
                    <p><code>GIT_EDITOR=true</code> tells Git to keep the existing commit message instead of opening a text editor for you to confirm it. Without it, the continue step drops you into an editor you then have to save and quit.</p>
                </details>
                <p>Confirm the outcome yourself, then push:</p>
                <pre><code class="language-bash">
git status
git log --oneline --graph --decorate --all -n 10
git push origin main</code></pre>
                <p>A normal push should now succeed. The final history should be linear: the GitHub edit is followed by the replayed VM edit.</p>
            </li>
        </ol>
        <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Recovery ladder:</strong> If the graph does not match the description, use <code>git status</code> and confirm which branch labels point to which commits. If you are in the rebase and cannot identify both versions, run <code>git rebase --abort</code>; this returns you to the pre-rebase state. After one careful retry or 10 minutes, ask a TA. Do not use force-push or destructive reset commands.</blockquote>
        <h4>5.7 Complete and Verify the Recovery Record</h4>
        <p>Update Case 2 and Final Verification in <code>git_recovery.md</code>. Use evidence from your actual run:</p>
        <ul>
            <li>the reason shown in <code>/tmp/lab1_push_rejection.txt</code>;</li>
            <li>the branch structure shown in <code>/tmp/lab1_divergence.txt</code>;</li>
            <li>the conflict markers you observed and the final line you chose; and</li>
            <li>the final clean status and recent commit graph.</li>
        </ul>
        <pre><code class="language-bash">cat /tmp/lab1_push_rejection.txt
cat /tmp/lab1_divergence.txt
nano git_recovery.md
git add git_recovery.md docs/
git commit -m "Document Git sync and conflict recovery"
git push origin main
git fetch origin
git status
git log --oneline --graph --decorate --all -n 12</code></pre>
        <p>Run the automated checks from the repository root. <code>pytest</code> is the Python test runner that <code>test_lab_1.py</code> is written for, and the setup script already installed it.</p>
        <pre><code class="language-bash">pytest -v</code></pre>
        <p><strong>Final checkpoint:</strong> All tests pass; the working tree is clean; <code>main</code> and <code>origin/main</code> point to the same commit; the recent history is linear; and GitHub shows <code>git_recovery.md</code>, all five screenshots, and the resolved <code>sync_conflict.txt</code>.</p>
    </section>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="analysis">
    <h2>6. Analysis and Discussion</h2>
    <p>Record your graded Git analysis in <code>git_recovery.md</code> using evidence from your repository. You should also be able to answer the following questions:</p>
    <ul>
        <li>What is the difference between a Docker <strong>image</strong> and a <strong>container</strong>?</li>
        <li>Why do files placed in <code>~/workspaces</code> survive when the container exits, while files elsewhere in the container do not?</li>
        <li>Why can <code>git status</code> be stale about GitHub until you fetch?</li>
        <li>What is the difference between fetching remote state and integrating it into your current branch?</li>
        <li>Why does rejecting a non-fast-forward push protect work?</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="troubleshooting">
    <h2>9. Troubleshooting</h2>
    <p>Setup, Docker, and Git problems that recur across labs are collected on the course website: <a href="https://mems-intro-to-robotics.github.io/troubleshooting/" target="_blank" rel="noopener">Troubleshooting</a>. It covers the errors this lab is most likely to produce, including <code>docker</code> permission failures, GUI applications that cannot open a display, a blank FastX screen, a rejected <code>git push</code>, a <code>git pull</code> that asks how to reconcile divergent branches, and a rebase that stops with a conflict.</p>
    <p>That page is maintained across semesters, so check it before asking a TA.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>10. References</h2>
    <ul>
        <li><a href="https://git-scm.com/book/en/v2" target="_blank" rel="noopener"><em>Pro Git</em> by Scott Chacon and Ben Straub</a></li>
        <li><a href="http://linuxcommand.org/lc3_learning_the_shell.php" target="_blank" rel="noopener"><em>Learning the Shell</em></a></li>
        <li><a href="https://docs.github.com/" target="_blank" rel="noopener">GitHub Documentation</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/index.html" target="_blank" rel="noopener">ROS 2 Documentation</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
