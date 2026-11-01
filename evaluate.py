from src.resume_parser import find_skills

# (text, skills a human says are really claimed). Add more until you have 15 to 20.
SAMPLES = [
    ("Skills: Python, PostgreSQL, Git, REST API", {"python", "sql", "git", "rest api"}),
    ("Built reports in Power BI and used Excel", {"data visualization", "excel"}),
    ("Familiar with Docker and AWS deployments", {"docker", "cloud basics"}),
    ("Manual testing, test cases and debugging", {"software testing", "debugging"}),
    ("Studied algorithms and data structures", {"dsa"}),
    ("Machine learning projects using Python", {"machine learning", "python"}),
    ("I enjoy hiking and photography", set()),
    ("financial analysis of the market", set()),
    ("shipping containers at the port", set()),
]

tp = fp = fn = 0
for text, expected in SAMPLES:
    found = set(find_skills(text))
    tp += len(found & expected)
    fp += len(found - expected)
    fn += len(expected - found)
    if found != expected:
        print(f"MISMATCH: {text!r}\n   expected {sorted(expected)}\n   found    {sorted(found)}")

precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
print(f"\nSamples: {len(SAMPLES)}  Precision: {precision:.2f}  Recall: {recall:.2f}  F1: {f1:.2f}")