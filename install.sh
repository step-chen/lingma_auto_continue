#!/bin/bash

# Installation script for VSCode LINGMA Auto Continue Button Clicker

set -e

echo "Starting installation of VSCode LINGMA Auto Continue Button Clicker..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root. It will request sudo permissions when needed."
    exit 1
fi

# Get current working directory
WORKING_DIR=$(pwd)
echo "Working directory: $WORKING_DIR"

# Update package list
echo "Updating package list..."
if ! sudo apt update; then
    echo "Warning: Failed to update package list. Continuing with installation..."
fi

# Install Python3 and pip (if not already installed)
echo "Checking and installing Python3 and pip..."
if ! sudo apt install -y python3 python3-pip python3-venv; then
    echo "Error: Failed to install Python3 and pip. Please check your system and try again."
    exit 1
fi

# Create a virtual environment
echo "Creating virtual environment..."
if ! python3 -m venv lingma_venv; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
if ! source lingma_venv/bin/activate; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if ! pip install -r requirements.txt; then
    echo "Error: Failed to install Python dependencies from requirements.txt."
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
if ! sudo apt install -y python3-opencv; then
    echo "Warning: Failed to install python3-opencv. You may need to install it manually."
fi

# Install xdotool for window control
echo "Installing xdotool..."
if ! sudo apt install -y xdotool; then
    echo "Warning: Failed to install xdotool. Some screenshot methods may not work."
fi

# Install ImageMagick for xwd conversion
echo "Installing ImageMagick..."
if ! sudo apt install -y imagemagick; then
    echo "Warning: Failed to install ImageMagick. Some screenshot methods may not work."
fi

echo "Installation completed!"

# Offer to set up systemd service
echo ""
echo "Would you like to set up a systemd service to run this automatically?"
echo "1. System-wide service (requires sudo)"
echo "2. User-level service (no sudo required)"
echo "3. Skip service setup"
read -p "Enter your choice (1/2/3): " service_choice

case $service_choice in
    1)
        echo "Setting up system-wide service..."
        # Create system service file with current paths
        sed -e "s|{{WORKING_DIR}}|$WORKING_DIR|g" \
            -e "s|{{VENV_PYTHON}}|$WORKING_DIR/lingma_venv/bin/python|g" \
            vscode-auto-continue-system.service | sudo tee /etc/systemd/system/vscode-auto-continue.service > /dev/null
        
        sudo systemctl daemon-reload
        sudo systemctl enable vscode-auto-continue.service
        echo "System-wide service installed and enabled."
        echo "To start the service now, run: sudo systemctl start vscode-auto-continue.service"
        echo "To check service status, run: sudo systemctl status vscode-auto-continue.service"
        ;;
    2)
        echo "Setting up user-level service..."
        # Create user service directory if it doesn't exist
        mkdir -p ~/.config/systemd/user
        
        # Create user service file with current paths
        sed -e "s|{{WORKING_DIR}}|$WORKING_DIR|g" \
            -e "s|{{VENV_PYTHON}}|$WORKING_DIR/lingma_venv/bin/python|g" \
            vscode-auto-continue-user-template.service > ~/.config/systemd/user/vscode-auto-continue.service
        
        systemctl --user daemon-reload
        systemctl --user enable vscode-auto-continue.service
        echo "User-level service installed and enabled."
        echo "To start the service now, run: systemctl --user start vscode-auto-continue.service"
        echo "To check service status, run: systemctl --user status vscode-auto-continue.service"
        ;;
    *)
        echo "Skipping service setup."
        ;;
esac

echo ""
echo "Usage instructions:"
echo "1. First, capture the LINGMA Continue button screenshots for both light and dark themes"
echo "2. Save them in the templates directory with appropriate names"
echo "3. Update config.json if needed to match your template paths"
echo "4. Run source lingma_venv/bin/activate # To activate the virtual environment"
echo "5. Run python3 vscode_auto_continue.py"
echo "6. Or set as a scheduled task to run periodically"
echo ""
echo "To run directly without activating the environment:"
echo "./lingma_venv/bin/python vscode_auto_continue.py"
echo ""
echo "To uninstall, run: ./uninstall.sh"