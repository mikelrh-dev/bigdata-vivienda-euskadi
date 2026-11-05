# Demo Mapa Euskadi — pipeline + choropleth (Hyperframes)

Vídeo de 34 s (1920×1080, sin audio) con el **pipeline real** (fuentes → HDFS
→ Kafka → MongoDB → CSV) y un **mini-choropleth de puntos** usando solo datos
reales del reto de vivienda en Euskadi. Contrato Hyperframes respetado:
timelines GSAP pausados en `window.__timelines`, todo elemento timed con
`class="clip"` + `data-start`/`data-duration`, determinista (sin
`Math.random`/`Date.now`/fetch en runtime salvo el CDN de GSAP 3.15.0).

## Datos usados (sin inventar)

- `data/resultados/mongo_esfuerzo_por_municipio.csv`: **252 filas** (una por
  municipio, verificado contando filas con Python/csv). Columnas reales:
  `codigo_ine`, `nombre`, `territorio`, `tiene_alquiler_oficial`, `n_anuncios`,
  `esfuerzo_joven_pct`, …
- `data/procesado/municipios_euskadi_252.geojson`: **252 features**
  (`datos.features`, CRS EPSG:4326, meta `n_municipios: 252`). Solo se usan
  sus coordenadas para dibujar los puntos: cada centroide municipal se
  normalizó a `x,y ∈ [0,1000]` con los bounds reales
  `lon −3.450329…−1.729239`, `lat 42.471338…43.456846`
  (`x = (lon−minLon)/(maxLon−minLon)*1000`,
  `y = (maxLat−lat)/(maxLat−minLat)*1000`, Y invertida para el SVG).
  Las 252 coordenadas quedaron **hardcodeadas** como `<circle>` en
  `compositions/pipeline-mapa.html` (ningún fetch en runtime).
- `README.md` raíz (infraestructura y conclusiones O1–O4):
  HDFS centro `http://10.22.87.215:50070` usuario `iabd-user15`
  (351 ficheros raw en
  `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`),
  Kafka VM `192.168.201.162:9094` broker 4.3.1 KRaft, topic
  `anuncios_inmobiliarios` con 3 particiones, MongoDB 13 colecciones y
  8 pipelines de agregación.

### Cifras verificadas desde el CSV (Python, 2026-11-04)

| Métrica | Valor | Verificación |
|---|---|---|
| Filas | 252 | `csv.DictReader` |
| `esfuerzo_joven_pct` mediana (252) | **40,9 %** | `statistics.median` |
| `esfuerzo_joven_pct` > 30 % | **249 de 252 (98,8 %)** | conteo binario |
| `esfuerzo_joven_pct` ≤ 30 % | **3**: Garai 24,5 %, Laukiz 26,2 %, Gabiria 22,3 % | conteo binario |
| Máx / Mín esfuerzo | **62,0 % Barakaldo / 22,3 % Gabiria** | max/min |
| Con alquiler oficial | 159 (`tiene_alquiler_oficial=True`), todos > 30 % | filtro |
| Robustos (n ≥ 30) | **Bilbao 173 (60,7 %), Donostia / San Sebastián 113 (61,5 %), Getxo 40 (46,1 %), Vitoria-Gasteiz 39 (53,7 %)** | `n_anuncios` ordenado |
| GeoJSON ↔ CSV | 252 códigos coinciden 1:1, sin huecos | join por `codigo_ine` |

> Nota de transparencia: el README del reto cita «mediana 43,5 %» y «100 % de
> los 159 con dato supera el 30 %» (O1) de un corte anterior. El CSV actual da
> mediana **40,9 %** (42,9 % sobre los 159 oficiales). Esta demo usa siempre
> los valores **recalculados del CSV** (40,9 %, 249/252), que es lo que el
> encargo pide («usando solo datos reales», «columna real», «si el CSV los
> confirma»). Los 4 robustos 173/113/40/39 sí se confirman tal cual.

### Guión (34 s)

