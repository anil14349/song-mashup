#!/usr/bin/env python3

"""
Fix syntax issues in app_enhanced.py by searching for and correcting specific patterns.
"""

import re
import os

def fix_syntax_issues():
    """Fix various syntax issues in the app_enhanced.py file."""
    
    app_path = "app_enhanced.py"
    print(f"Reading {app_path}...")
    
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
    
    # List of problematic patterns and their fixes
    patterns = [
        {
            'desc': 'String with embedded key parameter',
            'regex': r'"([^"]*), key="([^"]*)"\)"',
            'replacement': r'"\1", key="\2")'
        },
        {
            'desc': 'Missing closing parenthesis on slider',
            'regex': r'(st\.slider\([^)]*?)(\n\s*[a-zA-Z_])',
            'replacement': r'\1)\2'
        },
        {
            'desc': 'Extra comma in slider definition',
            'regex': r'(key="[^"]*"),\s*\)',
            'replacement': r'\1)'
        }
    ]
    
    # Apply each pattern fix
    fixed_content = content
    total_fixed = 0
    
    for pattern in patterns:
        matches = re.findall(pattern['regex'], fixed_content)
        if matches:
            count = len(matches)
            fixed_content = re.sub(pattern['regex'], pattern['replacement'], fixed_content)
            total_fixed += count
            print(f"✓ Fixed {count} instances of: {pattern['desc']}")
    
    # Save if changes were made
    if total_fixed > 0:
        # Save the fixed content
        with open(app_path, 'w') as f:
            f.write(fixed_content)
        print(f"\n✓ Successfully fixed {total_fixed} syntax issues")
        return True
    else:
        print("\n× No syntax issues found matching our patterns")
        return False

if __name__ == "__main__":
    print("Fixing syntax issues...\n")
    fix_syntax_issues() 