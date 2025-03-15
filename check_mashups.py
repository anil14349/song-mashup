#!/usr/bin/env python3

"""
Check the mashup directory for existing files and verify permissions.
This will help debug issues with the audio player controls not appearing.
"""

import os
import glob
import time

# The path should match the one in app_enhanced.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MASHUP_DIR = os.path.join(BASE_DIR, "song_mashup", "data", "mashups")

def check_mashup_directory():
    print(f"Checking mashup directory: {MASHUP_DIR}")
    
    # Check if the directory exists
    if not os.path.exists(MASHUP_DIR):
        print(f"❌ ERROR: Mashup directory does not exist!")
        try:
            os.makedirs(MASHUP_DIR, exist_ok=True)
            print(f"✓ Created mashup directory")
        except Exception as e:
            print(f"❌ Failed to create directory: {str(e)}")
        return
    
    # Check permissions
    if not os.access(MASHUP_DIR, os.R_OK | os.W_OK):
        print(f"❌ ERROR: No read/write permission on mashup directory!")
        return
    
    # Find mashup files
    mashup_files = glob.glob(os.path.join(MASHUP_DIR, "*.mp3"))
    
    if not mashup_files:
        print("❌ No mashup files found!")
    else:
        print(f"✓ Found {len(mashup_files)} mashup files:")
        
        # List the most recent mashups first
        mashup_files.sort(key=os.path.getmtime, reverse=True)
        
        for i, file_path in enumerate(mashup_files[:5]):  # Show only the 5 most recent
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            mod_time = time.ctime(os.path.getmtime(file_path))
            
            print(f"  {i+1}. {file_name} ({file_size:.2f} MB) - Modified: {mod_time}")
            
            # Check if the file is readable
            if not os.access(file_path, os.R_OK):
                print(f"    ❌ WARNING: File is not readable!")
        
        if len(mashup_files) > 5:
            print(f"  ... and {len(mashup_files) - 5} more files")

if __name__ == "__main__":
    check_mashup_directory() 