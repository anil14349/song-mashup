#!/usr/bin/env python3

"""
Final fix script for app_enhanced.py
This script addresses any remaining indentation issues, particularly with 'with' blocks.
"""

def fix_remaining_issues():
    # Read the file
    with open('app_enhanced.py', 'r') as file:
        lines = file.readlines()
    
    fixed_count = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        # Skip empty lines
        if not stripped:
            i += 1
            continue
        
        # Calculate current indentation
        current_indent = len(line) - len(stripped)
        
        # Check for 'with' statements that need proper block indentation
        if stripped.startswith('with ') and stripped.endswith(':'):
            # Find the block that should be indented under this 'with' statement
            expected_indent = current_indent + 4  # Expected 4 more spaces for indented block
            
            # Check next line
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.lstrip()
                
                if next_stripped and len(next_line) - len(next_stripped) < expected_indent:
                    # Indentation is incorrect, fix all lines in the block
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= current_indent:
                        if lines[j].strip():  # Not an empty line
                            content = lines[j].lstrip()
                            lines[j] = ' ' * expected_indent + content
                            fixed_count += 1
                        j += 1
        
        # Also check for try/except/finally blocks with improper indentation
        if stripped.startswith(('try:', 'except ', 'finally:')):
            # Find the block that should be indented
            expected_indent = current_indent + 4
            
            # Check next line
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.lstrip()
                
                if next_stripped and len(next_line) - len(next_stripped) < expected_indent:
                    # Indentation is incorrect, fix all lines in the block
                    j = i + 1
                    while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) <= current_indent):
                        if lines[j].strip() and not lines[j].lstrip().startswith(('except ', 'finally:')):
                            content = lines[j].lstrip()
                            lines[j] = ' ' * expected_indent + content
                            fixed_count += 1
                        j += 1
        
        i += 1
    
    # Specifically fix the error details expander block at lines 2068-2073
    for i in range(len(lines)):
        if "with st.expander(\"Error Details\"):" in lines[i]:
            # Fix the next few lines to be properly indented
            indent_level = len(lines[i]) - len(lines[i].lstrip())
            expected_indent = indent_level + 4
            
            # Check and fix the next few lines
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) < expected_indent:
                    content = lines[j].lstrip()
                    lines[j] = ' ' * expected_indent + content
                    fixed_count += 1
                # Break if we hit a line with less indentation than the 'with' line
                elif lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent_level:
                    break
    
    # Write the fixed content back
    with open('app_enhanced.py', 'w') as file:
        file.writelines(lines)
    
    print(f"Fixed {fixed_count} remaining indentation issues in app_enhanced.py")

if __name__ == "__main__":
    fix_remaining_issues() 