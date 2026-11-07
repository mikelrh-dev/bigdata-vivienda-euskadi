# Archive report: 2026-11-07-pisos-re-resolver-ubicacion

Archivado: 2026-11-07 (SDD-Archive, Modo openspec, rama `master`, sin commit/push).
Estado: CERRADO. Deltas sincronizados a `openspec/specs/` base sin perder requisitos (ver §5).

## 1. Resolución P1-1 — `indicadores` stale (759 → 594)

**Causa:** `dim_municipios_enriquecido.csv` y `analisis_variables_base.csv` de 2026-11-05 no regenerados tras T3 (`dim_municipios.csv` 2026-11-07 15:23). `storage/load_mongo.py` consume enriquecido (`load_municipios`) y `analisis_variables_base` (`load_indicadores:317-348`), de ahí `indicadores` suma 759 (Bilbao 173) vs `anuncios` 594 (Bilbao 204) en verify-report Gate 3 / P1-1.

**Fix aplicado (archive):**
- Backup silver previo en `scratchpad/p1-1_backup_2026-11-07/` (analisis_variables_base, dim_municipios, dim_municipios_enriquecido, dim_municipios_renta, dim_municipios_tension).
- Cadena regenerada en orden topológico (base → enricher):
  `transform/generar_analisis_variables_base.py` → `transform/calcular_renta_joven.py` → `transform/calcular_tension_social.py` → `transform/construir_dim_gold.py`
- Recarga Mongo vía `python -m storage.load_mongo` (staging+backup+rename+`ensure_indexes`, nunca `drop()` directo). Invocación como script directo falla (`ModuleNotFoundError: storage`); usar `-m`.
- `dim_municipios.py` NO re-ejecutado a propósito: cuenta `n_anuncios` desde raw por `municipio_busqueda` (`transform/dim_municipios.py:158`) y resucitaría el baseline 173/759, violando PISOS-01. Se conserva `dim_municipios.csv` (594/843) generado por T3 (`unificar` → `aplicar_cobertura`).
- Manifests regenerados `python extract/generar_manifest.py --write` (3 hashes cambiados: analisis_variables_base, dim_municipios_enriquecido, dim_municipios_renta).

**Verificación post-fix (Mongo `vivienda_euskadi`, literal):**
```
anuncios 594; indicadores 252; suma n_anuncios 594.0
TOP: Bilbao 204.0, Donostia / San Sebastián 126.0, Getxo 50.0, Vitoria-Gasteiz 39.0, Sopela 19.0, Zarautz 15.0
L2 (10-29): 3
zeros (n_anuncios==0): 188
tasa_paro_lanbide_pct non-null: 249
anuncios__backup: 594; municipios: 252
gold dim_municipios_enriquecido.csv: 252 filas, suma 594 / raw 843, L2 3, zeros 188
mongo_esfuerzo_por_municipio.csv: 252 filas, suma n_anuncios 594, precio_medio_eur non-null 62 (=> precio 62/252)
load_all: {'municipios': 252, 'anuncios': 594, 'alquiler_municipal': 252, 'indicadores': 252, ...}
```
Especificación de entrada cumplida: indicadores suma 594, Bilbao 204, L2 3, precio 62/252.

## 2. Gates finales (evidencia literal)

