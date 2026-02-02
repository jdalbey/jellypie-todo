#!/usr/bin/env bash

# Installer
# Copyright (c) 2025 Zulfian <zulfian1732@gmail.com>
# license : GPL v3
# Design Rationale: https://gist.github.com/jdalbey/c064ef454e8e118ed53e83a48a5f562f

set -e

APP_NAME='jellypie'
# Prefer /usr/bin/python3 (the distro Python that has python3-gi installed) over
# whatever python3 appears first in $PATH (like a shim from pyenv). 
# That way both the dependency checks and the venv will use the correct interpreter.
PYTHON=$( ([ -x /usr/bin/python3 ] && echo /usr/bin/python3) || command -v python3 || command -v python)

VENV_PATH="/opt/$APP_NAME-venv"
SYS_PATH="/usr/share"
BIN_PATH="/usr/local/bin/$APP_NAME"

# Warna
YELLOW=$(tput setaf 11 2>/dev/null || echo -e "\e[33m")
GREEN=$(tput setaf 10 2>/dev/null || echo -e "\e[32m")
RED=$(tput setaf 9 2>/dev/null || echo -e "\e[31m")
RESET=$(tput sgr0 2>/dev/null || echo -e "\e[0m")

log()   { echo -e "${YELLOW}[+] $1${RESET}"; }
ok()    { echo -e "${GREEN}OK${RESET}"; }
fail()  { echo -e "${RED}ERROR: $1${RESET}"; exit 1; }

# ===== DETECT DISTRO =====
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|linuxmint|zorin|pop|neon|kubuntu|lubuntu|xubuntu|ubuntu-mate)
                echo "debian" ;;
            fedora|nobara|ultramarine)
                echo "fedora" ;;
            arch|manjaro|endeavouros|garuda|artix|cachyos)
                echo "arch" ;;
            *)
                echo "unsupported" ;;
        esac
    else
        echo "unsupported"
    fi
}

DISTRO=$(detect_distro)
[[ "$DISTRO" == "unsupported" ]] && fail "Unable to detect distro type. Please install dependencies manually."

# ===== CHECK DEPENDENCIES =====
MISSING=()

check_dep() {
    local name="$1"
    local test_cmd="$2"
    local deb_pkg="$3"
    local fed_pkg="$4"
    local arch_pkg="$5"
    local optional="$6"

    echo -n "Checking $name... "
    if eval "$test_cmd" >/dev/null 2>&1; then
        ok
    else
        if [[ "$optional" == "true" ]]; then
            echo -e "${YELLOW}not found (optional)${RESET}"
            echo -e "${YELLOW}→ You can install Evince later if you want PDF preview support.${RESET}"
        else
            echo -e "${RED}not found!${RESET}"
            MISSING+=("$name|$deb_pkg|$fed_pkg|$arch_pkg")
        fi
    fi
    }

check_all_deps() {
    log "Checking dependencies, please wait..."

    # Python version
    check_dep "Python 3.10–3.14" \
        "$PYTHON -c 'import sys; sys.exit(not (3,10) <= sys.version_info[:2] <= (3,14))'" \
            "" "" "" "false"

    # venv
    check_dep "Python venv module" \
        "$PYTHON -c 'import venv, ensurepip' 2>/dev/null" \
        "python3-venv" "python3-virtualenv" "python-virtualenv" "false"

    # PyGObject
    check_dep "PyGObject (gi)" \
        "$PYTHON -c 'import gi' 2>/dev/null" \
        "python3-gi python3-gi-cairo" "python3-gobject" "python-gobject" "false"

    # GTK4
    check_dep "GTK 4 (>=4.10)" \
        "$PYTHON -c 'import gi; gi.require_version(\"Gtk\", \"4.0\"); from gi.repository import Gtk; v=(Gtk.get_major_version(), Gtk.get_minor_version()); exit(0 if v>=(4,10) else 1)' 2>/dev/null" \
        "gir1.2-gtk-4.0 libgtk-4-1" "gtk4" "gtk4" "false"

    # GtkSourceView5
    check_dep "GtkSourceView 5" \
        "$PYTHON -c 'import gi; gi.require_version(\"GtkSource\", \"5\"); from gi.repository import GtkSource' 2>/dev/null" \
        "gir1.2-gtksource-5 libgtksourceview-5-0" "gtksourceview5" "gtksourceview5" "false"

    # Evince optional
    check_dep "Evince (PDF viewer)" \
        "command -v evince" \
        "evince" "evince" "evince" "true"

    if [[ ${#MISSING[@]} -ne 0 ]]; then
        echo
        log "Some dependencies are missing. Will be installed automatically..."
        install_missing
    fi
}

# ===== INSTALL any missing dependencies =====
install_missing() {
    case "$DISTRO" in
        debian)
            pkgs=()
            for item in "${MISSING[@]}"; do
                pkgs+=($(echo "$item" | cut -d'|' -f2))
            done
            log "Installing missing packages via apt: ${pkgs[*]}"
            sudo apt update
            sudo apt install -y "${pkgs[@]}"
            ;;
        fedora)
            pkgs=()
            for item in "${MISSING[@]}"; do
                pkgs+=($(echo "$item" | cut -d'|' -f3))
            done
            log "Installing missing packages via dnf: ${pkgs[*]}"
            sudo dnf install -y "${pkgs[@]}"
            ;;
        arch)
            pkgs=()
            for item in "${MISSING[@]}"; do
                pkgs+=($(echo "$item" | cut -d'|' -f4))
            done
            log "Installing missing packages via pacman: ${pkgs[*]}"
            sudo pacman -Sy --noconfirm "${pkgs[@]}"
            ;;
    esac
}

