---
title: "Lab 01: VM and Git Setup"
---

# Lab 01: VM and Git Setup

<div class="lab-content">

<nav id="toc">
    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#prelab">Prelab &mdash; Do Before Lab</a></li>
        <li><a href="#equipment">Equipment and Software</a></li>
        <li><a href="#procedure">Lab Procedure</a></li>
        <li><a href="#references">References</a></li>
    </ol>
</nav>
<section id="introduction">
    <h2>1. Introduction</h2>
    <h3>1.1 Overview</h3>
    <p>This lab serves as the foundation for the rest of the course. You will set up your virtual machine (VM), configure your development environment, and become familiar with the basic workflow we will use throughout the semester. In the second half of the lab, you will complete a Git scavenger hunt to practice essential Git commands in a guided, hands-on way.</p>
    <h3>1.2 Background</h3>
    <p>A consistent and reproducible development environment reduces troubleshooting time and ensures all students start from the same baseline. The Git scavenger hunt is designed to familiarize you with common commands such as <code>git log</code>, <code>git checkout</code>, and <code>git diff</code>, which you will use repeatedly in later labs.</p>
    <h4>Why Are We Using These Tools?</h4>
    <ul>
        <li><strong>Linux (Ubuntu):</strong> We use Linux because it is the industry-standard and primary supported operating system for robotics development, particularly for ROS.</li>
        <li><strong>Git:</strong> Git is a version control system crucial for collaboration and tracking changes in code. Learning it is essential for managing complex software projects.</li>
        <li><strong>Docker:</strong> Docker allows us to run applications in isolated environments called containers. We use it to provide you with a pre-configured environment with ROS 2 and all its dependencies, saving you from a complex installation and ensuring everyone has the exact same setup.</li>
        <li><strong>ROS 2 (Robot Operating System):</strong> ROS is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.</li>
    </ul>
    <h3>1.3 Objectives</h3>
    <ul>
        <li>Set up a complete robotics development environment, starting with a Virtual Machine running Ubuntu, and including VS Code, Docker, and a ROS 2 workspace.</li>
        <li>Practice CLI, SSH, Git branching/PRs, and container basics.</li>
        <li>Explore Git through a structured scavenger hunt.</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="prelab">
    <h2>2. Prelab &mdash; Do Before Lab</h2>
    <h3>2.1 Readings</h3>
    <ul>
        <li><a href="https://git-scm.com/book/en/v2" target="_blank" rel="noopener"><strong><em>Pro Git</em></strong> by Scott Chacon and Ben Straub</a> &mdash; Chapters 1 and 2<br /><em>Focus on repositories, commits, and branches &mdash; no need to memorize every command.</em></li>
        <li><a href="http://linuxcommand.org/lc3_learning_the_shell.php" target="_blank" rel="noopener"><em>Learning the Shell</em></a> &mdash; Sections 1&ndash;10</li>
    </ul>
    <h3>2.2 Reserve Your Course VM</h3>
    <p>We are going to use VMs throughout this course. A <strong>VM (Virtual Machine)</strong> is a computer that runs inside another physical computer, behaving like a separate machine with its own operating system and resources. This allows us to operate a Linux-based computer virtually from our Windows and Mac laptops.</p>
    <ol>
        <li>Go to the <a href="https://vcm.duke.edu" target="_blank" rel="noopener">VCM Portal</a> and sign in with your Duke NetID.<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:446px;min-height:101px;margin:1em auto;">VCM Portal sign in</div></li>
        <li>Select <strong>Reserve a VM</strong> and choose the <strong>ROS VM</strong> for this course.<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:350px;min-height:100px;margin:1em auto;">Reserve a VM option</div></li>
        <li>Note your VM&rsquo;s hostname (e.g., <code>vcm-xxxxx.vm.duke.edu</code>).</li>
        <li>To start your VM, click <em>Book now</em>.<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:364px;min-height:117px;margin:1em auto;">Book now button</div></li>
        <li>VMs run for up to <strong>4 hours per reservation</strong> and then power off automatically. You can renew or reserve a new session if needed.</li>
    </ol>
    <div class="alert alert-warning" style="background-color: #fff3cd; border-color: #ffeeba; padding: 10px; border-radius: 4px; margin-bottom: 20px;"><strong>CRITICAL:</strong> Save your work often! VMs power off after 4 hours.</div>
    <p>If you need to power down (not delete) your VM, click the red trash can.<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:400px;min-height:150px;margin:1em auto;">Power down VM</div></p>
    <h3>2.3 Add Your SSH Key to the Duke Directory</h3>
    <p>An SSH key is a cryptographic key pair (private and public) used to securely authenticate your identity without needing a password. Your computer keeps the private key, and you give the public key to Duke. This allows for a public/private key handshake during every login. Using SSH keys with VMs improves security and convenience by preventing password theft and allowing automated, encrypted logins.</p>
    <p>This ensures the VCM can configure secure access for your VM. Generate it once on <em>your laptop</em> in a terminal (such as PowerShell) and paste it into the Duke Directory.</p>
    <ol>
        <li><strong>Generate a new SSH key</strong> (replace with your Duke email):
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
    <p>Click on "+ See More about SSH keys" button to show the box to enter your SSH key.<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:475px;min-height:90px;margin:1em auto;">SSH key entry</div></p>
    <p><em>Additional resources: <a href="https://vcm.duke.edu/help/23" target="_blank" rel="noopener">VCM SSH Key Guide</a></em></p>
    <h3>2.4 Configure Your VM Environment</h3>
    <ol>
        <li>SSH into your VM from your laptop:
            <pre><code class="language-bash">ssh yourNetID@vcm-xxxxx.vm.duke.edu</code></pre>
        </li>
        <li>Download the setup script:
            <pre><code class="language-bash">cd ~
