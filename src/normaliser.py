import csv
from pathlib import Path

SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills.csv"


def clean(text):
    """Lowercase, trim, and collapse repeated spaces."""
    return " ".join(text.lower().strip().split())


def load_synonym_map(path=SKILLS_FILE):
    """Build {variant: canonical_skill} from skills.csv."""
    synonym_map = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            canonical = clean(row["skill"])
            synonym_map[canonical] = canonical  # a skill maps to itself
            for syn in row["synonyms"].split(";"):
                syn = clean(syn)
                if not syn:
                    continue
                if syn in synonym_map and synonym_map[syn] != canonical:
                    print(f"WARNING: '{syn}' maps to both "
                          f"'{synonym_map[syn]}' and '{canonical}'")
                synonym_map[syn] = canonical
    return synonym_map


SYNONYM_MAP = load_synonym_map()


def normalise(skill, synonym_map=None):
    """Return the canonical skill name, or None if unknown."""
    if synonym_map is None:
        synonym_map = SYNONYM_MAP
    return synonym_map.get(clean(skill))