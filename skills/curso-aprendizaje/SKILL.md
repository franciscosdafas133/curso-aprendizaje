---
name: curso-aprendizaje
description: >-
  Método de aprendizaje DM/ML en Cursor: TEORÍA primero, luego PRÁCTICA/experimento,
  luego simulacro de examen. Genera cuadernos desde el índice de tus PPT/PDF.
  Usar para estudiar o prepararse — no como resumidor ni solo como indexador.
---

# curso-aprendizaje

## El método (esto es lo importante)

Orden fijo — **no lo inviertas**:

```text
1) TEORÍA     → comprender (coloquial → rigor → conexiones)
2) PRÁCTICA   → experimento con propósito + reflexión
3) SIMULACRO  → examen (teoría + práctica + interpretación), soluciones aparte
```

| Perfil | Cómo se entrega |
|---|---|
| **Data Mining (`dm`)** | Un cuaderno A: teoría → práctica en ese orden |
| **Machine Learning (`ml`)** | A1 teoría **separada** + A2 práctica **separada** (como evaluación real) |
| Ambos | Producto B = simulacro formato examen |

La ingesta/OCR/índice/web son **infra**. El producto son los cuadernos de aprendizaje.

## Flujo del agente

1. Indexar materiales si falta `data/index/`.
2. Consultar índice del tema.
3. Generar con `generate_learning.py` (no sustituyas por plantillas fijas de `templates/`).
4. Guiar: **terminar teoría → luego práctica → luego simulacro sin soluciones**.
5. Distinguir: material indexado / propuesta pedagógica / web / hueco.

## Comandos

```bash
source .venv/bin/activate
pip install -r requirements.txt   # una vez

python3 skills/curso-aprendizaje/scripts/extract.py --input materials/… --out data/chunks.json
python3 skills/curso-aprendizaje/scripts/build_index.py --chunks data/chunks.json --outdir data/index

# Núcleo: genera teoría→práctica (+ simulacro)
python3 skills/curso-aprendizaje/scripts/generate_learning.py \
  --index data/index --tema "KNN y escalado" --perfil dm --outdir examples/generated

# ML (teoría y práctica en archivos distintos)
python3 skills/curso-aprendizaje/scripts/generate_learning.py \
  --index data/index --tema "KNN y escalado" --perfil ml --outdir examples/generated
```

## Procedimientos

`procedures/aprender.md` · `ingestar.md` · `indexar-consultar.md` · `web-y-generar.md`
