"""
Streamlit app for the AI-powered Song Mashup Generator.
"""

import os
import sys
import time
import uuid
import tempfile
import threading
from pathlib import Path

# Add the parent directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import necessary libraries with error handling
try:
    import streamlit as st
    import numpy as np
except ImportError as e:
    print(f"Error importing core libraries: {e}")
    print("Please install required packages: pip install streamlit numpy")
    sys.exit(1)

# Import project modules with error handling
try:
    from song_mashup.api.process import process_files, load_and_analyze_audio
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


def reset_state():
    """Reset the app state to initial values."""
    st.session_state["job_id"] = None
    st.session_state["job_status"] = "idle"
    st.session_state["uploaded_files"] = []
    st.session_state["blend_ratios"] = {}
    st.session_state["audio_details"] = {}
    st.session_state["mashup_path"] = None
    st.session_state["processing_thread"] = None


def process_files_sync(job_id, file_paths, blend_ratios):
    """
    Process files synchronously (for Streamlit to avoid threading issues).
    """
    try:
        # Process files
        process_files(job_id, file_paths, blend_ratios)
        
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
    
    # Create a new job ID
    job_id = str(uuid.uuid4())
    st.session_state["job_id"] = job_id
    st.session_state["job_status"] = "processing"
    
    # Create job directory
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save uploaded files to disk
    saved_file_paths = []
    for uploaded_file in st.session_state["uploaded_files"]:
        file_path = os.path.join(job_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_file_paths.append(file_path)
    
    # Get blend ratios
    blend_ratios = []
    for i, uploaded_file in enumerate(st.session_state["uploaded_files"]):
        ratio = st.session_state["blend_ratios"].get(uploaded_file.name, 1.0)
        blend_ratios.append(ratio)
    
    # Instead of using a thread, we'll use Streamlit's session state to keep track of processing
    # This avoids the ScriptRunContext errors in threading
    result = process_files_sync(job_id, saved_file_paths, blend_ratios)
    
    # Update state based on result
    if isinstance(result, dict) and "error" in result:
        st.session_state["job_status"] = "error"
    else:
        st.session_state["job_status"] = "completed"
        st.session_state["mashup_path"] = result


def display_file_details(uploaded_files):
    """Display details about the uploaded audio files."""
    for uploaded_file in uploaded_files:
        # Check if we've already analyzed this file
        if uploaded_file.name not in st.session_state["audio_details"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            
            # Analyze audio
            try:
                audio_data = load_and_analyze_audio(tmp_path)
                st.session_state["audio_details"][uploaded_file.name] = {
                    'tempo': audio_data['tempo'],
                    'key': audio_data['key'],
                    'duration': audio_data['duration']
                }
            except Exception as e:
                st.session_state["audio_details"][uploaded_file.name] = {
                    'error': f"Could not analyze file: {str(e)}"
                }
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Display file details in a collapsible section
        with st.expander(f"Details: {uploaded_file.name}"):
            details = st.session_state["audio_details"][uploaded_file.name]
            if 'error' in details:
                st.error(details['error'])
            else:
                st.markdown(f"**Duration:** {details['duration']:.2f} seconds")
                st.markdown(f"**Tempo:** {details['tempo']:.2f} BPM")
                st.markdown(f"**Key:** {details['key']}")
                
                # Blend ratio slider
                if uploaded_file.name not in st.session_state["blend_ratios"]:
                    st.session_state["blend_ratios"][uploaded_file.name] = 1.0
                
                st.session_state["blend_ratios"][uploaded_file.name] = st.slider(
                    "Blend Ratio",
                    min_value=0.1,
                    max_value=2.0,
                    value=st.session_state["blend_ratios"][uploaded_file.name],
                    step=0.1,
                    key=f"slider_{uploaded_file.name}"
                )


def main():
    """Main app function."""
    # Check dependencies if not done yet
    if not st.session_state["dependency_check"]:
        st.session_state["dependency_check"] = check_dependencies()
        if not st.session_state["dependency_check"]:
            st.stop()
    
    # Header
    st.markdown('<h1 class="main-header">AI Song Mashup Generator</h1>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center;">
        Upload 2-3 songs and our AI will blend them into a unique mashup!
        </div>
        """, 
        unsafe_allow_html=True
    )
    
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
    
    # Sidebar
    with st.sidebar:
        # App Logo/Header section
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #6d28d9;">🎵 AI Song Mashup</h2>
            <p style="font-size: 0.8rem; color: #a78bfa;">v1.0</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                <p style="font-size: 0.9rem; margin-bottom: 0;">Upload 2-3 audio files in MP3, WAV, or FLAC format.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h4 style="color: #a78bfa; margin-top: 0;">2. AI Analysis</h4>
                <p style="font-size: 0.9rem; margin-bottom: 0;">Each track is analyzed for tempo, key, and musical elements.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h4 style="color: #a78bfa; margin-top: 0;">3. AI Blending</h4>
                <p style="font-size: 0.9rem; margin-bottom: 0;">AI algorithms blend the tracks into a coherent mashup.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h4 style="color: #a78bfa; margin-top: 0;">4. Download</h4>
                <p style="font-size: 0.9rem; margin-bottom: 0;">Download and share your unique AI-generated mashup.</p>
            </div>
            """, unsafe_allow_html=True)
            
        elif nav_option == "🎚️ Features":
            st.markdown("### Key Features")
            
            # Feature list with icons
            features = [
                ("🧠 AI Music Analysis", "Identifies key musical elements"),
                ("🔄 Smart Blending", "Creates smooth transitions between tracks"),
                ("🎛️ Blend Controls", "Adjust the prominence of each track"),
                ("🔊 Custom Mixes", "Generate unique mashups from your music"),
                ("⚡ Simple Workflow", "Easy upload, blend, and download process")
            ]
            
            for icon_feature, description in features:
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="font-weight: bold; margin-bottom: 2px;">{icon_feature}</div>
                    <div style="font-size: 0.85rem; color: #cbd5e1;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Note about enhanced version
            st.markdown("""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <p style="font-size: 0.85rem; margin-bottom: 0;">💡 Try the Enhanced version for advanced features like stem separation and effects processing!</p>
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
                """)
                
            with st.expander("How many songs can I mashup?"):
                st.markdown("""
                You can upload 2-3 songs for each mashup.
                
                For optimal results, choose songs that:
                - Have similar tempos
                - Are in complementary musical keys
                """)
                
            with st.expander("How does the blend ratio work?"):
                st.markdown("""
                The blend ratio controls how prominent each track is in the final mashup:
                
                - Higher values (>1.0) make that track more prominent
                - Lower values (<1.0) make that track less prominent
                - Default value (1.0) provides balanced mixing
                """)
                
            with st.expander("Is my data private?"):
                st.markdown("""
                Yes, we respect your privacy:
                - All processing happens locally
                - Your audio files aren't permanently stored
                - We don't share your data with third parties
                """)
        
        # System info section at bottom
        st.markdown("<hr style='margin: 15px 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        # Collapsible system info
        with st.expander("System Info"):
            st.markdown(f"**Python:** {sys.version.split()[0]}")
            
            try:
                import librosa
                st.markdown(f"**Librosa:** {librosa.__version__}")
            except:
                pass
        
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
            st.experimental_rerun()
    
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
            
            display_file_details(uploaded_files)
            
            # Generate button
            if len(uploaded_files) >= 2:
                if st.button("Generate Mashup", use_container_width=True):
                    with st.spinner("Processing your mashup..."):
                        start_processing()
                        st.experimental_rerun()
            else:
                st.warning("Please upload at least 2 audio files to generate a mashup.")
    
    elif st.session_state["job_status"] == "processing":
        # Show processing status
        st.markdown('<h2 class="sub-header">Processing Your Mashup</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="status-container">', unsafe_allow_html=True)
        st.info("This may take several minutes depending on the length of your tracks.")
        progress_bar = st.progress(0)
        
        # Show indeterminate progress
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.1)
            
            # Check if we should continue or if processing is done
            if st.session_state["job_status"] != "processing":
                st.experimental_rerun()
                break
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Cancel Processing", use_container_width=True):
            reset_state()
            st.experimental_rerun()
    
    elif st.session_state["job_status"] == "completed":
        # Show results
        st.markdown('<h2 class="sub-header">Your AI Mashup is Ready!</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="status-container">', unsafe_allow_html=True)
        
        # Display audio player
        if st.session_state["mashup_path"] and os.path.exists(st.session_state["mashup_path"]):
            st.audio(st.session_state["mashup_path"], format="audio/mp3")
            
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
            st.experimental_rerun()
    
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
            st.experimental_rerun()
    
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


if __name__ == "__main__":
    main() 