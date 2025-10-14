# SSR JSON Editor - Interface Guide

## Main Window Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File  Edit                                                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Loaded: myfile.json                            Size: 125.3 MB          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                ┃                                        ┃
┃  LEFT PANEL: Tree View         ┃  RIGHT PANEL: Value Editor            ┃
┃  ━━━━━━━━━━━━━━━━━━━━━━━━━━━  ┃  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ┃
┃                                ┃                                        ┃
┃  Search: [________] [x]Regex   ┃  Value Editor                         ┃
┃         [Find]                 ┃  ─────────────                        ┃
┃                                ┃                                        ┃
┃  ┌────────────────────┐        ┃  Path: users > [0] > name             ┃
┃  │ ▼ Root {}          │ ▲      ┃                                        ┃
┃  │   ▼ users [2]      │ │      ┃  ┌──────────────────────────────┐    ┃
┃  │     ▶ [0] {}       │ │      ┃  │ {                            │ ▲   ┃
┃  │     ▼ [1] {}       │ │      ┃  │   "name": "Alice",           │ │   ┃
┃  │       name: Alice  │ │      ┃  │   "email": "alice@ex.com",   │ │   ┃
┃  │       email: ali...│ │      ┃  │   "age": 28                  │ │   ┃
┃  │   ▶ config {}      │ │      ┃  │ }                            │ │   ┃
┃  │   ▶ data []        │ │      ┃  │                              │ │   ┃
┃  │                    │ │      ┃  │                              │ │   ┃
┃  │                    │ │      ┃  │                              │ │   ┃
┃  │                    │ ▼      ┃  │                              │ ▼   ┃
┃  └────────────────────┘        ┃  └──────────────────────────────┘    ┃
┃  ◀─────────────────────▶       ┃                                        ┃
┃                                ┃  [Apply Changes] [Revert]  ✓Saved     ┃
┃                                ┃                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Panel Descriptions

### Status Bar (Top)
```
┌──────────────────────────────────────────────────────┐
│ Loaded: myfile.json                Size: 125.3 MB    │
└──────────────────────────────────────────────────────┘
```
- Shows current file name
- Displays file size
- Status messages (Loading, Modified, Error, etc.)

### Left Panel - Tree View

#### Search Bar
```
Search: [your search term here]  [✓] Regex  [Find]
```
- Text input for search terms
- Checkbox to enable regex mode
- Find button (or press Enter)

#### Tree Structure
```
▼ Root {}
  ▼ users [2]
    ▶ [0] {}
    ▼ [1] {}
      name: "Alice"
      email: "alice@example.com"
      ▶ settings {}
  ▶ config {}
  ▶ data [1000]
```

**Symbols:**
- `▶` = Collapsed node (click to expand)
- `▼` = Expanded node (click to collapse)
- `{}` = Object with item count
- `[]` = Array with item count
- `: value` = Leaf node with value

**Interactions:**
- Single click: Select and view
- Double-click: Focus and toggle expand/collapse
- Right-click: Open context menu

#### Context Menu (Right-Click)
```
┌──────────────────────┐
│ Save Node to File    │
│ Copy Path            │
│ ──────────────────── │
│ Expand Node          │
│ Collapse Node        │
│ ──────────────────── │
│ Go to Node           │
└──────────────────────┘
```

### Right Panel - Value Editor

#### Path Display
```
Path: users > [1] > settings > theme
```
Shows the full path from root to selected node

#### Value Text Area
```
┌─────────────────────────────────┐
│ {                               │
│   "theme": "dark",              │
│   "notifications": true         │
│ }                               │
│                                 │
└─────────────────────────────────┘
```
- Displays selected node's value
- Editable for making changes
- Pretty-printed JSON for objects/arrays
- Plain text for primitive values

#### Action Buttons
```
[Apply Changes]  [Revert]     Status: ✓ Saved
```
- **Apply Changes**: Save edits to memory
- **Revert**: Undo current edits
- **Status**: Shows current edit state

## Menu Bar

### File Menu
```
File
├── Open             Ctrl+O
├── Save             Ctrl+S
├── Save As          Ctrl+Shift+S
├── ─────────────────────────
├── Close            Ctrl+W
├── ─────────────────────────
└── Exit
```

### Edit Menu
```
Edit
├── Find             Ctrl+F
├── Expand All
└── Collapse All
```

