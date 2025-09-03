# Sanitize — Cross‑Platform Document Sanitizer (Single Binary, Dual‑Mode)

Authoritative specification for a modern, cross‑platform document sanitizer that ships as one simple application: GUI by default, headless when launched with flags. The UI, states, visuals, and flow are implemented exactly as defined in GUI-SPEC.md.

Inputs reviewed
- sanitize.py (current sanitization logic for PDF/DOCX)
- sanitize-ui.py (initial Tk wrapper)
- REFERENCE.xml (robust multi‑OS CI/release patterns)
- GUI-SPEC.md (canonical UI prototype and interaction model)

---

## 1) Vision and Goals

- Single artifact per OS that users can double‑click to launch the GUI.
- Same binary supports headless (no‑UI) operation when invoked with flags for automation.
- Exact visual/UI behavior from GUI-SPEC.md, with predictable, safe sanitization defaults.
- Reproducible builds and GitHub Releases for Windows, macOS, and Linux.

Non‑goals (v1)
- In‑app content preview/editing.
- Features not present in GUI-SPEC without explicit follow‑up.

---

## 2) Supported Formats (initial)

- PDF
  - Strip DocInfo, XMP, refresh trailer IDs, remove ViewerPreferences/Outlines/OpenAction/AA, remove page‑level Metadata/LastModified/PieceInfo, purge JavaScript and attachments, purge XFA, drop empty AcroForm.
  - Preserve visual content (no rasterization/reflow).
- DOCX
  - Clear core/app/dcterms properties; remove custom.xml and thumbnails; update [Content_Types].xml accordingly.

Backlog candidates: PPTX, XLSX, ODT/ODS/ODP, image EXIF/IPTC/XMP.

---

## 3) Core Principles and Safety

- Offline by default; no telemetry or network calls.
- Atomic file replacement; never corrupt originals.
- Safe defaults; adjustable via presets (Safe/Balanced/Aggressive).
- Transparent JSON reporting (per‑file sidecars and combined session report).
- Clear documentation of limitations; sanitization can’t guarantee removal of all proprietary/malformed artifacts.

---

## 4) Architecture Overview

- Language: Python 3.10+
- Core library: `sanitize.core` (PDF/DOCX, report assembly, helpers).
- GUI frontend: WebView (pywebview) that loads the exact HTML/CSS/JS from GUI-SPEC.md.
  - Visuals per spec: gradient #1a2332→#2d3748, 400×580 card, 24px radius, 2px progress bar, 8px preset dots, 400ms transitions.
  - States via `data-state`: `empty`, `files-added`, `processing`, `complete`, `details`, `error`.
- Bridge: pywebview API (Python exposed to JS) + callbacks from Python to JS to drive state changes.
- Single entry point: if started without args → launch GUI; if with args → run headless and exit.
- Packaging: PyInstaller (includes Python + web assets). No network required at runtime.

Repository layout
```
.
├─ src/
│  └─ sanitize/
│     ├─ __init__.py
│     ├─ core/
│     │  ├─ pdf.py
│     │  ├─ docx.py
│     │  └─ report.py
│     ├─ app.py              # single entry: GUI default; headless with args
│     ├─ gui/
│     │  ├─ webview_app.py   # pywebview bootstrap + JS bridge
│     │  └─ api.py           # Python API exposed to JS
│     ├─ config.py
│     ├─ logging_config.py
│     └─ version.py
├─ assets/
│  └─ ui/
│     └─ index.html          # EXACT HTML/CSS/JS from GUI-SPEC.md
├─ tests/
│  ├─ unit/
│  └─ integration/
├─ .github/
│  └─ workflows/
├─ pyproject.toml
├─ VERSION
├─ README.md
├─ SECURITY.md
├─ CONTRIBUTING.md
├─ LICENSE
└─ SPEC.md
```

Notes
- UI remains a single HTML file to preserve exact visuals/animations and minimize moving parts.
- GUI import is lazy; headless mode does not require WebView runtime on Windows.

---

## 5) Modernization and Unification

- Refactor current logic into `sanitize.core` with types, docstrings, and consistent error handling.
- Adopt `pyproject.toml` (PEP 621), src layout, and a single console entry point.
- Replace Tk wrapper with pywebview that renders `assets/ui/index.html` exactly.
- Define JS↔Python bridge for file selection, presets, output mode, progress updates, summary/details, and error states.
- Pin dependencies; deterministic builds.

