"""
modules/error_detection.py
---------------------------
The Error Detection & Live Debugging screen for SYNTAXAA.
Integrates the VS Code-style panel containing the AI Debugger with
offline/network detection.
"""

import tkinter as tk
from tkinter import messagebox
import database
from modules import theme
from modules.debug_panel import DebugPanel


class ErrorDetectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        # Proportional vertical weighting for main layout
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=1)

        # =========================================================
        # TOP PANEL: CODE EDITOR & ACTIONS
        # =========================================================
        self.top_frame = tk.Frame(self, bg=theme.BG)
        self.top_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 5))

        # 1. Header Title
        header = tk.Label(
            self.top_frame,
            text="Intelligent Error Detection & Debugger",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=theme.BG
        )
        header.pack(side="top", anchor="w", pady=(0, 5))

        # 2. Action Buttons Bar (Packed TOP so it stays strictly visible)
        self.btn_frame = tk.Frame(self.top_frame, bg=theme.BG)
        self.btn_frame.pack(side="bottom", fill="x", pady=(5, 5))

        self.analyze_btn = tk.Button(
            self.btn_frame,
            text="▶ Analyze & Debug Code",
            font=("Segoe UI", 10, "bold"),
            bg="#238636",
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.run_code_analysis
        )
        self.analyze_btn.pack(side="left")

        self.back_btn = tk.Button(
            self.btn_frame,
            text="Back to Dashboard",
            font=("Segoe UI", 9),
            bg="#21262d",
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.go_back
        )
        self.back_btn.pack(side="right")

        # 3. Code Editor Text Box (Fills remaining middle space)
        self.code_editor = tk.Text(
            self.top_frame,
            font=("Consolas", 11),
            bg="#0d1117",
            fg="#e6edf3",
            insertbackground="white",
            bd=1,
            relief="solid"
        )
        self.code_editor.pack(side="top", fill="both", expand=True, pady=5)

        # =========================================================
        # BOTTOM PANEL: DEBUG PANEL
        # =========================================================
        self.vscode_panel = DebugPanel(self, controller)
        self.vscode_panel.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))

    def run_code_analysis(self):
        """Simulates syntax/runtime error checking and updates the debug panel."""
        code = self.code_editor.get("1.0", tk.END).strip()

        if not code:
            messagebox.showwarning("Empty Code", "Please enter some Python code to analyze.")
            return

        detected_error = ""
        error_name = ""

        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            detected_error = f"SyntaxError: {e.msg} at line {e.lineno}"
            error_name = "SyntaxError"
        except Exception as e:
            detected_error = f"{type(e).__name__}: {str(e)}"
            error_name = type(e).__name__

        if self.controller.current_user:
            user_id = self.controller.current_user["user_id"]
            database.log_history(user_id, error_name, code)

        self.vscode_panel.update_debug_data(code, detected_error)

    def go_back(self):
        if self.controller.current_user and self.controller.current_user.get("user_type") == "teacher":
            self.controller.show_frame("TeacherDashboardFrame")
        else:
            self.controller.show_frame("StudentDashboardFrame")

    def on_show(self):
        pass