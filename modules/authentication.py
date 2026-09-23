"""
authentication.py
------------------
Login and Signup screens. All actual validation and hashing
happens in database.py; this file only handles the GUI and
displays friendly messages.

UI ENHANCED: now built from modules/theme.py so it shares the same
look (hover buttons, focus-highlighted inputs, gradient accent bar)
as the rest of the app. No change to login/signup logic.
"""

import tkinter as tk
from tkinter import messagebox

import database
from modules import theme


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        wrapper = tk.Frame(self, bg=theme.BG)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="SYNTAXAA", font=theme.F_DISPLAY,
                 fg=theme.ACCENT, bg=theme.BG).pack()
        theme.gradient_bar(wrapper, width=240).pack(pady=(6, 10))
        tk.Label(wrapper, text="Offline-First Intelligent Debugging & Analysis System",
                 font=theme.F_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG).pack(pady=(0, 28))

        card_outer = theme.make_card(wrapper, padx=42, pady=34)
        card_outer.pack()
        card = card_outer.inner

        tk.Label(card, text="Welcome back", font=theme.F_H2, fg=theme.TEXT,
                 bg=theme.SURFACE).pack(anchor="w", pady=(0, 2))
        tk.Label(card, text="Log in to continue debugging.", font=theme.F_SMALL,
                 fg=theme.TEXT_MUTED, bg=theme.SURFACE).pack(anchor="w", pady=(0, 18))

        theme.field_label(card, "USERNAME").pack(fill="x", pady=(0, 4))
        username_wrap, self.username_entry = theme.make_entry(card)
        username_wrap.pack(fill="x", pady=(0, 14))

        theme.field_label(card, "PASSWORD").pack(fill="x", pady=(0, 4))
        password_wrap, self.password_entry = theme.make_entry(card, show="*")
        password_wrap.pack(fill="x", pady=(0, 22))
        self.password_entry.bind("<Return>", lambda e: self.login())

        theme.make_button(card, "Log In", command=self.login, style="primary",
                           pady=10).pack(fill="x")

        theme.make_button(card, "Don't have an account? Sign Up",
                           command=lambda: controller.show_frame("SignupFrame"),
                           style="ghost", pady=8, font=theme.F_BODY).pack(fill="x", pady=(10, 0))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username.strip() or not password.strip():
            messagebox.showwarning("Login", "Please enter your username and password.")
            return

        user = database.verify_login(username, password)
        if user is None:
            messagebox.showerror("Login", "The username or password is incorrect, "
                                           "or the database could not be reached.")
            return

        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.controller.login_success(user)


class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        wrapper = tk.Frame(self, bg=theme.BG)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="Create Your Account", font=theme.F_H1,
                 fg=theme.ACCENT, bg=theme.BG).pack()
        tk.Label(wrapper, text="Join SYNTAXAA to start tracking your debugging journey.",
                 font=theme.F_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG).pack(pady=(4, 20))

        card_outer = theme.make_card(wrapper, padx=42, pady=32)
        card_outer.pack()
        card = card_outer.inner

        theme.field_label(card, "USERNAME").pack(fill="x", pady=(0, 4))
        username_wrap, self.username_entry = theme.make_entry(card)
        username_wrap.pack(fill="x", pady=(0, 14))

        theme.field_label(card, "PASSWORD").pack(fill="x", pady=(0, 4))
        password_wrap, self.password_entry = theme.make_entry(card, show="*")
        password_wrap.pack(fill="x", pady=(0, 16))

        theme.field_label(card, "I AM A").pack(fill="x", pady=(0, 6))
        self.user_type = tk.StringVar(value="student")
        type_row = tk.Frame(card, bg=theme.SURFACE)
        type_row.pack(fill="x", pady=(0, 22))
        self._make_type_option(type_row, "Student", "student")
        self._make_type_option(type_row, "Teacher", "teacher")

        theme.make_button(card, "Sign Up", command=self.signup, style="primary",
                           pady=10).pack(fill="x")

        theme.make_button(card, "Already have an account? Log In",
                           command=lambda: controller.show_frame("LoginFrame"),
                           style="ghost", pady=8, font=theme.F_BODY).pack(fill="x", pady=(10, 0))

    def _make_type_option(self, parent, label, value):
        tk.Radiobutton(
            parent, text=label, variable=self.user_type, value=value,
            bg=theme.SURFACE, fg=theme.TEXT, activebackground=theme.SURFACE,
            activeforeground=theme.ACCENT, selectcolor=theme.SURFACE_ALT,
            font=theme.F_BODY, relief="flat", highlightthickness=0,
            cursor="hand2",
        ).pack(side="left", padx=(0, 20))

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()

        success, message = database.create_user(username, password, user_type)
        if success:
            messagebox.showinfo("Sign Up", message)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.controller.show_frame("LoginFrame")
        else:
            messagebox.showerror("Sign Up", message)
