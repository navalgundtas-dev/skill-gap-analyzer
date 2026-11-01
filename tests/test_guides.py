from src.gap_engine import load_roles
from src.guides import (importance_label, load_role_guides, load_skill_guides,
                        roadmap_for)
from src.normaliser import SYNONYM_MAP

KNOWN = set(SYNONYM_MAP.values())


def test_every_skill_has_a_guide():
    missing = KNOWN - set(load_skill_guides())
    assert not missing, f"skills without a guide: {sorted(missing)}"


def test_every_role_has_a_role_guide():
    guides = load_role_guides()
    for name in load_roles():
        assert name in guides, f"no role guide for '{name}'"


def test_roadmap_covers_only_the_missing_levels():
    road = roadmap_for("python", 1, 3, load_skill_guides())
    assert [s["level"] for s in road["steps"]] == [2, 3]
    assert road["total_hours"] == sum(s["hours"] for s in road["steps"])


def test_no_gap_gives_an_empty_roadmap():
    assert roadmap_for("python", 3, 3, load_skill_guides())["steps"] == []


def test_unknown_skill_has_no_roadmap():
    assert roadmap_for("underwater basket weaving", 0, 3, load_skill_guides()) is None


def test_importance_labels():
    assert importance_label(5) == "Critical"
    assert importance_label(4) == "High"
    assert importance_label(3) == "Medium"
    assert importance_label(2) == "Nice to have"