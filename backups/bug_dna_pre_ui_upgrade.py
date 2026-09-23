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
"""

import tkinter as tk

import database

CATEGORY_TO_CONCEPT = {
    "Syntax": "Basic code structure (brackets, colons, operators)",
    "Indentation": "Indentation and code blocks",
    "Name": "Variable creation and usage",
    "Type": "Data types and type conversion",
    "Logic": "Program logic (conditions, loops, indexing)",
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
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(header, text="Your Bug DNA", font=("Segoe UI", 20, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(side="left")
        tk.Button(header, text="Back to Dashboard", command=lambda: controller.show_frame("StudentDashboardFrame"),
                  bg="#161b22", fg="#c9d1d9", relief="flat", padx=12, pady=6).pack(side="right")

        self.content = tk.Frame(self, bg="#0d1117")
        self.content.pack(fill="both", expand=True, padx=30, pady=10)

    def on_show(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        user = self.controller.current_user
        if not user:
            return
        data = generate_bug_dna(user["user_id"])

        if data["message"]:
            tk.Label(self.content, text=data["message"], font=("Segoe UI", 12),
                     fg="#8b949e", bg="#0d1117").pack(pady=30)
            return

        tk.Label(self.content, text=f"Total logged mistakes: {data['total_errors']}",
                 font=("Segoe UI", 12), fg="#c9d1d9", bg="#0d1117").pack(anchor="w", pady=(0, 10))

        tk.Label(self.content, text="Likely weak concepts:", font=("Segoe UI", 13, "bold"),
                 fg="#f0883e", bg="#0d1117").pack(anchor="w")
        for concept in data["weak_concepts"]:
            tk.Label(self.content, text=f"• {concept}", font=("Segoe UI", 11),
                     fg="#c9d1d9", bg="#0d1117").pack(anchor="w", padx=10)

        tk.Label(self.content, text="Breakdown by category:", font=("Segoe UI", 13, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(anchor="w", pady=(20, 5))

        for cat in data["categories"]:
            row = tk.Frame(self.content, bg="#161b22")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=cat["concept"], font=("Segoe UI", 11), fg="#e6edf3",
                     bg="#161b22", anchor="w").pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(row, text=f"{cat['frequency']} times", font=("Segoe UI", 10), fg="#8b949e",
                     bg="#161b22").pack(side="right", padx=10)
            tk.Label(row, text=f"~{cat['avg_debug_time_seconds']}s avg", font=("Segoe UI", 10),
                     fg="#8b949e", bg="#161b22").pack(side="right", padx=10)
