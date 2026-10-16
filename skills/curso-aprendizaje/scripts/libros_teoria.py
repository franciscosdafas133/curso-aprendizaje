#!/usr/bin/env python3
"""
Punto único (skill general): inspecciona el curso → fuentes → solo teoría.

  python3 libros_teoria.py --curso-dir /ruta/a/tu-curso
  python3 libros_teoria.py --curso-dir /ruta/a/tu-curso --tema "PCA"   # opcional
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from inspect_curso import inspect_curso  # noqa: E402


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Inspecciona carpeta de curso y genera SOLO TEORÍA desde materiales/libros"
    )
    ap.add_argument("--curso-dir", required=True, help="Raíz del curso actual")
    ap.add_argument("--perfil", choices=("dm", "ml"), default=None, help="Forzar perfil (si no, auto)")
    ap.add_argument("--tema", default=None, help="Tema (si no, primer tema sugerido por inspección)")
    ap.add_argument("--no-fetch", action="store_true", help="No descargar lecturas libres del catálogo")
    ap.add_argument("--force-fetch", action="store_true")
    ap.add_argument(
        "--solo-libros",
        action="store_true",
        help="Indexar solo carpeta libros/ (default: todo el curso excepto data/generated)",
    )
    ap.add_argument("--pages", default=None, help="Rango páginas PDF opcional")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--inspect-only", action="store_true", help="Solo inventariar; no generar")
    args = ap.parse_args()

    curso = Path(args.curso_dir).expanduser().resolve()
    if not curso.is_dir():
        print(f"ERROR: no existe carpeta de curso: {curso}", file=sys.stderr)
        return 2

    report = inspect_curso(curso)
    perfil = args.perfil or report["perfil"]
    tema = args.tema or report["tema_default"]

    data = Path(args.data_dir).expanduser().resolve() if args.data_dir else curso / "data"
    out = Path(args.outdir).expanduser().resolve() if args.outdir else curso / "generated"
    data.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    (curso / "libros").mkdir(parents=True, exist_ok=True)

    inv_path = data / "inventario_curso.json"
    report["perfil_usado"] = perfil
    report["tema_usado"] = tema
    inv_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== inspección del curso ===")
    print(f"carpeta:  {curso}")
    print(f"perfil:   {perfil} (scores={report['perfil_scores']})")
    print(f"archivos: {report['n_files']} | semanas={report['semanas']} | libros={len(report['libros'])}")
    print(f"tema:     {tema}")
    print(f"inventario → {inv_path}")
    if args.inspect_only:
        return 0

    py = sys.executable
    if not args.no_fetch:
        fetch_cmd = [
            py,
            str(HERE / "fetch_books.py"),
            "--curso",
            perfil,
            "--outdir",
            str(curso / "libros"),
        ]
        if args.force_fetch:
            fetch_cmd.append("--force")
        run(fetch_cmd)

    # Fuente de extracción: todo el curso o solo libros
    source = str(curso / "libros") if args.solo_libros else str(curso)
    chunks = data / "chunks_curso.json"
    index = data / "index_curso"
    extract_cmd = [
        py,
        str(HERE / "extract.py"),
        "--input",
        source,
        "--out",
        str(chunks),
        "--no-ocr",
    ]
    if args.pages:
        extract_cmd.extend(["--pages", args.pages])
    run(extract_cmd)

    if not chunks.exists() or chunks.stat().st_size < 10:
        print("ERROR: sin chunks tras extract. Revisa materiales del curso.", file=sys.stderr)
        return 2

    n_chunks = len(json.loads(chunks.read_text(encoding="utf-8")))
    if n_chunks == 0:
        print("ERROR: 0 chunks. ¿Carpeta vacía o solo binarios sin texto?", file=sys.stderr)
        return 2
    print(f"chunks indexables: {n_chunks}")

    run([py, str(HERE / "build_index.py"), "--chunks", str(chunks), "--outdir", str(index)])
    run(
        [
            py,
            str(HERE / "generate_learning.py"),
            "--index",
            str(index),
            "--tema",
            tema,
            "--perfil",
            perfil,
            "--solo-teoria",
            "--outdir",
            str(out),
            "--top",
            str(args.top),
        ]
    )
    print(f"listo → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
