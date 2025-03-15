#!/usr/bin/env python
"""
Entry point script to run the Song Mashup Generator application with Streamlit.
This script allows users to choose between the standard and enhanced versions.
"""

import os
import sys
import subprocess
import argparse

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run the AI Song Mashup Generator')
    parser.add_argument('--enhanced', action='store_true', help='Run the enhanced version with improved AI models (default)')
    parser.add_argument('--standard', action='store_true', help='Run the standard version with basic functionality')
    args = parser.parse_args()
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to the path
    sys.path.insert(0, current_dir)
    
    # Determine which app to run
    if args.standard:
        app_path = os.path.join(current_dir, "app_standard.py")
        print("Running standard version with basic functionality...")
    else:
        # Default to enhanced if available, otherwise fall back to standard
        enhanced_app_path = os.path.join(current_dir, "app_enhanced.py")
        standard_app_path = os.path.join(current_dir, "app_standard.py")
        
        if os.path.exists(enhanced_app_path) and (args.enhanced or not args.standard):
            app_path = enhanced_app_path
            print("Running enhanced version with improved AI models and advanced features...")
        else:
            app_path = standard_app_path
            if args.enhanced:
                print("Enhanced version not found, falling back to standard version...")
            else:
                print("Running standard version...")
    
    # Run the Streamlit app
    subprocess.run(["streamlit", "run", app_path]) 