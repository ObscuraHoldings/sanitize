from pathlib import Path
import zipfile

from sanitize.core import docx as docxmod


def make_min_docx(path: Path) -> None:
    core = b"""<?xml version='1.0' encoding='UTF-8'?>
    <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <dc:title>Title</dc:title>
      <dc:creator>Author</dc:creator>
      <cp:lastModifiedBy>Someone</cp:lastModifiedBy>
      <dcterms:created xsi:type="dcterms:W3CDTF">2020-01-01T00:00:00Z</dcterms:created>
      <dcterms:modified xsi:type="dcterms:W3CDTF">2020-01-02T00:00:00Z</dcterms:modified>
    </cp:coreProperties>"""

    app = b"""<?xml version='1.0' encoding='UTF-8'?>
    <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
      <Application>Word</Application>
      <AppVersion>16.0</AppVersion>
      <Company>ACME</Company>
      <Manager>Boss</Manager>
    </Properties>"""

    content_types = b"""<?xml version="1.0" encoding="UTF-8"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
      <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
      <Default Extension="xml" ContentType="application/xml"/>
      <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
      <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
      <Override PartName="/docProps/custom.xml" ContentType="application/vnd.openxmlformats-officedocument.custom-properties+xml"/>
      <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
      <Override PartName="/docProps/thumbnail.jpeg" ContentType="image/jpeg"/>
    </Types>"""

    rels = b"""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="/word/document.xml"/>
    </Relationships>"""

    document = b"""<?xml version="1.0" encoding="UTF-8"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Hi</w:t></w:r></w:p></w:body></w:document>"""

    custom = b"""<?xml version='1.0' encoding='UTF-8'?>
    <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
      <property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="Custom"><vt:lpwstr>val</vt:lpwstr></property>
    </Properties>"""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("docProps/custom.xml", custom)
        z.writestr("docProps/thumbnail.jpeg", b"\xff\xd8\xff\xd9")
        z.writestr("word/document.xml", document)


def test_docx_sanitize_inplace(tmp_path: Path):
    p = tmp_path / "sample.docx"
    make_min_docx(p)

    before = {}
    with zipfile.ZipFile(p, "r") as z:
        before = docxmod._read_props(z)
    assert before["core"]
    assert before["app"]
    assert before["custom_props_present"] is True
    assert before["thumbnail_present"] is True

    rep = docxmod.sanitize_inplace(p)
    after = rep["new"]
    assert after["core"] == {}
    assert after["app"] == {}
    assert after["custom_props_present"] is False
    assert after["thumbnail_present"] is False

