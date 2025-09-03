import json
from pathlib import Path

import pytest

pytest.importorskip("pikepdf")

from sanitize.app import headless_main
from .unit.test_pdf import make_sample_pdf


def test_headless_jsonl(tmp_path, capsys):
    p = tmp_path / "x.pdf"
    make_sample_pdf(p)
    code = headless_main(["--auto", "--mode", "export", "--out-dir", str(tmp_path / "out"), str(p)])
    captured = capsys.readouterr()
    assert code == 0
    # Expect a JSON line
    line = captured.out.strip().splitlines()[0]
    data = json.loads(line)
    assert data["document"].endswith("x.pdf")
    assert data["type"] == "pdf"

