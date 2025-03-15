"""
Utility functions for handling file uploads and temporary storage.
"""

import os
import shutil
import asyncio
from typing import List
from fastapi import UploadFile


async def save_upload_file_tmp(upload_file: UploadFile, dest_folder: str) -> str:
    """
    Asynchronously saves an upload file to a temporary location
    
    Args:
        upload_file: The uploaded file
        dest_folder: Destination folder to save the file
        
    Returns:
        Path to the saved temporary file
    """
    # Ensure destination folder exists
    os.makedirs(dest_folder, exist_ok=True)
    
    # Create output filepath
    dest = os.path.join(dest_folder, upload_file.filename)
    
    # Write file
    with open(dest, "wb") as buffer:
        # Read file in chunks and write to destination
        contents = await upload_file.read()
        buffer.write(contents)
    
    return dest


async def cleanup_temp_files(job_id: str, hours: int = 24):
    """
    Schedule cleanup of temporary files after specified hours
    
    Args:
        job_id: Unique identifier for the job
        hours: Number of hours to wait before cleaning up
    """
    # Wait for the specified time
    await asyncio.sleep(hours * 3600)
    
    # Get base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Get paths
    upload_dir = os.path.join(BASE_DIR, "song_mashup", "data", "uploads", job_id)
    mashup_file = os.path.join(BASE_DIR, "song_mashup", "data", "mashups", f"{job_id}.mp3")
    
    # Remove directories if they exist
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    
    if os.path.exists(mashup_file):
        os.remove(mashup_file) 