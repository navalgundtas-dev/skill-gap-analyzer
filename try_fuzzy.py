from src.fuzzy_matcher import match_skill

for text in ["Pythn", "postgre sql", "PostgreSQL", "Javascript",
             "underwater basket weaving", "machin learning", "github", "java", "react", "c", "r", "sqlite", "excell", "sequel", "pyton3"]:
    print(f"{text!r:32} -> {match_skill(text)}")