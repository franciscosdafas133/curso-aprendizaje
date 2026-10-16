# curso-aprendizaje

Skill de Cursor para **Data Mining** y **Machine Learning**: extrae PPT/PDF (con OCR si hay imagen), índice con sinónimos, web filtrada, cuadernos experimentales y simulacros tipo examen.

## Instalar en Cursor (cualquier carpeta de curso)

```bash
git clone https://github.com/franciscosdafas133/curso-aprendizaje.git
cp -R curso-aprendizaje/skills/curso-aprendizaje ~/.cursor/skills/curso-aprendizaje
```

Reinicia Cursor. En el chat de **cualquier proyecto**:

```
Usa curso-aprendizaje.
Ingresa materials/… (o la carpeta de mis apuntes), indexa y ayúdame con [tema].
```

Si no aparece `/curso-aprendizaje`, el texto de arriba basta.

## Dependencias (en el proyecto donde trabajes)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

(`requirements.txt` está en la raíz de este repo.)

## Probar el paquete

```bash
cd curso-aprendizaje
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash comprobar.sh
```

## Material real

Copia PPT/PDF locales a `materials/mi-curso/` **en tu máquina**. No subas materiales privados de campus a GitHub.

## Estructura

| Ruta | Para qué |
|---|---|
| `skills/curso-aprendizaje/` | La skill (SKILL.md + scripts + procedures) |
| `templates/` | Experimentos + simulacro examen |
| `materials/sample-course/` | Fixture de demo |
| `comprobar.sh` | Pruebas automatizadas |

## Relación con product-flow

Esta skill es el **producto** (cursos). El método de construcción es [product-flow](https://github.com/franciscosdafas133/product-flow); no hace falta para usarla día a día.
