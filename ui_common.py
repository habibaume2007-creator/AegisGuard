"""Shared light professional UI theme and helpers used by every AegisGuard page."""
import html
import json
import re

import streamlit as st

import config

ABOUT = json.loads((config.BASE_DIR / "about.json").read_text(encoding="utf-8"))

CSS = r"""<style>
:root {
  --bg:#f6f7f9;
  --surface:#ffffff;
  --surface-2:#f9fafb;
  --surface-3:#eef2f5;
  --line:#dfe3e8;
  --line-strong:#cfd6dd;
  --text:#1f2933;
  --text-2:#46515c;
  --muted:#6f7b87;
  --accent:#5f7485;
  --accent-dark:#455b6b;
  --accent-soft:#e9eef2;
  --green:#4f7f64;
  --green-soft:#eef6f1;
  --red:#a45757;
  --red-soft:#fbf1f1;
  --amber:#9b7435;
  --amber-soft:#faf5ea;
  --blue:#5d7589;
  --blue-soft:#edf2f6;
  --shadow:0 8px 26px rgba(31,41,51,.055);
  --mono:ui-monospace,"Cascadia Code","JetBrains Mono",Consolas,"Courier New",monospace;
}

#MainMenu, footer {visibility:hidden;}
html, body, [class*="css"] {font-family: Inter, "Segoe UI", Arial, sans-serif;}
.stApp {background:var(--bg); color:var(--text);}
.block-container {padding-top:1.25rem; padding-bottom:3rem; max-width:1240px;}

/* Global readable text */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"],
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {color:var(--text)!important;}
h1,h2,h3,h4,h5,h6 {color:var(--text)!important; letter-spacing:-.015em;}
[data-testid="stCaptionContainer"], .stCaption {color:var(--muted)!important;}
code {color:#33424d!important; background:#eef1f4!important;}

/* Sidebar stays light too */
[data-testid="stSidebar"] {
  background:#eef1f4;
  border-right:1px solid var(--line-strong);
}
[data-testid="stSidebar"] * {color:var(--text)!important;}
[data-testid="stSidebar"] code {background:#e1e6ea!important;}
[data-testid="stSidebar"] hr {border-color:var(--line-strong);}
[data-testid="stSidebarNav"] a {border-radius:9px; margin:2px 6px; padding-top:.55rem; padding-bottom:.55rem;}
[data-testid="stSidebarNav"] a:hover {background:#e2e7eb;}
[data-testid="stSidebarNav"] a[aria-current="page"] {background:#dde4e9;}

/* Buttons */
.stButton > button,
[data-testid^="stBaseButton"] {
  border-radius:9px;
  font-weight:650;
  border:1px solid var(--line-strong);
  box-shadow:none;
  min-height:2.55rem;
}
.stButton > button:hover {border-color:#aeb8c1;}
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
  background:var(--accent-dark);
  color:white!important;
  border-color:var(--accent-dark);
}
.stButton > button[kind="primary"] *, button[data-testid="stBaseButton-primary"] * {color:white!important;}
.stButton > button[kind="primary"]:hover {background:#384c5a; border-color:#384c5a;}

/* Inputs */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
textarea {background:white!important; border-color:var(--line-strong)!important;}
input, textarea {color:var(--text)!important;}

/* Tabs */
[data-baseweb="tab-list"] {gap:8px; border-bottom:1px solid var(--line);}
[data-baseweb="tab"] {
  height:46px;
  padding:0 16px;
  border-radius:9px 9px 0 0;
  color:var(--muted)!important;
  font-weight:650;
}
[data-baseweb="tab"][aria-selected="true"] {
  color:var(--accent-dark)!important;
  background:white;
}

/* File uploader -- prominent */
[data-testid="stFileUploader"] {
  background:white;
  border:1px solid var(--line);
  border-radius:14px;
  box-shadow:var(--shadow);
  padding:4px;
}
[data-testid="stFileUploaderDropzone"] {
  background:#fbfcfd!important;
  border:1.5px dashed #aeb9c3!important;
  border-radius:11px!important;
  min-height:150px;
}
[data-testid="stFileUploaderDropzone"] * {color:var(--text)!important;}

/* Generic Streamlit cards */
[data-testid="stMetric"] {
  background:white;
  border:1px solid var(--line);
  border-radius:12px;
  padding:14px 16px;
  box-shadow:0 3px 14px rgba(31,41,51,.035);
}
[data-testid="stExpander"] {background:white; border:1px solid var(--line); border-radius:11px;}
[data-testid="stDataFrame"], [data-testid="stTable"] {background:white; border-radius:11px;}

/* Top product header */
.ag-hero {
  background:white;
  border:1px solid var(--line);
  border-radius:16px;
  padding:24px 26px;
  margin-bottom:18px;
  box-shadow:var(--shadow);
  position:relative;
}
.ag-hero:after {
  content:"";
  position:absolute;
  left:0; top:22px; bottom:22px;
  width:4px;
  border-radius:0 4px 4px 0;
  background:var(--accent);
}
.ag-eyebrow {font-size:.72rem; font-weight:750; letter-spacing:.13em; color:var(--accent); text-transform:uppercase;}
.ag-hero h1 {margin:5px 0 2px; font-size:2rem; font-weight:760;}
.ag-hero p {margin:8px 0 0; color:var(--text-2)!important; max-width:880px; line-height:1.55;}

/* Section headers */
.ag-section {font-size:.74rem; letter-spacing:.13em; color:var(--muted); text-transform:uppercase; font-weight:800; margin:20px 0 8px;}
.ag-panel {background:white; border:1px solid var(--line); border-radius:12px; padding:14px 16px; margin:8px 0 12px; box-shadow:0 3px 12px rgba(31,41,51,.03); color:var(--text);}
.ag-note {background:var(--accent-soft); border:1px solid #d7e0e6; border-radius:11px; padding:12px 14px; color:#43525d; margin:8px 0 14px;}

/* Upload callout */
.ag-upload-intro {display:flex; gap:14px; align-items:flex-start; background:white; border:1px solid var(--line); border-radius:14px; padding:18px 20px; margin-bottom:12px; box-shadow:var(--shadow);}
.ag-upload-icon {width:42px; height:42px; flex:none; border-radius:11px; background:var(--accent-soft); color:var(--accent-dark); display:flex; align-items:center; justify-content:center; font-size:1.25rem; font-weight:800;}
.ag-upload-title {font-weight:760; font-size:1rem; margin-bottom:3px; color:var(--text);}
.ag-upload-copy {font-size:.9rem; color:var(--text-2); line-height:1.5;}

/* Chips */
.ag-chip {display:inline-block; padding:4px 9px; border-radius:999px; font-size:.69rem; font-weight:800; text-transform:uppercase; letter-spacing:.035em; color:white!important;}
.ag-red {background:var(--red);} .ag-green {background:var(--green);} .ag-amber {background:var(--amber);} .ag-blue {background:var(--blue);} .ag-grey {background:#7b858e;}
.ag-cwe {font-size:.76rem; color:var(--muted); margin-left:8px; font-family:var(--mono);}

/* Banners */
.ag-banner {padding:11px 13px; border-radius:9px; font-weight:650; margin:7px 0 10px; font-size:.84rem;}
.ag-banner-red {border:1px solid #dfc2c2; background:var(--red-soft); color:#823f3f;}
.ag-banner-green {border:1px solid #bfd4c7; background:var(--green-soft); color:#3f674f;}
.ag-banner-amber {border:1px solid #dfcea9; background:var(--amber-soft); color:#765824;}

/* Pipeline */
.ag-pipe {display:grid; grid-template-columns:repeat(6,1fr); gap:7px; margin:7px 0 15px;}
.ag-node {padding:10px 9px; border-radius:9px; border:1px solid var(--line); background:white; font-size:.68rem; font-weight:800; text-transform:uppercase; color:var(--muted); text-align:center;}
.ag-node small {display:block; font-size:.61rem; margin-top:2px; font-weight:500; text-transform:none;}
.ag-node.done {border-color:#b8d0c1; background:var(--green-soft); color:var(--green);}
.ag-node.fail {border-color:#dec1c1; background:var(--red-soft); color:var(--red);}
.ag-node.active {border-color:#b6c4ce; background:var(--blue-soft); color:var(--accent-dark);}

/* Terminal */
.ag-term {background:#f1f3f5; border:1px solid var(--line); border-radius:10px; padding:12px 14px; font-family:var(--mono); font-size:.79rem; color:#34434f; line-height:1.55; overflow-x:auto; white-space:pre-wrap;}
.ag-term .p {color:#728492;}

/* Team */
.ag-team-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px; margin:8px 0 14px;}
.ag-person {display:flex; gap:14px; align-items:center; background:white; border:1px solid var(--line); border-radius:12px; padding:14px 16px;}
.ag-leader {border-color:#c8d2da; background:#fbfcfd;}
.ag-avatar {width:44px; height:44px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; background:#e3e8ec; color:#4b5f6d; flex:none;}
.ag-pname {font-weight:750; color:var(--text);} .ag-prole {color:var(--accent-dark); font-size:.84rem; font-weight:650;}
.ag-pfocus {color:var(--muted); font-size:.84rem;} .ag-plinks a {color:var(--blue); font-size:.84rem; margin-right:10px;}
.ag-brand {font-weight:850; letter-spacing:.08em; color:var(--text)!important; font-size:1.02rem;}

@media (max-width:900px) {.ag-pipe{grid-template-columns:repeat(3,1fr);}}
</style>"""