curl -L "https://gitlab.oit.duke.edu/introtorobotics/mems-robotics-toolkit/-/raw/main/vm_setup.sh" -o vm_setup.sh
chmod +x vm_setup.sh</code></pre>
        </li>
        <li>Run the setup script with the provided license key:
            <pre><code class="language-bash">FASTX_ACTIVATION_KEY="5663-3746-0011-6357" ./vm_setup.sh</code></pre>
        </li>
    </ol>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Notes on Using the Terminal</strong><br />
        <ul>
            <li>When you enter your password for <code>sudo</code> in Linux, nothing will appear on screen (no dots or asterisks). This is normal &mdash; just type your password and press <strong>Enter</strong>.</li>
            <li>You may see messages like <code>SyntaxWarning: invalid escape sequence</code> when Terminator installs. These warnings are harmless and can be ignored.</li>
        </ul>
    </blockquote>
    <ol start="4">
        <li>If the setup script does not fully activate FastX, run the following command manually:
            <pre><code class="language-bash">sudo -u fastx /usr/lib/fastx/4/install/activate</code></pre>
            <p>Enter the license key when prompted: <code>5663-3746-0011-6357</code></p>
            <p>Enter 1 for number of seats to activate. When activation succeeds, you should see confirmation messages about the license being applied.</p>
        </li>
        <li>When the script finishes, <strong>log out of the SSH session by typing <code>exit</code> in the terminal</strong>.</li>
    </ol>
    <h3>2.5 Install &amp; Configure FastX Desktop Client</h3>
    <p><strong>FastX</strong> is a remote desktop software that lets you securely connect to Linux servers or VMs and run applications. We use it to connect to VMs because it provides a GUI-based way to access full desktop environments.</p>
    <ol>
        <li>Download and install the <a href="https://www.starnet.com/download-fastx-client/" target="_blank" rel="noopener"><strong>FastX 4 Desktop Client</strong></a> (not the Server).</li>
        <li>Add a new <strong>SSH Connection</strong>:<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:166px;min-height:98px;margin:1em auto;">Add SSH connection</div>
            <ul>
                <li><strong>Host:</strong> <code>vcm-xxxxx.vm.duke.edu</code></li>
                <li><strong>User:</strong> your NetID</li>
                <li><strong>Port:</strong> <code>22</code> (default, don&rsquo;t change)</li>
            </ul>
            <div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:268px;min-height:150px;margin:1em auto;">SSH connection settings</div>
        </li>
        <li>Create a new session:<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:363px;min-height:129px;margin:1em auto;">Create new session</div>
            <ul>
                <li><strong>Command:</strong> <code>startxfce4</code></li>
                <li><strong>Window Mode:</strong> <strong>Single</strong> (not Multiple)</li>
            </ul>
            <div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:457px;min-height:96px;margin:1em auto;">Session settings</div>
        </li>
        <li>Launch the session. On first run, if prompted, choose the <strong>default XFCE panel layout</strong>.<br /><div class="image-placeholder" style="background:#e0e0e0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#666;font-style:italic;text-align:center;padding:1em;max-width:277px;min-height:150px;margin:1em auto;">XFCE panel layout</div></li>
    </ol>
    <p>📸 <strong>Screenshot Requirement:</strong> Take a screenshot showing your VM desktop running through FastX. This will be submitted as part of your deliverables.</p>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="equipment">
    <h2>3. Equipment and Software</h2>
    <h3>3.1 Hardware</h3>
    <ul>
        <li>Personal computer capable of running the course VM.</li>
    </ul>
    <h3>3.2 Software (On VM)</h3>
    <ul>
        <li>Course VM image (Ubuntu)</li>
        <li>VS Code</li>
        <li>Docker (installed via provided script)</li>
        <li>Git (SSH configured)</li>
        <li>ROS 2 Jazzy (inside Docker image)</li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="procedure">
    <h2>4. Lab Procedure</h2>
    <h3>4.1 Connect to Your VM</h3>
    <ol>
        <li><strong>Open the FastX Desktop Client</strong> on your laptop.</li>
        <li><strong>Connect to your VM</strong> using the SSH connection you created in the prelab:
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
    <h3>4.2 Verify Access</h3>
    <ol>
        <li>Open a terminal inside your XFCE desktop (from the <strong>Applications</strong> menu or by right-clicking the desktop &rarr; <strong>Open Terminal</strong>).</li>
        <li>Run the following commands to confirm key tools are installed:
            <pre><code class="language-bash">docker --version
