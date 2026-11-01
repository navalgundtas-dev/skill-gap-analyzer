# Student Skill Gap Analyzer

An explainable system that compares a student's honest skill levels with what job roles require, shows the gap, and gives a prioritised, step-by-step learning roadmap.

Built for the AKHYAN Level 2 Internship, Project 04: *AI-Based Student Skill Gap Analysis System*.

> **Status:** working prototype. The student quest, job description quest, resume upload, login, mentor class view and REST API are implemented and tested.

---

## 1. Problem Definition

### The situation
Many students have limited exposure to what companies actually hire for. They do not know which skills are in demand, which topics interviews cover, or how important fundamentals such as DSA and aptitude are. Placement guidance often arrives late and is generic ("practice DSA"), without showing a student where they personally stand.

### The problem
1. **Thin resumes.** Students often list few real skills, sometimes none that match a role.
2. **Fake skills to pass ATS.** To get past Applicant Tracking Systems, students copy skills from job descriptions that they do not actually have.
3. **Interview failure.** The gap between the resume and real ability appears in the interview, where the student gets stuck.
4. **No personal roadmap.** Students cannot tell what to learn first, why it matters, or how far they are from a target role.
5. **No batch view for mentors.** Placement officers cannot easily see which skills are weak across a whole batch.

### The solution
A system that:
- records a student's skills with an **honest proficiency level** (not just a skill name),
- compares them with the **required skills, minimum levels and importance weights** of a target role,
- computes a **readiness score** with a per-skill breakdown,
- explains **what the industry expects** from the role and how important each skill is,
- produces a **learning roadmap** ordered by impact, with topics, a project to build and an hours estimate for every missing level,
- gives mentors a **class view** of common gaps.

### Users
| User | Need |
|---|---|
| **Student** | Know where I stand for a role, what to learn first, why, and exactly what to study |
| **Mentor / placement officer** | See common skill gaps across students and plan training |

### User stories
- As a student, I want to pick a target role and see my readiness score so that I know how far I am from it.
- As a student, I want my skills recorded with a level (not only a name) so that I know what I can honestly defend in an interview.
- As a student, I want to know how important each skill is in the industry so that I spend my time on what matters.
- As a student, I want to know exactly what to learn at each level (topics and a project) so that I am not just told to "learn machine learning".
- As a student, I want to upload my resume so that my skills are filled in without typing them all.
- As a mentor, I want to see the most common gaps across a batch so that I can plan training sessions.

---

## 2. Scope

### In scope
- Skill and level model (0 to 5 scale)
- Role model with required skills, minimum levels and weights
- Weighted gap scoring and readiness percentage
- Skill matching: synonym map, then fuzzy (TF-IDF) matching with a "confirm" step
- Learning path recommender with prerequisites and explanations
- Industry guide per role and a level-by-level learning guide per skill
- Resume parsing (PDF text extraction, claimed skills only)
- Job descriptions: collected manually from public career pages, or pasted by the user
- Basic login with student and mentor roles
- REST API and a gamified Streamlit dashboard
- Evaluation metrics, automated tests and documentation

### Out of scope
- Mobile app
- Any guarantee of placement or interview outcomes

### Scope notes
- Resume parsing is PDF-only and reads text, not layout. It detects *claimed* skills and sets them to level 1, because a resume cannot prove a level.
- The system does not scrape job sites, because most forbid it in their terms of service. Job descriptions are collected by hand from public pages or pasted by the user.
- Login is basic (hashed passwords, two roles) and is not intended for production use.

---

## 3. How It Works

```
Typed skills / resume PDF / pasted job description
        |
        v
Skill matching   (synonym map -> TF-IDF fuzzy match -> accept / confirm / reject)
        |
        v
Gap engine       (weighted gap score, readiness %)
        |
        v
Recommender      (prerequisite-aware learning path with reasons)
        |
        v
Guides           (industry expectations, topics and projects per level)
        |
        v
FastAPI backend  and  Streamlit dashboard (student view, mentor view)
```

See `docs/architecture.md` for the diagram.

### Skill and level format
A student is a mapping of skill name to level on a 0 to 5 scale:

| Level | Meaning |
|---|---|
| 0 | No knowledge |
| 1 | Heard of it |
| 2 | Followed tutorials |
| 3 | Built something with it |
| 4 | Can build alone |
| 5 | Can teach it |

