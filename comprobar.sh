#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate

SCR=skills/curso-aprendizaje/scripts
export PYTHONPATH="$SCR"

echo "== plantillas =="
python3 "$SCR/make_templates.py"
test -f templates/experiments/01_knn_escalado.ipynb
test -f templates/experiments/02_overfitting_train_test.ipynb
test -f templates/experiments/03_kmeans_elegir_k.ipynb
test -f templates/exam/simulacro_examen.ipynb
test -f templates/exam/simulacro_examen_SOLUCIONES.md

echo "== extracción + OCR =="
python3 "$SCR/extract.py" --input materials/sample-course --out data/chunks.json
python3 - <<'PY'
import json
chunks=json.load(open("data/chunks.json"))
assert chunks, "sin chunks"
ocr=[c for c in chunks if c.get("ocr")]
assert ocr, "se esperaban chunks OCR de diapositiva/página imagen"
blob=" ".join(c["text"].lower() for c in chunks)
assert "normalizacion" in blob or "normalización" in blob or "knn" in blob
print("ocr_chunks", len(ocr), "ok")
PY

echo "== índice semántico (sinónimo) =="
python3 "$SCR/build_index.py" --chunks data/chunks.json --outdir data/index
# query usa sinónimo "normalización" / no solo la palabra exacta del OCR
python3 "$SCR/query_index.py" --index data/index --q "¿qué dice sobre standardization de features en vecinos?" --json > data/query.json
python3 - <<'PY'
import json
hits=json.load(open("data/query.json"))
assert hits, "sin hits semánticos"
blob=" ".join(h["text"].lower() for h in hits)
assert any(k in blob for k in ("normaliz", "escal", "knn", "distanc")), hits
print("top", hits[0]["score"], hits[0]["locator"])
PY

echo "== web filtrada =="
python3 "$SCR/search_web.py" --q "KNN feature scaling sklearn" --out data/web.json --offline-demo
python3 - <<'PY'
import json
w=json.load(open("data/web.json"))
acc=w["accepted"]; rej=w["rejected"]
assert any("scikit-learn.org" in (a.get("url") or "") for a in acc), acc
assert any("wikipedia" in (r.get("url") or "").lower() and not r.get("accepted") for r in rej) or any(
    "Localidades" in (r.get("title") or "") for r in rej
), rej
print("accepted", len(acc), "rejected", len(rej))
PY

echo "== skill invocable =="
test -f skills/curso-aprendizaje/SKILL.md
grep -q '^name: curso-aprendizaje' skills/curso-aprendizaje/SKILL.md
grep -q 'OCR' skills/curso-aprendizaje/SKILL.md

echo "== experimentos corren =="
python3 - <<'PY'
# smoke de las aserciones de los experimentos (sin jupyter)
import numpy as np
from sklearn.datasets import make_classification, make_moons, make_blobs
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans

X, y = make_classification(n_samples=400, n_features=5, n_informative=3, n_redundant=1, random_state=0)
X[:, 0] *= 1000
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
knn = KNeighborsClassifier(n_neighbors=5)
acc_raw = accuracy_score(yte, knn.fit(Xtr, ytr).predict(Xte))
sc = StandardScaler()
acc_sc = accuracy_score(yte, knn.fit(sc.fit_transform(Xtr), ytr).predict(sc.transform(Xte)))
assert acc_sc >= acc_raw - 1e-9

X, y = make_moons(n_samples=300, noise=0.25, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
deep = DecisionTreeClassifier(max_depth=None, random_state=0).fit(Xtr, ytr)
shallow = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)
gap_deep = accuracy_score(ytr, deep.predict(Xtr)) - accuracy_score(yte, deep.predict(Xte))
gap_shallow = accuracy_score(ytr, shallow.predict(Xtr)) - accuracy_score(yte, shallow.predict(Xte))
assert gap_deep >= gap_shallow - 0.05

X, _ = make_blobs(n_samples=300, centers=3, random_state=0)
inertias = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_ for k in range(1, 8)]
drops = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
assert drops[0] > drops[-1]
print("experiments ok")
PY

echo "OK comprobar.sh"
