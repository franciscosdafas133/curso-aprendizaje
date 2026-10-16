---
name: curso-aprendizaje
description: >-
  Sistema de aprendizaje DM/ML en Cursor. Si el workspace es una carpeta de
  curso, inspecciona TODO lo que hay ahí, detecta DM/ML, descarga lecturas
  libres a libros/ de ESA carpeta y genera teoría/práctica. No es un resumidor.
---

# curso-aprendizaje

## Dónde opera (importante)

La skill trabaja sobre **la carpeta abierta en Cursor** (workspace), no sobre el repo de GitHub.

```text
Workspace = tu curso (ej. ~/Documents/Data_Mining)
         → inspección
         → descarga a ./libros/   ← aquí, en tu curso
         → índice en ./data/
         → notebooks en ./generated/
```

GitHub solo sirve para **instalar/actualizar** la skill en `~/.cursor/skills/curso-aprendizaje`.  
Después, al pedir teoría/aprendizaje con esta carpeta abierta, el agente ejecuta los scripts **contra el workspace actual**.

## Flujo del agente (obligatorio en carpeta de curso)

Cuando el usuario pida teoría, libros, aprender, o use esta skill y el workspace parezca un curso (`libros/`, `semana-*`, `silabo/`, o nombre Data_Mining / Machine_Learning):

1. `CURSO_DIR` = raíz del workspace (`.` / `$PWD` del proyecto abierto).
2. Localizar scripts en este orden:
   - `~/.cursor/skills/curso-aprendizaje/scripts/`
   - si no, `skills/curso-aprendizaje/scripts/` dentro del repo skill.
3. Correr **sin pedirle al usuario que clone nada**:

```bash
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir "$CURSO_DIR"
```

Eso ya: inspecciona materiales → detecta perfil → **descarga libres a `$CURSO_DIR/libros`** → indexa → genera `generated/A_solo_teoria_*.ipynb`.

4. Mostrar inventario (`data/inventario_curso.json`) y el notebook generado.
5. Si pide también práctica/simulacro, usar el mismo índice / materiales del curso con `generate_learning.py` (Producto A/B).

No descargar en el clone de GitHub. No pedir `--curso-dir` a otra ruta si ya están en el curso.

## Productos

### Producto A — Cuaderno conceptual-experimental (o solo teoría)
- Coloquial → rigor → conexiones; experimento con propósito si aplica.
- Con `--solo-teoria` (vía `libros_teoria.py`): solo teoría desde materiales/libros.

### Producto B — Simulacros
- DM: práctico. ML: teórico + práctico. Soluciones aparte. No fingir examen oficial.

## Método

```text
CARPETA DEL CURSO → inspeccionar → (fetch a ./libros) → índice → A (teoría[+práctica]) → B
```

## Comandos auxiliares

```bash
# Solo inventario
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir . --inspect-only

# A+B clásico si ya hay índice
python3 ~/.cursor/skills/curso-aprendizaje/scripts/generate_learning.py \
  --index ./data/index_curso --tema "…" --perfil dm|ml --outdir ./generated
```

## Principios
Comprensión > acumulación · anclar a materiales del curso abierto · citar procedencia · Jupyter primero.

## Procedimientos
`aprender.md` · `ingestar.md` · `indexar-consultar.md` · `web-y-generar.md` · `libros-teoria.md`
