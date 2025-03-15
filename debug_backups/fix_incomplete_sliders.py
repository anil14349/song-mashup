#!/usr/bin/env python3

"""
Fix incomplete slider definitions in app_enhanced.py.
This script specifically targets sliders that are missing parameters or have incomplete definitions.
"""

import os
import re

def fix_incomplete_sliders():
    """Fix incomplete slider definitions in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Dictionary of incomplete slider patterns and their replacements
    incomplete_sliders = {
        # Fix the key alignment slider 
        r'st\.session_state\["advanced_mix_params"\]\["key_alignment"\] = st\.slider\(\s*"Key Alignment Strength", 0\.0, 1\.0,\s*\)': 
            'st.session_state["advanced_mix_params"]["key_alignment"] = st.slider(\n                "Key Alignment Strength", \n                min_value=0.0,\n                max_value=1.0,\n                value=st.session_state["advanced_mix_params"]["key_alignment"],\n                step=0.1,\n                key="key_alignment_slider"\n            )',
            
        # Fix any "with comp_cols[1]" incomplete sliders for vocals
        r'with comp_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["vocals"\]\["compression"\]\["ratio"\] = st\.slider\(\s*"Ratio",\s*\)': 
            'with comp_cols[1]:\n                    st.session_state["stem_effects"]["vocals"]["compression"]["ratio"] = st.slider(\n                        "Ratio",\n                        min_value=1.0,\n                        max_value=20.0,\n                        value=st.session_state["stem_effects"]["vocals"]["compression"]["ratio"],\n                        step=0.5,\n                        key="vocals_comp_ratio_slider"\n                    )',
            
        # Fix any "with delay_cols[1]" incomplete sliders
        r'with delay_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["vocals"\]\["delay"\]\["feedback"\] = st\.slider\(\s*"Feedback",\s*\)': 
            'with delay_cols[1]:\n                    st.session_state["stem_effects"]["vocals"]["delay"]["feedback"] = st.slider(\n                        "Feedback",\n                        min_value=0.0,\n                        max_value=0.9,\n                        value=0.3,\n                        step=0.1,\n                        key="vocals_delay_feedback_slider"\n                    )',
            
        # Fix drums compression ratio slider
        r'with comp_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["drums"\]\["compression"\]\["ratio"\] = st\.slider\(\s*"Ratio",\s*\)': 
            'with comp_cols[1]:\n                st.session_state["stem_effects"]["drums"]["compression"]["ratio"] = st.slider(\n                    "Ratio",\n                    min_value=1.0,\n                    max_value=20.0,\n                    value=st.session_state["stem_effects"]["drums"]["compression"]["ratio"],\n                    step=0.5,\n                    key="drums_comp_ratio_slider"\n                )',
            
        # Fix bass compression ratio slider
        r'with comp_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["bass"\]\["compression"\]\["ratio"\] = st\.slider\(\s*"Ratio",\s*\)': 
            'with comp_cols[1]:\n                st.session_state["stem_effects"]["bass"]["compression"]["ratio"] = st.slider(\n                    "Ratio",\n                    min_value=1.0,\n                    max_value=20.0,\n                    value=st.session_state["stem_effects"]["bass"]["compression"]["ratio"],\n                    step=0.5,\n                    key="bass_comp_ratio_slider"\n                )',
            
        # Fix master volume slider
        r'st\.session_state\["mix_params"\]\["master_volume"\] = st\.slider\(\s*"Master Volume",\s*\)': 
            'st.session_state["mix_params"]["master_volume"] = st.slider(\n                                    "Master Volume",\n                                    min_value=0.0,\n                                    max_value=2.0,\n                                    value=st.session_state["mix_params"]["master_volume"],\n                                    step=0.1,\n                                    key="master_volume_slider"\n                                )'
    }
    
    # Count replacements
    fix_count = 0
    
    # Apply the fixes
    for pattern, replacement in incomplete_sliders.items():
        # Check if pattern exists
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            # Apply replacement
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            fix_count += len(matches)
            print(f"Fixed {len(matches)} instances of incomplete slider pattern")
    
    # Write the fixed content back to the file
    with open(app_path, 'w') as f:
        f.write(content)
    
    if fix_count > 0:
        print(f"\n✓ Successfully fixed {fix_count} incomplete slider definitions")
    else:
        print("\n× No incomplete sliders found to fix")
    
    return fix_count > 0

if __name__ == "__main__":
    print("Fixing incomplete slider definitions in app_enhanced.py...\n")
    fix_incomplete_sliders()
    print("Done.") 