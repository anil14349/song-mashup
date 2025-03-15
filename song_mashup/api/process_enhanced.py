"""
Enhanced core processing module for audio analysis and mashup generation.
Uses improved AI models for better audio analysis and processing.
"""

import os
import time
import uuid
import numpy as np
import librosa
import soundfile as sf
from typing import List, Dict, Tuple, Optional, Any
import torch
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
import logging
from ..models.enhanced.demucs_integration import DemucsProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import enhanced audio model
try:
    from ..models.enhanced.audio_model_enhanced import EnhancedAudioModel
    from ..models.enhanced.integration import enhanced_models_available, load_enhanced_models
    from ..models.enhanced.integration import separate_stems as enhanced_separate
    from ..models.enhanced.integration import generate_mashup as enhanced_mashup
    
    # Load enhanced models
    load_enhanced_models()
    ENHANCED_PROCESSING_AVAILABLE = enhanced_models_available()
    logger.info("Enhanced AI models loaded successfully")
except ImportError:
    logger.warning("Enhanced audio models not available - falling back to base processing")
    ENHANCED_PROCESSING_AVAILABLE = False

# Try to import base audio model
try:
    from ..models.base.audio_model import BaseAudioModel
    BASE_PROCESS_AVAILABLE = True
except ImportError:
    logger.warning("Base audio models not available")
    BASE_PROCESS_AVAILABLE = False

# Initialize the Demucs processor
demucs_processor = DemucsProcessor()

async def process_files_async(job_id: str, file_paths: List[str], blend_ratios: List[float], mix_params: Dict[str, Any] = {}):
    """
    Asynchronous wrapper for processing audio files and generating a mashup.
    
    Args:
        job_id: Unique identifier for the job
        file_paths: List of paths to audio files
        blend_ratios: List of blending ratios for each file
        mix_params: Dictionary of mixing parameters for advanced processing
    """
    # Run the processing in a separate thread to avoid blocking
    with ThreadPoolExecutor() as executor:
        executor.submit(
            process_files,
            job_id,
            file_paths,
            blend_ratios,
            mix_params
        )


def process_files(job_id: str, file_paths: List[str], blend_ratios: List[float], mix_params: Dict[str, Any] = {}):
    """
    Process audio files to create a mashup.
    
    Args:
        job_id: Unique identifier for the job
        file_paths: List of paths to audio files
        blend_ratios: List of blending ratios for each file
        mix_params: Dictionary of mixing parameters for advanced processing
    
    Returns:
        Path to the output mashup file
    """
    try:
        # Log processing start
        logger.info(f"Starting enhanced audio processing for job: {job_id}")
        
        # Check if there are enough files
        if len(file_paths) < 2:
            raise ValueError("At least 2 files are required to create a mashup")
        
        # Process each audio file
        processed_audio_data = []
        for i, file_path in enumerate(file_paths):
            try:
                logger.info(f"Processing file: {os.path.basename(file_path)}")
                
                # Load and analyze the audio
                audio_data = load_and_analyze_audio(file_path)
                
                # Add the blend ratio
                audio_data['blend_ratio'] = blend_ratios[i] if i < len(blend_ratios) else 1.0
                
                # Store the processed data
                processed_audio_data.append(audio_data)
            except Exception as e:
                error_msg = f"Error processing file {os.path.basename(file_path)}: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Separate audio stems if enhanced separation is available
        try:
            if ENHANCED_PROCESSING_AVAILABLE:
                logger.info("Separating audio stems")
                for audio_data in processed_audio_data:
                    # Make sure we have a sample_rate key for compatibility
                    if 'sr' in audio_data and 'sample_rate' not in audio_data:
                        audio_data['sample_rate'] = audio_data['sr']
                        
                    # Get mix parameters
                    vocal_prominence = mix_params.get('vocal_prominence', 1.0)
                    drum_prominence = mix_params.get('drum_prominence', 1.0)
                    bass_prominence = mix_params.get('bass_prominence', 1.0)
                    
                    # Call enhanced_separate with correct arguments
                    # Function expects only one argument (audio_data)
                    audio_data['stems'] = enhanced_separate(audio_data)
        except Exception as e:
            error_msg = f"Error separating audio stems: {str(e)}"
            logger.error(error_msg)
            # Continue without stems - this is not fatal
            logger.warning("Continuing with basic processing")
        
        # Generate the mashup
        try:
            logger.info("Generating mashup")
            if ENHANCED_PROCESSING_AVAILABLE:
                # Get mix parameters
                key_alignment = mix_params.get('key_alignment', 0.8)
                tempo_alignment = mix_params.get('tempo_alignment', 0.8)
                crossfade_duration = mix_params.get('crossfade_duration', 4.0)
                eq_profile = mix_params.get('eq_profile', 'balanced')
                
                # Ensure each audio_data has sample_rate key
                for audio_data in processed_audio_data:
                    if 'sr' in audio_data and 'sample_rate' not in audio_data:
                        audio_data['sample_rate'] = audio_data['sr']
                
                # Call enhanced_mashup with correct parameters
                blend_ratios = [audio.get('blend_ratio', 1.0) for audio in processed_audio_data]
                output_waveform = enhanced_mashup(processed_audio_data, blend_ratios)
            else:
                # Fall back to standard mashup generation
                output_waveform = standard_mashup(processed_audio_data)
        except Exception as e:
            error_msg = f"Error generating mashup: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Save the output file
        try:
            output_path = os.path.join(BASE_DIR, "song_mashup", "data", "mashups", f"{job_id}.mp3")
            
            # Get the sample rate - make sure we handle both sr and sample_rate keys
            first_audio = processed_audio_data[0]
            if 'sr' in first_audio:
                sample_rate = first_audio['sr']
            elif 'sample_rate' in first_audio:
                sample_rate = first_audio['sample_rate']
            else:
                sample_rate = 44100  # Default
                logger.warning("No sample rate found, using default 44100Hz for output")
                
            # Save using soundfile
            sf.write(output_path, output_waveform, sample_rate)
            logger.info(f"Mashup saved to: {output_path}")
            return output_path
        except Exception as e:
            error_msg = f"Error saving output file: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    except Exception as e:
        error_msg = f"Error processing mashup: {str(e)}"
        logger.error(error_msg)
        # Create an error file for debugging
        error_path = os.path.join(BASE_DIR, "song_mashup", "data", "mashups", f"{job_id}_error.txt")
        with open(error_path, 'w') as f:
            f.write(error_msg)
        raise e


