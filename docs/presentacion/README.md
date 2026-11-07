# Presentación de defensa

10 diapositivas 16:9, sin dependencias externas y sin conexión.

## Ficheros

| Fichero | Qué es |
|---|---|
| `index.html` | Deck generado (presentar abriéndolo en Chrome) |
| `presentacion.pdf` | Export para entregar o imprimir |
| `index.template.html` | Plantilla editable (sistema visual y contenido) |
| `build_presentacion.py` | Genera HTML y los 7 SVG desde los CSV |
| `assets/*.svg` | 5 gráficos + 2 capas decorativas (topo y trama) |
| `shots/*.jpg` | Previsualización de las 10 diapositivas |

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
Añade `?static` a la URL para desactivar las animaciones (capturas y OBS).

## Exportar PDF

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="docs/presentacion/presentacion.pdf" \
  "file:///C:/Users/mikel/Documents/bigdata-vivienda-euskadi/docs/presentacion/index.html"
```

El CSS de impresión fija páginas de 13,333 × 7,5 in (1280 × 720 px) y una
diapositiva por página.

## Sistema visual

Dos tonos deliberados, para que el cambio de tema se vea sin anunciarlo:

| Diapositivas | Tono | Fondo |
|---|---|---|
| 1–7 y 10 | Papel | `#F4F0E6`, curvas de nivel al 30 % en `multiply`, grano al 20 % |
| 8–9 | Blueprint | `#090D12`, rejilla cian al 6 %, dos halos y traza de pipeline |

- **Tipografía:** Georgia (titulares y cifras, números tabulares), Segoe UI
  (texto), Consolas (etiquetas y código). Todo del sistema: cero peticiones.
- **Acento único por tono:** terracota `#A8481F` sobre papel, cian `#4CC9F0`
  sobre blueprint. El verde musgo `#1F4B43` solo en etiquetas y barras.
- **Gráficos:** SVG transparentes generados por el build, retintados para
  papel. Por eso se disuelven en el fondo sin caja blanca.
- **Imágenes decorativas:** no son fotos de stock.
  - `assets/topo.svg`: curvas de nivel (el relieve es contexto, no dato).
  - `assets/trama.svg`: **un pictograma de vivienda por anuncio** (759), que en
    la diapositiva 7 convierte la cobertura del dato en textura.
- **Cifras:** las que varían salen de los CSV vía `{{placeholders}}`; el build
  falla si queda alguno sin resolver.

## Criterio de diseño

La diapositiva 1 responde a la pregunta; las 2–7 la sostienen; la 8 enseña
cómo se calculó y la 9 cómo se prueba; la 10 declara el perímetro. Ningún gráfico
lleva cifras escritas a mano: salen de los CSV.
