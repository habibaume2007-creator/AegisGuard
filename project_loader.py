"""Safe loader for uploaded Python files and ZIP projects.

The loader never imports or executes uploaded code. It only returns UTF-8 Python
source files after validating paths and size limits.
"""
from __future__ import annotations

import io
import stat
import zipfile
from pathlib import PurePosixPath

import config

IGNORE_PARTS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", "__pycache__", ".pytest_cache",
    "venv", ".venv", "env", ".env", "node_modules", "dist", "build", ".mypy_cache",
    ".ruff_cache", "site-packages",
}


class ProjectUploadError(ValueError):
    """Raised when an upload is unsafe, unsupported, or too large."""


def _safe_relative_path(name: str) -> PurePosixPath:
    normalized = name.replace("\\", "/")
    p = PurePosixPath(normalized)
    if p.is_absolute() or not p.parts or any(part in ("", ".", "..") for part in p.parts):
        raise ProjectUploadError(f"Unsafe path in upload: {name!r}")
    if ":" in p.parts[0]:
        raise ProjectUploadError(f"Unsafe drive path in upload: {name!r}")
    return p


def _ignored(path: PurePosixPath) -> bool:
    return any(part.lower() in IGNORE_PARTS for part in path.parts)


def _decode_python(data: bytes, name: str) -> str:
    if len(data) > config.MAX_SINGLE_FILE_BYTES:
        raise ProjectUploadError(f"Python file is too large: {name}")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectUploadError(f"Python file is not valid UTF-8: {name}") from exc


def _load_single_python(filename: str, data: bytes) -> dict:
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise ProjectUploadError("Upload exceeds the configured size limit.")
    path = _safe_relative_path(PurePosixPath(filename).name)
    if path.suffix.lower() != ".py":
        raise ProjectUploadError("Only .py files or .zip Python projects are supported.")
    source = _decode_python(data, str(path))
    return {
        "name": path.stem,
        "files": {str(path): source},
        "skipped": [],
        "total_bytes": len(data),
    }


def _load_zip(filename: str, data: bytes) -> dict:
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise ProjectUploadError("ZIP upload exceeds the configured size limit.")

    files: dict[str, str] = {}
    skipped: list[str] = []
    total_uncompressed = 0
    seen_entries = 0

    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ProjectUploadError("The uploaded ZIP is invalid or corrupted.") from exc

    with archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            seen_entries += 1
            if seen_entries > config.MAX_PROJECT_FILES:
                raise ProjectUploadError("Project contains too many files.")
            if info.flag_bits & 0x1:
                raise ProjectUploadError("Encrypted ZIP entries are not supported.")

            mode = (info.external_attr >> 16) & 0xFFFF
            if mode and stat.S_ISLNK(mode):
                skipped.append(f"{info.filename} (symbolic link)")
                continue

            path = _safe_relative_path(info.filename)
            if _ignored(path) or path.suffix.lower() != ".py":
                continue
            if info.file_size > config.MAX_SINGLE_FILE_BYTES:
                skipped.append(f"{path} (too large)")
                continue

            total_uncompressed += info.file_size
            if total_uncompressed > config.MAX_EXTRACTED_BYTES:
                raise ProjectUploadError("Extracted project exceeds the configured size limit.")
            if len(files) >= config.MAX_PYTHON_FILES:
                raise ProjectUploadError("Project contains too many Python files.")

            raw = archive.read(info)
            try:
                files[str(path)] = _decode_python(raw, str(path))
            except ProjectUploadError as exc:
                skipped.append(str(exc))

    if not files:
        raise ProjectUploadError("No readable Python files were found in the ZIP.")

    project_name = PurePosixPath(filename).stem or "uploaded_project"
    return {
        "name": project_name,
        "files": files,
        "skipped": skipped,
        "total_bytes": total_uncompressed,
    }


def load_project_upload(filename: str, data: bytes) -> dict:
    """Return a validated project manifest for a .py or .zip upload."""
    lower = filename.lower()
    if lower.endswith(".py"):
        return _load_single_python(filename, data)
    if lower.endswith(".zip"):
        return _load_zip(filename, data)
    raise ProjectUploadError("Unsupported upload. Use a .py file or a .zip Python project.")
