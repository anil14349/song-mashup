#!/usr/bin/env python3

"""
Fix mixed indentation issues in app_enhanced.py.
This script specifically targets lines where comments and code are misaligned.
"""

import os
import re

def fix_mixed_indentation():
    """Fix lines with mixed indentation patterns in app_enhanced.py."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file line by line
    with open(app_path, 'r') as f:
        lines = f.readlines()
    
    # Track fixed lines
    fixed_count = 0
    
    # First pass - fix trailing comments and update code blocks
    for i in range(len(lines)):
        # Fix lines with trailing comments followed by indented code
        if re.search(r'\)\s+#.*', lines[i]) and i+1 < len(lines) and re.match(r'^\s{30,}', lines[i+1]):
            # Check for trailing comment after close parenthesis
            parts = lines[i].split('#')
            code_part = parts[0].rstrip()
            comment_part = '#' + '#'.join(parts[1:])
            
            # Normalize the indentation - replace excessively indented comment with normal
            indent_level = len(re.match(r'^(\s*)', code_part).group(1))
            lines[i] = code_part + '\n'
            
            # Insert the comment on its own line with proper indentation
            fixed_count += 1
            print(f"Fixed trailing comment on line {i+1}")
            
            # Add proper indentation to the next few lines that might be affected
            next_indent = indent_level
            for j in range(i+1, min(i+10, len(lines))):
                current_indent = len(re.match(r'^(\s*)', lines[j]).group(1))
                # If current line is indented more than needed, fix it
                if current_indent > indent_level + 8:
                    lines[j] = ' ' * (indent_level + 4) + lines[j].lstrip()
                    fixed_count += 1
                    print(f"Fixed excessive indentation on line {j+1}")
    
    # Second pass - specifically fix the line 1491 issue (by line number)
    for i in range(len(lines)):
        # Look for the line with "# Update the session state to use the processed file" comment
        if ")                                                        # Update the session state to use the processed file" in lines[i]:
            # Get the base indentation from the beginning of this line
            base_indent = re.match(r'^(\s*)', lines[i]).group(1)
            
            # Split the line to separate code and comment
            parts = lines[i].split('#')
            code_part = parts[0].rstrip()
            
            # Fix this line
            lines[i] = code_part + '\n'
            
            # Insert the comment as a separate line with proper indentation
            lines.insert(i+1, base_indent + '# Update the session state to use the processed file\n')
            fixed_count += 1
            print(f"Fixed mixed code/comment at line {i+1}")
            
            # Fix indentation for the following if statement and code block
            if i+2 < len(lines) and "if result_path and os.path.exists(result_path):" in lines[i+2]:
                # Normalize indentation for the if statement
                lines[i+2] = base_indent + '    if result_path and os.path.exists(result_path):\n'
                fixed_count += 1
                print(f"Fixed if statement indentation at line {i+3}")
                
                # Fix the indentation for the entire block
                current_indent = base_indent + '        '
                for j in range(i+3, min(i+15, len(lines))):
                    # Skip already processed lines
                    if "else:" in lines[j] and not re.search(r'^\s+else:', lines[j]):
                        continue
                        
                    # Normalize indentation for this block
                    stripped_line = lines[j].lstrip()
                    if stripped_line:
                        lines[j] = current_indent + stripped_line
                        fixed_count += 1
                        print(f"Fixed block indentation at line {j+1}")
    
    # Third pass - fix any remaining issues with the same pattern
    i = 0
    while i < len(lines):
        # Find any remaining instances of "rerun()" followed by "else:" on the same line
        if re.search(r'rerun\(\)\s+else:', lines[i]):
            parts = lines[i].split('else:')
            if len(parts) > 1:
                # Get indentation level
                base_indent = re.match(r'^(\s*)', lines[i]).group(1)
                
                # Fix the line with rerun()
                lines[i] = parts[0] + '\n'
                
                # Insert else on its own line
                lines.insert(i+1, base_indent + 'else:\n')
                
                # Adjust indentation for the line after else:
                if i+2 < len(lines):
                    lines[i+2] = base_indent + '    ' + lines[i+2].lstrip()
                
                fixed_count += 2
                print(f"Fixed rerun() else: pattern at line {i+1}")
                
                # Skip the newly inserted line
                i += 1
        i += 1
    
    # Fourth pass - check for other common error patterns
    for i in range(len(lines)):
        # Fix lines with the pattern ")                else:"
        if re.search(r'\)\s+else:', lines[i]) and not re.search(r'^\s+else:', lines[i]):
            match = re.search(r'^(\s*.*?\))\s+else:', lines[i])
            if match:
                # Get the indentation level
                base_indent = re.match(r'^(\s*)', lines[i]).group(1)
                
                # Fix the line with closing parenthesis
                lines[i] = match.group(1) + '\n'
                
                # Insert else: on its own line
                lines.insert(i+1, base_indent + 'else:\n')
                fixed_count += 1
                print(f"Fixed parenthesis + else: pattern at line {i+1}")
    
    # Write the fixed content back to the file
    if fixed_count > 0:
        with open(app_path, 'w') as f:
            f.writelines(lines)
        print(f"\n✓ Successfully fixed {fixed_count} mixed indentation issues in {app_path}")
    else:
        print("\n× No mixed indentation issues found to fix")
    
    return fixed_count > 0

if __name__ == "__main__":
    print("Fixing mixed indentation issues in app_enhanced.py...\n")
    fixed = fix_mixed_indentation()
    if fixed:
        print("\nDone. Mixed indentation issues fixed.")
    else:
        print("\nDone. No issues found to fix.") 