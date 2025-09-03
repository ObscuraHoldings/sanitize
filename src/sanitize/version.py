from __future__ import annotations

from pathlib import Path

def _read_version() -> str:
    for p in (Path(__file__).resolve().parents[2] / "VERSION", Path.cwd() / "VERSION"):
        try:
            if p.exists():
                return p.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return "0.1.0-dev"

__version__ = _read_version()

