# Presentación v2 — deck nuevo (frontend-slides)

Carpeta de salida para una presentación **nueva**, independiente del deck actual
(`docs/presentacion/`, que sigue generándose con `build_presentacion.py` y no se toca).

## Qué hay aquí

- `guion.md` — guion oral slide por slide, con cifras, gráficas, backups y mapa de rúbrica.
- `index.html` — deck completo, 15 diapositivas + 8 de backup. Estilo **Swiss Modern**.
  Una sola página, CSS/JS inline, sin red: se abre con doble clic.
- `assets/` — 12 PNG de `data/resultados/` copiados para que la carpeta sea portable.
- `presentacion_v2.pdf` — exportación a 1920×1080, 23 páginas (15 + backups).
- H8b (`H8b_modalidad_mediana_eur_m2.png`) se genera en `run_analisis_mongo.py` desde
  `pipeline_modalidades`, que ahora calcula `mediana_eur_m2` por modalidad. Gold pasa a 53/53.

## Cómo se usa

Abrir `index.html` en Chrome. `←` / `→` o clic para navegar; `Ctrl+P` → «Guardar como PDF».
El PDF incluido se generó con Chrome headless:

```
chrome --headless=new --no-pdf-header-footer \
  --print-to-pdf=docs/presentacion_v2/presentacion_v2.pdf \
  file:///.../docs/presentacion_v2/index.html
```

Si cambias una cifra en `guion.md`, actualízala también en `index.html` y vuelve a exportar.
Las cifras canónicas siguen en `data/resultados/*.csv`.

## Skill instalado

```
.agents/skills/frontend-slides/     # 163 ficheros, ~3.9 MB, MIT
```

Invocación en el agente: skill `frontend-slides`. El flujo del skill es:

1. Contarle el contenido (guion, mensajes, imágenes) y el público.
2. Genera 3 previews de estilo; se elige una.
3. Genera el deck completo en el estilo elegido, con escenario fijo 16:9 (1920×1080).
4. Exporta a PDF (`scripts/export-pdf.sh`, requiere Playwright + Chromium) o se imprime
   desde Chrome.

## Estilo elegido

**A · Swiss Modern**: papel `#F5F4F0`, tinta `#121212`, acento bermellón `#C8451B`, rejilla
visible, titulares en Bahnschrift (fallback DIN / Helvetica), cifras tabulares y figuras
enmarcadas con pie mono. Los backups van numerados `B1…B8` para no confundirlos con las 15.

## Reglas para no romper lo que ya funciona

- **No mezclar con `docs/presentacion/`**: el deck de la defensa actual no se regenera aquí.
- Si el deck nuevo usa cifras del proyecto, **alimentarlo desde `data/resultados/*.csv`**;
  no teclear números (P-05).
- Revisar acentos, `ñ` y símbolos (€, ‰, ≥) en el HTML y en el PDF: los presets usan fuentes
  web y conviene comprobar que cargan sin red.
- Comprobar que ningún texto se corta en 16:9 y que el PDF no parte diapositivas.

## Estilos disponibles

12 presets en `STYLE_PRESETS.md` (Swiss Modern, Editorial, Vellum, Terminal Green, etc.) y 34
plantillas "bold" en `bold-template-pack/`, con previews progresivas.
