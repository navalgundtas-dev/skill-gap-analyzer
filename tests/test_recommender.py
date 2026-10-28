from src.recommender import build_learning_path


def make(skill, shortfall, weight=1):
    return {"skill": skill, "have": 0, "need": shortfall, "weight": weight,
            "shortfall": shortfall, "weighted_shortfall": shortfall * weight}


PREREQS = {"machine learning": ["python"]}


def test_prerequisite_comes_first_even_with_smaller_gap():
    breakdown = [make("machine learning", 7), make("sql", 4), make("python", 3)]
    path = build_learning_path(breakdown, PREREQS)
    assert [p["skill"] for p in path] == ["python", "machine learning", "sql"]


def test_skills_without_a_gap_are_excluded():
    breakdown = [make("python", 0), make("sql", 2)]
    path = build_learning_path(breakdown, {})
    assert [p["skill"] for p in path] == ["sql"]