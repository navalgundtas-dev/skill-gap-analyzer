from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.gap_engine import compute_gap, load_roles
from src.recommender import build_learning_path

app = FastAPI(title="Student Skill Gap Analyzer")
ROLES = load_roles()


class AnalyseRequest(BaseModel):
    role: str
    skills: dict[str, int]  # {"python": 3, "sql": 2}


@app.get("/roles")
def list_roles():
    """List every role and the skills it requires."""
    return [
        {"role": name, "required_skills": [r["skill"] for r in role["required"]]}
        for name, role in ROLES.items()
    ]


@app.post("/analyse")
def analyse(req: AnalyseRequest):
    """Score a student against a role and return a learning path."""
    role = ROLES.get(req.role)
    if role is None:
        raise HTTPException(status_code=404, detail=f"Unknown role: {req.role}")
    try:
        result = compute_gap(req.skills, role)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    result["learning_path"] = build_learning_path(result["breakdown"])
    return result