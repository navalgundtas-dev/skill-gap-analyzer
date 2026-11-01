import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

LEVEL_NAMES = {1: "Aware", 2: "Beginner", 3: "Practitioner", 4: "Confident", 5: "Expert"}


def load_skill_guides(path=DATA_DIR / "skill_guides.json"):
    """{skill: {"what": str, "levels": {"1": {learn, build, hours}, ...}}}"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_role_guides(path=DATA_DIR / "role_guides.json"):
    """{role name: {summary, employers_expect, interview_focus, note}}"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def importance_label(weight):
    """Turn a role weight (1 to 5) into plain words."""
    if weight >= 5:
        return "Critical"
    if weight == 4:
        return "High"
    if weight == 3:
        return "Medium"
    return "Nice to have"


def roadmap_for(skill, have, need, guides):
    """Learning steps for every level between what you have and what the role needs.

    Returns None if there is no guide for the skill.
    """
    guide = guides.get(skill)
    if guide is None:
        return None
    steps = []
    for level in range(have + 1, need + 1):
        data = guide["levels"].get(str(level))
        if data:
            steps.append({"level": level, "name": LEVEL_NAMES[level], **data})
    return {"skill": skill, "what": guide["what"], "steps": steps,
            "total_hours": sum(s["hours"] for s in steps)}


def expected_proof(skill, level, guides):
    """What reaching a level looks like (the 'build this' item), or ''."""
    guide = guides.get(skill)
    if guide is None:
        return ""
    return guide["levels"].get(str(level), {}).get("build", "")