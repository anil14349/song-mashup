#!/usr/bin/env python3

"""Fix indentation in the Try Again button handler"""

with open('app_enhanced.py', 'r') as file:
    lines = file.readlines()

for i, line in enumerate(lines):
    if 'if st.button("Try Again"' in line:
        # Next two lines should be indented at the same level as the if + 4 spaces
        if i+1 < len(lines) and 'reset_state()' in lines[i+1]:
            indent = len(line) - len(line.lstrip()) + 4
            lines[i+1] = ' ' * indent + lines[i+1].lstrip()
            
        if i+2 < len(lines) and 'rerun()' in lines[i+2]:
            indent = len(line) - len(line.lstrip()) + 4
            lines[i+2] = ' ' * indent + lines[i+2].lstrip()

with open('app_enhanced.py', 'w') as file:
    file.writelines(lines)

print("Fixed button handler indentation") 