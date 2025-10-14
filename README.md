# SSR JSON Editor

A powerful desktop application for viewing, editing, and splitting large JSON files with ease.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📥 Download & Install

### For End Users (No Python Required!)

#### macOS
1. **Download** `SSR-JSON-Editor-macOS.zip` from the [Releases](../../releases) page
2. **Extract** the ZIP file
3. **Drag** `SSR JSON Editor.app` to your **Applications** folder
4. **Right-click** the app and select **"Open"** (first time only)
5. Done! 🎉

**Note:** macOS may warn about the app being from an "unidentified developer" - this is normal for unsigned apps. Just right-click and choose "Open" to bypass this.

#### Windows
1. **Download** `SSR-JSON-Editor-Windows.zip` from the [Releases](../../releases) page
2. **Extract** the ZIP file
3. **Run** `SSR JSON Editor.exe` from anywhere
4. (Optional) Create a desktop shortcut
5. Done! 🎉

**Note:** Windows Defender may show a warning - click "More info" → "Run anyway" to proceed.

---

## ✨ Features

### Core Features
- 📂 **Open Large JSON Files** - Efficiently handles files 50MB+ with lazy loading
- 🌲 **Tree View Navigation** - Browse complex nested JSON structures easily
- 🔍 **Deep Search** - Find any key or value with optional regex support
- ✏️ **Edit & Save** - Modify JSON data and save changes
- ✂️ **Smart File Splitting** - Split large files by size or count with intelligent nesting
- 🎯 **Drag & Drop** - Simply drag JSON files onto the app (macOS)
- 📋 **Paste JSON** - Load JSON directly from your clipboard
- ⚡ **Fast Performance** - Optimized for large datasets

### Advanced Splitting
- **Split by Number of Files** - Evenly distribute data across N files
- **Split by File Size** - Create files up to a specified size (KB/MB/GB)
- **Smart Nesting** - Automatically handles oversized keys by splitting one level deeper
- **User Control** - Choose how to handle oversized structures with interactive prompts

### User Interface
- 🎨 Clean, intuitive interface
- ⌨️ Keyboard shortcuts for all common actions
- 🔄 Progress bars for long operations
- 💾 Auto-detection of file changes
- 📊 File size and structure information

---

## 🚀 Quick Start

### Loading JSON
1. Click **"📁 Open File"** or use **Cmd/Ctrl+O**
2. Or drag a `.json` file onto the app window (macOS)
3. Or paste JSON with **Cmd/Ctrl+V**

### Searching
1. Type in the search bar for quick filtering
2. Click **"Search"** button for deep search through all nested data
3. Enable **"Regex"** checkbox for pattern matching
4. Click **"Clear"** to restore the full tree view

### Editing
1. Select any node in the tree
2. Edit the value in the right panel
3. Click **"Apply Changes"** to save
4. Use **Cmd/Ctrl+S** to save the file

### Splitting Large Files
1. Load your JSON file
2. Click **"✂ Split"** button in the toolbar
3. Choose your split method:
   - **By number of files**: Split into N equal parts
   - **By file size**: Split into chunks of max size
4. Select an output folder
5. Click **"Split"**

When splitting by size, if a top-level key is too large:
- **Create Separate File** - Save the entire key as-is
- **Split One Level Deeper** - Automatically split its contents
- **Skip This Key** - Don't include it

---

## ⌨️ Keyboard Shortcuts

| Action | macOS | Windows |
|--------|-------|---------|
| Open File | `Cmd+O` | `Ctrl+O` |
| Save File | `Cmd+S` | `Ctrl+S` |
| Save As | `Cmd+Shift+S` | `Ctrl+Shift+S` |
| Paste JSON | `Cmd+V` | `Ctrl+V` |
| Search | `Cmd+F` | `Ctrl+F` |
| Close File | `Cmd+W` | `Ctrl+W` |

---

## 💻 System Requirements

### macOS
- macOS 10.13 (High Sierra) or higher
- 100 MB free disk space
- 4 GB RAM (recommended for large files)
- Works on both Intel and Apple Silicon Macs

### Windows
- Windows 7 or higher (Windows 10/11 recommended)
- 100 MB free disk space
- 4 GB RAM (recommended for large files)

---

## 🛠️ Building from Source

### For Developers

Want to build the executable yourself? It's easy!

#### Prerequisites
- Python 3.7 or higher
- Git (to clone the repository)

#### Clone the Repository
```bash
git clone https://github.com/yourusername/SSRJsonEditor.git
cd SSRJsonEditor
```

#### Setup Virtual Environment
```bash
# macOS/Linux
python3 -m venv SSRVenv
source SSRVenv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv SSRVenv
SSRVenv\Scripts\activate
pip install -r requirements.txt
```

#### Build the Application

**macOS:**
```bash
./build_mac.sh
```
Output: `dist/SSR JSON Editor.app`

**Windows:**
```batch
build_windows.bat
```
Output: `dist\SSR JSON Editor.exe`

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build documentation.

---

## 📖 Usage Examples

### Example 1: Loading a Large JSON File
```
1. Click "Open File"
2. Select your 50MB+ JSON file
3. Wait for the progress bar (usually 10-30 seconds)
4. Browse the tree structure
```

