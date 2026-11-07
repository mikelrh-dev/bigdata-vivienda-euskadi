# Archive Report: Habitaciones medianas (residencia vs habitaciones)

**Change:** `2026-11-07-habitaciones-medianas`
**Mode:** openspec
**Date:** 2026-11-08
**Verdict (verify):** GATE PASS — implementación (con 4× P1 literales reconciliados en archive: P1-1 n/n_precio, P1-2 62/60, P1-3 PNG 12/13, P1-4 raw 2 diffs). GATE FAIL literal palabra-por-palabra queda subsanado por corrección en base sincronizada (ver §Notas). Sin CRITICAL de código.

## Final state (at close)

- **pytest:** `177 passed, 1 skipped` (skip `tests/test_pisos_ubicacion_real.py:245: skip separado: MONGO_ALLOW_DESTRUCTIVE!=1`). Re-ejecutado en archive: `177 passed, 1 skipped in 7.39s`. Coincide con esperado `tasks.md` §4.
- **Doble `run_analisis_mongo.py`:** SHA256 doble idéntico `mongo_habitaciones_por_municipio.csv` = `35bcd8699c67bff4ae9b9ab0d6601f7d27e47f78099861b6db2b26a7866e5696` (400 bytes, verificado en archive); huella interna 11 pipelines `0f15c729901693ba5cc925d5241140c2bb83251ff0763b813f30865dcff76daa` con `reproducibilidad: ok`. Tier SHA `b8411b77fdfa8df60b06618883dc05ee6bd04699b319b3dbb6b28ee9a8103015`; esfuerzo SHA `7f813fd61ee6800dacd24a230aaef43a8d97e9dbe1abd0300fa1da5b974f75a3`; alquiler SHA `ff39e852d27a754eabb2fe3db76c71c1ac35e8a0cdcd4e799ff9fb7c9798263e`.
- **`mongo_habitaciones_por_municipio.csv`:** 9 filas, `n`=201 / `n_precio`=200 (no 201). Bilbao 96/96 400/3400/600; Donostia 66/66 470/7700/1200; Vitoria 12/12 240/109000/400; Barakaldo 11/11 350/2000/500; Getxo 8/8 400/2700/700; Irun 3/3 400/500/450; Errenteria 2/2 385/2500/2500; Durango `n`=2/`n_precio`=1 1650/1650/1650; Eibar 1/1 390/390/390. Durango: anuncio 187607209 con `precio_eur` vacío (None) no imputado.
- **Pipeline:** `pipeline_habitaciones_por_municipio` pública en `analysis/mongo_aggregations.py` (`$group` por `codigo_ine`, mediana cruda, sin winsorizar ni imputar). `PIPELINE_ORDER`: 11 pipelines, tier (10) + habitaciones (11), los 10 previos sin reordenar.
- **Gráfico:** `chart_habitaciones_medianas.svg` 4ª `chart_*` (11 SVG), 3 series nunca agregadas, `n_precio` + min–max, `firme solo Bilbao (96) y Donostia (66) n≥30 · resto indicativo, sin ranking`. `index.template.html` con `<img src="assets/chart_habitaciones_medianas.svg" alt="Comparación residencia vs habitaciones por municipio">` (slide 9/15). PDF regenerado (P2-2).
- **Tier intacto:** 252 filas A4/B3/C57/D188, `n_anuncios` 594, `n_precio` 439, 7 filas `n_precio>0`. Precio reconciliado: observable 62/252 pre-M1; 60/252 tras filtro M1/winsorización (P1-2).
- **Tasks:** 19/19 checked, 0 sin marcar en `tasks.md` (Task Completion Gate PASS vía reconciliación excepcional — ver §Gates).
- **Restricciones:** sin Docker (sin `Dockerfile`/`docker-compose` nuevos); HDFS solo raw (352 documentales, sin live — P2-5); Kafka→HDFS, nunca Kafka→Mongo (sin conector nuevo). Sin commit/push.
- **Review:** `reviewGate` ausente → archive procede bajo política ordinaria del repo.

## Specs synced (base = source of truth)

| Domain | Action | Details |
|--------|--------|---------|
| mongodb-y-analisis | Updated | ADDED HAB-01 (pipeline nº 11 + CSV 9 filas + 4 escenarios). Corregidos: `n`=201/`n_precio`=200, Durango `n`=2/`n_precio`=1; Tier con `62/252 (60/252 tras M1)`. Preservados 17 requisitos previos (MODELO-01 … CAPAS-01). |
| presentacion-de-resultados | Updated | ADDED `chart_habitaciones_medianas` (3 series + firme/indicativo + 3 escenarios), tras DOCS-01 y antes del mapa §13–§14. Corregido: resto en `n_precio` (Durango 1, `n`=2). Preservados CONCLUSION-01/02, BOOTSTRAP-01, DOCS-01 y mapa §13–§14. |

Requisitos exigidos presentes en base: HAB-01, `chart_habitaciones_medianas`. Ningún requisito fuera del delta se eliminó ni modificó.

## Gates finales

