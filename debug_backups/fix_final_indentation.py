#!/usr/bin/env python3

"""
Fix the final remaining indentation issues in app_enhanced.py.
This comprehensive script addresses all remaining indentation problems after previous fixes.
"""

import os
import re

def fix_final_indentation():
    """Fix all remaining indentation issues in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file as a single string to handle multiline fixes
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Track the number of fixes
    fix_count = 0
    
    # Fix 1: The vocal prominence slider section (lines 658-661)
    vocal_slider_pattern = r'st\.session_state\["advanced_mix_params"\]\["vocal_prominence"\] = st\.slider\(\s*"Vocal Prominence",\s*min_value=0\.0,\s*max_value=2\.0,\s*value=st\.session_state\["advanced_mix_params"\]\["vocal_prominence"\],\s*step=0\.1,\s*help="Controls how prominent vocals are in the final mix",\s*key="vocal_prominence_slider"\s*\),\s*help="Preset EQ profiles for different sound characteristics"\s*\)'
    vocal_slider_replacement = 'st.session_state["advanced_mix_params"]["vocal_prominence"] = st.slider(\n            "Vocal Prominence",\n            min_value=0.0,\n            max_value=2.0,\n            value=st.session_state["advanced_mix_params"]["vocal_prominence"],\n            step=0.1,\n            help="Controls how prominent vocals are in the final mix",\n            key="vocal_prominence_slider"\n        )'
    
    if re.search(vocal_slider_pattern, content):
        content = re.sub(vocal_slider_pattern, vocal_slider_replacement, content)
        fix_count += 1
        print("Fixed vocal prominence slider issue (lines 658-661)")
    
    # Fix 2: The comp_cols and delay_cols section (lines 1457-1488)
    # This is a very complex section with multiple indentation issues
    # It's easier to do multiple targeted replacements
    
    # Fix for the vocals compression ratio slider
    vocals_comp_pattern = r'with comp_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["vocals"\]\["compression"\]\["ratio"\] = st\.slider\(\s*"Ratio",\s*min_value=1\.0,\s*max_value=20\.0,\s*value=st\.session_state\["stem_effects"\]\["vocals"\]\["compression"\]\["ratio"\],\s*step=0\.5,\s*key="vocals_comp_ratio_slider"\s*\)'
    vocals_comp_replacement = '                                with comp_cols[1]:\n                                    st.session_state["stem_effects"]["vocals"]["compression"]["ratio"] = st.slider(\n                                        "Ratio",\n                                        min_value=1.0,\n                                        max_value=20.0,\n                                        value=st.session_state["stem_effects"]["vocals"]["compression"]["ratio"],\n                                        step=0.5,\n                                        key="vocals_comp_ratio_slider"\n                                    )'
    
    match_count = len(re.findall(vocals_comp_pattern, content))
    if match_count > 0:
        content = re.sub(vocals_comp_pattern, vocals_comp_replacement, content)
        fix_count += match_count
        print(f"Fixed vocals compression slider indentation ({match_count} instances)")
    
    # Fix for the vocals delay feedback slider
    vocals_delay_pattern = r'with delay_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["vocals"\]\["delay"\]\["feedback"\] = st\.slider\(\s*"Feedback",\s*min_value=0\.0,\s*max_value=0\.9,\s*value=0\.3,\s*step=0\.1,\s*key="vocals_delay_feedback_slider"\s*\)'
    vocals_delay_replacement = '                                with delay_cols[1]:\n                                    st.session_state["stem_effects"]["vocals"]["delay"]["feedback"] = st.slider(\n                                        "Feedback",\n                                        min_value=0.0,\n                                        max_value=0.9,\n                                        value=0.3,\n                                        step=0.1,\n                                        key="vocals_delay_feedback_slider"\n                                    )'
    
    match_count = len(re.findall(vocals_delay_pattern, content))
    if match_count > 0:
        content = re.sub(vocals_delay_pattern, vocals_delay_replacement, content)
        fix_count += match_count
        print(f"Fixed vocals delay slider indentation ({match_count} instances)")
    
    # Fix for the drums compression ratio slider
    drums_comp_pattern = r'with comp_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["drums"\]\["compression"\]\["ratio"\] = st\.slider\(\s*"Ratio",\s*min_value=1\.0,\s*max_value=20\.0,\s*value=st\.session_state\["stem_effects"\]\["drums"\]\["compression"\]\["ratio"\],\s*step=0\.5,\s*key="drums_comp_ratio_slider"\s*\)'
    drums_comp_replacement = '                                with comp_cols[1]:\n                                    st.session_state["stem_effects"]["drums"]["compression"]["ratio"] = st.slider(\n                                        "Ratio",\n                                        min_value=1.0,\n                                        max_value=20.0,\n                                        value=st.session_state["stem_effects"]["drums"]["compression"]["ratio"],\n                                        step=0.5,\n                                        key="drums_comp_ratio_slider"\n                                    )'
    
    match_count = len(re.findall(drums_comp_pattern, content))
    if match_count > 0:
        content = re.sub(drums_comp_pattern, drums_comp_replacement, content)
        fix_count += match_count
        print(f"Fixed drums compression slider indentation ({match_count} instances)")
    
    # Fix for the bass compression ratio slider
    bass_comp_pattern = r'with comp_cols\[1\]:\s*\n\s*st\.session_state\["stem_effects"\]\["bass"\]\["compression"\]\["ratio"\] = st\.slider\(\s*"Ratio",\s*min_value=1\.0,\s*max_value=20\.0,\s*value=st\.session_state\["stem_effects"\]\["bass"\]\["compression"\]\["ratio"\],\s*step=0\.5,\s*key="bass_comp_ratio_slider"\s*\)'
    bass_comp_replacement = '                                with comp_cols[1]:\n                                    st.session_state["stem_effects"]["bass"]["compression"]["ratio"] = st.slider(\n                                        "Ratio",\n                                        min_value=1.0,\n                                        max_value=20.0,\n                                        value=st.session_state["stem_effects"]["bass"]["compression"]["ratio"],\n                                        step=0.5,\n                                        key="bass_comp_ratio_slider"\n                                    )'
    
    match_count = len(re.findall(bass_comp_pattern, content))
    if match_count > 0:
        content = re.sub(bass_comp_pattern, bass_comp_replacement, content)
        fix_count += match_count
        print(f"Fixed bass compression slider indentation ({match_count} instances)")
    
    # Fix 3: The update session state section (lines 1503-1511)
    update_session_pattern = r'# Update the session state to use the processed file\s*\n\s*if result_path and os\.path\.exists\(result_path\):\s*\n\s*# Store both the original and processed paths\s*\n\s*if "original_mashup_path" not in st\.session_state:'
    update_session_replacement = '                                            # Update the session state to use the processed file\n                                            if result_path and os.path.exists(result_path):\n                                                # Store both the original and processed paths\n                                                if "original_mashup_path" not in st.session_state:'
    
    if re.search(update_session_pattern, content):
        content = re.sub(update_session_pattern, update_session_replacement, content)
        fix_count += 1
        print("Fixed update session state indentation (lines 1503-1511)")
    
    # Fix for the error handling in the mix settings section
    error_handling_pattern = r'(\s+else:\s*\n\s+st\.error\("Failed to process audio with mix settings"\)\s*\n\s+except Exception as e:\s*\n\s+st\.error\(f"Error applying mix settings: {str\(e\)}"\)\s*\n\s+logger\.error\(f"Mix processing error: {str\(e\)}", exc_info=True\))'
    error_handling_replacement = '                                            else:\n                                                st.error("Failed to process audio with mix settings")\n                                        except Exception as e:\n                                            st.error(f"Error applying mix settings: {str(e)}")\n                                            logger.error(f"Mix processing error: {str(e)}", exc_info=True)'
    
    if re.search(error_handling_pattern, content):
        content = re.sub(error_handling_pattern, error_handling_replacement, content)
        fix_count += 1
        print("Fixed error handling indentation in mix settings section")
    
    # Fix 4: The reset button section (lines 1563-1591)
    reset_button_pattern = r'# Reset button \(only show if we have applied processing\)\s*\n\s*with col3:'
    reset_button_replacement = '                        # Reset button (only show if we have applied processing)\n                        with col3:'
    
    if re.search(reset_button_pattern, content):
        content = re.sub(reset_button_pattern, reset_button_replacement, content)
        fix_count += 1
        print("Fixed reset button section indentation (lines 1563-1591)")
    
    # Fix 5: The download button section (lines 1610-1618)
    download_button_pattern = r'# Download button\s*\n\s*with open\(st\.session_state\["mashup_path"\], "rb"\) as f:'
    download_button_replacement = '                    # Download button\n                    with open(st.session_state["mashup_path"], "rb") as f:'
    
    if re.search(download_button_pattern, content):
        content = re.sub(download_button_pattern, download_button_replacement, content)
        fix_count += 1
        print("Fixed download button section indentation (lines 1610-1618)")
    
    # Fix for the else clause after download button
    download_else_pattern = r'(\s+else:\s*\n\s+st\.error\("There was an error generating your mashup. Please try again."\))'
    download_else_replacement = '                else:\n                    st.error("There was an error generating your mashup. Please try again.")'
    
    if re.search(download_else_pattern, content):
        content = re.sub(download_else_pattern, download_else_replacement, content)
        fix_count += 1
        print("Fixed else clause after download button")
    
    # Write the fixed content back to the file
    if fix_count > 0:
        with open(app_path, 'w') as f:
            f.write(content)
        print(f"\n✓ Successfully fixed {fix_count} indentation issues in {app_path}")
    else:
        print("\n× No indentation issues found to fix")
    
    return fix_count > 0

if __name__ == "__main__":
    print("Fixing final indentation issues in app_enhanced.py...\n")
    fix_final_indentation()
    print("Done.") 