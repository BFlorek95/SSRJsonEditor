import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import ijson
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import threading


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
        import platform
        self.is_mac = platform.system() == 'Darwin'
        self.modifier = 'Command' if self.is_mac else 'Control'

        self._setup_menu()
        self._setup_ui()
        self._setup_context_menu()

    def _setup_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        accel_prefix = "Cmd" if self.is_mac else "Ctrl"
        file_menu.add_command(label="Open", command=self.open_file, accelerator=f"{accel_prefix}+O")
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

        # Save button
        save_btn = ttk.Button(toolbar, text="💾 Save", command=self.save_file, width=12)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Save As button
        save_as_btn = ttk.Button(toolbar, text="💾 Save As", command=self.save_file_as, width=12)
        save_as_btn.pack(side=tk.LEFT, padx=2, pady=2)

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

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Create initial "Welcome" tab
        self._create_welcome_tab()

        # Search bar
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.find_next())

        # Regex checkbox
        self.regex_var = tk.BooleanVar()
        regex_check = ttk.Checkbutton(search_frame, text="Regex", variable=self.regex_var)
        regex_check.pack(side=tk.LEFT, padx=2)

        ttk.Button(search_frame, text="Find", command=self.find_next).pack(side=tk.LEFT)

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

        # Check file size and warn if very large
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)

        if size_mb > 100:
            response = messagebox.askyesno(
                "Large File Warning",
                f"This file is {size_mb:.1f} MB. Loading may take some time.\n\nContinue?"
            )
            if not response:
                return

        self.current_file = file_path
        self.status_label.config(text=f"Loading: {os.path.basename(file_path)}...")
        self.file_size_label.config(text=f"Size: {size_mb:.1f} MB")
        self.root.update()

        # Load in background thread for large files
        def load_thread():
            try:
                self.loader = LazyJSONLoader(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)

                self.root.after(0, self._populate_tree)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Loaded: {os.path.basename(file_path)}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to load file:\n{str(e)}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="Error loading file"))

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
            root_id = self.tree.insert('', 'end', text='Root {}', open=True)
            self._add_dict_nodes(root_id, self.json_data)
        elif isinstance(self.json_data, list):
            root_id = self.tree.insert('', 'end', text='Root []', open=True)
            self._add_list_nodes(root_id, self.json_data)
        else:
            self.tree.insert('', 'end', text=f'Root: {self.json_data}')

    def _add_dict_nodes(self, parent_id: str, data: dict, max_items: int = 1000):
        """Add dictionary nodes to tree (with lazy loading for large dicts)."""
        items = list(data.items())

        if len(items) > max_items:
            # Add only first batch
            for key, value in items[:max_items]:
                self._add_node(parent_id, key, value)
            # Add placeholder for more items
            self.tree.insert(parent_id, 'end', text=f'... ({len(items) - max_items} more items)', tags=('placeholder',))
        else:
            for key, value in items:
                self._add_node(parent_id, key, value)

    def _add_list_nodes(self, parent_id: str, data: list, max_items: int = 1000):
        """Add list nodes to tree (with lazy loading for large arrays)."""
        if len(data) > max_items:
            # Add only first batch
            for i, value in enumerate(data[:max_items]):
                self._add_node(parent_id, f"[{i}]", value)
            # Add placeholder for more items
            self.tree.insert(parent_id, 'end', text=f'... ({len(data) - max_items} more items)', tags=('placeholder',))
        else:
            for i, value in enumerate(data):
                self._add_node(parent_id, f"[{i}]", value)

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

    def find_next(self):
        """Find next occurrence of search term."""
        search_term = self.search_var.get()
        if not search_term:
            return

        use_regex = self.regex_var.get()

        # Validate regex if regex mode is enabled
        if use_regex:
            try:
                re.compile(search_term)
            except re.error as e:
                messagebox.showerror("Invalid Regex", f"Invalid regular expression:\n{str(e)}")
                return

        # Get current selection or start from beginning
        current = self.tree.selection()
        start_item = current[0] if current else ''

        # Search through tree items
        found = self._search_tree(start_item, search_term, use_regex)

        if found:
            self.tree.selection_set(found)
            self.tree.focus(found)
            self.tree.see(found)
        else:
            search_type = "regex pattern" if use_regex else "text"
            messagebox.showinfo("Not Found", f"'{search_term}' not found ({search_type})")

    def _search_tree(self, start_item: str, search_term: str, use_regex: bool = False, started: bool = False) -> Optional[str]:
        """Recursively search tree for term."""
        items = self.tree.get_children() if not start_item else self.tree.get_children('')

        for item in items:
            if started or item == start_item:
                started = True
                if item != start_item:
                    text = self.tree.item(item, 'text')
                    if self._matches_search(text, search_term, use_regex):
                        return item

            # Search children
            children = self.tree.get_children(item)
            if children:
                result = self._search_tree_children(item, search_term, use_regex)
                if result:
                    return result

        return None

    def _search_tree_children(self, parent: str, search_term: str, use_regex: bool = False) -> Optional[str]:
        """Search children of a tree item."""
        for item in self.tree.get_children(parent):
            text = self.tree.item(item, 'text')
            if self._matches_search(text, search_term, use_regex):
                return item

            # Recursively search children
            result = self._search_tree_children(item, search_term, use_regex)
            if result:
                return result

        return None

    def _matches_search(self, text: str, search_term: str, use_regex: bool) -> bool:
        """Check if text matches the search term (with or without regex)."""
        if use_regex:
            try:
                return re.search(search_term, text, re.IGNORECASE) is not None
            except re.error:
                return False
        else:
            return search_term.lower() in text.lower()

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
