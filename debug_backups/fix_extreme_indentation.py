#!/usr/bin/env python3

"""
Fix extreme indentation issues in app_enhanced.py.
This script specifically handles lines with abnormally large indentation.
"""

import os
import re

def fix_extreme_indentation():
    """Fix lines with extreme indentation in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file line by line
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # Track fixed lines
    fixed_count = 0
    
    # Look for problematic patterns
    for i in range(len(lines)):
        # Match lines with extreme indentation
        if re.match(r'^\s{50,}with comp_cols\[1\]:', lines[i]):
            # Fix the indentation for with comp_cols[1]:
            lines[i] = '                                with comp_cols[1]:\n'
            fixed_count += 1
            print(f"Fixed extreme indentation at line {i+1} (with comp_cols[1]:)")
        
        # Match lines with extreme indentation for delay_cols
        elif re.match(r'^\s{50,}with delay_cols\[1\]:', lines[i]):
            # Fix the indentation for with delay_cols[1]:
            lines[i] = '                                with delay_cols[1]:\n'
            fixed_count += 1
            print(f"Fixed extreme indentation at line {i+1} (with delay_cols[1]:)")
        
        # Fix misplaced else statements
        elif re.search(r'rerun\(\)\s+else:', lines[i]):
            # Split the line at rerun() and else:
            parts = lines[i].split('rerun()')
            if len(parts) == 2:
                lines[i] = parts[0] + 'rerun()\n'
                # Insert the else with proper indentation
                lines.insert(i+1, '                                            else:\n')
                fixed_count += 1
                print(f"Fixed line break issue at line {i+1} (rerun() else:)")
        
        # Fix misplaced download button else statement
        elif re.search(r'\)\s+else:', lines[i]):
            match = re.search(r'^(\s+.*?\))\s+else:', lines[i])
            if match:
                # Get the base indentation level
                base_indent = re.match(r'^(\s+)', lines[i])
                base_indent = base_indent.group(1) if base_indent else ''
                
                # Split the line
                lines[i] = match.group(1) + '\n'
                # Insert the else with proper indentation
                lines.insert(i+1, base_indent + 'else:\n')
                fixed_count += 1
                print(f"Fixed line break issue at line {i+1} (closing parenthesis followed by else:)")
        
        # Fix line with store original_mashup_path - missing indentation
        elif re.search(r'if "original_mashup_path" not in st\.session_state:\s*\n\s*st\.session_state\["original_mashup_path"\]', ''.join(lines[i:i+2])):
            # Check if next line has proper indentation
            if i+1 < len(lines) and not re.match(r'^\s{50,}', lines[i+1]):
                current_indent = re.match(r'^(\s+)', lines[i])
                current_indent = current_indent.group(1) if current_indent else ''
                next_line = lines[i+1]
                
                # Add proper indentation to the next line
                lines[i+1] = current_indent + '    ' + next_line.lstrip()
                fixed_count += 1
                print(f"Fixed missing indentation at line {i+2} (original_mashup_path assignment)")
    
    # Write the fixed content back to the file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"\n✓ Successfully fixed {fixed_count} extreme indentation issues in {app_path}")
    else:
        print("\n× No extreme indentation issues found to fix")
    
    return fixed_count > 0

def normalize_indentation():
    """Normalize indentation for specific sections in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"\nNormalizing indentation in critical sections...")
    
    # Read the file as a single string
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Fix count
    fix_count = 0
    
    # Critical section patterns and their normalized replacements
    critical_sections = [
        # Fix the Update Session State section with normalized indentation
        (
            r'(\s+)# Update the session state to use the processed file\s*\n\s+if result_path and os\.path\.exists\(result_path\):\s*\n\s+# Store both the original and processed paths\s*\n\s+if "original_mashup_path" not in st\.session_state:\s*\n\s+(st\.session_state\["original_mashup_path"\].*?\n)\s+# Update the current mashup path to the processed version\s*\n\s+st\.session_state\["mashup_path"\] = result_path\s*\n\s+st\.session_state\["is_processed"\] = True',
            '                                        # Update the session state to use the processed file\n                                        if result_path and os.path.exists(result_path):\n                                            # Store both the original and processed paths\n                                            if "original_mashup_path" not in st.session_state:\n                                                st.session_state["original_mashup_path"] = st.session_state["mashup_path"]\n                                            # Update the current mashup path to the processed version\n                                            st.session_state["mashup_path"] = result_path\n                                            st.session_state["is_processed"] = True'
        ),
        
        # Fix the Error Handling section
        (
            r'(\s+)else:\s*\n\s+st\.error\("Failed to process (audio with mix settings|stems with effects)"\)\s*\n\s+except Exception as e:\s*\n\s+st\.error\(f"Error applying (mix|stem) settings: {str\(e\)}"\)\s*\n\s+logger\.error\(f"(Mix|Stem) processing error: {str\(e\)}", exc_info=True\)',
            '                                        else:\n                                            st.error("Failed to process \\2")\n                                    except Exception as e:\n                                        st.error(f"Error applying \\3 settings: {str(e)}")\n                                        logger.error(f"\\4 processing error: {str(e)}", exc_info=True)'
        )
    ]
    
    # Apply fixed indentation to critical sections
    for pattern, replacement in critical_sections:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            fix_count += len(matches)
            print(f"Normalized indentation in critical section (matches: {len(matches)})")
    
    # Write the modified content back to the file
    if fix_count > 0:
        with open(app_path, 'w') as f:
            f.write(content)
        print(f"✓ Successfully normalized indentation in {fix_count} critical sections")
    
    return fix_count > 0

if __name__ == "__main__":
    print("Fixing extreme indentation issues in app_enhanced.py...\n")
    fixed_extreme = fix_extreme_indentation()
    fixed_normalized = normalize_indentation()
    
    if fixed_extreme or fixed_normalized:
        print("\nDone. All extreme indentation issues fixed.")
    else:
        print("\nDone. No issues found to fix.") 