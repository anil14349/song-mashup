"""
Stem-specific audio effects processing module.
Provides functions for applying various audio effects to individual stems (vocals, drums, bass, other).
"""

import numpy as np
import logging
from scipy import signal
from typing import Dict, Any, List, Optional

# Configure logger
logger = logging.getLogger(__name__)

def apply_reverb(audio: np.ndarray, sr: int, amount: float = 0.5, room_size: float = 0.5) -> np.ndarray:
    """
    Apply reverb effect to audio.
    
    Args:
        audio: Audio waveform as numpy array
        sr: Sample rate
        amount: Reverb amount (0.0 to 1.0)
        room_size: Size of the simulated room (0.0 to 1.0)
        
    Returns:
        Processed audio with reverb applied
    """
    if amount <= 0.0:
        return audio
    
    try:
        # Scale parameters
        reverb_length = int(sr * (0.1 + room_size * 2.5))  # 0.1 to 2.6 seconds based on room size
        decay = 0.1 + (1.0 - amount) * 0.8  # Higher values = faster decay
        
        # Create reverb impulse response
        impulse_response = np.zeros(reverb_length)
        
        # Initial spike
        impulse_response[0] = 1.0
        
        # Early reflections (sparse early spikes)
        early_reflection_count = int(5 + room_size * 15)
        for i in range(early_reflection_count):
            position = int((i + 1) * reverb_length / (early_reflection_count * 2))
            impulse_response[position] = 0.5 * np.exp(-i / (early_reflection_count * 0.5))
        
        # Diffuse reverb tail (exponential decay)
        tail_start = int(reverb_length * 0.1)
        for i in range(tail_start, reverb_length):
            relative_pos = (i - tail_start) / (reverb_length - tail_start)
            impulse_response[i] = np.exp(-relative_pos / decay) * amount
        
        # Normalize impulse response
        impulse_response = impulse_response / np.sum(np.abs(impulse_response)) * amount
        
        # Apply convolution reverb
        reverb_signal = signal.fftconvolve(audio, impulse_response, mode='full')[:len(audio)]
        
        # Mix dry/wet signal
        dry_amount = 1.0 - (amount * 0.5)  # Keep more of the dry signal
        processed = audio * dry_amount + reverb_signal * amount
        
        return processed
    
    except Exception as e:
        logger.error(f"Error applying reverb: {str(e)}")
        return audio

def apply_delay(audio: np.ndarray, sr: int, time: float = 0.3, feedback: float = 0.4, mix: float = 0.5) -> np.ndarray:
    """
    Apply delay/echo effect to audio.
    
    Args:
        audio: Audio waveform as numpy array
        sr: Sample rate
        time: Delay time in seconds
        feedback: Feedback amount (0.0 to 0.9)
        mix: Dry/wet mix (0.0 to 1.0)
        
    Returns:
        Processed audio with delay applied
    """
    if mix <= 0.0:
        return audio
    
    try:
        # Ensure feedback doesn't cause infinite loop
        feedback = min(0.9, max(0.0, feedback))
        
        # Calculate delay in samples
        delay_samples = int(time * sr)
        
        # Create output array
        processed = np.copy(audio)
        
        # Apply multi-tap delay with feedback
        delay_line = np.zeros_like(audio)
        delay_line[delay_samples:] = audio[:-delay_samples]
        
        # Initial delay
        processed = processed + delay_line * mix * 0.7
        
        # Additional feedback delays (each quieter than the previous)
        for i in range(1, 5):  # Up to 5 delay repetitions
            scaled_feedback = feedback ** i
            if scaled_feedback < 0.05:  # Stop if feedback gets too quiet
                break
                
            delay_tap = np.zeros_like(audio)
            offset = delay_samples * i
            if offset >= len(audio):
                break
                
            delay_tap[offset:] = audio[:-offset] * scaled_feedback * mix
            processed = processed + delay_tap
        
        # Normalize to prevent clipping
        if np.max(np.abs(processed)) > 1.0:
            processed = processed / np.max(np.abs(processed)) * 0.99
            
        return processed
    
    except Exception as e:
        logger.error(f"Error applying delay: {str(e)}")
        return audio

