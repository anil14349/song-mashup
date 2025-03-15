#!/usr/bin/env python3

"""
Fix the duplicate slider widget issue in app_enhanced.py by adding unique keys to all sliders.
This script adds a unique key parameter to every st.slider call in the file.
"""

import re
import os
import sys

def add_unique_keys_to_sliders():
    """Add unique keys to all Streamlit sliders to prevent duplicate widget IDs."""
    
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
    
    # Count the original number of sliders
    slider_pattern = r'st\.slider\('
    original_sliders = len(re.findall(slider_pattern, content))
    print(f"Found {original_sliders} sliders in the file")
    
    # Pattern to find slider definitions without a key parameter
    slider_no_key_pattern = r'(st\.slider\([^)]*?)(?:\s*\))'
    
    # Check for existing key parameters
    key_param_pattern = r'key\s*=\s*["\'][^"\']*["\']'
    sliders_with_keys = len(re.findall(key_param_pattern, content))
    sliders_without_keys = original_sliders - sliders_with_keys
    
    print(f"- {sliders_with_keys} sliders already have keys")
    print(f"- {sliders_without_keys} sliders need keys added")
    
    # Function to add a key to a slider definition
    def add_key(match):
        slider_def = match.group(1)
        
        # Get a hint about what this slider controls from its label (first string argument)
        label_match = re.search(r'["\']([^"\']*)["\']', slider_def)
        key_hint = label_match.group(1).lower().replace(" ", "_").replace("(", "").replace(")", "") if label_match else "slider"
        
        # Get context to make key more unique
        context = ""
        
        # Check for stem context
        stem_context_match = re.search(r'stem_effects["\'][^"\']*["\']([^["\']]*)["\']', slider_def)
        if stem_context_match:
            stem_type = stem_context_match.group(1).strip(']["\'')
            context = f"{stem_type}_"
        
        # Get variable being set (if any)
        var_match = re.search(r'([a-zA-Z0-9_\[\]"\']+)\s*=\s*st\.slider', slider_def.replace("st.session_state", ""))
        if var_match:
            var_parts = re.findall(r'["\']([^"\']+)["\']', var_match.group(1))
            if var_parts:
                context += "_".join(var_parts) + "_"
        
        # Generate a unique key
        unique_key = f"{context}{key_hint}_slider"
        
        # Add the key parameter to the slider definition
        return f'{slider_def}, key="{unique_key}")'
    
    # Replace sliders without keys
    updated_content = re.sub(slider_no_key_pattern, add_key, content)
    
    # Count the number of replacements made
    keys_added = len(re.findall(r'key\s*=\s*["\'][^"\']*["\']', updated_content)) - sliders_with_keys
    
    # Save the updated content
    if keys_added > 0:
        try:
            with open(app_path, 'w') as file:
                file.write(updated_content)
            print(f"✓ Successfully added {keys_added} unique keys to sliders")
            return True
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            return False
    else:
        print("No changes made to the file")
        return False

if __name__ == "__main__":
    print("Adding unique keys to Streamlit sliders...")
    result = add_unique_keys_to_sliders()
    if result:
        print("✓ Fixed duplicate slider widget issue")
        sys.exit(0)
    else:
        print("× Failed to fix slider issue")
        sys.exit(1) 