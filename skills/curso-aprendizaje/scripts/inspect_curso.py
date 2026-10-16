#!/usr/bin/env python3
"""Inspecciona una carpeta de curso: perfil, materiales, libros, temas sugeridos."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

MATERIAL_EXT = {
    ".pdf",
    ".pptx",
    ".ppt",
    ".ppsx",
    ".ipynb",
    ".md",
    ".txt",
    ".csv",
    ".xls",
    ".xlsx",
}

SKIP_DIR_NAMES = {".git", ".venv", "venv", "__pycache__", "data", "generated", "node_modules"}

DM_HINTS = (
    "data mining",
    "datamining",
    "minería de datos",
    "mineria de datos",
    "pca",
    "nmf",
    "dbscan",
    "k-means",
    "kmeans",
    "clustering",
    "atributos",
    "silhouette",
    "zaki",
    "170327",
)
ML_HINTS = (
    "machine learning",
    "aprendizaje automático",
    "aprendizaje automatico",
    "gradient",
    "descenso",
    "sgd",
    "regresión",
    "regresion",
    "backprop",
    "bishop",
    "géron",
    "geron",
    "170338",
)


def _iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() in MATERIAL_EXT or p.name.lower().startswith("readme"):
            out.append(p)
    return sorted(out)


def _score_blob(blob: str) -> tuple[str, dict[str, int]]:
    low = blob.lower()
    dm = sum(1 for h in DM_HINTS if h in low)
    ml = sum(1 for h in ML_HINTS if h in low)
    if "data_mining" in low or "/data mining" in low or "data-mining" in low:
        dm += 3
    if "machine_learning" in low or "machine-learning" in low:
        ml += 3
    perfil = "dm" if dm >= ml else "ml"
    if dm == ml:
        perfil = "dm"  # empate → dm por defecto; el caller puede forzar
    return perfil, {"dm": dm, "ml": ml}


def _topics_from_names(files: list[Path], perfil: str) -> list[str]:
    blob = " ".join(f.name.lower() for f in files)
    candidates: list[tuple[str, tuple[str, ...]]] = [
        ("PCA y reducción de dimensionalidad", ("pca", "dimensional", "nmf")),
        ("Selección y transformación de atributos", ("atribut", "seleccion", "selección", "transformacion", "transformación")),
        ("K-means y distancias", ("k-means", "kmeans", "distancia")),
        ("DBSCAN y clustering jerárquico", ("dbscan", "jerarqu", "hierarchical")),
        ("Validación de clusters", ("silhouette", "davies", "validacion", "validación")),
        ("Descenso de gradiente y SGD", ("gradiente", "gradient", "sgd")),
        ("Regresión lineal", ("regresion", "regresión", "linear regression")),
        ("Overfitting y generalización", ("overfit", "sobreajuste")),
        ("KNN y escala", ("knn", "vecino", "escal")),
    ]
    hits = []
    for tema, keys in candidates:
        if any(k in blob for k in keys):
            # filtrar por perfil aproximado
            if perfil == "dm" and tema.startswith(("Descenso", "Regresión", "Overfitting", "KNN")):
                continue
            if perfil == "ml" and tema.startswith(("PCA", "Selección", "K-means", "DBSCAN", "Validación")):
                # ML también puede usar PCA/k-means vía Bishop; no filtrar tan duro
                pass
            hits.append(tema)
    return hits or (
        ["PCA y clustering"]
        if perfil == "dm"
        else ["Descenso de gradiente y regresión"]
    )


def inspect_curso(curso_dir: Path) -> dict:
    root = curso_dir.expanduser().resolve()
    files = _iter_files(root)
    names_blob = " ".join([root.name, str(root), *[str(f.relative_to(root)) for f in files]])
    # leer READMEs / sílabo nombres (no OCR masivo aquí)
    text_bits = [names_blob]
    for f in files:
        if f.suffix.lower() in {".md", ".txt"} and f.stat().st_size < 200_000:
            try:
                text_bits.append(f.read_text(encoding="utf-8", errors="ignore")[:8000])
            except OSError:
                pass
    blob = "\n".join(text_bits)
    perfil, scores = _score_blob(blob)

    by_folder: Counter[str] = Counter()
    inventory = []
    for f in files:
        rel = f.relative_to(root)
        top = rel.parts[0] if len(rel.parts) > 1 else "."
        by_folder[top] += 1
        inventory.append(
            {
                "path": str(rel),
                "suffix": f.suffix.lower(),
                "bytes": f.stat().st_size,
            }
        )

    libros = [i for i in inventory if i["path"].startswith("libros/") or "/libros/" in i["path"]]
    silabo = [i for i in inventory if "silabo" in i["path"].lower() or "sílabo" in i["path"].lower()]
    semanas = sorted(
        {p.split("/")[0] for p in (i["path"] for i in inventory) if re.match(r"semana-?\d+", p.split("/")[0], re.I)}
    )

    temas = _topics_from_names(files, perfil)
    return {
        "curso_dir": str(root),
        "perfil": perfil,
        "perfil_scores": scores,
        "n_files": len(files),
        "folders": dict(by_folder),
        "semanas": semanas,
        "silabo": silabo,
        "libros": libros,
        "temas_sugeridos": temas,
        "tema_default": temas[0],
        "inventory": inventory,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspecciona carpeta de curso")
    ap.add_argument("--curso-dir", required=True)
    ap.add_argument("--out", default=None, help="JSON de inventario (opcional)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = inspect_curso(Path(args.curso_dir))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"curso_dir: {report['curso_dir']}")
        print(f"perfil:    {report['perfil']}  scores={report['perfil_scores']}")
        print(f"archivos:  {report['n_files']}")
        print(f"semanas:   {', '.join(report['semanas']) or '(ninguna)'}")
        print(f"sílabo:    {len(report['silabo'])} | libros: {len(report['libros'])}")
        print("temas:     " + "; ".join(report["temas_sugeridos"][:6]))
        if args.out:
            print(f"report → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
