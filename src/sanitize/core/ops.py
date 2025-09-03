from __future__ import annotations

import json
import shutil
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from . import pdf as pdfmod
from . import docx as docxmod
from .report import FileReport, now_iso


def detect_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".docx":
        return "docx"
    return "unknown"


def _diff_pdf(old: Dict[str, Any], new: Dict[str, Any]) -> Tuple[List[str], int]:
    actions: List[str] = []
    removed = 0
    # DocInfo keys removed
    okeys = set((old.get("docinfo") or {}).keys())
    nkeys = set((new.get("docinfo") or {}).keys())
    dropped = sorted(list(okeys - nkeys))
    if dropped:
        actions += [f"docinfo:{k} removed" for k in dropped]
        removed += len(dropped)
    # Booleans flipped off
    for key in ["xmp_present", "has_outlines", "has_openaction", "has_viewer_prefs", "acroform_present"]:
        if old.get(key) and not new.get(key):
            actions.append(f"{key} cleared")
            removed += 1
    # Names.JavaScript reduced
    if old.get("javascript_names", 0) > new.get("javascript_names", 0):
        actions.append("javascript names removed")
        removed += old.get("javascript_names", 0) - new.get("javascript_names", 0)
    # Attachments removed
    if len(old.get("attachments", [])) > len(new.get("attachments", [])):
        actions.append("attachments removed")
        removed += len(old.get("attachments", [])) - len(new.get("attachments", []))
    # Page metadata reduced
    if old.get("page_metadata_count", 0) > new.get("page_metadata_count", 0):
        actions.append("page metadata removed")
        removed += old.get("page_metadata_count", 0) - new.get("page_metadata_count", 0)
    return actions, removed


def _diff_docx(old: Dict[str, Any], new: Dict[str, Any]) -> Tuple[List[str], int]:
    actions: List[str] = []
    removed = 0
    for section in ["core", "dcterms", "app"]:
        o = old.get(section, {}) or {}
        n = new.get(section, {}) or {}
        for k in o.keys():
            if k not in n or not n.get(k):
                actions.append(f"{section}:{k} cleared")
                removed += 1
    if old.get("custom_props_present") and not new.get("custom_props_present"):
        actions.append("custom properties removed")
        removed += 1
    if old.get("thumbnail_present") and not new.get("thumbnail_present"):
        actions.append("thumbnail removed")
        removed += 1
    return actions, removed


def process_file(
    path: Path,
    preset: str = "balanced",
    mode: str = "replace",
    out_dir: Path | None = None,
    sidecar: bool = True,
    dry_run: bool = False,
) -> FileReport:
    kind = detect_kind(path)
    if kind not in {"pdf", "docx"}:
        raise ValueError(f"Unsupported file type: {path}")

    started = time.time()

    # Determine destination file for export/backup
    if mode == "export":
        if not out_dir:
            raise ValueError("out_dir required for export mode")
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / path.name
        if not dry_run:
            if kind == "pdf":
                rep = pdfmod.sanitize_to(path, dest)
            else:
                rep = docxmod.sanitize_to(path, dest)
        else:
            # Simulate
            rep = {"old": {}, "new": {}, "path": str(dest)}
    else:
        # replace/backup operate on original
        if mode == "backup" and not dry_run:
            bak = path.with_suffix(path.suffix + ".bak")
            if not bak.exists():
                shutil.copy2(path, bak)
        if not dry_run:
            if kind == "pdf":
                rep = pdfmod.sanitize_inplace(path)
            else:
                rep = docxmod.sanitize_inplace(path)
        else:
            rep = {"old": {}, "new": {}, "path": str(path)}

    # Build actions/removed count
    if kind == "pdf":
        actions, removed = _diff_pdf(rep["old"], rep["new"])
    else:
        actions, removed = _diff_docx(rep["old"], rep["new"])

    report = FileReport(
        sanitized_at_utc=now_iso(),
        document=str(path),
        type=kind,
        old=rep["old"],
        new=rep["new"],
        actions=actions,
        errors=None,
        duration_ms=int((time.time() - started) * 1000),
        preset=preset,
        output_mode=mode,
    )

    # Sidecar
    if sidecar and not dry_run:
        out_path = Path(rep["path"]).with_suffix(Path(rep["path"]).suffix + ".sanitize.json")
        out_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    return report

