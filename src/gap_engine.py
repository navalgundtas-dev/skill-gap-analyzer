import json
from pathlib import Path

from src.normaliser import normalise

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_roles(data_dir=DATA_DIR):
    """Load every roles*.json file into {role_name: role_dict}."""
    roles = {}
    for path in sorted(data_dir.glob("roles*.json")):
        with open(path, encoding="utf-8") as f:
            role = json.load(f)
        roles[role["role"]] = role
    return roles


def clean_student_skills(raw_skills):
    """Normalise skill names. Returns (known, unrecognised).

    If two names map to the same skill (e.g. 'JS' and 'JavaScript'),
    keep the higher level.
    """
    known, unrecognised = {}, []
    for name, level in raw_skills.items():
        if not 0 <= level <= 5:
            raise ValueError(f"Level for '{name}' must be 0-5, got {level}")
        canonical = normalise(name)
        if canonical is None:
            unrecognised.append(name)
        else:
            known[canonical] = max(level, known.get(canonical, 0))
    return known, unrecognised


def compute_gap(raw_skills, role):
    """Compare a student's skills with a role.

    Returns readiness %, totals, a per-skill breakdown (biggest weighted
    shortfall first, ties broken by higher weight), and unrecognised skills.
    """
    student, unrecognised = clean_student_skills(raw_skills)

    breakdown = []
    weighted_gap = 0
    max_gap = 0
    for req in role["required"]:
        have = student.get(req["skill"], 0)
        shortfall = max(0, req["min_level"] - have)
        weighted = shortfall * req["weight"]
        weighted_gap += weighted
        max_gap += req["min_level"] * req["weight"]
        breakdown.append({
            "skill": req["skill"],
            "have": have,
            "need": req["min_level"],
            "weight": req["weight"],
            "shortfall": shortfall,
            "weighted_shortfall": weighted,
        })

    breakdown.sort(key=lambda b: (-b["weighted_shortfall"], -b["weight"]))
    readiness = 100.0 if max_gap == 0 else 100 - (weighted_gap / max_gap * 100)

    return {
        "role": role["role"],
        "readiness": round(readiness, 1),
        "weighted_gap": weighted_gap,
        "max_gap": max_gap,
        "breakdown": breakdown,
        "unrecognised": unrecognised,
    }