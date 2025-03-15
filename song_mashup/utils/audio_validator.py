"""
Utility functions for validating audio files.
"""

import os
from fastapi import UploadFile


def validate_audio_file(file: UploadFile) -> bool:
    """
    Validate if the uploaded file is a supported audio format.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        Boolean indicating if the file is a valid audio format
    """
    # List of supported audio extensions
    supported_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
    
    # Get the file extension
    _, ext = os.path.splitext(file.filename.lower())
    
    # Check if extension is supported
    if ext not in supported_extensions:
        return False
    
    # Check content type
    content_type = file.content_type
    if content_type and not content_type.startswith('audio/'):
        return False
    
    return True 