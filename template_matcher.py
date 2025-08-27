#!/usr/bin/env python3
"""
Template matching module

Author: Stephen Chen
Company: Navinfo
"""

import cv2
import os
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class TemplateMatcher:
    def __init__(self, config: dict, threshold: Optional[float] = None):
        self.config = config
        # Use threshold from config if not explicitly provided
        if threshold is None:
            self.threshold = config.get('threshold', 0.8) if config else 0.8
        else:
            self.threshold = threshold
            
        # Template cache to avoid reloading templates
        self.template_cache = {}
        logger.debug(f"TemplateMatcher initialized with threshold: {self.threshold}")
    
    def _load_template(self, template_path: str) -> Optional[np.ndarray]:
        """Load template from cache or file"""
        logger.debug(f"Loading template: {template_path}")
        if template_path in self.template_cache:
            logger.debug(f"Loaded template from cache: {template_path}")
            return self.template_cache[template_path]
        
        if not os.path.exists(template_path):
            logger.debug(f"Template file does not exist: {template_path}")
            return None
            
        template = cv2.imread(template_path)
        if template is None:
            logger.debug(f"Cannot read template file: {template_path}")
            return None
            
        # Cache the template
        self.template_cache[template_path] = template
        logger.debug(f"Cached template: {template_path}")
        return template

    def find_button_line_area(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Find button line area in screen screenshot using line templates
        
        Args:
            frame: Screen screenshot
            
        Returns:
            Button line area coordinates (x, y, width, height) or None if not found
        """
        logger.debug("Starting button line area detection")
        best_match = None
        best_val = -1
        best_pos = None
        best_template_size = None
        
        # Use line templates from config for initial matching
        line_templates = []
        if self.config and 'line_template_paths' in self.config:
            line_templates = self.config['line_template_paths']
            logger.debug(f"Using {len(line_templates)} line templates for matching")
        else:
            logger.error("No line template paths found in config file")
            return None
        
        if not line_templates:
            logger.error("Line template paths list is empty")
            return None
            
        for template_path in line_templates:
            logger.debug(f"Processing template: {template_path}")
            template = self._load_template(template_path)
                
            if template is None:
                logger.debug(f"Skipping template {template_path} because it could not be loaded")
                continue
                
            logger.debug(f"Template shape: {template.shape}")
            # Perform template matching
            try:
                res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                
                logger.debug(f"Template {template_path} matching result: {max_val:.4f} at {max_loc}")
                
                # Check if this is a better match
                if max_val > best_val:
                    best_val = max_val
                    best_match = template_path
                    best_pos = max_loc
                    best_template_size = template.shape[:2]  # (height, width)
                    logger.debug(f"New best match found: {best_val:.4f} with {best_match}")
            except cv2.error as e:
                logger.error(f"OpenCV error during template matching with {template_path}: {e}")
                continue
        
        # Check if best match exceeds threshold
        if best_val >= self.threshold:
            # Calculate area coordinates
            top_left = best_pos
            h, w = best_template_size
            logger.info(
                f"Found LINGMA button line area using template {best_match} "
                f"at position: ({top_left[0]}, {top_left[1]}, {w}, {h}), "
                f"matching degree: {best_val:.2f}"
            )
            return (top_left[0], top_left[1], w, h)
        else:
            logger.debug(
                f"Button line area not found, best matching degree: {best_val:.2f} "
                f"(threshold: {self.threshold})"
            )
            # Add more detailed debug information
            logger.debug(f"Frame shape: {frame.shape}")
            logger.debug(f"Number of templates tried: {len(line_templates)}")
            for template_path in line_templates:
                if os.path.exists(template_path):
                    template = cv2.imread(template_path)
                    if template is not None:
                        logger.debug(f"Template {template_path} shape: {template.shape}")
                    else:
                        logger.debug(f"Could not load template {template_path}")
                else:
                    logger.debug(f"Template file not found: {template_path}")
            return None
    
    def find_continue_button_in_area(self, frame: np.ndarray, area_x: int, area_y: int, 
                                   area_w: int, area_h: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Find continue button within a specified area using button templates
        
        Args:
            frame: Screen screenshot
            area_x: Search area top-left x coordinate
            area_y: Search area top-left y coordinate
            area_w: Search area width
            area_h: Search area height
            
        Returns:
            Button coordinates (x, y, width, height) or None if not found
        """
        logger.debug(f"Starting continue button detection in area: ({area_x}, {area_y}, {area_w}, {area_h})")
        best_val = -1
        best_pos = None
        best_template_size = None
        best_match = None
        
        # Use button templates from config for finding the actual button
        button_templates = []
        if self.config and 'button_template_paths' in self.config:
            button_templates = self.config['button_template_paths']
            logger.debug(f"Using {len(button_templates)} button templates for matching")
        else:
            logger.error("No button template paths found in config file")
            return None
        
        if not button_templates:
            logger.error("Button template paths list is empty")
            return None
            
        # Define search area with some padding to ensure we capture the whole button
        padding = 10  # pixels padding around the search area
        x_start = max(0, area_x - padding)
        y_start = max(0, area_y - padding)
        x_end = min(frame.shape[1], area_x + area_w + padding)
        y_end = min(frame.shape[0], area_y + area_h + padding)
        
        search_area = frame[y_start:y_end, x_start:x_end]
        logger.debug(
            f"Search area shape: {search_area.shape} "
            f"(original area: ({area_x}, {area_y}, {area_w}, {area_h}))"
        )
        
        for template_path in button_templates:
            logger.debug(f"Processing button template: {template_path}")
            template = self._load_template(template_path)
                
            if template is None:
                logger.debug(f"Skipping template {template_path} because it could not be loaded")
                continue
                
            logger.debug(f"Button template shape: {template.shape}")
            # Perform template matching
            try:
                res = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                
                logger.debug(f"Button template {template_path} matching result: {max_val:.4f} at {max_loc}")
                
                # Check if this is a better match
                if max_val > best_val:
                    best_val = max_val
                    best_match = template_path
                    best_pos = max_loc
                    best_template_size = template.shape[:2]  # (height, width)
                    logger.debug(f"New best button match found: {best_val:.4f} with {best_match}")
            except cv2.error as e:
                logger.error(f"OpenCV error during button template matching with {template_path}: {e}")
                continue
        
        # Check if best match exceeds threshold
        if best_val >= self.threshold:
            # Calculate button coordinates relative to the full screen
            top_left = best_pos
            template_h, template_w = best_template_size
            
            # Convert coordinates from search area to full screen coordinates
            abs_x = x_start + top_left[0]
            abs_y = y_start + top_left[1]
            
            logger.info(
                f"Found LINGMA Continue button using template {best_match} "
                f"at position: ({abs_x}, {abs_y}, {template_w}, {template_h}), "
                f"matching degree: {best_val:.2f}"
            )
            return (abs_x, abs_y, template_w, template_h)
        else:
            logger.debug(
                f"Continue button not found, best matching degree: {best_val:.2f} "
                f"(threshold: {self.threshold})"
            )
            # Add more detailed debug information
            logger.debug(f"Search area coordinates: x_start={x_start}, y_start={y_start}, x_end={x_end}, y_end={y_end}")
            logger.debug(f"Number of button templates tried: {len(button_templates)}")
            for template_path in button_templates:
                if os.path.exists(template_path):
                    template = cv2.imread(template_path)
                    if template is not None:
                        logger.debug(f"Button template {template_path} shape: {template.shape}")
                    else:
                        logger.debug(f"Could not load button template {template_path}")
                else:
                    logger.debug(f"Button template file not found: {template_path}")
            return None
    
    def find_continue_button(self, frame: np.ndarray, offset_x: int = 0, offset_y: int = 0) -> Optional[Tuple[int, int, int, int]]:
        """
        Find continue button in a single function call, combining both phases
            
        Args:
            frame: Screen screenshot
            offset_x: Optional x offset of the screenshot relative to the full screen
            offset_y: Optional y offset of the screenshot relative to the full screen

        Returns:
            Button coordinates (x, y, width, height) or None if not found
        """
        logger.debug(f"Starting two-phase continue button detection with offset (x: {offset_x}, y: {offset_y})")
        # Phase 1: Find button line area
        button_line_area = self.find_button_line_area(frame)
        if button_line_area is None:
            logger.debug("Phase 1 (button line area detection) failed, cannot proceed to phase 2")
            return None
            
        logger.debug(f"Phase 1 successful, button line area: {button_line_area}")
        # Phase 2: Find continue button within the button line area
        x, y, w, h = button_line_area
        button_rect = self.find_continue_button_in_area(frame, x, y, w, h)
        if button_rect is None:
            logger.debug("Phase 2 (continue button detection within area) failed")
        else:
            # Adjust the button coordinates by the provided offset
            adjusted_rect = (button_rect[0] + offset_x, button_rect[1] + offset_y, button_rect[2], button_rect[3])
            logger.debug(f"Phase 2 successful, continue button with offset: {adjusted_rect}")
        return button_rect
        
    def clear_cache(self) -> None:
        """Clear the template cache"""
        self.template_cache.clear()
        logger.debug("Template cache cleared")