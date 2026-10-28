from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.normaliser import SYNONYM_MAP, clean, normalise



_variants = sorted(SYNONYM_MAP)
_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
_matrix = _vectorizer.fit_transform(_variants)


ACCEPT = 0.75   # starting guesses: tune them with try_fuzzy.py
ASK = 0.5


def match_skill(text, accept=ACCEPT, ask=ASK):
    """Exact lookup, then fuzzy. Returns a dict, or None if nothing is close."""
    exact = normalise(text)
    if exact is not None:
        return {"skill": exact, "score": 1.0, "method": "exact"}

    scores = cosine_similarity(_vectorizer.transform([clean(text)]), _matrix)[0]
    best = scores.argmax()
    score = round(float(scores[best]), 2)
    skill = SYNONYM_MAP[_variants[best]]

    if score >= accept:
        return {"skill": skill, "score": score, "method": "fuzzy"}
    if score >= ask:
        return {"skill": skill, "score": score, "method": "confirm"}
    return None