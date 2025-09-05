#!/bin/bash

# VSCode LINGMA Plugin Auto Continue Button Clicker - Command Line Interface
# This script provides a simplified way to run the auto continue functionality

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
VENV_PATH="$SCRIPT_DIR/lingma_venv"
PYTHON_PATH="$VENV_PATH/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/vscode_auto_continue.py"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment directory $VENV_PATH not found"
    echo "Please run install.sh script to create virtual environment first"
    exit 1
fi

# Check if main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: Main script file $MAIN_SCRIPT not found"
    exit 1
fi

# Try to run xhost command to resolve possible display authorization issues
echo "Trying to run xhost command to resolve display authorization issues..."
xhost +SI:localuser:$(whoami) >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "xhost command executed successfully"
else
    echo "xhost command failed, if you encounter display-related errors, please manually run: xhost +SI:localuser:$(whoami)"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Parse command line arguments
ONCE_FLAG=""
DEBUG_FLAG=""
INTERVAL_VALUE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "VSCode LINGMA Plugin Auto Continue Button Clicker"
            echo ""
            echo "Options:"
            echo "  -h, --help          Show this help message"
            echo "  -o, --once          Execute detection and click only once"
            echo "  -d, --debug         Enable debug mode to save screenshots with marked positions"
            echo "  -i, --interval SEC  Detection interval in seconds, default is 60 seconds"
            echo ""
            echo "Examples:"
            echo "  $0                  # Run continuously with default settings"
            echo "  $0 --once           # Run once and exit"
            echo "  $0 --interval 30    # Run with 30 second interval"
            echo "  $0 --debug --once   # Run once in debug mode"
            exit 0
            ;;
        -o|--once)
            ONCE_FLAG="--once"
            shift
            ;;
        -d|--debug)
            DEBUG_FLAG="--debug"
            shift
            ;;
        -i|--interval)
            if [ -n "$2" ] && [ "$2" != "--"* ]; then
                INTERVAL_VALUE="--interval $2"
                shift 2
            else
                echo "Error: --interval option requires a numeric argument"
                exit 1
            fi
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use $0 --help to see available options"
            exit 1
            ;;
    esac
done

# Run main program
echo "Running main program..."
cd "$SCRIPT_DIR"
$PYTHON_PATH "$MAIN_SCRIPT" $ONCE_FLAG $DEBUG_FLAG $INTERVAL_VALUE