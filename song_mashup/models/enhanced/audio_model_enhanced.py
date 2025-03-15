"""
Enhanced AI models for audio analysis and generation.
Extends the base audio_model.py with improved capabilities:
1. Better audio feature extraction
2. More sophisticated track blending algorithms
3. Improved tempo and key alignment
"""

import os
import numpy as np
import torch
import librosa
from typing import Dict, List, Optional, Tuple, Union, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import base models to extend
try:
    from song_mashup.models.audio_model import MusicBERTAnalyzer, BarkGenerator, blend_with_ai
    BASE_MODELS_AVAILABLE = True
except ImportError:
    logger.warning("Base audio models could not be imported. Some functionality may be limited.")
    BASE_MODELS_AVAILABLE = False

# Optional advanced libraries
try:
    import librosa.decompose
    DECOMPOSE_AVAILABLE = True
except ImportError:
    DECOMPOSE_AVAILABLE = False

try:
    from sklearn.decomposition import NMF
    NMF_AVAILABLE = True
except ImportError:
    NMF_AVAILABLE = False


class EnhancedMusicBERTAnalyzer:
    """
    Enhanced wrapper for MusicBERT with better feature extraction.
    """
    
    def __init__(self, model_path: Optional[str] = None, use_base_model: bool = True):
        """
        Initialize the enhanced MusicBERT analyzer.
        
        Args:
            model_path: Path to a pre-trained MusicBERT model, or None to use default
            use_base_model: Whether to use the base MusicBERT model as fallback
        """
        self.use_base_model = use_base_model and BASE_MODELS_AVAILABLE
        
        if self.use_base_model:
            try:
                self.base_analyzer = MusicBERTAnalyzer(model_path)
                logger.info("Base MusicBERT analyzer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize base MusicBERT analyzer: {e}")
                self.use_base_model = False
        
        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
    
    def extract_chromagram(self, waveform: np.ndarray, sr: int) -> np.ndarray:
        """
        Extract enhanced chromagram features from audio.
        
        Args:
            waveform: Audio waveform
            sr: Sample rate
            
        Returns:
            Chromagram features
        """
        # Use higher resolution chroma features
        hop_length = 512
        n_chroma = 24  # Higher resolution (standard is 12)
        
        chromagram = librosa.feature.chroma_cqt(
            y=waveform, 
            sr=sr,
            hop_length=hop_length,
            n_chroma=n_chroma,
            bins_per_octave=n_chroma*3  # Higher resolution
        )
        
        return chromagram
    
    def extract_melody(self, waveform: np.ndarray, sr: int) -> np.ndarray:
        """
        Extract melody contour from audio.
        
        Args:
            waveform: Audio waveform
            sr: Sample rate
            
        Returns:
            Extracted melody contour
        """
        # Extract pitch using CREPE-like approach
        # (simplified for demonstration)
        hop_length = 512
        fmin = librosa.note_to_hz('C2')
        fmax = librosa.note_to_hz('C7')
        
        try:
            # First try to get pitch using PYIN if available
            pitch, magnitudes = librosa.core.piptrack(
                y=waveform, sr=sr, 
                fmin=fmin, fmax=fmax,
                hop_length=hop_length
            )
            
            # Find the most prominent pitches
            pitch_idx = np.argmax(magnitudes, axis=0)
            times = librosa.times_like(pitch_idx, sr=sr, hop_length=hop_length)
            pitches = np.array([pitch[i, t] for i, t in enumerate(pitch_idx)])
            
            # Filter to get the main melody
            pitches = librosa.util.normalize(pitches)
            return pitches
            
        except Exception as e:
            logger.warning(f"Advanced pitch extraction failed: {e}")
            # Fallback to spectrogram-based approach
            S = np.abs(librosa.stft(waveform, hop_length=hop_length))
            melspec = librosa.feature.melspectrogram(S=S, sr=sr)
            return np.mean(melspec, axis=0)
    
    def analyze(self, audio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced audio analysis with more detailed features.
        
        Args:
            audio_data: Dictionary containing audio data
            
        Returns:
            Dictionary with enhanced analysis results
        """
        waveform = audio_data.get('waveform')
        sr = audio_data.get('sample_rate')
        
        if waveform is None or sr is None:
            logger.error("Missing required audio data for analysis")
            return {}
        
        # Basic analysis
        analysis = {}
        
        # Extract enhanced features
        try:
            # Enhanced chroma features
            analysis['chroma'] = self.extract_chromagram(waveform, sr)
            
            # Melody extraction
            analysis['melody'] = self.extract_melody(waveform, sr)
            
            # Rhythm features
            onset_env = librosa.onset.onset_strength(y=waveform, sr=sr)
            tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
            analysis['rhythm'] = tempogram
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=waveform, sr=sr)
            analysis['spectral_contrast'] = contrast
            
            # Use base model for embeddings if available
            if self.use_base_model:
                base_analysis = self.base_analyzer.analyze(audio_data)
                analysis['embeddings'] = base_analysis.get('embeddings')
                analysis['melody_score'] = base_analysis.get('melody_score')
                analysis['harmony_score'] = base_analysis.get('harmony_score')
                analysis['rhythm_score'] = base_analysis.get('rhythm_score')
            else:
                # Fake embeddings as placeholder
                analysis['embeddings'] = np.random.randn(768)
                analysis['melody_score'] = float(np.random.uniform(0.5, 0.9))
                analysis['harmony_score'] = float(np.random.uniform(0.5, 0.9))
                analysis['rhythm_score'] = float(np.random.uniform(0.5, 0.9))
            
            # Musical complexity score (simple heuristic)
            flat_chroma = np.sum(analysis['chroma'], axis=1)
            norm_chroma = flat_chroma / np.sum(flat_chroma)
            entropy = -np.sum(norm_chroma * np.log2(norm_chroma + 1e-10))
            analysis['complexity_score'] = float(entropy / np.log2(len(norm_chroma)))
            
        except Exception as e:
            logger.error(f"Error during enhanced analysis: {e}")
            # Fallback to basic analysis if enhanced fails
            if self.use_base_model:
                analysis = self.base_analyzer.analyze(audio_data)
        
        return analysis


class EnhancedSeparator:
    """
    Enhanced audio source separation using NMF and other techniques.
    """
    
    def __init__(self):
        """Initialize the enhanced separator."""
        self.nmf_available = NMF_AVAILABLE
        self.decompose_available = DECOMPOSE_AVAILABLE
    
    def separate_stems(self, waveform: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """
        Separate audio into stems using advanced techniques.
        
        Args:
            waveform: Audio waveform
            sr: Sample rate
            
        Returns:
            Dictionary containing separated stems
        """
        # Initialize output stems
        stems = {
            'vocals': np.zeros_like(waveform),
            'drums': np.zeros_like(waveform),
            'bass': np.zeros_like(waveform),
            'other': np.zeros_like(waveform)
        }
        
        try:
            # Convert to mono if stereo
            if len(waveform.shape) > 1 and waveform.shape[0] == 2:
                waveform = np.mean(waveform, axis=0)
            
            # Calculate STFT
            D = librosa.stft(waveform)
            S = np.abs(D)
            
            # If NMF is available, use it for better separation
            if self.nmf_available and self.decompose_available:
                # Number of components for each instrument class
                n_components = {
                    'vocals': 2,
                    'drums': 2,
                    'bass': 1,
                    'other': 3
                }
                
                # Use NMF to decompose the spectrogram
                model = NMF(n_components=sum(n_components.values()), random_state=0)
                W = model.fit_transform(S.T)
                H = model.components_
                
                # Reconstruct each component
                start_idx = 0
                for stem_name, n_comp in n_components.items():
                    # Get the components for this stem
                    W_stem = W[:, start_idx:start_idx+n_comp]
                    H_stem = H[start_idx:start_idx+n_comp, :]
                    
                    # Reconstruct the spectrogram for this stem
                    S_stem = np.dot(W_stem, H_stem).T
                    
                    # Convert back to time domain
                    phase = np.angle(D)
                    D_stem = S_stem * np.exp(1j * phase)
                    stems[stem_name] = librosa.istft(D_stem, length=len(waveform))
                    
                    start_idx += n_comp
            else:
                # Fallback to simpler filtering techniques
                # Low-pass filter for bass
                bass = librosa.effects.preemphasis(waveform, coef=0.95)
                # High-pass filter for vocals
                vocals = waveform - librosa.effects.preemphasis(waveform, coef=0.95)
                # Mid-range for drums (simplified)
                drums = waveform - bass - vocals
                # Other is what's left
                other = waveform * 0.3  # Just to have something
                
                stems = {
                    'vocals': vocals,
                    'drums': drums,
                    'bass': bass,
                    'other': other
                }
            
        except Exception as e:
            logger.error(f"Error during stem separation: {e}")
            # Fallback to very basic separation
            stems = {
                'vocals': waveform * 0.4,
                'drums': waveform * 0.3,
                'bass': waveform * 0.2,
                'other': waveform * 0.1
            }
        
        return stems


class EnhancedMashupGenerator:
    """
    Enhanced mashup generation with better blending algorithms.
    """
    
    def __init__(self):
        """Initialize the enhanced mashup generator."""
        self.separator = EnhancedSeparator()
    
    def align_tempo(self, waveform: np.ndarray, sr: int, source_tempo: float, target_tempo: float) -> np.ndarray:
        """
        Align tempo more precisely using phase vocoder.
        
        Args:
            waveform: Audio waveform
            sr: Sample rate
            source_tempo: Source tempo in BPM
            target_tempo: Target tempo in BPM
            
        Returns:
            Tempo-aligned waveform
        """
        if abs(source_tempo - target_tempo) < 1.0:
            return waveform  # No need to adjust
        
        # Calculate stretch ratio
        ratio = target_tempo / source_tempo
        
        try:
            # Time stretch using phase vocoder
            y_stretched = librosa.effects.time_stretch(waveform, rate=ratio)
            return y_stretched
        except Exception as e:
            logger.error(f"Error during tempo alignment: {e}")
            return waveform
    
    def align_key(self, waveform: np.ndarray, sr: int, source_key: str, target_key: str) -> np.ndarray:
        """
        Align key more precisely using pitch shifting.
        
        Args:
            waveform: Audio waveform
            sr: Sample rate
            source_key: Source key (e.g., 'C', 'A minor')
            target_key: Target key (e.g., 'D', 'B minor')
            
        Returns:
            Key-aligned waveform
        """
        if source_key == target_key:
            return waveform  # No need to adjust
        
        # Map keys to semitones
        key_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        
        # Extract base key (ignoring minor/major)
        source_base = source_key.split()[0]
        target_base = target_key.split()[0]
        
        # Check if both keys are in the map
        if source_base not in key_map or target_base not in key_map:
            logger.warning(f"Could not map keys: {source_key} -> {target_key}")
            return waveform
        
        # Calculate semitone shift
        shift = key_map[target_base] - key_map[source_base]
        
        # Adjust for octave
        if shift > 6:
            shift -= 12
        elif shift < -6:
            shift += 12
        
        try:
            # Use pitch shifting
            y_shifted = librosa.effects.pitch_shift(waveform, sr=sr, n_steps=shift)
            return y_shifted
        except Exception as e:
            logger.error(f"Error during key alignment: {e}")
            return waveform
    
    def generate_mashup(self, audio_tracks: List[Dict], blend_ratios: List[float]) -> np.ndarray:
        """
        Generate an enhanced mashup with better blending.
        
        Args:
            audio_tracks: List of dictionaries with audio data
            blend_ratios: List of blend ratios for each track
            
        Returns:
            Mashup waveform
        """
        if not audio_tracks or len(audio_tracks) < 2:
            logger.error("Need at least 2 tracks for mashup")
            return np.array([])
        
        # Use the first track as reference
        reference = audio_tracks[0]
        ref_sr = reference['sample_rate']
        ref_tempo = reference['tempo']
        ref_key = reference['key']
        
        # Process each track
        stems_list = []
        for track in audio_tracks:
            waveform = track['waveform']
            sr = track['sample_rate']
            
            # Resample if needed
            if sr != ref_sr:
                waveform = librosa.resample(waveform, orig_sr=sr, target_sr=ref_sr)
            
            # Align tempo
            waveform = self.align_tempo(waveform, ref_sr, track['tempo'], ref_tempo)
            
            # Align key
            waveform = self.align_key(waveform, ref_sr, track['key'], ref_key)
            
            # Separate stems
            stems = self.separator.separate_stems(waveform, ref_sr)
            stems_list.append(stems)
        
        # Initialize output buffers for each stem type
        min_length = min(len(stems['vocals']) for stems in stems_list)
        vocals_out = np.zeros(min_length)
        drums_out = np.zeros(min_length)
        bass_out = np.zeros(min_length)
        other_out = np.zeros(min_length)
        
        # Blend stems with adaptive mixing
        for i, (stems, ratio) in enumerate(zip(stems_list, blend_ratios)):
            # Normalize ratio
            normalized_ratio = ratio / sum(blend_ratios)
            
            # Truncate stems to minimum length
            vocals = stems['vocals'][:min_length]
            drums = stems['drums'][:min_length]
            bass = stems['bass'][:min_length]
            other = stems['other'][:min_length]
            
            # Apply different mixing strategies for different stem types
            
            # For vocals, crossfade between tracks
            if i == 0:
                vocals_out = vocals * normalized_ratio * 1.2  # Boost primary vocals
            else:
                # Slightly reduce other vocals and apply envelope
                env = np.linspace(0.3, 0.7, len(vocals_out))
                vocals_out += vocals * normalized_ratio * 0.8 * env
            
            # For drums, prioritize the track with the clearest beat
            if i == np.argmax(blend_ratios):
                drums_out = drums  # Use drums from the dominant track
            else:
                drums_out += drums * 0.3 * normalized_ratio
            
            # For bass, use the track with the lowest registered frequency content
            if i == 0:  # Assuming first track has the best bass
                bass_out = bass
            else:
                # Apply low-shelf EQ (simplified)
                bass_out += bass * 0.2 * normalized_ratio
            
            # Blend other elements with crossfading
            other_out += other * normalized_ratio
        
        # Apply global effects
        mashup = vocals_out + drums_out + bass_out + other_out
        
        # Normalization
        mashup = librosa.util.normalize(mashup)
        
        # Apply subtle compression (simplified)
        threshold = 0.5
        ratio = 3.0
        attack = 0.01
        release = 0.2
        
        # Simple compressor implementation
        def compress(x, threshold, ratio, attack, release):
            # Envelope follower
            env = np.zeros_like(x)
            for i in range(1, len(x)):
                if abs(x[i]) > env[i-1]:
                    env[i] = env[i-1] + attack * (abs(x[i]) - env[i-1])
                else:
                    env[i] = env[i-1] + release * (abs(x[i]) - env[i-1])
            
            # Gain computation
            gain = np.ones_like(x)
            mask = env > threshold
            gain[mask] = 1.0 + (1.0/ratio - 1.0) * (env[mask] - threshold) / (1.0 - threshold)
            
            # Apply gain
            return x * gain
        
        mashup = compress(mashup, threshold, ratio, attack, release)
        
        # Final normalization
        mashup = librosa.util.normalize(mashup)
        
        return mashup 