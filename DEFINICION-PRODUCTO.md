# Definición de producto — Sistema inteligente de aprendizaje (DM / ML)

Documento canónico alineado al brief del dueño. Distingue **debe** / **podría** / **por validar**.

## 1. Propuesta de valor

Construimos un **skill de Cursor** que transforma materiales reales del curso en:

- **Producto A:** cuaderno conceptual-experimental (comprender + experimentar con propósito).
- **Producto B:** simulacros de evaluación auténticos (con soluciones aparte).

**No es:** chatbot suelto, resumidor de PDF, ni videocurso genérico.  
**Sí es:** aprendizaje anclado a *tus* diapositivas/apuntes, con perfiles DM vs ML.

## 2. Necesidad

- Desconexión teoría ↔ práctica (saber la definición de KNN ≠ entender escala/k/datos).
- Conectar conceptos, no memorizar islas.
- Prepararse para formatos distintos: DM más práctico; ML teoría exigente + práctica separadas.

## 3. Experiencia de uso

Materiales → indexar → generar A → estudiar (coloquial→rigor→experimento) → generar B → resolver sin soluciones → revisar errores.

## 4. Componentes

| Pieza | Rol |
|---|---|
| Skill `curso-aprendizaje` | Orquesta el método |
| extract / OCR / índice | Infra para anclar al material |
| `generate_learning.py` | Produce A y B |
| Web filtrada | Complemento público citado (opcional) |

## 5. Inteligencia pedagógica

Antes de generar: recuperar del índice; decidir si hace falta experimento, comparación o rigor teórico; no plantilla siempre igual. Etiquetar qué es del material vs propuesta.

## 6. Perfiles

- **DM:** A conecta teoría con decisiones de código; B = simulacro práctico.
- **ML:** A conecta teoría+experimento al aprender; B = **simulacro teórico** + **simulacro práctico** (separados al evaluar).

## 7. Calidad

- Cuaderno: ¿resuelve una dificultad concreta? ¿hay citas?
- Experimento: ¿la hipótesis se observa en el resultado?
- Simulacro: ¿exige razonar/combinar, no copiar definición?

## 8. Alcance actual (MVP)

Skill + índice + generación A/B por tema + fixtures demo + `comprobar.sh`.  
HTML interactivo y OCR masivo de scans: selectivo / pendiente.

## 9. Riesgos / pendientes

Material real de campus (local); embeddings densos; calidad pedagógica en temas fuera de las heurísticas de experimento; no afirmar “examen oficial”.

## 10. Éxito

El estudiante explica el concepto, predice un experimento, y resuelve un simulacro nuevo sin mirar soluciones — mejor que solo releer diapositivas.
