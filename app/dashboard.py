import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.batch import summarise
from src.gap_engine import compute_gap, load_roles
from src.recommender import build_learning_path

st.set_page_config(page_title="Student Skill Gap Analyzer", layout="wide")
ROLES = load_roles()

st.title("Student Skill Gap Analyzer")
view = st.sidebar.radio("View", ["Student", "Mentor"])


def parse_extra(text):
    """Turn 'pythn=3, docker=1' into {'pythn': 3, 'docker': 1}."""
    skills = {}
    for part in text.split(","):
        if "=" in part:
            name, level = part.split("=", 1)
            try:
                skills[name.strip()] = int(level)
            except ValueError:
                pass
    return skills


if view == "Student":
    role_name = st.selectbox("Target role", list(ROLES))
    role = ROLES[role_name]

    st.subheader("Rate your honest level (0 = none, 1 = heard of it, 3 = built something, 5 = can teach it)")
    cols = st.columns(3)
    raw = {}
    for i, req in enumerate(role["required"]):
        with cols[i % 3]:
            level = st.slider(req["skill"], 0, 5, 0, key=req["skill"])
            if level > 0:
                raw[req["skill"]] = level

    extra = st.text_input("Other skills, typed freely (example: pythn=3, postgre sql=2)")
    raw.update(parse_extra(extra))

    result = compute_gap(raw, role)
    st.divider()
    left, right = st.columns([1, 2])
    with left:
        st.metric("Readiness", f"{result['readiness']}%")
        st.progress(int(result["readiness"]) / 100)
        st.caption(f"Weighted gap {result['weighted_gap']} of {result['max_gap']}")
    with right:
        st.subheader("Gap breakdown")
        st.dataframe(pd.DataFrame(result["breakdown"]), use_container_width=True,
                     hide_index=True)

    for item in result["to_confirm"]:
        st.warning(f"Did you mean **{item['suggestion']}** when you typed "
                   f"'{item['typed']}'? Not counted until you confirm "
                   f"(match score {item['score']}).")
    if result["unrecognised"]:
        st.info("Not recognised: " + ", ".join(result["unrecognised"]))

    st.subheader("Your learning path")
    path = build_learning_path(result["breakdown"])
    if not path:
        st.success("No gaps for this role.")
    for step in path:
        st.markdown(f"**{step['step']}. {step['skill']}**: {step['reason']}")

else:
    st.subheader("Mentor view: batch of synthetic students")
    with open(ROOT / "data" / "students.json", encoding="utf-8") as f:
        students = json.load(f)
    summary = summarise(students, ROLES)

    c1, c2 = st.columns(2)
    c1.metric("Students", summary["student_count"])
    c2.metric("Average readiness", f"{summary['average_readiness']}%")

    st.subheader("Most common gaps")
    gaps = pd.DataFrame(summary["common_gaps"])
    if not gaps.empty:
        st.bar_chart(gaps.set_index("skill")["students_with_gap"])
        st.dataframe(gaps, use_container_width=True, hide_index=True)

    st.subheader("All students")
    st.dataframe(pd.DataFrame(summary["students"]), use_container_width=True,
                 hide_index=True)