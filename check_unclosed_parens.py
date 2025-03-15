#!/usr/bin/env python3

"""
Check for unclosed parentheses in app_enhanced.py.
"""

import re
import os
import sys

def check_unclosed_parentheses():
    """Find lines with unclosed parentheses in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    try:
        with open(app_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File {app_path} not found")
        return False
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return False
    
    # Check for sliders that might have unclosed parentheses
    problematic_lines = []
    for i, line in enumerate(lines):
        if "st.slider(" in line:
            # Look ahead up to 10 lines to find closing parenthesis
            found_closing = False
            open_count = line.count('(')
            close_count = line.count(')')
            
            if open_count > close_count:
                # Check next 10 lines for closing parenthesis
                for j in range(i+1, min(i+15, len(lines))):
                    open_count += lines[j].count('(')
                    close_count += lines[j].count(')')
                    
                    # If we've closed all parentheses, check if there's a key
                    if open_count <= close_count:
                        found_closing = True
                        # Check if these lines contain a key parameter
                        slider_code = "".join(lines[i:j+1])
                        if "key=" not in slider_code:
                            problematic_lines.append({
                                'start_line': i+1,  # Convert to 1-indexed
                                'end_line': j+1,
                                'needs_key': True
                            })
                        break
                
                if not found_closing:
                    problematic_lines.append({
                        'start_line': i+1,
                        'end_line': i+1,
                        'needs_key': False,
                        'unclosed_parens': True
                    })
    
    if problematic_lines:
        print(f"Found {len(problematic_lines)} slider definitions with potential issues:")
        for item in problematic_lines:
            print(f"\nSlider starting at line {item['start_line']} ending at line {item['end_line']}:")
            for i in range(item['start_line']-1, item['end_line']):
                print(f"{i+1}: {lines[i].rstrip()}")
            
            if item.get('needs_key', False):
                print("  → Missing key parameter")
            if item.get('unclosed_parens', False):
                print("  → Unclosed parentheses")
    else:
        print("No slider issues found")
    
    return True

if __name__ == "__main__":
    print("Checking for slider issues...\n")
    check_unclosed_parentheses() 