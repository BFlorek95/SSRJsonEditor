# Installation Guide - SSR JSON Editor

## macOS Installation

### Step 1: Install tkinter support
```bash
brew install python-tk@3.13
```

### Step 2: Install Python dependencies
```bash
# If using a virtual environment (recommended)
source SSRVenv/bin/activate
pip install -r requirements.txt

# Or install globally
pip3 install -r requirements.txt
```

### Step 3: Run the application
```bash
# With virtual environment
source SSRVenv/bin/activate
python json_editor.py

# Or use the launch script
./run.sh

# Or directly
python3 json_editor.py
```

## Quick Start (macOS)

For your current virtual environment setup:

```bash
# 1. Make sure you're in the project directory
cd /Users/brettflorek/Documents/GitHub/SSRJsonEditor

# 2. Activate virtual environment
source SSRVenv/bin/activate

# 3. Install ijson
pip install ijson

# 4. Run the application
python json_editor.py
```

## Windows Installation

### Step 1: Download Python
Download and install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH"
- Check "tcl/tk and IDLE" during installation

### Step 2: Install dependencies
```cmd
pip install -r requirements.txt
```

### Step 3: Run the application
```cmd
run.bat
```

Or directly:
```cmd
python json_editor.py
```

## Linux Installation

### Ubuntu/Debian
```bash
# Install tkinter
sudo apt-get update
sudo apt-get install python3-tk

# Install dependencies
pip3 install -r requirements.txt

# Run
./run.sh
```

### Fedora/RHEL
```bash
# Install tkinter
sudo dnf install python3-tkinter

# Install dependencies
pip3 install -r requirements.txt

# Run
./run.sh
```

### Arch Linux
```bash
# Install tkinter
sudo pacman -S tk

# Install dependencies
pip3 install -r requirements.txt

# Run
./run.sh
```

## Verification

Test that everything is installed correctly:

```bash
python3 -c "import tkinter; import ijson; print('✓ Ready to run!')"
```

If you see "✓ Ready to run!" then you can launch the application.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

### Quick Fixes

**macOS: "No module named '_tkinter'"**
```bash
brew install python-tk@3.13
```

**Any OS: "No module named 'ijson'"**
```bash
pip install ijson
# or
pip3 install ijson
```

**Virtual Environment Issues**
```bash
# Make sure virtual environment is activated
source SSRVenv/bin/activate  # macOS/Linux
SSRVenv\Scripts\activate     # Windows

# Then install
pip install -r requirements.txt
```

## Requirements

- **Python**: 3.7 or higher
- **Packages**: ijson (will be installed automatically)
- **System**: tkinter support (usually built-in, except Homebrew Python on macOS)

## First Run

After installation, test with the sample file:

```bash
python json_editor.py
# Then: File → Open → test_sample.json
```

Or generate larger test files:

```bash
python generate_test_json.py
# Creates test files from 1MB to 100MB

python generate_test_json.py --huge
# Creates a 2GB test file (takes several minutes)
```
