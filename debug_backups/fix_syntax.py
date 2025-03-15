#!/usr/bin/env python3

"""
Emergency syntax error fix for app_enhanced.py
This script specifically targets the indentation error at line ~2066
where an 'except' statement has incorrect indentation.
"""

import re

# Read the file
with open('app_enhanced.py', 'r') as file:
    content = file.read()

# Look for the problematic pattern
# Find a line with 'except Exception as e:' that's not properly indented
pattern = r'(\n[ ]{0,7})except Exception as e:'

# Replace with proper indentation (8 spaces)
fixed_content = re.sub(pattern, '\n        except Exception as e:', content)

# Write the fixed content back
with open('app_enhanced.py', 'w') as file:
    file.write(fixed_content)

print("Fixed the syntax error in app_enhanced.py") 