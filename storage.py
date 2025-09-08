
from __future__ import annotations
import json, time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path("data")
SCREENS_DIR = DATA_DIR / "screens"
BACKUP_DIR = DATA_DIR / "backups"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
PROFILE_FILE = DATA_DIR / "profile.json"
FEEDBACK_CSV = DATA_DIR / "feedback.csv"

def ensure_data_dirs() -> None:
    for d in (DATA_DIR, SCREENS_DIR, BACKUP_DIR):
        d.mkdir(parents=True, exist_ok=True)
    if not FEEDBACK_CSV.exists():
        FEEDBACK_CSV.write_text("timestamp,player,scenario_id,message\n", encoding="utf-8")

def _safe_load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        if path.exists():
            ts = time.strftime("%Y%m%d-%H%M%S")
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            (BACKUP_DIR / f"{path.stem}-{ts}.bak").write_bytes(path.read_bytes())
        return default

def _safe_save_json(path: Path, data: Any) -> None:
    if is_dataclass(data):
        data = asdict(data)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)

class DataStore:
    def load_settings(self) -> Dict[str, Any]:
        default = {
            "difficulty":"medium","timer_enabled":True,"round_seconds":45,"penalties_enabled":True,
            "hints_enabled":True,"sound_enabled":False,"high_contrast":False,"font_scale":100,
            "unsafe_penalty":-25,"base_correct":100,"base_partial":50,"skip_penalty":-10,"hint_cost":-5,
            "appearance":"Dark","accent":"blue"
        }
        if not SETTINGS_FILE.exists():
            _safe_save_json(SETTINGS_FILE, default); return default
        return _safe_load_json(SETTINGS_FILE, default)

    def save_settings(self, settings: Dict[str, Any]) -> None:
        _safe_save_json(SETTINGS_FILE, settings)

    def load_profile(self) -> Dict[str, Any]:
        default = {"name":"Player","best_score":0,"unlocked_badges":[],"last_session":{}}
        if not PROFILE_FILE.exists():
            _safe_save_json(PROFILE_FILE, default); return default
        return _safe_load_json(PROFILE_FILE, default)

    def save_profile(self, profile: Dict[str, Any]) -> None:
        _safe_save_json(PROFILE_FILE, profile)

    def append_leaderboard(self, name:str, score:int)->None:
        lb = self.get_leaderboard()
        lb.append({"name":name,"score":score,"ts":time.strftime("%Y-%m-%d %H:%M")})
        lb.sort(key=lambda r: r["score"], reverse=True)
        lb[:] = lb[:10]
        _safe_save_json(LEADERBOARD_FILE, lb)

    def set_leaderboard(self, rows: List[Dict[str,Any]])->None:
        _safe_save_json(LEADERBOARD_FILE, rows)

    def get_leaderboard(self)->List[Dict[str,Any]]:
        return _safe_load_json(LEADERBOARD_FILE, [])

    def log_feedback(self, player:str, scenario_id:str, message:str)->None:
        line = f"{int(time.time())},{player},{scenario_id},{message.replace(',',';')}\n"
        with FEEDBACK_CSV.open("a", encoding="utf-8") as f: f.write(line)

    def save_screen_postscript(self, widget, label:str)->None:
        try:
            from tkinter import Canvas, Tk
            if hasattr(widget, "postscript"):
                widget.postscript(colormode="color", file=str(SCREENS_DIR / f"{label}.ps"))
            else:
                tmp = Tk(); tmp.withdraw()
                cv = Canvas(tmp, width=480, height=220, background="white")
                cv.create_text(10,10,anchor="nw",text=f"Screenshot: {label}")
                cv.postscript(file=str(SCREENS_DIR / f"{label}.ps"))
                tmp.destroy()
        except Exception: 
            pass
