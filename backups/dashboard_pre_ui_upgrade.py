"""
dashboard.py
------------
The student's main hub after login: a simple card-based menu
linking to every offline feature.
"""

import tkinter as tk


class StudentDashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d1117")
        self.controller = controller

        header = tk.Frame(self, bg="#0d1117")
        header.pack(fill="x", padx=30, pady=(20, 10))
        self.welcome_label = tk.Label(header, text="Welcome!", font=("Segoe UI", 20, "bold"),
                                       fg="#00e5ff", bg="#0d1117")
        self.welcome_label.pack(side="left")
        tk.Button(header, text="Logout", command=self.logout, bg="#161b22", fg="#c9d1d9",
                  relief="flat", padx=12, pady=6).pack(side="right")

        self.status_label = tk.Label(self, text="", font=("Segoe UI", 10), fg="#8b949e", bg="#0d1117")
        self.status_label.pack(anchor="w", padx=30)

        grid = tk.Frame(self, bg="#0d1117")
        grid.pack(expand=True, padx=30, pady=30)

        cards = [
            ("🐞 Error Detection", "Check your code and get beginner-friendly explanations.",
             "ErrorDetectionFrame"),
            ("📖 Error Encyclopedia", "Browse and search common Python errors.",
             "EncyclopediaFrame"),
            ("🧬 Bug DNA", "See your personal mistake patterns and weak concepts.",
             "BugDNAFrame"),
            ("📈 My Progress", "Track your debugging history and improvement.",
             "ProgressFrame"),
            ("🤝 Join a Class", "Optionally connect with your teacher using a class code.",
             "JoinClassFrame"),
        ]

        for i, (title, desc, target) in enumerate(cards):
            card = tk.Frame(grid, bg="#161b22", padx=20, pady=20, cursor="hand2")
            card.grid(row=i // 2, column=i % 2, padx=15, pady=15, sticky="nsew")
            tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), fg="white", bg="#161b22").pack(anchor="w")
            tk.Label(card, text=desc, font=("Segoe UI", 10), fg="#8b949e", bg="#161b22",
                     wraplength=250, justify="left").pack(anchor="w", pady=(5, 0))
            card.bind("<Button-1>", lambda e, t=target: controller.show_frame(t))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, t=target: controller.show_frame(t))

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

    def on_show(self):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome, {user['username']}!")
        if self.controller.offline_mode:
            self.status_label.config(text="Offline Mode Active - Core debugging features are available.",
                                      fg="#f0883e")
        else:
            self.status_label.config(text="Connected to database.", fg="#3fb950")

    def logout(self):
        self.controller.logout()