git --version
code --version</code></pre>
        </li>
        <li>You should see output similar to the following (exact numbers may differ):
            <div style="background-color: #f8f9fa; border-left: 4px solid #005a9c; padding: 1em; margin-top: 1em; border-radius: 4px;">
                <pre style="margin: 0; font-family: monospace; font-size: 0.9em;"><code>Docker version XX.X.X, build XXXXXXX
git version X.XX.X
1.10X.X
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
x64</code></pre>
            </div>
        </li>
    </ol>
    <blockquote style="border-left: 4px solid #d9534f; padding: 1em; background-color: #f8d7da; border-radius: 4px;"><strong>Stop:</strong> If <code>docker</code> commands fail with a permissions error, you likely need to <strong>reboot your VM once</strong> after running the setup script. Run <code>sudo reboot</code> in your VM&rsquo;s terminal to restart.</blockquote>
    <h3>4.3 Submit a Screenshot</h3>
    <p>Take a screenshot of your VM desktop with the terminal open (showing the version checks above). Save the file to your home directory for your records and for TA verification.</p>
    <h3>4.4 Git Setup</h3>
    <h4>4.4.1 Create or Access Your GitHub Account</h4>
    <p>We use <strong>GitHub Classroom</strong> for assignment submissions. Each lab has its own assignment link that creates a private repository for you. Your repositories are only visible to you and the teaching staff.</p>
    <ol>
        <li>If you don&rsquo;t already have a GitHub account, create one at <a href="https://github.com/signup" target="_blank" rel="noopener">https://github.com/signup</a>.</li>
        <li>If you already have a GitHub account, you can use your existing account.</li>
    </ol>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> Course materials (Docker images, reference code, the scavenger hunt) are hosted on Duke GitLab. Your <em>submissions</em> go to GitHub Classroom. You do not need a Duke GitLab account for submissions.</blockquote>
    <h4>4.4.2 Generate an SSH Key on Your VM and Add it to GitHub</h4>
    <p>You will generate a new SSH key <strong>inside your VM</strong>. This allows the VM to authenticate with GitHub, which is required since all ROS 2 development for this course will be done in your VM environment.</p>
    <ol>
        <li>In your VM terminal, generate a key pair (use your email):
            <pre><code class="language-bash">ssh-keygen -t ed25519 -C "your_email@example.com"</code></pre>
            Press <kbd>Enter</kbd> to accept the default location (<code>~/.ssh/id_ed25519</code>). This creates two files:
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
            You should see a message like <em>&ldquo;Hi username! You&rsquo;ve successfully authenticated...&rdquo;</em>
        </li>
    </ol>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Note:</strong> You may also add your <strong>laptop&rsquo;s</strong> SSH key to GitHub if you want to work directly from your laptop. However, this course requires you to add the <strong>VM key</strong> since all ROS 2 development will be done inside the VM.</blockquote>
    <p>📸 <strong>Screenshot Requirement:</strong> Capture the terminal output confirming that you can connect to GitHub. This will be submitted as part of your deliverables.</p>
    <h4>4.4.3 Accept the GitHub Classroom Assignment and Clone Your Repository</h4>
    <ol>
        <li><strong>Accept the assignment:</strong> Click the following link to create your Lab 1 repository:
            <p style="margin: 1em 0;"><a style="font-size: 1.1em;" href="https://classroom.github.com/a/48Vq28p_" target="_blank" rel="noopener">https://classroom.github.com/a/48Vq28p_</a></p>
            <ul>
                <li>Sign in to GitHub if prompted.</li>
                <li>Select your name from the roster (if shown) to link your GitHub account to your identity in the course.</li>
                <li>Accept the assignment. GitHub Classroom will create a private repository for you under the course organization.</li>
            </ul>
        </li>
        <li><strong>Accept the repository invitation:</strong> GitHub Classroom creates your repo, but you must also accept a collaboration invite before you can access it.
            <ul>
                <li>Check your email for an invite from <strong>MEMS-Intro-to-Robotics</strong>, or</li>
                <li>Go directly to your repo URL (see next step) and click <strong>Accept invitation</strong> on the banner at the top.</li>
            </ul>
        </li>
        <li><strong>Note your repository URL:</strong> After accepting, you&rsquo;ll see a URL like:
            <pre><code>https://github.com/MEMS-Intro-to-Robotics/lab-01-vm-and-git-YOUR_GITHUB_USERNAME</code></pre>
        </li>
        <li><strong>Clone the repository into your workspace:</strong>
            <pre><code class="language-bash">mkdir -p ~/workspaces
