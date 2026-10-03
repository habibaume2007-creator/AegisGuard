"""LangGraph workflow: triage -> exploit -> sandbox -> patch -> verify -> record.
The human approval step happens in app.py (the graph stops at 'ready_for_approval')."""
import json
import operator
import re
import time
from typing import Annotated, NotRequired, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

import config
import memory
import rag
import sandbox
from graph_builder import build_call_graph, find_vulns, paths_to

USAGE = {"calls": 0, "approx_tokens": 0}   # rough Gemini usage this session (shown in the sidebar)

VULN_INFO = {
    "sql_injection": {"name": "SQL injection",
                      "fix": "use parameterized queries (placeholders) and never build SQL from strings"},
    "path_traversal": {"name": "path traversal",
                       "fix": "resolve the final path and refuse anything outside the allowed folder"},
    "xss": {"name": "cross-site scripting (XSS)",
            "fix": "escape the user's value before putting it into HTML"},
    "unsafe_deserialization": {"name": "unsafe deserialization",
            "fix": "do not deserialize untrusted data with pickle; use JSON or yaml.safe_load for untrusted structured data"},
}


class AgentState(TypedDict):
    # Present from initial_state().
    sample: str
    source: str
    regression_tests: str
    attack_hint: str
    log: Annotated[list[str], operator.add]

    # Added progressively by LangGraph nodes.
    sink: NotRequired[str]
    paths: NotRequired[list]
    vuln_type: NotRequired[str]
    vuln_name: NotRequired[str]
    guidance: NotRequired[list]
    past_fixes: NotRequired[list]
    exploit_test: NotRequired[str]
    exploit_result: NotRequired[dict]
    exploit_attempts: NotRequired[int]
    patched_source: NotRequired[str]
    verify_result: NotRequired[dict]
    patch_attempts: NotRequired[int]
    status: NotRequired[str]
    replayed: NotRequired[bool]


# ---------- helpers ----------
def get_llm(model: str = ""):
    return ChatGoogleGenerativeAI(
        model=model or config.GEMINI_MODEL, google_api_key=config.GOOGLE_API_KEY, temperature=0
    )


def is_rate_limit(error) -> bool:
    text = str(error)
    return "429" in text or "RESOURCE_EXHAUSTED" in text


def is_daily_limit(error) -> bool:
    text = str(error).lower()
    return "perday" in text or "per day" in text


def ask(prompt: str) -> str:
    """Call Gemini. On a 429 rate limit: wait and retry, then try the fallback model (if set)."""
    models = [config.GEMINI_MODEL]
    if config.GEMINI_FALLBACK_MODEL and config.GEMINI_FALLBACK_MODEL != config.GEMINI_MODEL:
        models.append(config.GEMINI_FALLBACK_MODEL)
    last: Exception | None = None
    for model in models:
        for wait in (0, 10):                      # one retry after 10 seconds
            if wait:
                time.sleep(wait)
            try:
                content = get_llm(model).invoke(prompt).content
                if isinstance(content, list):     # some models return a list of parts
                    content = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
                USAGE["calls"] += 1
                USAGE["approx_tokens"] += (len(prompt) + len(content)) // 4
                return content
            except Exception as e:
                last = e
                if not is_rate_limit(e):
                    raise
                if is_daily_limit(e):         # a daily quota will not recover in 10 seconds
                    break
    if last is not None:
        raise last
    raise RuntimeError("Gemini request failed without returning an exception.")


def extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return (match.group(1) if match else text).strip() + "\n"


BAD_SETUP = ("ModuleNotFoundError", "ImportError", "SyntaxError", "NameError", "no tests ran")


def is_expected_failure(result: dict) -> bool:
    """The exploit test must FAIL because the vulnerability exists, not because of a setup error."""
    out = result["output"]
    return (result["exit_code"] == 1 and "test_exploit.py" in out
            and "FAILED" in out and not any(b in out for b in BAD_SETUP))


def tail(text: str, n: int = 0) -> str:
    n = n or (500 if config.LOW_TOKEN_MODE else 1000)
    return text[-n:]


# ---------- samples (the demo apps a judge can choose from) ----------
def list_samples() -> dict:
    out = {}
    if config.SAMPLES_DIR.exists():
        for d in sorted(config.SAMPLES_DIR.iterdir()):
            meta = d / "meta.json"
            if meta.exists():
                out[d.name] = json.loads(meta.read_text(encoding="utf-8"))
    return out


def initial_state(sample: str = "sql_injection") -> AgentState:
    d = config.SAMPLES_DIR / sample
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    return {
        "sample": sample,
        "source": (d / "target_sample.py").read_text(encoding="utf-8"),
        "regression_tests": (d / "test_target.py").read_text(encoding="utf-8"),
        "attack_hint": meta.get("attack_hint", ""),
        "log": [],
    }