### Role format
A role is a list of required skills, each with a `min_level` and a `weight` (importance from 1 to 5). Each role file also records its `sources` and `notes`, including which parts are judgment calls.

### Gap score
For each required skill:

```
shortfall = max(0, min_level - student_level)
weighted_shortfall = shortfall x weight
```

```
weighted_gap     = sum of weighted_shortfall over all required skills
max_possible_gap = sum of (min_level x weight) over all required skills
readiness %      = 100 - (weighted_gap / max_possible_gap x 100)
```

Worked example: Python (needs 3, has 3, weight 5), SQL (needs 3, has 2, weight 4), Git (needs 2, has 0, weight 2) gives a weighted gap of 8, a maximum of 31, and readiness of about 74%.

Because shortfall is multiplied by weight, a skill with a high minimum level (such as DSA, level 3) can outrank a more important skill with a low minimum level (such as cloud basics, level 1). This is intended: the score reflects how much effort a gap represents.

### Skill matching
1. Clean the text (lowercase, trim).
2. Look it up in the synonym dictionary (for example, "PostgreSQL" maps to "sql").
3. If not found, use TF-IDF fuzzy matching against known skills. The match score decides the outcome:
   - **0.75 or above:** accepted and counted.
   - **0.5 to 0.75:** not counted; the student is asked to confirm.
   - **Below 0.5:** rejected and listed as unrecognised.

Why uncertain matches are not scored: this tool exists to stop inflated skills, so a silent wrong match is worse than a skill waiting for confirmation.

### Learning path rule
1. Each skill is scored by its own weighted gap plus the gaps of the skills it unlocks (skills that list it as a prerequisite).
2. Skills are placed from highest score to lowest.
3. A skill is placed only after all its prerequisites.
4. Ties are broken by higher role weight first, then alphabetically (only so results are the same every run).
5. Every item carries a reason, for example: *"You are at level 0; this role needs level 2 (importance 4/5). Learning it first also unlocks: system design."*

### Industry guides and the full roadmap
- `data/role_guides.json`: for each role, what employers expect from a fresher and what interviews focus on.
- `data/skill_guides.json`: for each skill and each level (1 to 4), the topics to learn, a project to build as proof, and a rough hours estimate.
- The dashboard shows only the levels the student is missing, for example going from level 1 to level 3 in Python shows the level 2 and level 3 steps.
- Importance comes from role weights, which were counted from the job postings collected for that role. Roles marked provisional use estimated weights, and the dashboard says so.

---

## 4. Data

| Role | Basis |
|---|---|
| Backend Developer | 3 public postings (TLC via Jobsora, Whitetable via Hirist, Dentsuaegis via NextRaise) |
| Data Analyst | 3 public postings (Euromonitor read in full; Bytemetrics and Jobaaj partly read) |
| QA / Software Tester | 1 posting (VyomWorld), provisional |
| Software Engineer | 1 posting (Honeywell), provisional |
| ML Engineer | Author's estimate, no postings read yet, provisional |

- **Skills:** 18 canonical skills in `data/skills.csv`, each with synonyms and prerequisites.
- **Students:** 20 synthetic profiles in `data/students.json`, generated by `make_students.py` with a fixed random seed.
- **Resumes:** `docs/sample_resume.pdf` is a fictional resume. Only the author's own or explicitly consented resumes are used for testing.

No private or personal data of other people is used.

---

## 5. Tech Stack

Python, FastAPI, Streamlit, scikit-learn (TF-IDF), pandas, pdfplumber, SQLite, bcrypt, pytest.

---

## 6. Project Structure

```
skill-gap-analyzer/
  data/        skills.csv, roles*.json, skill_guides.json, role_guides.json, students.json
  src/         normaliser, fuzzy_matcher, gap_engine, recommender, guides,
               resume_parser, jd_parser, batch, auth
  api/         main.py (FastAPI)
  app/         dashboard.py (Streamlit)
  tests/       unit and API tests
  docs/        design note, architecture diagram, screenshots
  evaluate.py  precision and recall of skill extraction
  make_students.py  generates the synthetic students
```

---

## 7. Setup

```bash
git clone https://github.com/navalgundtas-dev/skill-gap-analyzer.git
cd skill-gap-analyzer
python -m venv .venv
# Windows (Git Bash): source .venv/Scripts/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Mac/Linux:           source .venv/bin/activate
pip install -r requirements.txt
```

Run the dashboard:
```bash
streamlit run app/dashboard.py
```

