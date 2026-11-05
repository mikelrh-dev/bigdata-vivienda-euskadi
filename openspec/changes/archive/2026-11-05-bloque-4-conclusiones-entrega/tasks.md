# Tasks: bloque-4-conclusiones-entrega

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 150-300 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single change (docs + 1 pipeline) |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|----|----------------------|-----------------|-------------------|
| 1 | Indicadores 5 pipeline/silver + huella CSV | PR 1 | `pytest tests/test_mongo_pipeline.py tests/test_contrato.py -q` | `python analysis/run_analisis_mongo.py` | Revertir `analysis/mongo_aggregations.py` y CSV |
| 2 | Respuesta 4 robustos + matriz O1-O4 | PR 1 | `pytest tests/test_mongo_comparativa.py -q` | Lectura `docs/conclusiones_municipios.md` | Revertir docs y comparativa CSV |
| 3 | Guion Tema 8 + trazabilidad VM | PR 1 | `pytest tests/test_contrato.py tests/test_raw_guardrails.py -q` | Conteo páginas guion | Revertir `docs/guion_defensa.md` y trazabilidad |

## Phase 1: Indicadores 5 — pipeline Mongo verdadero o silver justificado (PLAN_10 16)

- [ ] 1.1 Auditar fuente Lanbide/Etxebide en Mongo prod (solo lectura, conteo antes/después) y decidir pipeline verdadero vs silver justificado en `analysis/mongo_aggregations.py`. Check: `python -c "import pymongo;print(pymongo.MongoClient().vivienda_euskadi.list_collection_names())"`.
- [ ] 1.2 Implementar `pipeline_indicadores_municipio` (tensión social y paro Lanbide) en `analysis/mongo_aggregations.py`, o documentar silver justificado sin inventar valores. Check: `grep -n "pipeline_indicadores_municipio\|silver" analysis/mongo_aggregations.py`.
- [ ] 1.3 Preservar `metodo_imputacion` en toda salida y todo `fillna` mediana con flag `is_imputed` en `analysis/mongo_aggregations.py` y `analysis/run_analisis_mongo.py`. Check: `grep -rn "fillna" analysis/ | grep -v is_imputed` devuelve vacío.
- [ ] 1.4 Regenerar CSV canónicos con huella 253/253/3 automáticos en `data/resultados/` y anotar hash en `docs/matriz_indicadores.md`. Check: `wc -l data/resultados/mongo_esfuerzo_por_municipio.csv data/resultados/mongo_alquiler_por_municipio.csv data/resultados/mongo_modalidades.csv`.

## Phase 2: Respuesta 4 robustos y matriz O1-O4 (PLAN_10 17)

- [ ] 2.1 Extender `data/resultados/comparativa_3_municipios_mongo.csv` a 4 filas (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, `codigo_ine` 5 dígitos) con paro no nulo o silver justificado. Check: `wc -l data/resultados/comparativa_3_municipios_mongo.csv` = 5.
- [ ] 2.2 Redactar matriz O1-O4 en `docs/conclusiones_municipios.md` (mediana 26,61 oficial 18-34, 25,2% sobre 30) con advertencia Getxo 40 vs Vitoria-Gasteiz 39 (1 anuncio, no ranking firme). Check: `grep -n "26,61\|25,2%\|Getxo 40 vs Vitoria" docs/conclusiones_municipios.md`.
- [ ] 2.3 Registrar la comparativa en `docs/trazabilidad_vm.md` (Fecha/Objetivo/Máquina/Comando/Salida/Conclusión), solo lectura HDFS centro y Mongo prod. Check: `grep -n "Bilbao 173\|Donostia 113" docs/trazabilidad_vm.md`.

## Phase 3: Guion Tema 8 y trazabilidad (PLAN_10 18)

- [ ] 3.1 Reescribir guion Tema 8 de 1 página en `docs/guion_defensa.md` (embedding, índices, atomicidad, HDFS centro + Kafka pid 1832, 10 criterios, lagunas). Check: `wc -l docs/guion_defensa.md` y `grep -c "embedding\|índices\|atomicidad" docs/guion_defensa.md`.
- [ ] 3.2 Marcar 16-29 legacy y 18-34 canónico en `docs/guion_defensa.md`, `docs/conclusiones_municipios.md` y `docs/matriz_indicadores.md`; ninguna conclusión usa 16-29 como canónico. Check: `grep -rn "16-29" docs/guion_defensa.md docs/conclusiones_municipios.md docs/matriz_indicadores.md`.
- [ ] 3.3 Re-verificar Kafka pid 1832 en VM (`LISTEN` 9093/9094) y anotar en `docs/trazabilidad_vm.md`. Check: `grep -n "pid 1832\|9093" docs/trazabilidad_vm.md`.

## Phase 4: Gate Bloque 4

- [ ] 4.1 Ejecutar suite completa y guardrails (sin `data/raw`, sin carpeta nueva, procesado sin subir, prod intacta). Check: `pytest tests -q` (130 passed) y `git status --short`.
