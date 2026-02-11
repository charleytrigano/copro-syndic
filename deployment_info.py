from __future__ import annotations

from pathlib import Path
import hashlib
import re
import subprocess

_DIFF_PATTERNS = (
    re.compile(r"^diff --git "),
    re.compile(r"^@@ "),
    re.compile(r"^index [0-9a-f]+\.\.[0-9a-f]+ \d{6}$"),
)


def build_deployment_diagnostic() -> str:
    commit = "inconnu"
    branch = "inconnue"
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
    except Exception:
        pass

    app_info = _inspect_file("app.py")
    models_info = _inspect_file("models.py")

    return (
        f"branch: {branch}\n"
        f"commit: {commit}\n"
        f"app.py sha256: {app_info['sha']}\n"
        f"models.py sha256: {models_info['sha']}\n"
        f"models.py index/diff markers: {'oui' if models_info['has_diff_markers'] else 'non'}\n\n"
        "app.py (3 premières lignes):\n"
        f"{app_info['preview']}\n\n"
        "models.py (3 premières lignes):\n"
        f"{models_info['preview']}"
    )


def _inspect_file(filename: str) -> dict[str, str | bool]:
    path = Path(__file__).with_name(filename)
    if not path.exists():
        return {"sha": "inconnu", "preview": "fichier introuvable", "has_diff_markers": False}

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    preview = "\n".join(lines[:3])
    has_diff_markers = any(pattern.search(line) for line in lines for pattern in _DIFF_PATTERNS)

    return {
        "sha": hashlib.sha256(path.read_bytes()).hexdigest()[:12],
        "preview": preview,
        "has_diff_markers": has_diff_markers,
    }