cd ~/workspaces
git clone git@github.com:MEMS-Intro-to-Robotics/lab-01-vm-and-git-YOUR_GITHUB_USERNAME.git
cd lab-01-vm-and-git-YOUR_GITHUB_USERNAME</code></pre>
            <p>Replace <code>YOUR_GITHUB_USERNAME</code> with your actual GitHub username.</p>
        </li>
        <li><strong>Configure Git identity:</strong>
            <pre><code class="language-bash">git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"</code></pre>
        </li>
        <li><strong>Update the README and push:</strong>
            <ol>
                <li>Open the README in nano:
                    <pre><code class="language-bash">nano README.md</code></pre>
                </li>
                <li>Update it with your information. A suggested format:
                    <pre><code># Lab 01: VM and Git Setup &mdash; [Your Name]
ECE 383 / ME 555: Introduction to Robotics and Automation (Spring 2026)
## Contents
- `docs/` &mdash; Screenshots and documentation
- `flags.txt` &mdash; Git scavenger hunt results</code></pre>
                </li>
                <li>Save and exit nano:
                    <ul>
                        <li>Press <strong>Ctrl+O</strong> (write out), hit <strong>Enter</strong> to confirm.</li>
                        <li>Press <strong>Ctrl+X</strong> to exit.</li>
                    </ul>
                </li>
                <li>Stage, commit, and push your changes:
                    <pre><code class="language-bash">git add README.md
