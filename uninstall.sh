#!/bin/bash

# Uninstallation script for VSCode LINGMA Auto Continue Button Clicker

echo "Starting uninstallation of VSCode LINGMA Auto Continue Button Clicker..."

# Stop and disable system-wide service if it exists
if systemctl list-unit-files | grep -q vscode-auto-continue.service; then
    echo "Stopping and disabling system-wide service..."
    sudo systemctl stop vscode-auto-continue.service 2>/dev/null || true
    sudo systemctl disable vscode-auto-continue.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/vscode-auto-continue.service
    sudo systemctl daemon-reload
fi

# Stop and disable user service if it exists
if systemctl --user list-unit-files | grep -q vscode-auto-continue.service; then
    echo "Stopping and disabling user service..."
    systemctl --user stop vscode-auto-continue.service 2>/dev/null || true
    systemctl --user disable vscode-auto-continue.service 2>/dev/null || true
    systemctl --user daemon-reload
fi

# Remove virtual environment
if [ -d "lingma_venv" ]; then
    echo "Removing virtual environment..."
    rm -rf lingma_venv
fi

# Remove log files
echo "Removing log files..."
rm -f /tmp/vscode_auto_continue.log*
rm -f /tmp/debug_screenshot_*.png

echo "Uninstallation completed!"