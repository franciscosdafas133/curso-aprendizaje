# Inspeccionar curso → solo teoría

La skill **mira toda la carpeta del curso**, detecta si es DM o ML, inventaría materiales/libros/sílabo/semanas y genera un cuaderno solo teórico.

## Uso (recomendado)

```bash
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py \
  --curso-dir .
```

Desde GitHub / clone:

```bash
python3 skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir /ruta/a/tu-curso
```

Qué hace:
1. Inspecciona archivos (`inspect_curso.py`) → perfil + temas + inventario JSON
2. Descarga lecturas libres del catálogo a `libros/` (salvo `--no-fetch`)
3. Extrae texto de **todo el curso** (semanas, sílabo, libros, notebooks…)
4. Indexa y genera `generated/A_solo_teoria_*.ipynb`

## Opciones útiles

| Flag | Efecto |
|---|---|
| `--inspect-only` | Solo inventario, no genera |
| `--tema "…"` | Fuerza el tema |
| `--perfil dm\|ml` | Fuerza el perfil |
| `--solo-libros` | Indexa solo `libros/` |
| `--no-fetch` | No descarga del catálogo |
| `--pages 137-180` | Limita páginas de PDF |

## Salidas en el curso

- `data/inventario_curso.json` — qué encontró
- `data/chunks_curso.json` / `data/index_curso/` — índice
- `generated/A_solo_teoria_*.ipynb` — teoría
