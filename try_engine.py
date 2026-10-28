from src.gap_engine import load_roles, compute_gap

roles = load_roles()
print("Roles loaded:", list(roles))

student = {"Python": 3, "PostgreSQL": 2, "git": 0, "Javascript": 2}
r = compute_gap(student, roles["Backend Developer"])

print("Readiness:", r["readiness"])
print("Unrecognised:", r["unrecognised"])
for b in r["breakdown"]:
    print(b)