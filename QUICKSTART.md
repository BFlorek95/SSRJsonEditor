# Quick Start Guide - SSR JSON Editor

## Installation (5 minutes)

1. **Install Python 3.7+** (if not already installed)
   - Mac: `brew install python3` or download from python.org
   - Windows: Download from python.org
   - Linux: `sudo apt-get install python3 python3-pip`

2. **Install Dependencies**
   ```bash
   # Mac/Linux
   pip3 install -r requirements.txt

   # Windows
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   # Mac/Linux
   ./run.sh

   # Windows
   run.bat

   # Or directly
   python json_editor.py
   ```

## First Steps

### Open a File
1. Click **File → Open** (or press `Ctrl/Cmd+O`)
2. Select your JSON file
3. Wait for it to load (large files may take a moment)

### Navigate the Tree
- Click the `▶` triangles to expand nodes
- Click the `▼` triangles to collapse nodes
- Scroll up/down to navigate through the hierarchy
- Click any node to view its value in the right panel

### Search for Something
1. Type your search term in the search box at the top
2. Check "Regex" if you want to use regular expressions
3. Click "Find" or press Enter
4. The first match will be selected and scrolled into view
5. Click "Find" again to find the next match

### Edit a Value
1. Select a node in the tree
2. Edit the value in the right panel
3. Click "Apply Changes" to save to memory
4. Use `Ctrl/Cmd+S` to save to disk

### Save Part of the JSON
1. Right-click on any node in the tree
2. Select "Save Node to File"
3. Choose where to save it
4. That node and all its children are saved as a new JSON file

## Common Tasks

### View a Specific Path
1. Use search to find the key you're looking for
2. Or manually expand the tree to navigate to it
3. Double-click to focus and expand

### Extract Data
1. Find the node you want to extract
2. Right-click → "Save Node to File"
3. Done! You now have that data in a separate file

### Copy a Path
1. Right-click on any node
2. Select "Copy Path"
3. The full path is now in your clipboard

### Search with Patterns
1. Check the "Regex" checkbox
2. Enter a pattern like `user.*email` to find all email fields under user keys
3. Click "Find"

## Tips & Tricks

1. **Large Files**: Don't click "Expand All" on huge files - navigate incrementally
2. **Search First**: Use search to jump directly to what you need
3. **Save Often**: Use `Ctrl/Cmd+S` frequently when editing
4. **Right-Click**: The context menu is your friend - use it often
5. **Double-Click**: Quick way to expand/collapse and focus

## Keyboard Shortcuts Cheat Sheet

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Open | `Cmd+O` | `Ctrl+O` |
| Save | `Cmd+S` | `Ctrl+S` |
| Save As | `Cmd+Shift+S` | `Ctrl+Shift+S` |
| Close | `Cmd+W` | `Ctrl+W` |
| Find | `Cmd+F` | `Ctrl+F` |

## Troubleshooting

**Q: App won't start**
- Make sure Python 3.7+ is installed
- Run `pip install -r requirements.txt` to install dependencies

**Q: File won't load**
- Check that it's valid JSON
- For very large files (>500MB), loading may take 1-2 minutes

**Q: Search not finding anything**
- Make sure the section you're searching is expanded (loaded)
- Try expanding more of the tree first
- Check if "Regex" is checked - turn it off for simple searches

**Q: Changes not saving**
- Click "Apply Changes" first (in the right panel)
- Then use `Ctrl/Cmd+S` to save to file

**Q: Out of memory**
- Close and reopen the file
- Don't use "Expand All" on very large files
- Navigate to only the sections you need

## Example Workflow

**Scenario**: You have a 500MB JSON log file and need to extract all error entries.

1. Open the file: `Ctrl/Cmd+O`
2. Search for "error": Type "error", click Find
3. Review the first error node
4. Right-click → "Save Node to File" → save as `error_001.json`
5. Click Find again for the next error
6. Repeat as needed

**Scenario**: You need to edit a configuration value deep in a nested structure.

1. Open the file: `Ctrl/Cmd+O`
2. Use search to find the key: `Ctrl/Cmd+F`, type the key name
3. Double-click the found node to focus on it
4. Edit the value in the right panel
5. Click "Apply Changes"
6. Save: `Ctrl/Cmd+S`

## Getting Help

- See `USAGE.md` for detailed usage instructions
- See `FEATURES.md` for complete feature list
- Check `README.md` for technical details

## Testing the App

A sample JSON file is included: `test_sample.json`

Try it out:
```bash
python json_editor.py
# Then open test_sample.json
```

Generate larger test files:
```bash
# Generate 1MB to 100MB test files
python generate_test_json.py

# Generate a 2GB test file (takes several minutes)
python generate_test_json.py --huge
```

Enjoy using SSR JSON Editor!
