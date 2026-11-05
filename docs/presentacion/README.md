# Presentación de defensa

10 diapositivas 16:9, sin dependencias externas y sin conexión.

## Ficheros

| Fichero | Qué es |
|---|---|
| `index.html` | Deck generado (presentar abriéndolo en Chrome) |
| `presentacion.pdf` | Export para entregar o imprimir |
| `index.template.html` | Plantilla editable (texto y layout) |
| `build_presentacion.py` | Genera HTML y los 4 SVG desde los CSV |
| `assets/*.svg` | Histograma, territorios, tramos, robustos y sensibilidad |

## Regenerar

```bash
.venv/Scripts/python.exe docs/presentacion/build_presentacion.py
```

Lee `data/resultados/mongo_esfuerzo_por_municipio.csv`,
`bootstrap_robustos.csv`, `sensibilidad_idw.csv` y
`data/procesado/vpo_municipal.csv`. Si cambian los datos, el deck cambia solo;
no hay cifras tecleadas en el HTML.

## Presentar

Abre `index.html` en Chrome y usa **← →**, **espacio** o clic; **F** para
pantalla completa. El texto completo está en `docs/guion_defensa_12min.md`.

## Exportar PDF

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="docs/presentacion/presentacion.pdf" \
  "file:///C:/Users/mikel/Documents/bigdata-vivienda-euskadi/docs/presentacion/index.html"
```

El CSS de impresión fija páginas de 13,333 × 7,5 in (1280 × 720 px) y una
diapositiva por página.

## Criterio de diseño

La diapositiva 1 responde a la pregunta; las 2–7 la sostienen; la 8 enseña
cómo se calculó y la 9 cómo se prueba; la 10 declara el perímetro. Ningún gráfico
lleva cifras escritas a mano: salen de los CSV.
