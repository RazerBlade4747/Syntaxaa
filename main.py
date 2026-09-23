
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

import threading
import tkinter as tk
from tkinter import messagebox

import database
from modules import theme
from modules import sync_manager
from modules.authentication import LoginFrame, SignupFrame
from modules.dashboard import StudentDashboardFrame
from modules.error_detection import ErrorDetectionFrame
from modules.error_encyclopedia import EncyclopediaFrame
from modules.bug_dna import BugDNAFrame
from modules.progress_analysis import ProgressFrame
from modules.teacher_dashboard import TeacherDashboardFrame, JoinClassFrame


class SyntaxaaApp(tk.Tk):
    @property
    def offline_mode(self):
      return database.is_offline()

    def __init__(self):
        super().__init__()
        self.title("SYNTAXAA - Offline-First Intelligent Debugging & Analysis System")
        self.geometry("1000x680")
        theme.apply_app_defaults(self)
        self.minsize(900, 600)
        self._center_on_screen(1000, 680)

        self.current_user = None
        sync_manager.ensure_local_storage()

        # Build Status & Control Top Bar
        self._build_top_bar()

        container = tk.Frame(self, bg=theme.BG)
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

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_frame("LoginFrame")

        # Start periodic background connectivity check
        self.after(5000, self.auto_check_connection)

    def _build_top_bar(self):
        """Creates top bar for status indicators and manual controls."""
        self.top_bar = tk.Frame(self, bg="#161b22", height=38)
        self.top_bar.pack(side="top", fill="x")

        self.status_label = tk.Label(
            self.top_bar,
            text="",
            bg="#161b22",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side="left", padx=15, pady=5)

        self.toggle_btn = tk.Button(
            self.top_bar,
            text="Force CSV Offline Mode",
            command=self.toggle_offline_mode,
            bg="#21262d",
            fg="white",
            relief="flat",
            padx=8
        )
        self.toggle_btn.pack(side="right", padx=10, pady=5)

        self.sync_btn = tk.Button(
            self.top_bar,
            text="Sync CSV -> MySQL",
            command=self.trigger_manual_sync,
            bg="#238636",
            fg="white",
            relief="flat",
            padx=8
        )
        self.sync_btn.pack(side="right", padx=5, pady=5)

        self.update_status_ui()

    def update_status_ui(self):
        """Refreshes status label and toggle button texts."""
        if database.FORCE_OFFLINE:
            self.status_label.config(text="● Mode: MANUAL OFFLINE (CSV Storage)", fg="#f2cc60")
            self.toggle_btn.config(text="Switch to Online Mode")
        elif database.get_connection() is None:
            self.status_label.config(text="● Mode: AUTO OFFLINE (MySQL Unreachable)", fg="#e5534b")
            self.toggle_btn.config(text="Force CSV Offline Mode")
        else:
            self.status_label.config(text="● Mode: ONLINE (MySQL Connected)", fg="#57ab5a")
            self.toggle_btn.config(text="Force CSV Offline Mode")

    def toggle_offline_mode(self):
        """Toggles manual offline switch."""
        database.FORCE_OFFLINE = not database.FORCE_OFFLINE
        self.update_status_ui()

        if database.FORCE_OFFLINE:
            messagebox.showinfo("Offline Mode Enabled", "Switched to local CSV storage mode.")
        else:
            if database.get_connection() is None:
                messagebox.showwarning("Connection Failed", "MySQL is unreachable. System remains in offline mode.")
            else:
                messagebox.showinfo("Online Mode", "Reconnected to MySQL database. Triggering sync...")
                self.trigger_manual_sync()

    def trigger_manual_sync(self):
        """Runs the CSV-to-MySQL sync process in a background thread."""
        def run_sync():
            success, msg = sync_manager.sync_local_data_to_mysql()
            if success:
                messagebox.showinfo("Sync Complete", msg)
            else:
                messagebox.showwarning("Sync Status", msg)
            self.update_status_ui()

        threading.Thread(target=run_sync, daemon=True).start()

    def auto_check_connection(self):
        """Periodically polls connection and triggers updates."""
        self.update_status_ui()
        # Re-check every 10 seconds
        self.after(10000, self.auto_check_connection)

    def _center_on_screen(self, width, height):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame is None:
            messagebox.showerror("Navigation Error", f"Screen '{name}' does not exist.")
            return
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def login_success(self, user):
        self.current_user = user
        if user["user_type"] == "teacher":
            self.show_frame("TeacherDashboardFrame")
        else:
            self.show_frame("StudentDashboardFrame")

    def logout(self):
        self.current_user = None
        self.show_frame("LoginFrame")

    def on_close(self):
        self.destroy()




app = FastAPI(title="Syntaxaa Shared API")

# Database configuration from Environment Variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "defaultdb")
DB_PORT = int(os.getenv("DB_PORT", 3306))


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT
    )


@app.on_event("startup")
def init_db_tables():
    """Automatically creates the required MySQL tables when the backend starts up on Render."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table automatically if it doesn't exist yet
        create_table_query = """
        CREATE TABLE IF NOT EXISTS teacher_codes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id INT NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"⚠️ Could not initialize database table: {e}")


class TeacherCodeSchema(BaseModel):
    teacher_id: int
    code: str


@app.get("/")
def health_check():
    return {"status": "online", "system": "Syntaxaa Central Server"}


@app.post("/api/teacher-codes/create")
def create_teacher_code(data: TeacherCodeSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teacher_codes (teacher_id, code) VALUES (%s, %s)",
            (data.teacher_id, data.code)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Code registered globally"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Teacher code already exists")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/api/teacher-codes/verify/{code}")
def verify_teacher_code(code: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher_codes WHERE code = %s", (code,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Invalid teacher code")
        
        return {"status": "valid", "data": result}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


if __name__ == "__main__":
    app = SyntaxaaApp()
    app.mainloop()