import json
from pathlib import Path

import pytest


pytest.importorskip("pikepdf")

import pikepdf  # type: ignore

from sanitize.core import pdf as pdfmod


def make_sample_pdf(path: Path) -> None:
    pdf = pikepdf.Pdf.new()
    # Add a page
    page = pikepdf.Page(pikepdf.Rectangle(0, 0, 200, 200))
    pdf.pages.append(page)

    # DocInfo
    pdf.docinfo["/Title"] = "Test Title"
    pdf.docinfo["/Author"] = "Tester"

    # Catalog keys: ViewerPreferences, Outlines, OpenAction
    pdf.Root["/ViewerPreferences"] = pikepdf.Dictionary()
    pdf.Root["/Outlines"] = pikepdf.Dictionary()
    pdf.Root["/OpenAction"] = pikepdf.Array([pikepdf.Name("/GoTo"), pdf.pages[0].obj])

    # Names.JavaScript (minimal stub)
    names = pikepdf.Dictionary()
    jsdict = pikepdf.Dictionary()
    jsdict["/Names"] = pikepdf.Array([pikepdf.String("a"), pikepdf.make_stream(b"app.alert('x')")])
    names["/JavaScript"] = jsdict
    pdf.Root["/Names"] = names

    # Attachment via API
    pdf.attachments["test.txt"] = b"hello"

    # Page-level metadata
    page.obj["/Metadata"] = pikepdf.make_stream(b"<x:xmpmeta>")

    # XMP at catalog
    pdf.Root["/Metadata"] = pikepdf.make_stream(b"<x:xmpmeta>")

    pdf.save(str(path))


def test_pdf_sanitize_inplace(tmp_path: Path):
    p = tmp_path / "sample.pdf"
    make_sample_pdf(p)

    before = pdfmod.read_state(p)
    assert before["docinfo"]
    assert before["xmp_present"] is True
    assert before["has_viewer_prefs"] is True
    assert before["has_outlines"] is True
    assert before["has_openaction"] is True
    assert before["javascript_names"] >= 1
    assert before["attachments"]
    assert before["page_metadata_count"] >= 1

    rep = pdfmod.sanitize_inplace(p)
    after = rep["new"]
    assert not after["docinfo"]
    assert after["xmp_present"] is False
    assert after["has_viewer_prefs"] is False
    assert after["has_outlines"] is False
    assert after["has_openaction"] is False
    assert after["javascript_names"] == 0
    assert not after["attachments"]
    assert after["page_metadata_count"] == 0

