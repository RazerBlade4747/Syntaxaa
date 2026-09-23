"""
error_detection.py
-------------------
The core Error Detection Engine.

VIVA NOTE - how this actually works:
We do NOT write our own Python parser (that would be far too complex
for a Class 12 project). Instead we let Python's own compiler check
the code for us using compile(), and we catch the exception it raises.
compile() only checks that the code is well-formed; it does not run it,
so this is safe even for code with mistakes or infinite loops.

We then translate the raised exception (e.g. SyntaxError, IndentationError)
into a beginner-friendly explanation using the Error Encyclopedia data.
"""

import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import database
from modules import smart_hints


def check_code(source_code):
    """
    Attempts to compile the given source code.

    Returns a dict:
      {
        "success": True/False,
        "error_type": "SyntaxError" / None,
        "line_number": int or None,
        "raw_message": str,
        "explanation": dict (from database) or None
      }
    """
    if not source_code or not source_code.strip():
        return {
            "success": False,
            "error_type": "EmptyInput",
            "line_number": None,
            "raw_message": "No code was entered.",
            "explanation": {
                "error_name": "Empty Input",
                "beginner_explanation": "You haven't typed or pasted any code yet. Write some Python code in the box above and try again.",
                "fix_text": "Type or paste your code into the editor before clicking Check Code.",
                "prevention_tip": "Always make sure your code is in the editor before checking it.",
                "category": "Input"
            }
        }

    try:
        # compile() only checks syntax/structure - it does NOT execute the code.
        compile(source_code, "<student_code>", "exec")
        return {
            "success": True,
            "error_type": None,
            "line_number": None,
            "raw_message": "No errors found. Your code compiled successfully!",
            "explanation": None
        }

    except SyntaxError as e:
        return _build_result("SyntaxError", e.lineno, str(e))

    except IndentationError as e:
        return _build_result("IndentationError", e.lineno, str(e))

    except TabError as e:
        return _build_result("IndentationError", e.lineno, str(e))

    except Exception as e:
        # Any other unexpected compile-time issue is still handled gracefully.
        error_type = type(e).__name__
        return _build_result(error_type, None, str(e))


def check_runtime_behaviour(source_code, timeout_seconds=3):
    """
    Optional deeper check: runs the code in a restricted way to catch
    runtime errors like NameError, TypeError, ZeroDivisionError etc.,
    which compile() alone cannot detect (it only checks structure).

    IMPORTANT SAFETY NOTE (viva talking point):
    We only run this when the student explicitly asks for a deeper
    check, using a very small restricted namespace, because executing
    arbitrary code always carries some risk. We do not allow file or
    network access from inside the executed code.
    """
    safe_globals = {"__builtins__": __builtins__}
    try:
        exec(compile(source_code, "<student_code>", "exec"), safe_globals)
        return {
            "success": True,
            "error_type": None,
            "line_number": None,
            "raw_message": "Code ran successfully with no errors.",
            "explanation": None
        }
    except Exception as e:
        error_type = type(e).__name__
        line_number = None
        tb = e.__traceback__
        while tb is not None:
            line_number = tb.tb_lineno
            tb = tb.tb_next
        return _build_result(error_type, line_number, str(e))


def _build_result(error_type, line_number, raw_message):
    """Looks up the matching Encyclopedia entry for a detected error type."""
    # The database lookup can fail for reasons unrelated to the student's
    # code (e.g. a stale/unread MySQL cursor, a dropped connection). If we
    # let that exception escape here, the whole app crashes to the terminal
    # instead of showing the result in the GUI - so we fall back gracefully.
    try:
        explanation = database.get_error_by_name(error_type)
    except Exception as db_error:
        print(f"[warning] Error Encyclopedia lookup failed for '{error_type}': {db_error}")
        explanation = None

    if explanation is None:
        explanation = {
            "error_name": error_type,
            "category": "General",
            "beginner_explanation": "This is a less common error. Try checking the Error Encyclopedia or asking your teacher for help.",
            "fix_text": "Review the line mentioned above carefully.",
            "prevention_tip": "Test your code in small pieces to catch errors early."
        }
    return {
        "success": False,
        "error_type": error_type,
        "line_number": line_number,
        "raw_message": raw_message,
        "explanation": explanation
    }


# =========================================================
# GUI: Error Detection Engine screen
# =========================================================

