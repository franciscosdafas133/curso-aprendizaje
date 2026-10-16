#!/usr/bin/env python3
"""Extrae texto de PPTX/PDF/MD/IPYNB; OCR si la diapositiva/página es imagen."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ocr_util import ocr_image, ocr_pil

ROOT = Path(__file__).resolve().parents[3]  # proyecto


def _chunk(source: str, locator: str, text: str, kind: str, ocr: bool = False) -> dict:
    return {
        "source": source,
        "locator": locator,
        "text": (text or "").strip(),
        "kind": kind,
        "ocr": ocr,
    }


def extract_md(path: Path) -> list[dict]:
    return [_chunk(str(path), "body", path.read_text(encoding="utf-8", errors="ignore"), "md")]


def extract_ipynb(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for i, cell in enumerate(data.get("cells", [])):
        src = cell.get("source", [])
        text = "".join(src) if isinstance(src, list) else str(src)
        if text.strip():
            parts.append(_chunk(str(path), f"cell-{i}:{cell.get('cell_type')}", text, "ipynb"))
    return parts


def extract_pptx(path: Path) -> list[dict]:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    from PIL import Image
    import io

    prs = Presentation(str(path))
    out: list[dict] = []
    for si, slide in enumerate(prs.slides, start=1):
        texts: list[str] = []
        ocr_bits: list[str] = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text and shape.text.strip():
                texts.append(shape.text.strip())
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    img = Image.open(io.BytesIO(shape.image.blob))
                    ocr_bits.append(ocr_pil(img))
                except Exception as exc:  # noqa: BLE001
                    ocr_bits.append(f"[ocr-error:{exc}]")
        native = "\n".join(texts).strip()
        if native:
            out.append(_chunk(str(path), f"slide-{si}", native, "pptx", ocr=False))
        if ocr_bits:
            joined = "\n".join(b for b in ocr_bits if b.strip())
            if joined.strip():
                out.append(_chunk(str(path), f"slide-{si}-ocr", joined, "pptx", ocr=True))
        if not native and not ocr_bits:
            out.append(_chunk(str(path), f"slide-{si}", "", "pptx", ocr=False))
    return out


def extract_pdf(path: Path) -> list[dict]:
    import pymupdf
    from PIL import Image
    import io

    doc = pymupdf.open(str(path))
    out: list[dict] = []
    for i, page in enumerate(doc, start=1):
        native = page.get_text("text").strip()
        if native:
            out.append(_chunk(str(path), f"page-{i}", native, "pdf", ocr=False))
        # Si poco texto nativo, rasterizar + OCR
        if len(native) < 40:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            try:
                text = ocr_pil(img)
            except Exception as exc:  # noqa: BLE001
                text = f"[ocr-error:{exc}]"
            if text.strip():
                out.append(_chunk(str(path), f"page-{i}-ocr", text, "pdf", ocr=True))
        # Imágenes embebidas
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                pil = Image.open(io.BytesIO(pix.tobytes("png")))
                t = ocr_pil(pil)
                if t.strip():
                    out.append(_chunk(str(path), f"page-{i}-img-{xref}", t, "pdf", ocr=True))
            except Exception:
                continue
    doc.close()
    return out


def extract_path(path: Path) -> list[dict]:
    suf = path.suffix.lower()
    if suf in {".md", ".txt"}:
        return extract_md(path)
    if suf == ".ipynb":
        return extract_ipynb(path)
    if suf in {".pptx", ".ppt"}:
        return extract_pptx(path)
    if suf == ".pdf":
        return extract_pdf(path)
    if suf in {".png", ".jpg", ".jpeg", ".webp"}:
        return [_chunk(str(path), "image", ocr_image(path), "image", ocr=True)]
    return []


def extract_tree(folder: Path) -> list[dict]:
    chunks: list[dict] = []
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() in {
            ".md",
            ".txt",
            ".pdf",
            ".pptx",
            ".ppt",
            ".ipynb",
            ".png",
            ".jpg",
            ".jpeg",
        }:
            chunks.extend(extract_path(p))
    return [c for c in chunks if c["text"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Archivo o carpeta de materiales")
    ap.add_argument("--out", required=True, help="JSON de chunks")
    args = ap.parse_args()
    src = Path(args.input)
    chunks = extract_tree(src) if src.is_dir() else extract_path(src)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"chunks={len(chunks)} → {out}")
    ocr_n = sum(1 for c in chunks if c.get("ocr"))
    print(f"ocr_chunks={ocr_n}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
