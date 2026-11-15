# Cobertura de la auditoría v13

## 1. Criterio → evidencia → estado

| Criterio | Evidencia primaria | Comando/lectura | Estado |
|---|---|---|---|
| C1 | `extract/` 41 scripts, cliente común, `main_ingest` | inspección + gobernanza | Cubierto |
| C2 | 353 objetos HDFS (histórico), waiver procesado, `/data/procesado` 404 | evidencia v8/v11 + TCP | Cubierto, no revalidable hoy |
| C3 | productor + `kafka_hdfs_uploader` con `offset+1` | código + evidencia v8 | Cubierto, no revalidable hoy |
| C4 | gate E2E | lectura de `run_vivo/check_lag/check_duplicados` | Cubierto, hallazgo H-06 |
| C5 | 16 loaders, `$lookup` por `codigo_ine` | `load_mongo.py`, Mongo 594/594 | Cubierto |
| C6 | embedding/referencing | `modelo_mongodb.md`, esquema Mongo | Cubierto |
| C7 | 6 operaciones de limpieza | `clean_mongo.py` | Cubierto |
| C8 | `run_mongo_pipeline.py` | código + `--fase mongo` documentada | Cubierto |
| C9 | justificación embedding/referencing + 7 preguntas | `modelo_mongodb.md` | Cubierto |
| C10 | CRUD con contadores | `demo_crud_operations` + tests | Cubierto (H-12) |
| C11 | 30 consultas | `mongo_queries.py` (AST/def) | Cubierto (H-05) |
| C12 | 11 pipelines, 8 etapas | `mongo_aggregations.py` (regex) + gobernanza | Cubierto |
| C13 | índice + explain | `explain()` en vivo | Cubierto (solo «después») |
| C14 | atómica + justificación | código + test | Cubierto |
| C15 | 7 formatos | `extract/`, `transform/` | Cubierto |
| C16 | `run_analisis_mongo.py` | 11 pipelines, huella gold | Cubierto |
| C17 | 7 indicadores | CSV + `matriz_indicadores.md` | Cubierto (H-03) |
| C18 | 4 Tier A + comparativa | `ranking_esfuerzo.csv`, `comparativa_3_municipios_mongo.csv` | Cubierto |
| C19 | 24 CSV + 31 PNG | conteo en `data/resultados` | Cubierto |
| T1–T7 | ver `matriz_rubrica.md` | mixto | Cubierto (T6/T7 con objeción) |
| P-01…P-08 | ver `informe.md` §5 | mixto | Cubierto |
| Invariantes (sin Docker, HDFS solo raw, Kafka→HDFS, no imputar como municipal, Nivel/Tier) | grep + specs + código | Cubierto, salvo «Nivel/Tier ortogonal» que sigue sin aparecer en deck/guion |

## 2. Barrido invertido: artefacto → criterio

Compruebo también qué trabajo hecho **no** puntúa en ningún criterio, para que no quede invisible.

| Artefacto | ¿Puntúa? | Observación |
|---|---|---|
| `validacion_portales_2026.csv` | C17/C18 (apoyo) | Sensibilidad por portal; no es criterio propio |
| `sensibilidad_idw.csv` | C17 | Demuestra honestidad metodológica; no suma criterio |
| `bootstrap_robustos.csv` | T7 | Municiones de defensa, no criterio |
| `capa_contexto.csv` | C5/C17 | Contexto territorial |
| `mongo_vpo_terminadas_por_municipio.csv` | C17 | 251 de 252 filas: una sin dato |
| 8 PNG de `anexo/` | C19 (apoyo) | No cuentan en los 55 |
| `openspec/` completo | Transversal | Gobernanza, no rúbrica |
| `docs/memoria/` | Entregable 4 | Sí puntúa, vía C18/T7 |

Ningún artefacto relevante queda huérfano de criterio; los que no puntúan son apoyo declarado.

## 3. Fases ejecutadas

| Fase | Estado | Nota |
|---|---|---|
| F0 contrato literal | Ejecutada | PDF y DOCX extraídos con `pymupdf`/`python-docx`; 0 divergencias con `contrato-reto` |
| F1 coherencia numérica | Ejecutada | 40 cifras del ledger; 4 discrepancias (H-01, H-02, H-04, H-08) |
| F2 misconceptions | Ejecutada | 20 contrapruebas; 4 confirmadas, 5 refutadas |
| F3 errores de código | Ejecutada | 50 `except Exception`, 15 `pass`, 1 test sin assert, alias, fallback |
| F4 reproducibilidad | Ejecutada | pytest, gobernanza, gate, `--check`, deck verifier, Mongo |
| F5 fuentes externas | **No ejecutada** | Ver `gaps.md` G-02 |
| F6 matriz de rúbrica | Ejecutada | `matriz_rubrica.md` |
| F7 invariantes | Ejecutada | `informe.md` §5 |
| F8 defensa | Ejecutada | `preguntas_defensa.md` |
| F9 síntesis | Ejecutada | `informe.md` |