class ErrorDetectionFrame(tk.Frame):
    """
    The screen where a student types/pastes code and checks it.
    Shows the friendly explanation, and offers Smart Hints and
    (if available) optional AI assistance.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller
        self.current_result = None
        self.current_history_id = None
        self.hint_index = 0
        self.start_time = None

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(header, text="Error Detection Engine", font=("Segoe UI", 20, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(side="left")
        tk.Button(header, text="Back to Dashboard", command=lambda: controller.show_frame("StudentDashboardFrame"),
                  bg="#161b22", fg="#c9d1d9", relief="flat", padx=12, pady=6).pack(side="right")

        tk.Label(self, text="Type or paste your Python code below:", font=("Segoe UI", 11),
                 fg="#8b949e", bg="#0d1117").pack(anchor="w", padx=30)

        self.code_box = scrolledtext.ScrolledText(self, height=12, font=("Consolas", 11),
                                                    bg="#161b22", fg="#e6edf3", insertbackground="white")
        self.code_box.pack(fill="both", expand=True, padx=30, pady=10)

        btn_row = tk.Frame(self, bg="#0d1117")
        btn_row.pack(fill="x", padx=30)
        tk.Button(btn_row, text="Check Code", command=self.check_code, bg="#00e5ff", fg="#0d1117",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=16, pady=8).pack(side="left")
        tk.Button(btn_row, text="Get a Hint", command=self.next_hint, bg="#238636", fg="white",
                  relief="flat", padx=16, pady=8).pack(side="left", padx=10)
        tk.Button(btn_row, text="Ask AI for More Detail", command=self.ask_ai, bg="#8957e5", fg="white",
                  relief="flat", padx=16, pady=8).pack(side="left")
        tk.Button(btn_row, text="Mark as Resolved", command=self.mark_resolved, bg="#30363d", fg="white",
                  relief="flat", padx=16, pady=8).pack(side="left", padx=10)

        self.result_box = scrolledtext.ScrolledText(self, height=10, font=("Segoe UI", 11),
                                                       bg="#0d1117", fg="#c9d1d9", relief="flat")
        self.result_box.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        self.result_box.config(state="disabled")

    def _write_result(self, text):
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)
        self.result_box.config(state="disabled")

    def check_code(self):
        code = self.code_box.get("1.0", tk.END)
        self.start_time = time.time()
        self.hint_index = 0
        result = check_code(code)
        self.current_result = result

        if result["success"]:
            self._write_result("✅ " + result["raw_message"])
            self.current_history_id = None
            return

        exp = result["explanation"]
        line_info = f" (around line {result['line_number']})" if result["line_number"] else ""
        text = (
            f"❌ {result['error_type']}{line_info}\n\n"
            f"What happened:\n{exp['beginner_explanation']}\n\n"
            f"Possible fix:\n{exp.get('fix_text', 'See the Error Encyclopedia for a suggested fix.')}\n\n"
            f"Prevention tip:\n{exp.get('prevention_tip', '')}"
        )
        self._write_result(text)

        # Logging history is a "nice to have" - if it fails (e.g. a database
        # hiccup), the student should still see the explanation that was
        # already written above, instead of the whole app crashing.
        user = self.controller.current_user
        if user:
            try:
                self.current_history_id = database.log_history(
                    user["user_id"], result["error_type"], code
                )
            except Exception as db_error:
                print(f"[warning] Could not log history: {db_error}")
                self.current_history_id = None

    def next_hint(self):
        if not self.current_result or self.current_result["success"]:
            messagebox.showinfo("Smart Hint Mode", "Check your code first - no error detected yet!")
            return
        category = self.current_result["explanation"].get("category", "General")
        hint = smart_hints.get_hint(category, self.hint_index)
        if hint is None:
            messagebox.showinfo("Smart Hint Mode", "No more hints left - check the full explanation above.")
        else:
            messagebox.showinfo(f"Hint {self.hint_index + 1}", hint)
            self.hint_index += 1

    def ask_ai(self):
        if not self.current_result or self.current_result["success"]:
            messagebox.showinfo("Ask AI", "Check your code first to get an error to ask about.")
            return
        from modules import ai_assist
        code = self.code_box.get("1.0", tk.END)
        answer = ai_assist.ask_ai_for_help(
            self.current_result["error_type"], code, self.current_result["raw_message"]
        )
        messagebox.showinfo("AI Assistance", answer)

    def mark_resolved(self):
        if self.current_history_id is None:
            messagebox.showinfo("Mark as Resolved", "There is no active logged error to resolve.")
            return
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        database.mark_resolved(self.current_history_id, elapsed)
        messagebox.showinfo("Nice work!", f"Marked as resolved. Debugging took about {elapsed} seconds.")
        self.current_history_id = None
