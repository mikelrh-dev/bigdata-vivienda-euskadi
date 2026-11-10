# Matriz de rúbrica v8 — 19 criterios

**Nota global: 187 / 190 (98,4 %).**  
BDA RA1: 37/40 · SBD RA1: 40/40 · SBD RA3: 60/60 · SBD RA4: 50/50.

La reauditoría v8 no añade criterios: revalida los 19 con evidencia viva. La deriva documental (H-02…H-09) no baja la nota; C2 sigue en 7 por HDFS procesado.

| # | Criterio | Nota | Evidencia v8 | Falsador |
|---|---|---:|---|---|
| 1 | BDA · Extracción Python (API **y** scraping) | **10** | 41 scripts en `extract/`; APIs `01_eustat_api.py`, `06_ine_api.py`, `19_udalmap...`, `25_udalmap_extendido.py`; scrapers `05_fotocasa_scraper.py`, `08_pisos_scraper.py`, `13_scraping_habitaciones.py`; `main_ingest.py` orquesta | Que un extractor clave exija intervención manual |
| 2 | BDA · HDFS (originales **y** procesados + recuperación) | **7** | HDFS raw: `fileCount=352`, `directoryCount=6`; `OPEN` del VPO 35.427 B y SHA idéntico; `procesado` → **404**; excepción declarada | Que `procesado` exista y se recupere, o que el waiver no esté escrito |
| 3 | BDA · Kafka (productor y consumidor procesan) | **10** | Topic `vivienda_euskadi`: 1 partición; `begin=0`, `end=352`; grupo `hdfs_centro` `committed=352`; lag 0; productor/consumidor en `storage/` | Que el offset comprometido no avance o que solo haya mocks |
| 4 | BDA · Integración (flujo completo hasta MongoDB) | **10** | `gate_extremo_a_extremo.py --offline` OK; `run_mongo_pipeline.py --dry-run` OK; 11/11 pipelines; cadena `extract → transform → load_mongo → Mongo → analysis` | Que el flujo a Mongo dependa de un paso manual |
| 5 | SBD RA1 · Integración de fuentes (2+ y campo común) | **10** | `load_all()` carga 14 colecciones de negocio + 2 de habitaciones; `$lookup` `anuncios → municipios` por `ubicacion.codigo_ine`: 594/594 con match | Que los `codigo_ine` no casen |
| 6 | SBD RA1 · Construcción (2+ colecciones + relación/embedding/referencia) | **10** | `municipios` con `demografia`, `empleo`, `demanda_social`; `anuncios.ubicacion` anidado, `equipamiento[]`, `historico_precios[]`; referencias por `codigo_ine` | Que el anidamiento no se use en consultas |
| 7 | SBD RA1 · Limpieza PyMongo (4+ ops con nulos, duplicados y tipos) | **10** | `clean_mongo.py`: `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`, `convert_types`; tests con asserts y no-op | Que una operación sea alias de otra |
| 8 | SBD RA1 · Automatización (carga+limpieza+transformación) | **10** | `scripts/run_mongo_pipeline.py`: `load_all → clean_all → ensure_indexes → pipeline_indicadores`; `--dry-run` OK | Que falte un paso o haya edición manual |
| 9 | SBD RA3 · Modelado (+ embedding/referencing explicado) | **10** | `docs/modelo_mongodb.md`: embed en `municipios` y `anuncios`; referencia por `codigo_ine`; tipos BSON (`Decimal128`, arrays, GeoJSON). Las cifras del documento están desfasadas (H-02), pero el esquema y la justificación son correctos | Que la justificación no corresponda al esquema |
| 10 | SBD RA3 · CRUD (4 ops + comprobación en código) | **10** | `clean_mongo.py:311 demo_crud_operations`; `test_mongo.py:214 test_crud_demo` asserta `inserted_id`, 2 ids, count 3, update 1/1, `find_one_and_update="ok"`, upsert 0, bulk delete 1, delete_one 1, delete_many 2, remaining 1 | Que el test solo compruebe que no lanza |
| 11 | SBD RA3 · Consultas (5 útiles, anidada/array y 2+ condiciones) | **10** | `mongo_queries.py` 30 funciones; ejecutadas igualdad, dot notation, `$elemMatch`, `$and`, proyección y sort | Que las 5 sean variantes de igualdad |
| 12 | SBD RA3 · Aggregation (3+ pipelines, 5 etapas, `$group` + `$lookup`/`$unwind`/`$facet`) | **10** | **11/11 pipelines** ejecutan; `$lookup`, `$unwind`, `$group`, `$match`, `$addFields`, `$project`, `$sort`, `$limit`; `$facet` no usado (no obligatorio) | Que `$lookup/$unwind` sean decorativos |
| 13 | SBD RA3 · Índices (`explain` antes/después, `COLLSCAN`/`IXSCAN`, `totalDocsExamined`) | **10** | Índice ESR presente; `explain` de Bilbao: `IXSCAN`, nReturned 68, `totalDocsExamined=68`, keys 68. La cifra `IXSCAN 1` de algunos docs es de otro filtro (H-03); el criterio se cumple | Que los números estén hardcodeados o que el índice no se use |
| 14 | SBD RA3 · Consistencia (atómica + justificación o transacción) | **10** | `storage/mongo.py:170 marcar_calidad_municipio` con `find_one_and_update` + `ReturnDocument.AFTER`; `test_mongo_consistencia.py:49` asserta valor nuevo y no creación; transacción rechazada en standalone (`setName=None`) | Que el test no compruebe el valor nuevo |
| 15 | SBD RA4 · Datos heterogéneos (estructuras distintas adaptadas) | **10** | 41 extractores sobre CSV/JSON/HTML/XLSX/ZIP/SHP/GTFS; `unificar_anuncios.py` (3 portales), `normalizar_json_crudos.py`, `load_mongo.py:70 _geo_point` | Que cada fuente se cargue sin normalización común |
| 16 | SBD RA4 · Automatización del análisis | **10** | `run_analisis_mongo.py`: 11 pipelines, doble ejecución con huella, 8 CSV + PNG; 11/11 en lectura. El argparse dice “9 + 5” (H-11), pero la ejecución es 11 + 8 | Que algún análisis principal se haga a mano |
| 17 | SBD RA4 · Indicadores (5+, 2+ fuentes) | **10** | `docs/matriz_indicadores.md`: esfuerzo 18–34, tensión social, paro Lanbide, precio m2, VPO terminadas; `$lookup` a `anuncios`, `alquiler_municipal`, `municipios`, `udalmap_*`, `osrm_tiempos`, `etxebide_*` | Que dos indicadores sean el mismo con otro nombre |
| 18 | SBD RA4 · Respuesta al reto (3+ municipios, conclusión ↔ indicador) | **10** | `comparativa_3_municipios_mongo.csv`: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39; `docs/conclusiones_municipios.md` da una frase por municipio con esfuerzo, precio, cuantía y paro | Que las conclusiones no citen indicador |
| 19 | SBD RA4 · Preparación visualización (3+ conjuntos automáticos) | **10** | `EXPORTS_8`: 8 CSV `mongo_*`; 28 PNG + 8 anexo; `exportar_png_desde_mongo`; el índice `docs/README.md` aún dice 4 CSV (H-06) | Que los CSV estén tecleados o los PNG no vengan de Mongo |

## Lectura

- **C2 (HDFS)** es el único criterio que no llega a 10 literal: hay originales, recuperación y SHA, pero no `procesado`; se sostiene por la excepción declarada, no por una suposición.
- **C13 (índices)** se cumple con la medición viva 68/68. El “1” de los documentos es una cifra de otro filtro más estrecho, no una prueba de que el índice no funcione.
- **C9, C12, C16, C18 y C19** se acreditan con código/datos; los documentos que los describen están desfasados. La nota no cambia, pero la defensa sí puede tropezar.
- La auditoría **no aplicó fixes**: esta matriz es una foto, no un plan de mejora ejecutado.
