# Troubleshooting Guide - SSR JSON Editor

## macOS: "ModuleNotFoundError: No module named '_tkinter'"

This error occurs because Homebrew's Python doesn't include tkinter by default.

### Quick Fix (Recommended)

Run the installation script:
```bash
./install_mac.sh
```

### Manual Solutions

#### Solution 1: Install python-tk via Homebrew
```bash
brew install python-tk@3.13
```

After installation, verify:
```bash
python3 -c "import tkinter; print('Success!')"
```

#### Solution 2: Use macOS System Python
macOS comes with Python that includes tkinter:
```bash
# Install ijson for system Python
/usr/bin/python3 -m pip install --user ijson

# Run with system Python
/usr/bin/python3 json_editor.py
```

#### Solution 3: Install Python from python.org
Download Python from [python.org](https://www.python.org/downloads/) - it includes tkinter by default.

### Verification

Test if tkinter is available:
```bash
python3 -c "import tkinter; tkinter._test()"
```

This should open a small test window if tkinter is working.

## Windows: tkinter Issues

Tkinter is usually included with Python on Windows. If you have issues:

1. **Reinstall Python** from python.org
   - Make sure to check "tcl/tk and IDLE" during installation

2. **Verify installation**:
   ```cmd
   python -c "import tkinter; print('Success!')"
   ```

## Linux: tkinter Missing

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### Fedora/RHEL
```bash
sudo dnf install python3-tkinter
```

### Arch Linux
```bash
sudo pacman -S tk
```

## Other Common Issues

### Issue: "No module named 'ijson'"
**Solution**: Install dependencies
```bash
pip3 install -r requirements.txt
```

### Issue: File won't open / Application crashes
**Causes**:
1. File is not valid JSON
2. File is too large (>2GB untested)
3. Insufficient memory

**Solutions**:
1. Validate JSON: `python3 -m json.tool yourfile.json`
2. Try a smaller file first
3. Close other applications to free memory

### Issue: Search not finding results
**Causes**:
1. Node not expanded/loaded
2. Regex pattern invalid
3. Case sensitivity issue

**Solutions**:
1. Expand more nodes before searching
2. Uncheck "Regex" for simple searches
3. Search is case-insensitive by default

### Issue: Changes not saving
**Causes**:
1. Didn't click "Apply Changes"
2. File is read-only
3. Insufficient disk space

**Solutions**:
1. Click "Apply Changes" before saving
2. Check file permissions
3. Check available disk space

### Issue: Application is slow
**Causes**:
1. File too large
2. Too many nodes expanded
3. Insufficient memory

**Solutions**:
1. Use lazy loading (don't expand all)
2. Collapse unused sections
3. Restart the application
4. Close other applications

### Issue: Keyboard shortcuts not working
**Causes**:
1. Wrong modifier key (Cmd vs Ctrl)
2. Focus in wrong panel
3. Operating system conflicts

**Solutions**:
1. Mac uses Cmd, Windows/Linux use Ctrl
2. Click on the tree or editor first
3. Check OS keyboard shortcut settings

## Platform-Specific Notes

### macOS
- Use `Cmd` key for shortcuts
- Right-click may require Control+Click on older Macs
- Homebrew Python requires `python-tk` package

### Windows
- Use `Ctrl` key for shortcuts
- May need to "Run as Administrator" for some file locations
- Use `run.bat` for easy launching

### Linux
- Use `Ctrl` key for shortcuts
- May need `python3-tk` package from your distro
- Use `./run.sh` for easy launching

## Getting Help

If you're still experiencing issues:

1. **Check Python version**:
   ```bash
   python3 --version
   ```
   (Requires 3.7 or higher)

2. **Check installed packages**:
   ```bash
   pip3 list | grep ijson
   ```

3. **Test tkinter**:
   ```bash
   python3 -c "import tkinter; tkinter._test()"
   ```

4. **Check file**:
   ```bash
   python3 -m json.tool yourfile.json
   ```

## Debug Mode

Run with verbose output:
```bash
python3 -v json_editor.py
```

This will show detailed import information and help identify issues.

## System Requirements

### Minimum
- Python 3.7+
- 2 GB RAM
- 100 MB disk space
- macOS 10.12+, Windows 7+, or Linux with X11

### Recommended
- Python 3.9+
- 4 GB RAM
- 500 MB disk space
- macOS 11+, Windows 10+, or Linux with modern desktop

## Known Limitations

1. **Files >2GB**: Untested, may have issues
2. **Very deep nesting**: May cause recursion limits
3. **Concurrent editing**: Not supported
4. **Binary data**: Not supported
5. **Invalid JSON**: Will fail to load

## Contact & Support

For persistent issues:
1. Check the documentation (README.md, USAGE.md, FEATURES.md)
2. Review the interface guide (INTERFACE_GUIDE.md)
3. Try the test sample (test_sample.json)
4. Generate test data (generate_test_json.py)

## Quick Diagnosis

Run this diagnostic command:
```bash
python3 << 'EOF'
import sys
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

try:
    import tkinter
    print("✓ tkinter: Available")
except ImportError as e:
    print(f"✗ tkinter: {e}")

try:
    import ijson
    print("✓ ijson: Available")
except ImportError as e:
    print(f"✗ ijson: {e}")
EOF
```

This will show exactly what's available on your system.
