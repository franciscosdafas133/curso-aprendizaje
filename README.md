# curso-aprendizaje

Skill/plugin **portable** de aprendizaje DM/ML: cualquiera la instala; opera sobre **su** carpeta de curso.

## Instalar (para cualquiera)

### Opción A — Desde GitHub en Cursor (recomendado)

1. Cursor → **Customize** → plugins / **From GitHub Repository**
2. Pega: `https://github.com/franciscosdafas133/curso-aprendizaje`
3. Instala (user o project scope)
4. En Agent chat: `/curso-aprendizaje`

### Opción B — Clone manual

```bash
git clone https://github.com/franciscosdafas133/curso-aprendizaje.git
cp -R curso-aprendizaje/skills/curso-aprendizaje ~/.cursor/skills/
# deps de los scripts
cd curso-aprendizaje && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### Opción C — Plugin local de prueba (Cursor)

```bash
mkdir -p ~/.cursor/plugins/local
cp -R curso-aprendizaje ~/.cursor/plugins/local/curso-aprendizaje
# Reload Window → Customize → verificar plugin
```

### Claude Code

**Skill personal (aparece con `/curso-aprendizaje`):**

```bash
git clone https://github.com/franciscosdafas133/curso-aprendizaje.git
mkdir -p ~/.claude/skills
cp -R curso-aprendizaje/skills/curso-aprendizaje ~/.claude/skills/
```

**Como plugin (sesión de Claude Code):**

```text
/plugin marketplace add franciscosdafas133/curso-aprendizaje
```

o, sin marketplace, clona el repo y:

```bash
claude plugin install ./curso-aprendizaje
```

Luego en el chat: `/curso-aprendizaje` (o el nombre que muestre el plugin).  
Abre la carpeta de tu curso y pide generar teoría — opera sobre esa carpeta.

## Usar

1. Abre tu carpeta de curso (`Data_Mining`, `Machine_Learning`, …).
2. Chat Agent → `/curso-aprendizaje`
3. Pide: “genera teoría con mis materiales y libros”.

La skill inspecciona **esa** carpeta, descarga libres a `./libros/`, indexa y genera `./generated/`.

```bash
# equivalente por terminal
python3 ~/.cursor/skills/curso-aprendizaje/scripts/libros_teoria.py --curso-dir .
# o, si instalaste como plugin, usa la ruta scripts/ del plugin
```

## Qué incluye

| Pieza | Rol |
|---|---|
| Skill `curso-aprendizaje` | Método + orquestación |
| `libros_teoria.py` | Inspeccionar curso → fetch → solo teoría |
| `generate_learning.py` | Producto A/B |
| `plugin.json` | Agent Plugins (portable) |
| `.cursor-plugin/plugin.json` | Cursor Plugins |

Ver `DEFINICION-PRODUCTO.md`. Probar: `bash comprobar.sh`.
