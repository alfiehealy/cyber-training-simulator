
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

Difficulty = str
Category = str

@dataclass
class Choice:
    label: str
    weight: int = 0  # optional scoring override

@dataclass
class Scenario:
    id: str
    title: str
    category: Category
    difficulty: Difficulty
    narrative: str
    choices: List[Choice]
    correct_indexes: Sequence[int]
    partial_indexes: Sequence[int] = field(default_factory=list)
    unsafe_penalty: int = 0
    hint: str = ""
    feedback_why: str = ""
    pro_tip: str = ""
    references: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        errs: List[str] = []
        if not self.title or not self.choices:
            errs.append(f"{self.id}: missing title/choices")
        if not self.correct_indexes:
            errs.append(f"{self.id}: missing correct indexes")
        n = len(self.choices)
        for ix in list(self.correct_indexes) + list(self.partial_indexes):
            if ix < 0 or ix >= n:
                errs.append(f"{self.id}: bad index {ix}")
        return errs

@dataclass
class GameSettings:
    difficulty: Difficulty = "medium"
    timer_enabled: bool = True
    round_seconds: int = 45
    penalties_enabled: bool = True
    hints_enabled: bool = True
    sound_enabled: bool = False
    high_contrast: bool = False
    font_scale: int = 100
    unsafe_penalty: int = -25
    base_correct: int = 100
    base_partial: int = 50
    skip_penalty: int = -10
    hint_cost: int = -5
    appearance: str = "Dark"   # Dark/Light
    accent: str = "blue"       # blue/green/dark-blue

@dataclass
class Profile:
    name: str = "Player"
    best_score: int = 0
    unlocked_badges: List[str] = field(default_factory=list)
    last_session: Dict = field(default_factory=dict)

@dataclass
class RoundResult:
    scenario_id: str
    selected_index: Optional[int]
    time_taken: float
    gained: int
    outcome: str  # Correct | Partial | Unsafe | Skipped

@dataclass
class GameState:
    rounds_total: int = 10
    current_index: int = 0
    score: int = 0
    streak: int = 0
    results: List[RoundResult] = field(default_factory=list)
    seen_ids: set[str] = field(default_factory=set)

    def progress_fraction(self) -> float:
        return min(1.0, self.current_index / max(1, self.rounds_total))
