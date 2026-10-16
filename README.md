# curso-aprendizaje

Plugin/skill **portable** de aprendizaje DM/ML. Cualquiera lo instala; opera sobre **su** carpeta de curso.

Repo: https://github.com/franciscosdafas133/curso-aprendizaje

---

## Instalar como plugin (recomendado)

### Claude Code — desde el chat

```text
/plugin marketplace add franciscosdafas133/curso-aprendizaje
/plugin install curso-aprendizaje@curso-aprendizaje
```

Luego: `/curso-aprendizaje`

### Cursor — desde la UI

1. **Customize** → instalar **From GitHub Repository**
2. URL: `https://github.com/franciscosdafas133/curso-aprendizaje`
3. Agent chat → `/curso-aprendizaje`

### Un comando (Cursor + Claude)

```bash
curl -fsSL https://raw.githubusercontent.com/franciscosdafas133/curso-aprendizaje/main/install.sh | bash
```

Solo uno:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/franciscosdafas133/curso-aprendizaje/main/install.sh) claude
bash <(curl -fsSL https://raw.githubusercontent.com/franciscosdafas133/curso-aprendizaje/main/install.sh) cursor
```

---

## Usar

1. Abre tu carpeta de curso (`Data_Mining`, `Machine_Learning`, …).
2. `/curso-aprendizaje`
3. “Genera teoría con mis materiales y libros.”

Descarga a `./libros/`, índice en `./data/`, notebooks en `./generated/`.

Deps de scripts:

```bash
pip install -r requirements.txt
```

---

## Qué es

| Pieza | Rol |
|---|---|
| Plugin (Cursor + Claude) | Instalación para cualquiera |
| Skill `curso-aprendizaje` | Método |
| `libros_teoria.py` | Inspeccionar curso → teoría |

Ver `DEFINICION-PRODUCTO.md`. Probar: `bash comprobar.sh`.