def apply_eq(audio: np.ndarray, sr: int, low_gain: float = 0.0, mid_gain: float = 0.0, high_gain: float = 0.0) -> np.ndarray:
    """
    Apply 3-band equalizer to audio.
    
    Args:
        audio: Audio waveform as numpy array
        sr: Sample rate
        low_gain: Low frequency gain (-1.0 to 1.0)
        mid_gain: Mid frequency gain (-1.0 to 1.0)
        high_gain: High frequency gain (-1.0 to 1.0)
        
    Returns:
        Processed audio with EQ applied
    """
    try:
        if low_gain == 0.0 and mid_gain == 0.0 and high_gain == 0.0:
            return audio
            
        # Create output array
        processed = np.zeros_like(audio)
        
        # Low band (0 - 250 Hz)
        if low_gain != 0.0:
            nyquist = sr / 2
            cutoff = 250 / nyquist
            b, a = signal.butter(4, cutoff, btype='lowpass')
            low_band = signal.filtfilt(b, a, audio)
            gain_factor = 1.0 + low_gain
            processed += low_band * gain_factor
        
        # Mid band (250 Hz - 4000 Hz)
        if mid_gain != 0.0:
            nyquist = sr / 2
            low_cutoff = 250 / nyquist
            high_cutoff = 4000 / nyquist
            b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
            mid_band = signal.filtfilt(b, a, audio)
            gain_factor = 1.0 + mid_gain
            processed += mid_band * gain_factor
        
        # High band (4000+ Hz)
        if high_gain != 0.0:
            nyquist = sr / 2
            cutoff = 4000 / nyquist
            b, a = signal.butter(4, cutoff, btype='highpass')
            high_band = signal.filtfilt(b, a, audio)
            gain_factor = 1.0 + high_gain
            processed += high_band * gain_factor
        
        # Add the bands that weren't modified
        if low_gain == 0.0:
            nyquist = sr / 2
            cutoff = 250 / nyquist
            b, a = signal.butter(4, cutoff, btype='lowpass')
            processed += signal.filtfilt(b, a, audio)
            
        if mid_gain == 0.0:
            nyquist = sr / 2
            low_cutoff = 250 / nyquist
            high_cutoff = 4000 / nyquist
            b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
            processed += signal.filtfilt(b, a, audio)
            
        if high_gain == 0.0:
            nyquist = sr / 2
            cutoff = 4000 / nyquist
            b, a = signal.butter(4, cutoff, btype='highpass')
            processed += signal.filtfilt(b, a, audio)
        
        # Normalize to prevent clipping
        if np.max(np.abs(processed)) > 1.0:
            processed = processed / np.max(np.abs(processed)) * 0.99
            
        return processed
    
    except Exception as e:
        logger.error(f"Error applying EQ: {str(e)}")
        return audio

def apply_compression(audio: np.ndarray, sr: int, threshold: float = -20.0, ratio: float = 4.0, attack: float = 0.01, release: float = 0.1) -> np.ndarray:
    """
    Apply dynamic range compression to audio.
    
    Args:
        audio: Audio waveform as numpy array
        sr: Sample rate
        threshold: Threshold in dB (-60.0 to 0.0)
        ratio: Compression ratio (1.0 to 20.0)
        attack: Attack time in seconds
        release: Release time in seconds
        
    Returns:
        Processed audio with compression applied
    """
    try:
        if ratio <= 1.0:
            return audio
            
        # Convert threshold from dB to linear
        threshold_linear = 10 ** (threshold / 20.0)
        
        # Calculate attack and release coefficients
        attack_coeff = np.exp(-1.0 / (sr * attack))
        release_coeff = np.exp(-1.0 / (sr * release))
        
        # Compute the envelope of the signal
        envelope = np.zeros_like(audio)
        envelope[0] = np.abs(audio[0])
        
        for i in range(1, len(audio)):
            current = np.abs(audio[i])
            if current > envelope[i-1]:
                # Attack phase
                envelope[i] = attack_coeff * envelope[i-1] + (1 - attack_coeff) * current
            else:
                # Release phase
                envelope[i] = release_coeff * envelope[i-1] + (1 - release_coeff) * current
        
        # Compute the gain reduction
        gain_reduction = np.ones_like(envelope)
        mask = envelope > threshold_linear
        
        if np.any(mask):
            # Calculate gain reduction only where the envelope exceeds threshold
            above_threshold = envelope[mask]
            gain_reduction_db = (threshold + ((np.log10(above_threshold) * 20.0) - threshold) / ratio) - (np.log10(above_threshold) * 20.0)
            gain_reduction[mask] = 10 ** (gain_reduction_db / 20.0)
        
        # Apply gain reduction to the audio
        processed = audio * gain_reduction
        
        # Apply makeup gain to bring the level back up
        if np.max(np.abs(processed)) > 0:
            makeup_gain = min(0.99 / np.max(np.abs(processed)), 2.0)  # Limit makeup gain to 2x
            processed = processed * makeup_gain
        
        return processed
    
    except Exception as e:
        logger.error(f"Error applying compression: {str(e)}")
        return audio

def apply_distortion(audio: np.ndarray, amount: float = 0.5, mix: float = 0.5) -> np.ndarray:
    """
    Apply distortion effect to audio.
    
    Args:
        audio: Audio waveform as numpy array
        amount: Distortion amount (0.0 to 1.0)
        mix: Dry/wet mix (0.0 to 1.0)
        
    Returns:
        Processed audio with distortion applied
    """
    if amount <= 0.0 or mix <= 0.0:
        return audio
    
    try:
        # Scale amount to control the distortion intensity
        distortion_gain = 1.0 + amount * 9.0  # 1x to 10x gain
        
        # Apply soft clipping distortion
        distorted = np.tanh(audio * distortion_gain) / np.tanh(distortion_gain)
        
        # Mix dry/wet
        processed = (1.0 - mix) * audio + mix * distorted
        
        return processed
    
    except Exception as e:
        logger.error(f"Error applying distortion: {str(e)}")
        return audio

