# Student Skill Gap Analyzer 🚀

An AI/ML-driven platform designed to help Tier 2 and Tier 3 college students identify technical skill gaps, clean up resume inconsistencies, and generate personalized, high-priority learning paths to clear engineering interviews.

## 🏗️ Project Architecture Layout

```text
[Streamlit Frontend Dashboard] 
       │      ▲
(JSON) │      │ (JSON Response)
       ▼      │
[ FastAPI Backend Endpoints ]
       │      ▲
       ▼      │
[ Core Matcher & Analytics Engine ] ◄─── Reads ─── [ data/ ]
  - Synonym Resolver (Dictionary + TF-IDF)
  - Gap Calculator (Shortfall × Weight)
  - Prioritized Learning Path Sequencer
```

## 🛠️ Tech Stack & Environment
* **Backend:** FastAPI (Python)
* **Frontend:** Streamlit Dashboard
* **ML/Analytics:** Scikit-Learn (TF-IDF Matching), Pandas
* **Testing:** Pytest

## 📂 Core Project Design
The complete functional guidelines, definitions of done, out-of-scope criteria, and mathematical gap formulas are documented in detail inside the [Design Note Document](docs/design-note.md).
