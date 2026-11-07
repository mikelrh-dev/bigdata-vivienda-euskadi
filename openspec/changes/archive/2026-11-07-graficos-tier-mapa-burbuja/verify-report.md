# Verify Report — 2026-11-07-graficos-tier-mapa-burbuja

Change: `2026-11-07-graficos-tier-mapa-burbuja` · Specs: `mongodb-y-analisis`, `presentacion-de-resultados` · Tasks 1.1–5.4 (todas marcadas `[x]` en `tasks.md`).
Verificación ejecutada el 2026-11-07 sobre el working tree real. Sin modificación de código.

## Veredicto GATE: PASS

Los cuatro bloques del GATE se cumplen tal como se definen en `tasks.md` y en las delta specs
(`mongo_tier_confianza.csv` 252 filas, 6 canónicos + vpo terminadas, mapa 252/252, burbuja 4 puntos,
`pytest` verde, doble SHA, PDF 13 páginas, sin Docker/HDFS/Kafka a Mongo).

---

## (1) Tests — PASS

Comando: `.venv/Scripts/python -m pytest tests -q`

Evidencia literal:

```
177 passed, 1 skipped in 7.11s
```

- 178 recolectados (177 passed + 1 skipped), exacto al esperado. Sin fallos pre-existentes.
- `tests/test_tier_confianza.py` aislado: `7 passed in 0.21s`.
- `grep -n "1500\|1800\|37\.69\|38\.17" docs/presentacion/build_presentacion.py` → sin coincidencias
  (`exit=1`): ningún precio/esfuerzo tecleado en las 3 funciones nuevas (tasks.md 5.2).

## (2) Artefactos regenerados — PASS

### 2a. 13 PNG frescos

Los 13 PNG no viven en `docs/presentacion/assets/` sino en `data/resultados/` (los emite
`analysis/run_analisis_mongo.py`: `png_mongo: 13 ficheros`). Todos con timestamp de hoy
`2026-11-07 18:53` tras el doble run:

```
A1_distribucion_esfuerzo_por_TH.png  25948f0f…
A2_pct_inasequibles_por_TH.png       7bce00f9…
B_paro_vs_precio.png                 f6f83c8f…
C_vpo_antiguedad_por_TH.png          b70705f2…
D_distancia_vs_precio.png            f240bccc…
E_demografia_edad.png                fcbd92a7…
F_comparativa_th.png                 63d27069…
G_gaps_limitaciones.png              55eb9703…
g1_esfuerzo_por_territorio.png       25948f0f… (duplicado byte-a-byte de A1)
g2_renta_vs_alquiler.png             d9d1eec9…
g3_top10_precio_medio.png            f233792a…
g4_distribucion_anuncios.png         bb8c2b9b…
g5_esfuerzo_robustos.png             88fd8d5f…
```

Conteo: `ls data/resultados/*.png | wc -l` → `13`. PASS con la salvedad de ruta (P2 en §6).

### 2b. 7 `mongo_*.csv`

```
mongo_accesibilidad_extendida.csv      c2b3b0ac…   252 filas
mongo_alquiler_por_municipio.csv       ff39e852…   252 filas
mongo_esfuerzo_por_municipio.csv       7f813fd6…   252 filas
mongo_modalidades.csv                  67e8120a…   2 filas
mongo_tier_confianza.csv               b8411b77…   252 filas
mongo_vpo_por_municipio.csv            66e8a674…   322 filas
mongo_vpo_terminadas_por_municipio.csv d9a512c8…   251 filas
```

Los 6 canónicos + `mongo_vpo_terminadas_por_municipio.csv` presentes. PASS.

### 2c. Doble SHA de `run_analisis_mongo.py` — PASS

Tres lecturas (antes, tras run 1, tras run 2) — SHA idéntico en las tres:

```
b8411b77fdfa8df60b06618883dc05ee6bd04699b319b3dbb6b28ee9a8103015 *data/resultados/mongo_tier_confianza.csv
7f813fd61ee6800dacd24a230aaef43a8d97e9dbe1abd0300fa1da5b974f75a3 *data/resultados/mongo_esfuerzo_por_municipio.csv
```

