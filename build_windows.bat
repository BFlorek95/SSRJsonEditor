@echo off
REM Build script for Windows

echo ==========================================
echo Building SSR JSON Editor for Windows
echo ==========================================

REM Activate virtual environment
call SSRVenv\Scripts\activate.bat

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the Windows executable
echo Building Windows executable...
pyinstaller build_spec.spec

REM Check if build was successful
if exist "dist\SSR JSON Editor.exe" (
    echo.
    echo ==========================================
    echo Build successful!
    echo ==========================================
    echo.
    echo Windows EXE Location: dist\SSR JSON Editor.exe
    echo.
    echo To install:
    echo 1. Open the 'dist' folder
    echo 2. Copy 'SSR JSON Editor.exe' to any location you want
    echo 3. Double-click to run
    echo.
    echo Optional: Create a desktop shortcut by right-clicking
    echo the .exe and selecting "Create shortcut"
    echo.
) else (
    echo.
    echo Build failed!
    echo Check the output above for errors.
    echo.
)

pause