```
$ .venv/Scripts/python -m pytest tests -q
166 passed, 1 skipped in 7.76s  (EXIT 0)
$ .venv/Scripts/python -m pytest tests -q -rs
SKIPPED [1] tests\test_pisos_ubicacion_real.py:239: skip separado: MONGO_ALLOW_DESTRUCTIVE!=1
166 passed, 1 skipped
$ ls data/resultados/*.png | wc -l  -> 13
$ ls data/resultados/mongo_*.csv | wc -l -> 6
# SHA RUN1 == SHA RUN2 (6/6 idénticos), huella 3edd333226de95900244746863e65194f38a09ca8e6fca3f4dca998ed2e23d8f
c2b3b0aca38d52c7f9bedb1c6202c1e4eb7fc8557509b7dcfec0516beaa8ce5e *mongo_accesibilidad_extendida.csv
ff39e852d27a754eabb2fe3db76c71c1ac35e8a0cdcd4e799ff9fb7c9798263e *mongo_alquiler_por_municipio.csv
2c72d19377e3d3ffea005c0d57079150bf5670236f887227a1c6d1068d48b999 *mongo_esfuerzo_por_municipio.csv
67e8120a311666d8cb7d3522766e8a19da468da34fb578c900d702bf2d81bcf0 *mongo_modalidades.csv
66e8a674af835c3f60d1b629f119095f16f25e7ae6b2197ab203feb9eff929d7 *mongo_vpo_por_municipio.csv
d9a512c82d9c493499b757fbb914b3ee331e0b3e390b59a64c1f4ab6c1f587bb *mongo_vpo_terminadas_por_municipio.csv
reproducibilidad: ok (dos ejecuciones con la misma huella)
$ .venv/Scripts/python extract/generar_manifest.py --verify
OK: ...\docs\raw_manifest_sha256.txt (354 entradas, 0 errores)
OK: ...\data\procesado\manifest_sha256.txt (187 entradas, 0 errores)
$ grep -n municipio_busqueda transform/unificar_anuncios.py
64:        if not any(k in it for k in ("precio_eur", "municipio", "municipio_busqueda")):  # solo filtro validez; 0 en transform_pisos
$ python -c "from transform.muni_resolve import resolver_codigo; print(resolver_codigo(None, '48020'))"
(None, None)
$ git status -sb -> ## master...origin/master (sin ahead, sin push; sin Docker; HDFS solo raw; Kafka->HDFS, nunca Kafka->Mongo)
```
Conteo gates: **166 passed / 1 skipped**, doble SHA idéntico, **13 PNG / 6 CSV**, manifests **354 + 187**. Especificación de entrada cumplida.

## 3. Reconciliación P2 (archive)

- **P2-1 Spec stale:** delta `presentacion-de-resultados/spec.md:11` Bilbao 173/Donostia 113/Getxo 40/Vitoria 39 y L2=16 actualizados en spec base a valores reales **204/126/50/39, L2=3** (`openspec/specs/presentacion-de-resultados/spec.md`, `RESPUESTA-01` + `CONCLUSION-01` extensión). Docs ya sincronizados: `README.md:143-144` (Bilbao 204/Donostia 126/Getxo 50/Vitoria 39, Nivel1 4/Nivel2 54/Nivel3 194, L2=3), `docs/conclusiones_municipios.md:29-31`, `docs/guion_defensa.md:45-47`, `docs/metodologia.md:17`.
- **P2-2 Universo 263 vs 87 silver:** pitch 245 (baseline 187/245 por búsqueda) no es el universo raw. Real: `anuncios_pisos_dirigido.csv` 263 filas, `anuncios_pisos_enriquecido.csv` 235, `anuncios_unificados.csv` portal pisos 87 (tras dedup/filtros/fingerprint) + `cuarentena_pisos.csv` 45 `fuera_de_euskadi` = 132 trazables. La defensa no debe invocar 245 como silver; canónico: 263 raw / 87 silver / 45 cuarentena. Documentado en `openspec/specs/extraccion-datos/spec.md` (EXTRACCION-01 pisos).
- **P2-3 Backup 759 → 594:** el 759 es el pre-change (delta CARGA-SEGURA-01). Post-recarga y persona: `anuncios=594`, `anuncios__backup=594`. Actualizado en spec base (`CARGA-SEGURA-01` escenario «Recarga pisos re-resueltos (759→594)»). Escenarios históricos con 759 en `LIMPIEZA-01`/`RESPALDO-01` se conservan como baseline general, con escenario nuevo pisos 594.
- **P2-4 README 356 vs 354 hash → 356 (354+2) documentado:** `data/raw` tiene **356 ficheros** en disco; `docs/raw_manifest_sha256.txt` lista **354** (`--verify` OK). Los 2 extra son `.FROZEN` y `.gitkeep` (meta-ficheros sin hash por diseño); `README.md:124,136` «356 (354 con hash)» es correcto y se explicita aquí: **356 = 354 + 2**. Manifest silver 187 aparte (185 vs 188 de T6 queda cerrado con 187 verificadas post --write).

