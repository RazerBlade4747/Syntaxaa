"""
theme.py
--------
Central design system for the SYNTAXAA desktop app.

Every screen (LoginFrame, StudentDashboardFrame, ErrorDetectionFrame, ...)
now pulls its colors, fonts and common widgets from here instead of
hard-coding hex values everywhere. That means:
  1. The whole app can be re-themed by editing one file.
  2. Every button / card / input behaves and looks the same way
     (hover states, focus states, spacing) across every screen.

VIVA NOTE: This file introduces NO new business logic - it only builds
nicer-looking Tkinter widgets out of the same tk.Frame / tk.Button /
tk.Entry primitives the project already used. Nothing here talks to
the database or changes how the app behaves.
"""

import tkinter as tk
from tkinter import font as tkfont

# =========================================================
# COLOR PALETTE
# =========================================================
BG = "#0b0f17"            # app background
BG_ALT = "#0d1117"        # secondary background (kept for compatibility)
SURFACE = "#161b22"       # cards / panels
SURFACE_HOVER = "#1c2333"  # card hover state
SURFACE_ALT = "#0d1117"   # text boxes / inputs
BORDER = "#232a36"        # default hairline border
BORDER_STRONG = "#30363d"

ACCENT = "#00e5ff"        # brand cyan
ACCENT_HOVER = "#3ceeff"
ACCENT_SOFT = "#0f3138"

PURPLE = "#8957e5"
PURPLE_HOVER = "#9e75ee"

SUCCESS = "#3fb950"
SUCCESS_HOVER = "#4fd15f"
WARNING = "#f0883e"
WARNING_HOVER = "#ffa15c"
DANGER = "#f85149"
DANGER_HOVER = "#ff6b64"

TEXT = "#e6edf3"
TEXT_MUTED = "#8b949e"
TEXT_DIM = "#586069"
TEXT_ON_ACCENT = "#04121a"

CARD_ACCENTS = [ACCENT, PURPLE, SUCCESS, WARNING, "#58a6ff", "#f778ba"]

# =========================================================
# TYPOGRAPHY
# =========================================================
FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"

F_DISPLAY = (FONT_FAMILY, 32, "bold")
F_H1 = (FONT_FAMILY, 20, "bold")
F_H2 = (FONT_FAMILY, 15, "bold")
F_H3 = (FONT_FAMILY, 13, "bold")
F_BODY = (FONT_FAMILY, 11)
F_BODY_BOLD = (FONT_FAMILY, 11, "bold")
F_SMALL = (FONT_FAMILY, 9)
F_BUTTON = (FONT_FAMILY, 11, "bold")
F_MONO = (MONO_FAMILY, 11)
F_STAT = (FONT_FAMILY, 24, "bold")


def apply_app_defaults(root):
    """Call once from main.py to set sane app-wide font defaults."""
    try:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=FONT_FAMILY, size=10)
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=FONT_FAMILY, size=10)
    except tk.TclError:
        pass
    root.configure(bg=BG)


# =========================================================
# BUTTONS
# =========================================================
_BUTTON_STYLES = {
    "primary": dict(bg=ACCENT, hover=ACCENT_HOVER, fg=TEXT_ON_ACCENT),
    "success": dict(bg=SUCCESS, hover=SUCCESS_HOVER, fg="#04170a"),
    "purple": dict(bg=PURPLE, hover=PURPLE_HOVER, fg="white"),
    "warning": dict(bg=WARNING, hover=WARNING_HOVER, fg="#2b1400"),
    "danger": dict(bg=DANGER, hover=DANGER_HOVER, fg="white"),
    "ghost": dict(bg=SURFACE, hover=SURFACE_HOVER, fg=TEXT),
    "outline": dict(bg=BG, hover=SURFACE, fg=ACCENT),
}


