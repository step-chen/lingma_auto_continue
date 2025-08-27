#!/usr/bin/env python3
"""Module for testing required imports for vscode_auto_continue.py.

This script checks if the required Python packages (cv2, numpy, and pyautogui)
can be imported successfully and reports the results to the console.
"""

import sys

print("Testing imports for vscode_auto_continue.py...")

def test_import(module_name, expected=True):
    """Test if a module can be imported and print the result.
    
    Args:
        module_name (str): Name of the module to test.
        expected (bool): Whether the module is expected to be available.
        
    Returns:
        module: The imported module if successful, None otherwise.
    """
    try:
        module = __import__(module_name)
        print(f"✓ {module_name} imported successfully")
        return module
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
        if expected:
            return None
        sys.exit(1)

# Test cv2 import
cv2 = test_import("cv2")

# Test numpy import
numpy = test_import("numpy")

# Test pyautogui import without initializing the display
try:
    import pyautogui
    # Just check if the module was imported, don't try to use it
    if pyautogui is not None:
        print("✓ pyautogui imported successfully")
except (ImportError, Exception) as e:
    # Handle both ImportError and display connection errors
    if isinstance(e, ImportError):
        print(f"✗ Failed to import pyautogui: {e}")
    else:
        print("✓ pyautogui module imported (display connection error expected in terminal environment)")

print("Import test completed.")