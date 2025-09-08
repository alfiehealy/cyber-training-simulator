
from __future__ import annotations
import json, random
from pathlib import Path
from typing import List
from models import Scenario, Choice

SCENARIOS_JSON = Path("scenarios.json")

def load_scenarios()->List[Scenario]:
    def cast(o)->Scenario:
        return Scenario(
            id=o["id"], title=o["title"], category=o["category"], difficulty=o["difficulty"],
            narrative=o["narrative"],
            choices=[Choice(c["label"], c.get("weight",0)) for c in o["choices"]],
            correct_indexes=o["correct_indexes"],
            partial_indexes=o.get("partial_indexes", []),
            unsafe_penalty=o.get("unsafe_penalty", 0),
            hint=o.get("hint",""), feedback_why=o.get("feedback_why",""),
            pro_tip=o.get("pro_tip",""), references=o.get("references", []),
        )
    try:
        data = json.loads(SCENARIOS_JSON.read_text(encoding="utf-8"))
        sc = [cast(o) for o in data]
    except Exception:
        sc = []
    good = []
    for s in sc:
        if not s.validate():
            good.append(s)
    random.shuffle(good)
    return good
