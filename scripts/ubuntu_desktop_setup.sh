#!/usr/bin/env bash
# =============================================================================
# Ubuntu Lab Desktop Setup
# Duke University, Thomas Lord Department of Mechanical Engineering & Materials Science
#
# Fresh Ubuntu desktop bootstrap for shared lab machines.
# This script intentionally stays machine-level:
#   - installs shared packages and services
#   - configures Docker and optional NVIDIA container runtime
#   - avoids per-user shell/editor customization
#
# Optional environment variables:
#   UBUNTU_DESKTOP_SETUP_ENV=/path/to/ubuntu_desktop_setup.env
#   LAB_DESKTOP_USER=<username>   Add this user to the docker group.
#   DUKE_FALCON_DEB=/path/to/falcon-sensor_<version>_amd64.deb
#   DUKE_FALCON_CCID=<customer-id-with-checksum>
#   DUKE_FALCON_PROXY_HOST=<proxy-host>
#   DUKE_FALCON_PROXY_PORT=<proxy-port>
#   DUKE_FALCON_MASTER_IMAGE=1    Remove the Falcon agent ID for image cloning.
#   SKIP_DUKE_CROWDSTRIKE=1       Bypass Duke CrowdStrike installation.
# =============================================================================

set -euo pipefail

say()  { printf "\n\033[1;36m===== %s =====\033[0m\n\n" "$*"; }
warn() { printf "\n\033[1;33m[WARN]\033[0m %s\n" "$*" >&2; }
err()  { printf "\n\033[1;31m[ERROR]\033[0m %s\n" "$*" >&2; }

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_ENV_FILE="${SCRIPT_DIR}/ubuntu_desktop_setup.env"
CONFIG_FILE="${UBUNTU_DESKTOP_SETUP_ENV:-${DEFAULT_ENV_FILE}}"
CONFIG_DIR=""

