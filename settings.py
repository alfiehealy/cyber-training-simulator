
from __future__ import annotations
import customtkinter as ctk
from typing import Dict

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, settings: Dict, on_save):
        super().__init__(master)
        self.title("Settings")
        self.on_save = on_save
        self.geometry("560x420")
        self.resizable(False, False)

        self.vars = {
            "appearance": ctk.StringVar(value=settings.get("appearance","Dark")),
            "accent": ctk.StringVar(value=settings.get("accent","blue")),
            "difficulty": ctk.StringVar(value=settings.get("difficulty","medium")),
            "timer_enabled": ctk.BooleanVar(value=settings.get("timer_enabled", True)),
            "round_seconds": ctk.IntVar(value=settings.get("round_seconds",45)),
            "penalties_enabled": ctk.BooleanVar(value=settings.get("penalties_enabled", True)),
            "hints_enabled": ctk.BooleanVar(value=settings.get("hints_enabled", True)),
            "sound_enabled": ctk.BooleanVar(value=settings.get("sound_enabled", False)),
            "high_contrast": ctk.BooleanVar(value=settings.get("high_contrast", False)),
            "font_scale": ctk.IntVar(value=settings.get("font_scale", 100)),
        }

        pad = {"padx":12,"pady":8}
        for i in range(2): self.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(self, text="Appearance").grid(row=0, column=0, sticky="w", **pad)
        ctk.CTkOptionMenu(self, variable=self.vars["appearance"], values=["Dark","Light"]).grid(row=0,column=1,sticky="ew",**pad)

        ctk.CTkLabel(self, text="Accent").grid(row=1, column=0, sticky="w", **pad)
        ctk.CTkOptionMenu(self, variable=self.vars["accent"], values=["blue","green","dark-blue"]).grid(row=1,column=1,sticky="ew",**pad)

        ctk.CTkLabel(self, text="Difficulty").grid(row=2, column=0, sticky="w", **pad)
        ctk.CTkOptionMenu(self, variable=self.vars["difficulty"], values=["easy","medium","hard"]).grid(row=2,column=1,sticky="ew",**pad)

        ctk.CTkSwitch(self, text="Enable timer", variable=self.vars["timer_enabled"]).grid(row=3,column=0, sticky="w", **pad)
        ctk.CTkLabel(self, text="Seconds").grid(row=3,column=1, sticky="w", **pad)
        ctk.CTkEntry(self, textvariable=self.vars["round_seconds"], width=80).grid(row=3,column=1, sticky="e", **pad)

        ctk.CTkSwitch(self, text="Enable penalties", variable=self.vars["penalties_enabled"]).grid(row=4,column=0, sticky="w", **pad)
        ctk.CTkSwitch(self, text="Enable hints", variable=self.vars["hints_enabled"]).grid(row=4,column=1, sticky="w", **pad)
        ctk.CTkSwitch(self, text="Sound effects (Windows)", variable=self.vars["sound_enabled"]).grid(row=5,column=0, sticky="w", **pad)
        ctk.CTkSwitch(self, text="High contrast", variable=self.vars["high_contrast"]).grid(row=5,column=1, sticky="w", **pad)

        ctk.CTkLabel(self, text="Font size %").grid(row=6,column=0, sticky="w", **pad)
        ctk.CTkEntry(self, textvariable=self.vars["font_scale"], width=80).grid(row=6,column=1, sticky="w", **pad)

        btns = ctk.CTkFrame(self); btns.grid(row=7, column=0, columnspan=2, sticky="e", padx=12, pady=12)
        ctk.CTkButton(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Save", command=self._save).pack(side="right")

    def _save(self):
        out = {k:v.get() for k,v in self.vars.items()}
        self.on_save(out)
        self.destroy()
