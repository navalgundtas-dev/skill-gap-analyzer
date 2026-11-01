from src.jd_parser import role_from_jd


def test_repeated_skill_gets_higher_weight():
    role = role_from_jd("We need Python. Python and SQL. Python again.")
    weights = {r["skill"]: r["weight"] for r in role["required"]}
    assert weights["python"] == 5
    assert weights["sql"] == 3


def test_text_without_known_skills_gives_empty_role():
    assert role_from_jd("We love teamwork and coffee")["required"] == []