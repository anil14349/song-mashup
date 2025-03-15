#!/usr/bin/env python3

"""
Script to fix indentation issues in app_enhanced.py
"""

def fix_indentation():
    # Read the entire file
    with open('app_enhanced.py', 'r') as file:
        lines = file.readlines()
    
    # Find the problematic area and fix indentation
    for i in range(len(lines)):
        # Look for the specific pattern
        if "except Exception as e:" in lines[i] and not lines[i].startswith(' ' * 8):
            # This is the line with wrong indentation
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent == 0:  # No indentation
                # Fix this line and all subsequent lines until we hit a line with no indentation
                lines[i] = ' ' * 8 + lines[i].lstrip()
                
                # Fix indentation of the block under the except
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith(' ')):
                    if lines[j].strip():  # If not an empty line
                        # Ensure proper indentation (12 spaces)
                        content = lines[j].lstrip()
                        lines[j] = ' ' * 12 + content
                    j += 1
    
    # Write the fixed content back to the file
    with open('app_enhanced.py', 'w') as file:
        file.writelines(lines)
    
    print("Indentation fixed in app_enhanced.py")

if __name__ == "__main__":
    fix_indentation() 