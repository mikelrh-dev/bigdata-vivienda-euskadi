# Baseline v7 — 2026-11-09

| Hecho | Valor medido | Fuente |
|---|---|---|
| Rama | `master` | `evidencia/baseline.txt` |
| Commit | registrado en `evidencia/baseline.txt` | `git rev-parse HEAD` |
| Python | 3.12 (`.venv`) | `evidencia/baseline.txt` |
| Tests colectados | **238** (31 ficheros) | `pytest --collect-only -q` |
| Tests ejecutados | **238 colectados · 2 skipped · 0 failed · exit 0** → 236 passed | `evidencia/pytest.txt` |
| Skips | `test_pisos_ubicacion_real.py:202` (artefactos no versionados) y `:255` (`MONGO_ALLOW_DESTRUCTIVE!=1`) | `pytest -q -rs` |
| Gobernanza | **TODO OK** (46 requisitos, 45/34 scripts, 188 silver, 0 env, 11 pipelines) | `evidencia/gobernanza.txt` |
| Staleness | **exit 0** (34/34) | `evidencia/staleness.txt` |
| Gate offline | **OK** (354 raw, 188 silver, 14 colecciones, 0 duplicados, lag 0) | `evidencia/gate_offline.txt` |
| Fase de datos | **exit 1 / PENDIENTE** (FAIL 07 paro-cero conocido) | `evidencia/fase_datos.txt` |
| Mongo | **30 colecciones** = 16 vivas (14 loaders + 2 de habitaciones) + 14 `__backup` | `evidencia/mongo_snapshot.json` |
| `anuncios` | **594** (326 larga estancia + 268 temporal) | Mongo |
| Municipios | **252**; alquiler **252** (159 municipal + 93 comarcal); VPO **252** | Mongo |
| HDFS raw | **352 ficheros**, 6 directorios, 895.597.494 bytes | WebHDFS `GETCONTENTSUMMARY` |
| HDFS procesado | **404 Not Found** | WebHDFS |
| Kafka `vivienda_euskadi` | 1 partición, 1 réplica, offsets **0 → 352**, grupo `hdfs_centro` **committed 352**, lag 0 | `evidencia/kafka_offsets.json` |
| Funciones inventariadas | **814** (298 camino crítico, 280 tests, 236 estáticas) | `inventario_funciones.csv` |
| Artefactos | 17 CSV, 28 PNG + 8 anexo, 58 ficheros en `data/resultados` | `ls`/`find` |
| Escrituras en `data/` | **0** ficheros nuevos hoy | `find data/resultados -newermt` |

## Regla de cierre

- 814/814 funciones con fila en `inventario_funciones.csv`.
- 298 funciones del camino crítico revisadas con lectura profunda (nivel A).
- 280 funciones de test auditadas por aserción.
- 236 funciones de soporte clasificadas estáticamente (nivel B).
- No se re-ejecutó el productor Kafka ni `run_analisis_mongo.py` completo para no mutar topic ni `data/resultados`.
