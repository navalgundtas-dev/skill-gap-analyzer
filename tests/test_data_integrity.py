from src.gap_engine import load_roles
from src.normaliser import SYNONYM_MAP
from src.recommender import PREREQS

KNOWN = set(SYNONYM_MAP.values())


def test_every_role_skill_exists_in_skills_csv():
    for role in load_roles().values():
        for req in role["required"]:
            assert req["skill"] in KNOWN, \
                f"{role['role']} needs unknown skill '{req['skill']}'"


def test_every_prerequisite_exists_in_skills_csv():
    for skill, prereqs in PREREQS.items():
        for p in prereqs:
            assert p in KNOWN, f"'{skill}' has unknown prerequisite '{p}'"