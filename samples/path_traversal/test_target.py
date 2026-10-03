"""Existing regression tests: these must pass before AND after the patch."""
import pytest
from target_sample import app, read_public_file


def test_reads_public_file():
    assert read_public_file("notes.txt") == "public note"


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_public_file("missing.txt")


def test_files_endpoint():
    client = app.test_client()
    assert client.get("/files?name=notes.txt").data.decode() == "public note"
    assert client.get("/files?name=missing.txt").status_code == 404