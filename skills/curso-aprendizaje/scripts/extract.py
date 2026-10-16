#!/usr/bin/env python3
"""Extrae texto de PPTX/PDF/MD/IPYNB; OCR si la diapositiva/página es imagen."""
from __future__ import annotations

import argparse
import json
import re
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


def extract_md(path: Path, *, max_chars: int = 2500) -> list[dict]:
    """Parte .md largos (p. ej. capítulos de libro) por headings o ventanas."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Split por headings markdown
    parts = re.split(r"(?m)^(?=#{1,3}\s+.+)$", text)
    # re.split con capturas deja headings en lista; reconstruir bloques
    raw_lines = text.splitlines(keepends=True)
    blocks: list[tuple[str, str]] = []
    current_loc = "body"
    buf: list[str] = []
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$")

    def flush() -> None:
        nonlocal buf
        body = "".join(buf).strip()
        if body:
            blocks.append((current_loc, body))
        buf = []

    for line in raw_lines:
        m = heading_re.match(line.strip("\n"))
        if m:
            flush()
            current_loc = re.sub(r"\s+", "-", m.group(2).strip())[:80] or "section"
            buf.append(line)
        else:
            buf.append(line)
    flush()

    if not blocks:
        blocks = [("body", text)]

    out: list[dict] = []
    for loc, body in blocks:
        if len(body) <= max_chars:
            out.append(_chunk(str(path), loc, body, "md"))
            continue
        # ventanas solapadas para bloques enormes
        step = max_chars - 400
        for i in range(0, len(body), step):
            piece = body[i : i + max_chars].strip()
            if piece:
                out.append(_chunk(str(path), f"{loc}@{i}", piece, "md"))
    return out


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


def _parse_pages(spec: str | None) -> set[int] | None:
    """'12-20,45,100-105' → conjunto de páginas 1-indexadas. None = todas."""
    if not spec:
        return None
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a), int(b)
            pages.update(range(lo, hi + 1))
        else:
            pages.add(int(part))
    return pages


def extract_pdf(
    path: Path,
    *,
    no_ocr: bool = False,
    pages: set[int] | None = None,
) -> list[dict]:
    import pymupdf
    from PIL import Image
    import io

    doc = pymupdf.open(str(path))
    out: list[dict] = []
    for i, page in enumerate(doc, start=1):
        if pages is not None and i not in pages:
            continue
        native = page.get_text("text").strip()
        if native:
            out.append(_chunk(str(path), f"page-{i}", native, "pdf", ocr=False))
        if no_ocr:
            continue
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


def extract_path(
    path: Path,
    *,
    no_ocr: bool = False,
    pages: set[int] | None = None,
) -> list[dict]:
    suf = path.suffix.lower()
    if suf in {".md", ".txt"}:
        return extract_md(path)
    if suf == ".ipynb":
        return extract_ipynb(path)
    if suf in {".pptx", ".ppt", ".ppsx"}:
        return extract_pptx(path)
    if suf == ".pdf":
        return extract_pdf(path, no_ocr=no_ocr, pages=pages)
    if suf in {".png", ".jpg", ".jpeg", ".webp"}:
        if no_ocr:
            return []
        return [_chunk(str(path), "image", ocr_image(path), "image", ocr=True)]
    return []


_SKIP_DIR_PARTS = {".git", ".venv", "venv", "__pycache__", "data", "generated", "node_modules"}


def extract_tree(
    folder: Path,
    *,
    no_ocr: bool = False,
    pages: set[int] | None = None,
) -> list[dict]:
    chunks: list[dict] = []
    for p in sorted(folder.rglob("*")):
        if any(part in _SKIP_DIR_PARTS for part in p.parts):
            continue
        if p.name.startswith("."):
            continue
        if p.name in {"README.md", "README_LIBROS.md", "fetch_report.json", "inventario_curso.json"}:
            continue
        if p.is_file() and p.suffix.lower() in {
            ".md",
            ".txt",
            ".pdf",
            ".pptx",
            ".ppt",
            ".ppsx",
            ".ipynb",
            ".png",
            ".jpg",
            ".jpeg",
        }:
            chunks.extend(extract_path(p, no_ocr=no_ocr, pages=pages if p.suffix.lower() == ".pdf" else None))
    return [c for c in chunks if c["text"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Archivo o carpeta de materiales")
    ap.add_argument("--out", required=True, help="JSON de chunks")
    ap.add_argument(
        "--no-ocr",
        action="store_true",
        help="Solo texto nativo (recomendado para libros PDF con texto seleccionable)",
    )
    ap.add_argument(
        "--pages",
        default=None,
        help="Rango de páginas PDF 1-indexado, ej. 180-230,340-390 (solo aplica a PDF)",
    )
    args = ap.parse_args()
    src = Path(args.input)
    page_set = _parse_pages(args.pages)
    if src.is_dir():
        chunks = extract_tree(src, no_ocr=args.no_ocr, pages=page_set)
    else:
        chunks = extract_path(src, no_ocr=args.no_ocr, pages=page_set)
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
