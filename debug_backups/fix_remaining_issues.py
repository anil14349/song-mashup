#!/usr/bin/env python3

"""
Fix remaining indentation issues in app_enhanced.py after the slider fixes.
This script addresses specific problematic sections with indentation errors.
"""

import os
import re

def fix_remaining_issues():
    """Fix specific remaining indentation issues in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # Store original content for comparison
    original_lines = lines.copy()
    
    # Dictionary of specific fixes for problematic sections
    # Format: {line_number: (current_pattern, replacement_pattern)}
    specific_fixes = {
        # Fix the vocal prominence slider section (lines 658-661)
        658: (
            r'(\s+key="vocal_prominence_slider"\s*\n\s+),(\s*help=.*?\n\s+\))',
            r'\1)\n'
        ),
        
        # Fix the blend preview section (line 701)
        701: (
            r'(\s{4}st\.info\("This visualization shows.*?\"\))',
            r'    st.info("This visualization shows how the tracks will be blended in the final mashup.")'
        ),
        
        # Fix the update session state section (lines 1457-1477)
        1457: (
            r'(\s{40})(\s*# Update the session state.*?\n)(\s{44})(.*?\n)(\s{44})(.*?\n)(\s{48})(.*?\n)',
            r'            # Update the session state to use the processed file\n            if result_path and os.path.exists(result_path):\n                # Store both the original and processed paths\n                if "original_mashup_path" not in st.session_state:\n'
        ),
        
        1473: (
            r'(\s{40})(\s*else:\n)(\s{44})(.*?\n)(\s{40})(\s*except.*?\n)(\s{44})(.*?\n)(\s{44})(.*?\n)',
            r'            else:\n                st.error("Failed to process audio with mix settings")\n        except Exception as e:\n            st.error(f"Error applying mix settings: {str(e)}")\n            logger.error(f"Mix processing error: {str(e)}", exc_info=True)\n'
        )
    }
    
    fixed_count = 0
    
    # Apply the specific fixes
    for line_num, (pattern, replacement) in specific_fixes.items():
        # Get a block of lines around the problematic line
        start_idx = max(0, line_num - 5)
        end_idx = min(len(lines), line_num + 10)
        block = ''.join(lines[start_idx:end_idx])
        
        # Apply the fix to the block
        fixed_block = re.sub(pattern, replacement, block, flags=re.DOTALL)
        
        # If the block was changed, update the lines
        if fixed_block != block:
            # Split the fixed block back into lines
            fixed_lines = fixed_block.splitlines(True)
            
            # Replace the original lines with the fixed lines
            lines[start_idx:end_idx] = fixed_lines
            fixed_count += 1
            print(f"Fixed issue around line {line_num}")
    
    # Check if the content was modified
    if fixed_count > 0:
        # Write the modified content back to the file
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"\n✓ Successfully fixed {fixed_count} issues in {app_path}")
    else:
        print("\n× No issues found to fix")
    
    return fixed_count > 0

# Special fix for known issues in the file
def fix_known_issues():
    """Fix specific known issues with direct replacements."""
    
    app_path = "app_enhanced.py"
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Fix 1: The vocal prominence slider section
    content = content.replace(
        'st.session_state["advanced_mix_params"]["vocal_prominence"] = st.slider(\n            "Vocal Prominence",\n            min_value=0.0,\n            max_value=2.0,\n            value=st.session_state["advanced_mix_params"]["vocal_prominence"],\n            step=0.1,\n            help="Controls how prominent vocals are in the final mix",\n            key="vocal_prominence_slider"\n        ),\n                help="Preset EQ profiles for different sound characteristics"\n            )',
        'st.session_state["advanced_mix_params"]["vocal_prominence"] = st.slider(\n            "Vocal Prominence",\n            min_value=0.0,\n            max_value=2.0,\n            value=st.session_state["advanced_mix_params"]["vocal_prominence"],\n            step=0.1,\n            help="Controls how prominent vocals are in the final mix",\n            key="vocal_prominence_slider"\n        )'
    )
    
    # Fix 2: The key alignment slider section
    content = content.replace(
        'st.session_state["advanced_mix_params"]["key_alignment"] = st.slider(\n                "Key Alignment Strength", 0.0, 1.0, )',
        'st.session_state["advanced_mix_params"]["key_alignment"] = st.slider(\n                "Key Alignment Strength", 0.0, 1.0, \n                value=st.session_state["advanced_mix_params"]["key_alignment"],\n                key="key_alignment_slider"\n            )'
    )
    
    # Fix 3: Processing section indentation
    content = content.replace(
        '                                        # Update the session state to use the processed file\n                                            if result_path and os.path.exists(result_path):',
        '            # Update the session state to use the processed file\n            if result_path and os.path.exists(result_path):'
    )
    
    content = content.replace(
        '                                                # Store both the original and processed paths\n                                                if "original_mashup_path" not in st.session_state:',
        '                # Store both the original and processed paths\n                if "original_mashup_path" not in st.session_state:'
    )
    
    content = content.replace(
        '                                        else:\n                                            st.error("Failed to process audio with mix settings")\n                                    except Exception as e:',
        '            else:\n                st.error("Failed to process audio with mix settings")\n        except Exception as e:'
    )
    
    content = content.replace(
        '                                        st.error(f"Error applying mix settings: {str(e)}")\n                                        logger.error(f"Mix processing error: {str(e)}", exc_info=True)',
        '            st.error(f"Error applying mix settings: {str(e)}")\n            logger.error(f"Mix processing error: {str(e)}", exc_info=True)'
    )
    
    # Fix 4: Missing definitions for sliders
    slider_with_missing_content = re.search(r'with col1:\n\s+st\.session_state\["mix_params"\]\["master_volume"\] = st\.slider\(\n\s+"Master Volume", \)', content)
    if slider_with_missing_content:
        content = content.replace(
            'st.session_state["mix_params"]["master_volume"] = st.slider(\n                                    "Master Volume", )',
            'st.session_state["mix_params"]["master_volume"] = st.slider(\n                                    "Master Volume",\n                                    min_value=0.0,\n                                    max_value=2.0,\n                                    value=st.session_state["mix_params"]["master_volume"],\n                                    step=0.1,\n                                    key="master_volume_slider"\n                                )'
        )
    
    # Fix other incomplete sliders similarly...
    with open(app_path, 'w') as f:
        f.write(content)
    
    print("Applied direct fixes to known issues")

if __name__ == "__main__":
    print("Fixing remaining issues in app_enhanced.py...\n")
    
    # Try the more precise fixes first
    if not fix_remaining_issues():
        # If that doesn't work, use the direct replacement approach
        fix_known_issues()
    
    print("Done.") 