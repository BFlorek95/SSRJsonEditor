# SSR JSON Editor - Quick Start Guide

## For Users (Just Want to Use the App)

### macOS
1. Download `SSR JSON Editor.app`
2. Drag it to your **Applications** folder
3. Right-click and select **"Open"** (first time only)
4. Done! Use it like any other Mac app

### Windows
1. Download `SSR JSON Editor.exe`
2. Put it anywhere (Desktop, Program Files, etc.)
3. Double-click to run
4. Done!

---

## For Developers (Want to Build the App)

### macOS - One Command Build
```bash
./build_mac.sh
```
Output: `dist/SSR JSON Editor.app`

### Windows - One Command Build
```batch
build_windows.bat
```
Output: `dist\SSR JSON Editor.exe`

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed information.

---

## Features

- **Open Large JSON Files**: Handles 50MB+ files efficiently
- **Tree View Navigation**: Browse nested JSON structures
- **Deep Search**: Find any key or value with regex support
- **Edit & Save**: Modify JSON data and save changes
- **Split Files**: Split large JSON into smaller files by size or count
- **Drag & Drop**: Just drag JSON files onto the app (macOS)
- **Paste JSON**: Paste JSON directly from clipboard

---

## Usage Tips

### Loading Files
- Click **"Open File"** button
- Or drag a `.json` file onto the app (macOS)
- Or paste JSON with **Cmd/Ctrl+V**

### Searching
- Use the search bar for quick filtering
- Click **"Search"** for deep search through all nested data
- Enable **"Regex"** for pattern matching

### Splitting Files
1. Click **"Split"** button
2. Choose split method:
   - **By number of files**: Evenly divide into N files
   - **By file size**: Split based on max file size (KB/MB/GB)
3. Select output folder
4. Click **"Split"**

### Keyboard Shortcuts
- **Cmd/Ctrl+O**: Open file
- **Cmd/Ctrl+S**: Save file
- **Cmd/Ctrl+Shift+S**: Save as
- **Cmd/Ctrl+F**: Search
- **Cmd/Ctrl+V**: Paste JSON
- **Cmd/Ctrl+W**: Close file

---

## System Requirements

### macOS
- macOS 10.13 (High Sierra) or higher
- 100 MB free disk space
- 4 GB RAM recommended for large files

### Windows
- Windows 7 or higher
- 100 MB free disk space
- 4 GB RAM recommended for large files

---

## Troubleshooting

### macOS: "App can't be opened"
Right-click the app → Select **"Open"** → Click **"Open"** again

### Windows: Antivirus warning
This is common with PyInstaller apps. The app is safe - add an exception if needed.

### Large files loading slowly
Files over 100MB may take time to load. Progress bar will show status.

### Can't paste large JSON
Clipboard has size limits. For very large JSON, save to a file first and use **"Open File"**.

---

**Enjoy using SSR JSON Editor!**
