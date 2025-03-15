#!/usr/bin/env python3

"""
Manually fix the specific slider syntax errors in app_enhanced.py.
This script performs targeted fixes for each reported slider error.
"""

import os

def manual_fix():
    """Directly fix the known syntax errors in the file."""
    
    fixes = [
        # Line 513-516: Pitch Shift slider
        {
            'line': 513,
            'old': '                        "Pitch Shift (semitones", key="slider_slider"),',
            'new': '                        "Pitch Shift (semitones)",\n                        key="pitch_shift_slider",'
        },
        # Line 698-701: Crossfade Duration slider
        {
            'line': 698,
            'old': '            "Crossfade Duration (seconds", key="slider_slider"), 1.0, 8.0, ',
            'new': '            "Crossfade Duration (seconds)",\n            1.0, 8.0,\n            key="crossfade_duration_slider",'
        },
        # Line 1603-1606: Vocals Threshold slider
        {
            'line': 1603,
            'old': '                                        "Threshold (dB", key="slider_slider"), ',
            'new': '                                        "Threshold (dB)",\n                                        key="vocals_threshold_slider",'
        },
        # Line 1629-1632: Delay Time slider
        {
            'line': 1629,
            'old': '                                        "Delay Time (s", key="slider_slider"), ',
            'new': '                                        "Delay Time (s)",\n                                        key="vocals_delay_time_slider",'
        },
        # Line 1699-1702: Drums Threshold slider
        {
            'line': 1699,
            'old': '                                    "Threshold (dB", key="slider_slider"), ',
            'new': '                                    "Threshold (dB)",\n                                    key="drums_threshold_slider",'
        },
        # Line 1786-1789: Bass Threshold slider
        {
            'line': 1786,
            'old': '                                    "Threshold (dB", key="slider_slider"), ',
            'new': '                                    "Threshold (dB)",\n                                    key="bass_threshold_slider",'
        }
    ]
    
    app_path = "app_enhanced.py"
    
    # Read the file
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # Apply each fix
    fixed_count = 0
    for fix in fixes:
        line_idx = fix['line'] - 1  # Convert to 0-indexed
        if line_idx < len(lines):
            if fix['old'] in lines[line_idx]:
                lines[line_idx] = lines[line_idx].replace(fix['old'], fix['new'])
                print(f"✓ Fixed line {fix['line']}")
                fixed_count += 1
            else:
                print(f"× Line {fix['line']} doesn't match expected content")
                print(f"  Expected: {fix['old']}")
                print(f"  Found: {lines[line_idx].strip()}")
    
    # Write the fixed file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"\n✓ Successfully fixed {fixed_count} slider syntax errors")
    else:
        print("\n× No fixes were applied")

if __name__ == "__main__":
    print("Manually fixing slider syntax errors...\n")
    manual_fix() 