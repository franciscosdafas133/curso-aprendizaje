#!/usr/bin/env python3
"""
Genera materiales de APRENDIZAJE desde el índice del curso (no plantillas fijas sueltas).

Producto A: cuaderno conceptual-experimental (.ipynb)
  - explicación progresiva anclada a chunks recuperados
  - experimento con propósito (código ejecutable)
  - preguntas de reflexión

Producto B: simulacro formato examen (.ipynb) + soluciones aparte (.md)
  - preguntas derivadas de los conceptos indexados
  - sin soluciones incrustadas

Perfiles:
  - dm: un cuaderno A (teoría ligera + práctica fuerte)
  - ml: cuaderno A teoría+experimento; opcional --separar-practica
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from query_index import query  # noqa: E402


def _nb(cells: list[tuple[str, str]]) -> dict:
    out = []
    for ctype, src in cells:
        cell = {
            "cell_type": ctype,
            "metadata": {},
            "source": [ln + "\n" for ln in src.strip("\n").split("\n")],
        }
        if ctype == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        out.append(cell)
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "curso_aprendizaje": {"generated": True},
        },
        "cells": out,
    }


def _write_nb(path: Path, cells: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_nb(cells), ensure_ascii=False, indent=2), encoding="utf-8")


def _slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9áéíóúñ]+", "-", s, flags=re.I)
    return s.strip("-")[:60] or "tema"


def _cite(hits: list[dict]) -> str:
    lines = []
    for h in hits:
        src = Path(h.get("source", "?")).name
        loc = h.get("locator", "?")
        ocr = " [OCR]" if h.get("ocr") else ""
        excerpt = re.sub(r"\s+", " ", h.get("text", ""))[:220]
        lines.append(f"- `{src}` / `{loc}`{ocr} (score={h.get('score')}): {excerpt}")
    return "\n".join(lines) if lines else "- (sin hits en el índice)"


def _concept_blob(hits: list[dict]) -> str:
    return "\n\n".join(h.get("text", "") for h in hits)


def _pick_experiment(topic: str, blob: str) -> tuple[str, str, str]:
    """Devuelve (titulo, hipotesis, codigo) según señales del material."""
    t = (topic + " " + blob).lower()
    if any(k in t for k in ("knn", "vecino", "distanc", "escal", "normaliz", "standard")):
        return (
            "KNN y escala de variables",
            "Si una feature tiene rango mucho mayor, domina la distancia y cambia las predicciones de KNN; escalar debería estabilizar.",
            """import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
X, y = make_classification(n_samples=400, n_features=5, n_informative=3, n_redundant=1, random_state=0)
X[:, 0] *= 1000
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
knn = KNeighborsClassifier(n_neighbors=5)
acc_raw = accuracy_score(yte, knn.fit(Xtr, ytr).predict(Xte))
sc = StandardScaler()
acc_sc = accuracy_score(yte, knn.fit(sc.fit_transform(Xtr), ytr).predict(sc.transform(Xte)))
print("acc_raw", round(acc_raw, 3), "acc_scaled", round(acc_sc, 3))
assert acc_sc >= acc_raw - 1e-9
print("OK: el experimento ilustra el efecto de la escala en KNN")""",
        )
    if any(k in t for k in ("overfit", "sobreajuste", "train", "test", "arbol", "tree")):
        return (
            "Sobreajuste: train vs test",
            "Un modelo muy flexible puede memorizar el train y empeorar en test; el gap train−test lo revela.",
            """from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