git commit -m "Update README with lab info"
git push origin main</code></pre>
                </li>
            </ol>
        </li>
    </ol>
    <h3>4.5 Docker-based ROS 2 Environment</h3>
    <p>You will do all your ROS 2 development <strong>inside the course Docker container</strong>.</p>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Image vs. Container</strong><br />
        <ul>
            <li>A <strong>Docker image</strong> is like a blueprint &mdash; it&rsquo;s a read-only package that includes the operating system, software, and configurations needed for a project.</li>
            <li>A <strong>Docker container</strong> is a running instance of that image. You can think of it as &ldquo;launching&rdquo; the image so you can interact with it, make changes, and run programs inside it.</li>
            <li>Multiple containers can be created from the same image, and each container is isolated from your host system.</li>
        </ul>
    </blockquote>
    <h4>4.5.1 Prepare</h4>
    <ol>
        <li>Open a terminal on your VM.</li>
        <li>If you haven&rsquo;t already, ensure the VM setup script from section 2.4 has been run.</li>
        <li>You should already have a <code>~/workspaces</code> directory from cloning your Lab 1 repo. We&rsquo;ll use that same folder for all ROS 2 development.</li>
    </ol>
    <h4>4.5.2 Pull the Course Image</h4>
    <p>Pull the prebuilt course image from the Duke GitLab Container Registry:</p>
    <pre><code class="language-bash">docker pull gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest</code></pre>
    <h4>4.5.3 Allow GUI Connections</h4>
    <p>On your VM, before starting the container, run the following command. This grants Docker permission to draw graphical windows (like the turtle simulator) on your VM&rsquo;s desktop:</p>
    <pre><code class="language-bash">xhost +local:docker</code></pre>
    <h4>4.5.4 Run the Container (mount your workspace)</h4>
    <p>Change into your <code>workspaces</code> directory and start an interactive shell with it mounted at <code>/workspaces</code>, with X11 passthrough so graphical applications can launch:</p>
    <pre><code class="language-bash">cd ~/workspaces
