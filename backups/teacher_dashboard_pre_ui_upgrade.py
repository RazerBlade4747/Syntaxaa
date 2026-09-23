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
"""

import tkinter as tk
from tkinter import messagebox

import database
from modules import bug_dna, progress_analysis


class TeacherDashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller
        self.class_code = None

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        self.welcome_label = tk.Label(header, text="Teacher Dashboard", font=("Segoe UI", 20, "bold"),
                                       fg="#00e5ff", bg="#0d1117")
        self.welcome_label.pack(side="left")
        tk.Button(header, text="Logout", command=self.logout, bg="#161b22", fg="#c9d1d9",
                  relief="flat", padx=12, pady=6).pack(side="right")

        code_row = tk.Frame(self, bg="#0d1117")
        code_row.pack(fill="x", padx=30, pady=10)
        tk.Button(code_row, text="Generate Class Code", command=self.generate_code, bg="#238636", fg="white",
                  relief="flat", padx=14, pady=8).pack(side="left")
        self.code_label = tk.Label(code_row, text="", font=("Segoe UI", 14, "bold"),
                                    fg="#f0883e", bg="#0d1117")
        self.code_label.pack(side="left", padx=15)

        tk.Label(self, text="Connected Students", font=("Segoe UI", 13, "bold"),
                 fg="#c9d1d9", bg="#0d1117").pack(anchor="w", padx=30, pady=(10, 0))

        body = tk.Frame(self, bg="#0d1117")
        body.pack(fill="both", expand=True, padx=30, pady=10)

        self.listbox = tk.Listbox(body, width=25, font=("Segoe UI", 11), bg="#161b22",
                                   fg="#e6edf3", relief="flat", highlightthickness=0)
        self.listbox.pack(side="left", fill="y", padx=(0, 20))
        self.listbox.bind("<<ListboxSelect>>", self.show_student_detail)

        self.detail_box = tk.Text(body, font=("Segoe UI", 11), bg="#161b22", fg="#c9d1d9",
                                   relief="flat", wrap="word")
        self.detail_box.pack(side="left", fill="both", expand=True)
        self.detail_box.config(state="disabled")

        self.students_cache = []

    def on_show(self):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Teacher Dashboard - {user['username']}")
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
            lines.append(f"  Recent attempts resolved:  {trend['recent_resolution_rate']}%")
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
                lines.append(f"  • {concept}")
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
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(header, text="Join a Teacher's Class", font=("Segoe UI", 20, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(side="left")
        tk.Button(header, text="Back to Dashboard", command=lambda: controller.show_frame("StudentDashboardFrame"),
                  bg="#161b22", fg="#c9d1d9", relief="flat", padx=12, pady=6).pack(side="right")

        tk.Label(self, text="This is optional. Only enter a code if your teacher has given you one.",
                 font=("Segoe UI", 11), fg="#8b949e", bg="#0d1117").pack(anchor="w", padx=30, pady=(10, 5))

        form = tk.Frame(self, bg="#0d1117")
        form.pack(padx=30, pady=10, anchor="w")
        tk.Label(form, text="Teacher's username:", fg="#c9d1d9", bg="#0d1117").grid(row=0, column=0, sticky="w", pady=5)
        self.teacher_entry = tk.Entry(form, bg="#161b22", fg="white", insertbackground="white")
        self.teacher_entry.grid(row=0, column=1, padx=10)

        tk.Label(form, text="Class code:", fg="#c9d1d9", bg="#0d1117").grid(row=1, column=0, sticky="w", pady=5)
        self.code_entry = tk.Entry(form, bg="#161b22", fg="white", insertbackground="white")
        self.code_entry.grid(row=1, column=1, padx=10)

        tk.Button(self, text="Connect", command=self.connect, bg="#00e5ff", fg="#0d1117",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=16, pady=8).pack(padx=30, pady=15, anchor="w")

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
