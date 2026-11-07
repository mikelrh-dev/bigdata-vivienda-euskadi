# Proposal: Datos P0/P1 — outliers, staleness, paro y capas

## Intent

- M1: `precio_m2` 0.16–83.33 y `habitaciones` float contaminan indicadores; 17 IQR sin excluir.
- M2: 62/252 con precio vs `n_precio=7` no reconciliado tras suprimir C/D.
- M3: ranking esfuerzo sin filtro `n>=30` (Barakaldo `n=6` sobre Donostia `n=126`).
- M4: stale 759→594 en docs/presentación; M5: paro 249→252; M6: sin dedup; M7: capas invisibles.

## Scope

### In Scope

- M1: filtrar `precio_m2` 3–50 y superficie 10–500; excluir IQR; `habitaciones` int.
- M2: reconciliar 62/252 vs `n_precio=7`; publicar solo A+B (C/D suprimidas).
- M3: bloquear top-10/ranking esfuerzo con `n<30`.
- M4: 759→594 en `docs/datos_finales_conclusiones_2026-11-05.md`, `docs/informe_final.md`, `data/resultados/README.md`, `presentacion/index.html`.
- M5: paro 249→252 (01003/20037/48916) vía extract 18/21 + `corregir_empleo`.
- M6: dedup dura por `property_fingerprint` + test.
- M7: capas visibles — 159 oficial (titular), 93 IDW (sensibilidad), 252 contexto (`completar_alquiler_comarca` + `load_mongo` + `run_analisis` mapa).

### Out of Scope

- Sin Docker; HDFS solo raw (`hdfs_utils.py` 0 changes); Kafka→HDFS, no Kafka→Mongo.
- Sin imputar comarcal/IDW como municipal; sin tocar `data/raw`.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `extraccion-datos` (M1/M5/M6): tipos/outliers, paro 252, dedup fingerprint.
- `mongodb-y-analisis` (M1/M5/M7): exclusión outliers en agregaciones, paro 252, capas 159/93/252.
- `presentacion-de-resultados` (M2/M3/M4): A+B 62/252, ranking `n>=30`, cifras 594.

## Approach

1. `filtrar_outliers`/`generar_anuncios_residencial_filtrado`: rangos 3–50/10–500, exclusión IQR, cast int.
2. `unificar_anuncios` → dedup fingerprint → `load_mongo` (staging+backup) → `run_analisis` regenera resultados.
3. A+B solo; ranking exige `n>=30`; capas 159/93/252 etiquetadas.
4. Corregir 01003/20037/48916 (extract 18/21 + `corregir_empleo`); sincronizar los 4 documentos M4.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `transform/filtrar_outliers.py`, `generar_anuncios_residencial_filtrado.py` | Modified | M1 rangos/exclusión/cast |
| `transform/unificar_anuncios.py`, `generar_fingerprint.py` | Modified | M6 dedup dura |
| `extract/*18*`, `*21*`, `transform/corregir_empleo*` | Modified | M5 paro 252 |
| `transform/completar_alquiler_comarca.py`, `storage/load_mongo.py`, `analysis/run_analisis*` | Modified | M7 capas visibles |
| 4 docs M4 + resultados/mapa | Modified | 759→594, A+B, `n>=30` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| M1 reduce cobertura útil | Med | Excluidos contados por motivo; umbrales en config |
| 62/252 contradice cifras previas | Med | Tabla conciliación 62 vs `n_precio=7` en README |
| Bloqueo ranking rompe demo | Low | "n insuficiente" en vez de ocultar municipio |

## Rollback Plan

- Mongo: rename desde `__backup`; `git checkout --` transform/docs; `data/raw` intacto.

## Dependencies

- `.venv`; MongoDB local; `dim_municipios.csv` (252).

## Success Criteria

- [ ] Agregaciones sin `precio_m2` fuera de 3–50 ni superficie 10–500; `habitaciones` entero.
- [ ] 62/252 reconciliado; ranking sin `n<30`; 594 en los 4 documentos.
- [ ] Paro 252/252; 0 duplicados fingerprint; capas 159/93/252 etiquetadas.
- [ ] `pytest tests -q` en verde, sin regresión en conteo previo.
