from __future__ import annotations

import argparse
import json
import logging
import sys
from glob import glob
from pathlib import Path
from typing import Iterable, List

from .core.ops import process_file
from .core.report import FileReport
from .logging_config import setup_logging


def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="sanitize",
        description="Sanitize documents. GUI if no arguments; headless otherwise.",
        add_help=True,
    )
    p.add_argument("paths", nargs="*", help="Files or globs to sanitize")
    p.add_argument("--auto", action="store_true", help="Auto-detect type by extension (default)")
    p.add_argument("--preset", choices=["safe", "balanced", "aggressive"], default="balanced")
    p.add_argument("--mode", choices=["replace", "backup", "export"], default="replace")
    p.add_argument("--out-dir", default=None, help="Output directory for export mode")
    p.add_argument("--no-sidecar", action="store_true", help="Disable per-file JSON sidecars")
    p.add_argument("--json-array", action="store_true", help="Emit one JSON array instead of JSON lines")
    p.add_argument("--dry-run", action="store_true", help="Report only; do not write outputs")
    p.add_argument("--recursive", action="store_true", help="Recurse into directories")
    p.add_argument("--verbose", "-v", action="count", default=0)
    return p.parse_args(argv)


def _iter_files(paths: Iterable[str], recursive: bool) -> Iterable[Path]:
    for pat in paths:
        p = Path(pat)
        if p.is_dir():
            if recursive:
                yield from (q for q in p.rglob("*") if q.is_file())
        else:
            # globs
            matched = list(map(Path, glob(pat)))
            if matched:
                yield from (m for m in matched if m.is_file())
            elif p.exists() and p.is_file():
                yield p


def _detect_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".docx":
        return "docx"
    return "unknown"


def headless_main(argv: List[str]) -> int:
    args = _parse_args(argv)
    if not args.paths:
        # No arguments -> fall back to GUI
        from .gui.webview_app import run_gui

        run_gui()
        return 0

    # Headless
    level = logging.WARNING - min(args.verbose, 2) * 10
    setup_logging(level)
    log = logging.getLogger("sanitize")

    files = list(_iter_files(args.paths, args.recursive))
    if not files:
        log.error("No files matched.")
        return 2

    reports: List[FileReport] = []
    for f in files:
        kind = _detect_kind(f)
        if kind not in {"pdf", "docx"}:
            log.warning("Skipping unsupported file: %s", f)
            continue
        try:
            rep = process_file(
                f,
                preset=args.preset,
                mode=args.mode,
                out_dir=Path(args.out_dir) if args.out_dir else None,
                sidecar=not args.no_sidecar,
                dry_run=args.dry_run,
            )
            reports.append(rep)
        except Exception as e:
            log.error("Failed to sanitize %s: %s", f, e)

    if args.json_array:
        print(json.dumps([r.__dict__ for r in reports], indent=2))
    else:
        for r in reports:
            print(json.dumps(r.__dict__, ensure_ascii=False))

    return 0 if len(reports) > 0 else 1


def main() -> None:
    sys.exit(headless_main(sys.argv[1:]))
