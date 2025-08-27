#!/usr/bin/env python3
"""
Logging configuration module

Author: Stephen Chen
Company: Navinfo
"""

import logging
import logging.handlers
import os
from utils.common_utils import ensure_directory_exists


def setup_logging(config):
    """Setup logging configuration with rotation"""
    # Get log level from config
    log_level_str = config.get('log_level', 'INFO') if config else 'INFO'
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Get log file path from config
    log_file = config.get('log_file', '/tmp/vscode_auto_continue.log') if config else '/tmp/vscode_auto_continue.log'
    
    # Get log rotation settings from config
    max_bytes = config.get('max_log_size', 10485760) if config else 10485760  # Default 10MB
    backup_count = config.get('backup_count', 5) if config else 5
    
    # Create directory for log file if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        try:
            ensure_directory_exists(log_dir)
        except Exception as e:
            # If we can't create the log directory, fall back to /tmp
            log_file = '/tmp/vscode_auto_continue.log'
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not create log directory {log_dir}: {e}. Falling back to /tmp")
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)