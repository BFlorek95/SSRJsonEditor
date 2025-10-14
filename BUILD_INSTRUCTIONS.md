# SSR JSON Editor - Build Instructions

This document explains how to build standalone executables for **SSR JSON Editor** on Windows and macOS.

## Overview

SSR JSON Editor is a powerful desktop application for viewing, editing, and splitting large JSON files. The build process creates:
- **Windows**: A standalone `.exe` file
- **macOS**: A `.app` bundle that can be installed in Applications

---

## Prerequisites

### Both Platforms
- Python 3.7 or higher installed
- Virtual environment already set up (SSRVenv folder)
- All dependencies installed in the virtual environment

### Windows Only
- Windows 7 or higher
- PowerShell or Command Prompt

### macOS Only
- macOS 10.13 (High Sierra) or higher
- Terminal

---

## Building on macOS

### Quick Build (One Command)

Open Terminal in the project folder and run:

```bash
./build_mac.sh
```

This will:
1. Activate the virtual environment
2. Install PyInstaller
3. Clean previous builds
4. Build the macOS application
5. Create `dist/SSR JSON Editor.app`

### Manual Build

If you prefer to build manually:

```bash
# 1. Activate virtual environment
source SSRVenv/bin/activate

# 2. Install PyInstaller
pip install pyinstaller

# 3. Build the app
pyinstaller build_spec.spec

# The app will be in: dist/SSR JSON Editor.app
```

### Installing the macOS App

1. Open the `dist` folder
2. Drag `SSR JSON Editor.app` to your **Applications** folder
3. On first launch:
   - Right-click the app and select **"Open"**
   - Or go to **System Preferences > Security & Privacy** and allow the app

### Creating a DMG Installer (Optional)

To create a `.dmg` installer for distribution:

```bash
# Install create-dmg tool
brew install create-dmg

# Create DMG
create-dmg \
  --volname "SSR JSON Editor" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "SSR JSON Editor.app" 175 120 \
  --app-drop-link 425 120 \
  "SSR-JSON-Editor-Installer.dmg" \
  "dist/SSR JSON Editor.app"
```

---

## Building on Windows

### Quick Build (One Command)

Open Command Prompt or PowerShell in the project folder and run:

```batch
build_windows.bat
```

This will:
1. Activate the virtual environment
2. Install PyInstaller
3. Clean previous builds
4. Build the Windows executable
5. Create `dist\SSR JSON Editor.exe`

### Manual Build

If you prefer to build manually:

```batch
REM 1. Activate virtual environment
call SSRVenv\Scripts\activate.bat

REM 2. Install PyInstaller
pip install pyinstaller

REM 3. Build the executable
pyinstaller build_spec.spec

REM The executable will be in: dist\SSR JSON Editor.exe
```

### Installing the Windows App

1. Open the `dist` folder
2. Copy `SSR JSON Editor.exe` to any location you want (e.g., Desktop, Program Files)
3. Double-click to run
4. (Optional) Right-click the `.exe` and select **"Create shortcut"** to make a desktop shortcut

### Creating a Windows Installer (Optional)

To create an `.msi` or `.exe` installer for distribution, you can use [Inno Setup](https://jrsoftware.org/isinfo.php):

1. Download and install Inno Setup
2. Create an installer script (`.iss` file) pointing to your `dist\SSR JSON Editor.exe`
3. Compile the installer

---

## Build Output

After a successful build, you'll find:

```
dist/
├── SSR JSON Editor.app     (macOS only)
└── SSR JSON Editor.exe     (Windows only)

build/                      (temporary build files - can be deleted)
```

### File Sizes
- **macOS**: ~15-25 MB (includes Python runtime)
- **Windows**: ~15-25 MB (includes Python runtime)

---

## Customizing the Build

### Adding an Icon

1. **macOS**: Create an `.icns` file and place it in the project folder
2. **Windows**: Create an `.ico` file and place it in the project folder
3. Edit `build_spec.spec` and update the `icon` parameter:

```python
# For Windows
icon='icon.ico'

# For macOS app bundle
app = BUNDLE(
    ...
    icon='icon.icns',
    ...
)
```

### Changing App Name or Version

Edit `build_spec.spec`:

```python
# Change executable name
name='Your New Name',

# Change version (macOS bundle)
info_plist={
    'CFBundleVersion': '2.0.0',
    'CFBundleShortVersionString': '2.0.0',
    ...
}
```

---

## Troubleshooting

### "Command not found" on macOS
Make sure the build script is executable:
```bash
chmod +x build_mac.sh
```

### "PyInstaller not found"
Install it manually:
```bash
pip install pyinstaller
```

### "Module not found" errors during build
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### macOS: "App is damaged and can't be opened"
This is a Gatekeeper security message. To fix:
```bash
xattr -cr "dist/SSR JSON Editor.app"
```

### Windows: Antivirus blocking the .exe
This is common with PyInstaller executables. Add an exception in your antivirus software, or sign the executable with a code signing certificate.

---

## Distribution

### macOS
- Distribute the `.app` file directly (users drag to Applications)
- Or create a `.dmg` installer for a more professional distribution

### Windows
- Distribute the `.exe` file directly
- Or create an installer using Inno Setup or NSIS

### Both Platforms
Consider creating a GitHub Release with:
- `SSR-JSON-Editor-macOS.zip` (containing the .app)
- `SSR-JSON-Editor-Windows.zip` (containing the .exe)
- Version notes and installation instructions

---

## Version Information

- **Current Version**: 1.0.0
- **Python Version**: 3.7+
- **Build Tool**: PyInstaller
- **License**: (Add your license here)

---

## Support

For issues or questions:
- Create an issue on GitHub
- Contact: (Add your contact info)

---

**SSR JSON Editor** - Powerful JSON editing for large files
