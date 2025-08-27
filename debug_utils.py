#!/usr/bin/env python3
"""
Debug utilities module

Author: Stephen Chen
Company: Navinfo
"""

import cv2
import time
import logging
import os
import numpy as np
from typing import Tuple
from utils.common_utils import ensure_directory_exists

logger = logging.getLogger(__name__)


def debug_mark_positions(
    frame: np.ndarray, 
    button_line_area: Tuple[int, int, int, int], 
    button_rect: Tuple[int, int, int, int], 
    debug_output_dir: str = "/tmp"
):
    """
    Mark detected positions on screenshot for debugging
    
    Args:
        frame: Screen screenshot
        button_line_area: Button line area coordinates (x, y, width, height)
        button_rect: Button coordinates (x, y, width, height)
        debug_output_dir: Directory to save debug screenshots
    """
    # Ensure debug output directory exists
    try:
        ensure_directory_exists(debug_output_dir, "/tmp")
    except Exception as e:
        logger.error("Failed to create debug output directory: %s", e)
        debug_output_dir = "/tmp"
    
    # Draw rectangle around detection area (line area)
    ax, ay, aw, ah = button_line_area
    cv2.rectangle(frame, (ax, ay), (ax + aw, ay + ah), (255, 0, 0), 2)
    cv2.putText(frame, 'Line Area', (ax, ay-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # Log line area coordinates
    logger.info(f"Line area coordinates: x={ax}, y={ay}, width={aw}, height={ah}")
    
    # Draw rectangle around detected button area
    bx, by, bw, bh = button_rect
    cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
    cv2.putText(frame, 'Detected Button', (bx, by-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Mark actual click point (at 65% height of the button)
    click_y = by + int(bh * 0.65)
    click_x = bx + bw // 2
    cv2.circle(frame, (click_x, click_y), 5, (0, 0, 255), -1)
    cv2.putText(frame, 'Click Point', (click_x+10, click_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    # Draw a line from button center to click point to visualize offset
    center_x = bx + bw // 2
    center_y = by + bh // 2
    cv2.line(frame, (center_x, center_y), (click_x, click_y), (255, 255, 0), 1)
    
    # Save debug image
    timestamp = int(time.time())
    filename = os.path.join(debug_output_dir, f'debug_screenshot_{timestamp}.png')
        
    try:
        cv2.imwrite(filename, frame)
        logger.info("Debug screenshot saved to: %s", filename)
    except Exception as e:
        logger.error("Failed to save debug screenshot to %s: %s", filename, e)
            
        # Try fallback to /tmp
        fallback_filename = f'/tmp/debug_screenshot_{timestamp}.png'
        try:
            cv2.imwrite(fallback_filename, frame)
            logger.info("Debug screenshot saved to fallback location: %s", fallback_filename)
        except Exception as fallback_e:
            logger.error("Failed to save debug screenshot to fallback location: %s", fallback_e)