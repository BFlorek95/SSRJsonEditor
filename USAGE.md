# SSR JSON Editor - Usage Guide

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python json_editor.py
```

## Features Guide

### Opening Files

- **Menu**: File → Open (Cmd+O)
- **File Types**: Supports .json files
- **Large Files**: The application will warn you when opening files larger than 100MB

### Navigation

- **Tree View**: The left panel shows the JSON structure as an expandable tree
- **Lazy Loading**: Child nodes are loaded only when you expand them, keeping memory usage low
- **Path Display**: The current path is shown at the top of the right panel
- **Search**: Use the search bar or Cmd+F to find keys/values in the tree

### Viewing Data

- **Expand/Collapse**: Click the triangles to expand or collapse nodes
- **Value Display**: Select any node to view its value in the right panel
- **Pretty Formatting**: Complex objects and arrays are automatically formatted with proper indentation
- **Truncation**: Very long values (>100 characters) are truncated in the tree view but shown in full in the editor

### Editing Data

1. Select a node in the tree view
2. Edit the value in the right panel text editor
3. Click "Apply Changes" to save the change to memory
4. The status will show "Modified" when changes are pending
5. Use File → Save (Cmd+S) to write changes to disk

**Editing Tips**:
- For simple values (strings, numbers, booleans), just type the new value
- For objects and arrays, use valid JSON format
- Invalid JSON will be treated as a string value
- Click "Revert" to undo changes before applying them

### Saving Files

- **Save**: File → Save (Cmd+S) - Saves to the current file
- **Save As**: File → Save As (Cmd+Shift+S) - Saves to a new file
- **Auto-prompt**: The application will prompt you to save if you have unsaved changes when closing

### Search

1. Type your search term in the search bar
2. Click "Find" or press Enter
3. The tree will select and scroll to the next matching node
4. Search is case-insensitive and matches anywhere in the key or value

### Keyboard Shortcuts

- **Cmd+O**: Open file
- **Cmd+S**: Save file
- **Cmd+Shift+S**: Save as
- **Cmd+W**: Close file
- **Cmd+F**: Focus search bar

### Menu Options

**File Menu**:
- Open: Load a JSON file
- Save: Save changes to current file
- Save As: Save to a new file
- Close: Close the current file
- Exit: Quit the application

**Edit Menu**:
- Find: Focus the search bar
- Expand All: Expand all nodes (use cautiously with large files)
- Collapse All: Collapse all nodes

## Performance Tips

### For Very Large Files (>100MB)

1. **Don't Expand All**: Expanding all nodes loads everything into memory
2. **Use Search**: Search helps you jump directly to the data you need
3. **Navigate Incrementally**: Expand only the sections you need to work with
4. **Lazy Loading**: The application loads child nodes only when you expand them
5. **Batch Limits**: Arrays and objects with >1000 items show only the first 1000 with a "..." indicator

### Memory Management

- The application keeps only the visible portion of the tree in memory
- Unexpanded nodes remain unloaded
- Collapsing a node frees memory for its children
- Large string values are truncated in the tree view

## Troubleshooting

### File Won't Load
- Check that the file is valid JSON
- For very large files, be patient - loading may take 30-60 seconds
- Check available disk space and memory

### Application Freezes
- This can happen when expanding very large arrays or objects
- Close and reopen the file
- Navigate to smaller sections of the data

### Changes Not Saving
- Ensure you clicked "Apply Changes" before saving
- Check file permissions
- Ensure you have disk space available

### Search Not Working
- Search only works on loaded (visible) nodes
- Expand sections to make them searchable
- Search is case-insensitive

## Testing with Sample Data

Generate test files:
```bash
# Generate small to medium test files (1MB - 100MB)
python generate_test_json.py

# Generate large 2GB test file (takes several minutes)
python generate_test_json.py --huge
```

This creates:
- `test_small.json` (1 MB) - Quick testing
- `test_medium.json` (10 MB) - Nested structures
- `test_large_array.json` (50 MB) - Large arrays
- `test_large_mixed.json` (100 MB) - Mixed structures
- `test_huge.json` (2 GB) - Only with --huge flag

## Limitations

- **File Size**: Tested up to 2GB, larger files may work but are untested
- **Editing**: Currently supports editing individual values, not adding/removing keys
- **Undo**: No multi-level undo - use "Revert" before applying changes
- **Concurrent Editing**: No support for multiple users editing the same file

## Best Practices

1. **Start Small**: Test with smaller files first
2. **Backup**: Keep backups of important files before editing
3. **Incremental Saves**: Save frequently when making multiple changes
4. **Search First**: Use search to find what you need instead of expanding everything
5. **Close When Done**: Close files to free memory when finished editing
