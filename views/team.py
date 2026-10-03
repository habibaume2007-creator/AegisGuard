"""Page 4: about the project, the team leader and the members."""
import streamlit as st

from ui_common import ABOUT, hero, person_html, section

hero(f"{ABOUT['project']}: About and Team", ABOUT["tagline"], eyebrow=f"{ABOUT['team_name']}  |  {ABOUT['program']}")
st.markdown(f"**{ABOUT['event']}**  |  **{ABOUT['program']}**  |  Team: **{ABOUT['team_name']}**")

team = ABOUT.get("team", [])
leader = ABOUT.get("leader") or next((m for m in team if "leader" in m.get("role", "").lower()), None)
members = [m for m in team if m is not leader and "leader" not in m.get("role", "").lower()]

section("team leader")
if leader:
    st.markdown(person_html(leader, leader=True), unsafe_allow_html=True)

section("team members")
st.markdown('<div class="ag-team-grid">' + "".join(person_html(m) for m in members) + "</div>", unsafe_allow_html=True)

section("how it works")
for i, step in enumerate(ABOUT["how_it_works"], 1):
    st.markdown(f"{i}. {step}")

section("built with")
st.table([{"Layer": t["layer"], "Technology": t["tech"], "Purpose": t["purpose"]} for t in ABOUT["tech_stack"]])