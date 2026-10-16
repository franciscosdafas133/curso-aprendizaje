#!/usr/bin/env python3
"""Índice local semántico: expansión de sinónimos + TF-IDF (cosine)."""
from __future__ import annotations

import argparse
import json
import pickle
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

HERE = Path(__file__).resolve().parent


def load_synonyms() -> dict[str, list[str]]:
    p = HERE / "synonyms.json"
    return json.loads(p.read_text(encoding="utf-8"))


def expand_text(text: str, syn: dict[str, list[str]]) -> str:
    low = text.lower()
    extras: list[str] = []
    for key, alts in syn.items():
        if re.search(rf"\b{re.escape(key.lower())}\b", low) or key.lower() in low:
            extras.extend(alts)
        for a in alts:
            if a.lower() in low:
                extras.append(key)
                extras.extend(alts)
    # también dejar el texto original
    return text + "\n" + " ".join(sorted(set(extras)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    chunks = json.loads(Path(args.chunks).read_text(encoding="utf-8"))
    if not chunks:
        print("sin chunks", file=sys.stderr)
        return 1
    syn = load_synonyms()
    docs = [expand_text(c["text"], syn) for c in chunks]
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vec.fit_transform(docs)
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (out / "vectorizer.pkl").open("wb") as f:
        pickle.dump(vec, f)
    with (out / "matrix.pkl").open("wb") as f:
        pickle.dump(matrix, f)
    meta = {"n_chunks": len(chunks), "method": "tfidf+synonym-expansion"}
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"indexados={len(chunks)} → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
