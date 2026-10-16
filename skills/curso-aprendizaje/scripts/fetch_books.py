#!/usr/bin/env python3
"""Descarga solo libros/papers con URL legal (status=free). Los comerciales quedan como pendientes manuales."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "books_catalog.json"
UA = "curso-aprendizaje-skill/0.1 (educational; legal sources only)"


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download_pdf(url: str, dest: Path, timeout: int = 120) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = _get(url, timeout=timeout)
    if len(data) < 2000:
        raise RuntimeError(f"respuesta demasiado corta ({len(data)} bytes) para {url}")
    if not data.startswith(b"%PDF") and b"%PDF" not in data[:1024]:
        raise RuntimeError(f"no parece PDF: {url}")
    dest.write_bytes(data)


def _html_to_text(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</div>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text, flags=re.I)
    text = re.sub(r"&amp;", "&", text, flags=re.I)
    text = re.sub(r"&lt;", "<", text, flags=re.I)
    text = re.sub(r"&gt;", ">", text, flags=re.I)
    text = re.sub(r"&\w+;", " ", text)
    # pdf2htmlEX a veces separa letras con espacios: "C H A P T E R" → dejamos tal cual
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def download_html_chapters(entry: dict, dest_md: Path, force: bool = False) -> dict:
    """Baja capítulos html (pdf2htmlEX .page) del sitio oficial y los junta en un .md."""
    chapters = entry.get("chapters") or []
    if not chapters:
        raise RuntimeError("entrada html_chapters sin 'chapters'")
    dest_md.parent.mkdir(parents=True, exist_ok=True)
    if dest_md.exists() and not force:
        return {"path": str(dest_md), "skipped": True, "bytes": dest_md.stat().st_size}

    parts: list[str] = [
        f"# {entry.get('title')}",
        "",
        f"Fuente: {entry.get('license_note', 'HTML oficial')}",
        "",
    ]
    page_count = 0
    for ch in chapters:
        base = ch["base_url"].rstrip("/") + "/"
        label = ch.get("label") or ch.get("id") or base
        book_html = _get(base + "book.html").decode("utf-8", errors="ignore")
        pages = re.findall(r'data-page-url="([^"]+\.page)"', book_html)
        if not pages:
            raise RuntimeError(f"sin páginas .page en {base}book.html")
        parts.append(f"## {label}")
        parts.append("")
        for pg in pages:
            html = _get(base + pg).decode("utf-8", errors="ignore")
            plain = _html_to_text(html)
            if plain:
                parts.append(f"### {pg}")
                parts.append("")
                parts.append(plain)
                parts.append("")
                page_count += 1
        print(f"  capítulo {label}: {len(pages)} páginas")

    dest_md.write_text("\n".join(parts), encoding="utf-8")
    return {"path": str(dest_md), "pages": page_count, "bytes": dest_md.stat().st_size}


def main() -> int:
    ap = argparse.ArgumentParser(description="Descarga lecturas libres del catálogo del curso")
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    ap.add_argument("--curso", choices=("dm", "ml", "all"), default="all")
    ap.add_argument("--outdir", required=True, help="Carpeta destino (ej. materials/libros o …/Data_Mining/libros)")
    ap.add_argument("--force", action="store_true", help="Re-descargar aunque exista el archivo")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cat = load_catalog(args.catalog)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cursos = ["dm", "ml"] if args.curso == "all" else [args.curso]
    report: dict = {"downloaded": [], "skipped_existing": [], "manual": [], "errors": []}

    for cid in cursos:
        block = cat.get("cursos", {}).get(cid)
        if not block:
            continue
        for entry in block.get("entries", []):
            status = entry.get("status")
            fmt = entry.get("format", "pdf")
            fname = entry.get("filename") or f"{entry.get('id')}.pdf"
            dest = outdir / fname
            meta = {
                "curso": cid,
                "id": entry.get("id"),
                "title": entry.get("title"),
                "filename": fname,
                "topics": entry.get("topics", []),
                "format": fmt,
            }
            if status == "manual":
                report["manual"].append({**meta, "hint": entry.get("hint", "")})
                continue
            if status != "free":
                report["errors"].append({**meta, "error": "entrada sin status free"})
                continue

            if args.dry_run:
                report["downloaded"].append({**meta, "path": str(dest), "dry_run": True})
                continue

            try:
                if fmt == "html_chapters":
                    print(f"descargando capítulos HTML {entry['id']} → {dest}")
                    info = download_html_chapters(entry, dest, force=args.force)
                    if info.get("skipped"):
                        report["skipped_existing"].append({**meta, "path": str(dest)})
                    else:
                        report["downloaded"].append({**meta, **info, "license_note": entry.get("license_note", "")})
                elif fmt == "pdf" or entry.get("url"):
                    if dest.exists() and not args.force:
                        report["skipped_existing"].append({**meta, "path": str(dest)})
                        continue
                    print(f"descargando {entry['id']} → {dest}")
                    download_pdf(entry["url"], dest)
                    report["downloaded"].append(
                        {
                            **meta,
                            "path": str(dest),
                            "url": entry["url"],
                            "bytes": dest.stat().st_size,
                            "license_note": entry.get("license_note", ""),
                        }
                    )
                else:
                    report["errors"].append({**meta, "error": "formato desconocido"})
            except Exception as exc:  # noqa: BLE001
                report["errors"].append({**meta, "error": str(exc), "url": entry.get("url")})
                print(f"ERROR {entry.get('id')}: {exc}", file=sys.stderr)

    lines = [
        "# Libros en esta carpeta",
        "",
        "Generado por `fetch_books.py`. Solo se descargan fuentes **legales/abiertas**.",
        "",
        "## Descargados / presentes",
    ]
    for item in report["downloaded"] + report["skipped_existing"]:
        lines.append(f"- `{item['filename']}` — {item['title']}")
    lines += ["", "## Pendientes (coloca tu PDF legal)", ""]
    if report["manual"]:
        for item in report["manual"]:
            lines.append(f"- `{item['filename']}` — {item['title']}")
            if item.get("hint"):
                lines.append(f"  - {item['hint']}")
    else:
        lines.append("- (ninguno)")
    lines += ["", "## Temas sugeridos", ""]
    for cid in cursos:
        for entry in cat["cursos"][cid]["entries"]:
            if not entry.get("topics"):
                continue
            lines.append(f"### {entry['title']}")
            for t in entry["topics"]:
                extra = t.get("pages") or t.get("chapter") or "?"
                lines.append(f"- **{t['tema']}** → {extra}")
            lines.append("")
    (outdir / "README_LIBROS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    report_path = outdir / "fetch_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"ok downloaded={len(report['downloaded'])} "
        f"existing={len(report['skipped_existing'])} "
        f"manual={len(report['manual'])} "
        f"errors={len(report['errors'])} → {report_path}"
    )
    return 1 if report["errors"] and not (report["downloaded"] or report["skipped_existing"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
