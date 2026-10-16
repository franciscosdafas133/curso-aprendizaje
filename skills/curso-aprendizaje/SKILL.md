---
name: curso-aprendizaje
description: >-
  Sistema inteligente de aprendizaje DM/ML en Cursor: materiales → Producto A
  (cuaderno) y Producto B (simulacros). Incluye flujo general libros→solo teoría
  (fetch legal + índice + notebook) usable en cualquier carpeta de curso.
  No es un resumidor.
---

# curso-aprendizaje

## Qué es (brief del dueño)

No es chatbot ni resumidor. Es un skill que, con **tus** PPT/PDF/apuntes/notebooks:

1. Inspecciona materiales e identifica conceptos / relaciones / dificultades / qué se evalúa.
2. Decide qué experiencias generar (no maximizar archivos).
3. Entrega **Producto A** y **Producto B**.

### Producto A — Cuaderno conceptual y experimental (`.ipynb`)
- Explicación pedagógica (coloquial → rigor → conexiones), no resumen de diapositivas.
- Experimento **con propósito** cuando aporte; si no, otra vía (demo, diagrama…).
- Predicción → observación → interpretación.

### Producto B — Simulacros
- Exigentes, basados en materiales; **no** fingir “examen oficial del profesor”.
- Soluciones **aparte**.
- **Data Mining:** simulacro principalmente **práctico**.
- **Machine Learning:** simulacro **teórico** + simulacro **práctico** (separados en evaluación; conectados en el aprendizaje vía A).

## Método

```text
APRENDER:  materiales → índice → Producto A (teoría + experimento conectados)
EVALUAR:   DM → B práctico | ML → B teórico + B práctico (sin soluciones a la vista)
```

Ingesta/OCR/índice/web = infraestructura. El valor es A y B.

## Flujo del agente

1. Indexar si falta `data/index/`.
2. Consultar índice del tema.
3. `generate_learning.py --perfil dm|ml` → genera A y B según perfil.
4. Guiar estudio de A; luego simulacro(s) sin abrir soluciones.
5. Etiquetar: material indexado / propuesta pedagógica / web / hueco.
6. Razonar cómo enseñar cada concepto (no plantilla rígida siempre igual).

## Comandos

```bash
python3 skills/curso-aprendizaje/scripts/extract.py --input materials/… --out data/chunks.json
python3 skills/curso-aprendizaje/scripts/build_index.py --chunks data/chunks.json --outdir data/index
python3 skills/curso-aprendizaje/scripts/generate_learning.py \
  --index data/index --tema "KNN y escala" --perfil ml --outdir examples/generated
```

### Solo teoría (inspecciona la carpeta del curso)

```bash
# Desde la raíz de tu curso (Data_Mining, Machine_Learning, …)
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir .
```

Auto: detecta DM/ML, lista materiales/libros/sílabo/semanas, descarga libres si faltan, indexa y genera `generated/A_solo_teoria_*.ipynb`.  
Procedimiento: `libros-teoria.md`.

## Principios
Comprensión > acumulación · conexión · experimento con propósito · rigor · citar procedencia · autonomía · Jupyter primero.

## Procedimientos
`aprender.md` · `ingestar.md` · `indexar-consultar.md` · `web-y-generar.md` · `libros-teoria.md`
