@echo off
echo Checking System...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.10 and check "Add to PATH".
    pause
    exit
)

echo Installing Libraries...
pip install SpeechRecognition edge-tts pygame screen_brightness_control pyautogui pytesseract Pillow numpy customtkinter tinydb pyaudio AppOpener opencv-python psutil

echo Checking AI Models...
ollama list > models.txt
findstr "dolphin-llama3" models.txt >nul
if %errorlevel% neq 0 (
    echo Downloading Chat Brain...
    ollama pull dolphin-llama3
) else (
    echo Chat Brain found.
)

findstr "llava" models.txt >nul
if %errorlevel% neq 0 (
    echo Downloading Vision Brain...
    ollama pull llava
) else (
    echo Vision Brain found.
)

del models.txt
echo Setup Complete.
pause