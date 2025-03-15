@echo off
REM Setup and run script for AI Song Mashup Generator (Windows version)

echo.
echo [92m===== AI Song Mashup Generator Setup =====[0m
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [91mPython is not installed. Please install Python 3.9 or higher and try again.[0m
    exit /b 1
)

REM Print Python version
python --version
echo.

REM Check if virtual environment exists, create it if it doesn't
if not exist venv (
    echo [93mCreating virtual environment...[0m
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [91mFailed to create virtual environment. Please install venv and try again.[0m
        echo [93mYou might need to run: pip install virtualenv[0m
        exit /b 1
    )
)

REM Activate virtual environment
echo [93mActivating virtual environment...[0m
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo [91mFailed to activate virtual environment.[0m
    exit /b 1
)

REM Install dependencies
echo [93mInstalling dependencies...[0m
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [91mFailed to install some dependencies. Trying to install core dependencies...[0m
    pip install numpy scipy pandas streamlit torch librosa
)

REM Check if FFmpeg is installed
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [93mFFmpeg is not installed. This is required for audio processing.[0m
    echo [93mYou can download FFmpeg from: https://ffmpeg.org/download.html[0m
    
    echo [93mContinue anyway? (y/n)[0m
    set /p response=
    if /i not "%response%"=="y" (
        echo [91mExiting. Please install FFmpeg and try again.[0m
        call venv\Scripts\deactivate
        exit /b 1
    )
) else (
    echo [92mFFmpeg is installed.[0m
)

REM Create necessary directories
echo [93mCreating necessary directories...[0m
mkdir song_mashup\data\uploads song_mashup\data\mashups 2>nul

REM Run the application
echo [92mStarting the Song Mashup Generator...[0m
python run.py

REM Deactivate virtual environment when done
call venv\Scripts\deactivate 