"""
Integration module to incorporate enhanced AI models into the existing workflow.
This module provides adapter functions to use the enhanced models with minimal changes to the existing code.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the enhanced models
try:
    from song_mashup.models.enhanced.audio_model_enhanced import (
        EnhancedMusicBERTAnalyzer,
        EnhancedSeparator,
        EnhancedMashupGenerator
    )
    ENHANCED_MODELS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced models could not be imported: {e}")
    logger.warning("Falling back to standard models")
    ENHANCED_MODELS_AVAILABLE = False

# Import the base models as fallback
try:
    from song_mashup.models.audio_model import (
        MusicBERTAnalyzer,
        BarkGenerator,
        blend_with_ai
    )
    BASE_MODELS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Base models could not be imported: {e}")
    BASE_MODELS_AVAILABLE = False

# Import demucs processor for stem separation
try:
    from .demucs_integration import DemucsProcessor
    demucs_processor = DemucsProcessor()
    DEMUCS_AVAILABLE = True
except ImportError:
    DEMUCS_AVAILABLE = False


class ModelManager:
    """
    Manages model selection and provides a unified interface.
    Automatically selects enhanced models if available, with fallback to base models.
    """
    
    def __init__(self, force_base_models: bool = False):
        """
        Initialize the model manager.
        
        Args:
            force_base_models: If True, use base models even if enhanced are available
        """
        self.use_enhanced = ENHANCED_MODELS_AVAILABLE and not force_base_models
        
        if self.use_enhanced:
            logger.info("Using enhanced AI models for audio processing")
            self.music_analyzer = EnhancedMusicBERTAnalyzer()
            self.mashup_generator = EnhancedMashupGenerator()
            self.separator = EnhancedSeparator()
        elif BASE_MODELS_AVAILABLE:
            logger.info("Using base AI models for audio processing")
            self.music_analyzer = MusicBERTAnalyzer()
            # No direct equivalent for these in base models
            self.mashup_generator = None
            self.separator = None
        else:
            logger.error("Neither enhanced nor base models are available")
            raise ImportError("Required audio models are not available")

    def analyze_audio(self, audio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze audio data using the appropriate model.
        
        Args:
            audio_data: Dictionary containing audio data
            
        Returns:
            Dictionary with analysis results
        """
        if self.use_enhanced:
            return self.music_analyzer.analyze(audio_data)
        else:
            return self.music_analyzer.analyze(audio_data)
    
    def generate_mashup(self, audio_tracks: List[Dict], blend_ratios: List[float]) -> np.ndarray:
        """
        Generate a mashup using the appropriate model.
        
        Args:
            audio_tracks: List of dictionaries with audio data
            blend_ratios: List of blend ratios for each track
            
        Returns:
            Mashup waveform
        """
        if self.use_enhanced and self.mashup_generator is not None:
            return self.mashup_generator.generate_mashup(audio_tracks, blend_ratios)
        else:
            # Fall back to the base blend_with_ai function
            if BASE_MODELS_AVAILABLE:
                return blend_with_ai(audio_tracks, blend_ratios)
            else:
                raise RuntimeError("No mashup generation model available")
    
    def separate_stems(self, audio_data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Separate audio into stems using the appropriate model.
        
        Args:
            audio_data: Dictionary containing audio data
            
        Returns:
            Dictionary containing separated stems
        """
        if self.use_enhanced and self.separator is not None:
            return self.separator.separate_stems(
                audio_data['waveform'], 
                audio_data['sample_rate']
            )
        else:
            # Basic fallback implementation
            waveform = audio_data['waveform']
            # Low-pass filter for bass
            bass = np.zeros_like(waveform)
            # High-pass filter for vocals
            vocals = np.zeros_like(waveform)
            # Mid-range for drums (simplified)
            drums = np.zeros_like(waveform)
            # Other is what's left
            other = waveform
            
            return {
                'vocals': vocals,
                'drums': drums,
                'bass': bass,
                'other': other
            }


# Singleton instance for convenience
model_manager = ModelManager()

# Convenience functions that use the model manager
def analyze_audio(audio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze audio data using the best available model.
    
    Args:
        audio_data: Dictionary containing audio data
        
    Returns:
        Dictionary with analysis results
    """
    return model_manager.analyze_audio(audio_data)

def generate_mashup(audio_tracks: List[Dict], blend_ratios: List[float]) -> np.ndarray:
    """
    Generate a mashup using the best available model.
    
    Args:
        audio_tracks: List of dictionaries with audio data
        blend_ratios: List of blend ratios for each track
        
    Returns:
        Mashup waveform
    """
    return model_manager.generate_mashup(audio_tracks, blend_ratios)

def separate_stems(waveform, sr, **kwargs):
    """
    Separate audio into stems using Demucs if available.
    Falls back to other methods if not available.
    
    Args:
        waveform: Audio waveform (numpy array)
        sr: Sample rate
        **kwargs: Additional parameters 
                 (vocal_prominence, drum_prominence, bass_prominence, etc.)
    
    Returns:
        Dictionary containing separated stems (vocals, drums, bass, other)
    """
    try:
        if DEMUCS_AVAILABLE:
            # Use Demucs for high-quality stem separation
            logger.info("Using Demucs for high-quality stem separation")
            
            # Extract prominence parameters for adjusting stem levels
            vocal_prominence = kwargs.get("vocal_prominence", 1.0)
            drum_prominence = kwargs.get("drum_prominence", 1.0)
            bass_prominence = kwargs.get("bass_prominence", 1.0)
            other_prominence = kwargs.get("other_prominence", 1.0)
            
            # Separate stems
            stems = demucs_processor.separate_stems(waveform, sr)
            
            # Adjust stem levels based on prominence parameters
            levels = {
                'vocals': vocal_prominence,
                'drums': drum_prominence,
                'bass': bass_prominence,
                'other': other_prominence
            }
            
            adjusted_stems = demucs_processor.adjust_stem_levels(stems, levels)
            logger.info(f"Successfully separated stems with Demucs")
            
            return adjusted_stems
        else:
            # Fall back to the model manager for separation
            logger.info("Demucs not available, falling back to model manager for separation")
            audio_data = {'waveform': waveform, 'sample_rate': sr}
            return model_manager.separate_stems(audio_data)
    except Exception as e:
        logger.error(f"Error in stem separation: {str(e)}")
        # Return dummy stems as fallback
        return {
            'vocals': waveform.copy(),
            'drums': waveform.copy(),
            'bass': waveform.copy(),
            'other': waveform.copy()
        } 