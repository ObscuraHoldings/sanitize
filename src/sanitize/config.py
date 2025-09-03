from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


def _platform_config_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "sanitize"
    if sys := os.environ.get("XDG_CONFIG_HOME"):
        return Path(sys) / "sanitize"
    if os.name == "posix" and "Darwin" in os.uname().sysname:
        return Path.home() / "Library" / "Application Support" / "sanitize"
    return Path.home() / ".config" / "sanitize"


@dataclass
class AppConfig:
    preset: str = "balanced"
    mode: str = "replace"  # replace|backup|export


def load_config() -> AppConfig:
    cfg_dir = _platform_config_dir()
    cfg_file = cfg_dir / "config.json"
    try:
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
        return AppConfig(**{k: v for k, v in data.items() if k in {"preset", "mode"}})
    except Exception:
        return AppConfig()


def save_config(cfg: AppConfig) -> None:
    cfg_dir = _platform_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "config.json").write_text(json.dumps(cfg.__dict__, indent=2), encoding="utf-8")