## 4. Tareas y Success Criteria (P1-2)

`tasks.md` 27×`- [ ]` → 27×`- [x]` y `proposal.md:72-75` 4×`- [ ]` → 4×`- [x]`, solo con la evidencia §1-§2 (166 passed 1 skipped, doble SHA, 13 PNG/6 CSV, manifests 354+187, indicadores 594/204/L2 3/precio 62/252). Sin pendientes. Nota honesta: T3/T6 con valores reales (594, L1 204/126/50/39, L2 3, Nivel2 54/Nivel3 194, precio 62/252) que difieren del baseline del proposal/delta (173/113/40/39, L2 16, 66/182, 80/252); los ticks cubren la variante «reales con justificación» de tasks.md, y los deltas fueron sincronizados con los reales.

## 5. Sincronización delta → specs base (sin perder requisitos)

- `openspec/specs/extraccion-datos/spec.md` (+46): añadidos `EXTRACCION-01 — Ubicación real desde subtítulo/título (pisos)`, `PISOS-01`, `PISOS-02` (con conciliación 263/87/45; escenario «245 passed» corregido a `15 passed, 1 skipped`). `EXTRACCION-01` API+scraping, `EXTRACCION-02`, `FORMATO-01`, `COMPLEMENTARIOS-01`, `PYTHON-01`, `GATE-JOIN-01` intactos.
- `openspec/specs/mongodb-y-analisis/spec.md` (+43): escenario CARGA-SEGURA «759→594» + cadena gold, escenario LIMPIEZA orden base→enricher, nuevos `PISOS-03` (594/843, 62/252) y `PISOS-04` (252/252, 249/252, doble SHA). `MODELO-01`…`RENTA-01` intactos (759 histórico conservado en LIMPIEZA-01/RESPALDO-01).
- `openspec/specs/presentacion-de-resultados/spec.md` (+56/actualizado): `RESPUESTA-01` 173/113/40/39→**204/126/50/39** (advertencia 1→11 anuncios), nuevos `CONCLUSION-01` niveles L1/L2/L3 (L2=3) y `PISOS-05` (252 contextual/159). `DATOS-HETEROGENEOS-01`, `AUTOMATIZACION-ANALISIS-01`, `INDICADORES-01`, `PREPARACION-VISUALIZACION-01` y guion `CONCLUSION-01` original intactos.

## 6. Diff stat (tracked) y artefactos no tracked

```
19 files changed, 592 insertions(+), 111 deletions(-)
README.md, docs/conclusiones_municipios.md, docs/guion_defensa.md, docs/guion_defensa_12min.md, docs/metodologia.md,
extract/08_pisos_scraper.py, storage/load_mongo.py,
transform/aplicar_cobertura_mercado.py, transform/muni_resolve.py, transform/unificar_anuncios.py,
tests/test_fase_datos.py, tests/test_mongo.py, tests/test_mongo_consistencia.py, tests/test_mongo_geo.py,
tests/test_mongo_pymongo_pro.py, tests/test_raw_guardrails.py,
openspec/specs/extraccion-datos/spec.md, openspec/specs/mongodb-y-analisis/spec.md, openspec/specs/presentacion-de-resultados/spec.md
+ untracked: openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/ (proposal+tasks+3 deltas+verify-report), archive-report.md (este), tests/test_pisos_ubicacion_real.py, scratchpad/
```
Silver `data/procesado/*` está gitignored (`.gitignore:18`): regenerados existen en disco y Mongo pero no entran en el diff (analisis_variables_base, dim_municipios_enriquecido, dim_municipios_renta, dim_municipios_tension, manifest 187). Manifest raw `docs/raw_manifest_sha256.txt` (354) también regenerado vía `--write` sin cambios de conteo.

## 7. Restricciones cumplidas

Sin Docker (sin Dockerfile/compose, `git diff --name-only | grep -i docker` vacío), HDFS solo raw (`data/raw`, sin procesados subidos), Kafka→HDFS nunca Kafka→Mongo (topología intacta), sin commit ni push (`master...origin/master` sin ahead).
