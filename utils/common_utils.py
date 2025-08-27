#!/usr/bin/env python3
"""
Common utility functions used across the project

Author: Stephen Chen
Company: Navinfo
"""

import os
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


def ensure_directory_exists(
    directory_path: str, 
    fallback_path: Optional[str] = None
) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory to ensure exists
        fallback_path: Fallback path if the primary path cannot be created
        
    Returns:
        The path that was successfully created or already exists, 
        or the fallback path if provided and the primary path failed
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.debug(f"Created directory: {directory_path}")
        return directory_path
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        
        if fallback_path:
            try:
                if not os.path.exists(fallback_path):
                    os.makedirs(fallback_path)
                    logger.debug(
                        f"Created fallback directory: {fallback_path}"
                    )
                return fallback_path
            except Exception as fallback_e:
                logger.error(
                    f"Failed to create fallback directory {fallback_path}: {fallback_e}"
                )
                raise
        raise


def create_temp_file(
    suffix: str = '', 
    prefix: str = 'tmp', 
    delete: bool = True
) -> tempfile.NamedTemporaryFile:
    """
    Create a temporary file with consistent settings.
    
    Args:
        suffix: Suffix for the temporary file
        prefix: Prefix for the temporary file
        delete: Whether to delete the file when closed
        
    Returns:
        A NamedTemporaryFile object
    """
    return tempfile.NamedTemporaryFile(
        suffix=suffix, 
        prefix=prefix, 
        delete=delete
    )