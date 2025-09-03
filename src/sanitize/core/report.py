from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class FileReport:
    sanitized_at_utc: str
    document: str
    type: str  # pdf|docx
    old: Dict[str, Any] = field(default_factory=dict)
    new: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    errors: Optional[str] = None
    duration_ms: Optional[int] = None
    preset: Optional[str] = None
    output_mode: Optional[str] = None


def placeholder_report(path: str, kind: str, preset: str, output_mode: str) -> FileReport:
    return FileReport(
        sanitized_at_utc=now_iso(),
        document=path,
        type=kind,
        old={},
        new={},
        actions=["placeholder"],
        errors=None,
        duration_ms=0,
        preset=preset,
        output_mode=output_mode,
    )

