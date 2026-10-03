"""Runs pytest on a set of files in an isolated Docker container."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import config

DOCKERFILE = """FROM python:3.11-slim
RUN pip install --no-cache-dir flask pytest
WORKDIR /app
"""


class SandboxError(Exception):
    pass


def _client():
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        raise SandboxError(
            "Docker is not available. Start Docker Desktop, or set USE_DOCKER=false in .env "
            f"for local (NOT isolated) runs. Details: {e}"
        )


def build_image():
    """Build the sandbox image once (needs internet; the runs themselves do not)."""
    import io
    client = _client()
    client.images.build(fileobj=io.BytesIO(DOCKERFILE.encode()), tag=config.SANDBOX_IMAGE, rm=True)


def _ensure_image(client):
    try:
        client.images.get(config.SANDBOX_IMAGE)
    except Exception:
        build_image()


def _run_docker(workdir: Path, targets):
    client = _client()
    _ensure_image(client)
    container = client.containers.run(
        config.SANDBOX_IMAGE,
        ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", *targets],
        detach=True,
        working_dir="/app",
        volumes={str(workdir.resolve()): {"bind": "/app", "mode": "ro"}},
        network_mode="none",                 # no network while tests run
        mem_limit=config.SANDBOX_MEMORY,
        nano_cpus=1_000_000_000,             # 1 CPU
        pids_limit=128,
        user="nobody",
        cap_drop=["ALL"],
        security_opt=["no-new-privileges"],
        environment={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        try:
            exit_code = container.wait(timeout=config.SANDBOX_TIMEOUT)["StatusCode"]
        except Exception:
            container.kill()
            exit_code = 124   # timed out
        output = container.logs().decode(errors="replace")
    finally:
        container.remove(force=True)
    return exit_code, output


def _run_local(workdir: Path, targets):
    """Fallback for development. NOT isolated: generated code runs on your machine."""
    try:
        p = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *targets],
            cwd=workdir, capture_output=True, text=True, timeout=config.SANDBOX_TIMEOUT,
            env={**{k: v for k, v in os.environ.items()
                    if k in ("SYSTEMROOT", "PATH", "TEMP", "TMP")},
                 "PYTHONDONTWRITEBYTECODE": "1"},
        )
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "Timed out"


def run_pytest(files: dict, targets: list) -> dict:
    """files: {filename: source}. Returns {exit_code, output, mode}."""
    config.WORKSPACE_ROOT.mkdir(exist_ok=True)
    workdir = Path(tempfile.mkdtemp(dir=config.WORKSPACE_ROOT))
    try:
        for name, content in files.items():
            (workdir / name).write_text(content, encoding="utf-8")
        os.chmod(workdir, 0o755)   # container runs as "nobody" and must be able to read this folder
        if config.USE_DOCKER:
            code, out = _run_docker(workdir, targets)
            mode = "docker"
        else:
            code, out = _run_local(workdir, targets)
            mode = "local"
        return {"exit_code": code, "output": out, "mode": mode}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)