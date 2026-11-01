"""Skill Gap Analyzer: gamified Streamlit dashboard."""
import html as _html
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.auth import init_db, login, register
from src.batch import summarise
from src.gap_engine import compute_gap, load_roles
from src.jd_parser import role_from_jd
from src.recommender import build_learning_path
from src.resume_parser import extract_text, find_skills

st.set_page_config(page_title="Skill Gap Analyzer", page_icon="🦊", layout="wide")
init_db()
ROLES = load_roles()

MASCOT = "🦊"

EMOJI = {
    "python": "🐍", "sql": "🗄️", "git": "🌿", "docker": "🐳", "dsa": "🧩",
    "rest api": "🔌", "cloud basics": "☁️", "system design": "🏗️",
    "machine learning": "🤖", "excel": "📊", "data visualization": "📈",
    "statistics": "📐", "data analysis": "🔍", "software testing": "🧪",
    "debugging": "🐞", "programming fundamentals": "💻",
    "software engineering principles": "🧱", "code review": "👀",
}

LEVELS = [(0, "Seedling", "🌱"), (25, "Explorer", "🧭"), (50, "Climber", "🧗"),
          (75, "Pro", "🚀"), (90, "Interview Ready", "🏆")]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;800;900&display=swap');
html, body, .stApp, .stApp * { font-family: 'Nunito', sans-serif; }
h1, h2, h3 { font-weight: 900 !important; }
.block-container { padding-top: 2rem; max-width: 1200px; }

