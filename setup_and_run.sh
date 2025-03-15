#!/bin/bash
# Setup and run script for AI Song Mashup Generator

# Print colorful messages
print_green() {
    echo -e "\033[0;32m$1\033[0m"
}

print_yellow() {
    echo -e "\033[0;33m$1\033[0m"
}

print_red() {
    echo -e "\033[0;31m$1\033[0m"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_red "Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

# Print Python version
PYTHON_VERSION=$(python3 --version)
print_green "Using $PYTHON_VERSION"

# Check if virtual environment exists, create it if it doesn't
if [ ! -d "venv" ]; then
    print_yellow "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_red "Failed to create virtual environment. Please install venv and try again."
        print_yellow "You might need to run: pip install virtualenv"
        exit 1
    fi
fi

# Activate virtual environment
print_yellow "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_red "Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
print_yellow "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_red "Failed to install some dependencies. Trying to install core dependencies..."
    pip install numpy scipy pandas streamlit torch librosa
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    print_yellow "FFmpeg is not installed. This is required for audio processing."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_yellow "On macOS, you can install FFmpeg with Homebrew: brew install ffmpeg"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_yellow "On Ubuntu/Debian, you can install FFmpeg with: sudo apt-get install ffmpeg"
    fi
    
    print_yellow "Continue anyway? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        print_red "Exiting. Please install FFmpeg and try again."
        exit 1
    fi
else
    print_green "FFmpeg is installed: $(ffmpeg -version | head -n 1)"
fi

# Create necessary directories
print_yellow "Creating necessary directories..."
mkdir -p song_mashup/data/uploads song_mashup/data/mashups

# Run the application
print_green "Starting the Song Mashup Generator..."
python run.py

# Deactivate virtual environment when done
deactivate 