load_config_file() {
  if [[ -n "${UBUNTU_DESKTOP_SETUP_ENV:-}" && ! -f "${CONFIG_FILE}" ]]; then
    err "Config file not found: ${CONFIG_FILE}"
    exit 1
  fi

  if [[ -f "${CONFIG_FILE}" ]]; then
    CONFIG_DIR="$(cd -- "$(dirname -- "${CONFIG_FILE}")" && pwd)"
    say "Loading config from ${CONFIG_FILE}"
    set -a
    # shellcheck source=/dev/null
    . "${CONFIG_FILE}"
    set +a

    if [[ -n "${DUKE_FALCON_DEB:-}" && "${DUKE_FALCON_DEB}" != /* ]]; then
      DUKE_FALCON_DEB="${CONFIG_DIR}/${DUKE_FALCON_DEB}"
    fi
  fi
}

load_config_file

if [[ ${EUID} -eq 0 ]]; then
  SUDO=()
else
  if ! command -v sudo >/dev/null 2>&1; then
    err "sudo is required when running as a non-root user."
    exit 1
  fi
  sudo -v
  SUDO=(sudo)
fi

sudo_run() {
  "${SUDO[@]}" "$@"
}

wait_for_apt_locks() {
  # fuser lives in psmisc, which may not be present on a fresh install
  if ! command -v fuser >/dev/null 2>&1; then
    sudo_run apt-get install -y psmisc 2>/dev/null || true
  fi

  local lock_files=(
    /var/lib/dpkg/lock-frontend
    /var/lib/dpkg/lock
    /var/lib/apt/lists/lock
    /var/cache/apt/archives/lock
  )

  while sudo_run fuser "${lock_files[@]}" >/dev/null 2>&1; do
    say "Waiting for apt/dpkg locks..."
    sleep 5
  done
}

package_exists() {
  apt-cache show "$1" >/dev/null 2>&1
}

package_installed() {
  dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"
}

resolve_target_user() {
  if [[ -n "${LAB_DESKTOP_USER:-}" ]]; then
    printf '%s\n' "${LAB_DESKTOP_USER}"
    return 0
  fi

  if [[ ${EUID} -eq 0 ]]; then
    if [[ -n "${SUDO_USER:-}" && "${SUDO_USER}" != "root" ]]; then
      printf '%s\n' "${SUDO_USER}"
    fi
    return 0
  fi

  printf '%s\n' "${USER}"
}

has_nvidia_gpu() {
  if command -v nvidia-smi >/dev/null 2>&1; then
    return 0
  fi

  if command -v lspci >/dev/null 2>&1 && lspci | grep -qi 'NVIDIA'; then
    return 0
  fi

  return 1
}

ensure_packages() {
  wait_for_apt_locks
  sudo_run apt-get install -y "$@"
}

configure_vscode_repo() {
  say "Configuring Visual Studio Code repository"
  sudo_run install -d -m 0755 /usr/share/keyrings
  wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
    | sudo_run gpg --dearmor --batch --yes -o /usr/share/keyrings/packages.microsoft.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main" \
    | sudo_run tee /etc/apt/sources.list.d/vscode.list >/dev/null
}

install_nvidia_container_toolkit() {
  say "Installing NVIDIA Container Toolkit"

  sudo_run rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list \
                  /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg || true

  sudo_run install -d -m 0755 /usr/share/keyrings
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo_run gpg --dearmor --batch --yes -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

  echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/amd64 /" \
    | sudo_run tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null

  wait_for_apt_locks
  sudo_run apt-get update -y
  sudo_run apt-get install -y \
    libnvidia-container1 libnvidia-container-tools \
    nvidia-container-toolkit-base nvidia-container-toolkit

  if command -v nvidia-ctk >/dev/null 2>&1; then
    sudo_run nvidia-ctk runtime configure --runtime=docker || warn "nvidia-ctk runtime configure failed."
    sudo_run systemctl restart docker
  else
    warn "nvidia-ctk was not found after install; Docker NVIDIA runtime was not configured."
  fi
}

install_duke_crowdstrike() {
  say "Installing Duke CrowdStrike Falcon Sensor"

  if [[ "${SKIP_DUKE_CROWDSTRIKE:-0}" == "1" ]]; then
    warn "Skipping Duke CrowdStrike installation because SKIP_DUKE_CROWDSTRIKE=1 was set."
    return 0
  fi

  local falcon_deb="${DUKE_FALCON_DEB:-}"
  local falcon_ccid="${DUKE_FALCON_CCID:-}"
  local proxy_host="${DUKE_FALCON_PROXY_HOST:-}"
  local proxy_port="${DUKE_FALCON_PROXY_PORT:-}"
  local master_image="${DUKE_FALCON_MASTER_IMAGE:-0}"
  local falcon_installed_before=0

  if package_installed falcon-sensor; then
    falcon_installed_before=1
    warn "falcon-sensor is already installed. Duke OIT does not support changing CID in place; purge and reinstall if you need a different CID."
  else
    if [[ -z "${falcon_deb}" ]]; then
      err "DUKE_FALCON_DEB is required. Download the Debian Falcon installer from Duke OIT and pass its local path."
      exit 1
    fi

    if [[ -z "${falcon_ccid}" ]]; then
      err "DUKE_FALCON_CCID is required. Retrieve the Duke CrowdStrike CCID and pass it to the script."
      exit 1
    fi

    if [[ ! -f "${falcon_deb}" ]]; then
      err "CrowdStrike installer not found at: ${falcon_deb}"
      exit 1
    fi

    sudo_run dpkg -i "${falcon_deb}" || {
      wait_for_apt_locks
      sudo_run apt-get install -f -y
      sudo_run dpkg -i "${falcon_deb}"
    }
  fi

  if [[ ! -x /opt/CrowdStrike/falconctl ]]; then
    err "falconctl was not found after installing falcon-sensor."
    exit 1
  fi

  if [[ -n "${proxy_host}" || -n "${proxy_port}" ]]; then
    if [[ -z "${proxy_host}" || -z "${proxy_port}" ]]; then
      err "Set both DUKE_FALCON_PROXY_HOST and DUKE_FALCON_PROXY_PORT together."
      exit 1
    fi
    sudo_run /opt/CrowdStrike/falconctl -s --aph="${proxy_host}" --app="${proxy_port}"
    sudo_run /opt/CrowdStrike/falconctl -s --apd=FALSE
  fi

  if [[ "${falcon_installed_before}" -eq 0 ]]; then
    sudo_run /opt/CrowdStrike/falconctl -s --cid="${falcon_ccid}"
  fi

  sudo_run systemctl start falcon-sensor

  if ! ps -e | grep -q "[f]alcon-sensor"; then
    err "falcon-sensor is not running after installation."
    exit 1
  fi

  if [[ "${master_image}" == "1" ]]; then
    sudo_run /opt/CrowdStrike/falconctl -d -f --aid
  fi
}

TARGET_USER="$(resolve_target_user)"
REBOOT_REQUIRED=0

say "Updating apt metadata"
wait_for_apt_locks
sudo_run apt-get update -y

say "Setting locale"
ensure_packages locales
sudo_run locale-gen en_US en_US.UTF-8
sudo_run update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

say "Installing shared desktop and development packages"
ensure_packages \
  curl wget git git-lfs ssh openssh-server \
  build-essential cmake ninja-build pkg-config \
  python3 python3-pip python3-venv python3-dev \
  net-tools htop btop tmux terminator \
  software-properties-common apt-transport-https ca-certificates gnupg lsb-release \
  nano vim tree zip unzip p7zip-full \
  dnsutils iputils-ping traceroute \
  evince xclip gnome-system-monitor \
  ncdu bat fd-find ripgrep fzf jq \
  shellcheck strace ltrace \
  gnome-tweaks gparted meld vlc fonts-firacode \
  pciutils mesa-utils x11-xserver-utils ubuntu-drivers-common

install_duke_crowdstrike

say "Ensuring Firefox is installed"
if ! command -v firefox >/dev/null 2>&1; then
  if command -v snap >/dev/null 2>&1; then
    sudo_run snap install firefox
  else
    ensure_packages firefox
  fi
fi

say "Installing Docker"
docker_packages=(docker.io)
if package_exists docker-compose-v2; then
  docker_packages+=(docker-compose-v2)
elif package_exists docker-compose-plugin; then
  docker_packages+=(docker-compose-plugin)
elif package_exists docker-compose; then
  docker_packages+=(docker-compose)
fi
ensure_packages "${docker_packages[@]}"
sudo_run systemctl enable --now docker

if [[ -n "${TARGET_USER}" ]] && id "${TARGET_USER}" >/dev/null 2>&1; then
  sudo_run usermod -aG docker "${TARGET_USER}" || true
else
  warn "Skipping docker group assignment. Set LAB_DESKTOP_USER=<username> to grant non-root Docker access."
fi

say "Enabling SSH server"
sudo_run systemctl enable --now ssh || warn "SSH service failed to start."

# =============================================================================
# UDEV RULES — Crazyradio PA and Crazyflie 2.x bootloader
# =============================================================================
say "Installing Crazyradio udev rules"
sudo_run tee /etc/udev/rules.d/99-crazyradio.rules >/dev/null <<'UDEVRULES'
# Crazyradio PA
SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="7777", MODE="0664", GROUP="plugdev"
# Crazyflie 2.x (DFU bootloader)
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE="0664", GROUP="plugdev"
UDEVRULES
sudo_run udevadm control --reload-rules
sudo_run udevadm trigger

if [[ -n "${TARGET_USER}" ]] && id "${TARGET_USER}" >/dev/null 2>&1; then
  sudo_run usermod -aG plugdev "${TARGET_USER}" || true
fi

# =============================================================================
# X11 FORWARDING FOR DOCKER GUI APPLICATIONS
# =============================================================================
say "Configuring X11 forwarding for Docker containers"
if [[ -n "${TARGET_USER}" ]]; then
  XPROFILE_PATH="/home/${TARGET_USER}/.xprofile"
  XHOST_LINE='xhost +local:docker >/dev/null 2>&1'
  if [[ ! -f "${XPROFILE_PATH}" ]] || ! grep -qF 'xhost +local:docker' "${XPROFILE_PATH}"; then
    echo "${XHOST_LINE}" | sudo_run tee -a "${XPROFILE_PATH}" >/dev/null
    sudo_run chown "${TARGET_USER}:${TARGET_USER}" "${XPROFILE_PATH}"
  fi
fi

# =============================================================================
# STUDENT DATA WIPE (PLACEHOLDER)
# TODO: Implement overlay-based /home reset or nightly wipe via systemd timer.
#   Options:
#     1. OverlayFS on /home/<labuser> — upper layer on tmpfs, wiped on reboot
#     2. systemd timer + script that resets /home/<labuser> from a skeleton nightly
#     3. PAM pam_mkhomedir with logout cleanup hook
# =============================================================================

say "Configuring git-lfs"
sudo_run git lfs install --system || warn "git-lfs system install failed; continuing."

configure_vscode_repo
say "Installing Visual Studio Code"
wait_for_apt_locks
sudo_run apt-get update -y
sudo_run apt-get install -y code

say "Checking for NVIDIA GPU"
if has_nvidia_gpu; then
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    warn "NVIDIA GPU detected, but the host driver is not ready. Installing recommended Ubuntu drivers."
    if sudo_run ubuntu-drivers autoinstall; then
      REBOOT_REQUIRED=1
    else
      warn "ubuntu-drivers autoinstall failed. Install the host NVIDIA driver manually before validating GPU containers."
    fi
  fi

  install_nvidia_container_toolkit

  if command -v nvidia-smi >/dev/null 2>&1; then
    if ! sudo_run docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi; then
      warn "Docker could not access the GPU yet. If the driver was just installed, reboot and re-run the script."
    fi
  else
    warn "NVIDIA driver install may require a reboot before GPU containers can be validated."
  fi
else
  say "No NVIDIA GPU detected; skipping NVIDIA container runtime setup"
fi

say "Performing apt cleanup"
wait_for_apt_locks
sudo_run apt-get autoremove -y
sudo_run apt-get clean

say "Setup complete!"
echo
echo "Notes:"
echo "  - Docker: log out/in (or reboot) so docker-group membership applies."
echo "  - SSH: server is enabled and running (port 22)."
echo "  - Crazyradio: udev rules installed; user added to plugdev group."
echo "  - Docker GUI: xhost +local:docker will run on login via .xprofile."
echo "  - Config: place ubuntu_desktop_setup.env next to this script to avoid retyping setup values."
echo "  - Duke CrowdStrike: DUKE_FALCON_DEB and DUKE_FALCON_CCID are required unless SKIP_DUKE_CROWDSTRIKE=1 is set."
echo "  - VS Code extensions, pipx tools, nvm, and shell customizations were intentionally left out."
echo "  - If you need per-user developer tooling, use vm_setup_dev.sh only on single-user machines."
if [[ "${REBOOT_REQUIRED}" -eq 1 ]]; then
  echo "  - Reboot required: an NVIDIA driver was installed and needs a reboot before GPU validation will pass."
fi
