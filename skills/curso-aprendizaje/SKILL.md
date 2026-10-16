---
name: curso-aprendizaje
description: >-
  Aprendizaje DM/ML portable: inspecciona la carpeta de curso abierta, detecta
  DM/ML, descarga lecturas libres a ./libros y genera teoría (y opcionalmente
  práctica/simulacros). Usar cuando el usuario pida teoría, libros, aprender
  del curso, o invoque /curso-aprendizaje. No es un resumidor.
---

# curso-aprendizaje

Skill **portable** (plugin). Opera sobre el **workspace abierto** (la carpeta del curso), no sobre el repo del plugin.

## Resolver scripts

Los scripts están en `scripts/` junto a este `SKILL.md` (instalación plugin o `~/.cursor/skills/…`).

```bash
# SCRIPT_DIR = carpeta scripts/ de esta skill (donde esté instalada)
python3 "$SCRIPT_DIR/libros_teoria.py" --curso-dir "$WORKSPACE_ROOT"
```

`WORKSPACE_ROOT` = raíz del curso abierto en el editor.

## Flujo obligatorio

1. Tomar la carpeta abierta como curso.
2. Ejecutar `libros_teoria.py --curso-dir .` (inspecciona → fetch a `./libros` → índice → `./generated/A_solo_teoria_*.ipynb`).
3. Mostrar inventario (`data/inventario_curso.json`) y el notebook.
4. Si piden práctica/simulacro: `generate_learning.py` con el índice del curso.

No pedir clonar el repo para usar la skill si ya está instalada como plugin/skill.

## Productos

- **A:** cuaderno teórico o conceptual-experimental.
- **B:** simulacros (DM práctico; ML teórico + práctico). Soluciones aparte.

## Procedimientos
`procedures/libros-teoria.md` · `aprender.md` · `ingestar.md` · `indexar-consultar.md` · `web-y-generar.md`
