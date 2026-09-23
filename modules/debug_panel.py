import tkinter as tk
import threading
import database
from modules import error_encyclopedia
from modules.ai_debugger import explain_error_with_gemini, is_network_available


class DebugPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        # Dark Theme Styling
        self.BG_DARK = "#0d1117"
        self.BG_CONTENT = "#161b22"
        self.TAB_ACTIVE_BG = "#1f2937"
        self.TAB_INACTIVE_BG = "#0d1117"
        self.TEXT_COLOR = "#c9d1d9"
        self.ERROR_RED = "#f85149"
        self.PLACEHOLDER_TEXT = "Ask a follow-up question..."

        # State Variables
        self.current_code = ""
        self.current_error = ""
        self.current_error_type = ""
        self.cached_ai_response = ""
        
        # Default active tab (preserves state across execution)
        self.active_tab = "Problems"  
        self.ai_triggered_for_current_run = False

        # --- Top Tab Bar ---
        self.nav_bar = tk.Frame(self, bg=self.BG_DARK, height=35)
        self.nav_bar.pack(side="top", fill="x", padx=5, pady=(2, 0))

        self.tabs = {}
        tab_names = ["Output", "Problems", "AI Debugger"]

        for name in tab_names:
            btn = tk.Button(
                self.nav_bar,
                text=name,
                font=("Segoe UI", 10, "normal"),
                fg=self.TEXT_COLOR,
                bg=self.TAB_INACTIVE_BG,
                activebackground=self.TAB_ACTIVE_BG,
                activeforeground="white",
                bd=0,
                padx=14,
                pady=4,
                relief="flat",
                cursor="hand2",
                command=lambda n=name: self.select_tab(n)
            )
            btn.pack(side="left", padx=2)
            self.tabs[name] = btn

        # --- Main Display Container ---
        self.content_area = tk.Frame(self, bg=self.BG_CONTENT, bd=1, relief="solid")
        self.content_area.pack(fill="both", expand=True, padx=5, pady=(2, 5))

        # --- Follow-Up Bar ---
        self.followup_frame = tk.Frame(self.content_area, bg="#0d1117", bd=1, relief="solid")

        self.followup_entry = tk.Entry(
            self.followup_frame,
            bg="#161b22",
            fg="#8b949e",
            insertbackground="white",
            font=("Segoe UI", 10),
            bd=1,
            relief="solid"
        )
        self.followup_entry.insert(0, self.PLACEHOLDER_TEXT)
        self.followup_entry.pack(side="left", fill="x", expand=True, padx=(8, 5), pady=6)

        # Placeholder event bindings
        self.followup_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.followup_entry.bind("<FocusOut>", self._on_entry_focus_out)
        self.followup_entry.bind("<Return>", lambda e: self.send_followup())

        # Simple Up-Arrow Send Button
        self.followup_btn = tk.Button(
            self.followup_frame,
            text="▲",
            font=("Segoe UI", 10, "bold"),
            bg="#238636",
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=2,
            cursor="hand2",
            command=self.send_followup
        )
        self.followup_btn.pack(side="right", padx=(0, 8), pady=6)

        # --- Display Area (Scrollbar + Read-Only Text Output) ---
        self.display_frame = tk.Frame(self.content_area, bg="#011627")
        self.display_frame.pack(side="top", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.display_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.text_display = tk.Text(
            self.display_frame,
            bg="#011627",
            fg="#d6deeb",
            font=("Consolas", 10),
            wrap="word",
            bd=0,
            padx=12,
            pady=12,
            yscrollcommand=self.scrollbar.set,
            state="disabled",
            cursor="arrow"
        )
        self.text_display.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text_display.yview)

        # Initial view stays on Problems/Output
        self.select_tab(self.active_tab)

    # --- Placeholder Handlers ---
    def _on_entry_focus_in(self, event):
        if self.followup_entry.get() == self.PLACEHOLDER_TEXT:
            self.followup_entry.delete(0, tk.END)
            self.followup_entry.config(fg="#e6edf3")

    def _on_entry_focus_out(self, event):
        if not self.followup_entry.get().strip():
            self.followup_entry.delete(0, tk.END)
            self.followup_entry.insert(0, self.PLACEHOLDER_TEXT)
            self.followup_entry.config(fg="#8b949e")

    def _set_display_text(self, content: str):
        """Writes content into read-only display safely."""
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert(tk.END, content)
        self.text_display.config(state="disabled")

    def _refresh_tab_labels(self):
        """Updates tab button styles and error badges."""
        for name, btn in self.tabs.items():
            is_active = (name == self.active_tab)
            bg = self.TAB_ACTIVE_BG if is_active else self.TAB_INACTIVE_BG
            font = ("Segoe UI", 10, "bold") if is_active else ("Segoe UI", 10, "normal")

            if name == "Problems":
                if self.current_error:
                    btn.config(text="Problems 🔴 1", fg=self.ERROR_RED, bg=bg, font=font)
                else:
                    btn.config(text="Problems", fg="#ffffff" if is_active else self.TEXT_COLOR, bg=bg, font=font)
            else:
                btn.config(text=name, fg="#ffffff" if is_active else self.TEXT_COLOR, bg=bg, font=font)

    def select_tab(self, selected_name):
        """Switches display without changing tab selection on execution."""
        self.active_tab = selected_name
        self._refresh_tab_labels()

        self.followup_frame.pack_forget()

        if selected_name == "AI Debugger":
            self.followup_frame.pack(side="bottom", fill="x", padx=5, pady=(0, 5))

            if not is_network_available():
                msg = (
                    "═══════════════════════════════════════════════════════════════════════\n"
                    " 🔴 AI DEBUGGER: NETWORK NOT AVAILABLE (OFFLINE MODE)\n"
                    "═══════════════════════════════════════════════════════════════════════\n\n"
                    "• The application is running in local CSV mode or cannot reach Gemini.\n"
                    "• AI analysis is temporarily paused.\n\n"
                    "• Switch to the 'Problems' tab to view local static analysis rules."
                )
                self._set_display_text(msg)
            elif self.cached_ai_response:
                self._set_display_text(self.cached_ai_response)
            elif (self.current_code or self.current_error) and not self.ai_triggered_for_current_run:
                # Triggers AI Debugger ONLY on explicit user click of this tab
                self.run_ai_analysis()
            elif not self.current_code and not self.current_error:
                self._set_display_text("No code executed yet. Click 'Analyze & Debug Code' above.")

        elif selected_name == "Output":
            if self.current_code and not self.current_error:
                self._set_display_text("[Execution Succeeded]\nProgram finished with code 0.")
            elif self.current_error:
                self._set_display_text(f"[Execution Failed]\n{self.current_error}")
            else:
                self._set_display_text("Console output will appear here after execution.")

        elif selected_name == "Problems":
            if self.current_error:
                # Direct access to modules.error_encyclopedia
                encyclopedia_msg = ""
                if hasattr(error_encyclopedia, "get_error_info"):
                    encyclopedia_msg = error_encyclopedia.get_error_info(self.current_error_type)
                else:
                    encyclopedia_msg = database.get_error_details(self.current_error_type)

                formatted_output = (
                    f"════════════════════════════════════════════════\n"
                    f" 🛠️ LOCAL ERROR ENCYCLOPEDIA ENTRY\n"
                    f"════════════════════════════════════════════════\n\n"
                    f"❌ Execution Traceback:\n{self.current_error}\n\n"
                    f"{encyclopedia_msg}"
                )
                self._set_display_text(formatted_output)
            else:
                self._set_display_text("✔ No problems detected in your code.")

    def run_ai_analysis(self):
        """Fetches AI explanation in background thread and updates cache."""
        self.ai_triggered_for_current_run = True
        self._set_display_text("Connecting to Gemini AI...\n\n")

        def _fetch():
            res = explain_error_with_gemini(self.current_code, self.current_error)
            self.cached_ai_response = res
            self.after(0, lambda: self._display_cached_response())

        threading.Thread(target=_fetch, daemon=True).start()

    def _display_cached_response(self):
        if self.active_tab == "AI Debugger":
            self._set_display_text(self.cached_ai_response)

    def send_followup(self):
        """Sends follow-up query preserving conversation context."""
        question = self.followup_entry.get().strip()
        if not question or question == self.PLACEHOLDER_TEXT or not is_network_available():
            return

        self.followup_entry.delete(0, tk.END)
        self.followup_entry.insert(0, self.PLACEHOLDER_TEXT)
        self.followup_entry.config(fg="#8b949e")
        self.master.focus_set()

        self.cached_ai_response += f"\n\n════════════════════════════════════════════════\n❓ Follow-up: {question}\n════════════════════════════════════════════════\n\nThinking..."
        self._display_cached_response()

        def _fetch_followup():
            prompt_context = f"Code:\n{self.current_code}\n\nPrevious Analysis:\n{self.cached_ai_response}\n\nStudent Follow-Up Question:\n{question}"
            res = explain_error_with_gemini(self.current_code, prompt_context)
            
            self.cached_ai_response = self.cached_ai_response.replace("Thinking...", res)
            self.after(0, lambda: self._display_cached_response())

        threading.Thread(target=_fetch_followup, daemon=True).start()

    def update_debug_data(self, code, error, error_type=""):
        """Updates data while PRESERVING the currently selected tab."""
        self.current_code = code
        self.current_error = error
        self.current_error_type = error_type
        self.cached_ai_response = ""
        self.ai_triggered_for_current_run = False

        # Refreshes the currently active tab view without forcing switch to AI Debugger
        self.select_tab(self.active_tab)