def load_and_analyze_audio(file_path: str) -> Dict[str, Any]:
    """
    Load audio file and analyze its properties using enhanced analysis.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary containing audio data and analysis
    """
    try:
        # Verify the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        # Verify file size isn't zero
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"Audio file is empty: {file_path}")
            
        # Fall back to base implementation if necessary
        if not ENHANCED_PROCESSING_AVAILABLE and BASE_PROCESS_AVAILABLE:
            logger.info(f"Using base analysis for {os.path.basename(file_path)}")
            base_data = base_load_and_analyze(file_path)
            # Ensure we have both sr and sample_rate for compatibility
            if 'sr' in base_data and 'sample_rate' not in base_data:
                base_data['sample_rate'] = base_data['sr']
            elif 'sample_rate' in base_data and 'sr' not in base_data:
                base_data['sr'] = base_data['sample_rate']
            return base_data
        
        # Load audio file
        try:
            y, sr = librosa.load(file_path, sr=None)
            if len(y) == 0:
                raise ValueError(f"Failed to load audio data from {file_path}")
        except Exception as e:
            logger.error(f"Error loading audio file: {str(e)}")
            raise ValueError(f"Could not load audio file {os.path.basename(file_path)}: {str(e)}")
        
        # Basic analysis
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            key = estimate_key(chroma)
            
            # Extract features with STFT
            stft = np.abs(librosa.stft(y))
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            raise ValueError(f"Failed to analyze audio in {os.path.basename(file_path)}: {str(e)}")
        
        # Store in a dictionary
        audio_data = {
            'file_path': file_path,
            'waveform': y,
            'sr': sr,  
            'sample_rate': sr,  # Include both keys for compatibility
            'tempo': tempo,
            'key': key,
            'stft': stft,
            'duration': len(y) / sr
        }
        
        # Enhance with additional analysis if available
        if ENHANCED_PROCESSING_AVAILABLE:
            try:
                # Check waveform dimensions to avoid index errors
                if len(audio_data['waveform']) == 0:
                    logger.warning("Empty waveform - skipping enhanced analysis")
                    return audio_data
                    
                # Add try/except around enhanced analysis
                try:
                    enhanced_features = enhanced_analyze(audio_data)
                    # Add enhanced features to the audio data
                    for key, value in enhanced_features.items():
                        if key not in audio_data:  # Don't overwrite basic features
                            audio_data[key] = value
                except IndexError as idx_error:
                    # Handle index errors which might be caused by array boundary issues
                    logger.warning(f"Index error in enhanced analysis: {str(idx_error)}")
                except ValueError as val_error:
                    # Handle value errors which might be caused by incompatible inputs
                    logger.warning(f"Value error in enhanced analysis: {str(val_error)}")
            except Exception as e:
                logger.warning(f"Enhanced analysis failed: {str(e)}")
                # Continue without enhanced features - this is not fatal
        
        return audio_data
    
    except Exception as e:
        # Catch and re-raise any other errors with more context
        error_msg = f"Error processing {os.path.basename(file_path)}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def estimate_key(chroma) -> str:
    """
    Estimate the musical key from chroma features.
    Enhanced version with better heuristics.
    
    Args:
        chroma: Chromagram features
        
    Returns:
        Estimated key (e.g., 'C', 'A minor')
    """
    # Map of keys
    key_labels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Average chroma over time
    avg_chroma = np.mean(chroma, axis=1)
    
    # Cross-correlate with key templates (major and minor)
    # This is a more sophisticated approach than just picking the max energy
    major_template = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
    minor_template = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
    
    major_corr = np.zeros(12)
    minor_corr = np.zeros(12)
    
    # Calculate correlation for each key
    for i in range(12):
        # Rotate the template to each key
        rolled_major = np.roll(major_template, i)
        rolled_minor = np.roll(minor_template, i)
        
        # Calculate correlation
        major_corr[i] = np.corrcoef(avg_chroma, rolled_major)[0, 1]
        minor_corr[i] = np.corrcoef(avg_chroma, rolled_minor)[0, 1]
    
    # Get the key with maximum correlation
    max_major_key = np.argmax(major_corr)
    max_minor_key = np.argmax(minor_corr)
    
    # Determine if it's major or minor
    if major_corr[max_major_key] > minor_corr[max_minor_key]:
        return key_labels[max_major_key]
    else:
        return f"{key_labels[max_minor_key]} minor"


