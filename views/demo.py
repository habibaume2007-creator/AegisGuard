"""Security Scan: uploaded project scanning plus trusted demo remediation."""
import difflib
import hashlib
import html

import streamlit as st

import assistant
import config
import rag
from agent import AgentState, ask, build_graph, extract_code, initial_state, list_samples, replay_run
from graph_builder import build_call_graph, to_dot
from project_loader import ProjectUploadError, load_project_upload
from scanner import scan_project
from ui_common import (
    banner,
    hero,
    pipeline_html,
    section,
    severity_chip,
    show_sources,
    status_chip,
    terminal,
    upload_intro,
)

hero(
    "Security Scan",
    "Review a Python project for supported security issues, inspect evidence, and generate remediation suggestions. Demo Samples remain available for the complete exploit-to-verification workflow.",
    eyebrow="AegisGuard security workspace",
)

upload_tab, demo_tab = st.tabs(["Upload Project", "Demo Samples"])


# -----------------------------------------------------------------------------
# Uploaded project: safe static analysis + unverified patch suggestion
# -----------------------------------------------------------------------------
with upload_tab:
    upload_intro()

    uploaded = st.file_uploader(
        "Choose a Python file or ZIP project",
        type=["py", "zip"],
        key="project_upload",
        help="Upload one .py file or a .zip containing Python source. AegisGuard will not execute uploaded code while Docker is disabled.",
    )

    if uploaded is None:
        st.caption("Supported input: `.py` or `.zip` · Uploaded source is parsed, not executed.")
        st.info("Choose a file above to start a project security scan.")
    else:
        upload_bytes = uploaded.getvalue()
        upload_id = hashlib.sha256(upload_bytes).hexdigest()[:16]

        try:
            manifest = load_project_upload(uploaded.name, upload_bytes)
        except ProjectUploadError as exc:
            st.error(str(exc))
            manifest = None

        if manifest:
            report = scan_project(manifest["files"])

            section("Project summary")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Python files", report["files_scanned"])
            c2.metric("Findings", len(report["findings"]))
            c3.metric("Parse warnings", len(report["parse_errors"]))
            c4.metric("Source size", f"{manifest['total_bytes'] / 1024:.1f} KB")

            findings = report["findings"]
            section("Security findings")
            if not findings:
                banner("No supported vulnerability pattern was detected by the current static rules.", "green")
                st.caption("This does not prove the project is secure; AegisGuard currently checks a limited set of Python vulnerability patterns.")
            else:
                st.dataframe(
                    [{
                        "Severity": f["severity"].upper(),
                        "Finding": f["name"],
                        "CWE": f["cwe"],
                        "File": f["file"],
                        "Function": f["function"],
                        "Line": f["line"] or "-",
                    } for f in findings],
                    use_container_width=True,
                    hide_index=True,
                )

                labels = [
                    f"{f['severity'].upper()} · {f['name']} · {f['file']}:{f['line'] or '?'} · {f['function']}()"
                    for f in findings
                ]
                selected_index = st.selectbox(
                    "Select a finding to inspect",
                    range(len(findings)),
                    format_func=lambda i: labels[i],
                    key=f"finding_{upload_id}",
                )
                finding = findings[selected_index]
                source = manifest["files"][finding["file"]]

                with st.container(border=True):
                    st.markdown(
                        severity_chip(finding["severity"])
                        + f'<span class="ag-cwe">{html.escape(finding["cwe"])}</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"### {finding['name']}")
                    st.markdown(
                        f"**Location:** `{finding['file']}` · `{finding['function']}()` · line {finding['line'] or 'unknown'}"
                    )
                    st.write(finding["summary"])

                left, right = st.columns([1.15, .85])
                with left:
                    with st.expander("View source file", expanded=True):
                        st.code(source, language="python", line_numbers=True)

                guidance = rag.retrieve(f"{finding['name']} fix", k=2)
                with right:
                    st.markdown("**Recommended direction**")
                    if guidance:
                        show_sources(guidance)
                    else:
                        st.info("No matching knowledge-base guidance was found.")

                section("Suggested remediation")
                if not config.USE_DOCKER:
                    st.warning(
                        "Docker is off. AegisGuard can generate a suggested patch for review, but it will NOT execute the uploaded project or claim the patch is verified."
                    )

                patch_key = f"uploaded_patch_{upload_id}_{selected_index}"
                if st.button("Generate Suggested Patch", type="primary", key=f"patch_btn_{upload_id}_{selected_index}"):
                    guidance_text = "\n\n".join(
                        f"[{g['source']}]\n{g['text'][:1000]}" for g in guidance
                    ) or "No additional knowledge-base guidance was retrieved."
                    prompt = f"""You are a security engineer proposing a minimal patch for a Python source file.

Finding: {finding['name']} ({finding['cwe']})
File: {finding['file']}
Function: {finding['function']}

Security guidance:
{guidance_text}

Original file:
```python
{source}
```

Requirements:
- Fix only the stated vulnerability.
- Preserve public function names, signatures, routes, and normal behavior.
- Do not add network calls, subprocess execution, telemetry, or unrelated refactors.
- Return the COMPLETE corrected file in one Python code block and nothing else.
"""
                    try:
                        with st.spinner("Generating a minimal remediation suggestion..."):
                            st.session_state[patch_key] = extract_code(ask(prompt))
                    except Exception as exc:
                        st.error(f"Could not generate a patch: {exc}")

                proposed = st.session_state.get(patch_key)
                if proposed:
                    diff = "".join(
                        difflib.unified_diff(
                            source.splitlines(True),
                            proposed.splitlines(True),
                            f"{finding['file']} (before)",
                            f"{finding['file']} (suggested)",
                        )
                    )
                    if diff.strip():
                        st.code(diff, language="diff")
                        st.caption("Suggested patch only — not executed or verified while isolated testing is disabled.")
                        safe_name = finding["file"].replace("/", "_").replace("\\", "_")
                        st.download_button(
                            "Download Suggested Patched File",
                            data=proposed,
                            file_name=f"patched_{safe_name}",
                            mime="text/x-python",
                            key=f"download_{upload_id}_{selected_index}",
                        )
                    else:
                        st.info("The generated response did not change the file. Try again or review the finding manually.")

            if report["parse_errors"]:
                with st.expander(f"Parse warnings ({len(report['parse_errors'])})"):
                    for warning in report["parse_errors"]:
                        st.write(warning)

            if manifest["skipped"]:
                with st.expander(f"Skipped files ({len(manifest['skipped'])})"):
                    for skipped in manifest["skipped"]:
                        st.write(skipped)

            section("Current scanner coverage")
            st.caption(
                "Static rules currently cover SQL injection, path traversal, cross-site scripting (XSS), and unsafe deserialization. "
                "Treat results as focused findings for review, not as a complete security audit."
            )


# -----------------------------------------------------------------------------
# Existing trusted demo workflow
# -----------------------------------------------------------------------------
with demo_tab:
    samples = list_samples()
    keys = list(samples)
    if not keys:
        st.error("No demo samples were found in the samples/ directory.")
        st.stop()

    if st.session_state.get("chosen_sample") not in keys:
        st.session_state["chosen_sample"] = keys[0]


    def pick(k):
        st.session_state["chosen_sample"] = k


    section("01 / select demo finding")
    for col, k in zip(st.columns(len(keys)), keys):
        meta = samples[k]
        with col:
            with st.container(border=True):
                st.markdown(
                    severity_chip(meta.get("severity", "medium"))
                    + f'<span class="ag-cwe">{html.escape(meta.get("cwe", ""))}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{meta['title']}**")
                chosen = st.session_state["chosen_sample"] == k
                st.button(
                    "Selected" if chosen else "Select",
                    key=f"pick_{k}",
                    on_click=pick,
                    args=(k,),
                    disabled=chosen,
                    use_container_width=True,
                )

    choice = st.session_state["chosen_sample"]
    st.markdown(f'<div class="ag-panel">{html.escape(samples[choice]["description"])}</div>', unsafe_allow_html=True)
    state0: AgentState = initial_state(choice)
    with st.expander("View vulnerable demo code"):
        st.code(state0["source"], language="python", line_numbers=True)

    section("02 / run remediation workflow")
    if not config.USE_DOCKER:
        st.warning(
            "Local demo mode is active. Only run the bundled trusted samples here. Do not use local execution for untrusted uploaded code."
        )

    b1, b2, _ = st.columns([1.25, 2.0, 2.0])
    run_clicked = b1.button("Run AegisGuard", type="primary", use_container_width=True)
    replay_clicked = b2.button("Replay last verified run", use_container_width=True)

    if run_clicked:
        final, logs = dict(state0), []
        with st.status("Running analysis and remediation...", expanded=True) as box:
            try:
                for update in build_graph().stream(state0, stream_mode="updates"):
                    for node, delta in update.items():
                        for line in delta.get("log", []):
                            logs.append(line)
                            st.write(f"**{node}**: {line}")
                        final.update({k: v for k, v in delta.items() if k != "log"})
                box.update(label=f"Completed: {final.get('status')}", state="complete")
            except Exception as exc:
                box.update(label="Run failed", state="error")
                msg = str(exc)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    st.error(
                        "Gemini request quota was reached. Use Replay for a saved run, wait for quota recovery, "
                        "or configure a valid fallback model."
                    )
                else:
                    st.error(msg)
        final["log"] = logs
        st.session_state["result"] = final
        st.session_state.pop("approved", None)
        st.session_state.pop("explain", None)

    if replay_clicked:
        try:
            with st.spinner("Re-running the saved exploit test and patch..."):
                st.session_state["result"] = replay_run(choice)
            st.session_state.pop("approved", None)
            st.session_state.pop("explain", None)
        except Exception as exc:
            st.warning(str(exc))

    r = st.session_state.get("result")
    section("03 / remediation pipeline")
    st.markdown(pipeline_html(r, bool(st.session_state.get("approved"))), unsafe_allow_html=True)

    if r:
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown("**Result**")
        m1.markdown(status_chip(r.get("status", "")), unsafe_allow_html=True)
        rmeta = samples.get(r.get("sample"), {})
        m2.markdown("**Severity**")
        m2.markdown(
            severity_chip(rmeta.get("severity", "medium"))
            + f'<span class="ag-cwe">{html.escape(rmeta.get("cwe", ""))}</span>',
            unsafe_allow_html=True,
        )
        m3.metric("Patch attempts", r.get("patch_attempts", 1 if r.get("replayed") else 0))
        m4.metric("Run type", "Replay" if r.get("replayed") else "Live")

        col1, col2 = st.columns(2)
        with col1:
            section("Reachability")
            if r.get("paths"):
                st.graphviz_chart(to_dot(build_call_graph(r["source"]), r["paths"][0]))
                st.caption("Highlighted path shows how a public route reaches the vulnerable function.")
            else:
                st.info("No public route to the finding was identified.")

            section("Finding confirmation")
            er = r.get("exploit_result")
            if er:
                if er["expected"]:
                    banner("Vulnerability confirmed: the security test failed on the vulnerable code as expected.", "red")
                else:
                    banner("The generated security test did not fail for the expected reason.", "amber")
            if r.get("exploit_test"):
                with st.expander("View generated security test"):
                    st.code(r["exploit_test"], language="python")
            if er:
                with st.expander("View sandbox output"):
                    st.code(er["output"][-1500:])

        with col2:
            section("Proposed fix")
            if r.get("patched_source"):
                diff = "".join(
                    difflib.unified_diff(
                        r["source"].splitlines(True),
                        r["patched_source"].splitlines(True),
                        "target_sample.py (before)",
                        "target_sample.py (after)",
                    )
                )
                st.code(diff, language="diff")
                if st.button("Explain this fix"):
                    with st.spinner("Retrieving security guidance..."):
                        st.session_state["explain"] = assistant.ask_assistant(
                            f"Explain in simple words why this change fixes the {r.get('vuln_name', 'vulnerability')}.",
                            extra=diff[:2500],
                            query=f"{r.get('vuln_name', '')} fix",
                        )
                ex = st.session_state.get("explain")
                if ex:
                    st.success(ex["answer"])
                    if ex["sources"]:
                        with st.expander(f"Sources used ({len(ex['sources'])})"):
                            show_sources(ex["sources"])

            section("Verification")
            vr = r.get("verify_result")
            if vr:
                if vr["passed"]:
                    banner("Verification passed: the security test and original regression tests all pass.", "green")
                else:
                    banner("Verification failed.", "red")
                st.caption(f"Static re-scan clean: {vr['static_clean']}")
                with st.expander("View verification output"):
                    st.code(vr["output"][-1500:])

        if r.get("guidance"):
            with st.expander(f"Security guidance used by the patch agent ({len(r['guidance'])})"):
                show_sources(r["guidance"])
        if r.get("past_fixes"):
            st.caption(f"Used {len(r['past_fixes'])} earlier verified fix(es) from long-term memory as reference.")

        section("Agent activity")
        terminal(r.get("log", []))

        section("04 / human approval")
        if r.get("status") == "ready_for_approval":
            if st.button("Approve and save patch"):
                config.APPROVED_DIR.mkdir(exist_ok=True)
                (config.APPROVED_DIR / f"{r.get('sample', 'target')}_patched.py").write_text(
                    r["patched_source"], encoding="utf-8"
                )
                st.session_state["approved"] = True
                st.rerun()
            if st.session_state.get("approved"):
                st.success(f"Approved patch saved to approved/{r.get('sample', 'target')}_patched.py")
        else:
            st.warning("No verified patch is ready for approval. Human review is required.")
