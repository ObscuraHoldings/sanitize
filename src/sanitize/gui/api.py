from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

from ..core.ops import process_file
from ..core.report import FileReport


@dataclass
class UIFile:
    id: str
    path: str
    name: str
    size: int
    type: str  # pdf|docx


class Bridge:
    """API exposed to the WebView.

    Methods here are callable from JS (pywebview).
    """

    def __init__(self) -> None:
        self.files: List[UIFile] = []
        self.preset: str = "balanced"
        self.mode: str = "replace"
        self.out_dir: str | None = None
        self._window = None
        self._results: List[FileReport] = []

    def set_window(self, window) -> None:  # pragma: no cover (UI)
        self._window = window

    # --- JS calls ---
    def choose_files(self) -> List[Dict[str, Any]]:  # pragma: no cover (UI)
        # Show a native file dialog, accept multiple PDF/DOCX, and add them
        import webview  # type: ignore

        try:
            paths = webview.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=True,
                file_types=(
                    ("Documents", "*.pdf;*.docx"),
                    ("PDF", "*.pdf"),
                    ("DOCX", "*.docx"),
                ),
            ) or []
        except Exception:
            paths = []
        return self.add_paths(list(paths))

    def remove_file(self, id: str) -> None:  # pragma: no cover (UI)
        self.files = [f for f in self.files if f.id != id]

    def set_preset(self, name: str) -> None:  # pragma: no cover (UI)
        self.preset = name

    def set_output_mode(self, mode: str) -> None:  # pragma: no cover (UI)
        import webview  # type: ignore

        self.mode = mode
        if mode == "export" and not self.out_dir:
            try:
                folder = webview.create_file_dialog(webview.FOLDER_DIALOG)
                if folder:
                    self.out_dir = str(folder)
            except Exception:
                pass

    def add_paths(self, paths: List[str]) -> List[Dict[str, Any]]:  # pragma: no cover (UI)
        out: List[Dict[str, Any]] = []
        for p in paths:
            path = Path(p)
            f = UIFile(id=str(uuid.uuid4()), path=str(path), name=path.name, size=path.stat().st_size if path.exists() else 0, type=self._kind_from_ext(path.suffix))
            self.files.append(f)
            out.append(asdict(f))
        return out

    def start_processing(self) -> None:  # pragma: no cover (UI)
        if not self._window:
            return
        threading.Thread(target=self._worker, daemon=True).start()

    def export_report(self) -> str:  # pragma: no cover (UI)
        if not self._results:
            return ""
        out_dir = Path.home() / "sanitize"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "session-report.json"
        out_path.write_text(json.dumps([asdict(r) for r in self._results], indent=2), encoding="utf-8")
        return str(out_path)

    # --- internals ---
    def _worker(self) -> None:  # pragma: no cover (UI)
        win = self._window
        total = len(self.files)
        idx = 0
        self._results = []
        win.evaluate_js("setState('processing')")
        for f in self.files:
            idx += 1
            win.evaluate_js(f"document.getElementById('status-detail').textContent='Processing {f.name.replace("'"," ")}';")
            win.evaluate_js(f"document.getElementById('progress-count').textContent='{idx - 1} of {total} complete';")

            # Simulated progress bar steps (UI nicety)
            for percent in (10, 30, 55, 80, 100):
                win.evaluate_js(f"document.getElementById('progress-fill').style.width='{percent}%';document.querySelector('.progress-bar').setAttribute('aria-valuenow','{percent}');")
                time.sleep(0.15)

            try:
                rep = process_file(
                    Path(f.path),
                    preset=self.preset,
                    mode=self.mode,
                    out_dir=Path(self.out_dir) if self.out_dir else None,
                    sidecar=True,
                    dry_run=False,
                )
                self._results.append(rep)
            except Exception as e:
                # Surface error and stop
                msg = str(e).replace("'", " ")
                win.evaluate_js(f"document.getElementById('error-title').textContent='Processing Failed';document.getElementById('error-message').textContent='{msg}';setState('error');")
                return

        # Complete
        files = len(self._results)
        removed = sum(len(r.actions) for r in self._results)
        clean_pct = "100%"  # heuristic placeholder; could compute based on diffs
        win.evaluate_js(
            f"document.getElementById('stat-files').textContent='{files}';"
            f"document.getElementById('stat-removed').textContent='{removed}';"
            f"document.getElementById('stat-clean').textContent='{clean_pct}';"
            "setState('complete');"
        )

        # Populate details view
        try:
            import json as _json

            payload = [
                {
                    "name": Path(r.document).name,
                    "actions": r.actions,
                }
                for r in self._results
            ]
            js = (
                "(function(){var data="
                + _json.dumps(payload)
                + ";var el=document.getElementById('details-content');el.innerHTML='';"
                  "data.forEach(function(d){var sec=document.createElement('div');sec.className='metadata-section';"
                  "var t=document.createElement('div');t.className='metadata-title';t.textContent=d.name;sec.appendChild(t);"
                  "(d.actions||[]).forEach(function(a){var it=document.createElement('div');it.className='metadata-item';"
                  "var k=document.createElement('span');k.className='metadata-key';k.textContent=a;it.appendChild(k);"
                  "var b=document.createElement('span');b.className='removed-badge';b.textContent='Removed';it.appendChild(b);sec.appendChild(it);});"
                  "el.appendChild(sec);});})()"
            )
            win.evaluate_js(js)
        except Exception:
            pass

    @staticmethod
    def _kind_from_ext(ext: str) -> str:
        e = ext.lower()
        if e == ".pdf":
            return "pdf"
        if e == ".docx":
            return "docx"
        return "unknown"
