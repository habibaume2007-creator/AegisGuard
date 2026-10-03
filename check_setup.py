"""Run:  python check_setup.py
Checks everything AegisGuard needs, one step at a time, before you start Streamlit."""
import importlib
import subprocess
import sys


def step(name, fn):
    try:
        msg = fn()
        print(f"[PASS] {name}" + (f"  ({msg})" if msg else ""))
        return True
    except Exception as e:
        print(f"[FAIL] {name}\n       {type(e).__name__}: {str(e)[:400]}")
        return False


def imports():
    for m in ["langgraph", "langchain_google_genai", "networkx", "flask",
              "pytest", "streamlit", "dotenv", "docker"]:
        importlib.import_module(m)
    import streamlit
    major, minor = (int(x) for x in streamlit.__version__.split(".")[:2])
    if (major, minor) < (1, 36):
        raise RuntimeError("Streamlit is too old for the sidebar pages. Run: pip install -U streamlit")


def env():
    import config
    key = config.GOOGLE_API_KEY
    if not key or "your_gemini" in key:
        raise ValueError("GOOGLE_API_KEY is missing or still the placeholder in .env")
    return f"model={config.GEMINI_MODEL}, docker={config.USE_DOCKER}"


def target_tests():
    from pathlib import Path
    tests = sorted(Path("samples").glob("*/test_target.py"))
    if not tests:
        raise RuntimeError("no samples found in the samples/ folder")
    for t in tests:
        p = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_target.py"],
                           cwd=t.parent, capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"{t.parent.name}: " + (p.stdout + p.stderr)[-400:])
    return f"{len(tests)} samples: regression tests pass"

def sandbox_pass_fail():
    import sandbox
    ok = sandbox.run_pytest({"test_a.py": "def test_a():\n    assert 1 == 1\n"}, ["test_a.py"])
    bad = sandbox.run_pytest({"test_b.py": "def test_b():\n    assert 1 == 2\n"}, ["test_b.py"])
    if ok["exit_code"] != 0:
        raise RuntimeError(f"passing test returned {ok['exit_code']}: {ok['output'][-300:]}")
    if bad["exit_code"] != 1:
        raise RuntimeError(f"failing test returned {bad['exit_code']}: {bad['output'][-300:]}")
    return f"mode={ok['mode']}: pass=0, fail=1"


def sandbox_no_network():
    import config
    import sandbox
    if not config.USE_DOCKER:
        return "skipped (USE_DOCKER=false, local mode is not isolated)"
    code = ("import socket\n\ndef test_no_network():\n    try:\n"
            "        socket.create_connection(('1.1.1.1', 53), timeout=3)\n"
            "    except OSError:\n        return\n    assert False, 'network is reachable'\n")
    r = sandbox.run_pytest({"test_net.py": code}, ["test_net.py"])
    if r["exit_code"] != 0:
        raise RuntimeError("container can reach the network:\n" + r["output"][-300:])
    return "container has no network"


def gemini():
    from agent import ask
    return "reply: " + ask("Reply with the single word: ready").strip()[:30]


if __name__ == "__main__":
    results = [
        step("1. Packages import", imports),
        step("2. .env settings", env),
        step("3. Regression tests (all samples)", target_tests),
        step("4. Sandbox pass/fail", sandbox_pass_fail),
        step("5. Sandbox has no network", sandbox_no_network),
        step("6. Gemini responds", gemini),
    ]
    print("\nAll checks passed. Run: streamlit run app.py" if all(results)
          else "\nFix the first [FAIL] above, then run this again.")