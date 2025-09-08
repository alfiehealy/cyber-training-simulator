
from __future__ import annotations
import random
from typing import List, Tuple, Dict
from models import GameSettings, Scenario, RoundResult

def pick_round_seconds(settings: GameSettings) -> int:
    base = settings.round_seconds
    if settings.difficulty == "easy": return base + 10
    if settings.difficulty == "hard": return max(20, base - 10)
    return base

def compute_score(settings: GameSettings, scenario: Scenario, selected:int|None, remaining:int, streak:int)->Tuple[int,str]:
    if selected is None:
        return (settings.skip_penalty if settings.penalties_enabled else 0, "Skipped")
    if selected in scenario.correct_indexes:
        base = scenario.choices[selected].weight or settings.base_correct
        bonus = max(0, min(20, remaining//3)) if settings.timer_enabled else 0
        streak_bonus = 10 if streak>0 and streak%2==0 else 0
        return base + bonus + streak_bonus, "Correct"
    if selected in scenario.partial_indexes:
        return (scenario.choices[selected].weight or settings.base_partial), "Partial"
    penalty = scenario.unsafe_penalty or settings.unsafe_penalty if settings.penalties_enabled else 0
    return penalty, "Unsafe"

def select_scenarios(all_scenarios: List[Scenario], count:int, seen:set[str])->List[Scenario]:
    pool = [s for s in all_scenarios if s.id not in seen]
    random.shuffle(pool)
    if len(pool) < count:
        pool = all_scenarios[:]
        random.shuffle(pool)
    return pool[:count]

def update_badges(profile: Dict, results: List[RoundResult], settings: GameSettings)->None:
    badges = set(profile.get("unlocked_badges", []))
    phish_correct = sum(1 for r in results if r.outcome=="Correct" and r.scenario_id.startswith("phish"))
    if phish_correct >= 5: badges.add("Phish Fryer")
    if all(r.outcome!="Skipped" for r in results): badges.add("Zero Trust")
    if results and (sum(r.time_taken for r in results)/len(results)) < 10: badges.add("Fast Thinker")
    profile["unlocked_badges"] = sorted(badges)