docker run --rm -it \
  -v $PWD:/workspaces \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  gitlab-registry.oit.duke.edu/introtorobotics/mems-robotics-toolkit:base-jazzy-latest bash</code></pre>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Dissecting the <code>docker run</code> command:</strong>
        <ul>
            <li><code>--rm</code>: Automatically removes the container when you exit.</li>
            <li><code>-it</code>: Runs the container in interactive mode and gives you a terminal.</li>
            <li><code>-v $PWD:/workspaces</code>: Mounts your current host directory (<code>$PWD</code>) into the container at the <code>/workspaces</code> path. This is how you access your files from within the container.</li>
            <li><code>-e ...</code> and the second <code>-v ...</code>: These flags allow graphical applications to run from inside the container.</li>
        </ul>
    </blockquote>
    <p>Once inside the container, confirm that ROS 2 Jazzy is available:</p>
    <pre><code class="language-bash">echo $ROS_DISTRO</code></pre>
    <p>This should return <code>jazzy</code>.</p>
    <p>Next, check that ROS 2 commands work properly by listing nodes:</p>
    <pre><code class="language-bash">ros2 node list</code></pre>
    <p>If no nodes are running yet, the command may return an empty list &mdash; that is expected.</p>
    <p>📸 <strong>Screenshot Requirement:</strong> Capture the output of both commands (<code>echo $ROS_DISTRO</code> and <code>ros2 node list</code>) in your terminal.</p>
    <h4>4.5.5 Run a Talker/Listener Demo (test Python and C++)</h4>
    <ol>
        <li>Inside the container, launch a multi-pane terminal:
            <pre><code class="language-bash">terminator</code></pre>
            <p>To create multiple panes, right-click inside the Terminator window and select <strong>Split Horizontally</strong> or <strong>Split Vertically</strong>.</p>
        </li>
        <li>In <strong>pane A</strong>, run a C++ talker node:
            <pre><code class="language-bash">ros2 run demo_nodes_cpp talker</code></pre>
        </li>
        <li>In <strong>pane B</strong>, run a Python listener node:
            <pre><code class="language-bash">ros2 run demo_nodes_py listener</code></pre>
        </li>
        <li>The listener should print the string messages published by the talker. This confirms that both C++ and Python ROS 2 nodes work correctly.</li>
    </ol>
    <p>📸 <strong>Screenshot Requirement:</strong> Capture both panes in the same window, with the listener actively printing messages. This will be submitted as part of your deliverables.</p>
    <h4>4.5.6 Exit the Docker Container</h4>
    <p>Once you have verified the demo, close the <code>terminator</code> window, then type <code>exit</code> in your primary terminal.</p>
    <h3>4.6 Command Line Practice</h3>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Terminal Tip: Use Tab Auto-Completion!</strong><br />Save time and avoid typos using the Tab key. Start typing a command, file, or directory name and press Tab. The terminal will attempt to auto-complete it. If there are multiple possibilities, press Tab twice to see them all. Get in the habit of using this &mdash; it&rsquo;s a superpower!</blockquote>
    <p>Understanding command-line operations is essential for working efficiently with ROS 2 and Linux systems.</p>
    <h4>4.6.1 Watch the <em>Command Line Interface</em> Video</h4>
    <p>This video provides an introduction to using the Linux command line. Pay attention to common commands and navigation techniques.</p>
    <h4>4.6.2 Work Through Examples</h4>
    <p>Practice the examples in <em>Learning the Shell</em> (sections 1&ndash;10). This hands-on work reinforces your understanding.</p>
    <h4>4.6.3 Directory and File Practice</h4>
    <p>Try the following exercises in your VM terminal:</p>
    <ol>
        <li>Change into a directory called <code>cli_practice</code>:
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
    <h3>4.7 Git Scavenger Hunt</h3>
    <p>You will now practice core Git commands by finding hidden <code>FLAG{}</code> entries in a special repository. Each flag is hidden in a different part of Git history or state. The goal is to make you comfortable exploring commits, branches, tags, stashes, and diffs using the CLI.</p>
    <blockquote style="border-left: 4px solid #005a9c; padding: 1em; background-color: #d9edf7; border-radius: 4px;"><strong>Tip:</strong> In the terminal, you can use the <strong>Up Arrow</strong> and <strong>Down Arrow</strong> keys to cycle through your previous commands to save typing!</blockquote>
    <ol>
        <li><strong>Clone the scavenger hunt repository:</strong>
            <pre><code class="language-bash">cd ~/workspaces
git clone https://gitlab.oit.duke.edu/introtorobotics/git-scavenger-hunt.git
cd git-scavenger-hunt</code></pre>
        </li>
        <li><strong>Read the starting clue:</strong>
            <pre><code class="language-bash">cat clues.txt</code></pre>
            <p>This file will guide you toward the first flag.</p>
        </li>
        <li><strong>Search for flags in different Git locations.</strong> You may need to use:
            <ul>
                <li><strong><code>git log</code></strong> &mdash; shows commit history. Use it to look for flags hidden in commit messages or older versions of files.
                    <pre><code class="language-bash">git log --oneline --decorate