---

## 6) Presets, Output Modes, Config

Presets (UI dots; exact labels)
- Safe (conservative removal; avoid destructive form/annotation removals)
- Balanced (default; attachments, viewer prefs, JS/XFA purge, page‑level metadata removal)
- Aggressive (also removes AcroForm/annotations/embedded names; refresh trailer IDs)

Output Modes (exact labels)
- Replace: in‑place atomic replace.
- Backup: keep `<name><ext>.bak`; sanitized replaces original.
- Export: prompt for output folder; write sanitized copies there.

Config (optional v1)
- `${CONFIG_DIR}/sanitize/config.toml` to persist default preset/output mode.

---

## 7) Logging and Reporting

- Per‑file sidecars: `<name>.<ext>.sanitize.json` with fields
  - `sanitized_at_utc`, `document`, `type`, `old`, `new`, `actions`, `errors`, `duration_ms`, `preset`, `output_mode`.
- Session export (GUI Details → Export Report): combined JSON of all processed files.
- Rotating app logs in `${CONFIG_DIR}/sanitize/logs/`.

---

## 8) Headless Mode (single binary, no separate CLI)

Invocation
- If `argv` has no flags/paths → launch GUI.
- If `argv` has flags/paths → run headless, print JSON (default JSONL), exit.

Flags
- `--auto` (default if no explicit type): detect by extension
- `--preset {safe|balanced|aggressive}` (default: balanced)
- `--mode {replace|backup|export}` (default: replace)
- `--out-dir DIR` (required if `--mode export` and not using GUI prompt)
- `--no-sidecar` (disable per‑file sidecars)
- `--json-array` (emit one JSON array instead of JSONL)
- `--dry-run` (report only; do not write outputs)
- `PATH...` (one or more files/globs; `--recursive` for directories)

Exit codes
- 0: all succeeded
- 1: partial failures
- 2: invalid args/no inputs

Examples
- GUI (double‑click or): `sanitize`
- Headless: `sanitize --auto --preset balanced --mode export --out-dir ./out docs/*.pdf`

---

## 9) Exact GUI Specification (from GUI-SPEC.md)

Visual Identity
- Background gradient #1a2332 → #2d3748; card 400×580; 24px radius; 2px progress; 8px dots; 400ms transitions.

States (data-state)
- `empty`: drop zone (“Drop files anywhere” / “or press +”), primary = “Continue” (disabled), preset dots visible.
- `files-added`: animated file list, remove (×), output mode row (Replace · Backup · Export), primary = “Sanitize”.
- `processing`: spinner, “Sanitizing files”, detail “Processing <name>”, 2px progress bar, “N of M complete”, primary disabled (“Processing…”).
- `complete`: success icon, title “Sanitization Complete”, stats (Files, Items Removed, Clean%), primary = “View Details”, secondary = “Add More Files”.
- `details`: back link “← Back to summary”, scrollable per‑file removals, primary = “Export Report”.
- `error`: graceful error pane with message and hint, primary = “Try Again” (back to `files-added` if files remain, else `empty`).

Rules/Interactions
- Drag & drop overlay: “Drop to add files”.
- Preset dots update active state and label (Safe/Balanced/Aggressive).
- Output mode visible only in `files-added`; if Export without folder, prompt before processing.
- Removing all files returns to `empty`.
- Secondary button appears only in `complete`.

Accessibility/Perf
- Full keyboard access; GPU‑accelerated CSS animations; assets ~<100KB.

---

## 10) GUI–Core Bridge (pywebview)

UI→Core (JS → Python)
- `choose_files()` → returns `[File{id, path, name, size, type}]`; transitions to `files-added`.
- `remove_file(id)` → updates pending set and state.
- `set_preset(name)` → safe|balanced|aggressive
- `set_output_mode(mode)` → replace|backup|export (prompt path if export and none set)
- `start_processing()` → begin pipeline
- `export_report()` → write combined JSON; return path

Core→UI (Python → JS)
- `ui_set_state(state)`
- `ui_progress(current, total, file_name, percent)`
- `ui_complete(summary)` (files, itemsRemoved, cleanPercent)
- `ui_details(details)` (per‑file removals)
- `ui_error(message)`

Threading
- Run work in background threads/process pool; marshal events to UI thread via pywebview’s safe call.

---

## 11) Security and Threat Model

