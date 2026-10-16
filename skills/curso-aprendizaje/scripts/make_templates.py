#!/usr/bin/env python3
"""Genera plantillas de experimento (3+) y simulacro tipo examen."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "templates/experiments"
EXAM = ROOT / "templates/exam"
EXP.mkdir(parents=True, exist_ok=True)
EXAM.mkdir(parents=True, exist_ok=True)


def nb(cells: list[tuple[str, str]]) -> dict:
    out_cells = []
    for ctype, src in cells:
        out_cells.append(
            {
                "cell_type": ctype,
                "metadata": {},
                "source": [line + "\n" for line in src.strip().split("\n")],
                **({"outputs": [], "execution_count": None} if ctype == "code" else {}),
            }
        )
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "cells": out_cells,
    }


def write_nb(path: Path, cells):
    path.write_text(json.dumps(nb(cells), ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", path)


# 1) KNN + escala
write_nb(
    EXP / "01_knn_escalado.ipynb",
    [
        ("markdown", "# Experimento: KNN y escalado\n**Hipótesis:** sin escalar, una feature con rango grande domina la distancia."),
        ("code", "import numpy as np\nfrom sklearn.datasets import make_classification\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.neighbors import KNeighborsClassifier\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.metrics import accuracy_score\nX, y = make_classification(n_samples=400, n_features=5, n_informative=3, n_redundant=1, random_state=0)\nX[:, 0] *= 1000  # feature desescalada\nXtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)\nknn = KNeighborsClassifier(n_neighbors=5)\nacc_raw = accuracy_score(yte, knn.fit(Xtr, ytr).predict(Xte))\nsc = StandardScaler()\nacc_sc = accuracy_score(yte, knn.fit(sc.fit_transform(Xtr), ytr).predict(sc.transform(Xte)))\nprint('acc_raw', round(acc_raw, 3), 'acc_scaled', round(acc_sc, 3))\nassert acc_sc >= acc_raw - 1e-9"),
        ("markdown", "## Reflexión\n¿Por qué cambia el accuracy? Relaciona con distancias y normalización."),
    ],
)

# 2) overfitting train/test
write_nb(
    EXP / "02_overfitting_train_test.ipynb",
    [
        ("markdown", "# Experimento: sobreajuste (train vs test)\n**Hipótesis:** un árbol muy profundo memoriza train y empeora en test."),
        ("code", "from sklearn.datasets import make_moons\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\nX, y = make_moons(n_samples=300, noise=0.25, random_state=0)\nXtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)\ndeep = DecisionTreeClassifier(max_depth=None, random_state=0).fit(Xtr, ytr)\nshallow = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)\nprint('deep train/test', accuracy_score(ytr, deep.predict(Xtr)), accuracy_score(yte, deep.predict(Xte)))\nprint('shallow train/test', accuracy_score(ytr, shallow.predict(Xtr)), accuracy_score(yte, shallow.predict(Xte)))\ngap_deep = accuracy_score(ytr, deep.predict(Xtr)) - accuracy_score(yte, deep.predict(Xte))\ngap_shallow = accuracy_score(ytr, shallow.predict(Xtr)) - accuracy_score(yte, shallow.predict(Xte))\nassert gap_deep >= gap_shallow - 0.05"),
        ("markdown", "## Reflexión\nExplica overfitting con el gap train−test."),
    ],
)

# 3) k-means k choice
write_nb(
    EXP / "03_kmeans_elegir_k.ipynb",
    [
        ("markdown", "# Experimento: elegir k en k-means\n**Hipótesis:** la inercia baja al subir k, pero el codo sugiere un compromiso."),
        ("code", "import numpy as np\nfrom sklearn.datasets import make_blobs\nfrom sklearn.cluster import KMeans\nX, _ = make_blobs(n_samples=300, centers=3, random_state=0)\ninertias = []\nfor k in range(1, 8):\n    inertias.append(KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_)\nprint('inertias', [round(v, 1) for v in inertias])\n# codo grosero: mayor caída relativa temprana\ndrops = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]\nassert drops[0] > drops[-1]"),
        ("markdown", "## Reflexión\n¿Qué k elegirías y por qué no k máximo?"),
    ],
)

# Exam-format simulacro (DM/ML hybrid structure)
write_nb(
    EXAM / "simulacro_examen.ipynb",
    [
        ("markdown", """# Simulacro de examen — formato realista (DM / ML)

**Asignatura:** Data Mining / Machine Learning (plantilla)  
**Duración orientativa:** 90–120 min  
**Material permitido:** según tu curso (ajusta)  
**Instrucciones:** responde en este notebook. **No abras** `simulacro_examen_SOLUCIONES.md` hasta terminar.

## Estructura (como examen típico)
| Parte | Tipo | Puntos |
|---|---|---|
| A | Teoría corta (razonamiento) | 30 |
| B | Práctica de código / datos | 50 |
| C | Interpretación de resultados | 20 |

---
# Parte A — Teoría (30 pts)
Responde en markdown debajo de cada pregunta. Sé preciso; no copies definiciones vacías.
"""),
        ("markdown", """### A1 (10 pts)
¿Por qué la **escala** de las variables puede cambiar las predicciones de un modelo basado en distancias (p. ej. KNN)? Da un ejemplo numérico mental.
"""),
        ("markdown", "*(tu respuesta A1)*\n"),
        ("markdown", """### A2 (10 pts)
Define **sobreajuste** y explica cómo el split train/test ayuda a detectarlo. ¿Qué no demuestra el accuracy solo en train?
"""),
        ("markdown", "*(tu respuesta A2)*\n"),
        ("markdown", """### A3 (10 pts)
En clustering, ¿por qué maximizar k hasta el número de puntos no es una buena estrategia de evaluación?
"""),
        ("markdown", "*(tu respuesta A3)*\n"),
        ("markdown", """---
# Parte B — Práctica (50 pts)
Completa el código. No uses soluciones externas.
"""),
        ("code", """# B1 (25 pts): compara KNN con y sin StandardScaler en un dataset sintético.
# Escribe tu solución debajo.
import numpy as np
# TODO
"""),
        ("code", """# B2 (25 pts): entrena un árbol profundo vs poco profundo y reporta gap train-test.
# TODO
"""),
        ("markdown", """---
# Parte C — Interpretación (20 pts)
"""),
        ("markdown", """### C1 (20 pts)
Supón que tras escalar, el accuracy de KNN sube. Argumenta si siempre debes escalar en *todos* los modelos del curso y cuándo no aportaría.
"""),
        ("markdown", "*(tu respuesta C1)*\n"),
    ],
)

(EXAM / "simulacro_examen_SOLUCIONES.md").write_text(
    """# Soluciones — simulacro (abrir solo al final)

## A1
Las distancias (euclídea, etc.) se dominan por features con mayor rango. Escalar (p. ej. StandardScaler) iguala contribuciones.

## A2
Sobreajuste: buen rendimiento en train y malo en datos no vistos. Train/test estima generalización. Accuracy solo en train no prueba generalización.

## A3
k máximo puede dar inercia ~0 (cada punto un cluster) sin significado. Se busca compromiso (codo, silhouette, conocimiento del dominio).

## B1 / B2
Ver notebooks de experimento `01_knn_escalado.ipynb` y `02_overfitting_train_test.ipynb`.

## C1
Modelos basados en distancia/regularización sensibles a escala se benefician; árboles suelen ser invariantes a monótonas en una feature. No es regla ciega.
""",
    encoding="utf-8",
)
print("exam solutions ok")
