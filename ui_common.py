"""Shared light professional UI theme and helpers used by every AegisGuard page."""
import html
import json
import re

import streamlit as st

import config

ABOUT = json.loads((config.BASE_DIR / "about.json").read_text(encoding="utf-8"))

CSS = r"""<style>
/* =====================================================================
   AegisGuard design tokens
   ===================================================================== */
:root {
  --bg:#f5f7fb;
  --surface:#ffffff;
  --surface-2:#f8fafc;
  --surface-3:#eef2f7;
  --line:#e3e8ef;
  --line-strong:#cbd5e1;
  --text:#0f172a;
  --text-2:#475569;
  --muted:#64748b;

  --accent:#2f54d6;
  --accent-dark:#2443b8;
  --accent-soft:#eef2ff;
  --accent-line:#c7d2fe;

  --green:#16a34a;  --green-ink:#166534;  --green-soft:#ecfdf3;  --green-line:#b9e8cb;
  --red:#dc3d33;    --red-ink:#b42318;    --red-soft:#fef3f2;    --red-line:#f8c9c4;
  --amber:#d97706;  --amber-ink:#b45309;  --amber-soft:#fffaeb;  --amber-line:#f5dba3;
  --blue:#2563eb;   --blue-ink:#1d4ed8;   --blue-soft:#eff6ff;   --blue-line:#bfd6fb;
  --grey:#64748b;   --grey-ink:#475569;   --grey-soft:#f1f5f9;   --grey-line:#d8e0ea;

  --shadow-sm:0 1px 2px rgba(15,23,42,.05);
  --shadow:0 1px 2px rgba(15,23,42,.04), 0 10px 28px -8px rgba(15,23,42,.10);
  --mono:ui-monospace,"Cascadia Code","JetBrains Mono",Consolas,"Courier New",monospace;
}

/* =====================================================================
   App shell
   ===================================================================== */
#MainMenu, footer {visibility:hidden;}
html, body {font-family: Inter, "Segoe UI", system-ui, -apple-system, Arial, sans-serif;}
.stApp {background:var(--bg); color:var(--text);}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stDecoration"] {display:none;}
.block-container, [data-testid="stMainBlockContainer"] {
  padding-top:2.25rem;
  padding-bottom:4rem;
  max-width:1240px;
}
::selection {background:#dbe4ff;}
hr {border-color:var(--line)!important;}

/* =====================================================================
   Typography (forced so text stays readable on every OS theme)
   ===================================================================== */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] span:not([class*="ag-"]),
[data-testid="stWidgetLabel"] {color:var(--text)!important;}
[data-testid="stWidgetLabel"] [data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p {color:var(--text-2)!important; font-weight:600; font-size:.86rem;}
h1,h2,h3,h4,h5,h6 {color:var(--text)!important; letter-spacing:-.02em; font-weight:700;}
[data-testid="stMarkdownContainer"] h3 {font-size:1.28rem; margin:.1rem 0 .1rem; padding:.2rem 0 .3rem;}
[data-testid="stMarkdownContainer"] h4 {font-size:1.1rem; margin-top:.6rem;}
[data-testid="stMarkdownContainer"] h5 {font-size:.98rem;}
[data-testid="stCaptionContainer"],
.stCaption,
[data-testid="stCaptionContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"] p {color:var(--muted)!important; font-size:.84rem; line-height:1.5;}
[data-testid="stMarkdownContainer"] :not(pre) > code {
  color:#334155!important;
  background:#eef2f7!important;
  border:1px solid #e2e8f0;
  border-radius:6px;
  padding:.08em .4em;
  font-size:.86em;
}

/* =====================================================================
   Sidebar
   ===================================================================== */
[data-testid="stSidebar"] {
  background:#ffffff;
  border-right:1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child {background:#ffffff;}
[data-testid="stSidebar"] hr {border-color:var(--line)!important; margin:.9rem 0;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] svg {vertical-align:middle; margin-right:8px;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {font-size:.92rem;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {font-size:.8rem;}
[data-testid="stSidebarNavLink"] {
  border-radius:10px;
  margin:2px 8px;
  padding-top:.55rem;
  padding-bottom:.55rem;
  transition:background .15s ease;
}
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavLink"] span {color:var(--text-2)!important; font-weight:600;}
[data-testid="stSidebarNavLink"]:hover {background:var(--surface-3);}
[data-testid="stSidebarNavLink"][aria-current="page"] {background:var(--accent-soft);}
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"] span {color:var(--accent-dark)!important;}
.ag-brand {
  font-weight:800;
  letter-spacing:.14em;
  color:var(--text)!important;
  font-size:1.02rem;
  vertical-align:middle;
}

/* =====================================================================
   Buttons
   ===================================================================== */
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"] {
  border-radius:10px;
  font-weight:600;
  min-height:2.6rem;
  box-shadow:none;
  transition:background .15s ease, border-color .15s ease, box-shadow .15s ease, transform .05s ease;
}
[data-testid="stBaseButton-secondary"] {
  background:var(--surface);
  border:1px solid var(--line-strong);
}
.stApp button[data-testid="stBaseButton-secondary"] * {color:var(--text)!important;}
[data-testid="stBaseButton-secondary"]:hover {
  border-color:var(--accent);
  background:#f8faff;
  box-shadow:var(--shadow-sm);
}
[data-testid="stBaseButton-secondary"]:disabled {
  background:var(--accent-soft)!important;
  border-color:var(--accent-line)!important;
  box-shadow:none;
  opacity:1;
  cursor:default;
}
.stApp button[data-testid="stBaseButton-secondary"]:disabled * {color:var(--accent-dark)!important;}
[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {
  background:var(--accent);
  color:#ffffff!important;
  border:1px solid var(--accent);
  box-shadow:0 1px 2px rgba(15,23,42,.10), 0 8px 16px -6px rgba(47,84,214,.45);
}
.stApp button[data-testid="stBaseButton-primary"] *,
.stButton > button[kind="primary"] * {color:#ffffff!important;}
[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover {
  background:var(--accent-dark);
  border-color:var(--accent-dark);
}
[data-testid="stBaseButton-primary"]:active,
[data-testid="stBaseButton-secondary"]:active {transform:translateY(1px);}

/* =====================================================================
   Inputs
   ===================================================================== */
[data-baseweb="input"],
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"],
textarea {
  background:#ffffff!important;
  border-color:var(--line-strong)!important;
  border-radius:10px!important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"]:focus-within {
  border-color:var(--accent)!important;
  box-shadow:0 0 0 3px rgba(47,84,214,.14);
}
input, textarea {color:var(--text)!important;}
input::placeholder, textarea::placeholder {color:#94a3b8!important;}
[data-baseweb="popover"] > div {border-radius:12px; box-shadow:var(--shadow);}

/* =====================================================================
   Tabs
   ===================================================================== */
[data-baseweb="tab-list"] {gap:6px; border-bottom:1px solid var(--line);}
[data-baseweb="tab"] {
  height:46px;
  padding:0 18px;
  border-radius:10px 10px 0 0;
  color:var(--muted)!important;
  font-weight:650;
  transition:color .15s ease, background .15s ease;
}
[data-baseweb="tab"] [data-testid="stMarkdownContainer"] p {color:inherit!important; font-weight:inherit; font-size:.95rem;}
[data-baseweb="tab"]:hover {color:var(--text)!important; background:var(--surface-3);}
[data-baseweb="tab"][aria-selected="true"] {color:var(--accent-dark)!important; background:transparent;}
[data-baseweb="tab-highlight"] {background:var(--accent)!important; height:3px!important; border-radius:3px 3px 0 0;}
[data-baseweb="tab-border"] {background:var(--line)!important;}

/* =====================================================================
   File uploader (primary call to action)
   ===================================================================== */
[data-testid="stFileUploader"] {
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:16px;
  box-shadow:var(--shadow);
  padding:6px;
}
[data-testid="stFileUploaderDropzone"] {
  background:var(--surface-2)!important;
  border:1.5px dashed #b6c2d2!important;
  border-radius:12px!important;
  min-height:150px;
  transition:border-color .15s ease, background .15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color:var(--accent)!important;
  background:var(--accent-soft)!important;
}
[data-testid="stFileUploaderDropzone"] * {color:var(--text)!important;}

/* =====================================================================
   Metrics, expanders, tables, code, alerts
   ===================================================================== */
[data-testid="stMetric"] {
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:14px;
  padding:16px 18px;
  box-shadow:var(--shadow-sm);
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMetricLabel"] {color:var(--muted)!important; font-weight:650; font-size:.82rem;}
[data-testid="stMetricValue"] {color:var(--text)!important; font-weight:750; letter-spacing:-.02em;}

[data-testid="stExpander"] {
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:12px;
  box-shadow:var(--shadow-sm);
  overflow:hidden;
}
[data-testid="stExpander"] details {border:none!important; background:transparent!important;}
[data-testid="stExpander"] summary {font-weight:650; transition:background .15s ease;}
[data-testid="stExpander"] summary:hover {background:var(--surface-2);}

[data-testid="stDataFrame"] {
  background:var(--surface);
  border-radius:12px;
  overflow:hidden;
  box-shadow:var(--shadow-sm);
}
[data-testid="stTable"] {
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:12px;
  overflow:hidden;
  box-shadow:var(--shadow-sm);
}
[data-testid="stTable"] table {width:100%; border-collapse:collapse; border:none;}
[data-testid="stTable"] th {
  background:var(--surface-2)!important;
  color:var(--muted)!important;
  font-size:.74rem;
  font-weight:750;
  letter-spacing:.07em;
  text-transform:uppercase;
  padding:11px 16px!important;
  border:none!important;
  border-bottom:1px solid var(--line)!important;
  text-align:left;
}
[data-testid="stTable"] td {
  padding:11px 16px!important;
  border:none!important;
  border-bottom:1px solid var(--surface-3)!important;
  color:var(--text)!important;
  font-size:.92rem;
}
[data-testid="stTable"] tr:last-child td {border-bottom:none!important;}
[data-testid="stTable"] tbody tr:hover td {background:var(--surface-2);}

[data-testid="stCode"] {
  border:1px solid var(--line);
  border-radius:12px;
  overflow:hidden;
  box-shadow:var(--shadow-sm);
}
[data-testid="stCode"] pre {font-size:.82rem; line-height:1.6;}
[data-testid="stGraphVizChart"] {
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:12px;
  padding:10px;
  box-shadow:var(--shadow-sm);
  overflow-x:auto;
}
[data-testid="stAlert"],
[data-testid="stAlertContainer"] {border-radius:12px;}

/* =====================================================================
   Hero header
   ===================================================================== */
.ag-hero {
  position:relative;
  overflow:hidden;
  background:linear-gradient(135deg,#ffffff 0%,#f6f8ff 100%);
  border:1px solid var(--line);
  border-radius:18px;
  padding:28px 32px 28px 36px;
  margin:0 0 22px;
  box-shadow:var(--shadow);
}
.ag-hero::before {
  content:"";
  position:absolute;
  left:0; top:0; bottom:0;
  width:5px;
  background:linear-gradient(180deg,var(--accent),#7c97ff);
}
.ag-hero::after {
  content:"";
  position:absolute;
  right:-70px; top:-80px;
  width:260px; height:260px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(47,84,214,.11),rgba(47,84,214,0) 70%);
  pointer-events:none;
}
.ag-eyebrow {
  font-size:.72rem;
  font-weight:800;
  letter-spacing:.14em;
  color:var(--accent);
  text-transform:uppercase;
}
.ag-eyebrow::before {
  content:"";
  display:inline-block;
  width:7px; height:7px;
  border-radius:50%;
  background:var(--accent);
  margin-right:9px;
  vertical-align:middle;
  box-shadow:0 0 0 4px rgba(47,84,214,.14);
}
.ag-hero h1 {
  margin:8px 0 4px;
  padding:0;
  font-size:2.05rem;
  font-weight:780;
  letter-spacing:-.03em;
  line-height:1.15;
}
.ag-hero p {
  margin:10px 0 0;
  color:var(--text-2)!important;
  max-width:820px;
  line-height:1.65;
  font-size:1rem;
}

/* =====================================================================
   Section headers and panels
   ===================================================================== */
.ag-section {
  display:flex;
  align-items:center;
  gap:14px;
  font-size:.72rem;
  letter-spacing:.14em;
  color:var(--muted);
  text-transform:uppercase;
  font-weight:800;
  margin:30px 0 12px;
}
.ag-section::after {content:""; flex:1; height:1px; background:var(--line);}
.ag-panel {
  background:var(--surface);
  border:1px solid var(--line);
  border-left:4px solid var(--accent);
  border-radius:12px;
  padding:14px 18px;
  margin:12px 0 14px;
  box-shadow:var(--shadow-sm);
  color:var(--text-2);
  line-height:1.6;
}
.ag-note {
  background:var(--accent-soft);
  border:1px solid var(--accent-line);
  border-radius:12px;
  padding:12px 16px;
  color:#34408a;
  margin:8px 0 14px;
  line-height:1.55;
}

/* =====================================================================
   Upload callout
   ===================================================================== */
.ag-upload-intro {
  display:flex;
  gap:16px;
  align-items:flex-start;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:16px;
  padding:20px 22px;
  margin-bottom:12px;
  box-shadow:var(--shadow);
}
.ag-upload-icon {
  width:44px; height:44px;
  flex:none;
  border-radius:12px;
  background:linear-gradient(135deg,var(--accent),#6d8bff);
  color:#ffffff;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:1.3rem;
  font-weight:800;
  box-shadow:0 8px 16px -6px rgba(47,84,214,.5);
}
.ag-upload-title {font-weight:760; font-size:1.05rem; margin-bottom:4px; color:var(--text);}
.ag-upload-copy {font-size:.92rem; color:var(--text-2); line-height:1.6;}

/* =====================================================================
   Chips (soft badges)
   ===================================================================== */
.ag-chip {
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding:3px 11px 3px 9px;
  border-radius:999px;
  border:1px solid transparent;
  font-size:.68rem;
  font-weight:800;
  text-transform:uppercase;
  letter-spacing:.05em;
  line-height:1.55;
  white-space:nowrap;
  vertical-align:middle;
}
.ag-chip::before {content:""; width:6px; height:6px; border-radius:50%; background:currentColor; flex:none;}
.ag-red   {background:var(--red-soft);   color:var(--red-ink)!important;   border-color:var(--red-line);}
.ag-green {background:var(--green-soft); color:var(--green-ink)!important; border-color:var(--green-line);}
.ag-amber {background:var(--amber-soft); color:var(--amber-ink)!important; border-color:var(--amber-line);}
.ag-blue  {background:var(--blue-soft);  color:var(--blue-ink)!important;  border-color:var(--blue-line);}
.ag-grey  {background:var(--grey-soft);  color:var(--grey-ink)!important;  border-color:var(--grey-line);}
.ag-cwe {
  display:inline-block;
  font-size:.74rem;
  color:var(--muted)!important;
  margin-left:8px;
  padding:2px 8px;
  border-radius:6px;
  background:var(--surface-3);
  font-family:var(--mono);
  vertical-align:middle;
}

/* =====================================================================
   Banners
   ===================================================================== */
.ag-banner {
  padding:12px 16px;
  border-radius:12px;
  font-weight:600;
  margin:8px 0 12px;
  font-size:.88rem;
  line-height:1.55;
  border:1px solid;
  border-left-width:4px;
  box-shadow:var(--shadow-sm);
}
.ag-banner-red   {border-color:var(--red-line);   border-left-color:var(--red);   background:var(--red-soft);   color:var(--red-ink);}
.ag-banner-green {border-color:var(--green-line); border-left-color:var(--green); background:var(--green-soft); color:var(--green-ink);}
.ag-banner-amber {border-color:var(--amber-line); border-left-color:var(--amber); background:var(--amber-soft); color:var(--amber-ink);}

/* =====================================================================
   Remediation pipeline (stepper cards)
   ===================================================================== */
.ag-pipe {display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:10px; margin:10px 0 18px;}
.ag-node {
  position:relative;
  overflow:hidden;
  padding:15px 10px 13px;
  border-radius:12px;
  border:1px solid var(--line);
  background:var(--surface);
  font-size:.72rem;
  font-weight:800;
  letter-spacing:.07em;
  text-transform:uppercase;
  color:var(--muted);
  text-align:center;
  box-shadow:var(--shadow-sm);
}
.ag-node::before {content:""; position:absolute; left:0; right:0; top:0; height:3px; background:var(--line-strong);}
.ag-node small {display:block; margin-top:4px; font-size:.68rem; font-weight:500; letter-spacing:0; text-transform:none; color:var(--muted);}
.ag-node.done {border-color:var(--green-line); background:var(--green-soft); color:var(--green-ink);}
.ag-node.done::before {background:var(--green);}
.ag-node.done small {color:#4d8a67;}
.ag-node.fail {border-color:var(--red-line); background:var(--red-soft); color:var(--red-ink);}
.ag-node.fail::before {background:var(--red);}
.ag-node.fail small {color:#b0645d;}
.ag-node.active {
  border-color:var(--accent-line);
  background:var(--accent-soft);
  color:var(--accent-dark);
  box-shadow:0 0 0 3px rgba(47,84,214,.12);
}
.ag-node.active::before {background:var(--accent);}
.ag-node.active small {color:#5a6bb8;}

/* =====================================================================
   Agent activity console
   ===================================================================== */
.ag-term {
  background:#0f172a;
  border:1px solid #1e293b;
  border-radius:12px;
  padding:14px 16px;
  font-family:var(--mono);
  font-size:.8rem;
  color:#cbd5e1;
  line-height:1.65;
  overflow-x:auto;
  max-height:420px;
  overflow-y:auto;
  white-space:pre-wrap;
  box-shadow:var(--shadow);
}
div.ag-term span.p {color:#4ade80!important; font-weight:700;}

/* =====================================================================
   Team
   ===================================================================== */
.ag-team-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:14px; margin:8px 0 16px;}
.ag-person {
  display:flex;
  gap:16px;
  align-items:center;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:14px;
  padding:16px 18px;
  box-shadow:var(--shadow-sm);
  transition:box-shadow .18s ease, transform .18s ease, border-color .18s ease;
}
.ag-person:hover {box-shadow:var(--shadow); transform:translateY(-2px); border-color:var(--line-strong);}
.ag-leader {border-color:var(--accent-line); background:linear-gradient(135deg,#ffffff 0%,#f5f7ff 100%);}
.ag-avatar {
  width:46px; height:46px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:800;
  background:linear-gradient(135deg,#e0e7ff,#c7d2fe);
  color:var(--accent-dark);
  flex:none;
}
.ag-leader .ag-avatar {background:linear-gradient(135deg,var(--accent),#6d8bff); color:#ffffff;}
.ag-pname {font-weight:750; color:var(--text);}
.ag-prole {color:var(--accent-dark); font-size:.84rem; font-weight:650;}
.ag-pfocus {color:var(--muted); font-size:.84rem; line-height:1.5; margin-top:2px;}
.ag-plinks a {
  display:inline-block;
  margin:8px 6px 0 0;
  padding:3px 11px;
  border:1px solid var(--line);
  border-radius:999px;
  background:var(--surface-2);
  color:var(--accent-dark)!important;
  font-size:.78rem;
  font-weight:650;
  text-decoration:none!important;
  transition:background .15s ease, border-color .15s ease;
}
.ag-plinks a:hover {background:var(--accent-soft); border-color:var(--accent-line);}

@media (max-width:900px) {.ag-pipe{grid-template-columns:repeat(3,minmax(0,1fr));}}
@media (max-width:520px) {
  .ag-pipe{grid-template-columns:repeat(2,minmax(0,1fr));}
  .ag-hero{padding:22px 20px 22px 24px;}
  .ag-hero h1{font-size:1.65rem;}
}
</style>"""

SHIELD = ('<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2f54d6" stroke-width="1.8" '
          'stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3z"/>'
          '<path d="M8.5 12l2.5 2.5 4.5-5" stroke="#16a34a"/></svg>')

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