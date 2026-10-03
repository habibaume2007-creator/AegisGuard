"""Page 2: ask questions answered from the knowledge notes (RAG)."""
import streamlit as st

import assistant
import rag
from ui_common import hero, show_sources

hero("Security Assistant (RAG)",
     "Ask about vulnerabilities, fixes or how AegisGuard works. Every answer shows its sources.",
     eyebrow="Retrieval-augmented answers")

st.markdown("Answers come from the security notes in `knowledge/` (retrieval) and the saved run history "
            "(long-term memory). The language model is told to answer only from those.")

notes = rag.list_notes()
with st.expander(f"What does the assistant know? ({len(notes)} notes)"):
    st.table([{"Note": n["title"], "File": n["source"], "Sections": n["sections"]} for n in notes])

EXAMPLES = ["What is SQL injection?", "Why do parameterized queries fix it?",
            "What is path traversal?", "How can I stop XSS in Flask?",
            "How does AegisGuard verify a patch?", "How many fixes have been verified so far?"]


def set_question(text):
    st.session_state["q"] = text


st.markdown("**Try one of these:**")
for row in (EXAMPLES[:3], EXAMPLES[3:]):
    for col, ex in zip(st.columns(3), row):
        col.button(ex, on_click=set_question, args=(ex,), use_container_width=True)

q = st.text_input("Your question", key="q", placeholder="For example: What is path traversal?")
if st.button("Ask", type="primary") and q.strip():
    with st.spinner("Searching the notes and thinking..."):
        st.session_state["qa"] = {"q": q, **assistant.ask_assistant(q)}

qa = st.session_state.get("qa")
if qa:
    st.divider()
    st.markdown(f"**Q: {qa['q']}**")
    (st.success if qa.get("used_llm") else st.warning)(qa["answer"])
    if qa["sources"]:
        st.markdown(f"##### Sources used ({len(qa['sources'])})")
        show_sources(qa["sources"])