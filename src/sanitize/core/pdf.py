from __future__ import annotations

import hashlib
import inspect
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_replace(src: Path, dst: Path) -> None:
    os.replace(src, dst)


def _pikepdf():  # lazy import
    import pikepdf  # type: ignore

    return pikepdf


def _pdf_save(pdf, out_path: Path) -> None:
    sig = inspect.signature(pdf.save)
    supported = {p.name for p in sig.parameters.values()}
    opts = {}
    if "linearize" in supported:
        opts["linearize"] = True
    if "compress_streams" in supported:
        opts["compress_streams"] = True
    if "fix_metadata_version" in supported:
        opts["fix_metadata_version"] = False
    pdf.save(str(out_path), **opts)


def _pdf_root(pdf):
    pikepdf = _pikepdf()
    root = getattr(pdf, "Root", None) or getattr(pdf, "root", None)
    if not root:
        root = pdf.trailer.get(pikepdf.Name("/Root"))
    return root


def read_state(path: Path) -> Dict[str, Any]:
    pikepdf = _pikepdf()
    out: Dict[str, Any] = {
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
        "docinfo": {},
        "xmp_present": False,
        "trailer_id": None,
        "has_outlines": False,
        "has_openaction": False,
        "has_viewer_prefs": False,
        "lang": None,
        "attachments": [],
        "javascript_names": 0,
        "acroform_present": False,
        "page_metadata_count": 0,
    }
    with pikepdf.open(str(path)) as pdf:
        try:
            for k, v in pdf.docinfo.items():
                out["docinfo"][str(k)] = str(v)
        except Exception:
            pass

        try:
            tid = pdf.trailer.get(pikepdf.Name("/ID"))
            if tid and isinstance(tid, pikepdf.Array) and len(tid) >= 1:
                out["trailer_id"] = [
                    bytes(tid[0]).hex(),
                    bytes(tid[1]).hex() if len(tid) > 1 else None,
                ]
        except Exception:
            pass

        root = _pdf_root(pdf)
        if root:
            out["xmp_present"] = pikepdf.Name("/Metadata") in root
            out["has_outlines"] = pikepdf.Name("/Outlines") in root
            out["has_openaction"] = (
                pikepdf.Name("/OpenAction") in root or pikepdf.Name("/AA") in root
            )
            out["has_viewer_prefs"] = pikepdf.Name("/ViewerPreferences") in root
            if pikepdf.Name("/Lang") in root:
                try:
                    out["lang"] = str(root[pikepdf.Name("/Lang")])
                except Exception:
                    out["lang"] = True

            js_count = 0
            names = root.get(pikepdf.Name("/Names"))
            if isinstance(names, pikepdf.Dictionary):
                js = names.get(pikepdf.Name("/JavaScript"))
                if isinstance(js, pikepdf.Dictionary) and pikepdf.Name("/Names") in js:
                    arr = js[pikepdf.Name("/Names")]
                    try:
                        js_count = len(arr) // 2
                    except Exception:
                        js_count = 1
            out["javascript_names"] = js_count

        try:
            for name in getattr(pdf, "attachments", {}).keys():
                out["attachments"].append(str(name))
        except Exception:
            pass

        try:
            cat = root if root else {}
            acro = cat.get(pikepdf.Name("/AcroForm"))
            out["acroform_present"] = bool(acro)
        except Exception:
            pass

        page_meta = 0
        for page in pdf.pages:
            obj = page.obj
            for key in ("/Metadata", "/LastModified", "/PieceInfo"):
                if key in obj:
                    page_meta += 1
                    break
        out["page_metadata_count"] = page_meta

    return out


def _strip(pdf) -> None:
    pikepdf = _pikepdf()
    Name = pikepdf.Name

    try:
        del pdf.docinfo
    except Exception:
        try:
            pdf.docinfo.clear()
        except Exception:
            pass

    root = _pdf_root(pdf)
    if isinstance(root, pikepdf.Dictionary):
        for k in [
            "/Metadata",
            "/PieceInfo",
            "/AF",
            "/OpenAction",
            "/AA",
            "/Outlines",
            "/ViewerPreferences",
            "/Lang",
        ]:
            try:
                if Name(k) in root:
                    del root[Name(k)]
            except Exception:
                pass

        names = root.get(Name("/Names"))
        if isinstance(names, pikepdf.Dictionary):
            changed = False
            for nkey in ["/EmbeddedFiles", "/JavaScript"]:
                if Name(nkey) in names:
                    try:
                        del names[Name(nkey)]
                        changed = True
                    except Exception:
                        pass
            try:
                if changed and len(names.keys()) == 0:
                    del root[Name("/Names")]
            except Exception:
                pass

        acro = root.get(Name("/AcroForm"))
        if isinstance(acro, pikepdf.Dictionary):
            try:
                if Name("/XFA") in acro:
                    del acro[Name("/XFA")]
                if Name("/NeedAppearances") in acro:
                    del acro[Name("/NeedAppearances")]
                if Name("/Fields") not in acro or (
                    isinstance(acro.get(Name("/Fields")), pikepdf.Array)
                    and len(acro.get(Name("/Fields"))) == 0
                ):
                    del root[Name("/AcroForm")]
            except Exception:
                pass

    for page in pdf.pages:
        obj = page.obj
        for k in ["/Metadata", "/LastModified", "/PieceInfo", "/AA"]:
            try:
                if pikepdf.Name(k) in obj:
                    del obj[pikepdf.Name(k)]
            except Exception:
                pass

    try:
        for fname in list(getattr(pdf, "attachments", {}).keys()):
            del pdf.attachments[fname]
    except Exception:
        pass

    try:
        from pikepdf import String  # type: ignore

        pdf.trailer[pikepdf.Name("/ID")] = [
            String(os.urandom(16)),
            String(os.urandom(16)),
        ]
    except Exception:
        pass


def sanitize_inplace(path: Path) -> Dict[str, Any]:
    pikepdf = _pikepdf()
    old_state = read_state(path)

    tmp1 = Path(
        tempfile.mkstemp(
            prefix=path.stem + "_clean_", suffix=path.suffix, dir=str(path.parent)
        )[1]
    )
    tmp2 = Path(
        tempfile.mkstemp(
            prefix=path.stem + "_clean2_", suffix=path.suffix, dir=str(path.parent)
        )[1]
    )

    try:
        with pikepdf.open(str(path), allow_overwriting_input=True) as pdf:
            _strip(pdf)
            _pdf_save(pdf, tmp1)

        with pikepdf.open(str(tmp1)) as pdf2:
            _strip(pdf2)
            _pdf_save(pdf2, tmp2)

        _atomic_replace(tmp2, path)
        try:
            tmp1.unlink(missing_ok=True)
        except Exception:
            pass

        new_state = read_state(path)
        return {"old": old_state, "new": new_state, "path": str(path)}
    except Exception:
        for p in [tmp1, tmp2]:
            try:
                if p.exists():
                    p.unlink(missing_ok=True)
            except Exception:
                pass
        raise


def sanitize_to(path: Path, dest: Path) -> Dict[str, Any]:
    """Export mode: copy to dest then sanitize inplace on dest."""
    # Copy file
    dest.write_bytes(Path(path).read_bytes())
    return sanitize_inplace(dest)

