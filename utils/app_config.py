#!/usr/bin/env python3
"""
Application configuration module
Handles both configuration loading and logging setup

Author: Stephen Chen
Company: Navinfo
"""

import json
import logging
import logging.handlers
import os
from typing import Optional, Dict, Any
from utils.common_utils import ensure_directory_exists

CONFIG_PATH = 'config.json'
logger = logging.getLogger(__name__)


def load_config() -> Optional[Dict[str, Any]]:
    """Load configuration from JSON file."""
    config_path = CONFIG_PATH
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to load config file {config_path}: {e}")
        return None


def setup_app_config():
    """
    Setup both configuration and logging in one function.
    
    Returns:
        Configuration dictionary
    """
    config = load_config()
    
    # Setup logging
    # Check if LOG_LEVEL environment variable is set
    log_level_str = os.environ.get('LOG_LEVEL', '').upper()
    if not log_level_str:
        log_level_str = config.get('log_level', 'INFO') if config else 'INFO'
    
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    log_file = config.get('log_file', '/tmp/vscode_auto_continue.log') if config else '/tmp/vscode_auto_continue.log'
    max_bytes = config.get('max_log_size', 10485760) if config else 10485760
    backup_count = config.get('backup_count', 5) if config else 5
    
    log_dir = os.path.dirname(log_file)
    if log_dir:
        try:
            ensure_directory_exists(log_dir)
        except Exception:
            log_file = '/tmp/vscode_auto_continue.log'
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.getLogger(__name__).debug(f"Logging setup complete with level: {log_level_str}")
    logging.getLogger(__name__).debug(f"Using config file: {CONFIG_PATH}")
    
    return config