Salida del propio script: `reproducibilidad: ok (dos ejecuciones con la misma huella)`,
`huella: 3e54ee4927729c008e7fa38e64190ca85b662ae464aa2096c76dcaa0903bb45b`.
Coinciden con los SHA esperados `b841…` / `7f81…`. PASS.

### 2d. 3 SVG nuevos en `docs/presentacion/assets/` — PASS

Todos frescos `2026-11-07 18:38`, sin commitear aún (`??` en `git status`, esperado pre-archive):

```
-rw-r--r--  11532  chart_tierB_range.svg
-rw-r--r--  5907484 chart_mapa_tier.svg
-rw-r--r--  13206  chart_effort_vs_n.svg
```

Junto a los 7 SVG previos regenerados a la misma hora (`histograma_esfuerzo`, `territorios`,
`tramos`, `robustos`, `sensibilidad`, `topo`, `trama`). Contenido:

| SVG | Evidencia literal |
|---|---|
| `chart_tierB_range.svg` | `Sopela`, `Zarautz`, `Santurtzi` presentes; `indicativo` ×2 |
| `chart_mapa_tier.svg` | `grep -c "252 contextual sobre 159"` → `1`; texto literal presente |
| `chart_effort_vs_n.svg` | 4 nombres exactos: `Bilbao`, `Donostia`, `Getxo`, `Vitoria`; `n_insuficiente` ×1 |

GeoJSON: `data/procesado/municipios_euskadi_252.geojson` → `metadata.n_municipios = 252`.

### 2e. `index.html` sin placeholders — PASS

```
grep -c "{{" docs/presentacion/index.html  →  0
grep "Sopela 19" docs/presentacion/index.html → "Sopela 19: temporal 1500 (n=9) · larga 1500 (n=8) · Zarautz 15: temporal 1200 (n=9) · larga 1800 (n=6) · Santurtzi 11: temporal 1250 (n=5) · larga 1900 (n=4)"
grep -c "chart_tierB_range|chart_mapa_tier|chart_effort_vs_n" → 3
```

Los `{{…}}` de `index.template.html` son el sistema de plantilla (patrón vigente del build),
no placeholders pendientes en el HTML renderizado. PASS.

### 2f. `presentacion.pdf` — PASS

```
pypdf pages: 13
PDF text: 'Tier B' → True, '252 contextual' → True, 'n_insuficiente' → True
```

13 páginas, 7,87 MB, `2026-11-07 18:45`. Los 3 gráficos nuevos están en el PDF. PASS.

## (3) Pipeline tier — PASS

### Tier B (min/max/mediana por modalidad, de `mongo_tier_confianza.csv`)

| Municipio | n_anuncios | temporal (mediana, n) | larga (mediana, n) |
|---|---|---|---|
| Sopela | 19 | 1500 (n=9) | 1500 (n=8) |
| Zarautz | 15 | 1200 (n=9) | 1800 (n=6) |
| Santurtzi | 11 | 1250 (n=5) | 1900 (n=4) |

Coinciden literalmente con los valores del GATE. Columnas presentes en el CSV:
`min_precio_temporal, max_precio_temporal, mediana_precio_temporal, n_precio_temporal,
min_precio_larga, max_precio_larga, mediana_precio_larga, n_precio_larga`. PASS.

### Tier A (esfuerzo rankeable, `mongo_esfuerzo_por_municipio.csv`, `tier == 'A'`, 4 filas)

| Municipio | n_anuncios | n_precio | esfuerzo_joven_pct_18_34 |
|---|---|---|---|
| Bilbao | 204 | 190 | 37.688581 → **37.69** |
| Donostia / San Sebastián | 126 | 121 | 38.170379 → **38.17** |
| Getxo | 50 | 48 | 28.595300 → **28.60** |
| Vitoria-Gasteiz | 39 | 39 | 33.368953 → **33.37** |

PASS contra `204/126/50/39` y `37.69/38.17/28.60/33.37`.

