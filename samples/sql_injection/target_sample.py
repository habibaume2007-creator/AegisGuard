"""Intentionally vulnerable demo app (SQL injection). For hackathon demo only."""
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT, secret TEXT)")
DB.executemany(
    "INSERT INTO users (username, role, secret) VALUES (?, ?, ?)",
    [("alice", "user", "alice-secret"), ("bob", "user", "bob-secret"), ("admin", "admin", "ADMIN-TOKEN-123")],
)
DB.commit()


def search_users(name):
    # VULNERABLE: user input is placed directly into the SQL string.
    query = f"SELECT id, username, role FROM users WHERE username = '{name}'"
    rows = DB.execute(query).fetchall()
    return [dict(zip(("id", "username", "role"), row)) for row in rows]


@app.route("/search")
def search():
    name = request.args.get("name", "")
    return jsonify(search_users(name))


if __name__ == "__main__":
    app.run(debug=False)