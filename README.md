# VSCode LINGMA Plugin Auto Continue Button Clicker

This tool automatically detects and clicks the Continue button in the VSCode LINGMA plugin.

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

The installation script will:
- Check and install Python3, pip, and python3-venv if needed
- Create a Python virtual environment named `lingma_venv` in the project directory
- Install all required Python dependencies into this virtual environment

2. Capture the button screenshots and save as template images:
   - Identify the button you want to automatically click
   - Find the button in both light and dark themes (if applicable)
   - Screenshot and save as PNG format files:
     * Button line area (including title and button) in light theme
     * Button line area (including title and button) in dark theme
     * Button only in light theme
     * Button only in dark theme
   - Save these files in the `templates` directory

3. Update the configuration in `config.json` if needed:
   - Modify template paths if they are in different locations
   - Adjust threshold value if needed (0.0-1.0, higher is more strict)
   - Change default interval between detections
   - Configure logging options
   - Set debug mode if needed

## Usage

### Basic Usage

Before running the tool, you need to activate the virtual environment that was created during installation:

```bash
# Activate the virtual environment
source lingma_venv/bin/activate

# Continuous monitoring, detect every 60 seconds (uses default templates from config)
python vscode_auto_continue.py

# Specify detection interval (seconds)
python vscode_auto_continue.py --interval 30

# Execute detection only once
python vscode_auto_continue.py --once

# Enable debug mode to save screenshots with marked positions
python vscode_auto_continue.py --debug

# Deactivate the virtual environment when finished
deactivate
```

Alternatively, you can run the tool directly without activating the virtual environment:

```bash
# Run directly using the Python interpreter from the virtual environment
./lingma_venv/bin/python vscode_auto_continue.py --once
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
- `templates/continue_button_line_light.png` - Button line area with title and button in light theme
- `templates/continue_button_line_dark.png` - Button line area with title and button in dark theme
- `templates/continue_button_light.png` - Button only in light theme
- `templates/continue_button_dark.png` - Button only in dark theme

Note: Although the default template names refer to "continue button", this tool can actually be used to automatically click any button by replacing these template images with screenshots of your target button.

## Notes

1. The template images should match the actual button appearance as accurately as possible
2. If the screen resolution or scaling ratio changes, you may need to recreate the template images
3. The script needs to run in a graphical interface environment
4. Ensure the target window is visible on the screen
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

## Deploy to GitHub

To deploy this project to GitHub:

1. Create a new repository on GitHub (do not initialize with README, .gitignore, or license)
2. Run the deployment script:
   ```bash
   ./deploy_to_github.sh
   ```
3. When prompted, replace YOUR_USERNAME and YOUR_REPOSITORY with your actual GitHub username and repository name
4. If you encounter authentication issues, you may need to:
   - Use GitHub CLI: `gh auth login`
   - Set up SSH keys
   - Use a personal access token

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

## Running on Wayland or with Display Authorization Issues

If you encounter display connection errors such as:
```
Xlib.error.DisplayConnectionError: Can't connect to display ":0": b'Authorization required, but no authorization protocol specified\n'
```

This typically happens when running on Wayland sessions or when there are X11 authorization issues. To resolve this:

### Solution Steps

1. Add X11 authorization for your user:
```bash
xhost +SI:localuser:$(whoami)
```

2. Run the tool with the full command:
```bash
source lingma_venv/bin/activate && export DISPLAY=$(echo $DISPLAY) && python vscode_auto_continue.py --once
```

For continuous monitoring:
```bash
source lingma_venv/bin/activate && export DISPLAY=$(echo $DISPLAY) && python vscode_auto_continue.py
```

### Alternative Solutions

- **Switch to Xorg session**: Log out and select "Ubuntu on Xorg" at the login screen instead of the default "Ubuntu" session.
- **Use xwayland**: If you're on Wayland and xwayland is running, you might need to use a different DISPLAY value:
  ```bash
  export DISPLAY=:1
  ```
  
- **SSH with X11 forwarding**: If connecting via SSH, use the -X flag:
  ```bash
  ssh -X username@hostname
  ```

### Verification

You can verify if the issue is resolved by running a simple test:
```bash
python vscode_auto_continue.py --once
```