- Addressed: metadata leaks; PDF auto‑execution (JS/OpenAction); embedded files.
- Out of scope: malware scanning; reader exploit mitigation; opaque vendor fields.
- Practices: strict parsing; bounded temp/atomic writes; no eval/exec on inputs; redact PII in logs.

---

## 12) Dependencies

Runtime
- Python 3.10+
- pikepdf >= 9.0.0
- pywebview (WebKit on macOS/Linux; WebView2 on Windows)

Dev
- Ruff, MyPy, PyTest, uv (optional)

Packaging
- PyInstaller (all OSes)
- macOS: `hdiutil` / `create-dmg` (+ optional codesign/notary)
- Linux: AppImage + `.deb` (later Flatpak/Snap if desired)
- Windows: optional installer; GUI requires WebView2 runtime (headless does not)

Notes
- Ensure PyInstaller collects pikepdf native deps and pywebview backend correctly for each OS.

---

## 13) Build and Release

Versioning
- Root `VERSION` file; release workflows trigger on change or manual dispatch.

Workflows
- Windows: build `Sanitize.exe` (GUI default, headless w/ args), embed `assets/ui/index.html`; compute SHA256; attach to GitHub Release. Note WebView2 requirement for GUI.
- macOS: build `Sanitize.app` with embedded assets; DMG packaging; optional codesign/notary; checksum.
- Linux: PyInstaller build; package AppImage and `.deb`; checksums.
- PR test builds for all OSes; CodeQL for Python.

---

## 14) Installation and Distribution

- Windows: portable zip; GUI needs WebView2 runtime; headless mode works without runtime (lazy import GUI only when needed).
- macOS: DMG; if unsigned, include quarantine removal instructions.
- Linux: AppImage + `.deb`.

---

## 15) Testing and QA

Unit
- PDF/DOCX sanitization behaviors; report content; preset logic; output mode file handling.

Integration
- Headless: run with flags across small fixture sets; validate outputs and sidecars.
- GUI: pywebview smoke tests (launch, add files, sanitize, complete, details, error); Playwright check of UI states/labels using raw `assets/ui/index.html`.

Fixtures
- Minimal PDFs/DOCX with known metadata keys and attachments/thumbnails.

---

## 16) Documentation

- README: screenshots for all six states, install notes (runtime requirements), quick start (GUI + headless examples), troubleshooting.
- SECURITY: threat model and safe‑use guidance.
- CONTRIBUTING: dev setup, lint/test, release steps.

---

## 17) Cleanup Tasks (from current scripts)

- Move sanitization logic from `sanitize.py` into `sanitize.core.pdf` and `sanitize.core.docx`.
- Replace `sanitize-ui.py` with WebView app that loads `assets/ui/index.html`.
- Implement JS↔Python bridge (gui/api.py) per Section 10.
- Centralize JSON report creation; implement per‑file sidecars and session export.
- Add `pyproject.toml` with a single entry point: `sanitize = "sanitize.app:main"` (GUI default; headless with args).
- Ensure atomic file operations and consistent error messages that map to the `error` UI state.

---

## 18) Roadmap and Milestones

- M0 — Skeleton: repo layout, pyproject, entry point, copy `assets/ui/index.html` from GUI-SPEC.
- M1 — Core: port/harden PDF/DOCX; unit tests.
- M2 — Headless mode: flags, presets, modes, JSONL/array; integration tests.
- M3 — GUI: pywebview app; implement exact states/labels/flows; bridge; session export.
- M4 — Packaging/CI: PyInstaller specs, OS workflows, release artifacts.
- M5 — Docs/Polish: screenshots, README/SECURITY, final QA.

---

## 19) Acceptance Criteria

- One binary per OS; GUI by default; headless with flags as specified.
- GUI matches GUI-SPEC exactly (visuals, labels, transitions, states).
- Presets and output modes (Replace/Backup/Export) behave as defined.
- JSON sidecars and session export produced correctly.
- CI builds/release artifacts pass smoke tests; no telemetry; robust error handling via `error` state.

---

## 20) Local Dev Workflow

- Setup: `uv venv && uv pip install -e .[dev]`
- Lint/Format: `ruff check .` / `ruff format .`
- Types: `mypy src`
- Tests: `pytest -q`
- GUI: `sanitize`
- Headless: `sanitize --auto --preset balanced --mode export --out-dir ./out tests/fixtures/*.pdf`