X, y = make_moons(n_samples=300, noise=0.25, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
deep = DecisionTreeClassifier(max_depth=None, random_state=0).fit(Xtr, ytr)
shallow = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)
gap_deep = accuracy_score(ytr, deep.predict(Xtr)) - accuracy_score(yte, deep.predict(Xte))
gap_shallow = accuracy_score(ytr, shallow.predict(Xtr)) - accuracy_score(yte, shallow.predict(Xte))
print("gap_deep", round(gap_deep, 3), "gap_shallow", round(gap_shallow, 3))
assert gap_deep >= gap_shallow - 0.05
print("OK: mayor capacidad → mayor riesgo de sobreajuste")""",
        )
    if any(k in t for k in ("cluster", "k-means", "kmeans", "agrup")):
        return (
            "Elegir k en k-means",
            "Subir k baja la inercia, pero k máximo no es útil; buscamos un compromiso (codo).",
            """from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
X, _ = make_blobs(n_samples=300, centers=3, random_state=0)
inertias = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_ for k in range(1, 8)]
print("inertias", [round(v, 1) for v in inertias])
drops = [inertias[i] - inertias[i + 1] for i in range(len(inertias) - 1)]
assert drops[0] > drops[-1]
print("OK: la caída de inercia no es uniforme; k máximo no es la meta")""",
        )
    # genérico: siempre hay un experimento mínimo ejecutable
    return (
        f"Exploración numérica del tema «{topic}»",
        "Conectar una afirmación del material con un resultado observable en código.",
        f"""# Experimento genérico anclado al tema: {topic!r}
import numpy as np
rng = np.random.default_rng(0)
x = rng.normal(size=200)
print("media", round(float(x.mean()), 4), "std", round(float(x.std()), 4))
print("Revisa arriba las citas del material y explica qué property estás ilustrando.")
assert x.size == 200""",
    )


def build_teoria_cells(topic: str, hits: list[dict], profile: str) -> list[tuple[str, str]]:
    """FASE 1 — solo teoría (sin código). Orden del método: primero comprender."""
    blob = _concept_blob(hits)
    cites = _cite(hits)
    excerpt = re.sub(r"\s+", " ", blob)[:500]
    focus = (
        "Data Mining: al final de la teoría, anota qué decisión de *código* implica cada idea."
        if profile == "dm"
        else "Machine Learning: rigor en definiciones, supuestos, diferencias entre métodos y consecuencias."
    )
    return [
        (
            "markdown",
            f"""# FASE 1 — TEORÍA (antes de prácticas)
## Tema: {topic}
**Perfil:** {profile.upper()}  
**Regla del método:** no abras el notebook de práctica hasta terminar esta fase.

**Generado:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

---
# 1. En palabras simples (coloquial)
Explícaselo a un compañero en 2 minutos, sin jerga.
Según **tus materiales**:

> {excerpt}{'…' if len(blob) > 500 else ''}
""",
        ),
        (
            "markdown",
            f"""# 2. Cómo funciona de verdad (rigor)
Definiciones, mecanismos, supuestos y consecuencias.
Si algo no está en el índice, etiquétalo **propuesta pedagógica** (no como texto del profesor).

## Citas del índice (procedencia)
{cites}

**Enfoque:** {focus}
""",
        ),
        (
            "markdown",
            f"""# 3. Conexiones (sigue siendo teoría)
- Relación de «{topic}» con otros conceptos del curso
- Qué cambia si varías parámetros / preproceso / métrica (en abstracto)
- Errores conceptuales frecuentes

Escribe aquí tu mapa mental / respuestas teóricas antes de pasar a práctica.
""",
        ),
        ("markdown", "*(tus notas teóricas)*\n"),
    ]


def build_practica_cells(topic: str, hits: list[dict], profile: str) -> list[tuple[str, str]]:
    """FASE 2 — práctica / experimento (después de la teoría)."""
    blob = _concept_blob(hits)
    exp_title, hipotesis, codigo = _pick_experiment(topic, blob)
    cites = _cite(hits)
    return [
        (
            "markdown",
            f"""# FASE 2 — PRÁCTICA / EXPERIMENTO (después de la teoría)
## Tema: {topic}
**Perfil:** {profile.upper()}  
**Regla del método:** ya debiste completar la FASE 1 (teoría).

## Citas a tener a mano
{cites}
""",
        ),
        (
            "markdown",
            f"""# Experimento con propósito