git log --grep 'FLAG{'           # search messages for flag-like text
git log -p -- &lt;file&gt;             # see how a specific file changed</code></pre>
                    <p><em>(Press <code>q</code> to quit the log viewer.)</em></p>
                </li>
                <li><strong><code>git branch</code> and <code>git checkout</code></strong> &mdash; list and switch to branches. Flags may be hidden on non-<code>main</code> branches.
                    <pre><code class="language-bash">git branch -a
git checkout &lt;branch&gt;
# or inspect a file on another branch without switching:
git show origin/&lt;branch&gt;:&lt;path/to/file&gt;</code></pre>
                </li>
                <li><strong><code>git tag</code> and <code>git show &lt;tag&gt;</code></strong> &mdash; list and inspect tags. Tags are like bookmarks; annotated tags can contain messages.
                    <pre><code class="language-bash">git tag
git show &lt;tag&gt;</code></pre>
                </li>
                <li><strong><code>git diff</code></strong> &mdash; compare commits or branches. Use it to see what changed between two versions.
                    <pre><code class="language-bash">git diff &lt;base&gt;..&lt;topic&gt;
git diff &lt;base&gt;..&lt;topic&gt; -- &lt;file&gt;</code></pre>
                </li>
                <li><strong><code>git stash</code></strong> &mdash; list and inspect stashed changes (if any).
                    <pre><code class="language-bash">git stash list
git stash show -p stash@{0}</code></pre>
                </li>
            </ul>
        </li>
        <li><strong>Record each flag you find (in order):</strong>
            <pre><code class="language-bash">nano flags.txt</code></pre>
            <p>Add each <code>FLAG{}</code> in the order you find them. Save and close.</p>
        </li>
        <li><strong>Commit and push your results to your GitHub repository:</strong>
            <pre><code class="language-bash">cp flags.txt ~/workspaces/lab-01-vm-and-git-YOUR_GITHUB_USERNAME/
cd ~/workspaces/lab-01-vm-and-git-YOUR_GITHUB_USERNAME
git add flags.txt
git commit -m "Completed Git scavenger hunt"
git push origin main</code></pre>
        </li>
    </ol>
    <h3>4.8 Troubleshooting / Common Issues</h3>
    <ul>
        <li><strong>Symptom:</strong> <code>git push</code> fails with a &lsquo;permission denied&rsquo; error.
            <ul>
                <li><strong>Diagnosis:</strong> Your SSH key is not set up correctly in GitHub.</li>
                <li><strong>Solution:</strong> Go back to section 4.4.2, re-run the <code>cat</code> command to view your public key, and ensure the entire key is correctly pasted into your GitHub settings under SSH keys.</li>
            </ul>
        </li>
        <li><strong>Symptom:</strong> Any <code>docker</code> command fails with a &lsquo;permission denied&rsquo; error.
            <ul>
                <li><strong>Diagnosis:</strong> Docker group permissions have not been applied.</li>
                <li><strong>Solution:</strong> Make sure you have rebooted your VM after running the <code>vm_setup.sh</code> script, as this applies the necessary permissions. If you have rebooted, try closing and reopening your terminal.</li>
            </ul>
        </li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>
<section id="references">
    <h2>6. References</h2>
    <ul>
        <li><a href="https://git-scm.com/book/en/v2" target="_blank" rel="noopener"><em>Pro Git</em> by Scott Chacon and Ben Straub</a></li>
        <li><a href="http://linuxcommand.org/lc3_learning_the_shell.php" target="_blank" rel="noopener"><em>Learning the Shell</em></a></li>
        <li><a href="https://docs.github.com/" target="_blank" rel="noopener">GitHub Documentation</a></li>
        <li><a href="https://docs.ros.org/en/jazzy/index.html" target="_blank" rel="noopener">ROS 2 Documentation</a></li>
    </ul>
    <p><a href="#toc">&uarr; Back to top</a></p>
</section>

</div>
