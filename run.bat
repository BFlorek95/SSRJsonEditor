@echo off
REM Launch script for SSR JSON Editor (Windows)

echo Starting SSR JSON Editor...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed.
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import ijson" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
python json_editor.py

pause