- Task Completion Gate: PASS (19/19 ticks, 0 `- [ ]`). Reconciliación excepcional con prueba: `verify-report.md` GATE (1)–(4) + re-verificación archive (`pytest 177/1`, SHA `35bcd869…`, Tier 252 A4/B3/C57/D188, `PIPELINE_ORDER` 11, SVG + `<img>`). Motivo: `sdd-apply` no marcó ticks; el orquestador ordenó reconciliar solo con evidencia del gate — cumplido (ningún tick sin evidencia). P1 reconciliada: §1.5 + §2.3 (201→200), §3.4 (Durango 2→1), §4.4 (62→60). §3.6 PDF por evidencia indirecta (P2-2).
- Native Review Receipt Gate: `reviewGate` ausente → PASS (sin receipt que leer/bloquear).
- Mechanical Copy Contract: move vía shell `git mv` (fallback `mv`) con snapshot `cp -R` + readback `diff -r`. Salida verbatim: vacía (sin diferencias). `DIFF-EMPTY:PASS`. Source `openspec/changes/2026-11-07-habitaciones-medianas` desaparecido tras el move; destino `openspec/changes/archive/2026-11-07-habitaciones-medianas/` (sin doble fecha, convención del repo). Nota: `git mv` falló con `fatal: source directory is empty` (carpeta untracked); fallback `mv` aplicado, diff vacío confirma identidad byte-a-byte.
- Verify GATE PASS reconciliado: `pytest 177/1` + SHA `35bcd869…` + huella `0f15c729…` + Tier 252 SHA `b8411b77…`. P1 eran de texto, no de código (P1-3/P1-4 pre-existentes ajenos — ver §Notas).

## Notas (jerarquía Final-State Authority)

- **P1-1 (n_precio 201 vs 200) — RECONCILIADO.** Delta decía `suma n_precio = 201` con Durango 2. Real: `n`=201, `n_precio`=200, Durango `n`=2/`n_precio`=1 (anuncio None no imputado). Corrección en base: `Nueve filas con suma n=201 / n_precio=200`. El delta archivado conserva el texto original (auditoría); el source-of-truth corregido es `openspec/specs/`.
- **P1-2 (62/252 vs 60/252) — RECONCILIADO.** `62/252` es precio observable pre-M1; tras filtro M1/IQR + winsorización, `mongo_esfuerzo_por_municipio.csv` expone 60/252 (64→60; 4 municipios con anuncios quedan con `n_anuncios_filtrados`=0). Base HAB-01 lo concilia como `62/252 (60/252 tras M1)`. Tier intacto a hash/distribución.
- **P1-3 (PNG 12 vs 13) — pre-existente, NO tocado.** `run_analisis_mongo.py` emite 13 (g1 duplicado de A1); test/README exigen 12 únicos. Archivo g1 a mano tras cada regeneración (canónico 12). Pendiente fuera de habitaciones.
- **P1-4 (raw 2 diffs vs HEAD) — pre-existente, NO tocado.** 2 hashes `lanbide_*` por `extract/21_lanbide_historico_paro_joven.py` (apilado ajeno). Integridad raw verde (manifiesto 354 = disco 354). Habitaciones no toca `data/raw`.
- **P2 residuales (no bloqueantes):** P2-1 SVG no byte-determinista (`dc:date`; CSV sí byte-exacto) · P2-2 PDF sin verificación textual (evidencia indirecta: `5,05→7,68 MB`, `/Image 231→279`) · P2-3 mediana alta en n par (Errenteria 385/2500 → 2500) no declarada · P2-4 outlier crudo Vitoria max 109000 (spec exige crudo) · P2-5 HDFS 352 solo documental, sin live · P2-6 árbol apilado vs HEAD (9→11 pipelines, `data/resultados/*` ignorado) · P2-7 etiqueta `n` del gráfico usa `n_precio` (Durango `n=1`) vs `n`=2 de tasks.
- `verify-report.md` es snapshot intermedio (GATE PASS con P1). Los números finales de este report salen del gate + re-verificación archive. Trazabilidad: `verify-report.md` GATE (1)–(4) + recomprobación local archive OK.

> Las contradicciones de snapshot intermedio no se resuelven retroeditando la spec. Directiva archive.

## Diff stat (base specs)

```
 openspec/specs/mongodb-y-analisis/spec.md         | 180 +++++++++++++++++++-
 openspec/specs/presentacion-de-resultados/spec.md | 190 +++++++++++++++++++++-
 2 files changed, 354 insertions(+), 16 deletions(-)
```

Incluye syncs apilados no commiteados vs HEAD (M1/AGREGACION-01, RAW-01, pisos, Tier/burbuja/mapa). Aporte propio habitaciones: mongodb +32 líneas (HAB-01, 499→531), presentacion +27 líneas (chart, 437→464). Carpeta del change: untracked (`??`), movida con `mv` + `diff -r` vacío.

## Verificación archive (confirmada)

- [x] Main specs updated correctamente (HAB-01 + chart_habitaciones_medianas con P1 corregida; ningún otro requisito tocado)
- [x] Change folder movido a archive (`openspec/changes/archive/2026-11-07-habitaciones-medianas/`)
- [x] Archive contiene proposal.md, specs/ (2 deltas), tasks.md, verify-report.md, archive-report.md (aditivo)
- [x] Archived `tasks.md` sin unchecked: 19/19 `- [x]`
- [x] Active changes ya no contiene habitaciones
- [x] `diff -r` verbatim vacío (ver Gates) — única evidencia que pasa

## Archive contents

- proposal.md ✅
- specs/ (mongodb-y-analisis, presentacion-de-resultados) ✅
- tasks.md ✅ (19/19)
- verify-report.md ✅ (GATE PASS con P1)
- archive-report.md ✅ (este fichero, aditivo)
