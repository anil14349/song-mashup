#!/usr/bin/env python3

"""
Fix specific problematic sliders in app_enhanced.py.
This script directly modifies known problematic sliders by line number.
"""

import os

def fix_specific_sliders():
    """Fix specific problematic sliders in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # List of specific fixes indexed by line number
    specific_fixes = {
        # Line 463-469: Blend Ratio slider (IndentationError)
        463: {
            'lines': 7,
            'replacement': [
                '                st.session_state["blend_ratios"][uploaded_file.name] = st.slider(\n',
                '                    "Blend Ratio",\n',
                '                    min_value=0.1,\n',
                '                    max_value=2.0,\n',
                '                    value=st.session_state["blend_ratios"][uploaded_file.name],\n',
                '                    step=0.1,\n',
                '                    key="blend_ratio_slider"\n',
                '                )\n'
            ]
        },
        # Line 619-625: Dynamic Fade slider
        619: {
            'lines': 7,
            'replacement': [
                '    st.session_state["global_blend_settings"]["dynamic_fade"] = st.slider(\n',
                '        "Dynamic Fade Intensity",\n',
                '        min_value=0.0,\n',
                '        max_value=1.0,\n',
                '        value=st.session_state["global_blend_settings"]["dynamic_fade"],\n',
                '        step=0.1,\n',
                '        help="Intensity of volume dynamics between sections",\n',
                '        key="dynamic_fade_intensity_slider"\n',
                '    )\n'
            ]
        },
        # Line 650-654: Vocal Prominence slider
        650: {
            'lines': 5,
            'replacement': [
                '            st.session_state["advanced_mix_params"]["vocal_prominence"] = st.slider(\n',
                '                "Vocal Prominence",\n',
                '                min_value=0.0,\n',
                '                max_value=2.0,\n',
                '                value=st.session_state["advanced_mix_params"]["vocal_prominence"],\n',
                '                step=0.1,\n',
                '                help="Controls how prominent vocals are in the final mix",\n',
                '                key="vocal_prominence_slider"\n',
                '            )\n'
            ]
        },
        # Add more fixes for other sliders as needed
    }
    
    # Apply each fix
    fixed_count = 0
    for line_num, fix in specific_fixes.items():
        if line_num < len(lines):
            # Replace the lines
            start_line = line_num
            end_line = start_line + fix['lines']
            lines[start_line:end_line] = fix['replacement']
            fixed_count += 1
            print(f"✓ Fixed slider at line {line_num+1}")
    
    # Save the modified file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"\n✓ Successfully fixed {fixed_count} problematic sliders")
    else:
        print("\n× No fixes were applied")
    
    return fixed_count > 0

if __name__ == "__main__":
    print("Fixing specific problematic sliders...\n")
    fix_specific_sliders() 