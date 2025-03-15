"""
Core processing module for audio analysis and mashup generation.
"""

import os
import time
import numpy as np
import librosa
import soundfile as sf
from typing import List, Dict, Tuple, Optional
import torch
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor

# Path to the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def process_files_async(job_id: str, file_paths: List[str], blend_ratios: List[float]):
    """
    Asynchronous wrapper for processing audio files and generating mashup.
    
    Args:
        job_id: Unique identifier for the job
        file_paths: List of paths to audio files
        blend_ratios: List of blending ratios for each file
    """
    # Run the processing in a separate thread to avoid blocking
    with ThreadPoolExecutor() as executor:
        executor.submit(
            process_files,
            job_id=job_id,
            file_paths=file_paths,
            blend_ratios=blend_ratios
        )


def process_files(job_id: str, file_paths: List[str], blend_ratios: List[float]):
    """
    Process audio files and generate a mashup.
    
    Args:
        job_id: Unique identifier for the job
        file_paths: List of paths to audio files
        blend_ratios: List of blending ratios for each file
    """
    try:
        # Normalize ratios if necessary
        if sum(blend_ratios) != len(blend_ratios):
            total = sum(blend_ratios)
            blend_ratios = [r / total * len(blend_ratios) for r in blend_ratios]
        
        # 1. Load and analyze audio files
        audio_data = []
        for file_path, ratio in zip(file_paths, blend_ratios):
            audio = load_and_analyze_audio(file_path)
            audio['blend_ratio'] = ratio
            audio_data.append(audio)
        
        # 2. Separate stems using Demucs (vocal, drums, bass, other)
        stems = separate_stems(audio_data)
        
        # 3. Align tempos and keys
        aligned_audio = align_audio(audio_data)
        
        # 4. Generate mashup
        mashup = generate_mashup(aligned_audio, stems, blend_ratios)
        
        # 5. Save output
        output_path = os.path.join(BASE_DIR, "song_mashup", "data", "mashups", f"{job_id}.mp3")
        mashup.export(output_path, format="mp3")
        
    except Exception as e:
        # Log the error
        print(f"Error processing job {job_id}: {str(e)}")
        # Create an error file for debugging
        with open(os.path.join(BASE_DIR, "song_mashup", "data", "mashups", f"{job_id}_error.txt"), "w") as f:
            f.write(str(e))


def load_and_analyze_audio(file_path: str) -> Dict:
    """
    Load audio file and analyze its properties.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary containing audio data and analysis
    """
    # Load audio file
    y, sr = librosa.load(file_path, sr=None)
    
    # Basic analysis
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key = estimate_key(chroma)
    
    # Extract features with STFT
    stft = np.abs(librosa.stft(y))
    
    # Store in a dictionary
    return {
        'file_path': file_path,
        'waveform': y,
        'sample_rate': sr,
        'tempo': tempo,
        'key': key,
        'stft': stft,
        'duration': len(y) / sr
    }


def estimate_key(chroma) -> str:
    """
    Estimate the musical key from chroma features.
    
    Args:
        chroma: Chromagram features
        
    Returns:
        Estimated key (e.g., 'C', 'A minor')
    """
    # Map of keys
    key_labels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Average chroma over time
    avg_chroma = np.mean(chroma, axis=1)
    
    # Get key with max energy
    key_idx = np.argmax(avg_chroma)
    
    # Simple algorithm to determine if it's major or minor
    # (Real implementation would be more sophisticated)
    relative_minor_idx = (key_idx + 9) % 12
    if avg_chroma[relative_minor_idx] > 0.8 * avg_chroma[key_idx]:
        return f"{key_labels[relative_minor_idx]} minor"
    
    return key_labels[key_idx]


