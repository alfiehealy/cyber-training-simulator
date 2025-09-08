
from __future__ import annotations
import sys, time, os
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, List
from models import GameSettings, GameState, RoundResult, Scenario
from storage import DataStore
from settings import SettingsDialog
from scenarios import load_scenarios
from game import pick_round_seconds, compute_score, select_scenarios, update_badges
from analytics import per_category, draw_bar_chart

def _toast(master, text: str, ms: int = 1400):
    try:
        t = ctk.CTkToplevel(master)
        t.overrideredirect(True)
        t.attributes('-topmost', True)
        t.configure(fg_color=('#222222','#111111'))
        lbl = ctk.CTkLabel(t, text=text, padx=16, pady=10)
        lbl.pack()
        master.update_idletasks()
        x = master.winfo_rootx() + master.winfo_width() - t.winfo_reqwidth() - 24
        y = master.winfo_rooty() + master.winfo_height() - t.winfo_reqheight() - 24
        t.geometry(f"+{x}+{y}")
        t.after(ms, t.destroy)
    except Exception:
        pass

def try_beep(ok: bool) -> None:
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK if ok else winsound.MB_ICONHAND)
    except Exception:
        pass

class App(ctk.CTkFrame):
    """Main application frame (CustomTkinter, polished aesthetics)."""
    def __init__(self, master, store: DataStore):
        super().__init__(master)
        self.store = store
        self.settings: Dict = store.load_settings()
        self.profile: Dict = store.load_profile()
        self.all_scenarios: List[Scenario] = load_scenarios()
        self.font_scale = self.settings.get("font_scale",100)/100.0

        # App layout: top bar + content
        self._make_topbar()
        self._center = ctk.CTkFrame(self)
        self._center.pack(fill="both", expand=True)
        self._make_start()

    def _make_topbar(self):
        bar = ctk.CTkFrame(self, corner_radius=0, height=56)
        bar.pack(fill="x")
        bar.grid_propagate(False)
        title = ctk.CTkLabel(bar, text="🛡️ Cyber Training Simulator",
                             font=("Segoe UI Semibold", int(18*self.font_scale)))
        title.grid(row=0, column=0, padx=14, pady=10, sticky="w")
        bar.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(bar, text="New Game", command=self.new_game, width=110).grid(row=0, column=2, padx=6)
        ctk.CTkButton(bar, text="Continue", command=self.continue_game, width=110).grid(row=0, column=3, padx=6)
        ctk.CTkButton(bar, text="Settings", command=self.open_settings, width=100).grid(row=0, column=4, padx=6)
        ctk.CTkButton(bar, text="How to Play", command=self.show_help, width=120).grid(row=0, column=5, padx=6)
        ctk.CTkButton(bar, text="About", command=self.show_about, width=90).grid(row=0, column=6, padx=6)
        ctk.CTkButton(bar, text="Badges", command=self.show_badges, width=90).grid(row=0, column=7, padx=6)
        self._appearance = ctk.StringVar(value=self.settings.get("appearance","Dark"))
        ctk.CTkOptionMenu(bar, values=["Dark","Light"],
                          variable=self._appearance, command=self._set_theme, width=90).grid(row=0, column=8, padx=12)
        sep = ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=("gray85","#2b2b2b"))
        sep.pack(fill="x")

    def _set_theme(self, mode: str):
        ctk.set_appearance_mode(mode.lower())
        self.settings["appearance"] = mode
        self.store.save_settings(self.settings)

    def _clear_center(self):
        for w in self._center.winfo_children():
            w.destroy()

    def _make_start(self):
        self._clear_center()
        center = self._center
        hero = ctk.CTkFrame(center, corner_radius=16)
        hero.pack(padx=18, pady=18, fill="x")
        ctk.CTkLabel(hero, text="Cyber Training Simulator",
                     font=("Segoe UI Black", int(28*self.font_scale))).pack(anchor="w", padx=18, pady=(14,0))
        ctk.CTkLabel(hero, text="Practice real‑world incident response. Choose the safest action, beat the timer, learn fast.",
                     wraplength=900, justify="left").pack(anchor="w", padx=18, pady=(6,14))

        actions = ctk.CTkFrame(center, corner_radius=12)
        actions.pack(padx=18, pady=6, fill="x")
        ctk.CTkButton(actions, text="Start New Game", command=self.new_game, height=38, width=220).pack(side="left", padx=12, pady=12)
        ctk.CTkButton(actions, text="Continue", command=self.continue_game, height=38, width=160).pack(side="left", padx=12, pady=12)

        lb = ctk.CTkFrame(center, corner_radius=12)
        lb.pack(padx=18, pady=12, fill="x")
        ctk.CTkLabel(lb, text="🏆 Leaderboard (Top 10)",
                     font=("Segoe UI Semibold", int(14*self.font_scale))).pack(anchor="w", padx=14, pady=(10,4))
        rows = self.store.get_leaderboard()
        if not rows:
            ctk.CTkLabel(lb, text="No scores yet — be the first!", padx=14).pack(anchor="w", padx=14, pady=(0,10))
        else:
            for row in rows:
                ctk.CTkLabel(lb, text=f"{row['name'][:16]:16}  {row['score']:>4}  {row['ts']}").pack(anchor="w", padx=14)

    def open_settings(self):
        def on_save(new):
            self.settings.update(new)
            self.store.save_settings(self.settings)
            self.font_scale = self.settings.get("font_scale",100)/100.0
            messagebox.showinfo("Settings","Saved.")
            self._make_start()
        SettingsDialog(self.master, self.settings, on_save)

    def show_help(self):
        messagebox.showinfo("How to Play",
            "You will see 10 randomized scenarios.\n"
            "- Choose the safest response.\n"
            "- Timer (optional) awards a fast‑bonus.\n"
            "- Streaks add small bonuses.\n"
            "- You can Skip (−10) or ask for a Hint (−5).\n"
            "Learn from the feedback after each choice!")

    def show_about(self):
        messagebox.showinfo("About", "Cyber Training Simulator — CustomTkinter Edition")

    def show_badges(self):
        badges = self.profile.get("unlocked_badges", [])
        win = ctk.CTkToplevel(self)
        win.title("Badges")
        win.geometry("420x300")
        ctk.CTkLabel(win, text="Badges", font=("Segoe UI Semibold", 16)).pack(pady=8)
        if not badges:
            ctk.CTkLabel(win, text="No badges yet. Keep playing!").pack(pady=12)
        else:
            for b in badges:
                ctk.CTkLabel(win, text=f"• {b}").pack(anchor="w", padx=16, pady=2)

    # ----- game flow -----
    def new_game(self):
        self.state = GameState()
        self.round_seconds = pick_round_seconds(GameSettings(**self.settings))
        self.deck = select_scenarios(self.all_scenarios, self.state.rounds_total, self.state.seen_ids)
        self.state.current_index = 0
        self._render_round()

    def continue_game(self):
        if hasattr(self, "state") and self.state.results and self.state.current_index < self.state.rounds_total:
            self._render_round()
        else:
            self.new_game()

    def _render_round(self):
        self._clear_center()
        gs = GameSettings(**self.settings)
        wrap = self._center

        # Left status
        left = ctk.CTkFrame(wrap, width=230, corner_radius=12); left.pack(side="left", fill="y", padx=14, pady=14)
        left.pack_propagate(False)
        self.score_var = ctk.StringVar(value=str(getattr(self, 'state', GameState()).score))
        ctk.CTkLabel(left, text="Score", font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=12, pady=(12,2))
        ctk.CTkLabel(left, textvariable=self.score_var).pack(anchor="w", padx=12, pady=(0,8))
        self.timer_var = ctk.StringVar(value="--")
        ctk.CTkLabel(left, text="Timer", font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=12, pady=(8,2))
        ctk.CTkLabel(left, textvariable=self.timer_var).pack(anchor="w", padx=12, pady=(0,8))
        ctk.CTkLabel(left, text=f"Round {self.state.current_index+1} / {self.state.rounds_total}").pack(anchor="w", padx=12)
        self.progress = ctk.CTkProgressBar(left); self.progress.pack(padx=12, pady=10, fill="x")
        self.progress.set(self.state.progress_fraction())

        # Center scenario
        center = ctk.CTkFrame(wrap, corner_radius=12); center.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        self.scenario = self.deck[self.state.current_index]
        ctk.CTkLabel(center, text=self.scenario.title, font=("Segoe UI Semibold", 16)).pack(anchor="w", padx=12, pady=(10,6))
        txt = ctk.CTkTextbox(center, height=120, wrap="word"); txt.insert("1.0", self.scenario.narrative); txt.configure(state="disabled")
        txt.pack(fill="x", padx=12, pady=6)

        self.choice_var = ctk.IntVar(value=-1)
        for i, ch in enumerate(self.scenario.choices):
            ctk.CTkRadioButton(center, text=ch.label, variable=self.choice_var, value=i).pack(anchor="w", padx=12, pady=4)

        row = ctk.CTkFrame(center); row.pack(fill="x", pady=12, padx=10)
        ctk.CTkButton(row, text="Submit", command=self.on_submit).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Skip (−10)", command=self.on_skip).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Hint (−5)", command=self.on_hint).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Report Issue", command=self.on_report).pack(side="right", padx=6)

        # Right tips
        right = ctk.CTkFrame(wrap, width=280, corner_radius=12); right.pack(side="right", fill="y", padx=14, pady=14)
        right.pack_propagate(False)
        tip = self.scenario.hint or "Use policy + least privilege."
        ctk.CTkLabel(right, text="Hint", font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=12, pady=(10,2))
        ctk.CTkLabel(right, text=tip, wraplength=240, justify="left").pack(anchor="w", padx=12)
        ctk.CTkLabel(right, text="References", font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=12, pady=(12,2))
        refbox = ctk.CTkTextbox(right, height=120, wrap="word")
        refbox.insert("1.0", "\n".join(self.scenario.references or ["Follow company policy.", "Think before you click."]))
        refbox.configure(state="disabled"); refbox.pack(fill="x", padx=12)

        # Timer
        self.remaining = self.round_seconds if gs.timer_enabled else 0
        self._tick_id = None
        if gs.timer_enabled: self._tick()

        # Keyboard shortcuts
        self.master.bind("<Return>", lambda e: self.on_submit())
        self.master.bind("<Escape>", lambda e: self.on_skip())
        for k in range(1,10):
            self.master.bind(f"<Key-{k}>", lambda e, kk=k: self._select_choice(kk))
        self.master.bind("<Key-h>", lambda e: self.on_hint())
        self.master.bind("<Key-s>", lambda e: self.on_skip())

    def _select_choice(self, k:int):
        idx = k-1
        try:
            self.choice_var.set(idx)
            _toast(self.master, f"Selected option {k}")
        except Exception:
            pass

    def _tick(self):
        self.timer_var.set(f"{self.remaining}s")
        if self.remaining <= 0: return
        self.remaining -= 1
        self._tick_id = self.after(1000, self._tick)

    def on_hint(self):
        if not self.settings.get("hints_enabled", True):
            messagebox.showinfo("Hints disabled", "Enable hints in Settings."); return
        self.state.score += self.settings.get("hint_cost", -5)
        self.score_var.set(str(self.state.score))
        _toast(self.master, "Hint shown (−5)")

    def on_report(self):
        import tkinter.simpledialog as sd
        msg = sd.askstring("Report issue", "Describe the problem (saved locally):")
        if msg:
            self.store.log_feedback(self.profile.get("name","Player"), self.scenario.id, msg)
            _toast(self.master, "Feedback saved")

    def on_skip(self):
        gained, outcome = compute_score(GameSettings(**self.settings), self.scenario, None, 0, self.state.streak)
        self._finalise_choice(-1, gained, outcome, time_taken=self.round_seconds - max(0,self.remaining))

    def on_submit(self):
        sel = self.choice_var.get()
        if sel < 0:
            messagebox.showwarning("Choose one", "Please select an option."); return
        if self._tick_id: self.after_cancel(self._tick_id)
        gained, outcome = compute_score(GameSettings(**self.settings), self.scenario, sel, max(0,self.remaining), self.state.streak)
        self._finalise_choice(sel, gained, outcome, time_taken=self.round_seconds - max(0,self.remaining))

    def _finalise_choice(self, sel:int, gained:int, outcome:str, time_taken:float):
        self.state.score += gained; self.score_var.set(str(self.state.score))
        if outcome=="Correct": self.state.streak += 1; try_beep(True)
        else: self.state.streak = 0; try_beep(False)
        rr = RoundResult(self.scenario.id, None if sel<0 else sel, time_taken, gained, outcome)
        self.state.results.append(rr)
        self._show_feedback(outcome, gained)

    def _show_feedback(self, outcome:str, gained:int):
        msg = f"Result: {outcome}\nPoints: {gained}\n\nWhy: {self.scenario.feedback_why}\nPro tip: {self.scenario.pro_tip}"
        messagebox.showinfo("Round feedback", msg)
        self.state.current_index += 1
        if self.state.current_index >= self.state.rounds_total:
            self._show_summary()
        else:
            self._render_round()

    def _show_summary(self):
        self._clear_center()
        outer = self._center
        ctk.CTkLabel(outer, text="Game Summary", font=("Segoe UI Semibold", 18)).pack(anchor="w", pady=8, padx=18)
        ctk.CTkLabel(outer, text=f"Total score: {self.state.score}").pack(anchor="w", padx=18)

        from tkinter import Canvas
        chart_holder = ctk.CTkFrame(outer, corner_radius=12); chart_holder.pack(pady=8, padx=18, fill="x")
        cv = Canvas(chart_holder, width=640, height=240, background="#ffffff", highlightthickness=0); cv.pack()
        id_to_cat = {s.id:s.category for s in self.deck}
        draw_bar_chart(cv, per_category(self.state.results, id_to_cat))
        self.store.save_screen_postscript(cv, "summary-chart-ctk")

        wrong = [r for r in self.state.results if r.outcome in ("Unsafe","Partial")]
        tips = []
        for r in wrong[:3]:
            scen = next((s for s in self.deck if s.id==r.scenario_id), None)
            if scen: tips.append(f"• {scen.title}: {scen.pro_tip}")
        if not tips: tips = ["• Great job! Keep following policy and best practices."]
        ctk.CTkLabel(outer, text="Top lessons learned:", font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=18, pady=(8,2))
        ctk.CTkLabel(outer, text="\n".join(tips), justify="left").pack(anchor="w", padx=18)

        update_badges(self.profile, self.state.results, GameSettings(**self.settings))
        if self.state.score > self.profile.get("best_score",0):
            self.profile["best_score"] = self.state.score
        self.store.save_profile(self.profile)
        self.store.append_leaderboard(self.profile.get("name","Player"), self.state.score)

        btns = ctk.CTkFrame(outer); btns.pack(pady=12, padx=18, fill="x")
        ctk.CTkButton(btns, text="Back to Start", command=self._make_start).pack(side="left")
        ctk.CTkButton(btns, text="Save Report", command=self._save_report).pack(side="right")

    def _save_report(self):
        os.makedirs('data/reports', exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = f"data/reports/summary-{ts}.md"
        lines = [f"# Cyber Training Simulator — Summary ({ts})",
                 f"\n**Score:** {self.state.score}",
                 f"\n**Rounds:** {self.state.rounds_total}",
                 "\n\n## Lessons Learned"]
        wrong = [r for r in self.state.results if r.outcome in ("Unsafe","Partial")]
        for r in wrong[:5]:
            scen = next((s for s in self.deck if s.id==r.scenario_id), None)
            if scen:
                lines.append(f"- **{scen.title}** — {scen.pro_tip}")
        lines.append("\n_Data saved locally by the app._\n")
        with open(path, "w", encoding="utf-8") as f: f.write("\n".join(lines))
        _toast(self.master, "Report saved")

    def capture_screenshot(self):
        try:
            from tkinter import Canvas
            cv = Canvas(self, width=420, height=160, background="#ffffff", highlightthickness=0)
            cv.create_text(10, 10, anchor="nw", text="Cyber Training Simulator (CTk)")
            self.store.save_screen_postscript(cv, "start-ctk")
            cv.destroy()
        except Exception:
            pass
