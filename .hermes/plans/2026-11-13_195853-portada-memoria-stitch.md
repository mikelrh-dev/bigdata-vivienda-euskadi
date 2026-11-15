# Portada de la memoria en Google Stitch — Propuesta 4 (Territorio y personas)

> **Para Hermes:** plan de ejecución con las herramientas MCP de Stitch. No es código;
> los "comandos" son llamadas MCP con sus parámetros. Ejecutar solo cuando el usuario apruebe.

**Goal:** Generar en Google Stitch la portada de la memoria del proyecto (propuesta 4:
territorio + personas), con el título real en español, y dejarla lista para encajar en el PDF.

**Architecture:** Flujo Stitch de 6 pasos: crear proyecto -> generar pantalla con un prompt
descritivo -> recuperar pantalla y descargar screenshot + HTML -> verificar el texto en español
(corrigiendo si hace falta) -> (opcional) variantes -> guardar artefactos. Stitch devuelve una
pantalla web (HTML + PNG), no un PDF A4, así que el último paso para el PDF es componer la
portada en HTML/Imagen dentro de `docs/memoria/build.py`.

**Tech Stack:** MCP `stitch` (Google Stitch), modelo GEMINI_3_8_FLASH, `docs/memoria/build.py`.

---

## Contexto y supuestos

- Título: `¿Dónde pueden vivir los jóvenes en Euskadi?`
- Subtítulo: `Memoria técnica del pipeline de datos y del modelo MongoDB`
- Autor: `Equipo bigdata-vivienda-euskadi`
- Fecha: `2026-11-13`
- Paleta del documento: azul `#1f4e79`, gris `#444`, fondo claro `#f4f7fa`; serif Georgia para
  título, sans Segoe UI para el resto (`docs/memoria/estilo.css`).
- La propuesta 4 es "territorio y personas": mapa de Euskadi muy tenue + siluetas/iconos de
  vivienda y personas jóvenes, título en primer plano, azul con acento cálido (teja/ocre).

**Riesgo principal (asumido):** Stitch dibuja el texto dentro de la imagen y puede colar erratas
en español. Por eso el plan descarga también el **HTML** de la pantalla (descargable con
`download_file`), que sí permite corregir el texto y reutilizarlo en el PDF. Si el texto dibujado
sale mal, se corrige en el HTML y se regenera el PDF con `build.py`.

---

## Task 1: Crear el proyecto Stitch

**Objective:** Tener un contenedor donde generar la portada.

**Llamada MCP:**
- `mcp__stitch__create_project` con `{"title": "Memoria bigdata-vivienda-euskadi"}`

**Verification:** la respuesta incluye un `projectId`. Anótalo; se usa en todos los pasos
siguientes (sin el prefijo `projects/`).

---

## Task 2: Generar la portada (propuesta 4)

**Objective:** Generar la pantalla de portada con el concepto 4.

**Llamada MCP:** `mcp__stitch__generate_screen_from_text`
- `projectId`: el del Task 1
- `deviceType`: `DESKTOP`
- `modelId`: `GEMINI_3_8_FLASH`
- `designSystem`: vacío (primera pantalla: Stitch crea un design system acorde)
- `prompt`: el siguiente (texto literal, en inglés para el modelo, con los textos en español
  entre comillas para que los copie):

```
Design a title page / cover slide for a technical report, desktop layout, editorial and calm.
Composition: left third holds the text block, right two-thirds hold a very faint, light-blue
outline map of the Basque Country (Euskadi) with a few municipalities softly shaded in a warm
terracotta accent. Add minimal line icons of housing (a small building) and two abstract young
people figures near the map, not literal photos. Plenty of white space.

Text (spell exactly, in Spanish):
- Large serif display title in dark navy #1f4e79: "¿Dónde pueden vivir los jóvenes en Euskadi?"
- Smaller clean sans-serif subtitle in grey #444: "Memoria técnica del pipeline de datos y del modelo MongoDB"
- Near the bottom, small sans-serif: "Equipo bigdata-vivienda-euskadi" and below it "2026-11-13"

Palette: navy #1f4e79, warm terracotta accent #C4622D, light background #F4F7FA.
Typography: serif display (Georgia) for the title, clean sans-serif (Segoe UI) for the rest.
No emoji, no gradients, no stock-photo look, no lorem ipsum, no extra English text.
```

**Verification:** la generación puede tardar minutos. Si la llamada expira, NO reintentar:
usar `mcp__stitch__get_screen` cada ~30 s (hasta 10 veces) con el nombre de la pantalla hasta
que esté lista. La respuesta trae `output_components` y el `screenId`.

---

## Task 3: Recuperar y descargar los artefactos

**Objective:** Obtener el screenshot (PNG) y el HTML de la pantalla.