# ---------- nodes ----------
def triage_node(state: AgentState) -> AgentState:
    vulns = find_vulns(state["source"])
    if not vulns:
        return {"status": "no_vulnerability_found", "log": ["Triage: no known vulnerability pattern found."]}
    vuln_type, sink = vulns[0]
    info = VULN_INFO.get(vuln_type, {"name": vuln_type, "fix": "apply the standard secure fix"})
    G = build_call_graph(state["source"])
    paths = paths_to(G, sink)
    msg = f"Triage: {info['name']} in '{sink}'. "
    msg += ("Reachable via " + " -> ".join(paths[0])) if paths else "No public route reaches it (low priority)."
    return {"sink": sink, "paths": paths, "vuln_type": vuln_type, "vuln_name": info["name"],
            "status": "triaged", "log": [msg]}


def exploit_node(state: AgentState) -> AgentState:
    n = state.get("exploit_attempts", 0) + 1
    feedback = ""
    prev = state.get("exploit_result")
    if prev and not prev.get("expected"):
        feedback = ("\nYour previous test was not a valid exploit test. Pytest output:\n"
                    + tail(prev["output"]) + "\nFix the test.\n")
    prompt = f"""You are a security engineer writing a reproduction test.
The module under test is `target_sample.py`:
```python
{state['source']}
```
Vulnerability: {state['vuln_name']} in `{state['sink']}`.
Hint about the attack: {state.get('attack_hint', '')}
Write ONE pytest test file (test_exploit.py) with one test that FAILS on the vulnerable code
and PASSES once the vulnerability is properly fixed. Import with `from target_sample import ...`.
Assert the SAFE behavior. Make sure a correct fix really makes the test pass: do not assert on
text that could still appear harmlessly after a fix.
Rules: no network, no file writes, no subprocess, do not modify the module.
Reply with a single ```python code block and nothing else.{feedback}"""
    code = extract_code(ask(prompt))
    return {"exploit_test": code, "exploit_attempts": n,
            "log": [f"Exploit agent: generated test (attempt {n})."]}


def run_exploit_node(state: AgentState) -> AgentState:
    result = sandbox.run_pytest(
        {"target_sample.py": state["source"], "test_exploit.py": state["exploit_test"]},
        ["test_exploit.py"],
    )
    result["expected"] = is_expected_failure(result)
    msg = ("Sandbox: exploit test FAILED as expected -> vulnerability confirmed (RED)."
           if result["expected"] else "Sandbox: exploit test did not fail for the right reason.")
    return {"exploit_result": result,
            "status": "confirmed" if result["expected"] else "unconfirmed",
            "log": [f"{msg} [{result['mode']}]"]}


def patch_node(state: AgentState) -> AgentState:
    n = state.get("patch_attempts", 0) + 1
    feedback = ""
    prev = state.get("verify_result")
    if prev and not prev["passed"]:
        feedback = "\nYour previous patch FAILED verification. Pytest output:\n" + tail(prev["output"]) + "\n"
    vuln = state.get("vuln_type", "sql_injection")
    info = VULN_INFO.get(vuln, {"name": vuln, "fix": "apply the standard secure fix"})
    guidance = rag.retrieve(f"{info['name']} fix", k=1 if config.LOW_TOKEN_MODE else 2)   # RAG
    past = [] if config.LOW_TOKEN_MODE else memory.similar_successes(vuln, limit=1)       # long-term memory
    failures = [] if config.LOW_TOKEN_MODE else memory.recent_failures(vuln, limit=2)
    context = ""
    if guidance:
        context += "\nSecurity guidance (retrieved):\n" + "\n\n".join(
            f"[{g['source']}]\n{g['text'][:700]}" for g in guidance) + "\n"
    if past:
        context += ("\nA previously verified fix for a similar issue (reference only):\n```python\n"
                    + past[0]["patch"][:1000] + "\n```\n")
    if failures:
        context += "\nEarlier attempts that FAILED, so do not repeat them:\n" + "\n".join(
            "- " + f["note"][:300] for f in failures) + "\n"
    prompt = f"""Fix the {info['name']} vulnerability in `{state['sink']}` in this file.
```python
{state['source']}
```
Failing exploit test:
```python
{state['exploit_test']}
```
Pytest output on the vulnerable code:
{tail(state['exploit_result']['output'])}
{context}
Rules: {info['fix']}; keep every function name, signature and route unchanged;
change nothing else. Reply with the COMPLETE corrected file in a single ```python block.{feedback}"""
    code = extract_code(ask(prompt))
    return {"patched_source": code, "patch_attempts": n, "guidance": guidance,
            "past_fixes": [{"ts": p["ts"], "function": p["function"]} for p in past],
            "log": [f"Patch agent: proposed fix (attempt {n}); {len(guidance)} guidance note(s), "
                    f"{len(past)} past fix(es) used."]}


def verify_node(state: AgentState) -> AgentState:
    result = sandbox.run_pytest(
        {"target_sample.py": state["patched_source"],
         "test_exploit.py": state["exploit_test"],
         "test_target.py": state["regression_tests"]},
        ["test_exploit.py", "test_target.py"],
    )
    result["passed"] = result["exit_code"] == 0
    result["static_clean"] = not find_vulns(state["patched_source"])
    if result["passed"]:
        return {"verify_result": result, "status": "ready_for_approval",
                "log": ["Verifier: exploit test and regression tests all PASS (GREEN)."]}
    return {"verify_result": result, "status": "verification_failed",
            "log": ["Verifier: verification FAILED."]}


