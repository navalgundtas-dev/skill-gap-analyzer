
# Student Skill Gap Analyzer

An explainable system that compares a student's real skill levels with what job roles require, shows the gap, and recommends a prioritised learning path.

---

## 1. Problem Definition

### The situation
Many students have limited exposure to what companies actually hire for. They do not know which skills are in demand, which topics interviews cover, or how important fundamentals such as DSA and aptitude are. Placement guidance often arrives late and is generic ("practice DSA"), without showing a student where they personally stand.

### The problem
1. **Thin resumes**. Students often list few real skills, sometimes none that match a role.
2. **Fake skills to pass ATS.** To get past Applicant Tracking Systems, students copy skills from job descriptions that they do not actually have.
3. **Interview failure.** The gap between the resume and real ability appears in the interview, where the student gets stuck.
4. **No personal roadmap.** Students cannot tell what to learn first, why it matters, or how far they are from a target role.
5. **No batch view for mentors.** Placement officers cannot easily see which skills are weak across a whole batch.

### The solution
A system that:
- records a student's skills with an **honest proficiency level** (not just a skill name),
- compares them with the **required skills, minimum levels and importance weights** of a target role,
- computes a **readiness score** with a per-skill breakdown,
- produces a **learning path** ordered by impact, with a plain-language reason for every recommendation,
- gives mentors a **batch summary** of common gaps.
### Users

| User | Need |
|---|---|
| **Student** | Know where I stand for a role, what to learn first, and why |
| **Mentor / placement officer** | See common skill gaps across students and plan training |


### User stories
- As a student, I want to pick a target role and see my readiness score so that I know how far I am from it.
- As a student, I want my skills recorded with a level (not only a name) so that I know what I can honestly defend in an interview.
- As a student, I want each recommendation to come with a reason so that I understand why DSA, SQL or any other skill matters for my role.
- As a student, I want to upload my resume so that my skills are filled in without typing them all.
- As a mentor, I want to see the most common gaps across a batch so that I can plan training sessions.


## 2. Scope

### In scope
- Skill and level model (0 to 5 scale)
- Role model with required skills, minimum levels and weights
- Weighted gap scoring and readiness percentage
- Skill normalisation (synonym map, then fuzzy matching)
- Learning path recommender with prerequisites and explanations
- Resume parsing (PDF text extraction)
- Real job description data (collected manually from public career pages, or pasted by the user)
- Basic login with student and mentor roles
- REST API and Streamlit dashboard
- Evaluation metrics, unit tests and documentation

### Out of scope
- Mobile app
- Any guarantee of placement or interview outcomes

### Scope notes
- Resume parsing is PDF-only and uses text extraction, not layout understanding.
- Job descriptions are collected manually from public sources or pasted by the user. The system does not scrape job sites, because most forbid it in their terms of service.
- Login is basic (hashed passwords, two roles) and is not intended for production use.



## 3. How It Works

```
Resume PDF / typed skills / pasted job description
        |
        v
Skill extraction and normalisation   (synonym map -> fuzzy matching)
        |
        v
Matching engine                      (weighted gap score, readiness %)
        |
        v
Recommender                          (prerequisite-aware learning path + reasons)
        |
        v
FastAPI backend  -->  Streamlit dashboard (student view, mentor view)
```

### Skill and level format
A student is a mapping of skill name to level on a 0 to 5 scale:

| Level | Meaning |
|---|---|
| 0 | No knowledge |
| 1 | Heard of it |
| 3 | Built something with it |
| 5 | Can teach it |

### Role format
A role is a list of required skills, each with a `min_level` and a `weight` (importance).

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

### Learning path rule
1. Each skill is scored by its own weighted gap plus the gaps of the skills it unlocks (skills that list it as a prerequisite).
2. Skills are placed from highest score to lowest.
3. A skill is placed only after all its prerequisites.
4. Ties are broken by higher role weight first.
5. Every item carries a reason, for example: *"Python: your biggest gap, and Machine Learning requires it."*

### Skill normalisation
1. Clean the text (lowercase, trim).
2. Look it up in the synonym dictionary (for example, "JS" maps to "javascript").
3. If not found, use TF-IDF fuzzy matching against known skills.
4. If still unsure, ask the user to confirm.

---

## 4. Data

- **Roles:** 8 roles, based on public job descriptions collected manually.
- **Skills:** about 40 canonical skills with synonyms and prerequisites.
- **Students:** 20 synthetic student profiles.
- **Resumes:** only the author's own or explicitly consented resumes are used for testing.

No private or personal data of other people is used.

---

## 5. Tech Stack

Python, FastAPI, Streamlit, scikit-learn (TF-IDF), pandas, pdfplumber, SQLite, bcrypt, pytest.

---

## 6. Project Structure

```
skill-gap-analyzer/
  data/        roles, skills, synonyms, synthetic students
  src/         normaliser, gap engine, recommender, resume parser
  api/         FastAPI application
  app/         Streamlit dashboard
  tests/       unit and API tests
  docs/        design note, architecture diagram, screenshots
```

---

## 7. Setup *(to be filled and tested on Day 3)*

```bash
git clone <repo-url>
cd skill-gap-analyzer
python -m venv venv
# Windows: venv\Scripts\activate    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# run the API
uvicorn api.main:app --reload

# run the dashboard (new terminal)
streamlit run app/dashboard.py

# run the tests
pytest
```

Goal: a new user can run the project in under 10 minutes.

---

## 8. API Endpoints *(to be filled)*

At least three endpoints, all returning valid JSON:
- Analyse one student against a role
- List roles and their required skills
- Batch summary of common gaps (mentor)

Plus login and resume upload endpoints.

---

## 9. Evaluation *(to be filled)*

- Precision and recall of skill extraction on about 20 hand-labelled text samples
- Sanity tests: a student with all required skills scores about 100%, and one with none scores about 0%
- Check that higher-weight gaps are ranked first in the learning path
- Ablation: synonym map alone versus synonym map plus fuzzy matching

---

## 10. Testing *(to be filled)*

At least 8 passing unit tests covering scoring, normalisation, tie-breaking, prerequisite ordering and the API.

---

## 11. Limitations *(to be filled and kept honest)*

Expected limitations include:
- Skill levels are self-assessed, so honesty depends on the student. A short quiz is a future improvement.
- The role data covers only 8 roles and may not represent every company.
- Resume parsing works only on text-based PDFs, not scanned images.
- The prerequisite map is hand-written and incomplete.
- Fuzzy matching can produce wrong guesses on rare skills.

---

## 12. Future Improvements

- Short skill-verification quizzes to replace self-rating
- Project ideas linked to missing skills
- Year-wise roadmap from the first year of college
- Progress tracking over time

---

## 13. Safety and Data Notes

- Synthetic or consented data only.
- Passwords are stored hashed, never in plain text.
- Educational prototype, not a production hiring tool.

---

## 14. Author

Tasmiya Navalgund, B.E. Computer Science and Engineering, KLE Institute of Technology, Hubballi.
