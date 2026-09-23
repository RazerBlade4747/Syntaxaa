import database
import tkinter as tk

from modules import theme


class StudentDashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG)
        self.controller = controller

        header = tk.Frame(self, bg=theme.BG)
        header.pack(fill="x", padx=30, pady=(22, 4))
        self.welcome_label = tk.Label(header, text="Welcome!", font=theme.F_H1,
                                       fg=theme.TEXT, bg=theme.BG)
        self.welcome_label.pack(side="left")
        theme.make_button(header, "Logout", command=self.logout, style="ghost",
                           padx=14, pady=7, font=theme.F_BODY).pack(side="right")

        self.status_holder = tk.Frame(self, bg=theme.BG)
        self.status_holder.pack(anchor="w", padx=30, pady=(6, 0))

        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", padx=30, pady=(16, 0))

        grid = tk.Frame(self, bg=theme.BG)
        grid.pack(expand=True, fill="both", padx=30, pady=26)

        cards = [
            ("\U0001F41E", "Error Detection", "Check your code and get beginner-friendly explanations.",
             "ErrorDetectionFrame"),
            ("\U0001F4D6", "Error Encyclopedia", "Browse and search common Python errors.",
             "EncyclopediaFrame"),
            ("\U0001F9EC", "Bug DNA", "See your personal mistake patterns and weak concepts.",
             "BugDNAFrame"),
            ("\U0001F4C8", "My Progress", "Track your debugging history and improvement.",
             "ProgressFrame"),
            ("\U0001F91D", "Join a Class", "Optionally connect with your teacher using a class code.",
             "JoinClassFrame"),
        ]

        for i, (icon, title, desc, target) in enumerate(cards):
            accent = theme.CARD_ACCENTS[i % len(theme.CARD_ACCENTS)]
            card_outer = theme.make_card(grid, clickable=True, padx=22, pady=20)
            card_outer.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")
            inner = card_outer.inner

            top_row = tk.Frame(inner, bg=theme.SURFACE)
            top_row.pack(fill="x", anchor="w")
            tk.Label(top_row, text=icon, font=(theme.FONT_FAMILY, 22),
                     bg=theme.SURFACE, fg=accent).pack(side="left")
            tk.Label(top_row, text=title, font=theme.F_H3, fg=theme.TEXT,
                     bg=theme.SURFACE).pack(side="left", padx=(10, 0))

            tk.Label(inner, text=desc, font=theme.F_SMALL, fg=theme.TEXT_MUTED,
                     bg=theme.SURFACE, wraplength=260, justify="left").pack(
                anchor="w", pady=(8, 0))

            self._bind_click(card_outer, target)

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

    def _bind_click(self, card_outer, target):
        def go(_e=None):
            self.controller.show_frame(target)

        card_outer.bind("<Button-1>", go)
        card_outer.inner.bind("<Button-1>", go)
        for child in card_outer.inner.winfo_children():
            child.bind("<Button-1>", go)
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", go)

    def on_show(self):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome, {user['username']}!")

        for w in self.status_holder.winfo_children():
            w.destroy()

        if database.is_offline():
            pass



    def logout(self):
        self.controller.logout()
