# AI Song Mashup Generator - Enhanced Edition

An advanced application for creating AI-powered song mashups with enhanced audio processing capabilities.

## Enhanced AI Features

The Enhanced Edition builds upon the standard version by adding sophisticated AI models and algorithms for better audio analysis and processing:

### Improved Audio Analysis

- **High-Resolution Chromagram Analysis**: 24-note resolution (vs. standard 12-note) for more precise harmonic analysis
- **Advanced Key Detection**: Template-based correlation for accurate key estimation
- **Detailed Musical Feature Extraction**: Extracts and analyzes melody contours, rhythm patterns, and spectral characteristics
- **Audio Complexity Scoring**: Quantifies musical complexity based on harmonic and rhythmic variety

### Better Stem Separation

- **NMF-Based Source Separation**: Uses Non-Negative Matrix Factorization to isolate vocals, drums, bass, and other elements
- **Adaptive Component Modeling**: Automatically determines the appropriate number of components for each stem
- **Fallback Mechanisms**: Gracefully degrades to simpler methods when optimal separation isn't possible

### Sophisticated Audio Blending

- **Improved Tempo Alignment**: More precise time-stretching using phase vocoder
- **Advanced Key Alignment**: Intelligent pitch shifting with preservation of audio quality
- **Adaptive Mixing Strategies**: Different mixing approaches for different types of stems (vocals, drums, bass)
- **Dynamic Processing**: Subtle compression and normalization for professional-sounding output

### Enhanced User Experience

- **Toggle Between Processing Modes**: Choose between standard and enhanced AI processing
- **Multiple Visualization Options**: View audio as waveforms, spectrograms, chromagrams, or tempograms
- **Advanced Settings**: Fine-tune the mashup generation process with detailed controls
- **Detailed Audio Metrics**: View comprehensive analysis of both input tracks and generated mashups

## Requirements

### Standard Requirements

- Python 3.9-3.11
- FFmpeg
- 4GB+ RAM
- 2GB+ disk space

### Enhanced AI Requirements

- Python 3.9-3.11
- 8GB+ RAM recommended
- GPU support (optional, but recommended for faster processing)
- All standard requirements

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/song-mashup.git
cd song-mashup
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Run the application with enhanced AI features:

```bash
python run_enhanced.py --enhanced
```

Or run the standard version:

```bash
python run_enhanced.py --standard
```

## Usage

1. **Upload** 2-3 songs (MP3, WAV, FLAC, OGG, or M4A format)
2. Adjust the **blend ratio** for each track
3. Choose whether to use **enhanced AI models** (if available)
4. Select **visualization type** and adjust **advanced settings** (if desired)
5. Click **Generate Mashup**
6. **Download** your unique AI-generated song mashup

## How It Works

### Standard Processing Flow

1. Audio files are loaded and analyzed for tempo, key, and other musical features
2. Basic stem separation divides tracks into components
3. Tempo and key alignment ensures musical coherence
4. Blending combines the tracks with user-specified ratios
5. The final mashup is generated and made available for download

### Enhanced Processing Flow

1. High-resolution audio analysis extracts detailed musical features
2. NMF-based stem separation isolates vocals, drums, bass, and other elements
3. Sophisticated tempo and key alignment ensures precise musical coherence
4. Adaptive blending uses different strategies for different types of stems
5. Dynamic processing ensures professional sound quality
6. The enhanced mashup is generated with detailed analysis and metrics

## Troubleshooting

### Common Issues

- **Import Errors**: Ensure all required packages are installed

  ```
  pip install -r requirements.txt
  ```

- **Memory Issues**: The enhanced AI models require more RAM

  - Close other applications
  - Use a machine with 8GB+ RAM
  - Try the standard processing mode

- **Missing FFmpeg**: Install FFmpeg following the instructions for your OS

- **Processing Errors**: For some complex audio files, try:
  - Using shorter clips
  - Using the standard processing mode
  - Adjusting blend ratios to emphasize cleaner tracks

## Development

The enhanced AI models are designed with extensibility in mind:

- `song_mashup/models/enhanced/audio_model_enhanced.py`: Contains the enhanced AI models
- `song_mashup/models/enhanced/integration.py`: Provides integration with the base system
- `song_mashup/api/process_enhanced.py`: Enhanced processing workflow
- `app_enhanced.py`: Enhanced Streamlit user interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Librosa](https://librosa.org/) for audio analysis
- [MusicBERT](https://github.com/microsoft/muzic) for music understanding
- [Suno Bark](https://github.com/suno-ai/bark) for audio generation
- [Streamlit](https://streamlit.io/) for the web interface
