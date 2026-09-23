"""
authentication.py
-------------------
Login and Signup screens. All actual validation and hashing
happens in database.py; this file only handles the GUI and
displays friendly messages.
"""

import tkinter as tk
from tkinter import messagebox

import database


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        wrapper = tk.Frame(self, bg="#0d1117")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="SYNTAXAA", font=("Segoe UI", 34, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(pady=(0, 5))
        tk.Label(wrapper, text="Offline-First Intelligent Debugging & Analysis System",
                 font=("Segoe UI", 11), fg="#8b949e", bg="#0d1117").pack(pady=(0, 30))

        card = tk.Frame(wrapper, bg="#161b22", padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Login", font=("Segoe UI", 16, "bold"), fg="white", bg="#161b22").pack(pady=(0, 15))

        tk.Label(card, text="Username", fg="#8b949e", bg="#161b22", anchor="w").pack(fill="x")
        self.username_entry = tk.Entry(card, font=("Segoe UI", 12), bg="#0d1117", fg="white",
                                        insertbackground="white", relief="flat")
        self.username_entry.pack(fill="x", ipady=6, pady=(0, 10))

        tk.Label(card, text="Password", fg="#8b949e", bg="#161b22", anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(card, font=("Segoe UI", 12), bg="#0d1117", fg="white",
                                        insertbackground="white", relief="flat", show="*")
        self.password_entry.pack(fill="x", ipady=6, pady=(0, 20))

        tk.Button(card, text="Log In", command=self.login, bg="#00e5ff", fg="#0d1117",
                  font=("Segoe UI", 11, "bold"), relief="flat", pady=8).pack(fill="x")

        tk.Button(card, text="Don't have an account? Sign Up", command=lambda: controller.show_frame("SignupFrame"),
                  bg="#161b22", fg="#58a6ff", relief="flat", pady=6).pack(fill="x", pady=(10, 0))

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
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        wrapper = tk.Frame(self, bg="#0d1117")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="Create Your Syntaxaa Account", font=("Segoe UI", 20, "bold"),
                 fg="#00e5ff", bg="#0d1117").pack(pady=(0, 20))

        card = tk.Frame(wrapper, bg="#161b22", padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Username", fg="#8b949e", bg="#161b22", anchor="w").pack(fill="x")
        self.username_entry = tk.Entry(card, font=("Segoe UI", 12), bg="#0d1117", fg="white",
                                        insertbackground="white", relief="flat")
        self.username_entry.pack(fill="x", ipady=6, pady=(0, 10))

        tk.Label(card, text="Password", fg="#8b949e", bg="#161b22", anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(card, font=("Segoe UI", 12), bg="#0d1117", fg="white",
                                        insertbackground="white", relief="flat", show="*")
        self.password_entry.pack(fill="x", ipady=6, pady=(0, 10))

        tk.Label(card, text="I am a:", fg="#8b949e", bg="#161b22", anchor="w").pack(fill="x")
        self.user_type = tk.StringVar(value="student")
        type_row = tk.Frame(card, bg="#161b22")
        type_row.pack(fill="x", pady=(0, 20))
        tk.Radiobutton(type_row, text="Student", variable=self.user_type, value="student",
                        bg="#161b22", fg="white", selectcolor="#0d1117").pack(side="left")
        tk.Radiobutton(type_row, text="Teacher", variable=self.user_type, value="teacher",
                        bg="#161b22", fg="white", selectcolor="#0d1117").pack(side="left")

        tk.Button(card, text="Sign Up", command=self.signup, bg="#00e5ff", fg="#0d1117",
                  font=("Segoe UI", 11, "bold"), relief="flat", pady=8).pack(fill="x")

        tk.Button(card, text="Already have an account? Log In", command=lambda: controller.show_frame("LoginFrame"),
                  bg="#161b22", fg="#58a6ff", relief="flat", pady=6).pack(fill="x", pady=(10, 0))

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
