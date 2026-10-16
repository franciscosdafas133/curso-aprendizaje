# ingestar

1. Localiza la carpeta de materiales (`materials/…`).
2. Corre `extract.py --input … --out data/chunks.json`.
3. Revisa `ocr=true` en chunks: diapositivas/páginas imagen deben tener texto OCR.
4. Si OCR falla, informa al usuario (deps) y no inventes el contenido de la imagen.
