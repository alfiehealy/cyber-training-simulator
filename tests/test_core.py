
import unittest
from models import GameSettings, Scenario, Choice
from game import compute_score, pick_round_seconds

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.settings = GameSettings()
        self.scenario = Scenario(
            id="t", title="t", category="Phishing", difficulty="easy",
            narrative="n", choices=[Choice("a",0), Choice("b",0), Choice("c",0)],
            correct_indexes=[1], partial_indexes=[2], unsafe_penalty=-25
        )

    def test_correct_scoring(self):
        pts, outcome = compute_score(self.settings, self.scenario, 1, 30, streak=2)
        self.assertTrue(pts >= 100)
        self.assertEqual(outcome, "Correct")

    def test_partial(self):
        pts, outcome = compute_score(self.settings, self.scenario, 2, 10, 0)
        self.assertEqual(outcome, "Partial")
        self.assertEqual(pts, 50)

    def test_unsafe(self):
        pts, outcome = compute_score(self.settings, self.scenario, 0, 0, 0)
        self.assertEqual(outcome, "Unsafe")
        self.assertEqual(pts, -25)

    def test_timer_adjust(self):
        self.settings.difficulty = "hard"
        self.settings.round_seconds = 45
        self.assertEqual(pick_round_seconds(self.settings), 35)

if __name__ == "__main__":
    unittest.main()