SHIELD = ('<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#536a7a" stroke-width="1.8" '
          'stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3z"/>'
          '<path d="M8.5 12l2.5 2.5 4.5-5" stroke="#5c866c"/></svg>')

STATUS = {
    "ready_for_approval": ("Verification passed", "green"),
    "verification_failed": ("Verification failed", "red"),
    "escalated_to_human": ("Human review required", "amber"),
    "unconfirmed": ("Not confirmed", "amber"),
    "no_vulnerability_found": ("No vulnerability found", "grey"),
    "confirmed": ("Vulnerability confirmed", "red"),
    "triaged": ("Triaged", "blue"),
}
SEVERITY = {"critical": "red", "high": "amber", "medium": "blue", "low": "grey"}


def setup():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, eyebrow: str = "Security assessment"):
    st.markdown(
        f'<div class="ag-hero"><div class="ag-eyebrow">{html.escape(eyebrow)}</div>'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def upload_intro():
    st.markdown(
        '<div class="ag-upload-intro"><div class="ag-upload-icon">↑</div><div>'
        '<div class="ag-upload-title">Upload a Python project</div>'
        '<div class="ag-upload-copy">Drop a single <b>.py</b> file or a <b>.zip</b> project below. '
        'AegisGuard reads the source, scans supported vulnerability patterns, and can generate a suggested patch without executing the uploaded code.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def chip(text: str, color: str) -> str:
    return f'<span class="ag-chip ag-{color}">{html.escape(text)}</span>'


def status_chip(status: str) -> str:
    label, color = STATUS.get(status, (str(status), "grey"))
    return chip(label, color)


def severity_chip(severity: str) -> str:
    return chip(severity or "medium", SEVERITY.get((severity or "medium").lower(), "grey"))


def section(label: str):
    st.markdown(f'<div class="ag-section">{html.escape(label)}</div>', unsafe_allow_html=True)


def banner(text: str, kind: str):
    st.markdown(f'<div class="ag-banner ag-banner-{kind}">{html.escape(text)}</div>', unsafe_allow_html=True)


def note(text: str):
    st.markdown(f'<div class="ag-note">{html.escape(text)}</div>', unsafe_allow_html=True)


def pipeline_html(r=None, approved: bool = False) -> str:
    r = r or {}
    er, vr = r.get("exploit_result"), r.get("verify_result")
    steps = [
        ("Triage", "identify issue", "done" if r.get("sink") else "pend"),
        ("Exploit", "generate test", "done" if r.get("exploit_test") else "pend"),
        ("Confirm", "prove finding", ("done" if er["expected"] else "fail") if er else "pend"),
        ("Patch", "propose fix", "done" if r.get("patched_source") else "pend"),
        ("Verify", "run tests", ("done" if vr["passed"] else "fail") if vr else "pend"),
        ("Approve", "human review", "done" if approved else "pend"),
    ]
    if r and not any(s[2] == "fail" for s in steps):
        for i, (_, _, state) in enumerate(steps):
            if state == "pend" and (i == 0 or steps[i - 1][2] == "done"):
                steps[i] = (steps[i][0], steps[i][1], "active")
                break
    return '<div class="ag-pipe">' + "".join(
        f'<div class="ag-node {state}">{html.escape(name)}<small>{html.escape(hint)}</small></div>'
        for name, hint, state in steps
    ) + "</div>"


def terminal(lines):
    body = "<br>".join(
        f'<span class="p">&gt;</span> {html.escape(str(line))}' for line in lines
    ) or '<span class="p">&gt;</span> No run activity yet.'
    st.markdown(f'<div class="ag-term">{body}</div>', unsafe_allow_html=True)


def initials(name: str) -> str:
    return "".join(w[0] for w in re.findall(r"[A-Za-z]+", name)[:2]).upper() or "?"


def person_html(p: dict, leader: bool = False) -> str:
    links = " ".join(
        f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>'
        for label, url in (p.get("links") or {}).items() if str(url).startswith("https://")
    )
    name = p.get("name", "")
    return (
        f'<div class="ag-person{" ag-leader" if leader else ""}"><div class="ag-avatar">{html.escape(initials(name))}</div>'
        f'<div><div class="ag-pname">{html.escape(name)}</div><div class="ag-prole">{html.escape(p.get("role", ""))}</div>'
        f'<div class="ag-pfocus">{html.escape(p.get("bio") or p.get("focus") or "")}</div>'
        f'<div class="ag-plinks">{links}</div></div></div>'
    )


def show_sources(sources):
    for c in sources:
        head, _, body = c["text"].partition("\n")
        with st.container(border=True):
            st.markdown(
                f"**{c.get('title', c['source'])}: {head.lstrip('# ').strip()}**  \n"
                f"`{c['source']}` | relevance {c['score']}"
            )
            st.markdown(body.strip() or head)
