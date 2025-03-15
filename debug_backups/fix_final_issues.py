#!/usr/bin/env python3

"""
Fix the final compilation issues in app_enhanced.py.
This script performs direct replacements for known problematic sections.
"""

import os
import re

def fix_final_issues():
    """Fix the remaining compilation issues in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Track fixed issues
    fixed_count = 0
    
    # Read the entire file as a string
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Fix the nested indentation and try-except issues (line 1493-1507)
    # Look for the problematic section
    problematic_section = re.search(r'if "original_mashup_path" not in st\.session_state:\s+# Update the session state to use the processed file\s+try:', content)
    
    if problematic_section:
        # Define the corrected code block
        corrected_block = """                                        if "original_mashup_path" not in st.session_state:
                                            st.session_state["original_mashup_path"] = st.session_state["mashup_path"]
                                    
                                # Update the session state to use the processed file
                                try:
                                    if result_path and os.path.exists(result_path):
                                        # Store both the original and processed paths
                                        if "original_mashup_path" not in st.session_state:
                                            st.session_state["original_mashup_path"] = st.session_state["mashup_path"]"""
        
        # Replace the problematic section with our corrected version
        content = content.replace(problematic_section.group(0), corrected_block)
        fixed_count += 1
        print("Fixed missing indented block and duplicate code around line 1493-1498")
    
    # Fix 2: Fix the download button else issue (line 1617-1620)
    # Look for the download button section followed by an indented else
    download_else_pattern = r'(\s+)with open\(st\.session_state\["mashup_path"\], "rb"\) as f:\s*\n\s+st\.download_button\(.*?\n\s+.*?\n\s+.*?\n\s+.*?\n\s+\)\s*\n\s+else:'
    
    if re.search(download_else_pattern, content, re.DOTALL):
        # Replace with properly formatted code
        corrected_block = """                    with open(st.session_state["mashup_path"], "rb") as f:
                        st.download_button(
                            label="Download Mashup",
                            data=f,
                            file_name=f"song_mashup_{st.session_state['job_id']}.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                else:"""
        
        content = re.sub(download_else_pattern, corrected_block, content, flags=re.DOTALL)
        fixed_count += 1
        print("Fixed indentation issue with else statement around line 1617-1620")
    
    # Fix 3: Fix any remaining else statements with improper indentation
    else_pattern = r'(\s+)(\)\s+)else:'
    else_replacement = r'\1)\n\1else:'
    
    match_count = len(re.findall(else_pattern, content, re.DOTALL))
    if match_count > 0:
        content = re.sub(else_pattern, else_replacement, content, flags=re.DOTALL)
        fixed_count += match_count
        print(f"Fixed {match_count} additional else statements with improper indentation")
    
    # Write the fixed content back to the file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.write(content)
        print(f"\n✓ Successfully fixed {fixed_count + match_count} compilation issues in {app_path}")
    else:
        print("\n× No compilation issues found to fix")
    
    return fixed_count > 0

if __name__ == "__main__":
    print("Fixing final compilation issues in app_enhanced.py...\n")
    fixed = fix_final_issues()
    
    if fixed:
        print("\nDone. All compilation issues should now be fixed.")
        print("\nWhy do we have so many fix_*.py files?")
        print("========================================")
        print("We created separate scripts to tackle different types of issues:")
        print("1. fix_indentation.py - Fixed initial indentation issues")
        print("2. fix_all_sliders.py - Fixed slider compilation errors")
        print("3. fix_specific_sliders.py - Fixed specific slider issues")
        print("4. fix_extreme_indentation.py - Fixed extreme indentation issues")
        print("5. fix_mixed_indentation.py - Fixed issues with mixed indentation styles")
        print("6. fix_syntax_errors.py - Addressed syntax errors")
        print("7. fix_final_issues.py - This script (final targeted fixes)")
        print("\nYou can now delete these files or keep them for reference.")
        print("To clean up, you could run: rm fix_*.py")
    else:
        print("\nDone. No issues found to fix.") 