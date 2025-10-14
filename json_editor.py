import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import ijson
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import threading
import platform


class JSONNode:
    """Represents a node in the JSON tree structure."""

    def __init__(self, key: str, value: Any, parent=None, node_type: str = "value"):
        self.key = key
        self.value = value
        self.parent = parent
        self.children = []
        self.node_type = node_type  # 'object', 'array', 'value'
        self.loaded = False
        self.tree_id = None

    def get_path(self) -> List[str]:
        """Get the full path from root to this node."""
        path = []
        current = self
        while current.parent is not None:
            path.insert(0, current.key)
            current = current.parent
        return path

    def get_display_value(self) -> str:
        """Get the display string for this node."""
        if self.node_type == 'object':
            count = len(self.children) if self.loaded else '?'
            return f"{self.key} {{{count}}}"
        elif self.node_type == 'array':
            count = len(self.children) if self.loaded else '?'
            return f"{self.key} [{count}]"
        else:
            # Truncate long values
            val_str = str(self.value)
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            return f"{self.key}: {val_str}"


class LazyJSONLoader:
    """Handles lazy loading of large JSON files."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self._cache = {}

    def load_full_json(self) -> Any:
        """Load the entire JSON file (use cautiously with large files)."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_partial_json(self, max_depth: int = 2) -> Any:
        """Load JSON up to a certain depth using streaming."""
        with open(self.file_path, 'rb') as f:
            # For initial load, we'll load the full structure but lazily
            parser = ijson.parse(f)
            return self._build_structure(parser, max_depth)

    def _build_structure(self, parser, max_depth: int, current_depth: int = 0):
        """Build a partial JSON structure from streaming parser."""
        result = None
        stack = []

        for prefix, event, value in parser:
            if current_depth >= max_depth:
                # Stop parsing at max depth
                if event == 'map_key':
                    return {"...": "Content not loaded"}
                elif event == 'start_array':
                    return ["..."]

            # This is a simplified version - full implementation would be more complex
            if event == 'start_map':
                if result is None:
                    result = {}
                    stack.append(result)
            elif event == 'end_map':
                if stack:
                    stack.pop()
            elif event == 'start_array':
                if result is None:
                    result = []
                    stack.append(result)
            elif event == 'end_array':
                if stack:
                    stack.pop()

        return result

    def get_value_at_path(self, path: List[str]) -> Any:
        """Get a specific value at a given path in the JSON."""
        cache_key = '.'.join(path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Stream through the file to find the specific path
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            current = data
            for key in path:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list):
                    try:
                        current = current[int(key)]
                    except (ValueError, IndexError):
                        return None
                else:
                    return None

            self._cache[cache_key] = current
            return current