Run the API (interactive docs at `http://127.0.0.1:8000/docs`):
```bash
uvicorn api.main:app --reload
```

Run the tests and the evaluation:
```bash
python -m pytest
python evaluate.py
```

**Accounts:** register a student account from the *Join the quest* tab. To register a mentor account, choose "mentor" and enter the demo mentor code from `src/auth.py`.

---

## 8. Dashboard

| View | For | What it shows |
|---|---|---|
| My quest | Student | Industry expectations for the role, honest-level sliders, resume upload, readiness and level, skill cards, quest map, full roadmap with topics and projects |
| Job description quest | Student | Paste a job description; skills and weights are extracted from it, then the same roadmap |
| Class view | Mentor | Class average, most common gaps, suggested workshop, leaderboard |

---

## 9. API Endpoints

All endpoints return JSON. Interactive documentation is generated at `/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/roles` | List roles and their required skills |
| POST | `/analyse` | Score a student's skills against a role and return the breakdown and learning path |
| GET | `/batch-summary` | Score all synthetic students and return the most common gaps |
| POST | `/parse-resume` | Upload a PDF resume and get the claimed skills (levels set to 1) |

Login is handled in the dashboard through `src/auth.py`, not through the API.

---

## 10. Evaluation

| Metric | Result |
|---|---|
| Samples | 15 hand-labelled resume sentences |
| Precision | 0.95 |
| Recall | 0.87 |
| F1 | 0.91 |

The test set is small, so these numbers show the approach works but are not a guarantee. Precision is higher than recall on purpose: generic synonyms were removed so the parser rarely credits a skill that was not claimed, at the cost of missing some real ones.

Mismatches found (these are the limitations of keyword matching):
- "Developed a REST API using Flask and MySQL": expected python, rest api and sql; found rest api and sql. The tool name "Flask" is not a known synonym, so the language was missed.
- "Solved 200 problems on LeetCode covering arrays and trees": expected dsa; found nothing. The words "LeetCode", "arrays" and "trees" are not synonyms of dsa.
- "Wrote test cases and reported bugs using Jira": expected debugging and software testing; found software testing. Reporting a bug is not the same as debugging, so this label is ambiguous.
---

## 11. Testing

Run `python -m pytest`. The suite has 42 tests (confirm the number with the command) covering:
- skill normalisation and fuzzy matching
- gap scoring, tie-breaking and unrecognised skills
- learning path ordering
- resume and job description parsing, including false-match cases
- batch summary
- login: hashing, duplicate usernames, mentor code, short passwords
- API endpoints, including 404 and 422 errors
- data and guide integrity

---

## 12. Limitations

- Skill levels are self-assessed, so honesty depends on the student. The levels are defined with concrete proof to help, and a short quiz is a future improvement.
- Progress (sliders and ticked topics) is not saved after logout or refresh.
- Only five roles are included. QA / Software Tester and Software Engineer rest on one posting each, and ML Engineer rests on an estimate, so they are provisional.
- Fresher postings are often vague or use generic titles, so some weights are judgment calls. Each role file records its sources and which parts are judgment.
- The learning content and hours estimates are curated by the author from general industry knowledge. They are a guide, not an official standard, and should be reviewed with a mentor.
- Resume parsing works only on text-based PDFs, not scanned images, and detects claimed skills, not real ability.
- Keyword matching can produce false matches on generic words. The synonym "analysis" was removed for this reason, at the cost of missing resumes that use only that word.
- Letter-based fuzzy matching cannot catch spoken variants such as "sequel" for SQL. Thresholds were tuned on about 15 test inputs, so they are reasonable but not proven.
- The prerequisite map is hand-written and incomplete. Prerequisites that are not gaps for a role are ignored.
- Login is a prototype: no session tokens or password reset, and the mentor code is a demo value in the source file.

---

## 13. Future Improvements

- Short skill-verification quizzes to replace self-rating
- Saved progress, streaks and reminders
- More roles, each counted from more postings
- Project ideas linked to missing skills
- Year-wise roadmap from the first year of college

---

## 14. Safety and Data Notes

- Synthetic or consented data only.
- Passwords are stored as bcrypt hashes, never in plain text. The user database (`data/users.db`) is not committed to the repository.
- Educational prototype, not a production hiring tool.

---

## 15. Author

Tasmiya Navalgund, B.E. Computer Science and Engineering, KLE Institute of Technology, Hubballi.