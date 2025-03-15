#!/usr/bin/env python3

"""
Comprehensive indentation fixer for app_enhanced.py
This script fixes all try/except blocks with improper indentation.
"""

def fix_indentation():
    # Read the file
    with open('app_enhanced.py', 'r') as file:
        lines = file.readlines()
    
    # Track the current indentation level for try blocks
    try_indent_stack = []
    in_try_block = False
    fixed_count = 0
    
    # Process each line
    for i in range(len(lines)):
        line = lines[i]
        stripped = line.lstrip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # Calculate current indentation
        current_indent = len(line) - len(stripped)
        
        # Check for try statements
        if stripped.startswith('try:'):
            try_indent_stack.append(current_indent)
            in_try_block = True
        
        # Check for except statements
        elif stripped.startswith('except '):
            if try_indent_stack:
                expected_indent = try_indent_stack[-1]
                
                # If indentation is wrong, fix it
                if current_indent != expected_indent:
                    # Fix the except line
                    lines[i] = ' ' * expected_indent + stripped
                    fixed_count += 1
                    
                    # Fix indentation of the block following the except
                    j = i + 1
                    while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > expected_indent):
                        # If not an empty line and has content
                        if lines[j].strip():
                            # Calculate content indentation (expected + 4)
                            content = lines[j].lstrip()
                            lines[j] = ' ' * (expected_indent + 4) + content
                            fixed_count += 1
                        j += 1
                
                # If we're at the end of a try-except, pop the stack
                if len(try_indent_stack) > 0:
                    try_indent_stack.pop()
                    
                if len(try_indent_stack) == 0:
                    in_try_block = False
        
        # Handle specific issue in process_files_sync function
        if i > 195 and i < 210 and 'return os.path.join(MASHUP_DIR, f"{job_id}.mp3")' in line:
            # Check if next line is an except
            if i+1 < len(lines) and 'except Exception as e:' in lines[i+1]:
                # This is a special case where except is placed after a return
                # Need to move the except to the proper level and remove extra indentation
                expected_indent = try_indent_stack[-1] if try_indent_stack else 4
                lines[i+1] = ' ' * expected_indent + 'except Exception as e:\n'
                fixed_count += 1
    
    # Write the fixed content back
    with open('app_enhanced.py', 'w') as file:
        file.writelines(lines)
    
    print(f"Fixed {fixed_count} indentation issues in app_enhanced.py")

if __name__ == "__main__":
    fix_indentation() 