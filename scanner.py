"""Project-level static security scanning for uploaded Python source.

This module parses source code only. It does not import, execute, or test uploaded
projects, which makes it suitable for untrusted uploads when Docker is disabled.
"""
from __future__ import annotations

import ast

from graph_builder import find_vulns

VULN_META = {
    "sql_injection": {
        "name": "SQL Injection",
        "severity": "high",
        "cwe": "CWE-89",
        "summary": "Dynamic SQL reaches a database execution call.",
    },
    "path_traversal": {
        "name": "Path Traversal",
        "severity": "high",
        "cwe": "CWE-22",
        "summary": "A constructed path reaches file access without an obvious containment check.",
    },
    "xss": {
        "name": "Cross-site Scripting (XSS)",
        "severity": "medium",
        "cwe": "CWE-79",
        "summary": "HTML appears to include unescaped dynamic content.",
    },
    "unsafe_deserialization": {
        "name": "Unsafe Deserialization",
        "severity": "high",
        "cwe": "CWE-502",
        "summary": "Potentially unsafe deserialization API usage was detected.",
    },
}


def _function_lines(source: str) -> dict[str, int]:
    tree = ast.parse(source)
    return {
        node.name: node.lineno
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def scan_source(path: str, source: str) -> tuple[list[dict], str | None]:
    """Scan one Python source string and return (findings, parse_error)."""
    try:
        lines = _function_lines(source)
        raw = find_vulns(source)
    except (SyntaxError, ValueError) as exc:
        location = f"line {getattr(exc, 'lineno', '?')}" if isinstance(exc, SyntaxError) else "unknown line"
        return [], f"{path}: could not parse ({location}): {exc.msg if isinstance(exc, SyntaxError) else exc}"

    findings = []
    for vuln_type, function in raw:
        meta = VULN_META.get(vuln_type, {
            "name": vuln_type.replace("_", " ").title(),
            "severity": "medium",
            "cwe": "",
            "summary": "Potential security issue detected by a static rule.",
        })
        findings.append({
            "file": path,
            "function": function,
            "line": lines.get(function),
            "type": vuln_type,
            **meta,
        })
    return findings, None


def scan_project(files: dict[str, str]) -> dict:
    """Scan a {relative_path: source} project manifest without executing code."""
    findings: list[dict] = []
    parse_errors: list[str] = []
    for path, source in sorted(files.items()):
        found, error = scan_source(path, source)
        findings.extend(found)
        if error:
            parse_errors.append(error)

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda x: (severity_rank.get(x["severity"], 9), x["file"], x.get("line") or 0))
    return {
        "findings": findings,
        "parse_errors": parse_errors,
        "files_scanned": len(files),
    }