### Example 2: Finding All Occurrences of "error"
```
1. Type "error" in the search box
2. Check "Regex" if you want pattern matching
3. Click "Search"
4. Tree filters to show only matching nodes
5. Click "Clear" to restore full view
```

### Example 3: Splitting a 100MB JSON into 20MB Chunks
```
1. Load your 100MB JSON file
2. Click "Split" button
3. Select "Split by file size"
4. Enter "20" and select "MB"
5. Choose output folder
6. Click "Split"
7. Handle oversized keys as prompted
8. Get multiple 20MB JSON files
```

### Example 4: Editing Nested Values
```
1. Navigate the tree to find your value
2. Click on the node to select it
3. Edit in the right panel
4. Click "Apply Changes"
5. Save with Cmd/Ctrl+S
```

---

## 🔧 Troubleshooting

### macOS: "App is damaged and can't be opened"
This is a security warning for unsigned apps. Fix:
```bash
xattr -cr "/path/to/SSR JSON Editor.app"
```
Or right-click → Open → Open again

### macOS: "App can't be opened because it's from an unidentified developer"
- Right-click the app
- Select "Open"
- Click "Open" in the dialog
- The app will now open (and remember this choice)

### Windows: "Windows protected your PC"
- Click "More info"
- Click "Run anyway"
- This is normal for unsigned executables

### Windows: Antivirus blocking the .exe
- Add an exception in your antivirus software
- Or build from source and sign with your own certificate

### Large files loading slowly
- Files over 100MB may take 30-60 seconds to load
- Progress bar shows status
- This is normal - the app loads everything into memory for fast editing

### Can't paste very large JSON
- Clipboard has size limits (usually 10-20MB)
- For larger JSON, save to a file first and use "Open File"

### App crashes or freezes
- Check available RAM (large files need 2-4GB free)
- Try closing other applications
- For files over 500MB, consider splitting them first using command-line tools

---

## 📂 Project Structure

```
SSRJsonEditor/
├── json_editor.py           # Main application code
├── build_mac.sh             # macOS build script
├── build_windows.bat        # Windows build script
├── build_spec.spec          # PyInstaller configuration
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── BUILD_INSTRUCTIONS.md    # Detailed build guide
├── QUICKSTART.md           # Quick start guide
└── dist/                   # Build output directory
    ├── SSR JSON Editor.app     # macOS application
    └── SSR JSON Editor.exe     # Windows executable
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (both macOS and Windows if possible)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/SSRJsonEditor.git
cd SSRJsonEditor

# Setup virtual environment
python3 -m venv SSRVenv
source SSRVenv/bin/activate  # macOS/Linux
# or
SSRVenv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app in development mode
python json_editor.py
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🐛 Bug Reports

Found a bug? Please open an issue on GitHub with:
- **Description**: What happened?
- **Steps to reproduce**: How can we recreate it?
- **Expected behavior**: What should have happened?
- **Screenshots**: If applicable
- **Platform**: macOS/Windows version
- **File size**: How large was your JSON file?

---

## 💡 Feature Requests

Have an idea? Open an issue with:
- **Feature description**: What do you want?
- **Use case**: Why is it useful?
- **Example**: How would it work?

---

## 🙏 Acknowledgments

- Built with Python and tkinter
- Uses [ijson](https://github.com/ICRAR/ijson) for streaming JSON parsing
- Packaged with [PyInstaller](https://pyinstaller.org/)
- Inspired by the need for better large JSON file handling

---

## 📊 Stats

- **Language**: Python 3.7+
- **GUI Framework**: tkinter
- **Lines of Code**: ~2,000
- **File Size**: 10 MB (includes Python runtime)
- **Max Tested File Size**: 500+ MB
- **Platforms**: macOS, Windows (Linux support coming soon)

---

## 🔗 Links

- **GitHub Repository**: [https://github.com/yourusername/SSRJsonEditor](https://github.com/yourusername/SSRJsonEditor)
- **Issue Tracker**: [https://github.com/yourusername/SSRJsonEditor/issues](https://github.com/yourusername/SSRJsonEditor/issues)
- **Releases**: [https://github.com/yourusername/SSRJsonEditor/releases](https://github.com/yourusername/SSRJsonEditor/releases)
- **Documentation**: See docs folder or wiki

---

## 📧 Contact

- **Project Maintainer**: [Your Name]
- **Email**: your.email@example.com
- **Twitter**: [@yourusername]

---

## ⭐ Support

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features
- 🤝 Contributing code
- 📢 Sharing with others

---

## 🎉 Version History

### v1.0.0 (Current)
- ✅ Initial release
- ✅ Open and edit large JSON files
- ✅ Tree view with lazy loading
- ✅ Deep search with regex
- ✅ Smart file splitting by size or count
- ✅ Drag & drop support (macOS)
- ✅ Paste from clipboard
- ✅ Cross-platform (macOS & Windows)
- ✅ Standalone executables (no Python required)

### Coming Soon
- 🔜 Linux support
- 🔜 Syntax highlighting
- 🔜 JSON validation
- 🔜 Export to CSV/XML
- 🔜 Diff/Compare JSON files
- 🔜 Dark mode theme

---

**Made with ❤️ for JSON enthusiasts**

**SSR JSON Editor** - Because working with large JSON files should be easy.
