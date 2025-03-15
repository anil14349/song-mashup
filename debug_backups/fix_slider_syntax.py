#!/usr/bin/env python3

"""
Fix syntax errors in slider widgets in app_enhanced.py.
This script corrects errors where key parameters were incorrectly added inside string labels.
"""

import re
import os
import sys

def fix_slider_syntax_errors():
    """Fix slider syntax errors in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    try:
        with open(app_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File {app_path} not found")
        return False
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return False
    
    # Pattern to find incorrectly formatted sliders where key is inside the label string
    pattern = r'"([^"]*), key="([^"]*)"\)"'
    
    # Replace with correct format
    fixed_content = re.sub(pattern, r'"\1", key="\2")', content)
    
    # Count the number of fixes
    fixes_count = len(re.findall(pattern, content))
    
    if fixes_count > 0:
        print(f"Found {fixes_count} slider syntax errors to fix")
        
        # Save the updated content
        try:
            with open(app_path, 'w') as file:
                file.write(fixed_content)
            print(f"✓ Successfully fixed {fixes_count} slider syntax errors")
            return True
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            return False
    else:
        print("No syntax errors found")
        return True

if __name__ == "__main__":
    print("Fixing slider syntax errors...")
    result = fix_slider_syntax_errors()
    if result:
        print("✓ Script completed successfully")
        sys.exit(0)
    else:
        print("× Failed to fix syntax errors")
        sys.exit(1) 