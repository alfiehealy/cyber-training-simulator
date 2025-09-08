# 🛡️ Cyber Training Simulator (Python + CustomTkinter)

A polished desktop app that turns real-world cyber incidents into an interactive training game.  
Built with **Python 3** and **CustomTkinter**. No internet calls. All data is stored locally.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-CustomTkinter-1f6feb.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](./LICENSE)

Practice secure decision-making across realistic scenarios (phishing, MFA fatigue, tailgating, open ports, AI prompt injection, and more).  
Make a choice, see instant feedback, and review analytics at the end.

---

## ✨ Highlights
- **22+ curated scenarios** across Phishing, Network, Social Engineering, Physical, and Patching/MFA.
- **Scoring** with streak bonus, fast-response bonus, and configurable penalties.
- **Modern UI (CustomTkinter)** — Dark/Light theme toggle, clean cards, toasts, keyboard shortcuts.
- **Analytics**: per-category accuracy bar chart + “Top lessons learned”.
- **Persistence**: profiles, settings, badges, leaderboard, and exportable Markdown reports.
- **Local-only**: data saved to `./data/` with JSON auto-backup on parse errors.

---

## 🚀 Quickstart

```bash
# 1) Optional: create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) Install UI dependency
pip install customtkinter

# 3) Run
python main.py

---

## 📸 Screenshots

Here’s a look at the app in action:

### Start Screen
![Start Screen](docs/screens/start.png)

### Scenario Example
![Scenario Screen](docs/screens/scenario.png)

### Feedback Modal
![Feedback Modal](docs/screens/feedback.png)

### Summary & Analytics
![Summary Screen](docs/screens/summary.png)

### Badges
![Badges Screen](docs/screens/badges.png)
