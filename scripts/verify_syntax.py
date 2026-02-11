#!/usr/bin/env python3
"""Vérifie l'intégrité/syntaxe des sources Python du dépôt."""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

DIFF_INDEX_RE = re.compile(r"^index [0-9a-f]{7,}\.\.[0-9a-f]{7,} \d+$")


def git_tracked_python_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.py", "scripts/*.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    files = [root / line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(files)


def lint_text(source: str) -> list[str]:
    errors: list[str] = []
    first_non_empty = next((line for line in source.splitlines() if line.strip()), "")
    if first_non_empty.startswith((" ", "\t")):
        errors.append("première ligne non vide indentée (risque IndentationError)")

    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("diff --git") or stripped.startswith("@@ "):
            errors.append(f"marqueur de diff détecté: {stripped[:60]!r}")
        if DIFF_INDEX_RE.match(stripped):
            errors.append(f"ligne index git détectée: {stripped[:60]!r}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    py_files = git_tracked_python_files(root)

    has_error = False
    for path in py_files:
        source = path.read_text(encoding="utf-8")
        text_errors = lint_text(source)

        if text_errors:
            has_error = True
            for err in text_errors:
                print(f"FAIL {path.relative_to(root)}: {err}")
            continue

        try:
            ast.parse(source, filename=str(path))
            print(f"OK   {path.relative_to(root)}")
        except SyntaxError as exc:
            has_error = True
            print(
                f"FAIL {path.relative_to(root)}: {exc.msg} "
                f"(ligne {exc.lineno}, colonne {exc.offset})"
            )

    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
