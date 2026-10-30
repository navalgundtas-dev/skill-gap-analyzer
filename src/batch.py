from collections import defaultdict

from src.gap_engine import compute_gap


def summarise(students, roles, top_n=10):
    """Score every student and find the most common skill gaps."""
    results, skipped = [], []
    gaps = defaultdict(lambda: {"students_with_gap": 0, "total_weighted_shortfall": 0})

    for s in students:
        role = roles.get(s["target_role"])
        if role is None:
            skipped.append(s["name"])
            continue
        r = compute_gap(s["skills"], role)
        results.append({"name": s["name"], "target_role": s["target_role"],
                        "readiness": r["readiness"]})
        for b in r["breakdown"]:
            if b["shortfall"] > 0:
                gaps[b["skill"]]["students_with_gap"] += 1
                gaps[b["skill"]]["total_weighted_shortfall"] += b["weighted_shortfall"]

    common = sorted(
        ({"skill": k, **v} for k, v in gaps.items()),
        key=lambda g: (-g["students_with_gap"], -g["total_weighted_shortfall"], g["skill"]),
    )[:top_n]
    average = round(sum(r["readiness"] for r in results) / len(results), 1) if results else 0.0

    return {"student_count": len(results), "average_readiness": average,
            "common_gaps": common, "students": results, "skipped": skipped}