---
name: curso-aprendizaje
description: >-
  Skill para cursos de Data Mining y Machine Learning: extrae PPT/PDF (con OCR
  si la diapositiva/página es imagen), indexa conceptos con sinónimos, filtra
  material online por relevancia, genera cuadernos experimentales y simulacros
  con formato de examen. Usar cuando el usuario aporte materiales de curso o
  pida estudiar/preparar evaluación DM/ML en Cursor.
---

# curso-aprendizaje

Transforma materiales de **Data Mining** / **Machine Learning** en aprendizaje usable.

## Flujo (obligatorio)

1. **Ingestar** materiales del curso (`scripts/extract.py`) — OCR si hay imagen.
2. **Indexar** (`scripts/build_index.py`) — TF-IDF + sinónimos (no solo keyword).
3. **Consultar** el índice antes de explicar (`scripts/query_index.py`).
4. **Web opcional** (`scripts/search_web.py`) — filtrar relevancia; citar URL; nunca como “del profesor”.
5. **Generar** desde `templates/experiments/` y `templates/exam/` (adaptar al retrieve).
6. Distinguir en tu respuesta: (a) material indexado (b) propuesta pedagógica (c) web (d) hueco.

## Comandos

Desde la raíz del proyecto de curso (ajusta rutas):

```bash
source .venv/bin/activate  # si existe
python3 skills/curso-aprendizaje/scripts/extract.py \
  --input materials/sample-course --out data/chunks.json
python3 skills/curso-aprendizaje/scripts/build_index.py \
  --chunks data/chunks.json --outdir data/index
python3 skills/curso-aprendizaje/scripts/query_index.py \
  --index data/index --q "normalización en vecinos cercanos"
python3 skills/curso-aprendizaje/scripts/search_web.py \
  --q "KNN feature scaling sklearn" --out data/web.json --offline-demo
python3 skills/curso-aprendizaje/scripts/make_templates.py
```

## Perfiles

- **Data Mining:** énfasis práctica notebook + decisiones al programar.
- **Machine Learning:** teoría + práctica (simulacro con partes separadas).

## Material real del usuario

Copia (localmente) a `materials/mi-curso/` sin subir PDFs privados a repos públicos. Vuelve a extract → index.

## Procedimientos

Lee `procedures/` según la acción.
