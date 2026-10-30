import json
import random
from pathlib import Path

from src.gap_engine import load_roles

random.seed(42)  # same students every run

ROOT = Path(__file__).resolve().parent
roles = list(load_roles().values())

# (chance of having each required skill, level shift vs the role's minimum)
PROFILES = {"strong": (0.9, 1), "average": (0.55, 0), "weak": (0.2, -1)}
TYPOS = {"python": "pythn", "machine learning": "machin learning", "sql": "postgre sql"}

students = []
for i in range(1, 21):
    role = random.choice(roles)
    profile = random.choice(list(PROFILES))
    keep_prob, shift = PROFILES[profile]
    skills = {}
    for req in role["required"]:
        if random.random() < keep_prob:
            level = req["min_level"] + shift + random.choice([-1, 0, 0, 1])
            name = req["skill"]
            if name in TYPOS and random.random() < 0.15:
                name = TYPOS[name]  # some students mistype, to exercise fuzzy matching
            skills[name] = max(1, min(5, level))
    students.append({"name": f"Student {i:02d}",
                     "target_role": role["role"],
                     "skills": skills})

with open(ROOT / "data" / "students.json", "w", encoding="utf-8") as f:
    json.dump(students, f, indent=2)
print(f"Wrote {len(students)} synthetic students")