#!/usr/bin/env python3
"""Búsqueda online pública + filtro de relevancia (evita Wikipedia irrelevante)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_index import expand_text, load_synonyms  # noqa: E402

ALLOW_HINTS = (
    "scikit-learn.org",
    "sklearn",
    "wikipedia.org/wiki/",
    "arxiv.org",
    "pytorch.org",
    "tensorflow.org",
    "readthedocs",
    "github.com",
    "towardsdatascience.com",
)

# Heurística: título debe compartir tokens con la query (tras sinónimos)
STOP = {"de", "la", "el", "en", "y", "o", "a", "un", "una", "the", "and", "for", "to", "of"}


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def duckduckgo_html(query: str, n: int = 8) -> list[dict]:
    """HTML search (sin API key). Puede fallar sin red → lista vacía."""
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(
        url, headers={"User-Agent": "curso-aprendizaje-skill/0.1 (educational)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001
        return [{"error": f"red:{exc}", "title": "", "url": "", "snippet": ""}]

    # resultados: clase result__a / result__snippet
    links = re.findall(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.I | re.S
    )
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|td|div)', html, flags=re.I | re.S)
    out = []
    for i, (href, title) in enumerate(links[:n]):
        title_clean = re.sub(r"<[^>]+>", "", title)
        snip = re.sub(r"<[^>]+>", "", snippets[i]) if i < len(snippets) else ""
        # duckduckgo redirect
        if "uddg=" in href:
            href = urllib.parse.unquote(re.search(r"uddg=([^&]+)", href).group(1))
        out.append({"title": title_clean.strip(), "url": href, "snippet": snip.strip()})
    return out


def relevance_ok(query: str, title: str, snippet: str, min_score: float = 0.08) -> tuple[bool, float, str]:
    syn = load_synonyms()
    q = expand_text(query, syn)
    doc = expand_text(f"{title}\n{snippet}", syn)
    # tokens overlap
    q_toks = {t for t in re.findall(r"[a-zA-Záéíóúñ0-9\-]+", q.lower()) if t not in STOP and len(t) > 2}
    d_toks = {t for t in re.findall(r"[a-zA-Záéíóúñ0-9\-]+", doc.lower()) if t not in STOP and len(t) > 2}
    if not q_toks:
        return False, 0.0, "query-vacía"
    overlap = len(q_toks & d_toks) / len(q_toks)
    vec = TfidfVectorizer(ngram_range=(1, 2))
    try:
        m = vec.fit_transform([q, doc])
        cos = float(cosine_similarity(m[0], m[1])[0, 0])
    except ValueError:
        cos = 0.0
    score = 0.6 * cos + 0.4 * overlap
    # Wikipedia: exigir overlap fuerte (evita artículos random en ES)
    if "wikipedia.org" in (title + snippet + "").lower() or "wikipedia.org" in doc.lower():
        # check url in caller
        pass
    reason = "ok" if score >= min_score else "baja-relevancia"
    return score >= min_score, score, reason


def filter_results(query: str, results: list[dict], min_score: float = 0.12) -> list[dict]:
    kept = []
    for r in results:
        if r.get("error"):
            kept.append({**r, "accepted": False, "reason": r["error"]})
            continue
        url = r.get("url") or ""
        title = r.get("title") or ""
        snip = r.get("snippet") or ""
        ok, score, reason = relevance_ok(query, title, snip, min_score=min_score)
        if "wikipedia.org" in url.lower():
            # exigir que el título contenga algún token fuerte de la query expandida
            syn = load_synonyms()
            q_exp = expand_text(query, syn).lower()
            strong = [w for w in re.findall(r"[a-zA-Záéíóúñ]{4,}", q_exp) if w not in STOP]
            if not any(w in title.lower() for w in strong[:8]):
                ok, reason = False, "wikipedia-irrelevante"
        # prefer allow hints but don't require
        r2 = {**r, "score": round(score, 4), "accepted": ok, "reason": reason}
        if ok:
            kept.append(r2)
        else:
            kept.append(r2)  # se listan rechazados para revisión manual
    return kept


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-score", type=float, default=0.12)
    ap.add_argument("--offline-demo", action="store_true", help="No llama red; usa candidatos fijos")
    args = ap.parse_args()

    if args.offline_demo:
        raw = [
            {
                "title": "sklearn.preprocessing.StandardScaler",
                "url": "https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html",
                "snippet": "Standardize features by removing the mean and scaling to unit variance. Important for distance-based models like KNN.",
            },
            {
                "title": "Anexo:Localidades de España",
                "url": "https://es.wikipedia.org/wiki/Anexo:Localidades_de_España",
                "snippet": "Lista de localidades y municipios de España por comunidad autónoma.",
            },
            {
                "title": "k-nearest neighbors algorithm - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm",
                "snippet": "In statistics, the k-nearest neighbors algorithm is a non-parametric supervised learning method.",
            },
        ]
    else:
        raw = duckduckgo_html(args.q)

    filtered = filter_results(args.q, raw, min_score=args.min_score)
    accepted = [r for r in filtered if r.get("accepted")]
    payload = {
        "query": args.q,
        "accepted": accepted,
        "rejected": [r for r in filtered if not r.get("accepted")],
        "note": "Revisar accepted; rejected incluye Wikipedia irrelevante u otros.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"accepted={len(accepted)} rejected={len(payload['rejected'])} → {out}")
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
