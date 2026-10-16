"""OCR para diapositivas/páginas que son imagen (RapidOCR; Tesseract opcional)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


@lru_cache(maxsize=1)
def _rapid() -> Any:
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def ocr_image(path: str | Path) -> str:
    path = Path(path)
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    # 1) RapidOCR (pip, sin tesseract del sistema)
    try:
        engine = _rapid()
        result, _ = engine(arr)
        if result:
            texts = [row[1] for row in result if row and len(row) > 1]
            return " ".join(texts).strip()
    except Exception as exc:  # noqa: BLE001
        rapid_err = str(exc)
    else:
        rapid_err = ""
    # 2) Tesseract si existe
    try:
        import pytesseract

        return pytesseract.image_to_string(img, lang="spa+eng").strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"OCR no disponible (RapidOCR: {rapid_err or 'sin texto'}; "
            f"Tesseract: {exc}). Instala rapidocr-onnxruntime o tesseract-ocr."
        ) from exc


def ocr_pil(img: Image.Image) -> str:
    tmp = Path("/tmp") / "_curso_ocr_tmp.png"
    img.convert("RGB").save(tmp)
    try:
        return ocr_image(tmp)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