def make_button(parent, text, command=None, style="primary", icon=None,
                 padx=16, pady=9, font=F_BUTTON, width=None):
    """
    Returns a tk.Button styled per `style` ("primary", "success", "purple",
    "warning", "danger", "ghost", "outline") with a hover-highlight effect.
    Drop-in replacement for the old bare tk.Button(...) calls.
    """
    cfg = _BUTTON_STYLES.get(style, _BUTTON_STYLES["primary"])
    label = f"{icon}  {text}" if icon else text
    btn = tk.Button(
        parent, text=label, command=command, bg=cfg["bg"], fg=cfg["fg"],
        activebackground=cfg["hover"], activeforeground=cfg["fg"],
        font=font, relief="flat", bd=0, padx=padx, pady=pady,
        cursor="hand2", width=width if width else 0,
    )

    def on_enter(_e):
        btn.config(bg=cfg["hover"])

    def on_leave(_e):
        btn.config(bg=cfg["bg"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


# =========================================================
# CARDS
# =========================================================
def make_card(parent, bg=SURFACE, padx=20, pady=18, clickable=False,
              border=BORDER, hover_border=ACCENT):
    """
    A Frame with a thin hairline border, ready to hold widgets.
    If clickable=True, the border lights up on hover and the cursor
    becomes a hand - use for dashboard-style navigation cards.
    """
    outer = tk.Frame(parent, bg=border, highlightthickness=0)
    inner = tk.Frame(outer, bg=bg, padx=padx, pady=pady)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    outer.inner = inner

    if clickable:
        outer.config(cursor="hand2")
        inner.config(cursor="hand2")

        def on_enter(_e):
            outer.config(bg=hover_border)
            inner.config(bg=SURFACE_HOVER)
            _recolor_children(inner, SURFACE_HOVER)

        def on_leave(_e):
            outer.config(bg=border)
            inner.config(bg=bg)
            _recolor_children(inner, bg)

        outer.bind("<Enter>", on_enter)
        outer.bind("<Leave>", on_leave)
        inner.bind("<Enter>", on_enter)
        inner.bind("<Leave>", on_leave)

    return outer


def _recolor_children(widget, bg):
    """Keeps every nested label/frame inside a hoverable card in sync
    with the card's background, so the hover fill looks solid instead
    of leaving mismatched patches behind."""
    for child in widget.winfo_children():
        try:
            if isinstance(child, (tk.Label, tk.Frame)):
                child.config(bg=bg)
        except tk.TclError:
            pass
        _recolor_children(child, bg)


def make_stat_card(parent, label, value, accent=ACCENT):
    """Small metric card used on progress / teacher-detail screens."""
    card = tk.Frame(parent, bg=SURFACE, padx=20, pady=16,
                     highlightthickness=1, highlightbackground=BORDER)
    tk.Label(card, text=str(value), font=F_STAT, fg=accent, bg=SURFACE).pack()
    tk.Label(card, text=label, font=F_SMALL, fg=TEXT_MUTED, bg=SURFACE).pack(pady=(2, 0))
    return card


# =========================================================
# INPUTS
# =========================================================
def make_entry(parent, show=None, placeholder=None, font=F_BODY):
    """
    Returns (wrapper_frame, entry_widget). The wrapper frame draws a
    1px border that turns accent-cyan while the entry has focus, giving
    real visual feedback instead of a flat, static input box.
    """
    wrapper = tk.Frame(parent, bg=BORDER)
    entry = tk.Entry(wrapper, font=font, bg=SURFACE_ALT, fg=TEXT,
                      insertbackground=ACCENT, relief="flat", show=show or "")
    entry.pack(fill="x", ipady=8, padx=1, pady=1)

    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg=TEXT_DIM)

        def on_focus_in(_e):
            wrapper.config(bg=ACCENT)
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=TEXT)

        def on_focus_out(_e):
            wrapper.config(bg=BORDER)
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=TEXT_DIM)
    else:
        def on_focus_in(_e):
            wrapper.config(bg=ACCENT)

        def on_focus_out(_e):
            wrapper.config(bg=BORDER)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return wrapper, entry


def field_label(parent, text):
    return tk.Label(parent, text=text, fg=TEXT_MUTED, bg=SURFACE,
                     font=F_SMALL, anchor="w")


# =========================================================
# LAYOUT HELPERS
# =========================================================
def divider(parent, color=BORDER):
    line = tk.Frame(parent, bg=color, height=1)
    line.pack(fill="x")
    return line


def gradient_bar(parent, width=220, height=4, c1=ACCENT, c2=PURPLE):
    """A short two-tone accent bar, used under headings for a bit of polish."""
    canvas = tk.Canvas(parent, width=width, height=height, bg=BG,
                        highlightthickness=0, bd=0)
    steps = 40
    r1, g1, b1 = parent.winfo_rgb(c1)
    r2, g2, b2 = parent.winfo_rgb(c2)
    for i in range(steps):
        t = i / steps
        r = int((r1 + (r2 - r1) * t) / 256)
        g = int((g1 + (g2 - g1) * t) / 256)
        b = int((b1 + (b2 - b1) * t) / 256)
        color = f"#{r:02x}{g:02x}{b:02x}"
        x0 = width * i / steps
        x1 = width * (i + 1) / steps
        canvas.create_rectangle(x0, 0, x1 + 1, height, outline="", fill=color)
    return canvas


def build_header(parent, title, subtitle=None, on_back=None, on_logout=None,
                  back_text="Back to Dashboard"):
    """
    Standard screen header: big title (+ optional subtitle) on the left,
    nav buttons on the right, thin divider underneath. Used by every
    screen so navigation feels identical everywhere in the app.
    """
    wrap = tk.Frame(parent, bg=BG)
    wrap.pack(fill="x")

    row = tk.Frame(wrap, bg=BG)
    row.pack(fill="x", padx=30, pady=(22, 4))

    title_col = tk.Frame(row, bg=BG)
    title_col.pack(side="left")
    title_label = tk.Label(title_col, text=title, font=F_H1, fg=TEXT, bg=BG)
    title_label.pack(anchor="w")
    if subtitle:
        tk.Label(title_col, text=subtitle, font=F_SMALL, fg=TEXT_MUTED,
                  bg=BG).pack(anchor="w", pady=(2, 0))

    btn_col = tk.Frame(row, bg=BG)
    btn_col.pack(side="right")
    if on_logout:
        make_button(btn_col, "Logout", command=on_logout, style="ghost",
                    padx=14, pady=7, font=F_BODY).pack(side="right")
    if on_back:
        make_button(btn_col, back_text, command=on_back, style="ghost",
                    padx=14, pady=7, font=F_BODY).pack(side="right", padx=(0, 10))

    pad = tk.Frame(wrap, bg=BG, height=14)
    pad.pack(fill="x")
    line = tk.Frame(parent, bg=BORDER, height=1)
    line.pack(fill="x", padx=30)
    spacer = tk.Frame(parent, bg=BG, height=12)
    spacer.pack(fill="x")
    wrap.title_label = title_label
    return wrap


def status_pill(parent, text, kind="info"):
    """Small rounded-looking status badge (e.g. Offline Mode / Connected)."""
    colors = {
        "info": (ACCENT_SOFT, ACCENT),
        "success": ("#0f2415", SUCCESS),
        "warning": ("#2b1d0e", WARNING),
    }
    bg, fg = colors.get(kind, colors["info"])
    pill = tk.Frame(parent, bg=bg)
    tk.Label(pill, text=f"\u25CF  {text}", font=F_SMALL, bg=bg, fg=fg,
              padx=10, pady=4).pack()
    return pill