**Llamadas MCP:**
1. `mcp__stitch__get_screen` con `name`: `projects/{projectId}/screens/{screenId}` (salida del Task 2).
2. `mcp__stitch__download_file` con `name` = el `screenshot.name` devuelto -> guarda el PNG.
3. `mcp__stitch__download_file` con `name` = el `html_code.name` devuelto -> guarda el HTML.

**Verification:** el PNG se abre y la composición corresponde a la propuesta 4 (mapa tenue a la
derecha, título a la izquierda, iconos de vivienda/personas, paleta azul + teja). El HTML contiene
las cadenas exactas del título y el subtítulo.

---

## Task 4: Verificar y corregir el texto en español

**Objective:** Asegurar que el título, subtítulo, autor y fecha salgan bien escritos.

**Pasos:**
1. Buscar en el HTML descargado: `¿Dónde pueden vivir los jóvenes en Euskadi?`,
   `Memoria técnica del pipeline de datos y del modelo MongoDB`,
   `Equipo bigdata-vivienda-euskadi`, `2026-11-13`.
2. Si el HTML tiene erratas (lo habitual en texto generado): corregir el HTML directamente con
   `patch`/`write_file`. No hace falta regenerar la pantalla.
3. Si la composición está mal (mapa ilegible, iconos raros, texto solapado): regenerar con
   `mcp__stitch__edit_screens` (mismo `projectId`, `selectedScreenIds: [screenId]`, `prompt` de
   corrección concreto, p. ej. "make the map outline lighter and move the title block clear of the
   map; keep the exact Spanish text unchanged").

**Verification:** `grep` de las 4 cadenas en el HTML -> las 4 presentes. El PNG se ve coherente.

---

## Task 5 (opcional): Variantes para elegir

**Objective:** Explorar 2-3 versiones de la misma portada antes de decidir.

**Llamada MCP:** `mcp__stitch__generate_variants`
- `projectId`, `selectedScreenIds: [screenId]`, `deviceType: DESKTOP`, `modelId: GEMINI_3_8_FLASH`
- `variantOptions`: `{"variantCount": 3, "creativeRange": "EXPLORE", "aspects": ["COLOR_SCHEME", "IMAGES", "LAYOUT"]}`
- `prompt`: "Keep the exact Spanish title, subtitle, author and date. Explore the same cover: lighter
  map, warmer accent, clearer title block."

**Verification:** `mcp__stitch__list_screens` muestra las nuevas pantallas; descargar la favorita.

---

## Task 6: Guardar los artefactos en el repo (requiere aprobación)

**Objective:** Dejar la portada disponible para el PDF.

**Archivos propuestos (NO crear sin confirmar):**
- `docs/memoria/figuras/fig-portada.png` (screenshot de Stitch)
- `docs/memoria/portada-stitch.html` (HTML de la pantalla, con el texto corregido)

**Verification:** ambos archivos existen; el PNG tiene dimensiones coherentes con una portada.

---

## Task 7 (opcional, fuera de Stitch): integrar en el PDF

**Objective:** Que el PDF generado por `build.py` incluya la portada.

**Nota:** `docs/memoria/build.py` hoy genera el front matter + título + índice, no una portada
ilustrada. Para usar la portada 4 hay dos caminos:
- A) Que `build.py` inserte una página de portada con la imagen `fig-portada.png` (página
  completa, sin márgenes) antes del título.
- B) Que `build.py` inserca el `portada-stitch.html` tal cual como primera página (necesita
  ajustar el CSS A4 y el tamaño).

**Files:** modificar `docs/memoria/build.py` (función `build()`), y verificar con
`python docs/memoria/build.py --build` + `--pdf`.

**Verification:** `python docs/memoria/build.py --check` -> `OK 9 capítulos · tokens y figuras
resueltos`; el PDF se abre con la portada en la primera página.

---

## Riesgos y decisiones abiertas

1. **A4 vs pantalla web.** Stitch no produce A4 vertical; genera un lienzo de pantalla. Hay que
   decidir: (a) usar el PNG tal cual y encajarlo, o (b) usar el HTML y ajustar el CSS a A4.
2. **Mapa de Euskadi.** El modelo dibujará una silueta aproximada, no el mapa real. Si hace falta
   precisión, usar `docs/memoria/figuras/fig-mapa-2026.png` como base y superponer el texto en
   HTML (opción B).
3. **Texto generado.** Riesgo de erratas; el HTML descargado es la red de seguridad.
4. **Modificar el repo.** Los Tasks 6 y 7 tocan el repo; requieren confirmación explícita.

## Verificación global (al terminar)

- `docs/memoria/figuras/fig-portada.png` existe y se ve como la propuesta 4.
- El HTML contiene las 4 cadenas exactas en español.
- `python docs/memoria/build.py --check` sigue en OK.
- El PDF (si se hizo el Task 7) arranca con la portada.
