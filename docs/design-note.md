# Design Note: Student Skill Gap Analyzer

## Problem Statement
Many tier 2 and tier 3 college students don't know which skills companies demand, so their resumes have few real skills and they copy skills from job descriptions to pass ATS. This creates a gap between what a resume claims and what the student can do, and they get stuck in interviews. This system compares a student's assessed skills with role requirements, shows the gap, and gives a prioritised, explained learning path.

## Out of Scope
Real company or job-portal data, user login/accounts, resume file (PDF/DOCX) parsing, live job-market scraping.

## Definition of Done
1. Dataset has 8 roles, 40 skills and 20 synthetic students.
2. The matcher treats synonyms as one skill (e.g. "JS" = "JavaScript").
3. The API has 3 endpoints, each returning valid JSON.
4. The learning path is ordered by gap size (including the gaps a skill unlocks), prerequisites first.
5. At least 8 unit tests pass, including the all-skills (about 100%) and no-skills (about 0%) checks.
6. Two evaluation metrics are reported (precision and recall of skill extraction).
7. The README lets someone run the project in under 10 minutes.
8. All catalog submission items exist: repo, README, diagram, test evidence, demo recording, limitations, presentation.

## Design Decisions
### 1. Skill and level format
A student is a dictionary of skill name to level on a 0-5 scale (1 = heard of it, 3 = built something with it, 5 = can teach it).

### 2. Role format
A role is a list of required skills, each with a minimum level and a weight (importance).

### 3. Gap score
For each skill, shortfall = max(0, min_level - student_level). Weighted gap = sum of shortfall x weight. Readiness % = 100 - (weighted gap / maximum possible gap x 100). Ties are broken by higher weight first.

### 4. Synonym map
Clean the text (lowercase, trim), then look it up in a synonym dictionary. If not found, use TF-IDF fuzzy matching. If still unsure, ask the student to confirm.
