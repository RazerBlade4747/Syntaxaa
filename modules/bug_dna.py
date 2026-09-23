"""
bug_dna.py
----------
Generates a simple personalised "Bug DNA" profile for a student:
which error categories occur most often, and which concepts are
likely weak.

VIVA NOTE: This is plain arithmetic over the performance_data table -
no machine learning. We simply rank categories by frequency and label
the top ones as "weak concepts". This is intentionally simple so it
can be explained line by line in a viva.

UI ENHANCED: breakdown rows are now bordered cards with a small
progress bar showing each category's relative share of mistakes.
generate_bug_dna() logic is unchanged.
"""

import tkinter as tk

import database
from modules import theme

CATEGORY_TO_CONCEPT = {
    "Syntax": "Basic code structure (brackets, colons, operators)",
    "Indentation": "Indentation and code blocks",
    "Name": "Variable creation and usage",
    "Type": "Data types and type conversion",
    "Logic": "Program logic (conditions, loops, indexing)",
    "File Handling": "Opening, reading and writing files correctly",
    "Pickle": "Saving and loading data using the pickle module",
    "Attribute": "Using the right methods/properties for an object's type",
    "Import": "Importing modules and library names correctly",
    "Tkinter": "Building GUI screens with Tkinter widgets",
    "Database": "Connecting to and querying the MySQL database",
    "General": "General debugging practice"
}


def generate_bug_dna(user_id):
    """
    Returns a dict:
    {
      "categories": [ {category, frequency, avg_debug_time_seconds, concept}, ... ],
      "weak_concepts": [ "concept1", "concept2" ],
      "total_errors": int
    }
    """
    rows = database.get_bug_dna(user_id)

    if not rows:
        return {
            "categories": [],
            "weak_concepts": [],
            "total_errors": 0,
            "message": "No debugging history yet. Start checking some code to build your Bug DNA!"
        }

    total_errors = sum(r["frequency"] for r in rows)

    categories = []
    for r in rows:
        categories.append({
            "category": r["error_category"],
            "frequency": r["frequency"],
            "avg_debug_time_seconds": r["avg_debug_time_seconds"],
            "concept": CATEGORY_TO_CONCEPT.get(r["error_category"], r["error_category"])
        })

    # Weak concepts = top categories making up the majority of mistakes,
    # or simply anything appearing 3+ times.
    weak_concepts = [c["concept"] for c in categories if c["frequency"] >= 3][:3]
    if not weak_concepts and categories:
        weak_concepts = [categories[0]["concept"]]

    return {
        "categories": categories,
        "weak_concepts": weak_concepts,
        "total_errors": total_errors,
        "message": None
    }


# =========================================================
# GUI: Bug DNA screen
# =========================================================

class BugDNAFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        theme.build_header(self, "Your Bug DNA",
                            subtitle="Your personal mistake patterns, at a glance.",
                            on_back=lambda: controller.show_frame("StudentDashboardFrame"))

        canvas_wrap = tk.Frame(self, bg=theme.BG)
        canvas_wrap.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        self.content = tk.Frame(canvas_wrap, bg=theme.BG)
        self.content.pack(fill="both", expand=True)

    def on_show(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        user = self.controller.current_user
        if not user:
            return
        data = generate_bug_dna(user["user_id"])

        if data["message"]:
            tk.Label(self.content, text=data["message"], font=theme.F_BODY,
                     fg=theme.TEXT_MUTED, bg=theme.BG).pack(pady=30)
            return

        tk.Label(self.content, text=f"Total logged mistakes: {data['total_errors']}",
                 font=theme.F_BODY, fg=theme.TEXT, bg=theme.BG).pack(anchor="w", pady=(0, 14))

        tk.Label(self.content, text="LIKELY WEAK CONCEPTS", font=theme.F_SMALL,
                 fg=theme.WARNING, bg=theme.BG).pack(anchor="w")
        weak_wrap = tk.Frame(self.content, bg=theme.BG)
        weak_wrap.pack(fill="x", pady=(6, 20))
        for concept in data["weak_concepts"]:
            chip = tk.Frame(weak_wrap, bg=theme.SURFACE, highlightthickness=1,
                             highlightbackground=theme.WARNING)
            tk.Label(chip, text=f"\u26A0  {concept}", font=theme.F_SMALL, fg=theme.TEXT,
                     bg=theme.SURFACE, padx=10, pady=5).pack()
            chip.pack(side="left", padx=(0, 8), pady=2)

        tk.Label(self.content, text="BREAKDOWN BY CATEGORY", font=theme.F_SMALL,
                 fg=theme.ACCENT, bg=theme.BG).pack(anchor="w", pady=(4, 8))

        max_freq = max((c["frequency"] for c in data["categories"]), default=1)
        for i, cat in enumerate(data["categories"]):
            accent = theme.CARD_ACCENTS[i % len(theme.CARD_ACCENTS)]
            row = tk.Frame(self.content, bg=theme.SURFACE, highlightthickness=1,
                            highlightbackground=theme.BORDER)
            row.pack(fill="x", pady=4)

            top = tk.Frame(row, bg=theme.SURFACE)
            top.pack(fill="x", padx=14, pady=(10, 2))
            tk.Label(top, text=cat["concept"], font=theme.F_BODY_BOLD, fg=theme.TEXT,
                     bg=theme.SURFACE, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(top, text=f"{cat['frequency']} times", font=theme.F_SMALL,
                     fg=theme.TEXT_MUTED, bg=theme.SURFACE).pack(side="right", padx=(10, 0))
            tk.Label(top, text=f"~{cat['avg_debug_time_seconds']}s avg", font=theme.F_SMALL,
                     fg=theme.TEXT_MUTED, bg=theme.SURFACE).pack(side="right")

            # Lightweight bar showing this category's share of total mistakes.
            bar_bg = tk.Frame(row, bg=theme.SURFACE_ALT, height=6)
            bar_bg.pack(fill="x", padx=14, pady=(2, 12))
            bar_bg.pack_propagate(False)
            share = max(cat["frequency"] / max_freq, 0.04)
            bar_fill = tk.Frame(bar_bg, bg=accent)
            bar_fill.place(relx=0, rely=0, relwidth=share, relheight=1)