## {exp_title}
**Hipótesis:** {hipotesis}

1. Predice el resultado  
2. Corre el código  
3. Contrasta con la teoría de la FASE 1
""",
        ),
        ("code", codigo),
        (
            "markdown",
            """# Reflexión práctica
1. ¿Confirmó, matizó o contradijo la teoría?
2. Cita al menos una fuente del índice.
3. ¿Qué harías distinto en un examen práctico?
""",
        ),
        ("markdown", "*(tus respuestas)*\n"),
    ]


def build_product_a(
    topic: str,
    hits: list[dict],
    profile: str,
) -> list[tuple[str, str]]:
    """Un solo cuaderno DM: teoría primero, práctica después (mismo archivo)."""
    return (
        [
            (
                "markdown",
                f"""# Producto A — Aprendizaje (teoría → práctica)
## Tema: {topic}
**Método del producto:** **1) TEORÍA → 2) PRÁCTICA/EXPERIMENTO → (luego Producto B simulacro)**  
No mezclar: primero comprender, después experimentar.
""",
            )
        ]
        + build_teoria_cells(topic, hits, profile)
        + build_practica_cells(topic, hits, profile)
    )

def build_simulacro_teorico(topic: str, hits: list[dict]) -> tuple[list[tuple[str, str]], str]:
    """Producto B — línea teórica (ML / cuando la asignatura evalúa teoría aparte)."""
    cites = _cite(hits)
    excerpt = re.sub(r"\s+", " ", _concept_blob(hits))[:450]
    cells = [
        (
            "markdown",
            f"""# Simulacro TEÓRICO — {topic}
**Instrucciones:** solo razonamiento. Sin código. No abras las soluciones hasta terminar.
**Aviso:** preguntas *generadas para practicar* a partir del material indexado; **no** son el examen oficial del profesor.

Citas de apoyo (no las copies como respuesta):
{cites}
""",
        ),
        (
            "markdown",
            f"""### T1 (25 pts) — Mecanismo
Explica con rigor cómo funciona «{topic}». Incluye supuestos.
Fragmento recuperado (orientación):
> {excerpt}…
""",
        ),
        ("markdown", "*(T1)*\n"),
        (
            "markdown",
            """### T2 (25 pts) — Comparación
Compara este enfoque con una alternativa del temario. ¿Cuándo preferirías cada uno?
""",
        ),
        ("markdown", "*(T2)*\n"),
        (
            "markdown",
            """### T3 (25 pts) — Consecuencias
Si cambias un parámetro o condición clave, ¿qué pasa y por qué?
""",
        ),
        ("markdown", "*(T3)*\n"),
        (
            "markdown",
            """### T4 (25 pts) — Situación nueva
Describe un escenario *no idéntico* al de clase y razona la respuesta correcta.
""",
        ),
        ("markdown", "*(T4)*\n"),
    ]
    sol = f"""# Soluciones — simulacro TEÓRICO «{topic}»
Anclar a citas del índice. No inventar “pregunta oficial”.
{cites}
Generado: {datetime.now(timezone.utc).isoformat()}
"""
    return cells, sol


def build_simulacro_practico(topic: str, hits: list[dict], profile: str) -> tuple[list[tuple[str, str]], str]:
    """Producto B — línea práctica (DM principal; también ML práctica)."""
    cites = _cite(hits)
    cells = [
        (
            "markdown",
            f"""# Simulacro PRÁCTICO — {topic}
**Perfil:** {profile.upper()}  
**Instrucciones:** código + interpretación. Sin mirar soluciones.
**Aviso:** práctica generada desde el índice; no es el examen oficial.

Citas:
{cites}
""",
        ),
        (
            "markdown",
            """### P1 (40 pts) — Implementación
Resuelve el problema en código de forma autónoma (no copies un ejemplo de clase al pie de la letra).
""",
        ),
        (
            "code",
            f"""# P1 — {topic!r}
