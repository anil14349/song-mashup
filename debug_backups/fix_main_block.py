#!/usr/bin/env python3

"""
Script to fix the main block indentation in app_enhanced.py
"""

with open('app_enhanced.py', 'r') as file:
    lines = file.readlines()

# Find and fix the main block line
for i, line in enumerate(lines):
    if line.strip() == "if __name__ == \"__main__\":":
        # This line should not be indented
        lines[i] = "if __name__ == \"__main__\":\n"
        
        # Ensure initialize_session_state() and main() are properly indented
        if i+1 < len(lines) and "initialize_session_state()" in lines[i+1]:
            # Check indentation, should be 4 spaces
            if len(lines[i+1]) - len(lines[i+1].lstrip()) != 4:
                lines[i+1] = "    initialize_session_state()\n"
                
        if i+2 < len(lines) and "main()" in lines[i+2]:
            # Check indentation, should be 4 spaces
            if len(lines[i+2]) - len(lines[i+2].lstrip()) != 4:
                lines[i+2] = "    main()\n"
        
        break

with open('app_enhanced.py', 'w') as file:
    file.writelines(lines)

print("Fixed main block indentation in app_enhanced.py") 