def separate_stems(audio_data: List[Dict]) -> Dict:
    """
    Separate the audio tracks into stems using Demucs.
    
    Args:
        audio_data: List of audio data dictionaries
        
    Returns:
        Dictionary containing separated stems for each track
    """
    # For a real implementation, we would use Demucs here.
    # For this example, we'll use a simple placeholder
    stems = {}
    
    for i, audio in enumerate(audio_data):
        # Simulate stem separation with simple filtering
        # In real implementation, this would use the Demucs model
        waveform = audio['waveform']
        sr = audio['sample_rate']
        
        # Create fake stems using basic filtering
        # Low-pass filter for bass
        bass = librosa.effects.preemphasis(waveform, coef=0.95)
        # High-pass filter for vocals
        vocals = waveform - librosa.effects.preemphasis(waveform, coef=0.95)
        # Mid-range for drums (simplified)
        drums = waveform - bass - vocals
        # Other is what's left
        other = waveform - bass - vocals - drums
        
        stems[i] = {
            'vocals': vocals,
            'drums': drums,
            'bass': bass,
            'other': other,
            'sample_rate': sr
        }
    
    return stems


def align_audio(audio_data: List[Dict]) -> List[Dict]:
    """
    Align multiple audio tracks in tempo and key.
    
    Args:
        audio_data: List of audio data dictionaries
        
    Returns:
        List of aligned audio data dictionaries
    """
    # For simplicity, we'll use the first track as reference
    reference = audio_data[0]
    ref_tempo = reference['tempo']
    ref_key = reference['key']
    
    aligned_data = []
    for audio in audio_data:
        # Make a copy to avoid modifying the original
        aligned = audio.copy()
        
        # Adjust tempo if needed
        if abs(audio['tempo'] - ref_tempo) > 1.0:
            # Calculate stretch factor
            stretch_factor = ref_tempo / audio['tempo']
            # Time stretch audio
            aligned['waveform'] = librosa.effects.time_stretch(audio['waveform'], rate=stretch_factor)
            aligned['tempo'] = ref_tempo
        
        # Transpose to match key if needed
        if audio['key'] != ref_key:
            # Placeholder for key shifting
            # In a real implementation, we would use more sophisticated methods
            # to shift the key while preserving audio quality
            pass
        
        aligned_data.append(aligned)
    
    return aligned_data


def generate_mashup(aligned_audio: List[Dict], stems: Dict, blend_ratios: List[float]) -> AudioSegment:
    """
    Generate a mashup from the aligned audio tracks.
    
    Args:
        aligned_audio: List of aligned audio data
        stems: Dictionary of stems for each track
        blend_ratios: List of blending ratios
        
    Returns:
        AudioSegment containing the generated mashup
    """
    # Find the shortest duration
    min_duration = min(audio['duration'] for audio in aligned_audio)
    
    # Initialize output arrays for each stem type
    sr = aligned_audio[0]['sample_rate']
    length = int(min_duration * sr)
    
    # Initialize output arrays
    vocals_out = np.zeros(length)
    drums_out = np.zeros(length)
    bass_out = np.zeros(length)
    other_out = np.zeros(length)
    
    # Blend stems from each track
    for i, audio in enumerate(aligned_audio):
        ratio = audio['blend_ratio']
        
        # Get stems for this track
        track_stems = stems[i]
        
        # Truncate stems to the minimum duration
        vocals = track_stems['vocals'][:length]
        drums = track_stems['drums'][:length]
        bass = track_stems['bass'][:length]
        other = track_stems['other'][:length]
        
        # Add to output stems with blending ratio
        vocals_out += vocals * ratio
        
        # For drums, prioritize the track with the clearest beat
        if i == np.argmax([audio['blend_ratio'] for audio in aligned_audio]):
            drums_out = drums  # Use drums from the dominant track
        else:
            drums_out += drums * 0.3 * ratio  # Add a bit from other tracks
        
        # For bass, use the track with the best bass line
        if i == 0:  # Assuming first track has the best bass (simple heuristic)
            bass_out = bass
        else:
            bass_out += bass * 0.2 * ratio
        
        # Blend other elements
        other_out += other * ratio
    
    # Combine all stems
    mashup_waveform = vocals_out + drums_out + bass_out + other_out
    
    # Normalize
    mashup_waveform = librosa.util.normalize(mashup_waveform)
    
    # Convert to 16-bit PCM
    mashup_waveform = (mashup_waveform * 32767).astype(np.int16)
    
    # Save to temporary file
    temp_path = os.path.join(BASE_DIR, "song_mashup", "data", "temp_mashup.wav")
    sf.write(temp_path, mashup_waveform, sr)
    
    # Convert to AudioSegment for export
    mashup = AudioSegment.from_file(temp_path)
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return mashup 