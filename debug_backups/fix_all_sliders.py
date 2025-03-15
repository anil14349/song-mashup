#!/usr/bin/env python3

"""
Fix all slider compilation errors in app_enhanced.py.
This script handles all types of slider formatting issues.
"""

import os
import re

def fix_all_sliders():
    """Fix all slider compilation errors in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
        
    # Store original content for comparison
    original_content = content
    
    # Fix pattern 1: Duplicate slider definitions
    # This occurs when there's a correctly formatted slider followed by indented parameters
    # Example:
    # st.slider(...)
    #     )
    # min_value=0.0,
    # ...
    
    # We'll use regex to find these patterns and remove the duplicate parameters
    duplicate_slider_pattern = r'(\s*[a-zA-Z_0-9\[\]"\']+\s*=\s*st\.slider\([^)]*\))\s*\n(\s+[a-zA-Z_]+=.*?\n)+\s+\)'
    
    # Count occurrences
    duplicate_count = len(re.findall(duplicate_slider_pattern, content, re.DOTALL))
    if duplicate_count > 0:
        print(f"Found {duplicate_count} duplicate slider parameter blocks")
        
    # Remove the duplicate parameters
    content = re.sub(duplicate_slider_pattern, r'\1', content, flags=re.DOTALL)
    
    # Fix pattern 2: Malformed sliders with ), followed by indented parameters
    # Example:
    # st.slider("Label", ),
    #     min_value=0.0,
    malformed_slider_pattern = r'(st\.slider\(\s*"[^"]*")(,\s*\))\s*\n(\s+[a-zA-Z_]+=.*?\n)+'
    
    def fix_malformed_slider(match):
        # Extract the slider definition and parameters
        slider_def = match.group(1)
        params = match.group(0)[len(slider_def + match.group(2)):]
        
        # Get the indentation level
        indent_match = re.search(r'\n(\s+)', params)
        indent = indent_match.group(1) if indent_match else '    '
        
        # Extract all parameter lines
        param_lines = []
        for line in params.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(')'):
                param_lines.append(f"{indent}{line}")
        
        # Make sure there's a key parameter
        has_key = any("key=" in line for line in param_lines)
        if not has_key:
            # Extract label to create a key
            label_match = re.search(r'"([^"]*)"', slider_def)
            if label_match:
                label = label_match.group(1)
                key_value = label.lower().replace(" ", "_").replace("(", "").replace(")", "")
                param_lines.append(f"{indent}key=\"{key_value}_slider\"")
        
        # Check if the last parameter has a closing parenthesis
        if param_lines and not param_lines[-1].endswith(')'):
            param_lines[-1] = param_lines[-1] + ')'
        
        # Format parameters with commas
        for i in range(len(param_lines) - 1):
            if not param_lines[i].endswith(','):
                param_lines[i] = param_lines[i] + ','
        
        # Rebuild the slider
        return f"{slider_def},\n" + '\n'.join(param_lines)
    
    content = re.sub(malformed_slider_pattern, fix_malformed_slider, content, flags=re.DOTALL)
    malformed_count = len(re.findall(malformed_slider_pattern, original_content, re.DOTALL))
    if malformed_count > 0:
        print(f"Fixed {malformed_count} malformed sliders")
    
    # Fix pattern 3: Clean up remaining duplicate key parameters
    duplicate_key_pattern = r'(key=[^\s,)]*)(,\s*key=[^\s,)]*)'
    content = re.sub(duplicate_key_pattern, r'\1', content)
    duplicate_key_count = len(re.findall(duplicate_key_pattern, original_content))
    if duplicate_key_count > 0:
        print(f"Fixed {duplicate_key_count} duplicate key parameters")
    
    # Fix pattern 4: Remove any hanging lines after closing parenthesis
    # Example: 
    # )
    # step=0.1,
    # help="...",
    hanging_params_pattern = r'(\))\s*\n(\s+[a-zA-Z_]+=.*?\n)+'
    content = re.sub(hanging_params_pattern, r'\1', content, flags=re.DOTALL)
    hanging_count = len(re.findall(hanging_params_pattern, original_content, re.DOTALL))
    if hanging_count > 0:
        print(f"Removed {hanging_count} hanging parameter blocks")
    
    # Fix pattern 5: Clean up specific issues around line 658-661
    # These are extra parameters that appear after a correctly formatted slider
    special_case_pattern = r'(\s+\)\s*\n)(\s+step=.*?\n\s+help=.*?slider"\))'
    content = re.sub(special_case_pattern, r'\1', content, flags=re.DOTALL)
    special_case_count = len(re.findall(special_case_pattern, original_content, re.DOTALL))
    if special_case_count > 0:
        print(f"Fixed {special_case_count} special cases")
    
    # Save the modified file
    with open(app_path, 'w') as f:
        f.write(content)
    
    total_fixed = duplicate_count + malformed_count + duplicate_key_count + hanging_count + special_case_count
    if total_fixed > 0:
        print(f"\n✓ Successfully fixed {total_fixed} slider issues in {app_path}")
    else:
        print("\n× No slider issues found to fix")
    
    return total_fixed > 0

if __name__ == "__main__":
    print("Fixing all slider compilation errors...\n")
    fix_all_sliders() 