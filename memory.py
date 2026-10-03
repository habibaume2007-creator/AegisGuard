"""Long-term memory: every run is saved in a local SQLite file (memory.db)."""
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "memory.db"
VERIFIED = "ready_for_approval"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, vuln_type TEXT, function TEXT,
        outcome TEXT, attempts INTEGER, exploit_test TEXT, patch TEXT, note TEXT)""")
    return c


def save_run(vuln_type, function, outcome, attempts, exploit_test="", patch="", note=""):
    with _conn() as c:
        c.execute("INSERT INTO runs (ts, vuln_type, function, outcome, attempts, exploit_test, patch, note) "
                  "VALUES (?,?,?,?,?,?,?,?)",
                  (time.strftime("%Y-%m-%d %H:%M:%S"), vuln_type, function, outcome,
                   attempts, exploit_test, patch, note))


def similar_successes(vuln_type, limit=1):
    """Most recent runs of this vulnerability type whose fix passed verification."""
    with _conn() as c:
        rows = c.execute("SELECT * FROM runs WHERE vuln_type=? AND outcome=? AND patch != '' "
                         "ORDER BY id DESC LIMIT ?", (vuln_type, VERIFIED, limit)).fetchall()
    return [dict(r) for r in rows]


def latest_verified(vuln_type, function):
    """The most recent verified run (with its exploit test and patch) for this function, or None."""
    with _conn() as c:
        row = c.execute("SELECT * FROM runs WHERE vuln_type=? AND function=? AND outcome=? "
                        "AND patch != '' AND exploit_test != '' ORDER BY id DESC LIMIT 1",
                        (vuln_type, function, VERIFIED)).fetchone()
    return dict(row) if row else None


def recent_failures(vuln_type, limit=2):
    """Recent failed runs (with a note about why), so the agent can avoid repeating them."""
    with _conn() as c:
        rows = c.execute("SELECT * FROM runs WHERE vuln_type=? AND outcome != ? AND note != '' "
                         "ORDER BY id DESC LIMIT ?", (vuln_type, VERIFIED, limit)).fetchall()
    return [dict(r) for r in rows]


def stats():
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        ok = c.execute("SELECT COUNT(*) FROM runs WHERE outcome=?", (VERIFIED,)).fetchone()[0]
    return {"total": total, "verified": ok, "rate": round(100 * ok / total) if total else 0}


def all_runs(limit=30):
    with _conn() as c:
        rows = c.execute("SELECT id, ts, vuln_type, function, outcome, attempts FROM runs "
                         "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def get_run(run_id):
    """Full record of one run (exploit test, patch, note)."""
    with _conn() as c:
        row = c.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    return dict(row) if row else None


def outcome_counts():
    with _conn() as c:
        rows = c.execute("SELECT outcome, COUNT(*) AS n FROM runs GROUP BY outcome").fetchall()
    return {r["outcome"]: r["n"] for r in rows}