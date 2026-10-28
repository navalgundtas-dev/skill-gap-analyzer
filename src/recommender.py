import csv

from src.normaliser import clean, SKILLS_FILE


def load_prerequisites(path=SKILLS_FILE):
    """Build {skill: [prerequisite skills]} from skills.csv."""
    prereqs = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            skill = clean(row["skill"])
            prereqs[skill] = [clean(p) for p in row["prerequisites"].split(";") if p.strip()]
    return prereqs


PREREQS = load_prerequisites()


def _dependents(gaps, prereqs):
    """For each gap skill, which other gap skills list it as a prerequisite."""
    deps = {s: set() for s in gaps}
    for s in gaps:
        for p in prereqs.get(s, []):
            if p in gaps:
                deps[p].add(s)
    return deps


def _all_unlocked(skill, deps):
    """Every gap skill that depends on this one, directly or indirectly."""
    seen, stack = set(), list(deps[skill])
    while stack:
        s = stack.pop()
        if s not in seen:
            seen.add(s)
            stack.extend(deps[s])
    seen.discard(skill)
    return seen


def _reason(gap, unlocked):
    text = (f"You are at level {gap['have']}; this role needs level {gap['need']} "
            f"(importance {gap['weight']}/5).")
    if unlocked:
        text += " Learning it first also unlocks: " + ", ".join(sorted(unlocked)) + "."
    return text


def build_learning_path(breakdown, prereqs=None):
    """Turn a gap breakdown into an ordered learning path with reasons."""
    prereqs = PREREQS if prereqs is None else prereqs
    gaps = {b["skill"]: b for b in breakdown if b["shortfall"] > 0}
    deps = _dependents(gaps, prereqs)

    unlocks, priority = {}, {}
    for s in gaps:
        unlocked = _all_unlocked(s, deps)
        unlocks[s] = unlocked
        priority[s] = gaps[s]["weighted_shortfall"] + sum(
            gaps[u]["weighted_shortfall"] for u in unlocked)

    path, placed, remaining = [], set(), set(gaps)
    while remaining:
        ready = [s for s in sorted(remaining)
                 if all(p in placed or p not in gaps for p in prereqs.get(s, []))]
        if not ready:  # circular prerequisites in the data: fall back gracefully
            ready = sorted(remaining)
        best = max(ready, key=lambda s: (priority[s], gaps[s]["weight"]))
        path.append({
            "step": len(path) + 1,
            "skill": best,
            "have": gaps[best]["have"],
            "need": gaps[best]["need"],
            "weight": gaps[best]["weight"],
            "priority": priority[best],
            "unlocks": sorted(unlocks[best]),
            "reason": _reason(gaps[best], unlocks[best]),
        })
        placed.add(best)
        remaining.remove(best)
    return path