### Distribución 252 filas

```
tier value_counts: {'D': 188, 'C': 57, 'A': 4, 'B': 3}  → total 252
```

**4/3/57/188 = 252**. PASS.

## (4) Libertades — PASS

- **Sin Docker**: `ls Dockerfile* docker-compose*` → no existen; `docker ps` → daemon no disponible
  ("could not find the file specified"); `git status | grep docker` → vacío. Ningún servicio levantado.
- **HDFS solo raw**: `storage/hdfs_utils.py` solo sube raw (`upload_raw_excluding_legacy`,
  `data/_hdfs_state/hdfs_upload_raw.json`); `analysis/run_analisis_mongo.py` y
  `analysis/mongo_aggregations.py` sin referencias a HDFS (grep vacío).
- **Kafka → HDFS, no a Mongo**: `grep mongo storage/kafka_hdfs_uploader.py storage/kafka_raw_producer.py`
  → vacío; el uploader escribe en HDFS (`/raw/…`), Mongo solo se alimenta vía `storage/load_mongo.py`
  desde raw/HDFS.
- **Raw intacto**: `git status --porcelain -- data/raw` → vacío (0 diffs). `data/raw` = 356 ficheros
  recursivos / 200 en primer nivel; `docs/raw_manifest_sha256.txt` = 354 entradas y aparece como
  `M` en el working tree global, pero es deriva pre-existente ajena a este change
  (ver §6, P2): `data/raw` en sí tiene 0 diffs contra HEAD.

## (5) Lista de requisitos de las delta specs

| Requisito | Estado |
|---|---|
| AGREGACION-01: min/max/mediana temporal/larga + esfuerzo por Tier A, 252 filas, doble SHA, `pytest` verde | Cumplido |
| chart_tierB_range: 3 barras 19/15/11, min-max, doble mediana con su n, `indicativo`, sin promediar | Cumplido |
| chart_mapa_tier: SVG coroplético 4 cromas A/B/C/D, join `codigo_ine`, capas 159/93/252, texto `252 contextual sobre 159` | Cumplido (capas verificadas en datos: `capa_oficial.csv` 159, `capa_idw.csv` 93, `capa_contexto.csv` 252) |
| chart_effort_vs_n: burbuja exactamente 4 puntos Tier A, banda `n_insuficiente`, sin ranking 1-16 | Cumplido (4 nombres + banda presentes en SVG) |
| Scenario: sin valores inventados | Cumplido (grep literales vacío) |

## (6) Pendientes

### P1 — ninguno (bloqueante)

Ningún criterio del GATE está incumplido. No hay P1.

### P2 — no bloqueantes (documentación/higiene)

- **P2-1** `tasks.md` 5.1 habla de "13 PNG" sin ruta: los PNG están en `data/resultados/`
  (salida de `run_analisis_mongo.py`), mientras que los gráficos de presentación son SVG en
  `docs/presentacion/assets/`. El GATE se cumple en ambos sitios, pero convendría fijar la ruta
  canónica de los 13 PNG en `tasks.md` para evitar la lectura "assets = 13 PNG".
- **P2-2** `docs/presentacion/assets/chart_mapa_tier.svg` pesa 5,9 MB (geometrías embebidas
  completas). Funciona, pero es el artefacto más pesado de la presentación; candidato a
  simplificación de precisión en un change posterior.
- **P2-3** Working tree muy sucio de cambios ajenos al change (`git status` muestra decenas de `M`
  en `transform/`, `tests/`, `extract/`, `docs/` no relacionados). `data/raw` como tal es 0 diffs,
  pero `docs/raw_manifest_sha256.txt` figura `M`: conviene commitear/aislar los cambios de este
  change antes del archive para que la auditoría del GATE sea limpia.
- **P2-4** `data/resultados/g1_esfuerzo_por_territorio.png` es byte-a-byte idéntico a
  `A1_distribucion_esfuerzo_por_TH.png` (mismo SHA `25948f0f…`): duplicación heredada del
  generador, no introducida por este change. Solo informativo.
