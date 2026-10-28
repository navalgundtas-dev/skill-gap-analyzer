from src.gap_engine import compute_gap

ROLE = {
    "role": "Test Role",
    "required": [
        {"skill": "python", "min_level": 3, "weight": 5},
        {"skill": "sql", "min_level": 3, "weight": 4},
        {"skill": "git", "min_level": 2, "weight": 2},
    ],
}


def test_all_skills_gives_full_readiness():
    result = compute_gap({"python": 3, "sql": 3, "git": 2}, ROLE)
    assert result["readiness"] == 100.0


def test_no_skills_gives_zero_readiness():
    result = compute_gap({}, ROLE)
    assert result["readiness"] == 0.0


def test_worked_example_from_design_note():
    # python 3/3, sql 2/3, git 0/2 -> weighted gap 8, max 31, readiness 74.2
    result = compute_gap({"python": 3, "sql": 2, "git": 0}, ROLE)
    assert result["weighted_gap"] == 8
    assert result["max_gap"] == 31
    assert result["readiness"] == 74.2


def test_synonym_is_recognised():
    result = compute_gap({"PostgreSQL": 3, "py": 3, "github": 2}, ROLE)
    assert result["readiness"] == 100.0

def test_unrecognised_skill_is_reported():
    result = compute_gap({"underwater basket weaving": 3}, ROLE)
    assert "underwater basket weaving" in result["unrecognised"]
    assert result["readiness"] == 0.0

def test_tie_break_prefers_higher_weight():
    role = {
        "role": "Tie Role",
        "required": [
            {"skill": "git", "min_level": 2, "weight": 2},
            {"skill": "python", "min_level": 1, "weight": 4},
        ],
    }
    result = compute_gap({}, role)
    # git:    shortfall 2 x weight 2 = 4
    # python: shortfall 1 x weight 4 = 4  (same score, higher weight)
    assert result["breakdown"][0]["skill"] == "python"


def test_confident_typo_counts_toward_score():
    role = {"role": "T", "required": [
        {"skill": "machine learning", "min_level": 3, "weight": 5}]}
    result = compute_gap({"machin learning": 3}, role)
    assert result["readiness"] == 100.0

def test_uncertain_match_is_flagged_not_scored():
    role = {"role": "T", "required": [
        {"skill": "python", "min_level": 3, "weight": 5}]}
    result = compute_gap({"Pythn": 3}, role)
    assert result["readiness"] == 0.0
    assert result["to_confirm"][0]["suggestion"] == "python"