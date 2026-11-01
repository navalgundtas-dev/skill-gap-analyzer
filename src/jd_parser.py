import re
from collections import Counter

from src.normaliser import SYNONYM_MAP, clean


def count_skills(text):
    """Count how often each known skill (or a synonym) appears in the text."""
    text = clean(text)
    counts = Counter()
    for variant, canonical in SYNONYM_MAP.items():
        pattern = r"(?<![a-z0-9])" + re.escape(variant) + r"(?![a-z0-9])"
        counts[canonical] += len(re.findall(pattern, text))
    return {skill: n for skill, n in counts.items() if n > 0}


def role_from_jd(text, title="Pasted role"):
    """Build a temporary role. Weight: 1 mention = 3, 2 mentions = 4, 3 or more = 5."""
    required = [
        {"skill": skill, "min_level": 2, "weight": min(5, 2 + n)}
        for skill, n in sorted(count_skills(text).items())
    ]
    return {"role": title, "required": required,
            "sources": ["Pasted by user"],
            "notes": "Weights come from how often a skill appears. Minimum level is 2 for all skills."}