div.stButton > button {
  background: #58CC02; color: white; border: none; border-radius: 16px;
  font-weight: 900; padding: 0.6rem 1.4rem; box-shadow: 0 5px 0 #46A302;
  text-transform: uppercase; letter-spacing: 0.5px;
  transition: transform 0.1s, box-shadow 0.1s;
}
div.stButton > button p { color: white; font-weight: 900; }
div.stButton > button:hover { background: #61DA02; color: white; border: none; }
div.stButton > button:active { transform: translateY(4px); box-shadow: 0 1px 0 #46A302; }

.card {
  background: #FFFFFF; border: 2px solid #E5E5E5; border-radius: 20px;
  padding: 14px 18px; margin: 10px 0; box-shadow: 0 4px 0 #E5E5E5;
  animation: pop 0.45s ease both;
}
@keyframes pop { from { transform: scale(0.92); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.hero { display: flex; align-items: center; gap: 16px; margin: 6px 0 14px 0; }
.mascot { font-size: 72px; display: inline-block; animation: bounce 1.6s ease-in-out infinite; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-14px); } }
.bubble {
  background: #FFFFFF; border: 2px solid #E5E5E5; border-radius: 20px;
  padding: 12px 18px; font-weight: 800; font-size: 18px; position: relative;
  box-shadow: 0 4px 0 #E5E5E5;
}
.bubble:before {
  content: ''; position: absolute; left: -12px; top: 50%; margin-top: -10px;
  border: 10px solid transparent; border-right-color: #E5E5E5; border-left: 0;
}

.lvl { font-size: 22px; font-weight: 900; }
.xpbar { height: 24px; background: #E5E5E5; border-radius: 14px; overflow: hidden; margin: 10px 0 6px 0; }
.xpfill { height: 100%; background: linear-gradient(90deg, #58CC02, #A5ED6E); border-radius: 14px; animation: grow 1.2s ease-out both; }
@keyframes grow { from { width: 0; } }
.small { color: #777777; font-size: 14px; font-weight: 600; }

.skillhead { font-size: 18px; font-weight: 800; display: flex; justify-content: space-between; align-items: center; }
.stars { font-size: 12px; }
.bar { height: 14px; background: #EEEEEE; border-radius: 10px; overflow: hidden; margin: 8px 0 4px 0; }
.barfill { height: 100%; border-radius: 10px; animation: grow 1s ease-out both; }

.step { display: flex; align-items: center; gap: 14px; margin: 14px 0; }
.stepcard { flex: 1; margin: 0; }
.node {
  width: 72px; height: 72px; min-width: 72px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 32px;
}
.node.current { background: #58CC02; border-bottom: 7px solid #46A302; animation: pulse 1.6s infinite; }
.node.locked { background: #E5E5E5; border-bottom: 7px solid #CFCFCF; }
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(88, 204, 2, 0.55); }
  70% { box-shadow: 0 0 0 18px rgba(88, 204, 2, 0); }
  100% { box-shadow: 0 0 0 0 rgba(88, 204, 2, 0); }
}

.stat { text-align: center; }
.big { font-size: 34px; font-weight: 900; color: #46A302; }
.lb { display: flex; align-items: center; gap: 12px; }
.lb .rank { font-size: 26px; min-width: 40px; text-align: center; }
.lb .who { min-width: 210px; font-weight: 800; }
.lb .bar { flex: 1; margin: 0; }
.why { background: #FFF8DC; border-color: #FFC800; box-shadow: 0 4px 0 #FFC800; font-weight: 800; }
</style>
"""


def esc(value):
    return _html.escape(str(value))


def md(markup):
    """Render HTML. Lines are joined so Markdown never treats indentation as code."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()),
                unsafe_allow_html=True)


def em(skill):
    return EMOJI.get(skill, "⭐")


def hero(message):
    md(f'<div class="hero"><div class="mascot">{MASCOT}</div>'
       f'<div class="bubble">{esc(message)}</div></div>')


def level_of(readiness):
    current, upcoming = LEVELS[0], None
    for i, level in enumerate(LEVELS):
        if readiness >= level[0]:
            current = level
            upcoming = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return current, upcoming


def mascot_says(readiness):
    if readiness >= 90:
        return "You are interview ready! Time to apply with confidence. 🏆"
    if readiness >= 75:
        return "So close! A couple more skills and you are there! 🚀"
    if readiness >= 50:
        return "Great progress! Follow the quest map and keep climbing. 🧗"
    if readiness >= 25:
        return "Nice start! Every skill you add moves the bar. 🧭"
    if readiness > 0:
        return "Everyone starts somewhere. Take the START HERE skill first! 🌱"
    return "Move the sliders to your honest levels. No fake skills, only real growth! 🌱"


def score_card(result):
    r = result["readiness"]
    (_, name, icon), upcoming = level_of(r)
    xp = int(r * 10)
    if upcoming:
        need = round(upcoming[0] - r, 1)
        nxt = f"{need}% more to reach {upcoming[2]} {upcoming[1]}"
    else:
        nxt = "Top level reached! 🎉"
    md(f'<div class="card"><div class="lvl">{icon} Level: {esc(name)}</div>'
       f'<div class="xpbar"><div class="xpfill" style="width:{r}%"></div></div>'
       f'<div class="small"><b>{xp} / 1000 XP</b> &nbsp;·&nbsp; {r}% ready for '
       f'{esc(result["role"])} &nbsp;·&nbsp; {nxt}</div></div>')


def skill_rows(breakdown):
    parts = []
    for b in breakdown:
        pct = 100 if b["need"] == 0 else min(100, round(b["have"] / b["need"] * 100))
        if b["shortfall"] == 0:
            color, status = "#58CC02", "✅"
        elif b["have"] > 0:
            color, status = "#FFC800", "🎯"
        else:
            color, status = "#FF7A7A", "🎯"
        stars = "⭐" * b["weight"]
        parts.append(
            f'<div class="card"><div class="skillhead"><span>{em(b["skill"])} '
            f'{esc(b["skill"])} {status}</span><span class="stars">{stars}</span></div>'
            f'<div class="bar"><div class="barfill" style="width:{pct}%;background:{color}"></div></div>'
            f'<div class="small">You: level {b["have"]} &nbsp;·&nbsp; Needed: level {b["need"]} '
            f'&nbsp;·&nbsp; Importance: {b["weight"]}/5</div></div>')
    md("".join(parts))


def journey(path):
    if not path:
        md('<div class="card" style="text-align:center"><div style="font-size:50px">🎉</div>'
           '<b>No gaps left for this role!</b></div>')
        return
    offsets = [0, 60, 100, 60]
    parts = []
    for i, step in enumerate(path):
        if i == 0:
            cls, icon, label = "current", em(step["skill"]), "START HERE"
        else:
            cls, icon, label = "locked", "🔒", f"Step {step['step']}"
        parts.append(
            f'<div class="step" style="margin-left:{offsets[i % 4]}px">'
            f'<div class="node {cls}">{icon}</div>'
            f'<div class="card stepcard"><div class="small">{label}</div>'
            f'<b>{em(step["skill"])} {esc(step["skill"])}</b>'
            f'<div class="small">{esc(step["reason"])}</div></div></div>')
    md("".join(parts))


def show_result(result, tag):
    hero(mascot_says(result["readiness"]))
    why = st.session_state.get("why", "").strip()
    if why:
        md(f'<div class="card why">💛 Remember why you started: {esc(why)}</div>')
    score_card(result)

    for item in result["to_confirm"]:
        st.warning(f"🤔 Did you mean **{item['suggestion']}** when you typed "
                   f"'{item['typed']}'? It is not counted until you confirm "
                   f"(match score {item['score']}).")
    if result["unrecognised"]:
        st.info("🔎 I did not recognise: " + ", ".join(result["unrecognised"]))

    left, right = st.columns(2)
    with left:
        st.subheader("🎯 Your skills")
        skill_rows(result["breakdown"])
    with right:
        st.subheader("🗺️ Your quest map")
        journey(build_learning_path(result["breakdown"]))

    if result["readiness"] >= 75 and tag not in st.session_state.celebrated:
        st.session_state.celebrated.add(tag)
        st.balloons()


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


def sliders_for(role, prefix=""):
    cols = st.columns(3)
    raw = {}
    for i, req in enumerate(role["required"]):
        with cols[i % 3]:
            level = st.slider(f"{em(req['skill'])} {req['skill']}", 0, 5, 0,
                              key=prefix + req["skill"])
            if level > 0:
                raw[req["skill"]] = level
    return raw


def student_view():
    role_name = st.selectbox("🎯 Target role", list(ROLES))
    role = ROLES[role_name]
    st.text_input("💛 Who are you doing this for? (optional, I will remind you)", key="why")

    with st.expander("📄 Upload your resume (optional)"):
        up = st.file_uploader("PDF resume", type="pdf")
        if up is not None:
            try:
                claimed = find_skills(extract_text(up))
            except Exception:
                claimed = []
                st.error("Could not read this PDF (scanned images are not supported).")
            if claimed:
                st.info("Skills found in your resume (claimed, not verified): " + ", ".join(claimed))
                if st.button("Set matching sliders to level 1"):
                    for req in role["required"]:
                        if req["skill"] in claimed and st.session_state.get(req["skill"], 0) == 0:
                            st.session_state[req["skill"]] = 1
                st.caption("A resume shows what you claim, not how well you know it. "
                           "Set your honest level below.")

    st.subheader("🎚️ Rate your honest level")
    st.caption("0 = none · 1 = heard of it · 3 = built something · 5 = can teach it")
    raw = sliders_for(role)
    extra = st.text_input("✍️ Other skills, typed freely (example: pythn=3, postgre sql=2)")
    raw.update(parse_extra(extra))
    show_result(compute_gap(raw, role), "role:" + role_name)


def jd_view():
    hero("Paste a real job description and I will turn it into a quest for you!")
    title = st.text_input("Role title", "Pasted role")
    jd = st.text_area("📋 Paste a job description", height=200)
    if not jd.strip():
        return
    role = role_from_jd(jd, title or "Pasted role")
    if not role["required"]:
        st.warning("I did not find any known skills in this text.")
        return
    st.subheader("🔍 Skills found in the posting")
    st.caption("The more often a skill appears, the more important it is.")
    st.dataframe(pd.DataFrame(role["required"]), hide_index=True)
    st.subheader("🎚️ Rate your honest level for each")
    raw = sliders_for(role, prefix="jd:")
    show_result(compute_gap(raw, role), "jd")


def mentor_view():
    with open(ROOT / "data" / "students.json", encoding="utf-8") as f:
        students = json.load(f)
    summary = summarise(students, ROLES)
    gaps = summary["common_gaps"]
    top = gaps[0]["skill"] if gaps else "none"
    hero(f"Your class has {summary['student_count']} students. Average readiness is "
         f"{summary['average_readiness']}%. Biggest shared gap: {top}.")

    c1, c2, c3 = st.columns(3)
    for col, value, label in [
        (c1, summary["student_count"], "Students"),
        (c2, f"{summary['average_readiness']}%", "Average readiness"),
        (c3, f"{em(top)} {top}", "Biggest shared gap"),
    ]:
        with col:
            md(f'<div class="card stat"><div class="big">{esc(value)}</div>'
               f'<div class="small">{label}</div></div>')

    if gaps:
        st.subheader("📊 Most common gaps")
        frame = pd.DataFrame(gaps)
        st.bar_chart(frame.set_index("skill")["students_with_gap"])
        md(f'<div class="card">💡 <b>Suggested workshop:</b> {esc(top)} '
           f'({gaps[0]["students_with_gap"]} of {summary["student_count"]} students have this gap)</div>')

    st.subheader("🏆 Class leaderboard")
    ranked = sorted(summary["students"], key=lambda s: -s["readiness"])[:10]
    medals = ["🥇", "🥈", "🥉"]
    rows = []
    for i, s in enumerate(ranked):
        rank = medals[i] if i < 3 else f"#{i + 1}"
        rows.append(
            f'<div class="card lb"><div class="rank">{rank}</div>'
            f'<div class="who">{esc(s["name"])}<div class="small">{esc(s["target_role"])}</div></div>'
            f'<div class="bar"><div class="barfill" style="width:{s["readiness"]}%;'
            f'background:#58CC02"></div></div><div><b>{s["readiness"]}%</b></div></div>')
    md("".join(rows))


# ---------- app ----------
md(CSS)
st.session_state.setdefault("user", None)
st.session_state.setdefault("celebrated", set())

if st.session_state.user is None:
    hero("Hi! I am your skill coach. Let us find your gaps and turn them into a quest. "
         "Log in or join to start!")
    tab_in, tab_up = st.tabs(["🔑 Log in", "✨ Join the quest"])
    with tab_in:
        u = st.text_input("Username", key="li_user")
        p = st.text_input("Password", type="password", key="li_pass")
        if st.button("Log in"):
            role = login(u, p)
            if role:
                st.session_state.user = {"name": u.strip(), "role": role}
                st.rerun()
            else:
                st.error("Wrong username or password")
    with tab_up:
        nu = st.text_input("Choose a username", key="re_user")
        npw = st.text_input("Choose a password (6+ characters)", type="password", key="re_pass")
        nrole = st.selectbox("I am a", ["student", "mentor"])
        code = st.text_input("Mentor code (mentors only)", type="password")
        if st.button("Create account"):
            try:
                register(nu, npw, nrole, mentor_code=code)
                st.success("Account created! Now log in from the first tab. 🎉")
                st.balloons()
            except ValueError as e:
                st.error(str(e))
    st.stop()

user = st.session_state.user
with st.sidebar:
    md(f'<div class="card"><div style="font-size:40px">{MASCOT}</div>'
       f'<b>{esc(user["name"])}</b><div class="small">{esc(user["role"])}</div></div>')
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()

views = ["🎓 My quest", "📋 Job description quest"]
if user["role"] == "mentor":
    views.append("👩‍🏫 Class view")
view = st.sidebar.radio("Where to?", views)

st.title("Skill Gap Analyzer")
if view.startswith("🎓"):
    student_view()
elif view.startswith("📋"):
    jd_view()
else:
    mentor_view()