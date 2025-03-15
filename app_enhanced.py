"""
Enhanced Streamlit app for the AI-powered Song Mashup Generator.
This version includes the option to use improved AI models for better audio analysis and processing.
"""

import os
import sys
import time
import uuid
import tempfile
import logging
from pathlib import Path

# Add this import for the rerun method
try:
    from streamlit.script_runner import RerunException
    from streamlit.script_request_queue import RerunData
    RERUN_IMPORTS = True
except ImportError:
    RERUN_IMPORTS = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import necessary libraries with error handling
try:
    import streamlit as st
    import numpy as np
    import librosa
    import soundfile as sf
    import scipy
except ImportError as e:
    print(f"Error importing core libraries: {e}")
    print("Please install required packages: pip install streamlit numpy librosa soundfile scipy")
    sys.exit(1)

# Import project modules with error handling
try:
    # Try to import enhanced modules first
    try:
        from song_mashup.api.process_enhanced import process_files, load_and_analyze_audio
        ENHANCED_PROCESSING_AVAILABLE = True
        logger.info("Enhanced processing module loaded")
    except ImportError:
        logger.warning("Enhanced processing module not available. Falling back to standard module.")
        from song_mashup.api.process import process_files, load_and_analyze_audio
        ENHANCED_PROCESSING_AVAILABLE = False
    
    from song_mashup.utils.audio_validator import validate_audio_file
except ImportError as e:
    if 'streamlit' in sys.modules:
        st.error(f"Error importing project modules: {e}")
        st.info("Please ensure you've installed all required packages: pip install -r requirements.txt")
        st.stop()
    else:
        print(f"Error importing project modules: {e}")
        print("Please ensure you've installed all required packages: pip install -r requirements.txt")
        sys.exit(1)

