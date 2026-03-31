#!/usr/bin/env bash
# =============================================================================
# Developer VM Setup — VMware + Ubuntu (All-in-One)
# Duke University, Thomas Lord Department of Mechanical Engineering & Materials Science
# Author: Evan Kusa
#
# A personal/developer-oriented VM setup script. Unlike vm_setup.sh (which
# targets student VMs with FastX remote-desktop access), this script assumes:
#   - VMware Workstation/Fusion (installs open-vm-tools)
#   - Firefox via snap is fine
#   - You want a richer development environment
# =============================================================================

set -euo pipefail

# -----------------------------
# Helpers
# -----------------------------
say()  { printf "\n\033[1;36m===== %s =====\033[0m\n\n" "$*"; }
warn() { printf "\n\033[1;33m[WARN]\033[0m %s\n" "$*" >&2; }
err()  { printf "\n\033[1;31m[ERROR]\033[0m %s\n" "$*" >&2; }
require() { command -v "$1" >/dev/null 2>&1 || { err "Missing required command: $1"; exit 1; }; }
package_exists() { apt-cache show "$1" >/dev/null 2>&1; }

wait_for_apt_locks() {
  local lock_files=(
    /var/lib/dpkg/lock-frontend
    /var/lib/dpkg/lock
    /var/lib/apt/lists/lock
    /var/cache/apt/archives/lock
  )

  while sudo fuser "${lock_files[@]}" >/dev/null 2>&1; do
    say "Waiting for apt/dpkg locks..."
    sleep 5
  done
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

# Make sure sudo is ready
sudo -v

# -----------------------------
# Locale
# -----------------------------
say "Setting locale"
wait_for_apt_locks
sudo apt-get update -y
sudo apt-get install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# -----------------------------
# VMware Guest Tools
# -----------------------------
say "Installing VMware guest tools"
wait_for_apt_locks
sudo apt-get install -y open-vm-tools open-vm-tools-desktop

# -----------------------------
# Base development utilities
# -----------------------------
say "Installing base development utilities"
wait_for_apt_locks
sudo apt-get install -y \
  curl wget git git-lfs ssh \
  build-essential cmake ninja-build pkg-config \
  python3 python3-pip python3-venv python3-dev pipx \
  net-tools htop btop tmux terminator pciutils \
  software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Additional QoL & troubleshooting tools
wait_for_apt_locks
sudo apt-get install -y \
  nano vim tree zip unzip p7zip-full \
  dnsutils iputils-ping traceroute \
  evince xclip gnome-system-monitor \
  ncdu bat fd-find ripgrep fzf jq \
  shellcheck strace ltrace \
  gnome-tweaks gparted meld vlc fonts-firacode

# Symlink bat/fd to expected names (Ubuntu ships them as batcat / fdfind)
if command -v batcat >/dev/null 2>&1 && ! command -v bat >/dev/null 2>&1; then
  mkdir -p "${HOME}/.local/bin"
  ln -sf "$(command -v batcat)" "${HOME}/.local/bin/bat"
fi
if command -v fdfind >/dev/null 2>&1 && ! command -v fd >/dev/null 2>&1; then
  mkdir -p "${HOME}/.local/bin"
  ln -sf "$(command -v fdfind)" "${HOME}/.local/bin/fd"
fi

# Ensure ~/.local/bin is on PATH
if [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
  export PATH="${HOME}/.local/bin:${PATH}"
  echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${HOME}/.bashrc"
fi

# -----------------------------
# Firefox (snap — default on Ubuntu)
# -----------------------------
say "Installing Firefox via snap"
if ! snap list firefox >/dev/null 2>&1; then
  sudo snap install firefox
else
  say "Firefox snap already installed"
fi

# -----------------------------
# Docker
# -----------------------------
say "Installing Docker (docker.io)"
wait_for_apt_locks
docker_packages=(docker.io)
if package_exists docker-compose-v2; then
  docker_packages+=(docker-compose-v2)
elif package_exists docker-compose-plugin; then
  docker_packages+=(docker-compose-plugin)
elif package_exists docker-compose; then
  docker_packages+=(docker-compose)
fi
sudo apt-get install -y "${docker_packages[@]}"
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER" || true

# -----------------------------
# Git configuration helpers
# -----------------------------
say "Setting up git extras"
git lfs install || true

# git-delta (better diffs) — install from GitHub releases
if ! command -v delta >/dev/null 2>&1; then
  say "Installing git-delta"
  DELTA_VERSION="0.18.2"
  DELTA_DEB="/tmp/git-delta_${DELTA_VERSION}_amd64.deb"
  wget -q "https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION}_amd64.deb" \
    -O "${DELTA_DEB}" && \
  sudo dpkg -i "${DELTA_DEB}" && \
  rm -f "${DELTA_DEB}" || warn "Could not install git-delta; skipping."
fi

# lazygit — terminal UI for git
if ! command -v lazygit >/dev/null 2>&1; then
  say "Installing lazygit"
  LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | jq -r '.tag_name' | sed 's/^v//')
  if [ -n "$LAZYGIT_VERSION" ] && [ "$LAZYGIT_VERSION" != "null" ]; then
    curl -Lo /tmp/lazygit.tar.gz \
      "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
    sudo tar xf /tmp/lazygit.tar.gz -C /usr/local/bin lazygit
    rm -f /tmp/lazygit.tar.gz
  else
    warn "Could not determine lazygit version; skipping."
  fi
fi

# -----------------------------
# Python development tools (via pipx)
# -----------------------------
say "Installing Python dev tools via pipx"
pipx ensurepath || true
pipx install black 2>/dev/null || pipx upgrade black || true
pipx install ruff 2>/dev/null || pipx upgrade ruff || true
pipx install httpie 2>/dev/null || pipx upgrade httpie || true

# -----------------------------
# Node.js via nvm
# -----------------------------
say "Installing Node.js via nvm"
export NVM_DIR="${HOME}/.nvm"
if [ ! -d "$NVM_DIR" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  # Source nvm for this session
  # shellcheck source=/dev/null
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install --lts
  nvm use --lts
else
  say "nvm already installed"
  # shellcheck source=/dev/null
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# -----------------------------
# Zsh + Oh My Zsh (optional — does not change default shell)
# -----------------------------
say "Installing zsh + oh-my-zsh"
wait_for_apt_locks
sudo apt-get install -y zsh

if [ ! -d "${HOME}/.oh-my-zsh" ]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended || true
fi

# zsh-autosuggestions & zsh-syntax-highlighting
ZSH_CUSTOM="${HOME}/.oh-my-zsh/custom"
if [ -d "$ZSH_CUSTOM" ]; then
  [ -d "${ZSH_CUSTOM}/plugins/zsh-autosuggestions" ] || \
    git clone https://github.com/zsh-users/zsh-autosuggestions "${ZSH_CUSTOM}/plugins/zsh-autosuggestions" || true
  [ -d "${ZSH_CUSTOM}/plugins/zsh-syntax-highlighting" ] || \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting "${ZSH_CUSTOM}/plugins/zsh-syntax-highlighting" || true
fi

# -----------------------------
# Starship prompt (works in bash and zsh)
# -----------------------------
say "Installing Starship prompt"
if ! command -v starship >/dev/null 2>&1; then
  curl -sS https://starship.rs/install.sh | sh -s -- --yes
fi

# Add to bashrc if not already there
if ! grep -q 'eval "$(starship init bash)"' "${HOME}/.bashrc" 2>/dev/null; then
  echo 'eval "$(starship init bash)"' >> "${HOME}/.bashrc"
fi

# Add to zshrc if it exists and not already there
if [ -f "${HOME}/.zshrc" ] && ! grep -q 'eval "$(starship init zsh)"' "${HOME}/.zshrc" 2>/dev/null; then
  echo 'eval "$(starship init zsh)"' >> "${HOME}/.zshrc"
fi

# -----------------------------
# Visual Studio Code & Extensions
# -----------------------------
say "Installing Visual Studio Code"
wait_for_apt_locks
wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo gpg --dearmor --batch --yes -o /usr/share/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main" \
  | sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null
wait_for_apt_locks
sudo apt-get update -y
sudo apt-get install -y code

say "Installing VS Code extensions"
if command -v code >/dev/null 2>&1; then
  # Core language support
  code --install-extension ms-python.python --force || true
  code --install-extension ms-vscode.cpptools --force || true
  code --install-extension rust-lang.rust-analyzer --force || true

  # Jupyter
  code --install-extension ms-toolsai.jupyter --force || true
  code --install-extension ms-toolsai.jupyter-keymap --force || true
  code --install-extension ms-toolsai.jupyter-renderers --force || true

  # ROS 2 / CMake / XML / YAML
  code --install-extension ms-vscode.cmake-tools --force || true
  code --install-extension DotJoshJohnson.xml --force || true
  code --install-extension redhat.vscode-yaml --force || true

  # Containers / remote dev
  code --install-extension ms-vscode-remote.remote-containers --force || true
  code --install-extension ms-azuretools.vscode-docker --force || true
  code --install-extension ms-vscode-remote.remote-ssh --force || true

  # Git
  code --install-extension eamodio.gitlens --force || true
  code --install-extension mhutchie.git-graph --force || true

  # DX / quality of life
  code --install-extension usernamehw.errorlens --force || true
  code --install-extension streetsidesoftware.code-spell-checker --force || true
  code --install-extension esbenp.prettier-vscode --force || true
  code --install-extension charliermarsh.ruff --force || true
  code --install-extension tamasfe.even-better-toml --force || true
  code --install-extension EditorConfig.EditorConfig --force || true

  # AI assistance
  code --install-extension GitHub.copilot --force || true

  # Tunnels for headless access
  code --install-extension ms-vscode.remote-server --force || true
else
  warn "VS Code CLI 'code' not found; skipping extension installs."
fi

# -----------------------------
# NVIDIA Container Toolkit (optional)
# -----------------------------
say "Installing NVIDIA Container Toolkit (optional)"
if ! command -v docker >/dev/null 2>&1; then
  warn "Docker not found in PATH (unexpected). Skipping NVIDIA toolkit configuration."
elif ! has_nvidia_gpu; then
  say "No NVIDIA GPU detected; skipping NVIDIA container runtime setup"
else
  sudo rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list \
              /etc/apt/keyrings/nvidia-container-toolkit.asc || true

  sudo install -d -m 0755 /etc/apt/keyrings
  sudo wget -qO /etc/apt/keyrings/nvidia-container-toolkit.asc \
    https://nvidia.github.io/libnvidia-container/gpgkey

  echo "deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit.asc] https://nvidia.github.io/libnvidia-container/stable/deb/amd64 /" \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null

  if sudo apt-get update -y && sudo apt-get install -y nvidia-container-toolkit; then
    say "Configuring Docker to use NVIDIA runtime"
    if command -v nvidia-ctk >/dev/null 2>&1; then
      sudo nvidia-ctk runtime configure --runtime=docker || warn "nvidia-ctk configure failed"
      sudo systemctl restart docker
    fi
  else
    warn "NVIDIA toolkit packages could not be installed. Skipping GPU setup."
  fi
fi

# -----------------------------
# Cleanup
# -----------------------------
say "Performing apt cleanup"
wait_for_apt_locks
sudo apt-get autoremove -y
sudo apt-get clean

say "Setup complete!"
echo
echo "Notes:"
echo "  - Docker: log out/in (or reboot) so your 'docker' group membership applies."
echo "  - zsh:    run 'chsh -s \$(which zsh)' if you want zsh as your default shell."
echo "  - nvm:    open a new terminal to use node/npm."
echo "  - delta:  add '[core] pager = delta' to your ~/.gitconfig for better diffs."
