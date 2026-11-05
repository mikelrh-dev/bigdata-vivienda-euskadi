# Demo KPI Euskadi — Hyperframes

Vídeo de 24 s (1920×1080, sin audio) con 4 KPIs animados sobre los datos reales
del reto de vivienda en Euskadi. Contrato Hyperframes respetado:
timelines GSAP pausados en `window.__timelines`, todo elemento timed con
`class="clip"` + `data-start`/`data-duration`, determinista (sin
`Date.now`/`Math.random`/fetch en runtime salvo el CDN de GSAP).

## Datos usados (sin inventar)

- `data/resultados/mongo_esfuerzo_por_municipio.csv`: **252 filas** (una por
  municipio, verificado contando filas con Python/csv).
- `data/procesado/municipios_euskadi_252.geojson`: solo referencia geográfica.
- `README.md` raíz (conclusiones O1–O4) para las cifras KPIs:

  | Escena | KPI | Fuente |
  |---|---|---|
  | 1 (0–6 s) | **252** municipios | CSV (252 filas), README |
  | 2 (6–12 s) | **43,5 %** esfuerzo joven mediano | README (O1) |
  | 3 (12–18 s) | **100 %** > 30 % (n = 159) | README (O1); el CSV confirma 159 filas con `tiene_alquiler_oficial=True` y 159/159 > 30 % en ese subconjunto |
  | 4 (18–24 s) | **Bilbao 173, Donostia / San Sebastián 113, Getxo 40, Vitoria-Gasteiz 39** (n ≥ 30) | README (O2), verificado en CSV (`n_anuncios`) |

> Nota de transparencia: al recalcular la mediana de `esfuerzo_joven_pct` desde el
> CSV actual salen 40,9 % sobre las 252 filas (42,9 % sobre las 159 con alquiler
> oficial), no el 43,5 % del README; el 43,5 % corresponde a un corte anterior
> del cálculo. La demo usa el 43,5 % citado en el README, como ordena el encargo,
> y la caption lo atribuye a «esfuerzo joven según README del reto». El 100 %
> y el n = 159 sí se confirman tal cual en el CSV.

## Estructura

```
demo-kpi/
├── index.html                  raíz 1920×1080, 24 s, timeline "main"
├── compositions/
│   └── kpi-counters.html       4 escenas + caption + barra de progreso
├── meta.json
├── hyperframes.json
├── package.json                hyperframes@0.9.13 (scripts dev/check/render/publish)
├── renders/                    salida de `npm run render`
└── out.mp4                     copia de referencia del render (24,0 s · 749 KB)
```

## Componer / reproducir

```bash
cd demo-kpi
npm run check     # lint + runtime + layout + motion + contrast
npx hyperframes snapshot --at 2,8,15,22   # frames PNG para revisar
npm run render    # genera renders/<nombre>_<timestamp>.mp4
```

Verificado: `npm run check` pasa (exit 0, 0 errores; único aviso
`film_silent` porque el vídeo no lleva audio). Frames en 2, 8, 15 y 22 s leídos:
escena 1 animando 0→252, escena 2 animando 0→43,5 %, escena 3 en 100 % y
escena 4 con el ranking 173/113/40/39 completado.
