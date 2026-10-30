from src.batch import summarise

ROLES = {"R": {"role": "R", "required": [
    {"skill": "python", "min_level": 3, "weight": 5}]}}


def test_average_and_common_gaps():
    students = [
        {"name": "A", "target_role": "R", "skills": {}},
        {"name": "B", "target_role": "R", "skills": {"python": 3}},
    ]
    out = summarise(students, ROLES)
    assert out["average_readiness"] == 50.0
    assert out["common_gaps"][0]["skill"] == "python"
    assert out["common_gaps"][0]["students_with_gap"] == 1


def test_unknown_role_is_skipped_not_crashed():
    out = summarise([{"name": "C", "target_role": "Wizard", "skills": {}}], ROLES)
    assert out["student_count"] == 0
    assert out["skipped"] == ["C"]