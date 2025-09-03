from __future__ import annotations

import logging
from pathlib import Path

from .api import Bridge


def _find_index_html() -> Path:
    # Preferred: assets/ui/index.html relative to project root when packaged
    candidates = [
        Path(__file__).resolve().parents[2] / "assets" / "ui" / "index.html",
        Path.cwd() / "assets" / "ui" / "index.html",
        Path.cwd() / "index.html",  # demo UI in repo root (as requested)
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("index.html not found (looked in assets/ui/ and repo root)")


def run_gui() -> None:  # pragma: no cover (UI)
    import webview  # lazy import

    index = _find_index_html()
    logging.getLogger(__name__).info("Loading UI from %s", index)

    bridge = Bridge()
    window = webview.create_window("Sanitize", str(index), js_api=bridge)
    bridge.set_window(window)
    webview.start(debug=False)
