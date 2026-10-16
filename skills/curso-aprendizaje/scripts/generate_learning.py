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

def build_product_b(topic: str, hits: list[dict], profile: str) -> tuple[list[tuple[str, str]], str]:
    cites = _cite(hits)
    blob = _concept_blob(hits)
    excerpt = re.sub(r"\s+", " ", blob)[:400]

    nb_cells: list[tuple[str, str]] = [
        (
            "markdown",
            f"""# Producto B — Simulacro (formato examen)
**Tema ancla:** {topic}  
**Perfil:** {profile.upper()}  
**Instrucciones:** resuelve aquí. **No abras** el archivo de soluciones hasta terminar.

| Parte | Tipo | Puntos |
|---|---|---|
| A | Teoría / razonamiento | 30 |
| B | Práctica (código) | 50 |
| C | Interpretación | 20 |

Material de apoyo (solo orientación; el examen no copia diapositivas):
{cites}
""",
        ),
        (
            "markdown",
            f"""# Parte A — Teoría (30 pts)

### A1 (15 pts)
Con base en el material indexado sobre «{topic}», explica el mecanismo central en tus palabras.
Fragmento recuperado (no lo copies literal en la respuesta final; razona):
> {excerpt}…

### A2 (15 pts)
Describe una consecuencia práctica (qué pasa si ignoras este concepto al programar o al evaluar un modelo).
""",
        ),
        ("markdown", "*(respuesta A1)*\n"),
        ("markdown", "*(respuesta A2)*\n"),
        (
            "markdown",
            """# Parte B — Práctica (50 pts)
Escribe código. No uses el archivo de soluciones.
""",
        ),
        (
            "code",
            f"""# B1 (50 pts) — implementa una comprobación relacionada con: {topic!r}
# Debe correr y dejar un print interpretable.
# TODO: tu solución
raise NotImplementedError("completa B1")
""",
        ),
        (
            "markdown",
            """# Parte C — Interpretación (20 pts)
### C1
Si el resultado de B1 sale distinto a lo que esperabas según el material, ¿qué revisarías primero (datos, escala, split, métrica, k, …)? Justifica.
""",
        ),
        ("markdown", "*(respuesta C1)*\n"),
    ]

    sol = f"""# Soluciones — simulacro «{topic}» (abrir solo al final)

## A1 / A2
Deben anclarse a las citas del índice. No inventar “pregunta oficial del profesor”.
Citas usadas al generar:
{cites}

## B1
Depende del tema. Si el tema habla de escala/KNN, compara KNN con/sin StandardScaler.
Si habla de sobreajuste, compara árbol profundo vs poco profundo (gap train−test).
Si habla de clustering, muestra inertias para varios k.

## C1
Priorizar diagnósticos alineados al concepto (p. ej. escala en modelos por distancia; profundidad en árboles; elección de k).

Generado: {datetime.now(timezone.utc).isoformat()}
"""
    return nb_cells, sol


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera Producto A y B desde el índice del curso")
    ap.add_argument("--index", required=True, help="Carpeta data/index")
    ap.add_argument("--tema", required=True, help="Tema / unidad a estudiar")
    ap.add_argument("--perfil", choices=("dm", "ml"), default="dm")
    ap.add_argument("--outdir", required=True, help="Carpeta de salida (ej. examples/generated)")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument(
        "--solo-a",
        action="store_true",
        help="Solo Producto A (cuaderno conceptual-experimental)",
    )
    ap.add_argument(
        "--solo-b",
        action="store_true",
        help="Solo Producto B (simulacro)",
    )
    args = ap.parse_args()

    hits = query(Path(args.index), args.tema, top_k=args.top, min_score=0.03)
    if not hits:
        print("ERROR: el índice no devolvió hits para ese tema. Reingesta/indexa o reformula.", file=sys.stderr)
        return 2

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    slug = _slug(args.tema)
    manifest = {
        "tema": args.tema,
        "perfil": args.perfil,
        "hits": [{"source": h.get("source"), "locator": h.get("locator"), "score": h.get("score")} for h in hits],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    do_a = not args.solo_b
    do_b = not args.solo_a

    paths = []
    if do_a:
        if args.perfil == "ml":
            # ML: teoría y práctica en artefactos SEPARADOS (como el brief original)
            path_t = out / f"A1_teoria_{slug}_ml.ipynb"
            path_p = out / f"A2_practica_{slug}_ml.ipynb"
            _write_nb(path_t, build_teoria_cells(args.tema, hits, "ml"))
            _write_nb(path_p, build_practica_cells(args.tema, hits, "ml"))
            paths.extend([str(path_t), str(path_p)])
            print(f"Producto A1 TEORÍA  → {path_t}")
            print(f"Producto A2 PRÁCTICA → {path_p}")
        else:
            path_a = out / f"A_teoria_luego_practica_{slug}_dm.ipynb"
            _write_nb(path_a, build_product_a(args.tema, hits, "dm"))
            paths.append(str(path_a))
            print(f"Producto A (teoría→práctica) → {path_a}")

    if do_b:
        cells_b, sol = build_product_b(args.tema, hits, args.perfil)
        path_b = out / f"B_simulacro_{slug}_{args.perfil}.ipynb"
        path_sol = out / f"B_simulacro_{slug}_{args.perfil}_SOLUCIONES.md"
        _write_nb(path_b, cells_b)
        path_sol.write_text(sol, encoding="utf-8")
        paths.extend([str(path_b), str(path_sol)])
        print(f"Producto B → {path_b}")
        print(f"Soluciones  → {path_sol}")

    man = out / f"manifest_{slug}_{args.perfil}.json"
    manifest["artifacts"] = paths
    man.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest   → {man}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
