from src.normaliser import normalise


def test_synonym_maps_to_canonical():
    assert normalise("ML") == "machine learning"


def test_cleans_case_and_spaces():
    assert normalise("  PostgreSQL ") == "sql"


def test_unknown_skill_returns_none():
    assert normalise("underwater basket weaving") is None
    