# Matriz de rúbrica v7 — 19 criterios

**Nota global: 187 / 190 (98,4 %)**
BDA RA1: 37/40 · SBD RA1: 40/40 · SBD RA3: 60/60 · SBD RA4: 50/50.

| # | Criterio | Nota | Evidencia principal | Falsador |
|---|---|---:|---|---|
| 1 | BDA · Extracción Python (API **y** scraping) | **10** | 41 scripts en `extract/`; APIs `01_eustat_api.py:116`, `06_ine_api.py:51`, `19_udalmap...:105`, `25_udalmap_extendido.py:55`; scrapers `05_fotocasa_scraper.py:157`, `08_pisos_scraper.py:117`, `13_scraping_habitaciones.py:153/269`; `main_ingest.py:300` orquesta | Que un extractor clave exija intervención manual |
| 2 | BDA · HDFS (originales **y** procesados + recuperación) | **7** | HDFS raw: `fileCount=352`, `directoryCount=6`; lectura real de `alquiler_distrito_seccion_original.csv` (300 bytes); `procesado` → **404**; `scripts/upload_procesado.py:62` rechaza subir sin `--dry-run` | Que `procesado` exista en HDFS y se recupere |
| 3 | BDA · Kafka (productor y consumidor procesan) | **10** | Topic `vivienda_euskadi`: 1 partición, 1 réplica, `begin=0`, `end=352`, grupo `hdfs_centro` `committed=352`, lag 0; `kafka_raw_producer.py:49`, `kafka_hdfs_uploader.py:92` | Que el offset comprometido no avance o que solo haya mocks |
| 4 | BDA · Integración (flujo completo hasta MongoDB) | **10** | `gate_extremo_a_extremo.py --offline` OK; `run_mongo_pipeline.py --dry-run` OK; 11/11 pipelines ejecutados; cadena `extract → transform → load_mongo → Mongo → analysis` | Que el flujo a Mongo dependa de un paso manual |
| 5 | SBD RA1 · Integración de fuentes (2+ y campo común) | **10** | `load_all()` L590 carga **14 colecciones**; `$lookup` `anuncios → municipios` por `ubicacion.codigo_ine`: **594/594 con match** | Que los `codigo_ine` no casen |
| 6 | SBD RA1 · Construcción (2+ colecciones + relación/embedding/referencia) | **10** | `municipios` con `demografia`, `empleo`, `demanda_social`; `anuncios.ubicacion` anidado, `equipamiento[]` (77 docs), `historico_precios[]`; referencias por `codigo_ine` | Que el anidamiento no se use en consultas |
| 7 | SBD RA1 · Limpieza PyMongo (4+ ops con nulos, duplicados y tipos) | **10** | `clean_mongo.py`: `canonicalize_codigo_ine` L32, `mark_nulls` L104, `resolve_duplicates` L164, `convert_types` L222; tests `test_clean_mongo.py` con asserts y no-op | Que una operación sea alias de otra |
| 8 | SBD RA1 · Automatización (carga+limpieza+transformación) | **10** | `scripts/run_mongo_pipeline.py:63`: `load_all → clean_all → ensure_indexes → pipeline_indicadores`; `--dry-run` OK | Que falte un paso o haya edición manual |
| 9 | SBD RA3 · Modelado (+ embedding/referencing explicado) | **10** | `docs/modelo_mongodb.md`: embed en `municipios` y `anuncios`; referencia por `codigo_ine`; tipos BSON (`Decimal128`, arrays, GeoJSON) | Que la justificación no corresponda al esquema |
| 10 | SBD RA3 · CRUD (4 ops + comprobación en código) | **10** | `clean_mongo.py:311 demo_crud_operations`; `test_mongo.py:214 test_crud_demo` asserta inserted_id, 2 ids, count 3, update 1/1, `find_one_and_update="ok"`, upsert 0, bulk delete 1, delete_one 1, delete_many 2, remaining 1, `_demo_crud` ausente | Que el test solo compruebe que no lanza |
| 11 | SBD RA3 · Consultas (5 útiles, anidada/array y 2+ condiciones) | **10** | `mongo_queries.py` 30 funciones; ejecutadas igualdad, dot notation, `$elemMatch`, `$and`, proyección y sort (3 resultados cada una) | Que las 5 sean variantes de igualdad |
| 12 | SBD RA3 · Aggregation (3+ pipelines, 5 etapas, `$group` + `$lookup`/`$unwind`/`$facet`) | **10** | **11/11 pipelines** ejecutan; etapas: `$lookup` (L71,143,295…), `$unwind` (L296,477,497,499,518), `$group` (L288,316,495,690), `$match`, `$addFields`, `$project`, `$sort`, `$limit`; `$facet` no usado (no obligatorio) | Que `$lookup/$unwind` sean decorativos |
| 13 | SBD RA3 · Índices (`explain` antes/después, `COLLSCAN`/`IXSCAN`, `totalDocsExamined`) | **10** | Índice: `IXSCAN`, nReturned 8, `totalDocsExamined=8`, keys 8. Sin índice (`$natural`): `COLLSCAN`, nReturned 8, `totalDocsExamined=594`, keys 0. `mongo_indexes.py:107` | Que los números estén hardcodeados |
| 14 | SBD RA3 · Consistencia (atómica + justificación o transacción) | **10** | `storage/mongo.py:170 marcar_calidad_municipio` con `find_one_and_update` + `ReturnDocument.AFTER`; `test_mongo_consistencia.py:49` asserta valor nuevo y no creación; sonda de transacción rechazada en standalone (`setName=None`) | Que el test no compruebe el valor nuevo |
| 15 | SBD RA4 · Datos heterogéneos (estructuras distintas adaptadas) | **10** | 41 extractores sobre CSV/JSON/HTML/XLSX/ZIP/SHP/GTFS; `unificar_anuncios.py:135/177/217` (3 portales), `normalizar_json_crudos.py:30`, `load_mongo.py:70 _geo_point` | Que cada fuente se cargue sin normalización común |
| 16 | SBD RA4 · Automatización del análisis | **10** | `run_analisis_mongo.py:1161 main`: 11 pipelines, doble ejecución con huella, 8 CSV + PNG; 11/11 pipelines ejecutados en lectura | Que algún análisis principal se haga a mano |
| 17 | SBD RA4 · Indicadores (5+, 2+ fuentes) | **10** | `docs/matriz_indicadores.md`: 5 indicadores (esfuerzo 18-34, tensión social, paro Lanbide, precio m2, VPO terminadas); `$lookup` a `anuncios`, `alquiler_municipal`, `municipios`, `udalmap_*`, `osrm_tiempos`, `etxebide_*` | Que dos indicadores sean el mismo con otro nombre |
| 18 | SBD RA4 · Respuesta al reto (3+ municipios, conclusión ↔ indicador) | **10** | `comparativa_3_municipios_mongo.csv`: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39; `docs/conclusiones_municipios.md` da una frase por municipio con esfuerzo, precio, cuantía y paro | Que las conclusiones no citen indicador |
| 19 | SBD RA4 · Preparación visualización (3+ conjuntos automáticos) | **10** | `EXPORTS_8` L102; 8 CSV `mongo_*` con 252/252/2/252/252/322/251/9 filas; 28 PNG + 8 anexo; `exportar_png_desde_mongo` L397 | Que los CSV estén tecleados o los PNG no vengan de Mongo |

## Lectura

- El único criterio que no llega al 10 literal es **HDFS (C2)**: hay originales y recuperación, pero **no hay procesados** en HDFS (`procesado` → 404) y el script de subida solo hace `--dry-run`.
- Todo lo demás cumple el umbral del 10 con evidencia ejecutada, no con documentación.
- Los desfases documentales no cambian la nota, pero son riesgo de defensa (ver `hallazgos_v7.csv`).
