"""
error_encyclopedia.py
----------------------
Searchable, browsable reference of common Python errors.
Works fully offline: database.py already falls back to a local
JSON file if MySQL is unavailable, so this screen never breaks.
"""

import tkinter as tk
from tkinter import ttk

import database


class EncyclopediaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(header, text="Error Encyclopedia", font=("Segoe UI", 20, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(side="left")
        tk.Button(header, text="Back to Dashboard", command=lambda: controller.show_frame("StudentDashboardFrame"),
                  bg="#161b22", fg="#c9d1d9", relief="flat", padx=12, pady=6).pack(side="right")

        search_row = tk.Frame(self, bg="#0d1117")
        search_row.pack(fill="x", padx=30, pady=10)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_list())
        entry = tk.Entry(search_row, textvariable=self.search_var, font=("Segoe UI", 12),
                          bg="#161b22", fg="white", insertbackground="white", relief="flat")
        entry.pack(fill="x", ipady=6)
        entry.insert(0, "")
        tk.Label(search_row, text="Search by error name or category (e.g. 'Type', 'Index')",
                 font=("Segoe UI", 9), fg="#8b949e", bg="#0d1117").pack(anchor="w")

        body = tk.Frame(self, bg="#0d1117")
        body.pack(fill="both", expand=True, padx=30, pady=10)

        list_frame = tk.Frame(body, bg="#0d1117")
        list_frame.pack(side="left", fill="y", padx=(0, 20))
        self.listbox = tk.Listbox(list_frame, width=28, font=("Segoe UI", 11),
                                   bg="#161b22", fg="#e6edf3", relief="flat", highlightthickness=0)
        self.listbox.pack(fill="y", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.show_detail)

        self.detail_box = tk.Text(body, font=("Segoe UI", 11), bg="#161b22", fg="#c9d1d9",
                                   relief="flat", wrap="word")
        self.detail_box.pack(side="left", fill="both", expand=True)
        self.detail_box.config(state="disabled")

        self.errors_cache = []

    def on_show(self):
        """Called whenever this frame becomes visible."""
        self.refresh_list()

    def refresh_list(self):
        keyword = self.search_var.get()
        self.errors_cache = database.search_errors(keyword)
        self.listbox.delete(0, tk.END)
        for e in self.errors_cache:
            self.listbox.insert(tk.END, e["error_name"])

    def show_detail(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        error = self.errors_cache[selection[0]]
        text = (
            f"{error['error_name']}  ({error.get('category', '')})\n"
            f"{'-'*50}\n\n"
            f"Meaning:\n{error.get('meaning', '')}\n\n"
            f"Explanation:\n{error.get('beginner_explanation', '')}\n\n"
            f"Example:\n{error.get('example_code', 'N/A')}\n\n"
            f"Possible fix:\n{error.get('fix_text', 'N/A')}\n\n"
            f"Prevention tip:\n{error.get('prevention_tip', 'N/A')}"
        )
        self.detail_box.config(state="normal")
        self.detail_box.delete("1.0", tk.END)
        self.detail_box.insert(tk.END, text)
        self.detail_box.config(state="disabled")
