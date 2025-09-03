import json
from pathlib import Path

import pytest

pytest.importorskip("pikepdf")
import pikepdf  # type: ignore

from sanitize.core.ops import process_file, detect_kind
from sanitize.core import pdf as pdfmod
from sanitize.core import docx as docxmod

from .test_pdf import make_sample_pdf
from .test_docx import make_min_docx


def test_process_pdf_modes(tmp_path: Path):
    p = tmp_path / "a.pdf"
    make_sample_pdf(p)

    # export
    out_dir = tmp_path / "out"
    rep = process_file(p, preset="balanced", mode="export", out_dir=out_dir, sidecar=True)
    assert (out_dir / "a.pdf").exists()
    sidecar = out_dir / "a.pdf.sanitize.json"
    assert sidecar.exists()
    data = json.loads(sidecar.read_text())
    assert data["document"].endswith("a.pdf")
    assert data["actions"]

    # backup
    rep2 = process_file(p, preset="balanced", mode="backup", out_dir=None, sidecar=True)
    assert p.with_suffix(".pdf.bak").exists()


def test_process_docx_modes(tmp_path: Path):
    p = tmp_path / "b.docx"
    make_min_docx(p)
    out_dir = tmp_path / "out2"
    rep = process_file(p, preset="balanced", mode="export", out_dir=out_dir, sidecar=True)
    assert (out_dir / "b.docx").exists()
    assert (out_dir / "b.docx.sanitize.json").exists()

