"""
main.py
-------
Entry point for SYNTAXAA. Sets up the main window and switches
between screens (Frames) without opening multiple windows.

VIVA NOTE: This uses the standard Tkinter "stacked frames" pattern -
every screen is a Frame placed in the same location; show_frame()
just raises the one we want to the top. This keeps navigation simple
and centralised in one controller class (SyntaxaaApp) instead of
being scattered across every screen.
"""

import tkinter as tk
from tkinter import messagebox

import database
from modules.authentication import LoginFrame, SignupFrame
from modules.dashboard import StudentDashboardFrame
from modules.error_detection import ErrorDetectionFrame
from modules.error_encyclopedia import EncyclopediaFrame
from modules.bug_dna import BugDNAFrame
from modules.progress_analysis import ProgressFrame
from modules.teacher_dashboard import TeacherDashboardFrame, JoinClassFrame


class SyntaxaaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SYNTAXAA - Offline-First Intelligent Debugging & Analysis System")
        self.geometry("1000x650")
        self.configure(bg="#0d1117")
        self.minsize(900, 600)

        self.current_user = None
        # If MySQL cannot be reached at all, we still let the user browse
        # the Encyclopedia (via the JSON fallback) but authentication and
        # history logging will not work until the database is available.
        self.offline_mode = database.get_connection() is None

        container = tk.Frame(self, bg="#0d1117")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        frame_classes = [
            LoginFrame, SignupFrame, StudentDashboardFrame,
            ErrorDetectionFrame, EncyclopediaFrame, BugDNAFrame,
            ProgressFrame, TeacherDashboardFrame, JoinClassFrame
        ]

        for FrameClass in frame_classes:
            name = FrameClass.__name__
            frame = FrameClass(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Handle window close gracefully instead of crashing on any
        # in-progress operation.
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        """Raises the requested frame to the top and calls its on_show() if present."""
        frame = self.frames.get(name)
        if frame is None:
            messagebox.showerror("Navigation Error", f"Screen '{name}' does not exist.")
            return
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def login_success(self, user):
        """Called by LoginFrame after a successful login. Routes by user type."""
        self.current_user = user
        if user["user_type"] == "teacher":
            self.show_frame("TeacherDashboardFrame")
        else:
            self.show_frame("StudentDashboardFrame")

    def logout(self):
        self.current_user = None
        self.show_frame("LoginFrame")

    def on_close(self):
        # A clean shutdown point - useful if we later need to close
        # open database connections or save state before exiting.
        self.destroy()


if __name__ == "__main__":
    app = SyntaxaaApp()
    app.mainloop()
