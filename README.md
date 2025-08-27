# VSCode LINGMA Plugin Auto Continue Button Clicker

This tool automatically detects and clicks the Continue button in the VSCode LINGMA plugin.

## Author

Stephen Chen

## Company

Navinfo

## Features

- Automatically detect the Continue button in VSCode LINGMA plugin
- Automatically click the detected Continue button
- Support for multiple templates (light/dark themes)
- Configuration file for easy customization
- Configurable detection interval
- Comprehensive logging functionality
- Supports both single execution and continuous monitoring modes
- Debug mode with screenshot capture
- Flexible screenshot capture methods
- Log rotation support

## System Requirements

- Ubuntu 18.04 or higher
- Python 3.6 or higher
- VSCode editor

## Installation Steps

1. Run the installation script:
```bash
./install.sh
```

2. Capture the continue button screenshots and save as template images:
   - Open the LINGMA plugin in VSCode
   - Find the continue button in both light and dark themes
   - Screenshot and save as PNG format files:
     * LINGMA button line area (including title and button) in light theme
     * LINGMA button line area (including title and button) in dark theme
     * Continue button only in light theme
     * Continue button only in dark theme
   - Save these files in the `templates` directory

3. Update the configuration in `config.json` if needed:
   - Modify template paths if they are in different locations
   - Adjust threshold value if needed (0.0-1.0, higher is more strict)
   - Change default interval between detections
   - Configure logging options
   - Set debug mode if needed

## Usage

### Basic Usage

```bash
# Continuous monitoring, detect every 60 seconds (uses default templates from config)
python3 vscode_auto_continue.py

# Specify detection interval (seconds)
python3 vscode_auto_continue.py --interval 30

# Execute detection only once
python3 vscode_auto_continue.py --once

# Enable debug mode to save screenshots with marked positions
python3 vscode_auto_continue.py --debug
```

### Parameter Description

- `--interval`: Detection interval (seconds), default from config
- `--once`: Execute detection and click only once
- `--debug`: Enable debug mode to save screenshots with marked positions

## Configuration

The tool uses a configuration file (`config.json`) with the following options:
- `line_template_paths`: Array of line template file paths (used to find the button line area)
- `button_template_paths`: Array of button template file paths (used to find the actual continue button)
- `threshold`: Matching threshold (0.0-1.0), default 0.9
- `default_interval`: Default detection interval in seconds, default 60
- `debug_mode`: Enable debug mode to save screenshots with marked positions
- `log_level`: Log level (DEBUG/INFO/WARNING/ERROR)
- `log_file`: Log file path
- `debug_output_dir`: Directory for debug output files
- `max_log_size`: Maximum log file size before rotation
- `backup_count`: Number of backup log files to keep
- `screenshot_methods`: Array of screenshot methods to try in order (maim, scrot, or default)

## How It Works

1. The script uses OpenCV's template matching algorithm to find the continue button in screen screenshots
2. Two-phase detection approach:
   - Phase 1: Find the LINGMA button line area using line templates
   - Phase 2: Find the continue button within the detected line area using button templates
3. The best match among all templates is selected
4. If the matching degree exceeds the threshold, it is considered that the button is found
5. Use PyAutoGUI to perform the click operation at 66% height of the button
6. Log operations to `/tmp/vscode_auto_continue.log`
7. Optional debug mode saves screenshots with marked detection areas

## Template Files

The tool looks for these template files by default:
- `templates/continue_button_line_light.png` - LINGMA title and Continue button line in light theme
- `templates/continue_button_line_dark.png` - LINGMA title and Continue button line in dark theme
- `templates/continue_button_light.png` - Continue button only in light theme
- `templates/continue_button_dark.png` - Continue button only in dark theme

## Notes

1. The template images should match the actual button appearance as accurately as possible
2. If the screen resolution or scaling ratio changes, you may need to recreate the template images
3. The script needs to run in a graphical interface environment
4. Ensure the VSCode window is visible on the screen
5. Having multiple templates for different themes increases detection accuracy
6. Configuration file makes it easy to customize behavior without modifying code

## Scheduled Task Setup

You can use cron to set up scheduled tasks:

```bash
# Edit cron tasks
crontab -e

# Add the following line to execute detection every 5 minutes
*/5 * * * * DISPLAY=:0 python3 /home/stephen/workspace/lingmaAutoContinue/vscode_auto_continue.py --once
```

Note: The DISPLAY environment variable needs to be set to access the graphical interface in scheduled tasks.

## View Logs

```bash
# View operation logs
tail -f /tmp/vscode_auto_continue.log
```

## Troubleshooting

### ImportError: Import "pyautogui" could not be resolved

This error occurs when the required dependencies are not installed or not accessible in your current Python environment. The project uses a virtual environment to manage dependencies.

#### Solution 1: Using the project's virtual environment (Recommended)

The project already has a virtual environment with all required dependencies. Activate it before running the script:

```bash
source lingma_venv/bin/activate
python vscode_auto_continue.py
```

To deactivate the virtual environment when you're done:
```bash
deactivate
```

#### Solution 2: Install dependencies in your current environment

If you prefer to run the script without the virtual environment, you can install the dependencies directly:

```bash
pip install -r requirements.txt
```

Note: You might need to install system-level dependencies as well:
```bash
sudo apt install python3-opencv
```

### VSCode Integration

If you're using VSCode and still seeing the import error in the editor, make sure to select the project's virtual environment as your Python interpreter:

1. Press `Ctrl+Shift+P` to open the command palette
2. Type "Python: Select Interpreter" and select it
3. Choose the interpreter from `./lingma_venv/bin/python`
