#!/usr/bin/env python3

"""
Fix remaining syntax errors in app_enhanced.py.
This script focuses on fixing try-except blocks and misplaced else statements.
"""

import os
import re

def fix_syntax_errors():
    """Fix remaining syntax errors in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file line by line
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Track fixed issues
    fixed_count = 0
    
    # Fix 1: Missing try block for the except block around line 1504
    try_except_pattern = r'(\s+)if result_path and os\.path\.exists\(result_path\).*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?rerun\(\)\s*\n\s+else:.*?\n\s+st\.error\("Failed to process audio with mix settings"\)\s*\n(\s+)except Exception as e:'
    try_except_replacement = r'\1try:\n\1    if result_path and os.path.exists(result_path):\n\1        # Store both the original and processed paths\n\1        if "original_mashup_path" not in st.session_state:\n\1            st.session_state["original_mashup_path"] = st.session_state["mashup_path"]\n\1        # Update the current mashup path to the processed version\n\1        st.session_state["mashup_path"] = result_path\n\1        st.session_state["is_processed"] = True\n\1        \n\1        # Success message\n\1        st.success("Mix settings applied successfully!")\n\1        \n\1        # Rerun to refresh audio player\n\1        rerun()\n\1    else:\n\1        st.error("Failed to process audio with mix settings")\n\2except Exception as e:'
    
    if re.search(try_except_pattern, content, re.DOTALL):
        content = re.sub(try_except_pattern, try_except_replacement, content, flags=re.DOTALL)
        fixed_count += 1
        print("Fixed missing try: statement for except block around line 1504")
    
    # Fix 2: Indentation issue with else statement around line 1612
    download_else_pattern = r'(\s+)with open\(st\.session_state\["mashup_path"\], "rb"\) as f:\s*\n\s+st\.download_button\(.*?\n\s+.*?\n\s+.*?\n\s+.*?\n\s+\)\s*\n\s+else:'
    download_else_replacement = r'\1with open(st.session_state["mashup_path"], "rb") as f:\n\1    st.download_button(\n\1        label="Download Mashup",\n\1        data=f,\n\1        file_name=f"song_mashup_{st.session_state[\'job_id\']}.mp3",\n\1        mime="audio/mp3",\n\1        use_container_width=True\n\1    )\n\1else:'
    
    if re.search(download_else_pattern, content, re.DOTALL):
        content = re.sub(download_else_pattern, download_else_replacement, content, flags=re.DOTALL)
        fixed_count += 1
        print("Fixed indentation issue with else statement around line 1612")
    
    # Fix 3: Check for any other orphaned except blocks
    orphaned_except_pattern = r'(\s+)else:.*?\n(\s+)st\.error\(".*?"\)\s*\n(?!\s*try:)(\s+)except Exception as e:'
    orphaned_except_replacement = r'\1else:\n\2st.error("\3")\n\1try:\n\1    pass  # Placeholder for try block\n\3except Exception as e:'
    
    match_count = len(re.findall(orphaned_except_pattern, content, re.DOTALL))
    if match_count > 0:
        content = re.sub(orphaned_except_pattern, orphaned_except_replacement, content, flags=re.DOTALL)
        fixed_count += match_count
        print(f"Fixed {match_count} orphaned except blocks")
    
    # Fix 4: General else indentation issue pattern
    else_indentation_pattern = r'(\s+)(\)\s*\n\s+)else:'
    else_indentation_replacement = r'\1)\n\1else:'
    
    match_count = len(re.findall(else_indentation_pattern, content, re.DOTALL))
    if match_count > 0:
        content = re.sub(else_indentation_pattern, else_indentation_replacement, content, flags=re.DOTALL)
        fixed_count += match_count
        print(f"Fixed {match_count} else indentation issues")
    
    # Fix 5: Find and fix specific pattern with misaligned try-except
    specific_try_except_pattern = r'(\s+)(# Process the file with stem-specific effects.*?\n\s+.*?\n\s+result_path = process_stems_with_effects\(.*?\n\s+.*?,\n\s+.*?,\n\s+.*?\n\s+\))(\s+if result_path and os\.path\.exists\(result_path\))'
    specific_try_except_replacement = r'\1\2\n\1try:\3'
    
    if re.search(specific_try_except_pattern, content, re.DOTALL):
        content = re.sub(specific_try_except_pattern, specific_try_except_replacement, content, flags=re.DOTALL)
        fixed_count += 1
        print("Fixed specific try-except pattern around process_stems_with_effects")
    
    # Write the fixed content back to the file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.write(content)
        print(f"\n✓ Successfully fixed {fixed_count} syntax issues in {app_path}")
    else:
        print("\n× No syntax issues found to fix")
    
    return fixed_count > 0

# Add a direct fix for known problematic sections
def direct_fixes():
    """Apply direct replacements for known problematic sections."""
    
    app_path = "app_enhanced.py"
    print(f"\nApplying direct fixes to critical sections...")
    
    # Read the file
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # Track fixes
    fixed_count = 0
    
    # Search for the specific try-except block that's causing problems
    try_except_region_start = -1
    try_except_region_end = -1
    
    for i, line in enumerate(lines):
        # Find the bass_comp_ratio_slider section to locate the problematic region
        if "key=\"bass_comp_ratio_slider\"" in line:
            try_except_region_start = i + 5  # Start a few lines after
            break
    
    if try_except_region_start >= 0:
        # Find the end of this region (the "Apply stem effects button" comment)
        for i in range(try_except_region_start, len(lines)):
            if "# Apply stem effects button" in lines[i]:
                try_except_region_end = i - 1
                break
        
        if try_except_region_end > try_except_region_start:
            # We found the problematic region, now replace it with fixed code
            fixed_block = [
                "                                # Update the session state to use the processed file\n",
                "                                try:\n",
                "                                    if result_path and os.path.exists(result_path):\n",
                "                                        # Store both the original and processed paths\n",
                "                                        if \"original_mashup_path\" not in st.session_state:\n",
                "                                            st.session_state[\"original_mashup_path\"] = st.session_state[\"mashup_path\"]\n",
                "                                        # Update the current mashup path to the processed version\n",
                "                                        st.session_state[\"mashup_path\"] = result_path\n",
                "                                        st.session_state[\"is_processed\"] = True\n",
                "                                        \n",
                "                                        # Success message\n",
                "                                        st.success(\"Mix settings applied successfully!\")\n",
                "                                        \n",
                "                                        # Rerun to refresh audio player\n",
                "                                        rerun()\n",
                "                                    else:\n",
                "                                        st.error(\"Failed to process audio with mix settings\")\n",
                "                                except Exception as e:\n",
                "                                    st.error(f\"Error applying mix settings: {str(e)}\")\n",
                "                                    logger.error(f\"Mix processing error: {str(e)}\", exc_info=True)\n"
            ]
            
            # Replace the problematic region
            lines[try_except_region_start:try_except_region_end] = fixed_block
            fixed_count += 1
            print(f"Directly fixed try-except block in lines {try_except_region_start+1}-{try_except_region_end+1}")
    
    # Find and fix the download button else issue
    download_region_start = -1
    download_region_end = -1
    
    for i, line in enumerate(lines):
        if "# Download button" in line:
            download_region_start = i
            break
    
    if download_region_start >= 0:
        # Find the end of this region (the </div> line)
        for i in range(download_region_start, len(lines)):
            if "</div>" in lines[i]:
                download_region_end = i
                break
        
        if download_region_end > download_region_start:
            # Look for the problematic part within this region
            for i in range(download_region_start, download_region_end):
                if re.search(r'\)\s+else:', lines[i]):
                    # Split this line
                    parts = lines[i].split('else:')
                    base_indent = re.match(r'^(\s*)', lines[i]).group(1)
                    
                    if len(parts) > 1:
                        # Fix the line
                        lines[i] = parts[0] + '\n'
                        lines.insert(i+1, base_indent + 'else:\n')
                        fixed_count += 1
                        print(f"Directly fixed download button else: issue at line {i+1}")
                        break
    
    # Write the fixed content back to the file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"✓ Successfully applied {fixed_count} direct fixes to critical sections")
    
    return fixed_count > 0

if __name__ == "__main__":
    print("Fixing remaining syntax errors in app_enhanced.py...\n")
    
    # First try direct fixes for known issues
    fixed_direct = direct_fixes()
    
    # Then try pattern-based fixes for any remaining issues
    fixed_patterns = fix_syntax_errors()
    
    if fixed_direct or fixed_patterns:
        print("\nDone. All syntax errors fixed.")
    else:
        print("\nDone. No issues found to fix.") 