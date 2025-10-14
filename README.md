# SSR JSON Editor

A high-performance, cross-platform GUI application for viewing and editing very large JSON files (2GB+).

## Features

- **Large File Support**: Handles JSON files up to 2GB and beyond using streaming and lazy loading
- **Tree View**: Hierarchical, scrollable view of JSON structure with expandable nodes
- **Lazy Loading**: Only loads visible portions of the JSON tree for optimal performance
- **Edit Capabilities**: Edit values inline with real-time updates
- **Advanced Search**:
  - Regular text search (case-insensitive)
  - Regex pattern matching support
  - Search through entire JSON hierarchy
- **Context Menu Features**:
  - Right-click any node to save it as a separate JSON file
  - Copy path to clipboard
  - Quick expand/collapse/navigate actions
- **Double-Click Navigation**: Double-click nodes to focus and expand/collapse
- **Pretty Formatting**: Displays JSON in a readable, indented format
- **Cross-Platform**: Works seamlessly on Mac, Windows, and Linux

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Install Dependencies

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

**Windows:**
```cmd
pip install -r requirements.txt
```

## Usage

### Quick Start

**Mac/Linux:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

**Or run directly:**
```bash
python json_editor.py
```

Then use File → Open (Ctrl+O or Cmd+O) to load a JSON file.

## Key Features Explained

### Hierarchical Scrollable View
The left panel displays your JSON in a tree structure that's fully scrollable, making it easy to navigate even the largest files. Each node shows:
- Objects with `{count}` notation
- Arrays with `[count]` notation
- Values with their actual content (truncated if long)

### Search Functionality
- **Text Search**: Type any text and click "Find" to search through keys and values
- **Regex Search**: Check the "Regex" checkbox to use regular expressions for advanced pattern matching
- **Enter to Search**: Press Enter in the search box to find the next match

### Right-Click Context Menu
Right-click on any node in the hierarchy to:
- **Save Node to File**: Export just that key and its contents to a separate JSON file
- **Copy Path**: Copy the full path to that node to your clipboard
- **Expand/Collapse Node**: Quick node management
- **Go to Node**: Jump to and focus on the selected node

### Double-Click Navigation
Double-click any node to:
- Focus and scroll to that position in the tree
- Automatically expand or collapse container nodes (objects/arrays)

## Keyboard Shortcuts

**Mac:**
- `Cmd+O` - Open file
- `Cmd+S` - Save file
- `Cmd+Shift+S` - Save as
- `Cmd+W` - Close file
- `Cmd+F` - Focus search

**Windows/Linux:**
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+Shift+S` - Save as
- `Ctrl+W` - Close file
- `Ctrl+F` - Focus search

## Technical Details

- Uses `ijson` for streaming JSON parsing
- Implements virtual tree view for memory efficiency
- Only parses and displays visible nodes on-demand
- Supports incremental loading as you navigate the tree
- Cross-platform compatibility with platform-specific keyboard shortcuts
