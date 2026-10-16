# Inspeccionar curso abierto → descargar aquí → solo teoría

## Idea
No bajas libros “en la skill/repo”. Los bajas **en la carpeta del curso que tienes abierta**.

## Qué hace el agente
Con el workspace = tu curso:

```bash
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir .
```

1. Inspecciona **todo** lo de esta carpeta (semanas, sílabo, libros, notebooks…).
2. Detecta perfil `dm` / `ml`.
3. Descarga lecturas libres a **`./libros/`** (esta carpeta).
4. Indexa en `./data/`.
5. Genera `./generated/A_solo_teoria_*.ipynb`.

## Cómo lo usas tú
1. Abre en Cursor `Data_Mining` o `Machine_Learning` (File → Open Folder).
2. Pide: “usa curso-aprendizaje / genera teoría desde mis materiales y libros”.
3. La skill corre el comando de arriba sobre **esta** carpeta.

## Flags

| Flag | Efecto |
|---|---|
| `--inspect-only` | Solo inventario |
| `--tema "…"` | Fuerza tema |
| `--perfil dm\|ml` | Fuerza perfil |
| `--solo-libros` | Solo indexa `libros/` |
| `--no-fetch` | No descarga |