| Escena | Tiempo | Contenido |
|---|---|---|
| 1 — Fuentes → HDFS centro | 0–8 s | Eustat · INE · Fotocasa · Pisos.com → HDFS `10.22.87.215:50070` (`iabd-user15`, 351 ficheros) |
| 2 — Kafka VM → Mongo | 8–16 s | Kafka `192.168.201.162:9094` 4.3.1 KRaft · topic `anuncios_inmobiliarios` 3 particiones → Mongo 13 colecciones · 8 pipelines |
| 3 — Agregación → CSV | 16–24 s | 8 pipelines → `mongo_esfuerzo_por_municipio.csv` (252 filas · mediana 40,9 % · 249 > 30 %) |
| 4 — Choropleth de puntos | 24–34 s | Puntos por esfuerzo real (> 30 % naranja vs ≤ 30 % verde) + barras top robustos (n_anuncios) |

Caption permanente: *«Fuente: mongo_esfuerzo_por_municipio.csv +
municipios_euskadi_252.geojson»*.

## Estructura

```
demo-mapa/
├── index.html                  raíz 1920×1080, 34 s, timeline "main"
├── compositions/
│   └── pipeline-mapa.html      4 escenas + caption + barra de progreso
├── meta.json
├── hyperframes.json
├── package.json                hyperframes@0.9.13 (scripts dev/check/render/publish)
├── renders/                    salida de `npm run render`
└── out.mp4                     copia de referencia del render (34,0 s · 2,6 MB)
```

## Componer / reproducir

```bash
cd demo-mapa
npm run check     # lint + runtime + layout + motion + contrast
npx hyperframes snapshot --at 4,12,20,30   # frames PNG para revisar
npm run render    # genera renders/<nombre>_<timestamp>.mp4
```

Verificado: `npm run check` pasa (exit 0, 0 errores; avisos `film_silent`,
`text_below_floor` y tamaño de composición, sin errores). Frames en 4, 12, 20
y 30 s leídos: escena 1 con HDFS completo, escena 2 Kafka→Mongo, escena 3 CSV
con 252 filas, escena 4 con el choropleth (249 naranjas + 3 verdes) y las
barras 173/113/40/39 completadas. Render: `out.mp4` 34,0 s · 2,6 MB (1020
frames, 30 fps).

## GIF para README (`mapa.gif`)

`mapa.gif` (8,5 s · 480×270 · 10 fps · 85 fotogramas · 0,2 MB, verificado con
`ffprobe`) recorta los dos tramos más informativos: **0–2,5 s** (Fuentes→HDFS)
y **28–34 s** (choropleth de puntos + barras top robustos 173/113/40/39
completas; el choropleth empieza en 24 s y a los 25 s las barras aún ocupan
la mitad, por eso se usa el tramo final). Mismo filtro que `demo-kpi/kpi.gif`
(480×270, 10 fps, palettegen 128 colores):

```bash
ffmpeg -y -i demo-mapa/out.mp4 -filter_complex \
  "[0:v]trim=start=0:end=2.5,setpts=PTS-STARTPTS[v0];[0:v]trim=start=28:end=34,setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0,fps=10,scale=480:270:flags=lanczos,palettegen=max_colors=128" palette.png
ffmpeg -y -i demo-mapa/out.mp4 -i palette.png -filter_complex \
  "[0:v]trim=start=0:end=2.5,setpts=PTS-STARTPTS[v0];[0:v]trim=start=28:end=34,setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0,fps=10,scale=480:270:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" demo-mapa/mapa.gif
ffprobe -v error -show_entries stream=width,height,r_frame_rate,codec_name,duration -show_entries format=duration,size -of default=noprint_wrappers=1 demo-mapa/mapa.gif
```

## Dónde están las coordenadas

En `compositions/pipeline-mapa.html`, dentro del `<svg>` de la escena 4
(`#map-points`): un `<circle cx cy>` por municipio (252 en total, incluidos
los 3 halos verdes). Enlace `codigo_ine` → `data-code`, esfuerzo →
`data-esf`. Para regenerarlas desde los datos: leer el GeoJSON, calcular cada
centroide (media de vértices), normalizar contra los bounds de arriba y
sustituir los `<circle>`. La leyenda del mapa nombra a los 3 municipios
≤ 30 % y la caption atribuye ambas fuentes.