def standard_mashup(processed_audio_data: List[Dict[str, Any]], **kwargs) -> np.ndarray:
    """
    Standard mashup generation function.
    
    Args:
        processed_audio_data: List of processed audio data dictionaries
        **kwargs: Additional parameters
        
    Returns:
        Mashup waveform as numpy array
    """
    try:
        # Check if we have any audio data
        if not processed_audio_data:
            raise ValueError("No audio data provided for mashup")
        
        # Find the shortest duration
        min_duration = min(audio.get('duration', 0) for audio in processed_audio_data)
        if min_duration <= 0:
            raise ValueError("Invalid audio duration detected")
        
        # Get sample rate from first track (try both sr and sample_rate keys)
        first_audio = processed_audio_data[0]
        if 'sr' in first_audio:
            sr = first_audio['sr']
        elif 'sample_rate' in first_audio:
            sr = first_audio['sample_rate']
        else:
            sr = 44100  # Default
            logger.warning("No sample rate found in audio data, using default 44100Hz")
            
        if sr <= 0:
            raise ValueError(f"Invalid sample rate detected: {sr}")
        
        # Calculate output length in samples
        length = int(min_duration * sr)
        if length <= 0:
            raise ValueError(f"Invalid output length calculated: {length}")
        
        logger.info(f"Creating mashup with length {min_duration:.2f} seconds at {sr}Hz")
        
        # Initialize output array
        output = np.zeros(length)
        
        # Blend audio from each track
        for i, audio in enumerate(processed_audio_data):
            # Get the blend ratio for this track
            ratio = audio.get('blend_ratio', 1.0)
            
            # Get the waveform
            waveform = audio.get('waveform', None)
            if waveform is None or len(waveform) == 0:
                logger.warning(f"Empty waveform for track {i+1}, skipping")
                continue
            
            logger.info(f"Blending track {i+1} with ratio {ratio:.2f}")
            
            # Make sure waveform is not longer than the output
            if len(waveform) > length:
                waveform = waveform[:length]
            elif len(waveform) < length:
                # Pad with zeros if shorter
                waveform = np.pad(waveform, (0, length - len(waveform)))
            
            # Add to output with blending ratio
            output += waveform * ratio
        
        # Check if output has any sound
        if np.all(output == 0):
            raise ValueError("Generated mashup is silent - no audio data was successfully blended")
            
        # Check for clipping and prevent it
        if np.max(np.abs(output)) > 1.0:
            logger.warning("Clipping detected in output, normalizing")
        
        # Normalize output
        output = librosa.util.normalize(output)
        
        return output
    except Exception as e:
        logger.error(f"Error in standard mashup: {str(e)}")
        raise ValueError(f"Failed to create standard mashup: {str(e)}")


def enhanced_separate(waveform, sr, **kwargs):
    """
    This function has been moved to the integration module and is now imported as:
    from ..models.enhanced.integration import separate_stems as enhanced_separate
    
    It now uses Demucs for high-quality audio source separation.
    """
    # Importing the actual implementation to avoid breaking existing code
    from ..models.enhanced.integration import separate_stems
    return separate_stems(waveform, sr, **kwargs) 