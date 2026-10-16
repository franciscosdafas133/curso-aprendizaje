#!/usr/bin/env python3
"""Consulta el índice con expansión de sinónimos (no solo keyword exacto)."""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_index import expand_text, load_synonyms  # noqa: E402


def query(outdir: Path, q: str, top_k: int = 5, min_score: float = 0.05) -> list[dict]:
    chunks = json.loads((outdir / "chunks.json").read_text(encoding="utf-8"))
    with (outdir / "vectorizer.pkl").open("rb") as f:
        vec = pickle.load(f)
    with (outdir / "matrix.pkl").open("rb") as f:
        matrix = pickle.load(f)
    syn = load_synonyms()
    q_exp = expand_text(q, syn)
    qv = vec.transform([q_exp])
    sims = cosine_similarity(qv, matrix).ravel()
    order = sims.argsort()[::-1]
    hits = []
    for i in order[:top_k]:
        if float(sims[i]) < min_score:
            continue
        c = dict(chunks[i])
        c["score"] = round(float(sims[i]), 4)
        hits.append(c)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--q", required=True)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    hits = query(Path(args.index), args.q, top_k=args.top)
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    else:
        for h in hits:
            print(f"[{h['score']}] {h['locator']} :: {h['text'][:120].replace(chr(10),' ')}")
            print(f"   ← {h['source']} ocr={h.get('ocr')}")
    return 0 if hits else 2


if __name__ == "__main__":
    raise SystemExit(main())
