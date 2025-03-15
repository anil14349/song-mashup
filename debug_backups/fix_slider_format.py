#!/usr/bin/env python3

"""
Fix slider formatting issues in app_enhanced.py by directly replacing problematic patterns.
"""

import re
import os

def fix_sliders():
    """Fix slider formatting issues in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Pattern 1: "Label",)
    # Matches sliders with a closing parenthesis right after the label
    pattern1 = r'(st\.slider\(\s*"[^"]*"),\s*\)'
    replacement1 = r'\1'
    
    content = re.sub(pattern1, replacement1, content)
    count1 = len(re.findall(pattern1, content))
    print(f"Fixed {count1} sliders with premature closing parenthesis")
    
    # Pattern 2: Multiple key parameters (e.g., key="...", key="...")
    pattern2 = r'(key=f"[^"]*"),\s*(key="[^"]*")'
    replacement2 = r'\1'
    
    content = re.sub(pattern2, replacement2, content)
    count2 = len(re.findall(pattern2, content))
    print(f"Fixed {count2} sliders with duplicate key parameters")
    
    # Pattern 3: Fix specific blend_ratio slider issue
    blend_ratio_pattern = r'(st\.session_state\["blend_ratios"\]\[uploaded_file\.name\] = st\.slider\(\s*"Blend Ratio",\s*\))\s*\n(\s+min_value=.*?\n\s+max_value=.*?\n\s+value=.*?\n\s+step=.*?)(,\s*key=.*?key=.*?\))'
    
    def fix_blend_ratio(match):
        return match.group(1).replace(',)', '') + ',\n' + match.group(2) + ',\n        key="blend_ratio_slider")'
    
    content = re.sub(blend_ratio_pattern, fix_blend_ratio, content, flags=re.DOTALL)
    count3 = len(re.findall(blend_ratio_pattern, content))
    print(f"Fixed {count3} blend ratio sliders")
    
    # Check for common fixes and apply them
    fixes = [
        # Fix for line 464-469 (blend ratio slider)
        {
            'pattern': r'st\.session_state\["blend_ratios"\]\[uploaded_file\.name\] = st\.slider\(\s*"Blend Ratio",\s*\)\s*\n\s+min_value=0\.1,\s*\n\s+max_value=2\.0,\s*\n\s+value=st\.session_state\["blend_ratios"\]\[uploaded_file\.name\],\s*\n\s+step=0\.1,\s*\n\s+key=f"slider_\{uploaded_file\.name\}",\s*key="blend_ratio_slider"\)',
            'replacement': 'st.session_state["blend_ratios"][uploaded_file.name] = st.slider(\n                    "Blend Ratio",\n                    min_value=0.1,\n                    max_value=2.0,\n                    value=st.session_state["blend_ratios"][uploaded_file.name],\n                    step=0.1,\n                    key="blend_ratio_slider")'
        },
        # Fix for line 620-625 (dynamic fade slider)
        {
            'pattern': r'st\.session_state\["global_blend_settings"\]\["dynamic_fade"\] = st\.slider\(\s*"Dynamic Fade Intensity",\s*\)\s*\n\s+min_value=0\.0,\s*\n\s+max_value=1\.0,\s*\n\s+value=st\.session_state\["global_blend_settings"\]\["dynamic_fade"\],\s*\n\s+step=0\.1,\s*\n\s+help="Intensity of volume dynamics between sections",\s*key="dynamic_fade_intensity_slider"\)',
            'replacement': 'st.session_state["global_blend_settings"]["dynamic_fade"] = st.slider(\n        "Dynamic Fade Intensity",\n        min_value=0.0,\n        max_value=1.0,\n        value=st.session_state["global_blend_settings"]["dynamic_fade"],\n        step=0.1,\n        help="Intensity of volume dynamics between sections",\n        key="dynamic_fade_intensity_slider")'
        },
        # Fix for line 650-654 (vocal prominence slider)
        {
            'pattern': r'st\.session_state\["advanced_mix_params"\]\["vocal_prominence"\] = st\.slider\(\s*"Vocal Prominence",\s*0\.0,\s*2\.0,\s*\)\s*\n\s+value=st\.session_state\["advanced_mix_params"\]\["vocal_prominence"\],\s*\n\s+step=0\.1,\s*\n\s+help="Controls how prominent vocals are in the final mix",\s*key="vocal_prominence_slider"\)',
            'replacement': 'st.session_state["advanced_mix_params"]["vocal_prominence"] = st.slider(\n                "Vocal Prominence",\n                min_value=0.0,\n                max_value=2.0,\n                value=st.session_state["advanced_mix_params"]["vocal_prominence"],\n                step=0.1,\n                help="Controls how prominent vocals are in the final mix",\n                key="vocal_prominence_slider")'
        }
    ]
    
    # Apply specific fixes
    for i, fix in enumerate(fixes):
        old_content = content
        content = re.sub(fix['pattern'], fix['replacement'], content, flags=re.DOTALL)
        if content != old_content:
            print(f"Applied fix #{i+1}")
    
    # General pattern to fix slider indentation issues
    slider_pattern = r'(st\.[a-z_]+\[[^\]]+\]\[[^\]]+\] = st\.slider\(\s*"[^"]*")(?:,\s*\))?\s*\n(\s+)([a-z_]+=.*?)(?:,\s*key="[^"]*")?\s*\)'
    
    def fix_slider_format(match):
        var_and_label = match.group(1)  # The slider assignment and label
        indent = match.group(2)         # The indentation
        params = match.group(3)         # The parameters
        
        # Get parameter lines
        param_lines = params.split('\n')
        formatted_params = []
        
        for line in param_lines:
            line = line.strip()
            if line:
                formatted_params.append(f"{indent}{line}")
        
        # Extract key from the label to make a unique key
        label_match = re.search(r'"([^"]*)"', var_and_label)
        key_value = label_match.group(1).lower().replace(" ", "_").replace("(", "").replace(")", "") if label_match else "auto_fixed_slider"
        
        # Rebuild the slider
        return f'{var_and_label},\n{",\\n".join(formatted_params)},\n{indent}key="{key_value}_slider")'
    
    # Apply general slider fix
    old_content = content
    content = re.sub(slider_pattern, fix_slider_format, content, flags=re.DOTALL)
    if content != old_content:
        print("Applied general slider format fix")
    
    # Save the modified file
    with open(app_path, 'w') as f:
        f.write(content)
    
    print("\n✓ Fixed slider formatting issues")
    
    return True

if __name__ == "__main__":
    print("Fixing slider formatting issues...\n")
    fix_sliders() 