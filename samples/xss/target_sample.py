"""Intentionally vulnerable demo app (cross-site scripting). For hackathon demo only."""
from flask import Flask, request

app = Flask(__name__)


def render_greeting(name):
    # VULNERABLE: user input is inserted into HTML without escaping.
    return f"<h1>Hello, {name}!</h1>"


@app.route("/greet")
def greet():
    return render_greeting(request.args.get("name", "guest"))


if __name__ == "__main__":
    app.run(debug=False)