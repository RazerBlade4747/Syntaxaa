"""
modules/error_encyclopedia.py
-----------------------------
Searchable, browsable reference of common CPython, Tkinter, and MySQL errors.
Organized into collapsible module categories using a ttk.Treeview layout.
Works fully offline without external dependencies.
"""

import tkinter as tk
from tkinter import ttk
from modules import theme

# =============================================================================
# ERROR DATABASE STRUCTURED BY MODULE
# =============================================================================
ENCYCLOPEDIA_DATA = {
    "CPython Core Exceptions": {
        "SyntaxError": {
            "summary": "Invalid Python syntax encountered during code compilation.",
            "cause": "Missing colons, unmatched parentheses/brackets/quotes, or invalid keyword usage.",
            "fix": "Check the line indicated in the traceback for missing punctuation or unbalanced brackets."
        },
        "IndentationError": {
            "summary": "Code block is incorrectly indented.",
            "cause": "Mixing tabs and spaces, or omitting required indentation inside an if/loop/function block.",
            "fix": "Standardize all indentations to 4 spaces per nesting level."
        },
        "NameError": {
            "summary": "A local or global name is not found.",
            "cause": "Typo in variable/function name, or accessing a variable before assigning it.",
            "fix": "Verify the spelling and ensure the variable is declared in the current scope prior to use."
        },
        "TypeError": {
            "summary": "An operation or function is applied to an object of inappropriate type.",
            "cause": "Concatenating str and int, calling a non-callable object, or missing required positional arguments.",
            "fix": "Convert types explicitly (e.g., str(val)) or verify function signatures."
        },
        "ValueError": {
            "summary": "Operation receives an argument with correct type but invalid value.",
            "cause": "Converting non-numeric string with int() or passing invalid options to a parameter.",
            "fix": "Validate input formats before processing or catch with try/except."
        },
        "AttributeError": {
            "summary": "Attribute reference or assignment failed.",
            "cause": "Calling a non-existent method on an object or operating on a None variable.",
            "fix": "Check object type using type() or print() to verify supported methods."
        },
        "IndexError": {
            "summary": "Sequence index is out of range.",
            "cause": "Accessing list/tuple element using an index >= len(sequence) or < -len(sequence).",
            "fix": "Check bounds using len() or loop directly over items instead of indices."
        },
        "KeyError": {
            "summary": "Mapping key is not found in a dictionary.",
            "cause": "Looking up a dictionary key that does not exist.",
            "fix": "Use dict.get(key, default) or verify key presence using 'if key in dict:'."
        },
        "ZeroDivisionError": {
            "summary": "Second argument to a division or modulo operation is zero.",
            "cause": "Dividing by a variable whose calculated value evaluates to 0.",
            "fix": "Add a conditional guard: 'if divisor != 0:' before dividing."
        },
        "ImportError / ModuleNotFoundError": {
            "summary": "An imported module or attribute cannot be located.",
            "cause": "Package not installed in virtual environment, typo in module name, or circular imports.",
            "fix": "Install missing packages via pip or check file paths and module names."
        }
    },
    "Tkinter GUI Exceptions": {
        "TclError: bad geometry specifier": {
            "summary": "Window geometry dimensions string is invalid.",
            "cause": "Passing incorrectly formatted string to root.geometry(), e.g., '800x600' using 'X' instead of lower 'x'.",
            "fix": "Use format string 'WIDTHxHEIGHT' with lowercase 'x' (e.g., '800x600')."
        },
        "TclError: image doesn't exist": {
            "summary": "Tkinter cannot locate the specified PhotoImage or image reference.",
            "cause": "Image variable garbage collected or image path passed incorrectly.",
            "fix": "Keep an explicit reference to image objects (e.g., self.img = PhotoImage(...))."
        },
        "TclError: cannot use geometry manager grid inside": {
            "summary": "Mixed geometry managers inside the same parent container.",
            "cause": "Combining pack() and grid() on widgets that share the same parent Frame or Window.",
            "fix": "Stick exclusively to pack() OR grid() for children belonging to the same parent frame."
        },
        "TclError: invalid command name": {
            "summary": "Widget referenced after destruction or before creation.",
            "cause": "Calling methods on a widget after invoking destroy() or operating on destroyed roots.",
            "fix": "Ensure widget event bindings/callbacks stop prior to destroying widgets."
        },
        "TclError: unknown option": {
            "summary": "Invalid configuration key passed to widget.",
            "cause": "Misspelling widget properties (e.g., using 'background' where 'bg' is required, or widget-specific invalid keys).",
            "fix": "Verify valid configuration options for the target Tkinter/ttk widget."
        }
    },
    "MySQL Connector Exceptions": {
        "mysql.connector.errors.ProgrammingError (1045)": {
            "summary": "Access denied for database user.",
            "cause": "Incorrect username, wrong password, or user lacks access rights for specified host.",
            "fix": "Verify connection credentials (user, password, host) in database config."
        },
        "mysql.connector.errors.ProgrammingError (1049)": {
            "summary": "Unknown database.",
            "cause": "Target database name specified in connect() does not exist on the MySQL server.",
            "fix": "Check schema spelling or execute 'CREATE DATABASE <db_name>' on server."
        },
        "mysql.connector.errors.ProgrammingError (1146)": {
            "summary": "Table doesn't exist.",
            "cause": "Executing SQL query against a table name that hasn't been created.",
            "fix": "Verify table names or run database migration/init scripts to generate tables."
        },
        "mysql.connector.errors.OperationalError (2003)": {
            "summary": "Can't connect to MySQL server.",
            "cause": "MySQL service stopped, wrong host/port specified, or firewall blocking port 3306.",
            "fix": "Ensure MySQL server daemon is running and port 3306 is reachable."
        },
        "mysql.connector.errors.IntegrityError (1062)": {
            "summary": "Duplicate entry for key (Primary key / Unique constraint violation).",
            "cause": "Inserting a record with a PRIMARY KEY or UNIQUE column value that already exists.",
            "fix": "Check existing keys before inserting or use 'INSERT IGNORE' / 'ON DUPLICATE KEY UPDATE'."
        },
        "mysql.connector.errors.InterfaceError": {
            "summary": "Failed to communicate with MySQL database interface.",
            "cause": "Attempting operations on a closed connection or closed cursor object.",
            "fix": "Ensure connection and cursor remain open during transaction operations."
        }
    }
}


