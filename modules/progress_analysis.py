"""
progress_analysis.py
---------------------
Simple personal progress analysis for a student, built from
user_history and performance_data. No complicated statistics -
just counts, averages and simple ratios, matching the project's
"simple and explainable" principle.

UI ENHANCED with modules/theme.py (stat cards, trend badge, activity
list). analyze_progress() and get_improvement_trend() are unchanged.
"""

import tkinter as tk

import database
from modules import theme


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
    recent_half = history[:midpoint]  # newer attempts
    older_half = history[midpoint:]   # older attempts

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


_TREND_KIND = {"Improving": "success", "Needs attention": "warning", "Steady": "info"}


# =========================================================
# GUI: Personal Progress screen
# =========================================================

class ProgressFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        theme.build_header(self, "My Progress",
                            subtitle="Your debugging history and improvement over time.",
                            on_back=lambda: controller.show_frame("StudentDashboardFrame"))

        self.content = tk.Frame(self, bg=theme.BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=(0, 10))

    def on_show(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        user = self.controller.current_user
        if not user:
            return
        data = analyze_progress(user["user_id"])

        stats = tk.Frame(self.content, bg=theme.BG)
        stats.pack(fill="x", pady=(0, 16))
        theme.make_stat_card(stats, "Total Attempts", data["total_attempts"],
                              accent=theme.ACCENT).pack(side="left", padx=(0, 10), fill="x", expand=True)
        theme.make_stat_card(stats, "Resolved", data["resolved_attempts"],
                              accent=theme.SUCCESS).pack(side="left", padx=10, fill="x", expand=True)
        theme.make_stat_card(stats, "Resolution Rate", f"{data['resolution_rate']}%",
                              accent=theme.PURPLE).pack(side="left", padx=(10, 0), fill="x", expand=True)

        tk.Label(self.content, text=f"Most common mistake: {data['most_common_error'] or 'None yet'}",
                 font=theme.F_BODY_BOLD, fg=theme.WARNING, bg=theme.BG).pack(anchor="w", pady=(4, 8))

        trend = get_improvement_trend(user["user_id"])
        if trend["has_enough_data"]:
            trend_text = (f"{trend['trend']}  —  earlier {trend['older_resolution_rate']}% "
                           f"\u2192 recent {trend['recent_resolution_rate']}%")
            kind = _TREND_KIND.get(trend["trend"], "info")
        else:
            trend_text = trend["message"]
            kind = "info"
        theme.status_pill(self.content, trend_text, kind=kind).pack(anchor="w", pady=(0, 18))

        tk.Label(self.content, text="RECENT ACTIVITY", font=theme.F_SMALL,
                 fg=theme.ACCENT, bg=theme.BG).pack(anchor="w")

        activity_wrap = tk.Frame(self.content, bg=theme.BG)
        activity_wrap.pack(fill="both", expand=True, pady=(8, 10))

        if not data["recent_activity"]:
            tk.Label(activity_wrap, text="No activity yet - try checking some code!",
                     font=theme.F_BODY, fg=theme.TEXT_MUTED, bg=theme.BG).pack(anchor="w", pady=5)

        for row in data["recent_activity"]:
            resolved = row["resolved"]
            status_text = "Resolved" if resolved else "Open"
            status_color = theme.SUCCESS if resolved else theme.DANGER
            line = tk.Frame(activity_wrap, bg=theme.SURFACE, highlightthickness=1,
                             highlightbackground=theme.BORDER)
            line.pack(fill="x", pady=3)
            tk.Label(line, text=("\u25CF" if resolved else "\u25CB"), font=theme.F_BODY,
                     fg=status_color, bg=theme.SURFACE).pack(side="left", padx=(12, 6), pady=8)
            tk.Label(line, text=row.get("error_name") or "No error", font=theme.F_BODY,
                     fg=theme.TEXT, bg=theme.SURFACE).pack(side="left")
            tk.Label(line, text=str(row["occurred_at"]), font=theme.F_SMALL,
                     fg=theme.TEXT_DIM, bg=theme.SURFACE).pack(side="right", padx=12)
            tk.Label(line, text=status_text, font=theme.F_SMALL,
                     fg=status_color, bg=theme.SURFACE).pack(side="right", padx=12)
