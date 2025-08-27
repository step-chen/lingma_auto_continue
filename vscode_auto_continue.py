#!/usr/bin/env python3
"""
VSCode LINGMA plugin auto continue button clicker
Automatically detects and clicks the Continue button in VSCode LINGMA plugin

Author: Stephen Chen
Company: Navinfo
"""

import pyautogui
import time
import logging
import subprocess
import os
import numpy as np
from typing import Optional, List

# Import our new modules
from utils.app_config import setup_app_config
from screen_capture import ScreenCapture
from template_matcher import TemplateMatcher
from debug_utils import debug_mark_positions

logger = logging.getLogger(__name__)


class VSCodeAutoContinue:
    def __init__(self, template_paths: Optional[List[str]] = None):
        """
        Initialize auto continue button clicker
        
        Args:
            template_paths: List of continue button template image paths
        """
        # Set screenshot parameters
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Load configuration and setup logging
        config = setup_app_config()
        
        # Store config for later use
        self.config = config
        
        # Matching threshold from config
        self.threshold = config.get('threshold', 0.8) if config else 0.8
        
        # Debug mode - save screenshots with marked positions
        self.debug_mode = config.get('debug_mode', False) if config else False
        
        # Initialize components
        self.screen_capture = ScreenCapture(config)
        self.template_matcher = TemplateMatcher(config)
        logger.debug("VSCodeAutoContinue initialized")
    
    def click_continue_button(self, x: int, y: int, w: int, h: int, offset_x: int = 0, offset_y: int = 0, template_path: str = "") -> None:
        """
        Click continue button at calculated position
        
        Args:
            x: Button top-left x coordinate (relative to captured area)
            y: Button top-left y coordinate (relative to captured area)
            w: Button width
            h: Button height
            offset_x: X offset of the captured area on screen
            offset_y: Y offset of the captured area on screen
            template_path: Path to the template that was matched (not used in new implementation)
        """
        try:
            # Adjust coordinates to screen coordinates by adding window offset
            screen_x = offset_x + x + w // 2
            screen_y = offset_y + y + int(h * 0.66)
            
            pyautogui.click(screen_x, screen_y)
            logger.info(f"Clicked continue button at screen position: ({screen_x}, {screen_y}) "
                       f"(relative position: ({x + w // 2}, {y + int(h * 0.66)}) with window offset: ({offset_x}, {offset_y})")
        except Exception as e:
            logger.error(f"Button click failed: {e}")
    
    def is_vscode_running(self) -> bool:
        """
        Check if VSCode is running
        
        Returns:
            True if VSCode is running, False otherwise
        """
        try:
            result = subprocess.run(['pgrep', 'code'], 
                                  capture_output=True, text=True)
            logger.debug(f"VSCode process check - return code: {result.returncode}, stdout: {result.stdout}")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to check VSCode running status: {e}")
            return False
    
    def run_once(self) -> bool:
        """
        Execute one detection and click operation
        
        Returns:
            True if click operation was performed, False otherwise
        """
        logger.debug("Starting run_once execution")
        # Check if VSCode is running
        if not self.is_vscode_running():
            logger.debug("VSCode is not running")
            return False
        
        # Capture screen
        capture_result = self.screen_capture.capture_screen()
        if capture_result is None:
            logger.error("Failed to capture screen")
            return False
        
        frame, offset_x, offset_y = capture_result
        logger.debug(f"Screen captured successfully with shape: {frame.shape}, window offset: ({offset_x}, {offset_y})")
        
        # Use integrated function to find continue button
        logger.debug("Calling template_matcher.find_continue_button")
        button_rect = self.template_matcher.find_continue_button(frame)
        logger.debug(f"Template matching result: {button_rect}")
        
        if button_rect is not None:
            logger.info(f"Continue button found: {button_rect}")
            # For debug mode, we need to simulate the button line area
            # We'll just use the button rect as both for simplicity
            if self.debug_mode:
                debug_frame = frame.copy()
                debug_output_dir = self.config.get('debug_output_dir', '/tmp') if self.config else '/tmp'
                
                # Get the button line area for debugging
                button_line_area = self.template_matcher.find_button_line_area(frame)
                if button_line_area is not None:
                    debug_mark_positions(debug_frame, button_line_area, button_rect, debug_output_dir)
                else:
                    # Fallback if we can't get the line area
                    debug_mark_positions(debug_frame, button_rect, button_rect, debug_output_dir)
            
            # Click continue button with window offset
            self.click_continue_button(*button_rect, offset_x, offset_y)
            return True
        else:
            logger.debug("Continue button not found in this frame")
        
        return False
    
    def run_continuously(self, interval: Optional[int] = None) -> None:
        """
        Run detection program continuously
        
        Args:
            interval: Detection interval (seconds)
        """
        # Use default interval from config if not provided
        if interval is None:
            interval = self.config.get('default_interval', 60) if self.config else 60
            
        logger.info(f"Start continuous monitoring, detection interval: {interval} seconds")
        while True:
            try:
                logger.debug("Starting detection cycle")
                result = self.run_once()
                logger.debug(f"Detection cycle completed, result: {result}")
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, program exiting")
                break
            except Exception as e:
                logger.error(f"Runtime error: {e}")
                time.sleep(interval)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='VSCode LINGMA plugin auto continue button clicker'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        help='Detection interval (seconds), default from config'
    )
    parser.add_argument(
        '--templates', 
        nargs='+',
        help='Continue button template image paths'
    )
    parser.add_argument(
        '--once', 
        action='store_true',
        help='Execute detection and click only once'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode to save screenshots with marked positions'
    )
    
    args = parser.parse_args()
    
    # Create auto continue instance
    auto_continue = VSCodeAutoContinue(template_paths=args.templates)
    
    # Override debug mode if specified in command line
    if args.debug:
        auto_continue.debug_mode = True
    
    if args.once:
        # Execute once
        logger.debug("Running in 'once' mode")
        auto_continue.run_once()
    else:
        # Run continuously
        logger.debug("Running in continuous mode")
        auto_continue.run_continuously(args.interval)


if __name__ == "__main__":
    main()