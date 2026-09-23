"""
progress_analysis.py
---------------------
Simple personal progress analysis for a student, built from
user_history and performance_data. No complicated statistics -
just counts, averages and simple ratios, matching the project's
"simple and explainable" principle.
"""

import tkinter as tk

import database


def analyze_progress(user_id):
    """
    Returns a dict summarising a student's learning progress:
      {
        "total_attempts": int,
        "resolved_attempts": int,
        "resolution_rate": float (0-100),
        "most_common_error": str or None,
        "recent_activity": list of history rows
      }
    """
    history = database.get_user_history(user_id, limit=200)

    total_attempts = len(history)
    resolved_attempts = sum(1 for h in history if h["resolved"])
    resolution_rate = (resolved_attempts / total_attempts * 100) if total_attempts else 0

    error_counts = {}
    for h in history:
        name = h.get("error_name")
        if name:
            error_counts[name] = error_counts.get(name, 0) + 1

    most_common_error = None
    if error_counts:
        most_common_error = max(error_counts, key=error_counts.get)

    return {
        "total_attempts": total_attempts,
        "resolved_attempts": resolved_attempts,
        "resolution_rate": round(resolution_rate, 1),
        "most_common_error": most_common_error,
        "recent_activity": history[:10]
    }


def get_improvement_trend(user_id):
    """
    A simple "is this student improving?" measure for the teacher
    dashboard, without needing complicated statistics.

    VIVA NOTE: database.get_user_history() returns attempts newest-first.
    We split that list into two halves - the older half and the more
    recent half - and compare what fraction of attempts were resolved
    in each half. If the recent half has a higher resolved rate, the
    student is improving. This only needs simple counting and division.
    """
    history = database.get_user_history(user_id, limit=200)
    total = len(history)

    if total < 4:
        return {
            "has_enough_data": False,
            "message": "Not enough attempts yet to show a trend (needs at least 4)."
        }

    midpoint = total // 2
    recent_half = history[:midpoint]      # newer attempts
    older_half = history[midpoint:]       # older attempts

    def resolved_rate(rows):
        return (sum(1 for r in rows if r["resolved"]) / len(rows) * 100) if rows else 0

    recent_rate = resolved_rate(recent_half)
    older_rate = resolved_rate(older_half)
    difference = round(recent_rate - older_rate, 1)

    if difference > 5:
        trend = "Improving"
    elif difference < -5:
        trend = "Needs attention"
    else:
        trend = "Steady"

    return {
        "has_enough_data": True,
        "trend": trend,
        "older_resolution_rate": round(older_rate, 1),
        "recent_resolution_rate": round(recent_rate, 1),
        "difference": difference
    }


# =========================================================
# GUI: Personal Progress screen
# =========================================================

class ProgressFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(header, text="My Progress", font=("Segoe UI", 20, "bold"),
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
        data = analyze_progress(user["user_id"])

        stats = tk.Frame(self.content, bg="#0d1117")
        stats.pack(fill="x", pady=10)
        self._stat_card(stats, "Total Attempts", data["total_attempts"])
        self._stat_card(stats, "Resolved", data["resolved_attempts"])
        self._stat_card(stats, "Resolution Rate", f"{data['resolution_rate']}%")

        tk.Label(self.content, text=f"Most common mistake: {data['most_common_error'] or 'None yet'}",
                 font=("Segoe UI", 12), fg="#f0883e", bg="#0d1117").pack(anchor="w", pady=(10, 5))

        trend = get_improvement_trend(user["user_id"])
        if trend["has_enough_data"]:
            trend_text = (f"Improvement trend: {trend['trend']}  "
                          f"(earlier attempts resolved {trend['older_resolution_rate']}% → "
                          f"recent attempts resolved {trend['recent_resolution_rate']}%)")
        else:
            trend_text = trend["message"]
        tk.Label(self.content, text=trend_text, font=("Segoe UI", 11), fg="#3fb950",
                 bg="#0d1117", wraplength=800, justify="left").pack(anchor="w", pady=(0, 15))

        tk.Label(self.content, text="Recent activity:", font=("Segoe UI", 13, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(anchor="w")
        if not data["recent_activity"]:
            tk.Label(self.content, text="No activity yet - try checking some code!",
                     font=("Segoe UI", 11), fg="#8b949e", bg="#0d1117").pack(anchor="w", pady=5)
        for row in data["recent_activity"]:
            status = "✅ Resolved" if row["resolved"] else "🔴 Open"
            text = f"{row.get('error_name') or 'No error'} - {status} - {row['occurred_at']}"
            tk.Label(self.content, text=text, font=("Segoe UI", 10), fg="#c9d1d9",
                     bg="#0d1117").pack(anchor="w", padx=10, pady=2)

    def _stat_card(self, parent, label, value):
        card = tk.Frame(parent, bg="#161b22", padx=20, pady=15)
        card.pack(side="left", padx=10, fill="x", expand=True)
        tk.Label(card, text=str(value), font=("Segoe UI", 20, "bold"), fg="#00e5ff", bg="#161b22").pack()
        tk.Label(card, text=label, font=("Segoe UI", 10), fg="#8b949e", bg="#161b22").pack()
