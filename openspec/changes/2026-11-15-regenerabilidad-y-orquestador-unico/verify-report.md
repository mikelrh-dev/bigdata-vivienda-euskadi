# Verify report: regenerabilidad y orquestador único

**Fecha:** 2026-11-15 · **Rama:** `fix/regeneracion-procesado-resultados`
**Entorno:** Windows, `.venv` Python 3.12, Mongo local. HDFS y Kafka **no accesibles** (red del centro).

## Cambios

| Fichero | Cambio |
|---|---|
| `storage/load_mongo.py` | `load_habitaciones()` + las dos colecciones en `load_all()` (15 → 17) |
| `analysis/run_analisis_mongo.py` | guarda de vacío en `exportar_habitaciones_csv`; `main` devuelve 1 si falla esa exportación; flag `--sin-sync-deck` |
| `scripts/run_pipeline.py` | `--fase full` = silver, quality, mongo, gold; `--dry-run` previsualiza sin el flag destructivo |
| `scripts/verificar_reproducibilidad.py` | nuevo: raw, DAG, colecciones y gold |
| `docs/baseline_gold_sha256.json` | nuevo: huella y SHA de los 8 CSV canónicos |
| `tests/test_mongo_consistencia.py` | 15 → 17 colecciones; loader con `*args` |
| `tests/test_verificar_reproducibilidad.py` | nuevo: 5 tests |
| `scripts/gate_extremo_a_extremo.py` | `EXPECTED_COLLECTIONS` 15 → 17 y el check deja de imprimir el número fijo |
| `tests/test_extremo_a_extremo.py` | umbral de colecciones 15 → 17 |
| `README.md` | tests 298/300, `--fase full`, fila de `verificar_reproducibilidad.py`, gate con 17 |
| `openspec/project.md` | 300 tests colectados (298 passed, 2 skipped) |

## Evidencia

```
scripts/verificar_reproducibilidad.py
  [OK] raw          355 SHA de raw OK
  [OK] DAG          40 scripts, 119 datos de silver y 119 salidas con productor
  [OK] colecciones  17 colecciones vivas, todas con loader
  [OK] gold         huella 983fa53fb5c6… identica en dos pasadas y 8 CSV iguales a baseline y gold
  RESULTADO: OK  (rc 0)
```

```
run_pipeline.py --fase full --dry-run   -> rc 0, lista las 4 fases y marca mongo (DESTRUCTIVA)
run_pipeline.py --fase full             -> rc 2, exige --allow-mongo-write
run_pipeline.py --check                 -> rc 0 (355 raw, 183 silver)
gate_extremo_a_extremo.py --offline     -> OK (355, 183, 17 colecciones, 0 dup, lag 0)
verificar_gobernanza.py                 -> TODO OK (53/49, 47/40, 183, 11)
pytest tests                            -> 298 passed, 2 skipped
git status                              -> solo los ficheros del change (sin PNG del deck tocados)
```

La huella `983fa53fb5c61f37f526f4f27a9ffbc408a633c17c3a0cdf9d17771b00668b9e` coincide con la
registrada en la auditoría v12, así que el baseline no introduce un valor nuevo: fija el existente.

## Criterios de éxito

- [x] `load_all()` devuelve 17 colecciones y coincide con las vivas del Mongo local.
- [x] `exportar_habitaciones_csv` falla si el pipeline nº 11 devuelve 0 filas.
- [x] `--fase full` lista silver, quality, mongo y gold en orden.
- [x] `verificar_reproducibilidad.py` sale 0 con huella `983fa53f…` y 2 sin Mongo.
- [x] Suite en verde: 298 passed, 2 skipped.

## Desviaciones

- **`--dry-run` con fase destructiva**: antes exigía `--allow-mongo-write` incluso para listar el
  plan. Ahora el plan se previsualiza sin el flag porque no escribe nada; ejecutar sí lo exige.
  Afecta también a `--fase mongo --dry-run`, que gana la misma comodidad.
- **`--sin-sync-deck`**: las dos pasadas del verificador escribían en `docs/presentacion_v2/assets`
  porque el análisis sincroniza el deck por defecto. Se añade el flag y el verificador lo usa, para
  que la comprobación no deje efectos en el repo (se restauraron los tres PNG afectados).
- **`_bigdata`**: se recarga idéntica a la principal en vez de eliminarla. `_hab_col()` la prefiere
  si tiene documentos, así que mantener ambas reproduce el estado verificado. Unificarlas sigue
  siendo deuda (P3-19).

## Pendiente (fuera de este change)

- Gate `--vivo` real, fallback `noredirect` y verificación HDFS/Kafka: el lunes, en la red del centro.
- `auditoria_lagunas_silver.csv` sigue sin materializar (`run_all --check` rc 1, conocido).
- No se ha ejecutado la fase `mongo` ni se ha tocado dato alguno.
