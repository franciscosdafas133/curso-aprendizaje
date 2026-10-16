# curso-aprendizaje

Skill de Cursor: **método de aprendizaje** para Data Mining y Machine Learning.

## Método (núcleo)

```text
1) TEORÍA  →  2) PRÁCTICA / experimento  →  3) SIMULACRO de examen
```

- **DM:** un cuaderno con teoría y luego práctica.
- **ML:** cuaderno de teoría **aparte** + cuaderno de práctica **aparte** + simulacro.

La extracción/índice/OCR/web son infraestructura. Lo que importa es generar **Producto A** y **Producto B** desde tus materiales.

## Instalar

```bash
git clone https://github.com/franciscosdafas133/curso-aprendizaje.git
cp -R curso-aprendizaje/skills/curso-aprendizaje ~/.cursor/skills/curso-aprendizaje
pip install -r curso-aprendizaje/requirements.txt
```

Chat: `Usa curso-aprendizaje.`

## Generar material de un tema

```bash
cd curso-aprendizaje && source .venv/bin/activate
python3 skills/curso-aprendizaje/scripts/extract.py --input materials/sample-course --out data/chunks.json
python3 skills/curso-aprendizaje/scripts/build_index.py --chunks data/chunks.json --outdir data/index
python3 skills/curso-aprendizaje/scripts/generate_learning.py \
  --index data/index --tema "KNN y escalado" --perfil dm --outdir examples/generated
```

## Probar

```bash
bash comprobar.sh
```
