from __future__ import annotations

from pathlib import Path
import hashlib
import subprocess


def build_deployment_diagnostic() -> str:
    app_path = Path(__file__).with_name("app.py")
    app_preview = ""

    if app_path.exists():
        app_preview = "\n".join(app_path.read_text(encoding="utf-8").splitlines()[:3])

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

    app_hash = "inconnu"
    if app_path.exists():
        app_hash = hashlib.sha256(app_path.read_bytes()).hexdigest()[:12]

    return (
        f"branch: {branch}\n"
        f"commit: {commit}\n"
        f"app.py sha256: {app_hash}\n"
        "app.py (3 premières lignes):\n"
        f"{app_preview}"
    )
