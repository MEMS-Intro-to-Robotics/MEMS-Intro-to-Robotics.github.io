# Setup Scripts

Bootstrap scripts for provisioning student VMs, developer workstations, shared lab desktops, and GPU-enabled Docker hosts. All scripts are bundled in the [`scripts/`](https://github.com/MEMS-Intro-to-Robotics/MEMS-Intro-to-Robotics.github.io/tree/main/scripts) directory of this repository.

## Overview

| Script | Target Environment | Lines |
|--------|-------------------|-------|
| [`vm_setup.sh`](#vm_setupsh) | Student VM (FastX remote desktop) | ~220 |
| [`vm_setup_dev.sh`](#vm_setup_devsh) | Developer/TA VM (VMware) | ~330 |
| [`ubuntu_desktop_setup.sh`](#ubuntu_desktop_setupsh) | Shared lab desktop | ~390 |
| [`ubuntu_desktop_setup.env.example`](#ubuntu_desktop_setupenvexample) | Config template for lab desktop setup | ~15 |
| [`gpu_install.sh`](#gpu_installsh) | Standalone NVIDIA Container Toolkit install (GPU dev VMs, Lab 06) | ~85 |

## Environment Ownership Model

Each script targets one environment. Pick the one that matches your setup:

- **Student environment** (`vm_setup.sh`): The default path for students. Installs ROS 2 Jazzy, Docker, course container images, and shell configuration on a clean Ubuntu VM with FastX remote desktop access.
- **Developer environment** (`vm_setup_dev.sh`): A richer path for TAs and maintainers. Assumes VMware instead of FastX, installs additional dev tooling.
- **Shared lab desktops** (`ubuntu_desktop_setup.sh`): Machine-level bootstrap for persistent lab computers. Handles Docker, optional NVIDIA runtime, and system services — avoids per-user customization.
- **Standalone GPU path** (`gpu_install.sh`): Narrowly scoped — only installs the NVIDIA Container Toolkit. Use it on GPU-enabled dev VMs (Lab 06 points students here) or to repair a machine's GPU container runtime. The lab desktop script already includes this logic, so shared lab desktops never need it separately.

---

## `vm_setup.sh`

Student-facing VM setup. Installs locale, ROS 2 Jazzy, Docker, pulls course container images, and configures the shell environment.

??? note "Full script"
    ```bash
    --8<-- "scripts/vm_setup.sh"
    ```

---

## `vm_setup_dev.sh`

Developer/TA VM setup. Similar to the student script but assumes VMware (installs `open-vm-tools`), allows snap Firefox, and includes a richer development environment.

??? note "Full script"
    ```bash
    --8<-- "scripts/vm_setup_dev.sh"
    ```

---

## `ubuntu_desktop_setup.sh`

Shared lab desktop bootstrap. Machine-level only: installs packages and services, configures Docker and optional NVIDIA container runtime, avoids per-user shell/editor customization.

Accepts optional environment variables via a `.env` file — see the example below.

??? note "Full script"
    ```bash
    --8<-- "scripts/ubuntu_desktop_setup.sh"
    ```

---

## `ubuntu_desktop_setup.env.example`

Configuration template for the lab desktop setup script.

```bash
--8<-- "scripts/ubuntu_desktop_setup.env.example"
```

---

## `gpu_install.sh`

Installs the NVIDIA Container Toolkit on Ubuntu (24.04-friendly). Safe to re-run. `ubuntu_desktop_setup.sh` performs these same steps when it detects an NVIDIA GPU — this standalone copy exists for machines that only need the GPU container runtime added (for example, a student dev VM being prepared for Lab 06).

```bash
--8<-- "scripts/gpu_install.sh"
```
