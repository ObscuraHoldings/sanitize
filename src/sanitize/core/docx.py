from __future__ import annotations

import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}

SANITIZE_KEYS_CORE = [
    ("dc", "creator"),
    ("cp", "lastModifiedBy"),
    ("dc", "title"),
    ("dc", "subject"),
    ("dc", "description"),
    ("cp", "keywords"),
    ("cp", "category"),
    ("cp", "contentStatus"),
]
SANITIZE_KEYS_DCTERMS = ["created", "modified"]
SANITIZE_KEYS_APP = [
    ("ep", "Application"),
    ("ep", "AppVersion"),
    ("ep", "Company"),
    ("ep", "Manager"),
    ("ep", "HyperlinkBase"),
    ("ep", "DocSecurity"),
    ("ep", "Template"),
    ("ep", "TotalTime"),
    ("ep", "LastPrinted"),
]


def _read_props(zipf: zipfile.ZipFile) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "core": {},
        "dcterms": {},
        "app": {},
        "custom_props_present": False,
        "thumbnail_present": False,
    }
    if "docProps/core.xml" in zipf.namelist():
        xml = zipf.read("docProps/core.xml")
        try:
            root = ET.fromstring(xml)
            for ns, tag in SANITIZE_KEYS_CORE:
                el = root.find(f"{{{NS[ns]}}}{tag}")
                if el is not None and el.text:
                    out["core"][f"{ns}:{tag}"] = el.text
            for tag in SANITIZE_KEYS_DCTERMS:
                el = root.find(f"{{{NS['dcterms']}}}{tag}")
                if el is not None and el.text:
                    out["dcterms"][f"dcterms:{tag}"] = el.text
        except Exception:
            pass
    if "docProps/app.xml" in zipf.namelist():
        xml = zipf.read("docProps/app.xml")
        try:
            root = ET.fromstring(xml)
            for ns, tag in SANITIZE_KEYS_APP:
                el = root.find(f"{{{NS[ns]}}}{tag}")
                if el is not None and el.text:
                    out["app"][f"{ns}:{tag}"] = el.text
        except Exception:
            pass
    out["custom_props_present"] = "docProps/custom.xml" in zipf.namelist()
    out["thumbnail_present"] = any(n.lower().startswith("docprops/thumbnail") for n in zipf.namelist())
    return out


def _sanitize_core(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)
    for ns, tag in SANITIZE_KEYS_CORE:
        el = root.find(f"{{{NS[ns]}}}{tag}")
        if el is not None:
            el.text = ""
    for tag in SANITIZE_KEYS_DCTERMS:
        el = root.find(f"{{{NS['dcterms']}}}{tag}")
        if el is not None:
            el.text = ""
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _sanitize_app(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)
    for ns, tag in SANITIZE_KEYS_APP:
        el = root.find(f"{{{NS[ns]}}}{tag}")
        if el is not None:
            if el.text and el.text.strip().isdigit():
                el.text = "0"
            else:
                el.text = ""
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _content_types_remove_entries(xml_bytes: bytes, parts: List[str]) -> bytes:
    root = ET.fromstring(xml_bytes)
    removed = False
    ns = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    for override in list(root.findall(f"{ns}Override")):
        partname = override.attrib.get("PartName", "")
        if partname in parts:
            root.remove(override)
            removed = True
    return (
        ET.tostring(root, encoding="utf-8", xml_declaration=True) if removed else xml_bytes
    )


def sanitize_inplace(path: Path) -> Dict[str, Any]:
    old_meta = {}
    tmp_path = Path(
        tempfile.mkstemp(
            prefix=path.stem + "_clean_", suffix=path.suffix, dir=str(path.parent)
        )[1]
    )
    try:
        with zipfile.ZipFile(path, "r") as zin:
            old_meta = _read_props(zin)
            with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                drop_parts = set()
                if "docProps/custom.xml" in zin.namelist():
                    drop_parts.add("docProps/custom.xml")
                for name in zin.namelist():
                    if name.lower().startswith("docprops/thumbnail"):
                        drop_parts.add(name)

                for item in zin.infolist():
                    name = item.filename
                    if name in drop_parts:
                        continue
                    data = zin.read(name)
                    if name == "[Content_Types].xml" and drop_parts:
                        data = _content_types_remove_entries(data, parts=list(drop_parts))
                    elif name == "docProps/core.xml":
                        data = _sanitize_core(data)
                    elif name == "docProps/app.xml":
                        data = _sanitize_app(data)
                    zout.writestr(name, data)

        # Replace original
        from .pdf import _atomic_replace  # reuse

        _atomic_replace(tmp_path, path)

        with zipfile.ZipFile(path, "r") as zfinal:
            new_meta = _read_props(zfinal)
        return {"old": old_meta, "new": new_meta, "path": str(path)}
    except Exception:
        try:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def sanitize_to(path: Path, dest: Path) -> Dict[str, Any]:
    dest.write_bytes(Path(path).read_bytes())
    return sanitize_inplace(dest)

