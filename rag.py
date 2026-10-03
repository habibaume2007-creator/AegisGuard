"""Tiny RAG: retrieves security guidance from knowledge/*.md using TF-IDF similarity.
Pure Python, no extra packages, no embedding model (works on low-memory laptops)."""
import math
import re
from collections import Counter
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


STOPWORDS = {"a", "an", "the", "is", "are", "was", "to", "of", "in", "on", "for", "and", "or", "it", "this",
             "that", "do", "does", "why", "what", "how", "can", "i", "you", "my", "me", "be", "with", "as", "by"}


def _tokens(text: str) -> list:
    return [t for t in re.findall(r"[a-z0-9_]+", text.lower()) if t not in STOPWORDS]


def _load_chunks() -> list:
    """One chunk per '## section' of every markdown file."""
    chunks = []
    for f in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text else f.stem
        for part in re.split(r"\n(?=## )", text):
            part = part.strip()
            if len(part) > 40:
                chunks.append({"source": f.name, "text": part, "title": title})
    return chunks


def retrieve(query: str, k: int = 2) -> list:
    """Return the k most relevant chunks as [{'source', 'text', 'score'}]."""
    chunks = _load_chunks()
    if not chunks:
        return []
    docs = [Counter(_tokens(c["title"] + " " + c["text"])) for c in chunks]
    df = Counter()
    for d in docs:
        df.update(d.keys())
    n = len(docs)

    def vec(counter):
        return {t: (1 + math.log(c)) * (math.log((n + 1) / (df.get(t, 0) + 1)) + 1)
                for t, c in counter.items()}

    def cos(a, b):
        dot = sum(a[t] * b.get(t, 0.0) for t in a)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    q = vec(Counter(_tokens(query)))
    scored = sorted(((cos(q, vec(d)), c) for d, c in zip(docs, chunks)),
                    key=lambda x: x[0], reverse=True)
    return [{"source": c["source"], "title": c["title"], "text": c["text"], "score": round(s, 3)}
            for s, c in scored[:k] if s > 0]


def list_notes() -> list:
    """Overview of the knowledge base: [{'source', 'title', 'sections'}]."""
    notes = {}
    for c in _load_chunks():
        n = notes.setdefault(c["source"], {"source": c["source"], "title": c["title"], "sections": 0})
        n["sections"] += 1
    return list(notes.values())