# ---------- routing ----------
def after_triage(state: AgentState) -> str:
    return "exploit" if state.get("sink") else "end"


def after_run_exploit(state: AgentState) -> str:
    if state["exploit_result"]["expected"]:
        return "patch"
    return "exploit" if state["exploit_attempts"] < config.MAX_ATTEMPTS else "end"


def after_verify(state: AgentState) -> str:
    if state["verify_result"]["passed"]:
        return "end"
    if state["patch_attempts"] < config.MAX_ATTEMPTS:
        return "patch"
    return "escalate"


def escalate_node(state: AgentState) -> AgentState:
    return {"status": "escalated_to_human",
            "log": ["Max attempts reached: escalating to a human reviewer."]}


def record_node(state: AgentState) -> AgentState:
    """Save this run to long-term memory (success or failure)."""
    status = state.get("status", "unknown")
    note = ""
    if status in ("verification_failed", "escalated_to_human"):
        note = tail((state.get("verify_result") or {}).get("output", ""), 600)
    elif status == "unconfirmed":
        note = tail((state.get("exploit_result") or {}).get("output", ""), 600)
    try:
        memory.save_run(state.get("vuln_type", "unknown"), state.get("sink", ""), status,
                        state.get("patch_attempts", 0), state.get("exploit_test", ""),
                        state.get("patched_source", ""), note)
        return {"log": ["Memory: run saved to long-term memory."]}
    except Exception as e:
        return {"log": [f"Memory: could not save run ({e})."]}


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("triage", triage_node)
    g.add_node("exploit", exploit_node)
    g.add_node("run_exploit", run_exploit_node)
    g.add_node("patch", patch_node)
    g.add_node("verify", verify_node)
    g.add_node("escalate", escalate_node)
    g.add_node("record", record_node)
    g.set_entry_point("triage")
    g.add_conditional_edges("triage", after_triage, {"exploit": "exploit", "end": END})
    g.add_edge("exploit", "run_exploit")
    g.add_conditional_edges("run_exploit", after_run_exploit,
                            {"patch": "patch", "exploit": "exploit", "end": "record"})
    g.add_edge("patch", "verify")
    g.add_conditional_edges("verify", after_verify,
                            {"patch": "patch", "escalate": "escalate", "end": "record"})
    g.add_edge("escalate", "record")
    g.add_edge("record", END)
    return g.compile()


def replay_run(sample: str) -> AgentState:
    """Re-run the last VERIFIED exploit test and patch for this sample from long-term memory.
    No Gemini calls: the sandbox executes the saved code again, so the red-to-green proof is real.
    """
    state = initial_state(sample)
    rows = memory.similar_successes(sample, limit=1)
    if not rows:
        raise ValueError("No verified run is saved for this sample yet. Run it once with Gemini first.")

    row = rows[0]

    # Triage returns a partial workflow update; merge it into the existing state.
    state.update(triage_node(state))

    previous_log = state.pop("log", [])
    log = list(previous_log) + [f"Replay: using the verified run saved on {row['ts']}."]

    # Keep these as local variables as well as state fields. This makes their
    # presence explicit to static type checkers such as Pylance.
    exploit_test = str(row["exploit_test"])
    patched_source = str(row["patch"])
    state.update({
        "exploit_test": exploit_test,
        "patched_source": patched_source,
        "replayed": True,
    })

    res = sandbox.run_pytest(
        {
            "target_sample.py": state["source"],
            "test_exploit.py": exploit_test,
        },
        ["test_exploit.py"],
    )
    res["expected"] = is_expected_failure(res)
    state["exploit_result"] = res

    log.append(
        "Sandbox: saved exploit test FAILED on the vulnerable code (RED)."
        if res["expected"]
        else "Sandbox: saved exploit test did not fail as expected."
    )

    if not res["expected"]:
        state["status"] = "unconfirmed"
        state["log"] = log
        return state

    ver = sandbox.run_pytest(
        {
            "target_sample.py": patched_source,
            "test_exploit.py": exploit_test,
            "test_target.py": state["regression_tests"],
        },
        ["test_exploit.py", "test_target.py"],
    )
    ver["passed"] = ver["exit_code"] == 0
    ver["static_clean"] = not find_vulns(patched_source)

    state["verify_result"] = ver
    vuln_name = state.get("vuln_name", "vulnerability")
    state["guidance"] = rag.retrieve(f"{vuln_name} fix", k=2)

    log.append(
        "Verifier: saved patch passes the exploit test and regression tests (GREEN)."
        if ver["passed"]
        else "Verifier: saved patch FAILED verification."
    )

    state["status"] = "ready_for_approval" if ver["passed"] else "verification_failed"
    state["log"] = log
    return state
