from src.resume_parser import find_skills


def test_finds_skills_and_synonyms():
    text = "Skills: Python, PostgreSQL, Git/GitHub. Built REST API projects."
    assert {"python", "sql", "git", "rest api"} <= set(find_skills(text))


def test_whole_word_matching_avoids_partial_matches():
    assert "python" not in find_skills("I enjoy pythonic code style")


def test_unrelated_text_finds_nothing():
    assert find_skills("I enjoy hiking and photography") == []

def test_generic_word_analysis_does_not_match_data_analysis():
    assert "data analysis" not in find_skills("financial analysis of the market")


def test_full_phrase_still_matches():
    assert "data analysis" in find_skills("Experienced in data analysis and reporting")