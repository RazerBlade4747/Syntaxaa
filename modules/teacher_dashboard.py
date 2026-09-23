"""
teacher_dashboard.py
----------------------
Teacher-facing screen: generate/share a class code, view connected
students, and drill into an individual student's Bug DNA / progress.

VIVA NOTE on teacher-student connection:
Each teacher account can generate a class_code (just their user_id +
a random number). A student enters that code once; this creates one
row in class_connections. A teacher never sees ANY student unless
that student has entered their code - this is the "optional, not
automatic surveillance" requirement from the spec.

UI ENHANCED with modules/theme.py. All database calls and the
teacher/student connection logic are unchanged.
"""

import tkinter as tk
from tkinter import messagebox

import database
from modules import bug_dna, progress_analysis
from modules import theme


class TeacherDashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller
        self.class_code = None

        self.header_wrap = theme.build_header(
            self, "Teacher Dashboard", on_logout=self.logout)
        self.welcome_label = self.header_wrap.title_label

        code_row = tk.Frame(self, bg=theme.BG)
        code_row.pack(fill="x", padx=30, pady=(0, 10))
        theme.make_button(code_row, "Generate Class Code", command=self.generate_code,
                           style="success", icon="\U0001F3AB").pack(side="left")
        self.code_label = tk.Label(code_row, text="", font=theme.F_BODY_BOLD,
                                    fg=theme.WARNING, bg=theme.BG)
        self.code_label.pack(side="left", padx=15)

        tk.Label(self, text="CONNECTED STUDENTS", font=theme.F_SMALL,
                 fg=theme.TEXT_MUTED, bg=theme.BG).pack(anchor="w", padx=30, pady=(4, 6))

        body = tk.Frame(self, bg=theme.BG)
        body.pack(fill="both", expand=True, padx=30, pady=(0, 16))

        list_wrap = tk.Frame(body, bg=theme.BORDER)
        list_wrap.pack(side="left", fill="y", padx=(0, 16))
        self.listbox = tk.Listbox(list_wrap, width=25, font=theme.F_BODY, bg=theme.SURFACE,
                                   fg=theme.TEXT, relief="flat", highlightthickness=0,
                                   selectbackground=theme.ACCENT_SOFT, selectforeground=theme.ACCENT,
                                   activestyle="none", bd=0)
        self.listbox.pack(side="left", fill="y", padx=1, pady=1)
        self.listbox.bind("<<ListboxSelect>>", self.show_student_detail)

        detail_wrap = tk.Frame(body, bg=theme.BORDER)
        detail_wrap.pack(side="left", fill="both", expand=True)
        self.detail_box = tk.Text(detail_wrap, font=theme.F_BODY, bg=theme.SURFACE,
                                   fg=theme.TEXT, relief="flat", wrap="word",
                                   padx=14, pady=12, borderwidth=0)
        self.detail_box.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        self.detail_box.config(state="disabled")

        self.students_cache = []

    def on_show(self):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Teacher Dashboard \u2014 {user['username']}")
            self.refresh_students()

    def generate_code(self):
        user = self.controller.current_user
        code = database.generate_class_code(user["user_id"])
        self.class_code = code
        self.code_label.config(text=f"Share this code with students: {code}")

    def refresh_students(self):
        user = self.controller.current_user
        if not user:
            return
        self.students_cache = database.get_connected_students(user["user_id"])
        self.listbox.delete(0, tk.END)
        for s in self.students_cache:
            self.listbox.insert(tk.END, s["username"])

    def show_student_detail(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        student = self.students_cache[selection[0]]
        dna = bug_dna.generate_bug_dna(student["user_id"])
        progress = progress_analysis.analyze_progress(student["user_id"])

        trend = progress_analysis.get_improvement_trend(student["user_id"])

        avg_time = None
        if dna["categories"]:
            times = [c["avg_debug_time_seconds"] for c in dna["categories"] if c["avg_debug_time_seconds"]]
            avg_time = round(sum(times) / len(times)) if times else 0

        lines = [f"Student: {student['username']}", "-" * 40, ""]
        lines.append(f"Attempted questions: {progress['total_attempts']}")
        lines.append(f"Resolved: {progress['resolved_attempts']} ({progress['resolution_rate']}%)")
        lines.append(f"Average time spent debugging: {avg_time if avg_time is not None else 'No data yet'} seconds")
        lines.append("")
        if trend["has_enough_data"]:
            lines.append(f"Improvement trend: {trend['trend']}")
            lines.append(f"  Earlier attempts resolved: {trend['older_resolution_rate']}%")
            lines.append(f"  Recent attempts resolved: {trend['recent_resolution_rate']}%")
        else:
            lines.append(f"Improvement trend: {trend['message']}")
        lines.append("")
        lines.append(f"Most common mistake: {progress['most_common_error'] or 'None yet'}")
        lines.append("")
        lines.append("Weak concepts:")
        if dna["message"]:
            lines.append("  " + dna["message"])
        else:
            for concept in dna["weak_concepts"]:
                lines.append(f"  \u2022 {concept}")
        lines.append("")
        lines.append("Category breakdown:")
        for cat in dna["categories"]:
            lines.append(f"  {cat['concept']}: {cat['frequency']} times, ~{cat['avg_debug_time_seconds']}s avg")

        self.detail_box.config(state="normal")
        self.detail_box.delete("1.0", tk.END)
        self.detail_box.insert(tk.END, "\n".join(lines))
        self.detail_box.config(state="disabled")

    def logout(self):
        self.controller.logout()


class JoinClassFrame(tk.Frame):
    """Student-facing screen to join a teacher's class using a class code."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        theme.build_header(self, "Join a Teacher's Class",
                            on_back=lambda: controller.show_frame("StudentDashboardFrame"))

        tk.Label(self, text="This is optional. Only enter a code if your teacher has given you one.",
                 font=theme.F_BODY, fg=theme.TEXT_MUTED, bg=theme.BG).pack(anchor="w", padx=30, pady=(0, 14))

        card_outer = theme.make_card(self, padx=28, pady=24)
        card_outer.pack(padx=30, anchor="w")
        card = card_outer.inner

        theme.field_label(card, "TEACHER'S USERNAME").pack(fill="x", pady=(0, 4))
        teacher_wrap, self.teacher_entry = theme.make_entry(card)
        teacher_wrap.pack(fill="x", pady=(0, 14))

        theme.field_label(card, "CLASS CODE").pack(fill="x", pady=(0, 4))
        code_wrap, self.code_entry = theme.make_entry(card)
        code_wrap.pack(fill="x", pady=(0, 18))

        theme.make_button(card, "Connect", command=self.connect, style="primary",
                           icon="\U0001F91D").pack(fill="x")

    def connect(self):
        teacher_username = self.teacher_entry.get().strip()
        code = self.code_entry.get().strip()
        if not teacher_username or not code:
            messagebox.showwarning("Join Class", "Please enter both the teacher's username and the class code.")
            return

        teacher_id = database.find_user_id_by_username(teacher_username)
        if teacher_id is None:
            messagebox.showerror("Join Class", "That teacher username was not found.")
            return

        user = self.controller.current_user
        success, message = database.connect_student_to_class(user["user_id"], teacher_id, code)
        if success:
            messagebox.showinfo("Join Class", message)
        else:
            messagebox.showerror("Join Class", message)