# ===== INSTALL APPLICATION =====
install_app() {
    log "Installing $APP_NAME via pip..."

    sudo rm -rf "$VENV_PATH" "$BIN_PATH"
    sudo $PYTHON -m venv --system-site-packages "$VENV_PATH"

    # Fix for Debian/Ubuntu: Ensure venv can access dist-packages
    PYTHON_VERSION=$("$VENV_PATH/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    SITE_PACKAGES="$VENV_PATH/lib/python${PYTHON_VERSION}/site-packages"
    echo "/usr/lib/python3/dist-packages" | sudo tee "$SITE_PACKAGES/dist-packages.pth" >/dev/null

    sudo "$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel || true

    # Remove any pip-installed PyGObject packages that conflict with system gi
    # sudo "$VENV_PATH/bin/pip" uninstall -y PyGObject pygobject pgi 2>/dev/null || true
    sudo "$VENV_PATH/bin/pip" uninstall -y --no-input pgi 2>/dev/null || true

    # Verify gi module is accessible before proceeding
    if ! "$VENV_PATH/bin/python" -c "import gi" 2>/dev/null; then
        fail "Cannot import gi module in venv. System PyGObject may be broken."
    fi

    sudo "$VENV_PATH/bin/pip" install --no-deps . >/dev/null

    sudo ln -sf "$VENV_PATH/bin/jellypie" "$BIN_PATH"

    sudo mkdir -p "$SYS_PATH/applications" "$SYS_PATH/icons/hicolor" "$SYS_PATH/gtksourceview-5/styles"
    sudo cp data/com.github.jdalbey.jellypie.desktop "$SYS_PATH/applications/"
    sudo cp -r data/icons/hicolor/* "$SYS_PATH/icons/hicolor/"
    sudo cp src/jellypie/style/jellypie.xml "$SYS_PATH/gtksourceview-5/styles/"

    sudo chmod 644 "$SYS_PATH/applications/com.github.jdalbey.jellypie.desktop"
    sudo update-desktop-database "$SYS_PATH/applications"
    sudo gtk-update-icon-cache $SYS_PATH/icons/hicolor/ -f

    log "$APP_NAME successfully installed!"
    echo "Run: $APP_NAME"
    echo "Update anytime: git pull && ./install.sh -i"
}

uninstall() {
    log "Removing $APP_NAME..."
    sudo rm -rf "$VENV_PATH" "$BIN_PATH"
    sudo rm -f "$SYS_PATH/applications/com.github.jdalbey.jellypie.desktop"
    sudo rm -f $SYS_PATH/icons/hicolor/*/apps/com.github.jdalbey.jellypie.png
    sudo rm -f "$SYS_PATH/gtksourceview-5/styles/jellypie.xml"
    log "$APP_NAME successfully uninstalled!"
    }

# ===== MAIN =====
case "${1:-}" in
    -i|--install)
        check_all_deps
        install_app
        ;;
    -u|--uninstall)
        if command -v "$APP_NAME" >/dev/null 2>&1; then
            read -p "${YELLOW}Do you want to uninstall $APP_NAME? [y/N]: ${RESET}" answer
            [[ "$answer" =~ ^[Yy]$ ]] && uninstall
        else
            echo "${GREEN}$APP_NAME is not installed.${RESET}"
        fi
        ;;
    *)
        echo "${YELLOW}Usage: $0 [-i | -u]${RESET}"
        echo "   -i : install"
        echo "   -u : uninstall"
        exit 1
        ;;
esac
