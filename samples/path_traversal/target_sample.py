"""Intentionally vulnerable demo app (path traversal). For hackathon demo only."""
import os
import tempfile
from flask import Flask, request, abort

app = Flask(__name__)

# Demo files are created in a temp folder so the sample works anywhere (including Docker).
ROOT_DIR = tempfile.mkdtemp()
PUBLIC_DIR = os.path.join(ROOT_DIR, "public")
os.makedirs(PUBLIC_DIR)
with open(os.path.join(PUBLIC_DIR, "notes.txt"), "w", encoding="utf-8") as f:
    f.write("public note")
with open(os.path.join(ROOT_DIR, "secret.txt"), "w", encoding="utf-8") as f:
    f.write("TOP-SECRET-KEY")


def read_public_file(filename):
    # VULNERABLE: the name is joined to the folder without checking where the final path points.
    path = os.path.join(PUBLIC_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@app.route("/files")
def files():
    name = request.args.get("name", "")
    try:
        return read_public_file(name)
    except (FileNotFoundError, IsADirectoryError):
        abort(404)


if __name__ == "__main__":
    app.run(debug=False)