# Setup scripts guide

This repo contains several machine-setup scripts. They target different environments, so this page explains which one should own which job.

## Script matrix

| Script | Intended environment | What it does |
|---|---|---|
| `vm_setup.sh` | Student-facing Duke VCM or FastX VM | Installs the standard student desktop stack, Docker, FastX, VS Code, and optional NVIDIA container tooling |
| `vm_setup_dev.sh` | Personal VMware or Ubuntu developer VM | Installs a richer developer workstation stack with Docker, Git extras, pipx tools, Node via `nvm`, and shell customization |
| `ubuntu_desktop_setup.sh` | Shared lab desktop or managed Ubuntu workstation | Boots a machine-level desktop with Docker, VS Code, optional NVIDIA tooling, and Duke CrowdStrike setup |
| `ubuntu_desktop_setup.env.example` | Companion config for `ubuntu_desktop_setup.sh` | Shows required environment variables for lab desktop setup |
| `gpu_install.sh` | Standalone GPU Docker repair/helper | Configures NVIDIA Container Toolkit on Ubuntu when you only need GPU container support |
| `utilities.sh` | Older utility installer | Installs common packages and Firefox from the Mozilla PPA; overlaps with the newer setup scripts |

## Recommended ownership

### `vm_setup.sh`

Use this for the default student VM story. It is the script that matches the existing course workflow of FastX plus Docker on a remote VM.

Highlights from the script:

- Sets locale
- Installs developer utilities
- Installs Docker and adds the current user to the `docker` group
- Installs Firefox, VS Code, and recommended extensions
- Installs XFCE plus FastX server
- Attempts NVIDIA Container Toolkit setup when possible

### `vm_setup_dev.sh`

Use this when the machine is a personal development VM rather than a shared course VM.

Highlights from the script:

- Installs VMware guest tools
- Installs a broader workstation package set
- Adds Git extras like `git-lfs`, `delta`, and `lazygit`
- Installs `black`, `ruff`, and `httpie` through `pipx`
- Installs Node.js with `nvm`
- Adds optional shell tooling like zsh, Oh My Zsh, and Starship

### `ubuntu_desktop_setup.sh`

Use this for shared lab desktops where the machine itself needs to be prepared, not an individual user shell.

Highlights from the script:

- Reads configuration from `ubuntu_desktop_setup.env`
- Handles root or sudo execution
- Installs machine-level dependencies and services
- Configures VS Code and Docker
- Optionally configures NVIDIA container runtime
- Can install Duke CrowdStrike Falcon Sensor when the required installer path and CCID are provided

### `gpu_install.sh`

Use this when Docker is already installed and you only need to set up or repair NVIDIA GPU support. It is much narrower than the full setup scripts.

### `utilities.sh`

Treat this as a legacy helper unless there is a specific reason to keep using it directly. Its package-install role overlaps with `vm_setup.sh`, so it should not become the main documented path unless you intentionally simplify the course setup workflow around it.

## Suggested documentation split

- Student-facing docs should point primarily to `vm_setup.sh`.
- Maintainer docs should explain when to use `vm_setup_dev.sh` versus `ubuntu_desktop_setup.sh`.
- GPU setup should stay in its own troubleshooting page or appendix because only a subset of machines need it.

## What still needs follow-up

- None of these scripts are documented as the single official default yet, so students could still guess wrong.
- `utilities.sh` overlaps with newer scripts and would benefit from either deprecation language or a clearer purpose statement.