def apply_all_stem_effects(stems: Dict[str, np.ndarray], sr: int, effects_config: Dict[str, Dict[str, Any]]) -> Dict[str, np.ndarray]:
    """
    Apply configured effects to each stem.
    
    Args:
        stems: Dictionary of stems (vocals, drums, bass, other)
        sr: Sample rate
        effects_config: Configuration of effects to apply to each stem
            Example: {
                'vocals': {
                    'reverb': {'amount': 0.3, 'room_size': 0.5},
                    'eq': {'low_gain': -0.2, 'mid_gain': 0.4, 'high_gain': 0.2},
                    'compression': {'threshold': -20, 'ratio': 4.0},
                    'delay': {'time': 0.2, 'feedback': 0.3, 'mix': 0.2}
                },
                'drums': {
                    'compression': {'threshold': -12, 'ratio': 6.0}
                },
                'bass': {
                    'eq': {'low_gain': 0.3, 'mid_gain': 0.0, 'high_gain': -0.2}
                },
                'other': {
                    'reverb': {'amount': 0.2}
                }
            }
            
    Returns:
        Dictionary of processed stems
    """
    processed_stems = {}
    
    try:
        # Process each stem with its specific effects
        for stem_name, stem_audio in stems.items():
            processed = stem_audio.copy()
            
            # Skip if no effects defined for this stem
            if stem_name not in effects_config:
                processed_stems[stem_name] = processed
                continue
                
            stem_effects = effects_config[stem_name]
            
            # Apply each effect in sequence
            # The order matters: typically EQ -> Compression -> Distortion -> Delay -> Reverb
            
            # 1. Apply EQ
            if 'eq' in stem_effects:
                eq_params = stem_effects['eq']
                processed = apply_eq(
                    processed, 
                    sr,
                    low_gain=eq_params.get('low_gain', 0.0),
                    mid_gain=eq_params.get('mid_gain', 0.0),
                    high_gain=eq_params.get('high_gain', 0.0)
                )
            
            # 2. Apply Compression
            if 'compression' in stem_effects:
                comp_params = stem_effects['compression']
                processed = apply_compression(
                    processed,
                    sr,
                    threshold=comp_params.get('threshold', -20.0),
                    ratio=comp_params.get('ratio', 4.0),
                    attack=comp_params.get('attack', 0.01),
                    release=comp_params.get('release', 0.1)
                )
            
            # 3. Apply Distortion
            if 'distortion' in stem_effects:
                dist_params = stem_effects['distortion']
                processed = apply_distortion(
                    processed,
                    amount=dist_params.get('amount', 0.5),
                    mix=dist_params.get('mix', 0.5)
                )
            
            # 4. Apply Delay
            if 'delay' in stem_effects:
                delay_params = stem_effects['delay']
                processed = apply_delay(
                    processed,
                    sr,
                    time=delay_params.get('time', 0.3),
                    feedback=delay_params.get('feedback', 0.4),
                    mix=delay_params.get('mix', 0.5)
                )
            
            # 5. Apply Reverb
            if 'reverb' in stem_effects:
                reverb_params = stem_effects['reverb']
                processed = apply_reverb(
                    processed,
                    sr,
                    amount=reverb_params.get('amount', 0.5),
                    room_size=reverb_params.get('room_size', 0.5)
                )
            
            # Store the processed stem
            processed_stems[stem_name] = processed
            
        # Return the processed stems
        return processed_stems
        
    except Exception as e:
        logger.error(f"Error applying stem effects: {str(e)}")
        # Return original stems on error
        return stems

def mix_stems(stems: Dict[str, np.ndarray], levels: Dict[str, float] = None) -> np.ndarray:
    """
    Mix stems together with specified levels.
    
    Args:
        stems: Dictionary of stems (vocals, drums, bass, other)
        levels: Optional dictionary of level adjustments for each stem
            Example: {'vocals': 1.2, 'drums': 0.8, 'bass': 1.5, 'other': 0.6}
            
    Returns:
        Mixed audio as a numpy array
    """
    try:
        # Get a reference stem to determine dimensions
        if not stems:
            logger.error("No stems provided for mixing")
            return np.array([])
            
        ref_stem = next(iter(stems.values()))
        output = np.zeros_like(ref_stem)
        
        # Set default levels if none provided
        if levels is None:
            levels = {stem_name: 1.0 for stem_name in stems.keys()}
        
        # Mix each stem with its level
        for stem_name, stem_audio in stems.items():
            level = levels.get(stem_name, 1.0)
            output += stem_audio * level
        
        # Normalize if needed to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 0.99:
            output = output / max_val * 0.99
            
        return output
        
    except Exception as e:
        logger.error(f"Error mixing stems: {str(e)}")
        # Return the first stem as fallback
        if stems:
            return next(iter(stems.values()))
        return np.array([]) 