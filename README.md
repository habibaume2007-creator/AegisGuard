# AegisGuard (hackathon MVP)

Run order:
1. `python -m venv venv` and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your `GOOGLE_API_KEY`
4. Start Docker Desktop (or set `USE_DOCKER=false` for local, non-isolated runs)
5. `python check_setup.py`
6. `streamlit run app.py`, pick a sample, click Run AegisGuard

Samples live in `samples/` (SQL injection, path traversal, XSS). Each folder has the vulnerable
`target_sample.py`, its regression tests `test_target.py`, and a `meta.json` description.
Security notes used for RAG live in `knowledge/`.