## Visual States

### Tree Node States

**Object (Collapsed):**
```
▶ users {2}
```

**Object (Expanded):**
```
▼ users {2}
  ▶ [0] {}
  ▶ [1] {}
```

**Array (Collapsed):**
```
▶ items [100]
```

**Array (Expanded):**
```
▼ items [100]
  [0]: "value1"
  [1]: "value2"
  ...
```

**Value (Leaf Node):**
```
name: "Alice"
age: 28
active: true
```

**Large Array (Batched):**
```
▼ items [5000]
  [0]: "item1"
  [1]: "item2"
  ...
  [999]: "item1000"
  ... (4000 more items)
```

### Status Messages

**Loading:**
```
Loading: largefile.json...
```

**Loaded:**
```
Loaded: largefile.json          Size: 250.5 MB
```

**Modified:**
```
Modified: largefile.json *      Size: 250.5 MB
```

**Error:**
```
Error loading file
```

### Edit Status

**Not Modified:**
```
[Apply Changes] [Revert]
```

**Modified (Orange):**
```
[Apply Changes] [Revert]     Modified
```

**Saved (Green):**
```
[Apply Changes] [Revert]     ✓ Saved
```

**Path Copied (Blue):**
```
[Apply Changes] [Revert]     Path copied!
```

## Example Workflows

### Opening and Viewing a File

```
1. Click: File → Open (or Ctrl+O)
2. Select: mydata.json
3. Wait: [Loading indicator]
4. View: Tree appears in left panel

   ▼ Root {}
     ▶ section1 {}
     ▶ section2 []
     ▶ section3 {}
```

### Searching for Data

```
1. Type in search box: "email"
2. Optional: Check [✓] Regex
3. Click: [Find]
4. Result: First match is selected

   ▼ users [2]
     ▶ [0] {}
     ▼ [1] {}
       name: "Alice"
   >>> email: "alice@example.com" <<<  (selected)
```

### Editing a Value

```
1. Click on node: settings > theme
2. Right panel shows:

   Path: settings > theme
   ┌──────────────┐
   │ "dark"       │
   └──────────────┘

3. Edit to: "light"
4. Click: [Apply Changes]
5. Status: Modified (orange)
6. Save: Ctrl+S
7. Status: ✓ Saved (green)
```

### Saving a Node to File

```
1. Right-click on: users > [0]
2. Select: "Save Node to File"
3. Dialog appears:

   Save as: [0].json
   [Save] [Cancel]

4. Click: [Save]
5. Message: "Node saved to: /path/to/[0].json"
```

### Copying a Path

```
1. Right-click on: config > database > host
2. Select: "Copy Path"
3. Clipboard now contains:
   "config > database > host"
4. Status: "Path copied!" (blue)
```

## Color Scheme

### Default Colors
- **Background**: White/Light Gray
- **Text**: Black
- **Selected**: Blue highlight
- **Status Messages**:
  - Green: Success/Saved
  - Orange: Modified/Warning
  - Blue: Information
  - Red: Error

### Tree Indicators
- `▶` and `▼`: Standard text color
- Object `{}`: Standard text color
- Array `[]`: Standard text color
- Values: Standard text color

## Scrollbar Behavior

### Tree View
- **Vertical**: Scroll through nodes
- **Horizontal**: See long keys/values
- **Auto-scroll**: When selecting search results

### Value Editor
- **Vertical**: Scroll through large values
- **Horizontal**: See long lines
- **Word-wrap**: Enabled for readability

## Responsive Behavior

### Window Resizing
- Panels resize proportionally
- Splitter can be dragged to adjust panel sizes
- Minimum sizes maintained for usability

### Large Files
- Progress indicators during load
- Tree loads incrementally
- Smooth scrolling maintained

### Search Results
- Auto-scroll to show result
- Result highlighted
- Context visible around match

## Accessibility

### Keyboard Navigation
- Tab: Switch between panels
- Arrow keys: Navigate tree
- Enter: Expand/collapse
- Ctrl/Cmd shortcuts: File operations

### Mouse Operations
- Single click: Select
- Double-click: Focus and toggle
- Right-click: Context menu
- Scroll wheel: Vertical scroll
- Shift+scroll: Horizontal scroll (if supported)

---

This interface provides an intuitive, efficient way to work with large JSON files while maintaining performance and usability.
