#!/usr/bin/env python3

"""
Fix slider indentation issues in app_enhanced.py.
This script targets specific formatting patterns that cause syntax errors.
"""

import os
import re

def fix_indentation():
    """Fix the slider indentation issues in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # Process each line to find and fix sliders
    fixed_count = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Find potential slider lines with formatting issues
        if "st.slider(" in line and "))" not in line:
            # Check if the next line has unexpected indentation
            if i + 1 < len(lines) and lines[i+1].strip().startswith("min_value="):
                # This is a slider with formatting issues
                slider_start = i
                
                # Find all related slider parameter lines
                slider_lines = [line.strip()]
                j = i + 1
                while j < len(lines) and (lines[j].strip().startswith(("min_value", "max_value", "value=", "step=", "help=", "key=")) or lines[j].strip() == ")"):
                    slider_lines.append(lines[j].strip())
                    j += 1
                
                slider_end = j - 1
                
                # Get the base indentation
                base_indent = ""
                for char in line:
                    if char.isspace():
                        base_indent += char
                    else:
                        break
                
                # Check if there's a closing parenthesis after the label
                first_line = slider_lines[0]
                if '",)' in first_line or '", )' in first_line:
                    # Remove the premature closing parenthesis
                    first_line = first_line.replace('",)', '"').replace('", )', '"')
                    slider_lines[0] = first_line
                    fixed_count += 1
                
                # Format the slider properly
                formatted_slider = []
                formatted_slider.append(slider_lines[0])  # First line with label
                
                # Process parameter lines
                has_key = False
                for idx, param in enumerate(slider_lines[1:]):
                    if param == ")":
                        continue  # Skip standalone closing parenthesis
                    
                    if "key=" in param:
                        has_key = True
                    
                    # Fix potential duplicate key parameters
                    if "key=" in param and param.count("key=") > 1:
                        # Extract first key
                        key_match = re.search(r'key="([^"]*)"', param)
                        if key_match:
                            key_value = key_match.group(1)
                            # Replace with a single key parameter
                            param = f'key="{key_value}"'
                    
                    formatted_slider.append(f"{base_indent}    {param}")
                
                # Add key parameter if missing
                if not has_key:
                    # Extract label to create a key
                    label_match = re.search(r'"([^"]*)"', slider_lines[0])
                    if label_match:
                        label = label_match.group(1)
                        key_value = label.lower().replace(" ", "_").replace("(", "").replace(")", "")
                        formatted_slider.append(f"{base_indent}    key=\"{key_value}_slider\"")
                
                # Add closing parenthesis if missing
                if not formatted_slider[-1].endswith(")"):
                    formatted_slider[-1] = formatted_slider[-1] + ")"
                
                # Join with commas
                for idx in range(len(formatted_slider) - 1):
                    if not formatted_slider[idx].endswith(","):
                        formatted_slider[idx] = formatted_slider[idx] + ","
                
                # Replace the original lines with the fixed version
                fixed_lines = [line + "\n" for line in formatted_slider]
                lines[slider_start:slider_end+1] = fixed_lines
                
                fixed_count += 1
                print(f"Fixed slider at line {slider_start+1}")
                
                # Adjust the index
                i = slider_start + len(fixed_lines) - 1
        
        i += 1
    
    # Save the modified file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"\n✓ Successfully fixed {fixed_count} sliders with indentation issues")
    else:
        print("\n× No indentation issues found")

if __name__ == "__main__":
    print("Fixing slider indentation issues...\n")
    fix_indentation() 