"""AegisGuard entry point and sidebar navigation."""
import html

import streamlit as st

import config
import memory
import ui_common

st.set_page_config(
    page_title="AegisGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui_common.setup()

nav = st.navigation([
    st.Page("views/demo.py", title="Security Scan", icon="🔎", default=True),
    st.Page("views/assistant.py", title="Security Assistant", icon="💬"),
    st.Page("views/memory_page.py", title="Run History", icon="🗂️"),
    st.Page("views/team.py", title="About", icon="ℹ️"),
])

with st.sidebar:
    st.markdown(f'{ui_common.SHIELD} <span class="ag-brand">AEGISGUARD</span>', unsafe_allow_html=True)
    st.caption("Security analysis and assisted remediation")
    st.divider()

    st.markdown("**Workspace status**")
    if config.USE_DOCKER:
        st.markdown(ui_common.chip("Isolated verification", "green"), unsafe_allow_html=True)
        st.caption("Uploaded remediation can be verified in an isolated environment when enabled by the workflow.")
    else:
        st.markdown(ui_common.chip("Safe static mode", "blue"), unsafe_allow_html=True)
        st.caption("Uploaded projects are never executed. Suggested patches are unverified until isolated testing is enabled.")

    st.markdown(f"Model: `{html.escape(config.GEMINI_MODEL)}`")
    s = memory.stats()
    st.markdown(f"Verified demo fixes: **{s['verified']} / {s['total']}**")

    st.divider()
    st.caption(f"{ui_common.ABOUT['team_name']} · {ui_common.ABOUT['event']}")
    if not config.GOOGLE_API_KEY:
        st.error("GOOGLE_API_KEY is missing in .env")

nav.run()
