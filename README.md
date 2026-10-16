# curso-aprendizaje

Skill Cursor: **sistema de aprendizaje** para Data Mining y Machine Learning (brief del dueño).

## Productos

| | Qué |
|---|---|
| **A** | Cuaderno conceptual-experimental (teoría coloquial→rigor + experimento con propósito) |
| **B (DM)** | Simulacro **práctico** |
| **B (ML)** | Simulacro **teórico** + simulacro **práctico** (separados) |

Aprender: teoría y práctica **conectadas** (A).  
Evaluar: según perfil (B).

Infra (extract/OCR/índice/web) sirve para anclar al material; no es el producto.

## Instalar

```bash
git clone https://github.com/franciscosdafas133/curso-aprendizaje.git
cp -R curso-aprendizaje/skills/curso-aprendizaje ~/.cursor/skills/curso-aprendizaje
pip install -r curso-aprendizaje/requirements.txt
```

## Generar

```bash
python3 skills/curso-aprendizaje/scripts/extract.py --input materials/sample-course --out data/chunks.json
python3 skills/curso-aprendizaje/scripts/build_index.py --chunks data/chunks.json --outdir data/index
python3 skills/curso-aprendizaje/scripts/generate_learning.py \
  --index data/index --tema "KNN y escalado" --perfil ml --outdir examples/generated
```

## Solo teoría (inspecciona tu carpeta de curso)

```bash
# Instalar skill
cp -R skills/curso-aprendizaje ~/.cursor/skills/curso-aprendizaje

# En la raíz de tu curso (revisa todo lo que hay y procede)
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir .
```

Detalle: `skills/curso-aprendizaje/procedures/libros-teoria.md`.  
Ver `DEFINICION-PRODUCTO.md`. Probar: `bash comprobar.sh`.
