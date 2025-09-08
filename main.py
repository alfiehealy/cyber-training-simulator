
from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox
from storage import ensure_data_dirs, DataStore
from ui import App

def main() -> None:
    ensure_data_dirs()
    # Load appearance/accent before creating root
    store = DataStore()
    s = store.load_settings()
    appearance = s.get("appearance", "Dark")
    accent = s.get("accent", "blue")
    try:
        ctk.set_appearance_mode(appearance.lower())
    except Exception:
        ctk.set_appearance_mode("dark")
    try:
        ctk.set_default_color_theme(accent)
    except Exception:
        ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Cyber Training Simulator")
    root.geometry("1180x740")
    root.minsize(1024, 640)

    app = App(root, store)
    app.pack(fill="both", expand=True)

    # safe direct call
    getattr(app, 'capture_screenshot', lambda: None)()
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        messagebox.showerror("Unexpected error",
            "Cyber Training Simulator encountered an unexpected error and will close.\n\n"
            f"{exc}\n\nIf the problem persists, delete files in the data/ folder to reset.")
        raise
