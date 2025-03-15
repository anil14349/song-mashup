# AI-Powered Song Mashup Generator

This Python application uses artificial intelligence to generate unique song mashups by blending 2-3 uploaded songs. The project leverages advanced AI models like MusicBERT and Suno Bark for audio analysis and tune generation.

## Features

- Upload 2-3 songs in common audio formats (MP3, WAV, FLAC)
- AI-powered analysis of musical elements (tempo, key, chord progressions)
- Intelligent blending of melodies, harmonies, and rhythms
- Generation of unique mashups that preserve key musical elements from source tracks
- Streamlit web interface for easy interaction and download of results

## Technical Stack

- **Audio Processing**: Librosa, PyDub, FFmpeg
- **Machine Learning**: PyTorch, Transformers, Scikit-learn
- **AI Models**: MusicBERT, Suno Bark
- **Frontend**: Streamlit
- **Audio Separation**: Demucs (for extracting stems from original tracks)

## Requirements

- Python 3.10 or 3.11 (recommended)
- FFmpeg installed on your system
- Sufficient disk space for audio processing
- 4GB+ RAM recommended for larger audio files

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/song-mashup.git
   cd song-mashup
   ```

2. Create a virtual environment (recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   Note: If you encounter any dependency issues, you can try installing the core packages individually:

   ```
   pip install numpy scipy pandas librosa streamlit torch
   ```

4. Install FFmpeg (required for audio processing):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)

## Usage

1. Start the application:
   ```
   python run.py
   ```
   Or directly with Streamlit:
   ```
   streamlit run app.py
   ```
2. The application will open in your default web browser
3. Upload 2-3 songs (MP3, WAV, FLAC formats)
4. Adjust blend ratios for each track (optional)
5. Generate and download your unique AI-created mashup

## Troubleshooting

- **Missing Dependencies**: If you encounter dependency errors, try installing individual packages with specific versions compatible with your Python version.
- **FFmpeg Issues**: Ensure FFmpeg is correctly installed and available in your system PATH.
- **Memory Errors**: Processing large audio files requires significant memory. Try with shorter audio files or increase your system's swap space.
- **Model Download Failures**: Some AI models are downloaded the first time they're used. Ensure you have a stable internet connection.

## Project Structure

- `app.py`: Main Streamlit application
- `song_mashup/api`: Core audio processing logic
- `song_mashup/models`: AI model implementations
- `song_mashup/utils`: Helper functions for audio processing
- `song_mashup/data`: Directory for temporary storage of uploads and generated mashups

## How It Works

1. **Audio Analysis**: Each uploaded song is analyzed to extract tempo, key, and other musical features
2. **Stem Separation**: Songs are split into component parts (vocals, drums, bass, etc.) using Demucs
3. **Temporal and Harmonic Alignment**: Songs are aligned in tempo and key for coherent blending
4. **AI Blending**: Advanced algorithms intelligently blend the separate elements
5. **Final Composition**: The components are recombined into a final mashup, preserving the best elements of each song

## License

MIT License

## Acknowledgements

This project uses several open-source libraries and pre-trained models that have made AI-powered audio generation accessible.
