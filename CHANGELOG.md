# Changelog

## [1.1.0] - 2025-04-01

### Added

- Enhanced AI models for improved audio analysis and processing
- Advanced stem separation using NMF (Non-Negative Matrix Factorization)
- More sophisticated key and tempo alignment algorithms
- Better musical feature extraction with higher resolution analysis
- Audio complexity scoring and detailed metadata
- Toggle between standard and enhanced processing modes
- Multiple audio visualization options (waveform, spectrogram, etc.)
- Advanced processing settings for fine-tuning mashup generation

### Changed

- Improved key detection using template-based correlation
- Enhanced audio blending with adaptive mixing strategies
- Better error handling and graceful fallbacks
- More detailed logging for debugging

## [1.0.1] - 2025-03-15

### Fixed

- Fixed session state initialization issues in the Streamlit app
- Resolved threading issues that were causing "missing ScriptRunContext" errors
- Updated session state access to use dictionary notation for better consistency
- Removed unnecessary FastAPI dependency
- Added Windows setup script (setup_and_run.bat) for easier setup on Windows machines

## [1.0.0] - 2024-03-15

### Major Changes

- Converted the web interface from FastAPI + HTML to Streamlit
- Updated package dependencies for Python 3.11 compatibility
- Added better error handling and dependency checking

### Added

- Streamlit-based user interface with improved interactivity
- Dependency checking system that provides helpful error messages
- Shell script for easy setup and running on macOS and Linux
- Display of audio details (tempo, key, duration) for each uploaded track
- System information display in sidebar
- Python version compatibility information

### Changed

- Updated `suno-bark` to version 0.1.5 (compatible with Python 3.11)
- Improved error handling in audio processing modules
- Enhanced the BarkGenerator class to handle API differences between versions
- Made the user interface more responsive with real-time feedback

### Removed

- FastAPI backend and HTML templates
- Dependency on audiocraft (not compatible with Python 3.11)

### Fixed

- Compatibility issues with Python 3.11
- Audio processing error handling
- Temporary file cleanup reliability

## Next Steps

- Add user account system for saving favorite mashups
- Implement social sharing features
- Create preset templates for common mashup styles
- Add live streaming of processing status