def get_error_info(error_name: str) -> str:
    """Helper method for external lookup (e.g., DebugPanel / Problems Tab)."""
    for category, errors in ENCYCLOPEDIA_DATA.items():
        for name, details in errors.items():
            if error_name.strip().lower() in name.lower():
                return (
                    f"📌 Module Category: {category}\n"
                    f"📌 Error Name: {name}\n\n"
                    f"📌 Summary:\n{details['summary']}\n\n"
                    f"❓ Likely Cause:\n{details['cause']}\n\n"
                    f"💡 How to Fix:\n{details['fix']}"
                )

    return f"No direct match for '{error_name}' in local encyclopedia."


# =============================================================================
# ENCYCLOPEDIA GUI SCREEN MODULE
# =============================================================================
class EncyclopediaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        # --- Header Section ---
        header_frame = tk.Frame(self, bg=theme.BG)
        header_frame.pack(side="top", fill="x", padx=15, pady=(15, 10))

        title = tk.Label(
            header_frame,
            text="Offline Error Encyclopedia",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=theme.BG
        )
        title.pack(side="left")

        back_btn = tk.Button(
            header_frame,
            text="Back to Dashboard",
            font=("Segoe UI", 9),
            bg="#21262d",
            fg="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.go_back
        )
        back_btn.pack(side="right")

        # --- Search Bar Section ---
        search_frame = tk.Frame(self, bg=theme.BG)
        search_frame.pack(side="top", fill="x", padx=15, pady=(0, 10))

        search_lbl = tk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 10), fg="white", bg=theme.BG)
        search_lbl.pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_tree())

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            bg="#0d1117",
            fg="white",
            insertbackground="white",
            bd=1,
            relief="solid"
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

        # --- Main Split Content Frame ---
        content_frame = tk.Frame(self, bg=theme.BG)
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # --- Left Side: Categorized Dropdown Treeview ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#0d1117",
            foreground="#c9d1d9",
            fieldbackground="#0d1117",
            rowheight=25,
            font=("Segoe UI", 9)
        )
        style.map("Treeview", background=[("selected", "#1f2937")], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(content_frame, show="tree", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tree_scroll = tk.Scrollbar(content_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)

        # --- Right Side: Error Detail Reader ---
        detail_frame = tk.Frame(content_frame, bg="#161b22", bd=1, relief="solid")
        detail_frame.grid(row=0, column=1, sticky="nsew")

        self.detail_text = tk.Text(
            detail_frame,
            bg="#011627",
            fg="#d6deeb",
            font=("Consolas", 10),
            wrap="word",
            bd=0,
            padx=12,
            pady=12,
            state="disabled"
        )
        self.detail_text.pack(fill="both", expand=True)

        self.populate_tree()

    def populate_tree(self):
        """Populates Treeview hierarchy with module categories and error items."""
        self.tree.delete(*self.tree.get_children())

        for category, errors in ENCYCLOPEDIA_DATA.items():
            parent_node = self.tree.insert("", "end", text=f"📂 {category}", open=True)
            for err_name in errors.keys():
                self.tree.insert(parent_node, "end", text=f"  ❌ {err_name}", values=(category, err_name))

    def filter_tree(self):
        """Filters tree nodes based on search query."""
        query = self.search_var.get().strip().lower()

        if not query:
            self.populate_tree()
            return

        self.tree.delete(*self.tree.get_children())

        for category, errors in ENCYCLOPEDIA_DATA.items():
            matching_errors = [e for e in errors.keys() if query in e.lower() or query in category.lower()]
            if matching_errors:
                parent_node = self.tree.insert("", "end", text=f"📂 {category}", open=True)
                for err_name in matching_errors:
                    self.tree.insert(parent_node, "end", text=f"  ❌ {err_name}", values=(category, err_name))

    def on_item_selected(self, event):
        """Displays error details when a child item is clicked."""
        selected = self.tree.selection()
        if not selected:
            return

        item_values = self.tree.item(selected[0], "values")
        if not item_values:
            return

        category, err_name = item_values[0], item_values[1]
        details = ENCYCLOPEDIA_DATA[category][err_name]

        formatted = (
            f"════════════════════════════════════════════════\n"
            f" 📖 {err_name}\n"
            f" 📁 Module: {category}\n"
            f"════════════════════════════════════════════════\n\n"
            f"📌 Summary:\n{details['summary']}\n\n"
            f"❓ Common Cause:\n{details['cause']}\n\n"
            f"💡 How to Fix:\n{details['fix']}"
        )

        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, formatted)
        self.detail_text.config(state="disabled")

    def go_back(self):
        if self.controller.current_user and self.controller.current_user.get("user_type") == "teacher":
            self.controller.show_frame("TeacherDashboardFrame")
        else:
            self.controller.show_frame("StudentDashboardFrame")

    def on_show(self):
        pass


# Backward-compatibility alias
ErrorEncyclopediaFrame = EncyclopediaFrame