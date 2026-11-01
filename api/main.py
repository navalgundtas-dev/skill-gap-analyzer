from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi import File, UploadFile
from src.resume_parser import extract_text, find_skills 

from src.gap_engine import compute_gap, load_roles
from src.recommender import build_learning_path

import json
from pathlib import Path

from src.batch import summarise

STUDENTS_FILE = Path(__file__).resolve().parent.parent / "data" / "students.json"

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

@app.get("/batch-summary")
def batch_summary():
    """Mentor view: score all synthetic students and list the most common gaps."""
    with open(STUDENTS_FILE, encoding="utf-8") as f:
        students = json.load(f)
    return summarise(students, ROLES)

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Find claimed skills in a PDF resume. Levels are set to 1 until confirmed."""
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported")
    try:
        text = extract_text(file.file)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read this PDF")
    if not text.strip():
        raise HTTPException(status_code=422,
                            detail="No text found. Scanned PDFs are not supported")
    skills = find_skills(text)
    return {
        "skills_found": skills,
        "suggested_levels": {s: 1 for s in skills},
        "note": "Resume parsing detects claimed skills only. Confirm your real level for each.",
    }