# TODO
raise NotImplementedError("completa P1")
""",
        ),
        (
            "markdown",
            """### P2 (30 pts) — Interpretación
Interpreta la salida. ¿Qué decisión de modelado/datos justifica el resultado?
""",
        ),
        ("markdown", "*(P2)*\n"),
        (
            "markdown",
            """### P3 (30 pts) — Justificación
Si te pidieran cambiar una decisión (escala, k, split, métrica…), ¿cuál y por qué?
""",
        ),
        ("markdown", "*(P3)*\n"),
    ]
    sol = f"""# Soluciones — simulacro PRÁCTICO «{topic}»
Ver experimentos alineados (KNN/escala, overfitting, k-means) según el tema.
Citas:
{cites}
Generado: {datetime.now(timezone.utc).isoformat()}
"""
    return cells, sol


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera Producto A y B desde el índice (brief aprendizaje)")
    ap.add_argument("--index", required=True)
    ap.add_argument("--tema", required=True)
    ap.add_argument("--perfil", choices=("dm", "ml"), default="dm")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--solo-a", action="store_true")
    ap.add_argument("--solo-b", action="store_true")
    args = ap.parse_args()

    hits = query(Path(args.index), args.tema, top_k=args.top, min_score=0.03)
    if not hits:
        print("ERROR: sin hits en el índice para ese tema.", file=sys.stderr)
        return 2

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    slug = _slug(args.tema)
    paths: list[str] = []
    do_a = not args.solo_b
    do_b = not args.solo_a

    # Aprendizaje: teoría y práctica CONECTADAS (Producto A conceptual-experimental)
    if do_a:
        path_a = out / f"A_conceptual_experimental_{slug}_{args.perfil}.ipynb"
        _write_nb(path_a, build_product_a(args.tema, hits, args.perfil))
        paths.append(str(path_a))
        print(f"Producto A (aprender: teoría→experimento conectados) → {path_a}")

    # Evaluación: perfiles distintos (brief §5)
    if do_b:
        if args.perfil == "ml":
            # ML: simulacro teórico Y práctico SEPARADOS
            ct, st = build_simulacro_teorico(args.tema, hits)
            cp, sp = build_simulacro_practico(args.tema, hits, "ml")
            pt = out / f"B_simulacro_TEORICO_{slug}_ml.ipynb"
            pst = out / f"B_simulacro_TEORICO_{slug}_ml_SOLUCIONES.md"
            pp = out / f"B_simulacro_PRACTICO_{slug}_ml.ipynb"
            psp = out / f"B_simulacro_PRACTICO_{slug}_ml_SOLUCIONES.md"
            _write_nb(pt, ct)
            pst.write_text(st, encoding="utf-8")
            _write_nb(pp, cp)
            psp.write_text(sp, encoding="utf-8")
            paths.extend([str(pt), str(pst), str(pp), str(psp)])
            print(f"Producto B teórico  → {pt}")
            print(f"Producto B práctico → {pp}")
        else:
            # DM: evaluación principalmente práctica
            cp, sp = build_simulacro_practico(args.tema, hits, "dm")
            pp = out / f"B_simulacro_PRACTICO_{slug}_dm.ipynb"
            psp = out / f"B_simulacro_PRACTICO_{slug}_dm_SOLUCIONES.md"
            _write_nb(pp, cp)
            psp.write_text(sp, encoding="utf-8")
            paths.extend([str(pp), str(psp)])
            print(f"Producto B práctico (DM) → {pp}")

    man = out / f"manifest_{slug}_{args.perfil}.json"
    man.write_text(
        json.dumps(
            {
                "tema": args.tema,
                "perfil": args.perfil,
                "metodo": "aprender conectado (A); evaluar según perfil (B)",
                "hits": [
                    {"source": h.get("source"), "locator": h.get("locator"), "score": h.get("score")}
                    for h in hits
                ],
                "artifacts": paths,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"manifest → {man}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
