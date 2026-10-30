from src.fuzzy_matcher import match_skill


def test_exact_match_uses_dictionary():
    assert match_skill("PostgreSQL")["method"] == "exact"


def test_typo_is_matched_fuzzily():
    result = match_skill("machin learning")
    assert result["skill"] == "machine learning"
    assert result["method"] == "fuzzy"


def test_nonsense_returns_none():
    assert match_skill("underwater basket weaving") is None