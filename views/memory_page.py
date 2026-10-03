"""Page 3: long-term memory (history of every run)."""
import streamlit as st

import memory
from ui_common import hero, status_chip

hero(
    "Run History",
    "Review saved security runs, verification outcomes, and previously generated fixes.",
    eyebrow="Long-term memory",
)

s = memory.stats()
c1, c2, c3 = st.columns(3)
c1.metric("Runs saved", s["total"])
c2.metric("Verified fixes", s["verified"])
c3.metric("Success rate", f"{s['rate']}%")

with st.expander("How AegisGuard uses this memory", expanded=False):
    st.markdown(
        "- The patch agent can reuse the most recent **verified fix** for the same vulnerability type as a reference.\n"
        "- Notes from recent **failed runs** are retained so the agent can avoid repeating the same mistake.\n"
        "- Only fixes that passed verification are reused as successful examples."
    )

rows = memory.all_runs(limit=100)

if not rows:
    st.info(
        "No runs have been saved yet. Run one of the demo samples from Security Scan "
        "and completed runs will appear here."
    )
else:
    counts = memory.outcome_counts()

    st.markdown("#### Outcome summary")

    verified = counts.get("ready_for_approval", 0)
    failed = counts.get("verification_failed", 0)
    escalated = counts.get("escalated_to_human", 0)
    unconfirmed = counts.get("unconfirmed", 0)

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Verified", verified)
    o2.metric("Failed", failed)
    o3.metric("Escalated", escalated)
    o4.metric("Unconfirmed", unconfirmed)

    st.markdown("#### Recent activity")

    types = sorted({r["vuln_type"] for r in rows})
    selected_types = st.multiselect(
        "Filter by vulnerability type",
        options=types,
        default=types,
        format_func=lambda x: x.replace("_", " ").title(),
    )

    shown = [r for r in rows if r["vuln_type"] in selected_types]

    def display_status(outcome: str) -> str:
        labels = {
            "ready_for_approval": "Verified",
            "verification_failed": "Verification failed",
            "escalated_to_human": "Escalated",
            "unconfirmed": "Unconfirmed",
            "no_vulnerability_found": "No vulnerability found",
            "confirmed": "Confirmed",
            "triaged": "Triaged",
        }
        return labels.get(outcome, outcome.replace("_", " ").title())

    st.dataframe(
        [
            {
                "Run": f"#{r['id']}",
                "Time": r["ts"],
                "Vulnerability": r["vuln_type"].replace("_", " ").title(),
                "Function": r["function"],
                "Status": display_status(r["outcome"]),
                "Patch attempts": r["attempts"],
            }
            for r in shown
        ],
        use_container_width=True,
        hide_index=True,
    )

    if shown:
        st.markdown("#### Inspect a run")

        run_id = st.selectbox(
            "Choose a run",
            [r["id"] for r in shown],
            format_func=lambda i: next(
                (
                    f"#{r['id']}  ·  "
                    f"{r['vuln_type'].replace('_', ' ').title()}  ·  "
                    f"{display_status(r['outcome'])}"
                )
                for r in shown
                if r["id"] == i
            ),
        )

        run = memory.get_run(run_id)

        if run:
            st.markdown(status_chip(run["outcome"]), unsafe_allow_html=True)

            if run["exploit_test"]:
                with st.expander("Security test"):
                    st.code(run["exploit_test"], language="python")

            if run["patch"]:
                with st.expander("Verified patch"):
                    st.code(run["patch"], language="python")

            if run["note"]:
                with st.expander("Failure details"):
                    st.code(run["note"])
