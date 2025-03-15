"""
Demucs integration module for enhanced audio source separation.
This module provides high-quality isolation of vocals, bass, drums, and other instruments.
"""

import os
import torch
import numpy as np
import logging
from pathlib import Path
import tempfile

# Configure logger
logger = logging.getLogger(__name__)

try:
    # Import Demucs components
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    import torchaudio
    
    DEMUCS_AVAILABLE = True
    logger.info("Demucs model successfully loaded")
except ImportError as e:
    DEMUCS_AVAILABLE = False
    logger.warning(f"Demucs model could not be loaded: {e}")


class DemucsProcessor:
    """
    Handles audio source separation using Facebook's Demucs model.
    Separates audio into vocals, drums, bass, and other stems.
    """
    
    def __init__(self, model_name="htdemucs"):
        """
        Initialize the Demucs processor with the specified model.
        
        Args:
            model_name (str): Name of the Demucs model to use.
                Possible values: "htdemucs" (default), "htdemucs_ft", "mdx_extra", etc.
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        
        if DEMUCS_AVAILABLE:
            try:
                logger.info(f"Loading Demucs model {model_name} on {self.device}")
                self.model = get_model(self.model_name)
                self.model.to(self.device)
                logger.info("Demucs model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Demucs model: {e}")
                self.model = None
    
    def separate_stems(self, audio, sr):
        """
        Separate audio into individual stems (vocals, drums, bass, other).
        
        Args:
            audio (numpy.ndarray): Audio waveform (mono or stereo)
            sr (int): Sample rate of the audio
            
        Returns:
            dict: Dictionary containing separated stems as numpy arrays
                 Keys: 'vocals', 'drums', 'bass', 'other'
        """
        if not DEMUCS_AVAILABLE or self.model is None:
            logger.warning("Demucs not available, returning original audio in all stems")
            # Return original audio for all stems if Demucs is not available
            stems = {
                'vocals': audio.copy(),
                'drums': audio.copy(),
                'bass': audio.copy(),
                'other': audio.copy()
            }
            return stems
        
        try:
            # Convert to the format expected by Demucs
            if len(audio.shape) == 1:  # Mono audio
                audio_tensor = torch.tensor(audio).unsqueeze(0).unsqueeze(0)  # [1, 1, samples]
            else:  # Stereo audio
                audio_tensor = torch.tensor(audio.T).unsqueeze(0)  # [1, channels, samples]
            
            # Move to appropriate device
            audio_tensor = audio_tensor.to(self.device)
            
            # Process with Demucs
            logger.info("Starting stem separation with Demucs")
            with torch.no_grad():
                separated = self.model.forward(audio_tensor)
            
            # Get stem names from model
            stem_names = self.model.sources
            
            # Convert back to numpy arrays
            stems = {}
            for i, name in enumerate(stem_names):
                stem_data = separated[0, i].cpu().numpy()
                if len(audio.shape) == 1:  # If input was mono
                    stem_data = stem_data.squeeze()
                else:  # If input was stereo, transpose back
                    stem_data = stem_data.T
                stems[name] = stem_data
            
            logger.info(f"Successfully separated into {len(stems)} stems: {', '.join(stems.keys())}")
            return stems
            
        except Exception as e:
            logger.error(f"Error during stem separation: {e}")
            # Fall back to original audio
            stems = {
                'vocals': audio.copy(),
                'drums': audio.copy(),
                'bass': audio.copy(),
                'other': audio.copy()
            }
            return stems
    
    def apply_stem_config(self, stems, stems_config, original_audio=None):
        """
        Apply stem configuration to control which stems are included in the output.
        
        Args:
            stems (dict): Dictionary of separated stems
            stems_config (dict): Configuration specifying which stems to include
                Example: {'vocals': True, 'drums': True, 'bass': True, 'other': False}
            original_audio (numpy.ndarray, optional): Original audio to fall back to
            
        Returns:
            numpy.ndarray: Combined audio based on stem configuration
        """
        try:
            # If no stems available, return original audio
            if not stems or len(stems) == 0:
                logger.warning("No stems available for configuration, returning original audio")
                return original_audio if original_audio is not None else np.zeros_like(next(iter(stems.values())))
            
            # Get a reference stem to determine audio shape
            ref_stem = next(iter(stems.values()))
            
            # Initialize output array with zeros
            output = np.zeros_like(ref_stem)
            
            # Add each enabled stem
            for stem_name, include in stems_config.items():
                if include and stem_name in stems:
                    output += stems[stem_name]
            
            logger.info(f"Applied stem configuration: {stems_config}")
            return output
            
        except Exception as e:
            logger.error(f"Error applying stem configuration: {e}")
            return original_audio if original_audio is not None else next(iter(stems.values()))
    
    def adjust_stem_levels(self, stems, levels):
        """
        Adjust the levels (volume) of each stem.
        
        Args:
            stems (dict): Dictionary of separated stems
            levels (dict): Level adjustments for each stem (values typically 0-2)
                Example: {'vocals': 1.2, 'drums': 0.8, 'bass': 1.5, 'other': 0.6}
                
        Returns:
            dict: Dictionary of stems with adjusted levels
        """
        try:
            adjusted_stems = {}
            for stem_name, stem_audio in stems.items():
                if stem_name in levels:
                    # Apply the level adjustment
                    adjusted_stems[stem_name] = stem_audio * levels.get(stem_name, 1.0)
                else:
                    # Keep original if no adjustment specified
                    adjusted_stems[stem_name] = stem_audio
            
            logger.info(f"Applied stem level adjustments: {levels}")
            return adjusted_stems
            
        except Exception as e:
            logger.error(f"Error adjusting stem levels: {e}")
            return stems

# Example usage
if __name__ == "__main__":
    # Simple test
    import librosa
    
    audio, sr = librosa.load("test.mp3", sr=None)
    
    processor = DemucsProcessor()
    stems = processor.separate_stems(audio, sr)
    
    # Apply stem configuration
    stems_config = {'vocals': True, 'drums': True, 'bass': True, 'other': False}
    result = processor.apply_stem_config(stems, stems_config)
    
    # Apply level adjustments
    levels = {'vocals': 1.2, 'drums': 0.8, 'bass': 1.5, 'other': 0.6}
    adjusted_stems = processor.adjust_stem_levels(stems, levels) 