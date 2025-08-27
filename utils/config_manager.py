#!/usr/bin/env python3
"""
Configuration management module

Author: Stephen Chen
Company: Navinfo
"""

import json
import logging
from typing import Optional, Dict, Any

CONFIG_PATH = 'config.json'
logger = logging.getLogger(__name__)

def load_config() -> Optional[Dict[str, Any]]:
    """Load configuration from JSON file."""
    try:
        with open(CONFIG_PATH, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        logger.error(f"Failed to load config file: {e}")
        return None