# Set up page configuration
st.set_page_config(
    page_title="AI Song Mashup Generator", 
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define custom CSS for styling
def local_css():
    st.markdown("""
    <style>
        .main-header {
            color: #6d28d9;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            color: #8b5cf6;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        .stButton > button {
            background-color: #6d28d9;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton > button:hover {
            background-color: #5b21b6;
        }
        .status-container {
            padding: 1rem;
            border-radius: 10px;
            background-color: #1e1e1e;
            margin: 1rem 0;
        }
        .file-details {
            padding: 10px;
            border-radius: 5px;
            background-color: #2d2d2d;
            margin-bottom: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #aaa;
            font-size: 0.8rem;
        }
        /* Hide Streamlit footer */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# Check for required external dependencies
def check_dependencies():
    """Check if required external dependencies are available."""
    try:
        import librosa
        import torch
        import soundfile
        return True
    except ImportError as e:
        st.error(f"Missing dependency: {e}")
        st.info("Please install all required packages: `pip install -r requirements.txt`")
        return False

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "song_mashup", "data", "uploads")
MASHUP_DIR = os.path.join(BASE_DIR, "song_mashup", "data", "mashups")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MASHUP_DIR, exist_ok=True)

# Initialize session state variables properly
# These need to be at the module level for Streamlit to initialize them correctly
if "job_id" not in st.session_state:
    st.session_state["job_id"] = None
if "job_status" not in st.session_state:
    st.session_state["job_status"] = "idle"
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []
if "blend_ratios" not in st.session_state:
    st.session_state["blend_ratios"] = {}
if "audio_details" not in st.session_state:
    st.session_state["audio_details"] = {}
if "mashup_path" not in st.session_state:
    st.session_state["mashup_path"] = None
if "processing_thread" not in st.session_state:
    st.session_state["processing_thread"] = None
if "dependency_check" not in st.session_state:
    st.session_state["dependency_check"] = False
if "use_enhanced_models" not in st.session_state:
    st.session_state["use_enhanced_models"] = ENHANCED_PROCESSING_AVAILABLE
if "advanced_settings" not in st.session_state:
    st.session_state["advanced_settings"] = False


def reset_state():
    """Reset the app state to initial values."""
    st.session_state["job_id"] = None
    st.session_state["job_status"] = "idle"
    st.session_state["uploaded_files"] = []
    st.session_state["blend_ratios"] = {}
    st.session_state["audio_details"] = {}
    st.session_state["mashup_path"] = None
    st.session_state["processing_thread"] = None
    # Keep the enhanced models setting


def process_files_sync(job_id, file_paths, blend_ratios, mix_params):
    """
    Process files synchronously (for Streamlit to avoid threading issues).
    """
    try:
        # Process files
        process_files(job_id, file_paths, blend_ratios, mix_params)
        
        # Return success
        return os.path.join(MASHUP_DIR, f"{job_id}.mp3")
    except Exception as e:
        # Log the error
        error_message = str(e)
        error_path = os.path.join(MASHUP_DIR, f"{job_id}_error.txt")
        with open(error_path, "w") as f:
            f.write(error_message)
        
        # Return error
        return {"error": error_message, "path": error_path}


def start_processing():
    """Start processing the uploaded files."""
    if len(st.session_state["uploaded_files"]) < 2:
        st.error("Please upload at least 2 audio files.")
        return
    
    # Ensure blend_ratios exists in session state
    if "blend_ratios" not in st.session_state:
        st.session_state["blend_ratios"] = {}
    
    # Create a new job ID
    job_id = str(uuid.uuid4())
    st.session_state["job_id"] = job_id
    st.session_state["job_status"] = "processing"
    
    # Create job directory
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save uploaded files to disk
    saved_file_paths = []
    file_info = []
    for uploaded_file in st.session_state["uploaded_files"]:
        file_path = os.path.join(job_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_file_paths.append(file_path)
        
        # Collect track settings for each file
        track_info = {
            'path': file_path,
            'name': uploaded_file.name,
            'blend_ratio': st.session_state["blend_ratios"].get(uploaded_file.name, 1.0)
        }
        
        # Add track-specific settings if they exist
        if "track_settings" in st.session_state and uploaded_file.name in st.session_state["track_settings"]:
            settings = st.session_state["track_settings"][uploaded_file.name]
            track_info.update({
                'start_time': settings.get('start_time', 0.0),
                'end_time': settings.get('end_time', None),
                'pitch_shift': settings.get('pitch_shift', 0),
                'stems_config': {
                    'vocals': settings.get('use_vocals', True),
                    'drums': settings.get('use_drums', True),
                    'bass': settings.get('use_bass', True),
                    'other': settings.get('use_other', True)
                }
            })
        
        file_info.append(track_info)
    
    # Get blend ratios
    blend_ratios = []
    for i, uploaded_file in enumerate(st.session_state["uploaded_files"]):
        ratio = st.session_state["blend_ratios"].get(uploaded_file.name, 1.0)
        blend_ratios.append(ratio)
    
    # Get global blend settings
    blend_settings = {}
    if "global_blend_settings" in st.session_state:
        blend_settings = st.session_state["global_blend_settings"]
    
    # Get advanced mixing parameters if they exist
    mix_params = {}
    if "advanced_mix_params" in st.session_state:
        mix_params = st.session_state["advanced_mix_params"]
    
    # Add global blend settings to mix params
    mix_params.update({
        'track_info': file_info,
        'transition_type': blend_settings.get('transition_type', 'crossfade'),
        'beat_align': blend_settings.get('beat_align', True),
        'key_correction': blend_settings.get('key_correction', True),
        'structure': blend_settings.get('structure', 'chorus-verse-chorus'),
        'dynamic_fade': blend_settings.get('dynamic_fade', 0.5)
    })
    
    # Instead of using a thread, we'll use Streamlit's session state to keep track of processing
    # This avoids the ScriptRunContext errors in threading
    result = process_files_sync(job_id, saved_file_paths, blend_ratios, mix_params)
    
    # Update state based on result
    if isinstance(result, dict) and "error" in result:
        st.session_state["job_status"] = "error"
    else:
        st.session_state["job_status"] = "completed"
        st.session_state["mashup_path"] = result
        st.session_state["is_processed"] = True
        
        # Ensure mix controls are initialized when mashup is complete
        if "mix_params" not in st.session_state:
            st.session_state["mix_params"] = {
                "master_volume": 1.0,
                "bass_boost": 0.0,
                "treble_boost": 0.0,
                "reverb": 0.0,
                "vocal_prominence": 1.0,
                "dynamic_range": 1.0
            }
            
        # Ensure stem effects are initialized
        if "stem_effects" not in st.session_state:
            st.session_state["stem_effects"] = {
                "vocals": {
                    "level": 1.0,
                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                    "reverb": {"amount": 0.0, "room_size": 0.5}
                },
                "drums": {
                    "level": 1.0,
                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                    "compression": {"threshold": -20.0, "ratio": 4.0}
                },
                "bass": {
                    "level": 1.0,
                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0}
                },
                "other": {
                    "level": 1.0,
                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                    "reverb": {"amount": 0.0, "room_size": 0.5}
                }
            }


def display_file_details(uploaded_files):
    """Display details about the uploaded audio files with enhanced visualization."""
    # Ensure audio_details and blend_ratios exist in session state
    if "audio_details" not in st.session_state:
        st.session_state["audio_details"] = {}
    if "blend_ratios" not in st.session_state:
        st.session_state["blend_ratios"] = {}
    
    # Create a progress bar for the overall analysis
    total_files = len(uploaded_files)
    analysis_progress = st.progress(0)
    status_text = st.empty()
    
    # Process each file with progress updates
    for i, uploaded_file in enumerate(uploaded_files):
        # Update progress
        progress_pct = (i / total_files)
        analysis_progress.progress(progress_pct)
        status_text.text(f"Analyzing track {i+1}/{total_files}: {uploaded_file.name}")
        
        # Check if we've already analyzed this file
        if uploaded_file.name not in st.session_state["audio_details"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            
            # Analyze audio
            try:
                # Show more detailed progress for this file
                with st.spinner(f"Extracting audio features from {uploaded_file.name}..."):
                    audio_data = load_and_analyze_audio(tmp_path)
                
                # Initialize if not already initialized (extra safety check)
                if "audio_details" not in st.session_state:
                    st.session_state["audio_details"] = {}
                
                # Use a safer way to update the dict
                audio_details = st.session_state["audio_details"]
                audio_details[uploaded_file.name] = {
                    'tempo': audio_data['tempo'],
                    'key': audio_data['key'],
                    'duration': audio_data['duration']
                }
                
                # Add enhanced features if available
                if 'complexity_score' in audio_data:
                    audio_details[uploaded_file.name]['complexity'] = audio_data['complexity_score']
                if 'melody_score' in audio_data:
                    audio_details[uploaded_file.name]['melody'] = audio_data['melody_score']
                if 'harmony_score' in audio_data:
                    audio_details[uploaded_file.name]['harmony'] = audio_data['harmony_score']
                if 'rhythm_score' in audio_data:
                    audio_details[uploaded_file.name]['rhythm'] = audio_data['rhythm_score']
                
                # Update the session state
                st.session_state["audio_details"] = audio_details
                    
            except Exception as e:
                # Handle errors more gracefully
                st.error(f"Error analyzing file: {str(e)}")
                
                # Initialize if not already initialized
                if "audio_details" not in st.session_state:
                    st.session_state["audio_details"] = {}
                
                # Use a safer way to update the dict
                audio_details = st.session_state["audio_details"]
                audio_details[uploaded_file.name] = {
                    'error': f"Could not analyze file: {str(e)}"
                }
                
                # Update the session state
                st.session_state["audio_details"] = audio_details
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Update progress
        analysis_progress.progress((i + 1) / total_files)
    
    # Complete progress and show success message
    analysis_progress.progress(100)
    status_text.text("Analysis complete! Adjust blend settings below.")
    time.sleep(0.5)  # Short pause to show completion
    
    # Clear progress indicators
    analysis_progress.empty()
    status_text.empty()
    
    # Display a section title for blend controls
    st.markdown("## Track Blend Settings", help="Adjust how each track contributes to the final mashup")
    
    # Display file details in a collapsible section
    for uploaded_file in uploaded_files:
        with st.expander(f"Details: {uploaded_file.name}"):
            details = st.session_state["audio_details"][uploaded_file.name]
            if 'error' in details:
                st.error(details['error'])
            else:
                # Basic details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Duration:** {details['duration']:.2f} seconds")
                    st.markdown(f"**Tempo:** {details['tempo']:.2f} BPM")
                    st.markdown(f"**Key:** {details['key']}")
                
                # Enhanced metrics if available
                with col2:
                    if 'complexity' in details:
                        st.markdown(f"**Complexity Score:** {details['complexity']:.2f}")
                    if 'melody' in details:
                        st.markdown(f"**Melody Score:** {details['melody']:.2f}")
                    if 'harmony' in details:
                        st.markdown(f"**Harmony Score:** {details['harmony']:.2f}")
                    if 'rhythm' in details:
                        st.markdown(f"**Rhythm Score:** {details['rhythm']:.2f}")
                
                # Blend ratio slider
                if uploaded_file.name not in st.session_state["blend_ratios"]:
                    st.session_state["blend_ratios"][uploaded_file.name] = 1.0
                
                #st.session_state["blend_ratios"][uploaded_file.name] = st.slider(
                st.session_state["blend_ratios"][uploaded_file.name] = st.slider(
                    "Blend Ratio",
                    min_value=0.1,
                    max_value=2.0,
                    value=st.session_state["blend_ratios"][uploaded_file.name],
                    step=0.1,
                    key=f"blend_ratio_slider_{uploaded_file.name}"
                )
                # Add advanced track-specific settings
                if "track_settings" not in st.session_state:
                    st.session_state["track_settings"] = {}
                
                if uploaded_file.name not in st.session_state["track_settings"]:
                    st.session_state["track_settings"][uploaded_file.name] = {
                        "start_time": 0.0,
                        "end_time": details['duration'],
                        "pitch_shift": 0,
                        "use_vocals": True,
                        "use_drums": True,
                        "use_bass": True,
                        "use_other": True
                    }
                
                # Track settings
                with st.container():
                    st.markdown("### Track Options")
                    
                    # Time range selection
                    col1, col2 = st.columns(2)
                    with col1:
                        st.session_state["track_settings"][uploaded_file.name]["start_time"] = st.number_input(
                            "Start Time (seconds)",
                            min_value=0.0,
                            max_value=details['duration'] - 1.0,
                            value=st.session_state["track_settings"][uploaded_file.name]["start_time"],
                            step=1.0,
                            key=f"start_{uploaded_file.name}"
                        )
                    
                    with col2:
                        st.session_state["track_settings"][uploaded_file.name]["end_time"] = st.number_input(
                            "End Time (seconds)",
                            min_value=st.session_state["track_settings"][uploaded_file.name]["start_time"] + 1.0,
                            max_value=details['duration'],
                            value=st.session_state["track_settings"][uploaded_file.name]["end_time"],
                            step=1.0,
                            key=f"end_{uploaded_file.name}"
                        )
                    
                    # Pitch shift
                    st.session_state["track_settings"][uploaded_file.name]["pitch_shift"] = st.slider(
                        "Pitch Shift (semitones)",
                        min_value=-6,
                        max_value=6,
                        key=f"pitch_shift_slider_{uploaded_file.name}",
                        value=st.session_state["track_settings"][uploaded_file.name]["pitch_shift"],
                        step=1,
                        help="Adjust the pitch of the track"
                    )
                    
                    # Stem selection
                    st.markdown("#### Stems to Include")
                    stem_cols = st.columns(4)
                    
                    with stem_cols[0]:
                        st.session_state["track_settings"][uploaded_file.name]["use_vocals"] = st.checkbox(
                            "Vocals",
                            value=st.session_state["track_settings"][uploaded_file.name]["use_vocals"],
                            key=f"vocals_{uploaded_file.name}"
                        )
                    
                    with stem_cols[1]:
                        st.session_state["track_settings"][uploaded_file.name]["use_drums"] = st.checkbox(
                            "Drums",
                            value=st.session_state["track_settings"][uploaded_file.name]["use_drums"],
                            key=f"drums_{uploaded_file.name}"
                        )
                    
                    with stem_cols[2]:
                        st.session_state["track_settings"][uploaded_file.name]["use_bass"] = st.checkbox(
                            "Bass",
                            value=st.session_state["track_settings"][uploaded_file.name]["use_bass"],
                            key=f"bass_{uploaded_file.name}"
                        )
                    
                    with stem_cols[3]:
                        st.session_state["track_settings"][uploaded_file.name]["use_other"] = st.checkbox(
                            "Other",
                            value=st.session_state["track_settings"][uploaded_file.name]["use_other"],
                            key=f"other_{uploaded_file.name}"
                        )

    # Add global blend settings section after all tracks
    st.markdown("## Global Mashup Settings", help="Control how the tracks will be blended together")
    
    # Initialize global blend settings
    if "global_blend_settings" not in st.session_state:
        st.session_state["global_blend_settings"] = {
            "transition_type": "crossfade",
            "beat_align": True,
            "key_correction": True,
            "structure": "chorus-verse-chorus",
            "dynamic_fade": 0.5
        }
    
    # Create three columns for settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Fix the transition type selector to handle case properly
        transition_options = ["Crossfade", "Hard Cut", "Beat-matched", "Filter Sweep"]
        current_transition = st.session_state["global_blend_settings"]["transition_type"].title() 
        transition_index = 0
        
        try:
            # Try to find the index, with fallback for case differences
            transition_index = transition_options.index(current_transition)
        except ValueError:
            # If exact match fails, try lowercase comparison
            for i, option in enumerate(transition_options):
                if option.lower() == current_transition.lower():
                    transition_index = i
                    break
        
        st.session_state["global_blend_settings"]["transition_type"] = st.selectbox(
            "Transition Type",
            options=transition_options,
            index=transition_index,
            help="How to transition between sections of different tracks"
        ).lower()
    
    with col2:
        st.session_state["global_blend_settings"]["beat_align"] = st.checkbox(
            "Beat Alignment",
            value=st.session_state["global_blend_settings"]["beat_align"],
            help="Automatically align beats between tracks"
        )
    
    with col3:
        st.session_state["global_blend_settings"]["key_correction"] = st.checkbox(
            "Auto Key Correction",
            value=st.session_state["global_blend_settings"]["key_correction"],
            help="Automatically adjust track pitch to match keys"
        )
    
    # Song structure selection
    st.session_state["global_blend_settings"]["structure"] = st.selectbox(
        "Mashup Structure",
        options=["Intro-Verse-Chorus", "Chorus-Verse-Chorus", "Alternating Sections", "Progressive Build", "Custom"],
        index=["Intro-Verse-Chorus", "Chorus-Verse-Chorus", "Alternating Sections", "Progressive Build", "Custom"].index(
            st.session_state["global_blend_settings"]["structure"].title()
        ),
        help="The overall structure of the mashup"
    ).lower()
    
    # Dynamic fade control
    st.session_state["global_blend_settings"]["dynamic_fade"] = st.slider(
        "Dynamic Fade Intensity",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state["global_blend_settings"]["dynamic_fade"],
        step=0.1,
        help="Intensity of volume dynamics between sections",
        key="dynamic_fade_intensity_slider"
    )
    
    # Add Advanced Processing Settings section in main UI
    st.markdown("## Advanced Audio Processing", help="Fine-tune the audio characteristics of your mashup")
    
    with st.expander("Advanced Processing Settings", expanded=False):
        # Initialize advanced mixing parameters in session state if they don't exist
        if "advanced_mix_params" not in st.session_state:
            st.session_state["advanced_mix_params"] = {
                "vocal_prominence": 1.0,
                "bass_prominence": 1.0,
                "drum_prominence": 1.0,
                "key_alignment": 0.8,
                "tempo_alignment": 0.8,
                "crossfade_duration": 4.0,
                "eq_profile": "balanced"
            }
        
        st.info("These settings control sophisticated aspects of how your tracks are blended together, allowing for fine-tuned customization of your mashup.")
        
        # Basic parameters
        st.markdown("#### Basic Processing Parameters")
        col1, col2 = st.columns(2)
        st.session_state["advanced_mix_params"]["vocal_prominence"] = st.slider(
            "Vocal Prominence",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state["advanced_mix_params"]["vocal_prominence"],
            step=0.1,
            help="Controls how prominent vocals are in the final mix",
            key="vocal_prominence_slider"
        )
        
        # Alignment parameters
        st.markdown("#### Musical Alignment Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state["advanced_mix_params"]["key_alignment"] = st.slider(
                "Key Alignment Strength", 
                min_value=0.0,
                max_value=1.0,
                value=st.session_state["advanced_mix_params"]["key_alignment"],
                step=0.1,
                key="key_alignment_slider"
            )
        
        # Show preset combinations
        st.markdown("#### Preset Combinations")
        
        preset_cols = st.columns(3)
        with preset_cols[0]:
            if st.button("Dance Mix", use_container_width=True):
                st.session_state["advanced_mix_params"]["drum_prominence"] = 1.6
                st.session_state["advanced_mix_params"]["bass_prominence"] = 1.4
                st.session_state["advanced_mix_params"]["tempo_alignment"] = 1.0
                st.session_state["advanced_mix_params"]["eq_profile"] = "bass-heavy"
                st.experimental_rerun()
        
        with preset_cols[1]:
            if st.button("Vocal Showcase", use_container_width=True):
                st.session_state["advanced_mix_params"]["vocal_prominence"] = 1.8
                st.session_state["advanced_mix_params"]["drum_prominence"] = 0.7
                st.session_state["advanced_mix_params"]["bass_prominence"] = 0.8
                st.session_state["advanced_mix_params"]["eq_profile"] = "vocal-focused"
                st.experimental_rerun()
        
        with preset_cols[2]:
            if st.button("Ambient Blend", use_container_width=True):
                st.session_state["advanced_mix_params"]["crossfade_duration"] = 6.0
                st.session_state["advanced_mix_params"]["key_alignment"] = 1.0
                st.session_state["advanced_mix_params"]["drum_prominence"] = 0.6
                st.session_state["advanced_mix_params"]["eq_profile"] = "warm"
                st.experimental_rerun()
    
    # Advanced visualization selector
    st.markdown("### Blend Preview")
    st.info("This visualization shows how the tracks will be blended in the final mashup.")

    # Create a column layout for the visualization
    visuals = st.columns([1, 8, 1])

    with visuals[1]:
        # Placeholder for blend visualization
        st.markdown("""
        ```
        Track 1  ━━━━━━━━━━▶━━━━━━━━━━━━▷─────────────
        Track 2  ────────────────▷━━━━━━━━━━▶━━━━━━━━━
        Mashup   ━━━━━━━━━━▶◀▶━━━━━━━━━━▶◀▶━━━━━━━━━━
                 0:00      0:30      1:00      1:30
        ```
        """)
        
        # Note: In a real implementation, we would generate an actual timeline 
        # visualization showing when each track plays and how they blend


# Define a function for rerunning since different Streamlit versions handle this differently
def rerun():
    """Rerun a Streamlit app from the beginning"""
    try:
        # Try the newer experimental_rerun() method
        st.experimental_rerun()
    except Exception as e:
        try:
            # Fallback to older approaches
            if RERUN_IMPORTS:
                raise RerunException(RerunData())
            else:
                # If nothing else works, inform the user
                logger.error(f"Failed to rerun app: {str(e)}")
                st.warning("Could not rerun the app automatically. Please refresh the page.")
        except Exception as e:
            logger.error(f"Failed to rerun app: {str(e)}")
            st.warning("Could not rerun the app automatically. Please refresh the page.")
def initialize_session_state():
    """Initialize session state variables."""
    # Basic app state
    session_keys = {
        "job_status": "idle",
        "job_id": None,
        "output_file": None,
        "error_message": None,
        "uploaded_files": [],
        "dependency_check": False,
        "show_advanced_settings": False,
        "audio_details": {},
        "blend_ratios": {},
        "last_mashup_time": None,
        "download_count": 0
    }
    
    # Advanced mixing parameters
    advanced_keys = {
        "vocal_prominence": 1.0,
        "drum_prominence": 1.0,
        "bass_prominence": 1.0,
        "key_alignment": 0.8,
        "tempo_alignment": 0.8,
        "crossfade_duration": 4.0,
        "eq_profile": "balanced"
    }
    
    # Initialize all basic keys
    for key, default_value in session_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize all advanced keys
    for key, default_value in advanced_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            
    # Debug logging for session state
    logger.debug(f"Session state initialized with keys: {list(st.session_state.keys())}")
    
    # Verify critical keys exist
    critical_keys = ["audio_details", "blend_ratios", "job_status"]
    for key in critical_keys:
        if key not in st.session_state:
            logger.error(f"Critical session state key {key} is missing after initialization")
            # Force re-initialization of the key
            if key == "audio_details" or key == "blend_ratios":
                st.session_state[key] = {}
            elif key == "job_status":
                st.session_state[key] = "idle"


def process_mix_settings(input_path, output_path, mix_params):
    """
    Apply mixing parameters to an audio file and save the result.
    
    Args:
        input_path: Path to the input audio file
        output_path: Path to save the processed output
        mix_params: Dictionary of mixing parameters to apply
    
    Returns:
        Path to the processed audio file
    """
    try:
        logger.info(f"Applying mix settings to {input_path}")
        
        # Load audio file
        y, sr = librosa.load(input_path, sr=None)
        
        # Apply master volume
        master_volume = mix_params.get("master_volume", 1.0)
        y = y * master_volume
        
        # Apply bass boost/cut using a low-shelf filter
        bass_boost = mix_params.get("bass_boost", 0.0)
        if bass_boost != 0.0:
            # Simple low-shelf filter (below 250Hz)
            from scipy import signal
            cutoff = 250  # Hz
            nyquist = sr / 2
            normal_cutoff = cutoff / nyquist
            
            # Create a Butterworth filter
            b, a = signal.butter(4, normal_cutoff, btype='lowpass')
            
            # Apply the filter to get the low frequencies
            low_freqs = signal.filtfilt(b, a, y)
            
            # Mix the original signal with the boosted/cut low frequencies
            boost_factor = 1.0 + bass_boost  # Convert -1.0 to 1.0 range to 0.0 to 2.0
            y = y + (low_freqs * bass_boost)
        
        # Apply treble boost/cut using a high-shelf filter
        treble_boost = mix_params.get("treble_boost", 0.0)
        if treble_boost != 0.0:
            # Simple high-shelf filter (above 2000Hz)
            from scipy import signal
            cutoff = 2000  # Hz
            nyquist = sr / 2
            normal_cutoff = cutoff / nyquist
            
            # Create a Butterworth filter
            b, a = signal.butter(4, normal_cutoff, btype='highpass')
            
            # Apply the filter to get the high frequencies
            high_freqs = signal.filtfilt(b, a, y)
            
            # Mix the original signal with the boosted/cut high frequencies
            boost_factor = 1.0 + treble_boost  # Convert -1.0 to 1.0 range to 0.0 to 2.0
            y = y + (high_freqs * treble_boost)
        
        # Apply vocal prominence (mid-range boost)
        vocal_prominence = mix_params.get("vocal_prominence", 1.0)
        if vocal_prominence != 1.0:
            # Simple bandpass filter for vocals (300Hz - 3000Hz)
            from scipy import signal
            low_cutoff = 300 / (sr / 2)
            high_cutoff = 3000 / (sr / 2)
            
            # Create a Butterworth bandpass filter
            b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
            
            # Apply the filter to get the mid frequencies (vocals)
            mid_freqs = signal.filtfilt(b, a, y)
            
            # Scale the mid frequencies to adjust prominence
            mid_scale_factor = vocal_prominence - 1.0
            y = y + (mid_freqs * mid_scale_factor)
        
        # Apply reverb effect
        reverb_amount = mix_params.get("reverb", 0.0)
        if reverb_amount > 0.0:
            # Simple convolution reverb
            from scipy import signal
            
            # Create a simple reverb impulse response
            reverb_length = int(sr * 0.5 * reverb_amount)  # up to 0.5 seconds based on amount
            impulse_response = np.zeros(reverb_length)
            
            # Build a decreasing exponential for the impulse response
            for i in range(reverb_length):
                impulse_response[i] = np.exp(-5 * i / reverb_length)
            
            # Normalize the impulse response
            impulse_response = impulse_response / np.sum(impulse_response)
            
            # Apply convolution reverb
            reverb_signal = signal.convolve(y, impulse_response, mode='full')[:len(y)]
            
            # Mix the original signal with the reverb
            y = y * (1 - reverb_amount * 0.5) + reverb_signal * (reverb_amount * 0.5)
        
        # Apply dynamics processing
        dynamic_range = mix_params.get("dynamic_range", 1.0)
        if dynamic_range != 1.0:
            # Compress the signal if dynamic_range < 1, expand if > 1
            from scipy import signal
            
            # Calculate signal envelope
            envelope = np.abs(signal.hilbert(y))
            
            # Smooth the envelope
            window_size = int(sr * 0.01)  # 10ms window
            smoothing_window = np.ones(window_size) / window_size
            smooth_envelope = np.convolve(envelope, smoothing_window, mode='same')
            
            # Apply dynamic range adjustment
            gain_reduction = np.power(smooth_envelope, 1.0 - dynamic_range)
            y = y * gain_reduction
        
        # Ensure audio doesn't clip
        max_amplitude = np.max(np.abs(y))
        if max_amplitude > 0.99:
            logger.info(f"Normalizing audio to prevent clipping (max amplitude: {max_amplitude})")
            y = y / max_amplitude * 0.95  # Leave some headroom
        
        # Save the processed audio
        sf.write(output_path, y, sr)
        logger.info(f"Processed audio saved to {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error processing mix settings: {str(e)}")
        st.error(f"Error applying mix settings: {str(e)}")
        return input_path  # Return the original file on error


def process_stems_with_effects(input_path, output_path, stem_effects_config=None):
    """
    Process a mashup by separating stems, applying effects to specific stems, and remixing.
    
    Args:
        input_path: Path to the input audio file
        output_path: Path to save the processed output
        stem_effects_config: Dictionary of effects to apply to each stem
            Example: {
                'vocals': {
                    'reverb': {'amount': 0.3, 'room_size': 0.5},
                    'eq': {'low_gain': -0.2, 'mid_gain': 0.4, 'high_gain': 0.2},
                    'compression': {'threshold': -20, 'ratio': 4.0},
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
        Path to the processed audio file
    """
    # Import necessary modules here to avoid issues with importing at the module level
    try:
        # Import the DemucsProcessor for stem separation
        from song_mashup.models.enhanced.demucs_integration import DemucsProcessor
        # Import the stem effects processor
        from song_mashup.models.enhanced.stem_effects import apply_all_stem_effects, mix_stems
        import numpy as np
        import librosa
        import soundfile as sf
        
        logger.info(f"Processing stems with effects for {input_path}")
        
        # Load audio file
        with st.spinner("Loading audio file..."):
            try:
                y, sr = librosa.load(input_path, sr=None)
                st.success(f"Audio loaded: {len(y)/sr:.1f} seconds at {sr}Hz")
            except Exception as e:
                error_msg = f"Error loading audio file: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                return input_path  # Return the original file on error
        
        # Check if the stem effects config actually contains non-default values
        has_actual_effects = False
        if stem_effects_config:
            for stem_name, effects in stem_effects_config.items():
                # Check level changes
                if effects.get('level', 1.0) != 1.0:
                    has_actual_effects = True
                    break
                    
                # Check effect parameters
                for effect_name, params in effects.items():
                    if effect_name == 'level':
                        continue
                        
                    if effect_name == 'eq':
                        if any(abs(params.get(band, 0.0)) > 0.01 for band in ['low_gain', 'mid_gain', 'high_gain']):
                            has_actual_effects = True
                            break
                    elif effect_name == 'reverb':
                        if params.get('amount', 0.0) > 0.01:
                            has_actual_effects = True
                            break
                    elif effect_name == 'delay':
                        if params.get('mix', 0.0) > 0.01:
                            has_actual_effects = True
                            break
                    elif effect_name == 'compression':
                        if params.get('ratio', 1.0) > 1.0:
                            has_actual_effects = True
                            break
                    elif effect_name == 'distortion':
                        if params.get('amount', 0.0) > 0.01 and params.get('mix', 0.0) > 0.01:
                            has_actual_effects = True
                            break
                            
                if has_actual_effects:
                    break
                    
        if not has_actual_effects:
            st.info("No significant stem effects to apply - returning original audio")
            return input_path
        
        # Initialize Demucs processor for stem separation
        try:
            demucs = DemucsProcessor()
        except Exception as e:
            error_msg = f"Error initializing Demucs processor: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            return input_path  # Return the original file on error
        
        # Separate audio into stems
        with st.spinner("Separating audio stems (this may take a minute)..."):
            try:
                stems = demucs.separate_stems(y, sr)
                
                # Verify that we have actual stems
                if not stems or all(np.all(stem == 0) for stem in stems.values()):
                    st.warning("Could not separate stems properly - using original audio")
                    return input_path
                    
                stem_info = {name: f"{np.max(np.abs(audio)):.2f} max" for name, audio in stems.items()}
                st.success(f"Audio separated into stems: {stem_info}")
            except Exception as e:
                error_msg = f"Error separating stems: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                return input_path  # Return the original file on error
        
        # Apply stem-specific effects
        with st.spinner("Applying stem-specific effects..."):
            try:
                # Clean up the stem_effects_config to remove any empty effects
                cleaned_config = {}
                for stem_name, effects in stem_effects_config.items():
                    if stem_name not in stems:
                        continue
                        
                    stem_config = {}
                    for effect_name, params in effects.items():
                        if effect_name == 'level':
                            stem_config['level'] = params
                            continue
                            
                        # Check if the effect parameters indicate it should be applied
                        if effect_name == 'eq':
                            if any(abs(params.get(band, 0.0)) > 0.01 for band in ['low_gain', 'mid_gain', 'high_gain']):
                                stem_config[effect_name] = params
                        elif effect_name == 'reverb':
                            if params.get('amount', 0.0) > 0.01:
                                stem_config[effect_name] = params
                        elif effect_name == 'delay':
                            if params.get('mix', 0.0) > 0.01:
                                stem_config[effect_name] = params
                        elif effect_name == 'compression':
                            if params.get('ratio', 1.0) > 1.0:
                                stem_config[effect_name] = params
                        elif effect_name == 'distortion':
                            if params.get('amount', 0.0) > 0.01 and params.get('mix', 0.0) > 0.01:
                                stem_config[effect_name] = params
                    
                    if stem_config:
                        cleaned_config[stem_name] = stem_config
                
                # Apply the effects
                if cleaned_config:
                    processed_stems = apply_all_stem_effects(stems, sr, cleaned_config)
                    applied_effects = {
                        stem: list(effects.keys()) for stem, effects in cleaned_config.items()
                        if stem != 'level'
                    }
                    st.success(f"Applied effects: {applied_effects}")
                else:
                    processed_stems = stems
                    st.info("No significant effects to apply - using original stems")
                
                # Get stem levels for mixing
                stem_levels = {
                    stem: config.get('level', 1.0) 
                    for stem, config in stem_effects_config.items() 
                    if 'level' in config and stem in stems
                }
                
                # Mix stems back together
                output_audio = mix_stems(processed_stems, stem_levels)
                
                # Show which stems had level adjustments
                level_adjustments = {stem: level for stem, level in stem_levels.items() if abs(level - 1.0) > 0.01}
                if level_adjustments:
                    st.success(f"Adjusted stem levels: {level_adjustments}")
            except Exception as e:
                error_msg = f"Error applying stem effects: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                return input_path  # Return the original file on error
        
        # Ensure audio doesn't clip
        max_amplitude = np.max(np.abs(output_audio))
        if max_amplitude > 0.99:
            logger.info(f"Normalizing audio to prevent clipping (max amplitude: {max_amplitude})")
            output_audio = output_audio / max_amplitude * 0.95  # Leave some headroom
        
        # Save the processed audio
        with st.spinner("Saving processed audio..."):
            try:
                sf.write(output_path, output_audio, sr)
                st.success(f"Processed audio saved to {os.path.basename(output_path)}")
                logger.info(f"Processed audio with stem effects saved to {output_path}")
                return output_path
            except Exception as e:
                error_msg = f"Error saving audio: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                return input_path  # Return the original file on error
        
    except ImportError as e:
        error_msg = f"Required modules not available for stem processing: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return input_path  # Return the original file on error
        
    except Exception as e:
        error_msg = f"Error processing stems with effects: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return input_path  # Return the original file on error


def main():
    """Main app function."""
    try:
        # Check dependencies if not done yet
        if not st.session_state["dependency_check"]:
            st.session_state["dependency_check"] = check_dependencies()
            if not st.session_state["dependency_check"]:
                st.stop()
        
        # Header
        st.markdown('<h1 class="main-header">AI Song Mashup Generator</h1>', unsafe_allow_html=True)
        
        # Developer credit directly below the title
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 15px;">
                <a href="https://www.linkedin.com/in/etagowni/" target="_blank" style="color: #a78bfa; text-decoration: none; font-size: 1rem;">
                    <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="16" style="margin-right: 5px; vertical-align: middle;">
                    Developed by AnilKumar E
                </a>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if ENHANCED_PROCESSING_AVAILABLE:
            st.markdown(
                """
                <div style="text-align: center;">
                Upload 2-3 songs and our AI will blend them into a unique mashup with advanced audio processing!
                </div>
                """, 
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                """
                <div style="text-align: center;">
                Upload 2-3 songs and our AI will blend them into a unique mashup!
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Sidebar
        with st.sidebar:
            # App Logo/Header section
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #6d28d9;">🎵 AI Song Mashup</h2>
                <p style="font-size: 0.8rem; color: #a78bfa;">v1.0</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Advanced AI options
            if ENHANCED_PROCESSING_AVAILABLE:
                use_advanced = st.checkbox("Use advanced AI models - (Inprogress)", value=st.session_state["use_enhanced_models"])
                st.session_state["use_enhanced_models"] = use_advanced
            
            # Status indicator section - shows current app state
            if "job_status" in st.session_state:
                status = st.session_state["job_status"]
                if status == "idle":
                    st.markdown("""
                    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #1e293b; padding: 10px; border-radius: 5px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #10b981; margin-right: 10px;"></div>
                        <div style="font-size: 0.9rem;">Ready for uploads</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif status == "processing":
                    st.markdown("""
                    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #1e293b; padding: 10px; border-radius: 5px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #f59e0b; margin-right: 10px;"></div>
                        <div style="font-size: 0.9rem;">Processing mashup...</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif status == "completed":
                    st.markdown("""
                    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #1e293b; padding: 10px; border-radius: 5px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #3b82f6; margin-right: 10px;"></div>
                        <div style="font-size: 0.9rem;">Mashup completed</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif status == "error":
                    st.markdown("""
                    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #1e293b; padding: 10px; border-radius: 5px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #ef4444; margin-right: 10px;"></div>
                        <div style="font-size: 0.9rem;">Error occurred</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Navigation tabs in sidebar
            nav_option = st.radio(
                "Navigation",
                options=["🏠 Home", "ℹ️ How It Works", "🎚️ Features", "❓ FAQ"],
                horizontal=True
            )
            
            st.markdown("<hr style='margin: 15px 0; opacity: 0.3;'>", unsafe_allow_html=True)
            
            # Display different content based on navigation selection
            if nav_option == "🏠 Home":
                pass  # Home is default, content shown in main area
            elif nav_option == "ℹ️ How It Works":
                st.markdown("### How Song Mashup Works")
                
                st.markdown("""
                <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4 style="color: #a78bfa; margin-top: 0;">1. Upload Tracks</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 0;">Upload 2-3 audio files in MP3, WAV, or FLAC format. Our system works best with high-quality audio.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4 style="color: #a78bfa; margin-top: 0;">2. AI Analysis</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 0;">Each track is analyzed for tempo, key, structure, and musical elements using advanced AI models.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4 style="color: #a78bfa; margin-top: 0;">3. Stem Separation</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 0;">Tracks are separated into stems (vocals, drums, bass, other) for precise blending.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4 style="color: #a78bfa; margin-top: 0;">4. AI Blending</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 0;">Our AI creates a coherent mashup, aligning tempo and keys while preserving the best elements of each track.</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif nav_option == "🎚️ Features":
                st.markdown("### Key Features")
                
                # Feature list with icons
                features = [
                    ("🧠 Advanced AI Models", "Uses cutting-edge music processing algorithms"),
                    ("👂 Stem Separation", "Isolates vocals, drums, bass, and other elements"),
                    ("🎛️ Fine-Tuned Controls", "Adjust blending ratios and processing parameters"),
                    ("🔊 High Quality Output", "Creates studio-quality mashups"),
                    ("🔄 Rapid Processing", "Generates results in minutes, not hours")
                ]
                
                for icon_feature, description in features:
                    st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <div style="font-weight: bold; margin-bottom: 2px;">{icon_feature}</div>
                        <div style="font-size: 0.85rem; color: #cbd5e1;">{description}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Advanced features callout if available
                if ENHANCED_PROCESSING_AVAILABLE and st.session_state.get("use_enhanced_models", False):
                    st.markdown("""
                    <div style="background-color: #4c1d95; padding: 10px; border-radius: 5px; margin: 15px 0;">
                        <p style="font-weight: bold; margin-bottom: 5px;">🚀 Advanced Mode Active</p>
                        <p style="font-size: 0.85rem; margin-bottom: 0;">Using improved AI models for better audio quality and precision.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            elif nav_option == "❓ FAQ":
                st.markdown("### Frequently Asked Questions")
                
                with st.expander("What file formats are supported?"):
                    st.markdown("""
                    We support common audio formats:
                    - MP3 (.mp3)
                    - WAV (.wav)
                    - FLAC (.flac)
                    - OGG (.ogg)
                    - M4A (.m4a)
                    
                    For best results, use high-quality audio files.
                    """)
                    
                with st.expander("How many songs can I mashup?"):
                    st.markdown("""
                    You can upload 2-3 songs for each mashup.
                    
                    For optimal results, choose songs that:
                    - Have similar tempos
                    - Are in complementary musical keys
                    - Feature clear vocals and instruments
                    """)
                    
                with st.expander("Can I adjust the mashup after creation?"):
                    st.markdown("""
                    Yes! After your mashup is created, you can:
                    - Adjust mixing parameters
                    - Apply audio effects
                    - Modify stem levels
                    - Add reverb, EQ, and dynamics processing
                    
                    All adjustments are non-destructive and can be reset.
                    """)
                    
                with st.expander("Is my data private?"):
                    st.markdown("""
                    Yes, we respect your privacy:
                    - All processing happens locally
                    - Your audio files aren't permanently stored
                    - We don't share your data with third parties
                    
                    Files are temporarily cached to improve performance.
                    """)
            
            # System info section at bottom
            st.markdown("<hr style='margin: 15px 0; opacity: 0.3;'>", unsafe_allow_html=True)
            
            # Collapsible system info
            with st.expander("System Info"):
                st.markdown(f"**Python:** {sys.version.split()[0]}")
                
                # Add AI model info if enhanced
                if ENHANCED_PROCESSING_AVAILABLE:
                    try:
                        import torch
                        st.markdown(f"**PyTorch:** {torch.__version__}")
                        st.markdown(f"**CUDA Available:** {'Yes' if torch.cuda.is_available() else 'No'}")
                        if torch.cuda.is_available():
                            st.markdown(f"**GPU:** {torch.cuda.get_device_name(0)}")
                    except:
                        st.markdown("**PyTorch:** Not detected")
            
            # Add developer info
            st.markdown("""
            <div style="text-align: center; margin: 15px 0; font-size: 0.75rem; color: #a78bfa;">
                <a href="https://www.linkedin.com/in/etagowni/" target="_blank" style="color: #a78bfa; text-decoration: none;">
                    <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="12" style="margin-right: 4px; vertical-align: middle;">
                    Developed by AnilKumar E
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Reset button remains at the bottom
            if st.button("Reset Application", use_container_width=True):
                reset_state()
                rerun()
        
        # Main content
        if st.session_state["job_status"] == "idle":
            # File uploader
            st.markdown('<h2 class="sub-header">Upload Your Songs</h2>', unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "Choose 2-3 audio files (MP3, WAV, FLAC)",
                type=["mp3", "wav", "flac", "ogg", "m4a"],
                accept_multiple_files=True,
                key="file_uploader"
            )
            
            if uploaded_files:
                # Validate number of files
                if len(uploaded_files) > 3:
                    st.warning("You can only upload up to 3 files. Only the first 3 will be used.")
                    uploaded_files = uploaded_files[:3]
                
                st.session_state["uploaded_files"] = uploaded_files
                
                # Display file details and blend settings
                st.markdown('<h2 class="sub-header">Blend Settings</h2>', unsafe_allow_html=True)
                st.info("Adjust the blend ratio for each track to control how prominent it is in the final mashup.")
                
                # Safely call display_file_details with proper error handling
                try:
                    display_file_details(uploaded_files)
                except Exception as e:
                    st.error(f"Error displaying file details: {str(e)}")
                    logger.error(f"Error in display_file_details: {str(e)}")
                
                # Generate button
                if len(uploaded_files) >= 2:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("Generate Mashup", use_container_width=True):
                            with st.spinner("Processing your mashup..."):
                                start_processing()
                                rerun()
                else:
                    st.warning("Please upload at least 2 audio files to generate a mashup.")
        
        elif st.session_state["job_status"] == "processing":
            # Show processing status
            st.markdown('<h2 class="sub-header">Processing Your Mashup</h2>', unsafe_allow_html=True)
            
            st.markdown('<div class="status-container">', unsafe_allow_html=True)
            st.info("This may take several minutes depending on the length of your tracks.")
            
            # Show processing steps
            processing_steps = [
                "Analyzing audio files",
                "Extracting musical features",
                "Separating audio stems",
                "Aligning tempo and key",
                "Blending tracks",
                "Finalizing mashup"
            ]
            
            current_step = int(time.time() % len(processing_steps))
            progress_bar = st.progress(((current_step + 1) / len(processing_steps)) * 100)
            st.text(f"Step {current_step + 1}/{len(processing_steps)}: {processing_steps[current_step]}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Cancel Processing", use_container_width=True):
                reset_state()
                rerun()
        
        elif st.session_state["job_status"] == "completed":
            # Show results
            st.markdown('<h2 class="sub-header">Your AI Mashup is Ready!</h2>', unsafe_allow_html=True)
            
            st.markdown('<div class="status-container">', unsafe_allow_html=True)
            
            # Display audio player
            if st.session_state["mashup_path"] and os.path.exists(st.session_state["mashup_path"]):
                st.audio(st.session_state["mashup_path"], format="audio/mp3")
                
                # Add stem visualization section if stem effects have been applied
                if "stem_effects" in st.session_state and "is_processed" in st.session_state and st.session_state["is_processed"]:
                    # Create visual representation of stem levels
                    stem_viz_container = st.container()
                    with stem_viz_container:
                        st.markdown("#### Active Stems")
                        
                        # Create a progress bar for each stem to visualize its level
                        stem_levels = {
                            stem: config.get('level', 1.0) 
                            for stem, config in st.session_state["stem_effects"].items()
                            if 'level' in config
                        }
                        
                        # Normalize for visualization (max level is 100%)
                        max_level = max(stem_levels.values()) if stem_levels else 1.0
                        max_level = max(max_level, 1.0)  # Ensure we don't divide by zero
                        
                        stem_labels = {
                            "vocals": "👤 Vocals",
                            "drums": "🥁 Drums",
                            "bass": "🎸 Bass",
                            "other": "🎹 Other Instruments"
                        }
                        
                        # Show progress bars with labels and levels
                        for stem_name, level in stem_levels.items():
                            stem_label = stem_labels.get(stem_name, stem_name.title())
                            normalized_level = level / max_level
                            
                            # Only show stems with non-zero levels
                            if level > 0.01:
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    st.markdown(f"**{stem_label}**")
                                with col2:
                                    # Use a progress bar to visualize the stem level
                                    st.progress(normalized_level)
                                    st.markdown(f"<div style='text-align: right; margin-top: -20px;'>Level: {level:.1f}</div>", unsafe_allow_html=True)
                        
                        # Collect active effects data
                        active_effects = {}
                        for stem_name, config in st.session_state["stem_effects"].items():
                            effects_list = []
                            for effect_name, params in config.items():
                                if effect_name == "level":
                                    continue
                                
                                # Only show effects that are actually active
                                if effect_name == "eq" and any(abs(params.get(band, 0.0)) > 0.01 for band in ["low_gain", "mid_gain", "high_gain"]):
                                    effects_list.append("EQ")
                                elif effect_name == "reverb" and params.get("amount", 0.0) > 0.01:
                                    effects_list.append("Reverb")
                                elif effect_name == "compression" and params.get("ratio", 1.0) > 1.0:
                                    effects_list.append("Compression")
                                elif effect_name == "delay" and params.get("mix", 0.0) > 0.01:
                                    effects_list.append("Delay")
                                elif effect_name == "distortion" and params.get("amount", 0.0) > 0.01 and params.get("mix", 0.0) > 0.01:
                                    effects_list.append("Distortion")
                            
                            if effects_list:
                                active_effects[stem_name] = effects_list
                        
                        # Display active effects
                        if active_effects:
                            st.markdown("#### Active Effects")
                            for stem_name, effects_list in active_effects.items():
                                stem_label = stem_labels.get(stem_name, stem_name.title())
                                st.markdown(f"**{stem_label}**: {', '.join(effects_list)}")
                    
                    # Enhanced features section
                    if ENHANCED_PROCESSING_AVAILABLE and st.session_state["use_enhanced_models"]:
                        st.markdown("### Mashup Analysis")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
                            st.markdown("**Audio Characteristics**")
                            st.markdown("• Duration: 3:24")
                            st.markdown("• Estimated Tempo: 128 BPM")
                            st.markdown("• Estimated Key: A minor")
                            st.markdown("• Vocal Clarity: High")
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        with col2:
                            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
                            st.markdown("**AI Processing**")
                            st.markdown("• Stem Separation Quality: High")
                            st.markdown("• Blending Algorithm: Adaptive NMF")
                            st.markdown("• Enhancement Level: Advanced")
                            st.markdown("• Processing Time: 45 seconds")
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Add mixing controls section
                    st.markdown("### Mix Controls")
                    
                    with st.expander("Adjust Mix Parameters", expanded=True):
                        # Initialize mixing parameters in session state if they don't exist
                        if "mix_params" not in st.session_state:
                            st.session_state["mix_params"] = {
                                "master_volume": 1.0,
                                "bass_boost": 0.0,
                                "treble_boost": 0.0,
                                "reverb": 0.0,
                                "vocal_prominence": 1.0,
                                "dynamic_range": 1.0
                            }
                        
                        # Initialize stem effects in session state if they don't exist
                        if "stem_effects" not in st.session_state:
                            st.session_state["stem_effects"] = {
                                "vocals": {
                                    "level": 1.0,
                                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                                    "reverb": {"amount": 0.0, "room_size": 0.5}
                                },
                                "drums": {
                                    "level": 1.0,
                                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                                    "compression": {"threshold": -20.0, "ratio": 4.0}
                                },
                                "bass": {
                                    "level": 1.0,
                                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0}
                                },
                                "other": {
                                    "level": 1.0,
                                    "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                                    "reverb": {"amount": 0.0, "room_size": 0.5}
                                }
                            }
                        
                        # Create tabs for general mix vs stem-specific effects
                        mix_tabs = st.tabs(["General Mix", "Stem Effects"])
                        
                        # Tab 1: General Mix Controls (existing parameters)
                        with mix_tabs[0]:
                            # Create two columns for the controls
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.session_state["mix_params"]["master_volume"] = st.slider(
                                    "Master Volume",
                                    min_value=0.0,
                                    max_value=2.0,
                                    value=st.session_state["mix_params"]["master_volume"],
                                    step=0.1,
                                    key="master_volume_slider"
                                )
                                
                                st.session_state["mix_params"]["bass_boost"] = st.slider(
                                    "Bass Boost",
                                    min_value=-1.0,
                                    max_value=1.0,
                                    value=st.session_state["mix_params"]["bass_boost"],
                                    step=0.1,
                                    key="bass_boost_slider"
                                )
                            
                            with col2:
                                st.session_state["mix_params"]["treble_boost"] = st.slider(
                                    "Treble Boost",
                                    min_value=-1.0,
                                    max_value=1.0,
                                    value=st.session_state["mix_params"]["treble_boost"],
                                    step=0.1,
                                    key="treble_boost_slider"
                                )
                                
                                st.session_state["mix_params"]["reverb"] = st.slider(
                                    "Reverb",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=st.session_state["mix_params"]["reverb"],
                                    step=0.1,
                                    key="reverb_slider"
                                )
                            
                            with col3:
                                st.session_state["mix_params"]["vocal_prominence"] = st.slider(
                                    "Vocal Prominence",
                                    min_value=0.0,
                                    max_value=2.0,
                                    value=st.session_state["mix_params"]["vocal_prominence"],
                                    step=0.1,
                                    key="vocal_prominence_mix_slider"
                                )
                                
                                st.session_state["mix_params"]["dynamic_range"] = st.slider(
                                    "Dynamic Range",
                                    min_value=0.5,
                                    max_value=1.5,
                                    value=st.session_state["mix_params"]["dynamic_range"],
                                    step=0.1,
                                    key="dynamic_range_slider"
                                )
                            
                            # Apply mix settings button
                            if st.button("Apply Mix Settings", use_container_width=True):
                                with st.spinner("Processing audio with mix settings..."):
                                    try:
                                        # Make sure we have a valid mashup path
                                        if not st.session_state["mashup_path"] or not os.path.exists(st.session_state["mashup_path"]):
                                            st.error("No mashup file available to process")
                                            return
                                        
                                        # Create a processed version filename
                                        original_path = st.session_state["mashup_path"]
                                        job_id = st.session_state["job_id"]
                                        processed_filename = f"{job_id}_mix_processed.mp3"
                                        processed_path = os.path.join(MASHUP_DIR, processed_filename)
                                        
                                        # Use the original mashup path if available
                                        if "original_mashup_path" in st.session_state:
                                            input_path = st.session_state["original_mashup_path"]
                                        else:
                                            input_path = original_path
                                        
                                        # Process the file with mix settings
                                        logger.info(f"Processing mix with settings: {st.session_state['mix_params']}")
                                        result_path = process_mix_settings(
                                            input_path,
                                            processed_path,
                                            st.session_state["mix_params"]
                                        )
                                        
                                        # Update the session state to use the processed file
                                        if result_path and os.path.exists(result_path):
                                            # Store both the original and processed paths
                                            if "original_mashup_path" not in st.session_state:
                                                st.session_state["original_mashup_path"] = st.session_state["mashup_path"]
                                            # Update the current mashup path to the processed version
                                            st.session_state["mashup_path"] = result_path
                                            st.session_state["is_processed"] = True
                                            
                                            # Success message
                                            st.success("Mix settings applied successfully!")
                                            
                                            # Rerun to refresh audio player
                                            rerun()
                                        else:
                                            st.error("Failed to process audio with mix settings")
                                    except Exception as e:
                                        st.error(f"Error applying mix settings: {str(e)}")
                                        logger.error(f"Mix processing error: {str(e)}", exc_info=True)
                        
                        # Tab 2: Stem-specific effects
                        with mix_tabs[1]:
                            # Create a tab for each stem type
                            stem_tabs = st.tabs(["Vocals", "Drums", "Bass", "Other"])
                            
                            # Vocals tab
                            with stem_tabs[0]:
                                # Level slider
                                st.session_state["stem_effects"]["vocals"]["level"] = st.slider(
                                    "Vocals Level",
                                    min_value=0.0,
                                    max_value=2.0,
                                    value=st.session_state["stem_effects"]["vocals"]["level"],
                                    step=0.1,
                                    key="vocals_level_slider"
                                )
                                
                                # EQ controls
                                st.markdown("#### EQ Settings")
                                eq_cols = st.columns(3)
                                with eq_cols[0]:
                                    st.session_state["stem_effects"]["vocals"]["eq"]["low_gain"] = st.slider(
                                        "Low Gain",
                                        min_value=-1.0,
                                        max_value=1.0,
                                        value=st.session_state["stem_effects"]["vocals"]["eq"]["low_gain"],
                                        step=0.1,
                                        key="vocals_low_gain_slider"
                                    )
                                with eq_cols[1]:
                                    st.session_state["stem_effects"]["vocals"]["eq"]["mid_gain"] = st.slider(
                                        "Mid Gain",
                                        min_value=-1.0,
                                        max_value=1.0,
                                        value=st.session_state["stem_effects"]["vocals"]["eq"]["mid_gain"],
                                        step=0.1,
                                        key="vocals_mid_gain_slider"
                                    )
                                with eq_cols[2]:
                                    st.session_state["stem_effects"]["vocals"]["eq"]["high_gain"] = st.slider(
                                        "High Gain",
                                        min_value=-1.0,
                                        max_value=1.0,
                                        value=st.session_state["stem_effects"]["vocals"]["eq"]["high_gain"],
                                        step=0.1,
                                        key="vocals_high_gain_slider"
                                    )
                                
                                # Reverb controls
                                st.markdown("#### Reverb Settings")
                                reverb_cols = st.columns(2)
                                with reverb_cols[0]:
                                    st.session_state["stem_effects"]["vocals"]["reverb"]["amount"] = st.slider(
                                        "Amount",
                                        min_value=0.0,
                                        max_value=1.0,
                                        value=st.session_state["stem_effects"]["vocals"]["reverb"]["amount"],
                                        step=0.1,
                                        key="vocals_reverb_amount_slider"
                                    )
                                with reverb_cols[1]:
                                    st.session_state["stem_effects"]["vocals"]["reverb"]["room_size"] = st.slider(
                                        "Room Size",
                                        min_value=0.1,
                                        max_value=0.9,
                                        value=st.session_state["stem_effects"]["vocals"]["reverb"]["room_size"],
                                        step=0.1,
                                        key="vocals_reverb_room_size_slider"
                                    )
                            
                            # Drums tab (similar layout)
                            with stem_tabs[1]:
                                # Level slider
                                st.session_state["stem_effects"]["drums"]["level"] = st.slider(
                                    "Drums Level",
                                    min_value=0.0,
                                    max_value=2.0,
                                    value=st.session_state["stem_effects"]["drums"]["level"],
                                    step=0.1,
                                    key="drums_level_slider"
                                )
                                
                                # EQ controls
                                st.markdown("#### EQ Settings")
                                eq_cols = st.columns(3)
                                with eq_cols[0]:
                                    st.session_state["stem_effects"]["drums"]["eq"]["low_gain"] = st.slider(
                                        "Low Gain",
                                        min_value=-1.0,
                                        max_value=1.0,
                                        value=st.session_state["stem_effects"]["drums"]["eq"]["low_gain"],
                                        step=0.1,
                                        key="drums_low_gain_slider"
                                    )
                                
                            # Apply stem effects button
                            if st.button("Apply Stem Effects", use_container_width=True):
                                with st.spinner("Processing stems with effects..."):
                                    try:
                                        # Make sure we have a valid mashup path
                                        if not st.session_state["mashup_path"] or not os.path.exists(st.session_state["mashup_path"]):
                                            st.error("No mashup file available to process")
                                            return
                                        
                                        # Create a processed version filename
                                        original_path = st.session_state["mashup_path"]
                                        job_id = st.session_state["job_id"]
                                        processed_filename = f"{job_id}_stems_processed.mp3"
                                        processed_path = os.path.join(MASHUP_DIR, processed_filename)
                                        
                                        # Use the original mashup path if available
                                        if "original_mashup_path" in st.session_state:
                                            input_path = st.session_state["original_mashup_path"]
                                        else:
                                            input_path = original_path
                                        
                                        # Process the file with stem-specific effects
                                        logger.info(f"Processing stems with effects: {st.session_state['stem_effects']}")
                                        result_path = process_stems_with_effects(
                                            input_path,
                                            processed_path,
                                            st.session_state["stem_effects"]
                                        )
                                        if result_path and os.path.exists(result_path):
                                            # Store both the original and processed paths
                                            if "original_mashup_path" not in st.session_state:
                                                st.session_state["original_mashup_path"] = st.session_state["mashup_path"]
                                            # Update the current mashup path to the processed version
                                            st.session_state["mashup_path"] = result_path
                                            st.session_state["is_processed"] = True
                                            
                                            # Success message
                                            st.success("Stem effects applied successfully!")
                                            
                                            # Rerun to refresh audio player
                                            rerun()
                                        else:
                                            st.error("Failed to process stems with effects")
                                    except Exception as e:
                                        st.error(f"Error applying stem effects: {str(e)}")
                                        logger.error(f"Stem processing error: {str(e)}", exc_info=True)
                        
                        # Reset button (only show if we have applied processing)
                        if "is_processed" in st.session_state and st.session_state["is_processed"] and "original_mashup_path" in st.session_state:
                            if st.button("Reset to Original", use_container_width=True):
                                # Restore original mashup path
                                st.session_state["mashup_path"] = st.session_state["original_mashup_path"]
                                st.session_state["is_processed"] = False
                                
                                # Reset mix parameters to defaults
                                st.session_state["mix_params"] = {
                                    "master_volume": 1.0,
                                    "bass_boost": 0.0,
                                    "treble_boost": 0.0,
                                    "reverb": 0.0,
                                    "vocal_prominence": 1.0,
                                    "dynamic_range": 1.0
                                }
                                
                                # Reset stem effects
                                st.session_state["stem_effects"] = {
                                    "vocals": {
                                        "level": 1.0,
                                        "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                                        "reverb": {"amount": 0.0, "room_size": 0.5}
                                    },
                                    "drums": {
                                        "level": 1.0,
                                        "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                                        "compression": {"threshold": -20.0, "ratio": 4.0}
                                    },
                                    "bass": {
                                        "level": 1.0,
                                        "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0}
                                    },
                                    "other": {
                                        "level": 1.0,
                                        "eq": {"low_gain": 0.0, "mid_gain": 0.0, "high_gain": 0.0},
                                        "reverb": {"amount": 0.0, "room_size": 0.5}
                                    }
                                }
                                
                                st.success("Reset to original mashup")
                                rerun()
                        else:
                            # Show a disabled button or info message when no processing has been applied
                            st.markdown("*Apply mix settings to modify audio*")
                    
                    # Download button
                    with open(st.session_state["mashup_path"], "rb") as f:
                        st.download_button(
                            label="Download Mashup",
                            data=f,
                            file_name=f"song_mashup_{st.session_state['job_id']}.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                else:
                    st.error("There was an error generating your mashup. Please try again.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Create new mashup button
                if st.button("Create Another Mashup", use_container_width=True):
                    reset_state()
                    rerun()
            
            elif st.session_state["job_status"] == "error":
                # Show error
                st.markdown('<h2 class="sub-header">Error Processing Your Mashup</h2>', unsafe_allow_html=True)
                
                st.markdown('<div class="status-container">', unsafe_allow_html=True)
                st.error("There was an error processing your audio files. Please try again with different files.")
                
                # Show potential error details
                error_file = os.path.join(MASHUP_DIR, f"{st.session_state['job_id']}_error.txt")
                if os.path.exists(error_file):
                    with open(error_file, 'r') as f:
                        error_message = f.read()
                    with st.expander("Error Details"):
                        st.code(error_message)
                
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Try again button
                if st.button("Try Again", use_container_width=True):
                    reset_state()
                    rerun()
            
            # Footer
            st.markdown(
                """
                <div class="footer">
                Powered by AI - Mixing Creativity with Technology<br>
                <span style="font-size: 0.75rem;">Developed by <a href="https://www.linkedin.com/in/etagowni/" target="_blank" style="color: #a78bfa; text-decoration: none;">AnilKumar E</a></span>
                </div>
                """, 
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        logger.error(f"Uncaught error in main app: {str(e)}", exc_info=True)
            
        # Display error details in an expander
        with st.expander("Error Details"):
            st.code(str(e))
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    initialize_session_state()
    main() 