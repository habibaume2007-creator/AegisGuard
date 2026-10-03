"""RAG question answering: retrieve notes from knowledge/, then ask Gemini to answer ONLY from them
(plus the saved run history from long-term memory)."""
import memory
import rag

_CACHE = {}   # same question + same notes -> reuse the answer (saves Gemini requests)


def _history() -> str:
    s = memory.stats()
    lines = [f"Run history: {s['total']} runs saved, {s['verified']} verified fixes ({s['rate']}%)."]
    for r in memory.all_runs(limit=5):
        lines.append(f"- {r['ts']}: {r['vuln_type']} in {r['function']} -> {r['outcome']} "
                     f"({r['attempts']} patch attempt(s))")
    return "\n".join(lines)


def ask_assistant(question: str, extra: str = "", query: str = "", k: int = 3) -> dict:
    """Returns {'answer', 'sources', 'used_llm'}. `query` overrides what is searched for."""
    chunks = rag.retrieve(query or question, k=k)
    if not chunks and not extra and memory.stats()["total"] == 0:
        return {"answer": "I could not find that in the knowledge base. Try asking about SQL injection, "
                          "path traversal, XSS, or how AegisGuard works.",
                "sources": [], "used_llm": False}
    notes = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks) or "(no matching notes)"
    prompt = f"""You are the AegisGuard security assistant. Answer using ONLY the notes and run history below.
If they do not cover the question, say you do not know. Explain simply for someone new to security,
in at most 150 words, and cite the note file names in square brackets, like [sql_injection.md].

Notes:
{notes}

{_history()}
""" + (f"\nExtra context (the code change being discussed):\n{extra}\n" if extra else "") + f"\nQuestion: {question}"
    key = (question.strip().lower(), tuple(c["source"] + c["text"][:30] for c in chunks), extra[:200], _history())
    if key in _CACHE:
        return _CACHE[key]
    try:
        from agent import ask, is_rate_limit
        result = {"answer": ask(prompt).strip(), "sources": chunks, "used_llm": True}
        _CACHE[key] = result
        return result
    except Exception as e:
        try:
            from agent import is_daily_limit, is_rate_limit
            limited, daily = is_rate_limit(e), is_daily_limit(e)
        except Exception:
            limited, daily = False, False
        if limited and daily:
            msg = ("Gemini's DAILY quota for this model is used up. It resets once a day, or you can switch "
                   "GEMINI_MODEL in .env to another model. Here are the most relevant notes meanwhile.")
        elif limited:
            msg = ("Gemini's request limit was reached (free-tier limit). Wait about a minute and ask again. "
                   "If it keeps happening, the daily quota may be used up. Here are the most relevant notes meanwhile.")
        else:
            msg = f"The language model is unavailable ({str(e)[:120]}). Here are the most relevant notes instead."
        return {"answer": msg, "sources": chunks, "used_llm": False}