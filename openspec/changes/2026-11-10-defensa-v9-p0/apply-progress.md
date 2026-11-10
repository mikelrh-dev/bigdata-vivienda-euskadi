# Apply progress — 2026-11-10-defensa-v9-p0

Estado: **COMPLETADO** (19/19 tareas). Sin push; commits locales separados.

## Historial

- Inicio (subagente `deleg_94df6e12`): 2026-11-10 11:01:31
- Interrupción por error de API: 12:13:54 (~72 min, 75 api_calls)
- Reanudación y cierre manual: 2026-11-10 (sesión posterior)

El subagente dejó 15/19 tareas y el working tree con 36 ficheros modificados. La reanudación completó 6.1-6.4, re-verificó todo y separó los commits.

## Tareas completadas (19/19)

| Fase | Tareas | Estado |
|---|---|---|
| 1. Índices | 1.1-1.2 | `anuncios` con `_id_` + 4 índices (ESR, geo, portal_id, equipamiento); 24 índices en 16 vivas |
| 2. Explain read-only | 2.1-2.3 | `hint:{"$natural":1}`; COLLSCAN 594 → IXSCAN 1 (`docs=1`, `keys=1`, filtro `20069`); `main()` read-only |
| 3. Aislamiento tests | 3.1-3.4 | `test_mongo_geo` carga en `vivienda_euskadi_test`; `skipif(not ping())`; suite verde |
| 4. Guion y atribución | 4.1-4.3 | IXSCAN con filtro `20069`, referencing por `codigo_ine`, 24 índices; mutador `test_mongo_geo.py` |
| 5. Barrido documental | 5.1-5.3 | 594 / 16+14 / 11 / 8 / 204-126-50-39 / 235+2 / 28+8 PNG; geo 2dsphere, multikey y parcial |
| 6. Manifiestos, gate y flags | 6.1-6.4 | Ver abajo |

### Fase 6 (cerrada en la reanudación)

- **6.1** `ingestion_manifest.json` regenerado (354 ficheros). Verificado: los 5 `lanbide_paro_*` coinciden con `docs/raw_manifest_sha256.txt`.
- **6.2** `ingestion_manifest.json` ya está en `EXCLUIDOS` de `extract/generar_manifest.py`; `manifest_sha256.txt` conserva 188 entradas y 0 menciones. Sin edición necesaria.
- **6.3** `scripts/verificar_gobernanza.py`: cuenta 50 cabeceras `### Requirement:` (46 con ID canónico + 4 `chart_*`) y escanea `os.environ.get(...)`. `GATE_LIVE` y `RAW_GUARD_AUDIT_LOG` declaradas en `.env.example`. Gate: **TODO OK**.
- **6.4** HM-03: **no se ejecuta `clean_all()`**; se documenta como limitación (D8). Los pipelines de análisis no dependen de los flags y la única escritura destructiva pendiente queda fuera del cambio.

## Verificación ejecutada (2026-11-10)

| Comando | Resultado |
|---|---|
| `scripts/verificar_gobernanza.py` | **exit 0**, TODO OK: 50 cabeceras / 46 con ID / 42 scripts / 34 DAG / 188 silver / 0 env sin declarar / 11 pipelines |
| `pytest tests -q` | **exit 0**, 235 passed + 2 skipped (237 collected), sin `-k`/`--deselect` |
| `list_indexes()` + recuentos antes/después de la suite | **idénticos** (594 docs, 30 colecciones, 4 índices de negocio en `anuncios`) |
| `transform/run_all.py --check` | **exit 0** (34/34) |
| `scripts/gate_extremo_a_extremo.py --offline` | **exit 0** (354 SHA + 188 silver + 14 colecciones + 0 duplicados + lag 0; `PENDA-01` por HDFS/Kafka no alcanzables hoy) |
| `scripts/verificar_fase_datos.py` | **exit 1** solo por FAIL 07 conocido (paro-cero Aramaio/Gaintza/Usansolo), documentado sin enmascarar |
| `explain_before_after()` | before **COLLSCAN** 594 docs / after **IXSCAN** 1 doc (`nReturned=1`) |
| Artefactos | 8 CSV `mongo_*` + 28 PNG + 8 PNG de anexo |

## Commits (locales, sin atribución de agente)

1. `fac5223` — `chore: retira legacy DuckDB y alinea el gate a 42 scripts` (limpieza v9).
2. `be3ffe4` — `feat: valida el CSV VPO en memoria sin staging` (cambio `2026-11-09-vpo-sin-staging`).
3. Commit de este cambio (`defensa-v9-p0`): índices/explain read-only, tests aislados, barrido documental, manifiestos/gate y reauditoría v9.

## Limitaciones conocidas (no bloqueantes)

- **HDFS/Kafka centro no alcanzables** hoy (el usuario no está en el centro). Evidencia usada: histórico v8; el gate offline lo declara `PENDA-01`. No es un fallo del proyecto.
- **R-4**: al aislar `test_mongo_geo.py` se pierde la aserción sobre el geo real de prod (424/594). El dato sigue verificado por sonda read-only y documentado en la reauditoría.
- **C-1**: el escenario literal de `INDICES-01` en el spec principal aún describe «índice eliminado»; el delta de este cambio lo sustituye por el hint read-only, y la sincronización al spec principal ocurre en la fase archive.
- **HM-03**: flags de calidad sin `clean_all()`; documentado.
- **HM-06 / DS2-25**: duplicación de `anuncios_habitaciones_unificados` y huella de 11 pipelines sin registrar; fuera de alcance (P2).
