#!/usr/bin/env python3

"""
Direct fix for the Try Again button indentation issue
"""

# Read the file
with open('app_enhanced.py', 'r') as file:
    content = file.read()

# Replace the problematic block with properly indented code
problematic = """                        # Try again button
                        if st.button("Try Again", use_container_width=True):
                            reset_state()
                            rerun()"""

fixed = """                # Try again button
                if st.button("Try Again", use_container_width=True):
                    reset_state()
                    rerun()"""

# Apply the fix
fixed_content = content.replace(problematic, fixed)

# Write the fixed content back
with open('app_enhanced.py', 'w') as file:
    file.write(fixed_content)

print("Fixed the Try Again button indentation") 