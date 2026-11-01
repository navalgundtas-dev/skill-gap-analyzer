import re

import pdfplumber

from src.normaliser import SYNONYM_MAP, clean


def extract_text(pdf_file):
    """Read all text from a PDF (a path or a file object)."""
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def find_skills(text):
    """Find known skills (and their synonyms) mentioned in free text.

    Whole-word matching, so 'python' is found in 'Python, SQL' but not
    in 'pythonic'. Returns a sorted list of canonical skill names.
    """
    text = clean(text)
    found = set()
    for variant, canonical in SYNONYM_MAP.items():
        pattern = r"(?<![a-z0-9])" + re.escape(variant) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.add(canonical)
    return sorted(found)