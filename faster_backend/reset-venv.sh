#!/bin/bash

# Script to reset Python virtual environment and reinstall packages
# Usage:
#   ./reset-venv.sh reset        - Full reset (remove venv, create new, install packages)
#   ./reset-venv.sh reinstall    - Force reinstall packages in existing venv
#   ./reset-venv.sh reset --force    - Full reset without confirmation
#   ./reset-venv.sh reinstall --force - Force reinstall without confirmation

set -e  # Exit on any error

VENV_DIR="../.venv"
REQUIREMENTS_FILE="requirements.txt"
PYTHON_CMD="python3"
FORCE=false

# Parse force flag
if [ "$2" = "--force" ]; then
    FORCE=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm_action() {
    local message="$1"
    if [ "$FORCE" = true ]; then
        return 0
    fi

    echo -e "${YELLOW}[WARNING]${NC} $message"
    echo -e "${YELLOW}This action will affect your virtual environment.${NC}"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

check_requirements() {
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_error "Requirements file not found at $REQUIREMENTS_FILE"
        exit 1
    fi

    if ! command -v $PYTHON_CMD &> /dev/null; then
        log_error "$PYTHON_CMD could not be found. Please install Python 3."
        exit 1
    fi
}

activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        if ! confirm_action "Virtual environment not found at $VENV_DIR. Create it now?"; then
            log_info "Operation cancelled by user"
            exit 0
        fi
        create_venv
    fi

    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    log_success "Virtual environment activated"
}

create_venv() {
    log_info "Creating new virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "Virtual environment created"
}

remove_venv() {
    if [ -d "$VENV_DIR" ]; then
        log_warning "Removing current virtual environment..."
        rm -rf "$VENV_DIR"
        log_success "Virtual environment removed"
    else
        log_info "No virtual environment found"
    fi
}

upgrade_pip() {
    log_info "Upgrading pip..."
    pip install --upgrade pip
    log_success "Pip upgraded"
}

install_packages() {
    log_info "Installing packages from $REQUIREMENTS_FILE..."
    pip install --force-reinstall -r "$REQUIREMENTS_FILE"
    log_success "All packages installed/reinstalled"
}


show_usage() {
    echo "Usage: $0 {reset|reinstall} [--force]"
    echo ""
    echo "Commands:"
    echo "  reset     - Full reset: remove venv, create new, install packages"
    echo "  reinstall - Force reinstall packages in existing venv"
    echo ""
    echo "Options:"
    echo "  --force   - Skip confirmation prompts"
    echo ""
    echo "Examples:"
    echo "  $0 reset"
    echo "  $0 reset --force"
    echo "  $0 reinstall"
    echo "  $0 reinstall --force"
}

# Main script logic
case "${1:-}" in
    "reset")
        log_info "=== Starting Full Virtual Environment Reset ==="
        check_requirements

        # Ask confirmation if venv doesn't exist
        if [ ! -d "$VENV_DIR" ]; then
            if ! confirm_action "Virtual environment not found at $VENV_DIR. Create it now?"; then
                log_info "Operation cancelled by user"
                exit 0
            fi
        fi

        remove_venv
        create_venv
        activate_venv
        upgrade_pip
        install_packages
        log_success "=== Full Reset Complete ==="
        echo ""
        echo "To activate the virtual environment in new sessions:"
        echo "source .venv/bin/activate"
        ;;

    "reinstall")
        log_info "=== Starting Package Force Reinstall ==="
        check_requirements

        # Check if venv exists and ask user what to do
        if [ -d "$VENV_DIR" ]; then
            if ! confirm_action "Virtual environment already exists at $VENV_DIR. Reinstall packages?"; then
                log_info "Operation cancelled by user"
                exit 0
            fi
        fi

        activate_venv
        upgrade_pip
        install_packages
        log_success "=== Force Reinstall Complete ==="
        ;;

    *)
        show_usage
        exit 1
        ;;
esac