class JSONEditorGUI:
    """Main GUI application for JSON editing."""

    def __init__(self, root):
        self.root = root
        self.root.title("SSR JSON Editor")
        self.root.geometry("1200x800")

        # Store multiple files in tabs
        self.tabs_data = {}  # {tab_id: {'file': path, 'data': json_data, 'modified': bool, 'loader': loader}}
        self.current_tab = None

        # Legacy support (will be replaced by tab-specific data)
        self.current_file = None
        self.json_data = None
        self.loader = None
        self.modified = False
        self.root_node = None
        self.use_regex = False

        # Detect platform for keyboard shortcuts
        self.is_mac = platform.system() == 'Darwin'
        self.modifier = 'Command' if self.is_mac else 'Control'

        self._setup_menu()
        self._setup_ui()
        self._setup_context_menu()
        self._setup_drag_and_drop()

    def _setup_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        accel_prefix = "Cmd" if self.is_mac else "Ctrl"
        file_menu.add_command(label="Open", command=self.open_file, accelerator=f"{accel_prefix}+O")
        file_menu.add_command(label="Paste JSON", command=self.paste_json, accelerator=f"{accel_prefix}+V")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator=f"{accel_prefix}+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator=f"{accel_prefix}+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.close_file, accelerator=f"{accel_prefix}+W")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.show_search, accelerator=f"{accel_prefix}+F")
        edit_menu.add_command(label="Expand All", command=self.expand_all)
        edit_menu.add_command(label="Collapse All", command=self.collapse_all)

        # Keyboard shortcuts - cross-platform
        mod = self.modifier
        self.root.bind(f'<{mod}-o>', lambda e: self.open_file())
        self.root.bind(f'<{mod}-O>', lambda e: self.open_file())
        self.root.bind(f'<{mod}-v>', lambda e: self.paste_json())
        self.root.bind(f'<{mod}-V>', lambda e: self.paste_json())
        self.root.bind(f'<{mod}-s>', lambda e: self.save_file())
        self.root.bind(f'<{mod}-S>', lambda e: self.save_file_as())
        self.root.bind(f'<{mod}-w>', lambda e: self.close_file())
        self.root.bind(f'<{mod}-W>', lambda e: self.close_file())
        self.root.bind(f'<{mod}-f>', lambda e: self.show_search())
        self.root.bind(f'<{mod}-F>', lambda e: self.show_search())

    def _setup_ui(self):
        """Create the main UI components."""
        # Toolbar at top
        toolbar = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        # Open button
        open_btn = ttk.Button(toolbar, text="📁 Open File", command=self.open_file, width=15)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Paste JSON button
        paste_btn = ttk.Button(toolbar, text="📋 Paste JSON", command=self.paste_json, width=15)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Save button
        save_btn = ttk.Button(toolbar, text="💾 Save", command=self.save_file, width=12)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Save As button
        save_as_btn = ttk.Button(toolbar, text="💾 Save As", command=self.save_file_as, width=12)
        save_as_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Split button
        split_btn = ttk.Button(toolbar, text="✂ Split", command=self.show_split_dialog, width=10)
        split_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Close button
        close_btn = ttk.Button(toolbar, text="✖ Close", command=self.close_file, width=10)
        close_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="No file loaded - Drop a JSON file here or click 'Open File'", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.file_size_label = ttk.Label(self.status_frame, text="", relief=tk.SUNKEN)
        self.file_size_label.pack(side=tk.RIGHT, padx=5)

        # Main content area with splitter
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Tree view
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)

        # Search bar
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.deep_search())
        self.search_entry.bind('<KeyRelease>', self._on_search_change)

        # Regex checkbox
        self.regex_var = tk.BooleanVar()
        regex_check = ttk.Checkbutton(search_frame, text="Regex", variable=self.regex_var)
        regex_check.pack(side=tk.LEFT, padx=2)

        ttk.Button(search_frame, text="Search", command=self.deep_search, width=8).pack(side=tk.LEFT, padx=2)
        self.clear_search_btn = ttk.Button(search_frame, text="Clear", command=self.clear_search, width=6)
        self.clear_search_btn.pack(side=tk.LEFT)

        # Search tracking
        self.search_active = False
        self.search_results_count = 0

        # Tree view with scrollbar
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(tree_frame,
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.bind('<<TreeviewOpen>>', self.on_tree_expand)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Button-2>', self.show_context_menu)  # Right-click on Mac
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click on Windows/Linux

        # Right panel - Detail view
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Value Editor", font=('Arial', 12, 'bold')).pack(pady=5)

        # Path display
        path_frame = ttk.Frame(right_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(path_frame, text="Path:").pack(side=tk.LEFT)
        self.path_label = ttk.Label(path_frame, text="", relief=tk.SUNKEN)
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Value editor
        editor_frame = ttk.Frame(right_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.value_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, width=40)
        self.value_text.pack(fill=tk.BOTH, expand=True)
        self.value_text.bind('<<Modified>>', self.on_value_modified)

        # Intercept paste events for large content handling
        self.value_text.bind('<<Paste>>', self._handle_value_editor_paste)

        # Editor buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Revert", command=self.revert_changes).pack(side=tk.LEFT)

        self.edit_status_label = ttk.Label(button_frame, text="", foreground="green")
        self.edit_status_label.pack(side=tk.RIGHT, padx=5)

    def _setup_context_menu(self):
        """Create right-click context menu for tree view."""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Save Node to File", command=self.save_node_to_file)
        self.context_menu.add_command(label="Copy Path", command=self.copy_path)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Expand Node", command=self.expand_node)
        self.context_menu.add_command(label="Collapse Node", command=self.collapse_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Go to Node", command=self.goto_node)

    def _setup_drag_and_drop(self):
        """Setup drag and drop functionality using native macOS support."""
        if self.is_mac:
            # On macOS, we can use the native file drop support
            # Register the window to accept file drops
            try:
                # Use Tcl/Tk's native drag and drop on macOS
                self.root.tk.call('::tk::mac::addFileDropHandling',
                                 self.root._w,
                                 self.root.register(self._handle_mac_file_drop))
            except Exception as e:
                print(f"Note: macOS drag-and-drop registration failed: {e}")
                print("You can still open files using the 'Open File' button.")
        else:
            # For other platforms, provide a message
            print("Note: Drag and drop is currently only supported on macOS.")
            print("Use the 'Open File' button to load JSON files.")

    def _handle_mac_file_drop(self, *files):
        """Handle file drop event on macOS."""
        if not files:
            return

        # Get the first file
        file_path = files[0]

        # Check if it's a JSON file
        if not file_path.lower().endswith('.json'):
            messagebox.showwarning(
                "Invalid File",
                "Please drop a JSON file (.json extension)"
            )
            return

        # Check if file exists
        if not os.path.exists(file_path):
            messagebox.showerror(
                "File Not Found",
                f"File does not exist:\n{file_path}"
            )
            return

        # Load the file
        self._load_file(file_path)

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.context_menu.post(event.x_root, event.y_root)

    def save_node_to_file(self):
        """Save the selected node and its children to a separate JSON file."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a node to save")
            return

        item_id = selected[0]
        value = self._get_value_for_item(item_id)
        path = self._get_path_for_item(item_id)

        if value is None:
            messagebox.showwarning("No Data", "No data to save")
            return

        # Suggest filename based on key name
        key_name = path[-1] if path else "root"
        suggested_name = f"{key_name}.json"

        file_path = filedialog.asksaveasfilename(
            title="Save Node to File",
            defaultextension=".json",
            initialfile=suggested_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Success", f"Node saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save node:\n{str(e)}")

    def copy_path(self):
        """Copy the path of the selected node to clipboard."""
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        path = self._get_path_for_item(item_id)
        path_str = ' > '.join(path) if path else 'Root'

        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(path_str)
        self.edit_status_label.config(text="Path copied!", foreground="blue")
        self.root.after(2000, lambda: self.edit_status_label.config(text=""))

    def expand_node(self):
        """Expand the selected node."""
        selected = self.tree.selection()
        if selected:
            self.tree.item(selected[0], open=True)

    def collapse_node(self):
        """Collapse the selected node."""
        selected = self.tree.selection()
        if selected:
            self.tree.item(selected[0], open=False)

    def goto_node(self):
        """Navigate to and focus on the selected node (scroll into view)."""
        selected = self.tree.selection()
        if selected:
            item_id = selected[0]
            self.tree.see(item_id)
            self.tree.focus(item_id)
            # Also update the value editor
            self.on_tree_select(None)

    def on_tree_double_click(self, event):
        """Handle double-click on tree item - focus and scroll to it."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.tree.see(item)
            # Expand/collapse if it's a container
            tags = self.tree.item(item, 'tags')
            if 'object' in tags or 'array' in tags:
                current_state = self.tree.item(item, 'open')
                self.tree.item(item, open=not current_state)

    def open_file(self):
        """Open a JSON file."""
        file_path = filedialog.askopenfilename(
            title="Open JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        self._load_file(file_path)

    def paste_json(self):
        """Paste JSON from clipboard and load it."""
        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()

            if not clipboard_text or not clipboard_text.strip():
                messagebox.showwarning("Empty Clipboard", "Clipboard is empty. Please copy JSON data first.")
                return

            # Clean the clipboard text (remove BOM, trim whitespace)
            clipboard_text = clipboard_text.strip()
            if clipboard_text.startswith('\ufeff'):
                clipboard_text = clipboard_text[1:]

            # Show progress for large clipboard data
            data_size_mb = len(clipboard_text.encode('utf-8')) / (1024 * 1024)

            self.status_label.config(text="Parsing pasted JSON...")
            self.root.update()

            # Create progress window for large data
            progress_window = None
            progress_label = None
            progress_bar = None
            progress_percentage = None

            if data_size_mb > 0.5:
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Processing JSON")
                progress_window.geometry("450x150")
                progress_window.transient(self.root)
                progress_window.grab_set()

                # Center the window
                progress_window.update_idletasks()
                x = (progress_window.winfo_screenwidth() // 2) - (450 // 2)
                y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
                progress_window.geometry(f"450x150+{x}+{y}")

                ttk.Label(progress_window, text="Processing pasted JSON...",
                         font=('Arial', 10, 'bold')).pack(pady=10)

                progress_label = ttk.Label(progress_window, text="Validating JSON...")
                progress_label.pack(pady=5)

                # Deterministic progress bar
                progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=400, maximum=100)
                progress_bar.pack(pady=10)

                progress_percentage = ttk.Label(progress_window, text="0%")
                progress_percentage.pack(pady=2)

            # Parse JSON in background thread for large data
            def parse_thread():
                try:
                    # Update progress: 10%
                    if progress_window:
                        self.root.after(0, lambda: progress_bar.config(value=10))
                        self.root.after(0, lambda: progress_percentage.config(text="10%"))
                        self.root.after(0, lambda: progress_label.config(text="Parsing JSON..."))

                    # Try to parse the JSON with better error handling
                    try:
                        parsed_data = json.loads(clipboard_text)
                    except json.JSONDecodeError as json_err:
                        # Try fixing common formatting issues first
                        if progress_window:
                            self.root.after(0, lambda: progress_label.config(text="Cleaning JSON formatting..."))

                        try:
                            fixed_text = self._fix_json_formatting(clipboard_text)
                            parsed_data = json.loads(fixed_text)
                        except json.JSONDecodeError:
                            # Try with strict=False for more lenient parsing
                            try:
                                parsed_data = json.loads(clipboard_text, strict=False)
                            except:
                                # If still fails, try the quote conversion
                                if progress_window:
                                    self.root.after(0, lambda: progress_label.config(text="Attempting quote conversion..."))

                                try:
                                    converted = self._convert_quotes(clipboard_text)
                                    parsed_data = json.loads(converted)
                                except:
                                    # Re-raise the original error with context
                                    raise json_err

                    # Update progress: 50%
                    if progress_window:
                        self.root.after(0, lambda: progress_bar.config(value=50))
                        self.root.after(0, lambda: progress_percentage.config(text="50%"))
                        self.root.after(0, lambda: progress_label.config(text="Validating data structure..."))

                    # Set the data
                    self.json_data = parsed_data
                    self.current_file = None  # No file yet
                    self.loader = None
                    self.modified = True  # Mark as modified since it's new data

                    # Update progress: 75%
                    if progress_window:
                        self.root.after(0, lambda: progress_bar.config(value=75))
                        self.root.after(0, lambda: progress_percentage.config(text="75%"))
                        self.root.after(0, lambda: progress_label.config(text="Building tree view..."))

                    # Populate tree
                    self.root.after(0, self._populate_tree)

                    # Update progress: 100%
                    if progress_window:
                        self.root.after(0, lambda: progress_bar.config(value=100))
                        self.root.after(0, lambda: progress_percentage.config(text="100%"))
                        self.root.after(0, lambda: progress_label.config(text="Complete!"))

                    self.root.after(0, lambda: self.status_label.config(
                        text="Pasted JSON loaded - Use 'Save As' to save"
                    ))
                    self.root.after(0, lambda: self.file_size_label.config(
                        text=f"Size: {data_size_mb:.1f} MB"
                    ))

                    # Close progress window after brief delay to show 100%
                    if progress_window:
                        self.root.after(500, progress_window.destroy)

                except json.JSONDecodeError as e:
                    # Close progress window
                    if progress_window:
                        self.root.after(0, progress_window.destroy)

                    # Check if JSON is truncated/incomplete
                    error_pos = e.pos
                    is_truncated = error_pos >= len(clipboard_text) - 1

                    # Show context around the error
                    context_start = max(0, error_pos - 100)
                    context_end = min(len(clipboard_text), error_pos + 100)
                    context = clipboard_text[context_start:context_end]

                    # Save problematic JSON to a debug file
                    debug_file = "debug_failed_json.txt"
                    try:
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write("=== FAILED JSON ===\n\n")
                            f.write(clipboard_text)
                            f.write(f"\n\n=== ERROR ===\n{str(e)}\n")
                            f.write(f"Position: {e.pos}\n")
                            f.write(f"Line {e.lineno}, Column {e.colno}\n")
                            f.write(f"JSON length: {len(clipboard_text)} characters\n")
                            f.write(f"Truncated: {is_truncated}\n")
                            f.write(f"\n=== CONTEXT ===\n...{context}...")
                    except:
                        pass

                    # Create appropriate error message
                    if is_truncated:
                        error_msg = (
                            f"Clipboard JSON is INCOMPLETE/TRUNCATED!\n\n"
                            f"The clipboard data was cut off at {len(clipboard_text)} characters.\n"
                            f"The JSON ends with: ...{clipboard_text[-50:]}\n\n"
                            f"This is a clipboard size limitation.\n\n"
                            f"Solutions:\n"
                            f"1. Save the JSON to a file first, then use 'Open File'\n"
                            f"2. Use a smaller JSON subset\n"
                            f"3. Copy the data in multiple parts\n\n"
                            f"Full incomplete JSON saved to: {debug_file}"
                        )
                    else:
                        error_msg = (f"Invalid JSON in clipboard:\n{str(e)}\n\n"
                                    f"Line {e.lineno}, Column {e.colno}\n\n"
                                    f"Context around error:\n...{context}...\n\n"
                                    f"Full JSON saved to: {debug_file}\n"
                                    f"You can inspect this file to find the issue.")

                    self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                        "JSON Parse Error",
                        msg
                    ))
                    self.root.after(0, lambda: self.status_label.config(text="Error: Invalid JSON in clipboard"))
                except Exception as e:
                    # Close progress window
                    if progress_window:
                        self.root.after(0, progress_window.destroy)

                    error_msg = f"Failed to parse clipboard content:\n{str(e)}"
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                        "Error",
                        msg
                    ))
                    self.root.after(0, lambda: self.status_label.config(text="Error parsing clipboard"))

            # Use thread for large data
            if data_size_mb > 0.5:
                thread = threading.Thread(target=parse_thread, daemon=True)
                thread.start()
            else:
                # Parse directly for small data
                parse_thread()

        except tk.TclError:
            messagebox.showwarning("Clipboard Error", "Could not access clipboard. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste JSON:\n{str(e)}")

    def _handle_quote_conversion_error(self, file_path: str, error: json.JSONDecodeError):
        """Handle JSON parse error related to quotes and offer conversion."""
        response = messagebox.askyesno(
            "JSON Parse Error - Invalid Quotes",
            f"Invalid JSON format:\n{str(error)}\n\nLine {error.lineno}, Column {error.colno}\n\n"
            f"This error often occurs when single quotes (') are used instead of double quotes (\").\n\n"
            f"Would you like to attempt automatic conversion of single quotes to double quotes?"
        )

        if response:
            self._convert_and_reload_file(file_path)
        else:
            self.status_label.config(text="Error: Invalid JSON")
            self.current_file = None
            self.json_data = None

    def _convert_and_reload_file(self, file_path: str):
        """Convert single quotes to double quotes and reload the file."""
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Convert single quotes to double quotes
            # This is a simple conversion that handles most cases
            converted_content = self._convert_quotes(content)

            # Try to parse the converted content
            try:
                json_data = json.loads(converted_content)

                # Ask if user wants to save the corrected version
                save_response = messagebox.askyesnocancel(
                    "Conversion Successful",
                    f"Successfully converted the file!\n\n"
                    f"Would you like to save the corrected version?\n\n"
                    f"Yes - Save and load the corrected file\n"
                    f"No - Load without saving (temporary)\n"
                    f"Cancel - Don't load the file"
                )

                if save_response is None:  # Cancel
                    self.status_label.config(text="Load cancelled")
                    return
                elif save_response:  # Yes - Save
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    messagebox.showinfo("Saved", "File has been corrected and saved.")

                # Load the data
                self.json_data = json_data
                self.current_file = file_path
                self.loader = LazyJSONLoader(file_path)
                self._populate_tree()
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")

            except json.JSONDecodeError as e:
                messagebox.showerror(
                    "Conversion Failed",
                    f"Automatic conversion failed.\n\n"
                    f"The file still has JSON errors after quote conversion:\n{str(e)}\n\n"
                    f"Please fix the JSON format manually."
                )
                self.status_label.config(text="Error: Conversion failed")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to convert file:\n{str(e)}"
            )
            self.status_label.config(text="Error: Conversion failed")

    def _convert_quotes(self, content: str) -> str:
        """Convert single quotes to double quotes in JSON-like content."""
        # This is a simple but effective approach for most cases
        # It handles:
        # - Property names in single quotes: {'key': value}
        # - String values in single quotes: {key: 'value'}

        import ast

        # Try to use Python's AST to safely evaluate and convert
        # This works for Python dict syntax which is similar to JSON with single quotes
        try:
            # Replace true/false/null with Python equivalents temporarily
            temp_content = content.replace('true', 'True').replace('false', 'False').replace('null', 'None')
            # Try to evaluate as Python literal
            obj = ast.literal_eval(temp_content)
            # Convert back to JSON
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except:
            # Fallback: simple string replacement
            # This is less safe but works for simple cases
            result = content.replace("'", '"')
            return result

    def _fix_json_formatting(self, content: str) -> str:
        """Fix common JSON formatting issues."""
        # Remove null bytes and other control characters that can break parsing
        content = content.replace('\x00', '')

        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Remove any trailing commas before closing braces/brackets
        import re
        content = re.sub(r',(\s*[}\]])', r'\1', content)

        # Fix common escape sequence issues
        # Ensure backslashes in strings are properly escaped
        # But be careful not to double-escape already escaped sequences

        return content

    def _load_file(self, file_path: str):
        """Load a JSON file from the given path."""
        if not os.path.exists(file_path):
            messagebox.showerror(
                "File Not Found",
                f"File does not exist:\n{file_path}"
            )
            return

        # Check file size and warn if very large
        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)

            if size_mb > 100:
                response = messagebox.askyesno(
                    "Large File Warning",
                    f"This file is {size_mb:.1f} MB. Loading may take some time.\n\nContinue?"
                )
                if not response:
                    return
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to check file size:\n{str(e)}"
            )
            return

        self.current_file = file_path
        self.status_label.config(text=f"Loading: {os.path.basename(file_path)}...")
        self.file_size_label.config(text=f"Size: {size_mb:.1f} MB")
        self.root.update()

        # Show progress window for files larger than 1MB
        progress_window = None
        progress_bar = None
        progress_label = None
        progress_percentage = None

        if size_mb > 1:
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Loading File")
            progress_window.geometry("450x150")
            progress_window.transient(self.root)
            progress_window.grab_set()

            # Center the window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (450 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"450x150+{x}+{y}")

            ttk.Label(progress_window, text=f"Loading {os.path.basename(file_path)}...",
                     font=('Arial', 10, 'bold')).pack(pady=10)

            progress_label = ttk.Label(progress_window, text="Reading file...")
            progress_label.pack(pady=5)

            # Deterministic progress bar
            progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=400, maximum=100)
            progress_bar.pack(pady=10)

            progress_percentage = ttk.Label(progress_window, text="0%")
            progress_percentage.pack(pady=2)

        # Load in background thread for large files
        def load_thread():
            try:
                # Update progress: 20%
                if progress_window:
                    self.root.after(0, lambda: progress_bar.config(value=20))
                    self.root.after(0, lambda: progress_percentage.config(text="20%"))
                    self.root.after(0, lambda: progress_label.config(text="Reading file..."))

                self.loader = LazyJSONLoader(file_path)

                # Update progress: 40%
                if progress_window:
                    self.root.after(0, lambda: progress_bar.config(value=40))
                    self.root.after(0, lambda: progress_percentage.config(text="40%"))
                    self.root.after(0, lambda: progress_label.config(text="Parsing JSON..."))

                with open(file_path, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)

                # Update progress: 70%
                if progress_window:
                    self.root.after(0, lambda: progress_bar.config(value=70))
                    self.root.after(0, lambda: progress_percentage.config(text="70%"))
                    self.root.after(0, lambda: progress_label.config(text="Populating tree view..."))

                self.root.after(0, self._populate_tree)

                # Update progress: 100%
                if progress_window:
                    self.root.after(0, lambda: progress_bar.config(value=100))
                    self.root.after(0, lambda: progress_percentage.config(text="100%"))
                    self.root.after(0, lambda: progress_label.config(text="Complete!"))

                self.root.after(0, lambda: self.status_label.config(
                    text=f"Loaded: {os.path.basename(file_path)}"
                ))

                # Close progress window after brief delay to show 100%
                if progress_window:
                    self.root.after(500, progress_window.destroy)

            except json.JSONDecodeError as json_error:
                # Close progress window
                if progress_window:
                    self.root.after(0, progress_window.destroy)

                error_msg = str(json_error)

                # Check if the error is related to single quotes
                if "Expecting property name enclosed in double quotes" in error_msg or "'" in error_msg:
                    # Offer to convert single quotes to double quotes
                    self.root.after(0, lambda err=json_error: self._handle_quote_conversion_error(file_path, err))
                else:
                    full_error_msg = f"Invalid JSON format:\n{str(json_error)}\n\nLine {json_error.lineno}, Column {json_error.colno}"
                    self.root.after(0, lambda msg=full_error_msg: messagebox.showerror(
                        "JSON Parse Error",
                        msg
                    ))
                    self.root.after(0, lambda: self.status_label.config(text="Error: Invalid JSON"))
                    self.current_file = None
                    self.json_data = None
            except UnicodeDecodeError as unicode_error:
                # Close progress window
                if progress_window:
                    self.root.after(0, progress_window.destroy)

                error_msg = f"File encoding error:\n{str(unicode_error)}\n\nThe file may not be UTF-8 encoded."
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Encoding Error",
                    msg
                ))
                self.root.after(0, lambda: self.status_label.config(text="Error: File encoding issue"))
                self.current_file = None
                self.json_data = None
            except Exception as general_error:
                # Close progress window
                if progress_window:
                    self.root.after(0, progress_window.destroy)

                error_msg = f"Failed to load file:\n{str(general_error)}"
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Error",
                    msg
                ))
                self.root.after(0, lambda: self.status_label.config(text="Error loading file"))
                self.current_file = None
                self.json_data = None

        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def _populate_tree(self):
        """Populate the tree view with JSON data."""
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.json_data is None:
            return

        # Create root node
        if isinstance(self.json_data, dict):
            count = len(self.json_data)
            root_id = self.tree.insert('', 'end', text=f'Root {{{count}}}', open=True)
            self._add_dict_nodes(root_id, self.json_data)
        elif isinstance(self.json_data, list):
            count = len(self.json_data)
            root_id = self.tree.insert('', 'end', text=f'Root [{count}]', open=True)
            self._add_list_nodes(root_id, self.json_data)
        else:
            self.tree.insert('', 'end', text=f'Root: {self.json_data}')

    def _add_dict_nodes(self, parent_id: str, data: dict, max_items: int = 200):
        """Add dictionary nodes to tree (with lazy loading for large dicts)."""
        items = list(data.items())

        # Increase max_items to 200 for better initial display
        # Process in smaller chunks for ultra-fast response
        chunk_size = 50
        items_to_show = min(len(items), max_items)

        for i in range(0, items_to_show, chunk_size):
            chunk = items[i:i + chunk_size]
            for key, value in chunk:
                self._add_node(parent_id, key, value)
            # Reduced update frequency for speed
            if i + chunk_size < items_to_show and i % (chunk_size * 2) == 0:
                self.root.update_idletasks()

        # If there are more items, show all remaining items (no pagination needed for most cases)
        if len(items) > max_items:
            for key, value in items[max_items:]:
                self._add_node(parent_id, key, value)

    def _add_list_nodes(self, parent_id: str, data: list, max_items: int = 200):
        """Add list nodes to tree (with lazy loading for large arrays)."""
        # Increase max_items to 200 for better initial display
        # Process in smaller chunks for ultra-fast response
        chunk_size = 50
        items_to_show = min(len(data), max_items)

        for i in range(0, items_to_show, chunk_size):
            chunk_end = min(i + chunk_size, items_to_show)
            for idx in range(i, chunk_end):
                self._add_node(parent_id, f"[{idx}]", data[idx])
            # Reduced update frequency for speed
            if i + chunk_size < items_to_show and i % (chunk_size * 2) == 0:
                self.root.update_idletasks()

        # If there are more items, show all remaining items (no pagination needed for most cases)
        if len(data) > max_items:
            for idx in range(max_items, len(data)):
                self._add_node(parent_id, f"[{idx}]", data[idx])

    def _add_node(self, parent_id: str, key: str, value: Any):
        """Add a single node to the tree."""
        if isinstance(value, dict):
            count = len(value)
            node_id = self.tree.insert(parent_id, 'end', text=f'{key} {{{count}}}', tags=('object',))
            if count > 0:
                # Add placeholder for lazy loading
                self.tree.insert(node_id, 'end', text='Loading...', tags=('lazy',))
        elif isinstance(value, list):
            count = len(value)
            node_id = self.tree.insert(parent_id, 'end', text=f'{key} [{count}]', tags=('array',))
            if count > 0:
                # Add placeholder for lazy loading
                self.tree.insert(node_id, 'end', text='Loading...', tags=('lazy',))
        else:
            # Leaf node
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            self.tree.insert(parent_id, 'end', text=f'{key}: {value_str}', tags=('value',))

    def on_tree_expand(self, event):
        """Handle lazy loading when a node is expanded."""
        item_id = self.tree.focus()
        children = self.tree.get_children(item_id)

        # Check if this node needs lazy loading
        if len(children) == 1:
            child = children[0]
            if 'lazy' in self.tree.item(child, 'tags'):
                # Remove placeholder
                self.tree.delete(child)

                # Get the actual data for this node
                value = self._get_value_for_item(item_id)

                if isinstance(value, dict):
                    self._add_dict_nodes(item_id, value)
                elif isinstance(value, list):
                    self._add_list_nodes(item_id, value)

    def _get_value_for_item(self, item_id: str) -> Any:
        """Get the JSON value for a tree item by traversing the path."""
        path = []
        current = item_id

        while current:
            text = self.tree.item(current, 'text')
            parent = self.tree.parent(current)

            if parent:  # Not root
                # Extract key from text
                if ': ' in text:
                    key = text.split(': ')[0]
                elif ' {' in text:
                    key = text.split(' {')[0]
                elif ' [' in text:
                    key = text.split(' [')[0]
                else:
                    key = text

                path.insert(0, key)

            current = parent

        # Traverse JSON data using path
        value = self.json_data
        for key in path:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                # Extract index from [n] format
                if key.startswith('[') and key.endswith(']'):
                    index = int(key[1:-1])
                    value = value[index]

            if value is None:
                break

        return value

    def on_tree_select(self, event):
        """Handle tree item selection."""
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]

        # Get path
        path = self._get_path_for_item(item_id)
        self.path_label.config(text=' > '.join(path) if path else 'Root')

        # Get value and display in editor
        value = self._get_value_for_item(item_id)

        self.value_text.delete('1.0', tk.END)
        if value is not None:
            if isinstance(value, (dict, list)):
                # Pretty print complex objects
                formatted = json.dumps(value, indent=2, ensure_ascii=False)
                self.value_text.insert('1.0', formatted)
            else:
                self.value_text.insert('1.0', str(value))

        # Reset modified flag
        self.value_text.edit_modified(False)

    def _get_path_for_item(self, item_id: str) -> List[str]:
        """Get the path to a tree item."""
        path = []
        current = item_id

        while current:
            text = self.tree.item(current, 'text')
            parent = self.tree.parent(current)

            if parent:  # Not root
                if ': ' in text:
                    key = text.split(': ')[0]
                elif ' {' in text:
                    key = text.split(' {')[0]
                elif ' [' in text:
                    key = text.split(' [')[0]
                else:
                    key = text

                path.insert(0, key)

            current = parent

        return path

    def on_value_modified(self, event):
        """Handle value text modification."""
        if self.value_text.edit_modified():
            self.edit_status_label.config(text="Modified", foreground="orange")

    def _handle_value_editor_paste(self, event):
        """Handle paste events in the value editor for large content."""
        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()

            # Check size - if it's large, handle it specially
            text_size_mb = len(clipboard_text.encode('utf-8')) / (1024 * 1024)

            if text_size_mb > 1:  # If larger than 1MB
                # Cancel the default paste event
                self.value_text.after_idle(lambda: self._insert_large_text(clipboard_text))
                return "break"  # Prevent default paste

            # For small content, allow default behavior
            return None

        except Exception as e:
            print(f"Paste handler error: {e}")
            return None  # Allow default behavior on error

    def _insert_large_text(self, text):
        """Insert large text into value editor in chunks to prevent freezing."""
        # Clear existing content first
        self.value_text.delete('1.0', tk.END)

        # Disable the widget during insert to prevent UI updates
        self.value_text.config(state='disabled')
        self.edit_status_label.config(text="Pasting large content...", foreground="blue")
        self.root.update()

        # Insert text in chunks
        chunk_size = 50000  # 50KB chunks
        total_chunks = (len(text) + chunk_size - 1) // chunk_size

        def insert_chunk(index=0):
            if index < total_chunks:
                start = index * chunk_size
                end = min((index + 1) * chunk_size, len(text))
                chunk = text[start:end]

                # Temporarily enable to insert
                self.value_text.config(state='normal')
                self.value_text.insert(tk.END, chunk)
                self.value_text.config(state='disabled')

                # Update progress
                progress = int((index + 1) / total_chunks * 100)
                self.edit_status_label.config(text=f"Pasting... {progress}%", foreground="blue")

                # Schedule next chunk
                self.root.after(1, lambda: insert_chunk(index + 1))
            else:
                # Done - re-enable widget
                self.value_text.config(state='normal')
                self.value_text.mark_set(tk.INSERT, '1.0')  # Move cursor to start
                self.value_text.see('1.0')  # Scroll to top
                self.edit_status_label.config(text="Paste complete", foreground="green")
                self.root.after(2000, lambda: self.edit_status_label.config(text=""))
                # Mark as modified
                self.value_text.edit_modified(True)

        # Start inserting
        insert_chunk(0)

    def apply_changes(self):
        """Apply changes from the value editor back to the JSON data."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a node to edit")
            return

        item_id = selected[0]
        path = self._get_path_for_item(item_id)
        new_value_str = self.value_text.get('1.0', tk.END).strip()

        try:
            # Try to parse as JSON first
            try:
                new_value = json.loads(new_value_str)
            except json.JSONDecodeError:
                # If not valid JSON, treat as string
                new_value = new_value_str

            # Update the JSON data
            self._set_value_at_path(path, new_value)

            self.modified = True
            self.edit_status_label.config(text="Saved", foreground="green")
            self.status_label.config(text=f"Modified: {os.path.basename(self.current_file)} *")

            # Refresh the tree node
            self._refresh_tree_node(item_id, new_value)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply changes:\n{str(e)}")

    def _set_value_at_path(self, path: List[str], value: Any):
        """Set a value in the JSON data at the given path."""
        if not path:
            return

        current = self.json_data
        for key in path[:-1]:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                if key.startswith('[') and key.endswith(']'):
                    index = int(key[1:-1])
                    current = current[index]

        # Set the final value
        final_key = path[-1]
        if isinstance(current, dict):
            current[final_key] = value
        elif isinstance(current, list):
            if final_key.startswith('[') and final_key.endswith(']'):
                index = int(final_key[1:-1])
                current[index] = value

    def _refresh_tree_node(self, item_id: str, value: Any):
        """Refresh a tree node with new value."""
        text = self.tree.item(item_id, 'text')

        if isinstance(value, dict):
            key = text.split(' {')[0] if ' {' in text else text
            self.tree.item(item_id, text=f'{key} {{{len(value)}}}')
        elif isinstance(value, list):
            key = text.split(' [')[0] if ' [' in text else text
            self.tree.item(item_id, text=f'{key} [{len(value)}]')
        else:
            if ': ' in text:
                key = text.split(': ')[0]
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                self.tree.item(item_id, text=f'{key}: {value_str}')

    def revert_changes(self):
        """Revert changes in the value editor."""
        self.on_tree_select(None)
        self.edit_status_label.config(text="Reverted", foreground="blue")

    def save_file(self):
        """Save changes to the current file."""
        if not self.current_file:
            self.save_file_as()
            return

        if self.json_data is None:
            messagebox.showwarning("No Data", "No data to save")
            return

        if not self.modified:
            # Allow saving even if not modified
            response = messagebox.askyesno("No Changes", "No changes detected. Save anyway?")
            if not response:
                return

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=2, ensure_ascii=False)

            self.modified = False
            self.status_label.config(text=f"Saved: {os.path.basename(self.current_file)}")
            self.edit_status_label.config(text="File saved!", foreground="green")
            self.root.after(2000, lambda: self.edit_status_label.config(text=""))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def save_file_as(self):
        """Save changes to a new file."""
        if self.json_data is None:
            messagebox.showwarning("No Data", "No data to save")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save JSON File As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=2, ensure_ascii=False)

            self.current_file = file_path
            self.modified = False
            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "File saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def close_file(self):
        """Close the current file."""
        if self.modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_file()

        self.current_file = None
        self.json_data = None
        self.loader = None
        self.modified = False

        # Clear UI
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.value_text.delete('1.0', tk.END)
        self.path_label.config(text='')
        self.status_label.config(text='No file loaded')
        self.file_size_label.config(text='')
        self.edit_status_label.config(text='')

    def show_search(self):
        """Focus the search entry."""
        self.search_entry.focus()
        self.search_entry.select_range(0, tk.END)

    def _on_search_change(self, event):
        """Handle search text changes - clear search if empty."""
        if not self.search_var.get().strip() and self.search_active:
            self.clear_search()

    def deep_search(self):
        """Deep search through all JSON data and filter tree to show only matches."""
        search_term = self.search_var.get().strip()

        if not search_term:
            self.clear_search()
            return

        if self.json_data is None:
            messagebox.showwarning("No Data", "Please load a JSON file first")
            return

        use_regex = self.regex_var.get()

        # Validate regex if enabled
        if use_regex:
            try:
                re.compile(search_term)
            except re.error as e:
                messagebox.showerror("Invalid Regex", f"Invalid regular expression:\n{str(e)}")
                return

        # Show searching status
        self.status_label.config(text=f"Searching for '{search_term}'...")
        self.root.update()

        # Search through all JSON data
        matching_paths = self._deep_search_json(self.json_data, search_term, use_regex)

        if not matching_paths:
            self.status_label.config(text=f"No matches found for '{search_term}'")
            messagebox.showinfo("No Results", f"No matches found for '{search_term}'")
            return

        # Rebuild tree with only matching items and their parent paths
        self._populate_filtered_tree(matching_paths)

        self.search_active = True
        self.search_results_count = len(matching_paths)
        self.status_label.config(text=f"Found {len(matching_paths)} match{'es' if len(matching_paths) != 1 else ''} for '{search_term}'")

    def _deep_search_json(self, data: Any, search_term: str, use_regex: bool, current_path: List[str] = None) -> List[Tuple[List[str], Any]]:
        """Recursively search through JSON data for matches in keys and values."""
        if current_path is None:
            current_path = []

        matches = []

        def matches_search(text: str) -> bool:
            """Check if text matches search term."""
            if use_regex:
                try:
                    return re.search(search_term, str(text), re.IGNORECASE) is not None
                except re.error:
                    return False
            else:
                return search_term.lower() in str(text).lower()

        if isinstance(data, dict):
            for key, value in data.items():
                new_path = current_path + [key]

                # Check if key matches
                if matches_search(key):
                    matches.append((new_path, value))

                # Check if value matches (for leaf values)
                if not isinstance(value, (dict, list)):
                    if matches_search(str(value)):
                        matches.append((new_path, value))

                # Recursively search nested structures
                if isinstance(value, (dict, list)):
                    matches.extend(self._deep_search_json(value, search_term, use_regex, new_path))

        elif isinstance(data, list):
            for idx, value in enumerate(data):
                new_path = current_path + [f"[{idx}]"]

                # Check if value matches (for leaf values)
                if not isinstance(value, (dict, list)):
                    if matches_search(str(value)):
                        matches.append((new_path, value))

                # Recursively search nested structures
                if isinstance(value, (dict, list)):
                    matches.extend(self._deep_search_json(value, search_term, use_regex, new_path))

        return matches

    def _populate_filtered_tree(self, matching_paths: List[Tuple[List[str], Any]]):
        """Populate tree with only matching items and their parent paths."""
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not matching_paths:
            return

        # Build a set of all paths that need to be shown (matches + their parents)
        paths_to_show = set()
        for path, value in matching_paths:
            # Add the full path
            paths_to_show.add(tuple(path))
            # Add all parent paths
            for i in range(len(path)):
                paths_to_show.add(tuple(path[:i+1]))

        # Create root node
        if isinstance(self.json_data, dict):
            root_id = self.tree.insert('', 'end', text=f'Root (filtered: {len(matching_paths)} matches)', open=True, tags=('search_result',))
            self._add_filtered_dict_nodes(root_id, self.json_data, [], paths_to_show)
        elif isinstance(self.json_data, list):
            root_id = self.tree.insert('', 'end', text=f'Root (filtered: {len(matching_paths)} matches)', open=True, tags=('search_result',))
            self._add_filtered_list_nodes(root_id, self.json_data, [], paths_to_show)

    def _add_filtered_dict_nodes(self, parent_id: str, data: dict, current_path: List[str], paths_to_show: set):
        """Add only filtered dictionary nodes to tree."""
        for key, value in data.items():
            path = current_path + [key]
            path_tuple = tuple(path)

            # Only add if this path should be shown
            if path_tuple in paths_to_show:
                if isinstance(value, dict):
                    count = len(value)
                    node_id = self.tree.insert(parent_id, 'end', text=f'{key} {{{count}}}', open=True, tags=('object', 'search_result'))
                    self._add_filtered_dict_nodes(node_id, value, path, paths_to_show)
                elif isinstance(value, list):
                    count = len(value)
                    node_id = self.tree.insert(parent_id, 'end', text=f'{key} [{count}]', open=True, tags=('array', 'search_result'))
                    self._add_filtered_list_nodes(node_id, value, path, paths_to_show)
                else:
                    # Leaf node
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    self.tree.insert(parent_id, 'end', text=f'{key}: {value_str}', tags=('value', 'search_result'))

    def _add_filtered_list_nodes(self, parent_id: str, data: list, current_path: List[str], paths_to_show: set):
        """Add only filtered list nodes to tree."""
        for idx, value in enumerate(data):
            index_key = f"[{idx}]"
            path = current_path + [index_key]
            path_tuple = tuple(path)

            # Only add if this path should be shown
            if path_tuple in paths_to_show:
                if isinstance(value, dict):
                    count = len(value)
                    node_id = self.tree.insert(parent_id, 'end', text=f'{index_key} {{{count}}}', open=True, tags=('object', 'search_result'))
                    self._add_filtered_dict_nodes(node_id, value, path, paths_to_show)
                elif isinstance(value, list):
                    count = len(value)
                    node_id = self.tree.insert(parent_id, 'end', text=f'{index_key} [{count}]', open=True, tags=('array', 'search_result'))
                    self._add_filtered_list_nodes(node_id, value, path, paths_to_show)
                else:
                    # Leaf node
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    self.tree.insert(parent_id, 'end', text=f'{index_key}: {value_str}', tags=('value', 'search_result'))

    def clear_search(self):
        """Clear search and restore full tree."""
        if not self.search_active:
            return

        self.search_var.set("")
        self.search_active = False
        self.search_results_count = 0

        # Restore full tree
        self._populate_tree()

        file_name = os.path.basename(self.current_file) if self.current_file else "pasted JSON"
        self.status_label.config(text=f"Loaded: {file_name}")

    def show_split_dialog(self):
        """Show dialog for splitting JSON file into smaller files."""
        if self.json_data is None:
            messagebox.showwarning("No Data", "Please load a JSON file first")
            return

        # Only support splitting arrays or dicts at root level
        if not isinstance(self.json_data, (list, dict)):
            messagebox.showwarning("Cannot Split", "Can only split JSON arrays or objects")
            return

        # Create dialog with scrollable content
        dialog = tk.Toplevel(self.root)
        dialog.title("Split JSON File")
        dialog.geometry("550x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"550x500+{x}+{y}")

        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(dialog, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Title
        ttk.Label(scrollable_frame, text="Split JSON File", font=('Arial', 14, 'bold')).pack(pady=10)

        # Info frame
        info_frame = ttk.Frame(scrollable_frame)
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        data_type = "array" if isinstance(self.json_data, list) else "object"
        item_count = len(self.json_data)
        ttk.Label(info_frame, text=f"Current JSON: {data_type} with {item_count} items",
                 font=('Arial', 10)).pack(anchor=tk.W)

        # Split method selection
        method_frame = ttk.LabelFrame(scrollable_frame, text="Split Method", padding=10)
        method_frame.pack(fill=tk.X, padx=20, pady=10)

        split_method = tk.StringVar(value="count")

        ttk.Radiobutton(method_frame, text="Split by number of files",
                       variable=split_method, value="count",
                       command=lambda: update_options()).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(method_frame, text="Split by file size",
                       variable=split_method, value="size",
                       command=lambda: update_options()).pack(anchor=tk.W, pady=5)

        # Options frame
        options_frame = ttk.LabelFrame(scrollable_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=20, pady=10)

        # Count-based options
        count_frame = ttk.Frame(options_frame)
        ttk.Label(count_frame, text="Number of files:").pack(side=tk.LEFT, padx=(0, 10))
        file_count_var = tk.StringVar(value="2")
        file_count_spin = ttk.Spinbox(count_frame, from_=2, to=1000, textvariable=file_count_var, width=15)
        file_count_spin.pack(side=tk.LEFT)

        # Size-based options
        size_frame = ttk.Frame(options_frame)
        ttk.Label(size_frame, text="Max file size:").pack(side=tk.LEFT, padx=(0, 10))
        file_size_var = tk.StringVar(value="1")
        file_size_spin = ttk.Spinbox(size_frame, from_=1, to=1000, textvariable=file_size_var, width=10)
        file_size_spin.pack(side=tk.LEFT, padx=5)

        size_unit_var = tk.StringVar(value="MB")
        size_unit_combo = ttk.Combobox(size_frame, textvariable=size_unit_var,
                                       values=["KB", "MB", "GB"], state="readonly", width=8)
        size_unit_combo.pack(side=tk.LEFT, padx=5)

        # Function to update visible options based on method
        def update_options():
            # Hide both first
            count_frame.pack_forget()
            size_frame.pack_forget()

            # Show the appropriate one
            if split_method.get() == "count":
                count_frame.pack(fill=tk.X, pady=10)
            else:
                size_frame.pack(fill=tk.X, pady=10)

        # Show initial options
        update_options()

        # Output folder
        output_frame = ttk.LabelFrame(scrollable_frame, text="Output Folder", padding=10)
        output_frame.pack(fill=tk.X, padx=20, pady=10)

        output_path_var = tk.StringVar(value="")
        output_entry = ttk.Entry(output_frame, textvariable=output_path_var, state="readonly")
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def browse_folder():
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                output_path_var.set(folder)

        ttk.Button(output_frame, text="Browse...", command=browse_folder, width=12).pack(side=tk.LEFT)

        # Buttons at bottom
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        def do_split():
            if not output_path_var.get():
                messagebox.showwarning("No Output Folder", "Please select an output folder")
                return

            try:
                method = split_method.get()
                output_folder = output_path_var.get()

                if method == "count":
                    num_files = int(file_count_var.get())
                    self._split_by_count(output_folder, num_files)
                else:
                    size_value = float(file_size_var.get())
                    size_unit = size_unit_var.get()
                    self._split_by_size(output_folder, size_value, size_unit, dialog)

                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Split Error", f"Failed to split file:\n{str(e)}")

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Split", command=do_split, width=12).pack(side=tk.RIGHT, padx=5)

    def _split_by_count(self, output_folder: str, num_files: int):
        """Split JSON into specified number of files."""
        if isinstance(self.json_data, list):
            items = self.json_data
            items_per_file = max(1, len(items) // num_files)

            file_index = 0
            for i in range(0, len(items), items_per_file):
                if file_index >= num_files - 1 and i + items_per_file < len(items):
                    # Last file gets remaining items
                    chunk = items[i:]
                else:
                    chunk = items[i:i + items_per_file]

                if chunk:  # Only create file if there's data
                    output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(chunk, f, indent=2, ensure_ascii=False)
                    file_index += 1

                if file_index >= num_files:
                    break

        elif isinstance(self.json_data, dict):
            items = list(self.json_data.items())
            items_per_file = max(1, len(items) // num_files)

            file_index = 0
            for i in range(0, len(items), items_per_file):
                if file_index >= num_files - 1 and i + items_per_file < len(items):
                    # Last file gets remaining items
                    chunk_items = items[i:]
                else:
                    chunk_items = items[i:i + items_per_file]

                if chunk_items:  # Only create file if there's data
                    chunk_dict = dict(chunk_items)
                    output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(chunk_dict, f, indent=2, ensure_ascii=False)
                    file_index += 1

                if file_index >= num_files:
                    break

        messagebox.showinfo("Split Complete",
                           f"Successfully split into {file_index} files in:\n{output_folder}")
        self.status_label.config(text=f"Split into {file_index} files")

    def _split_by_size(self, output_folder: str, size_value: float, size_unit: str, parent_dialog=None):
        """Split JSON by file size, automatically going one level deeper for oversized keys."""
        # Convert size to bytes
        size_multipliers = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}
        max_size_bytes = size_value * size_multipliers[size_unit]

        file_index = 0
        current_chunk = [] if isinstance(self.json_data, list) else {}
        current_size = 0

        def get_item_size(item):
            """Estimate size of JSON item in bytes."""
            return len(json.dumps(item, ensure_ascii=False).encode('utf-8'))

        def save_chunk():
            """Save current chunk to file."""
            nonlocal file_index, current_chunk, current_size
            if (isinstance(current_chunk, list) and len(current_chunk) > 0) or \
               (isinstance(current_chunk, dict) and len(current_chunk) > 0):
                output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(current_chunk, f, indent=2, ensure_ascii=False)
                file_index += 1
                current_chunk = [] if isinstance(self.json_data, list) else {}
                current_size = 0

        def split_nested_dict(parent_key: str, nested_dict: dict):
            """Split a nested dictionary one level deeper."""
            nonlocal file_index
            nested_chunk = {}
            nested_size = 0

            for nested_key, nested_value in nested_dict.items():
                nested_item_size = get_item_size({nested_key: nested_value})

                # If adding this would exceed limit and we have content, save current nested chunk
                if nested_size + nested_item_size > max_size_bytes and len(nested_chunk) > 0:
                    output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump({parent_key: nested_chunk}, f, indent=2, ensure_ascii=False)
                    file_index += 1
                    nested_chunk = {}
                    nested_size = 0

                nested_chunk[nested_key] = nested_value
                nested_size += nested_item_size

            # Save final nested chunk
            if len(nested_chunk) > 0:
                output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({parent_key: nested_chunk}, f, indent=2, ensure_ascii=False)
                file_index += 1

        def split_nested_list(parent_key: str, nested_list: list):
            """Split a nested list one level deeper."""
            nonlocal file_index
            nested_chunk = []
            nested_size = 0

            for nested_item in nested_list:
                nested_item_size = get_item_size(nested_item)

                # If adding this would exceed limit and we have content, save current nested chunk
                if nested_size + nested_item_size > max_size_bytes and len(nested_chunk) > 0:
                    output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump({parent_key: nested_chunk}, f, indent=2, ensure_ascii=False)
                    file_index += 1
                    nested_chunk = []
                    nested_size = 0

                nested_chunk.append(nested_item)
                nested_size += nested_item_size

            # Save final nested chunk
            if len(nested_chunk) > 0:
                output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({parent_key: nested_chunk}, f, indent=2, ensure_ascii=False)
                file_index += 1

        if isinstance(self.json_data, list):
            for idx, item in enumerate(self.json_data):
                item_size = get_item_size(item)
                item_size_mb = item_size / (1024 * 1024)

                # Check if single item exceeds max size
                if item_size > max_size_bytes:
                    # If it's a dict or list, offer choice to go deeper
                    if isinstance(item, dict) and len(item) > 0:
                        # Create custom dialog with three options
                        choice_dialog = tk.Toplevel(parent_dialog if parent_dialog else self.root)
                        choice_dialog.title("Oversized Item")
                        choice_dialog.geometry("450x200")
                        choice_dialog.transient(parent_dialog if parent_dialog else self.root)
                        choice_dialog.grab_set()

                        # Center dialog
                        choice_dialog.update_idletasks()
                        x = (choice_dialog.winfo_screenwidth() // 2) - (225)
                        y = (choice_dialog.winfo_screenheight() // 2) - (100)
                        choice_dialog.geometry(f"450x200+{x}+{y}")

                        choice = tk.StringVar(value="")

                        ttk.Label(choice_dialog,
                                 text=f"Item at index [{idx}] is {item_size_mb:.2f} MB\n(exceeds {size_value} {size_unit} limit)",
                                 font=('Arial', 10, 'bold')).pack(pady=15)

                        ttk.Label(choice_dialog, text="What would you like to do?").pack(pady=5)

                        btn_frame = ttk.Frame(choice_dialog)
                        btn_frame.pack(pady=20)

                        ttk.Button(btn_frame, text="Create Separate File",
                                  command=lambda: [choice.set("separate"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Split One Level Deeper",
                                  command=lambda: [choice.set("deeper"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Skip This Item",
                                  command=lambda: [choice.set("skip"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)

                        choice_dialog.wait_window()

                        if choice.get() == "separate":
                            if len(current_chunk) > 0:
                                save_chunk()
                            oversized_chunk = [item]
                            output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(oversized_chunk, f, indent=2, ensure_ascii=False)
                            file_index += 1
                        elif choice.get() == "deeper":
                            if len(current_chunk) > 0:
                                save_chunk()
                            split_nested_dict(f"[{idx}]", item)
                        # else: skip
                        continue
                    elif isinstance(item, list) and len(item) > 0:
                        # Create custom dialog with three options
                        choice_dialog = tk.Toplevel(parent_dialog if parent_dialog else self.root)
                        choice_dialog.title("Oversized Item")
                        choice_dialog.geometry("450x200")
                        choice_dialog.transient(parent_dialog if parent_dialog else self.root)
                        choice_dialog.grab_set()

                        # Center dialog
                        choice_dialog.update_idletasks()
                        x = (choice_dialog.winfo_screenwidth() // 2) - (225)
                        y = (choice_dialog.winfo_screenheight() // 2) - (100)
                        choice_dialog.geometry(f"450x200+{x}+{y}")

                        choice = tk.StringVar(value="")

                        ttk.Label(choice_dialog,
                                 text=f"Item at index [{idx}] is {item_size_mb:.2f} MB\n(exceeds {size_value} {size_unit} limit)",
                                 font=('Arial', 10, 'bold')).pack(pady=15)

                        ttk.Label(choice_dialog, text="What would you like to do?").pack(pady=5)

                        btn_frame = ttk.Frame(choice_dialog)
                        btn_frame.pack(pady=20)

                        ttk.Button(btn_frame, text="Create Separate File",
                                  command=lambda: [choice.set("separate"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Split One Level Deeper",
                                  command=lambda: [choice.set("deeper"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Skip This Item",
                                  command=lambda: [choice.set("skip"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)

                        choice_dialog.wait_window()

                        if choice.get() == "separate":
                            if len(current_chunk) > 0:
                                save_chunk()
                            oversized_chunk = [item]
                            output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(oversized_chunk, f, indent=2, ensure_ascii=False)
                            file_index += 1
                        elif choice.get() == "deeper":
                            if len(current_chunk) > 0:
                                save_chunk()
                            split_nested_list(f"[{idx}]", item)
                        # else: skip
                        continue
                    else:
                        # It's a primitive value that's too large (shouldn't happen often)
                        response = messagebox.askyesno(
                            "Oversized Item",
                            f"Item at index [{idx}] is {item_size_mb:.2f} MB "
                            f"(exceeds {size_value} {size_unit} limit).\n\n"
                            f"Create a separate file for this item?",
                            parent=parent_dialog
                        )

                        if response:
                            if len(current_chunk) > 0:
                                save_chunk()
                            oversized_chunk = [item]
                            output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(oversized_chunk, f, indent=2, ensure_ascii=False)
                            file_index += 1
                        continue

                # Check if adding this item would exceed max size
                if current_size + item_size > max_size_bytes and len(current_chunk) > 0:
                    save_chunk()

                current_chunk.append(item)
                current_size += item_size

            # Save final chunk
            if len(current_chunk) > 0:
                save_chunk()

        elif isinstance(self.json_data, dict):
            for key, value in self.json_data.items():
                item_size = get_item_size({key: value})
                item_size_mb = item_size / (1024 * 1024)

                # Check if single key-value pair exceeds max size
                if item_size > max_size_bytes:
                    # If value is a dict or list, offer choice to go deeper
                    if isinstance(value, dict) and len(value) > 0:
                        # Create custom dialog with three options
                        choice_dialog = tk.Toplevel(parent_dialog if parent_dialog else self.root)
                        choice_dialog.title("Oversized Key")
                        choice_dialog.geometry("450x220")
                        choice_dialog.transient(parent_dialog if parent_dialog else self.root)
                        choice_dialog.grab_set()

                        # Center dialog
                        choice_dialog.update_idletasks()
                        x = (choice_dialog.winfo_screenwidth() // 2) - (225)
                        y = (choice_dialog.winfo_screenheight() // 2) - (110)
                        choice_dialog.geometry(f"450x220+{x}+{y}")

                        choice = tk.StringVar(value="")

                        ttk.Label(choice_dialog,
                                 text=f"Key '{key}' is {item_size_mb:.2f} MB\n(exceeds {size_value} {size_unit} limit)",
                                 font=('Arial', 10, 'bold')).pack(pady=15)

                        ttk.Label(choice_dialog, text="What would you like to do?").pack(pady=5)

                        btn_frame = ttk.Frame(choice_dialog)
                        btn_frame.pack(pady=20)

                        ttk.Button(btn_frame, text="Create Separate File",
                                  command=lambda: [choice.set("separate"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Split One Level Deeper",
                                  command=lambda: [choice.set("deeper"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Skip This Key",
                                  command=lambda: [choice.set("skip"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)

                        choice_dialog.wait_window()

                        if choice.get() == "separate":
                            if len(current_chunk) > 0:
                                save_chunk()
                            oversized_chunk = {key: value}
                            output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(oversized_chunk, f, indent=2, ensure_ascii=False)
                            file_index += 1
                        elif choice.get() == "deeper":
                            if len(current_chunk) > 0:
                                save_chunk()
                            split_nested_dict(key, value)
                        # else: skip
                        continue
                    elif isinstance(value, list) and len(value) > 0:
                        # Create custom dialog with three options
                        choice_dialog = tk.Toplevel(parent_dialog if parent_dialog else self.root)
                        choice_dialog.title("Oversized Key")
                        choice_dialog.geometry("450x220")
                        choice_dialog.transient(parent_dialog if parent_dialog else self.root)
                        choice_dialog.grab_set()

                        # Center dialog
                        choice_dialog.update_idletasks()
                        x = (choice_dialog.winfo_screenwidth() // 2) - (225)
                        y = (choice_dialog.winfo_screenheight() // 2) - (110)
                        choice_dialog.geometry(f"450x220+{x}+{y}")

                        choice = tk.StringVar(value="")

                        ttk.Label(choice_dialog,
                                 text=f"Key '{key}' is {item_size_mb:.2f} MB\n(exceeds {size_value} {size_unit} limit)",
                                 font=('Arial', 10, 'bold')).pack(pady=15)

                        ttk.Label(choice_dialog, text="What would you like to do?").pack(pady=5)

                        btn_frame = ttk.Frame(choice_dialog)
                        btn_frame.pack(pady=20)

                        ttk.Button(btn_frame, text="Create Separate File",
                                  command=lambda: [choice.set("separate"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Split One Level Deeper",
                                  command=lambda: [choice.set("deeper"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)
                        ttk.Button(btn_frame, text="Skip This Key",
                                  command=lambda: [choice.set("skip"), choice_dialog.destroy()],
                                  width=20).pack(pady=5)

                        choice_dialog.wait_window()

                        if choice.get() == "separate":
                            if len(current_chunk) > 0:
                                save_chunk()
                            oversized_chunk = {key: value}
                            output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(oversized_chunk, f, indent=2, ensure_ascii=False)
                            file_index += 1
                        elif choice.get() == "deeper":
                            if len(current_chunk) > 0:
                                save_chunk()
                            split_nested_list(key, value)
                        # else: skip
                        continue
                    else:
                        # It's a primitive value that's too large (shouldn't happen often)
                        response = messagebox.askyesno(
                            "Oversized Key",
                            f"Key '{key}' is {item_size_mb:.2f} MB "
                            f"(exceeds {size_value} {size_unit} limit).\n\n"
                            f"Create a separate file for this key?",
                            parent=parent_dialog
                        )

                        if response:
                            if len(current_chunk) > 0:
                                save_chunk()
                            oversized_chunk = {key: value}
                            output_file = os.path.join(output_folder, f"split_part_{file_index + 1}.json")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(oversized_chunk, f, indent=2, ensure_ascii=False)
                            file_index += 1
                        continue

                # Check if adding this key-value would exceed max size
                if current_size + item_size > max_size_bytes and len(current_chunk) > 0:
                    save_chunk()

                current_chunk[key] = value
                current_size += item_size

            # Save final chunk
            if len(current_chunk) > 0:
                save_chunk()

        messagebox.showinfo("Split Complete",
                           f"Successfully split into {file_index} files in:\n{output_folder}")
        self.status_label.config(text=f"Split into {file_index} files")

    def expand_all(self):
        """Expand all tree nodes (with confirmation for large trees)."""
        response = messagebox.askyesno(
            "Expand All",
            "Expanding all nodes may take time for large files. Continue?"
        )
        if response:
            self._expand_all_recursive('')

    def _expand_all_recursive(self, parent: str):
        """Recursively expand all nodes."""
        items = self.tree.get_children(parent)
        for item in items:
            self.tree.item(item, open=True)
            self._expand_all_recursive(item)

    def collapse_all(self):
        """Collapse all tree nodes."""
        self._collapse_all_recursive('')

    def _collapse_all_recursive(self, parent: str):
        """Recursively collapse all nodes."""
        items = self.tree.get_children(parent)
        for item in items:
            self.tree.item(item, open=False)
            self._collapse_all_recursive(item)


def main():
    root = tk.Tk()
    app = JSONEditorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
