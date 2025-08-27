#!/usr/bin/env python3
"""
Screen capture module

Author: Stephen Chen
Company: Navinfo
"""

import cv2
import numpy as np
import pyautogui
import subprocess
import os
import tempfile
import logging
from typing import Optional, List, Tuple
from utils.common_utils import create_temp_file

logger = logging.getLogger(__name__)


class ScreenCapture:
    def __init__(self, config):
        self.config = config

    def capture_screen(self) -> Optional[Tuple[np.ndarray, int, int]]:
        """
        Capture screen screenshot without causing screen flickering
        
        Returns:
            Tuple of (screen screenshot as numpy array, window x offset, window y offset)
        """
        logger.debug("Starting screen capture process")
        # Try multiple methods to capture screen to avoid flickering
        # Get preferred methods from config, or use defaults
        preferred_methods = self.config.get('screenshot_methods', []) if self.config else []
        logger.debug(f"Preferred screenshot methods from config: {preferred_methods}")
        
        # Map method names to actual functions
        method_map = {
            'x11_window': self._capture_with_x11_window,
            'gnome_screenshot': self._capture_with_gnome_screenshot,
            'scrot': self._capture_with_scrot,
            'xdotool': self._capture_with_xdotool,
            'pyautogui': self._capture_with_pyautogui
        }
        
        # Build method list in preferred order
        methods = []
        for method_name in preferred_methods:
            if method_name in method_map:
                methods.append(method_map[method_name])
        
        # If no valid methods specified in config, use default order
        if not methods:
            methods = [
                self._capture_with_x11_window,
                self._capture_with_gnome_screenshot,
                self._capture_with_scrot,
                self._capture_with_xdotool,
                self._capture_with_pyautogui
            ]
            logger.debug("Using default screenshot method order")
        else:
            logger.debug("Using configured screenshot method order")
        
        # Log the order of methods that will be tried
        method_names = [method.__name__ for method in methods]
        logger.debug(f"Screenshot methods will be tried in this order: {method_names}")
        
        for method in methods:
            try:
                logger.debug(f"Trying screenshot method: {method.__name__}")
                result = method()
                if result is not None:
                    frame, offset_x, offset_y = result
                    logger.info(
                        f"Screenshot captured successfully using {method.__name__}, "
                        f"shape: {frame.shape}, window offset: ({offset_x}, {offset_y})"
                    )
                    return (frame, offset_x, offset_y)
                else:
                    logger.debug(f"Screenshot method {method.__name__} returned None")
            except Exception as e:
                logger.debug(f"Screenshot method {method.__name__} failed: {e}")
                continue
        
        logger.error("All screenshot methods failed")
        return None
    
    def _capture_with_x11_window(self) -> Optional[Tuple[np.ndarray, int, int]]:
        """Capture VSCode window directly using X11 functions to avoid flickering"""
        logger.debug("Attempting X11 window capture")
        try:
            # Try to find the active VSCode window and capture it directly
            # First get the active window ID
            active_result = subprocess.run(
                ['xdotool', 'getwindowfocus'], 
                capture_output=True, text=True, timeout=5
            )
            
            if active_result.returncode == 0 and active_result.stdout.strip():
                active_window_id = active_result.stdout.strip()
                logger.debug(f"Active window ID: {active_window_id}")
                
                # Check if the active window is a VSCode window
                get_name_result = subprocess.run(
                    ['xdotool', 'getwindowname', active_window_id],
                    capture_output=True, text=True, timeout=5
                )
                
                if (get_name_result.returncode == 0 and 
                    'Visual Studio Code' in get_name_result.stdout.strip()):
                    logger.debug(f"Active window is VSCode: {get_name_result.stdout.strip()}")
                    # Capture this active VSCode window
                    return self._capture_single_window(active_window_id)
                else:
                    logger.debug("Active window is not VSCode, searching for VSCode windows")
                    # If active window is not VSCode, fall back to finding any VSCode window
                    search_result = subprocess.run(
                        ['xdotool', 'search', '--name', 'Visual Studio Code'], 
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if search_result.returncode == 0 and search_result.stdout.strip():
                        logger.debug(f"Found VSCode windows: {search_result.stdout.strip()}")
                        # Get the first VSCode window ID
                        window_id = search_result.stdout.strip().split('\n')[0]
                        logger.debug(f"Using first VSCode window ID: {window_id}")
                        return self._capture_single_window(window_id)
            else:
                # If we can't get active window, fall back to searching for VSCode windows
                logger.debug("Could not get active window, searching for VSCode windows")
                search_result = subprocess.run(
                    ['xdotool', 'search', '--name', 'Visual Studio Code'], 
                    capture_output=True, text=True, timeout=5
                )
                
                if search_result.returncode == 0 and search_result.stdout.strip():
                    logger.debug(f"Found VSCode windows: {search_result.stdout.strip()}")
                    # Get the first VSCode window ID
                    window_id = search_result.stdout.strip().split('\n')[0]
                    logger.debug(f"Using first VSCode window ID: {window_id}")
                    return self._capture_single_window(window_id)
                
            return None
        except subprocess.TimeoutExpired:
            logger.debug("Timeout when trying to capture VSCode window with X11")
            return None
        except Exception as e:
            logger.debug(f"X11 window capture failed: {e}")
            return None
    
    def _capture_single_window(self, window_id: str) -> Optional[Tuple[np.ndarray, int, int]]:
        """Capture a single window by its ID and return window offset"""
        logger.debug(f"Capturing single window with ID: {window_id}")
        
        tmp_xwd = create_temp_file(suffix='.xwd', delete=False)
        xwd_filename = tmp_xwd.name
        tmp_xwd.close()
        
        tmp_png = create_temp_file(suffix='.png', delete=False)
        png_filename = tmp_png.name
        tmp_png.close()
        
        try:
            # Get window position
            geometry_result = subprocess.run(
                ['xdotool', 'getwindowgeometry', '--shell', window_id],
                capture_output=True, text=True, timeout=5
            )
            
            offset_x, offset_y = 0, 0
            if geometry_result.returncode == 0:
                # Parse the output to get window position
                for line in geometry_result.stdout.split('\n'):
                    if line.startswith('X='):
                        offset_x = int(line.split('=')[1])
                    elif line.startswith('Y='):
                        offset_y = int(line.split('=')[1])
                logger.debug(f"Window position: ({offset_x}, {offset_y})")
            
            # Capture window with xwd
            logger.debug(f"Capturing window with xwd to {xwd_filename}")
            xwd_result = subprocess.run(
                ['xwd', '-id', window_id, '-silent', '-out', xwd_filename],
                capture_output=True, timeout=10
            )
            
            if xwd_result.returncode == 0 and os.path.exists(xwd_filename):
                logger.debug("XWD capture successful, converting to PNG")
                # Convert xwd to png using ImageMagick
                convert_result = subprocess.run(
                    ['convert', xwd_filename, png_filename],
                    capture_output=True, timeout=10
                )
                
                if convert_result.returncode == 0 and os.path.exists(png_filename):
                    logger.debug(f"Conversion successful, reading image from {png_filename}")
                    # Read the image
                    frame = cv2.imread(png_filename)
                    # Clean up temporary files
                    os.unlink(xwd_filename)
                    os.unlink(png_filename)
                    logger.debug("Successfully captured VSCode window")
                    return (frame, offset_x, offset_y)
                else:
                    logger.debug(f"Image conversion failed with return code: {convert_result.returncode}")
        
            # Clean up temporary files if they exist
            if os.path.exists(xwd_filename):
                os.unlink(xwd_filename)
            if os.path.exists(png_filename):
                os.unlink(png_filename)
                
        except Exception as e:
            # Clean up temporary files if they exist
            if os.path.exists(xwd_filename):
                os.unlink(xwd_filename)
            if os.path.exists(png_filename):
                os.unlink(png_filename)
            logger.debug(f"Failed to capture window {window_id}: {e}")
            
        return None
    
    def _capture_with_scrot(self) -> Optional[Tuple[np.ndarray, int, int]]:
        """Capture screen using scrot command"""
        logger.debug("Attempting to capture screen with scrot")
        tmp_file = create_temp_file(suffix='.png', delete=False)
        temp_filename = tmp_file.name
        tmp_file.close()
            
        try:
            result = subprocess.run(
                ['scrot', temp_filename], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(temp_filename):
                frame = cv2.imread(temp_filename)
                os.unlink(temp_filename)
                logger.debug("Successfully captured screen with scrot")
                # Full screen capture, no offset
                return (frame, 0, 0)
            else:
                # Clean up temp file if it exists
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                logger.debug(f"Scrot failed with return code: {result.returncode}")
                return None
        except subprocess.TimeoutExpired:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise
    
    def _capture_with_gnome_screenshot(self) -> Optional[Tuple[np.ndarray, int, int]]:
        """Capture screen using gnome-screenshot command"""
        tmp_file = create_temp_file(suffix='.png', delete=False)
        temp_filename = tmp_file.name
        tmp_file.close()
        
        try:
            result = subprocess.run(
                ['gnome-screenshot', '-f', temp_filename], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(temp_filename):
                frame = cv2.imread(temp_filename)
                os.unlink(temp_filename)
                # Full screen capture, no offset
                return (frame, 0, 0)
            else:
                # Clean up temp file if it exists
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                return None
        except subprocess.TimeoutExpired:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise
    
    def _capture_with_xdotool(self) -> Optional[Tuple[np.ndarray, int, int]]:
        """Capture screen using xdotool and gnome-screenshot"""
        tmp_file = create_temp_file(suffix='.png', delete=False)
        temp_filename = tmp_file.name
        tmp_file.close()
            
        try:
            # Get active window information
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowgeometry', '--shell'], 
                capture_output=True, text=True, timeout=5
            )
            
            offset_x, offset_y = 0, 0
            if result.returncode == 0:
                # Parse the output to get window position
                for line in result.stdout.split('\n'):
                    if line.startswith('X='):
                        offset_x = int(line.split('=')[1])
                    elif line.startswith('Y='):
                        offset_y = int(line.split('=')[1])
                logger.debug(f"Window position: ({offset_x}, {offset_y})")
                
                # Capture only the active window
                result = subprocess.run(
                    ['gnome-screenshot', '-w', '-f', temp_filename],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and os.path.exists(temp_filename):
                    frame = cv2.imread(temp_filename)
                    os.unlink(temp_filename)
                    return (frame, offset_x, offset_y)
            
            # Clean up temp file if it exists
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            # Full screen fallback
            return None
        except subprocess.TimeoutExpired:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise
    
    def _capture_with_pyautogui(self) -> Optional[Tuple[np.ndarray, int, int]]:
        """Capture screen using pyautogui (may cause flickering)"""
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Full screen capture, no offset
        return (frame, 0, 0)