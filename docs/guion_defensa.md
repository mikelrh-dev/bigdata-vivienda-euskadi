# Guion Tema 8 (1 página)

> Para la defensa completa de 12 minutos con reparto por persona: `docs/guion_defensa_12min.md`.

Entrada: `README.md` O1-O4, `docs/conclusiones_municipios.md`, `docs/matriz_indicadores.md`. Presentacion offline actual: HDFS centro `http://10.22.87.215:50070` solo lectura (352 ficheros raw canónicos en `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`; manifest local 354 SHA con 2 alias legacy) + Kafka clúster centro `10.22.87.215:9092` topic vigente `vivienda_euskadi` 1 partición RF 1 grupo `hdfs_centro` (lag 0; topic viejo `anuncios_inmobiliarios` eliminado 2026-11-06, verificado en `openspec/audit/informe_auditoria_2026-11-06_v2.md`).

## Tema 8: embedding, índices, atomicidad

- **Embedding**: cada anuncio se almacena embebido en `municipios` (`ubicacion.codigo_ine`, `demografia`, `empleo`, `demanda_social`) con `alquiler_municipal` por `$lookup`; documentos agregados, no referencias sueltas. Mongo local `vivienda_euskadi`: 16 vivas (14 negocio + 2 habitaciones 201+201) + 14 `__backup` = 30 totales.
- **Índices**: `anuncios` pasa de COLLSCAN (594 examinados) a IXSCAN (1 examinado) con indice compuesto ESR `{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}` + cobertura de `portal_id` (`explain_before_after` en `analysis/mongo_indexes.py`, invocado en `analysis/run_analisis_mongo.py`, test `test_indexes_explain`). ESR = Equality, Sort, Range en ese orden.
- **Atomicidad vs transacción**: atomicidad de documento (upsert idempotente en `storage/load_mongo.py`, índice único `(portal, id_anuncio)`) no exige replica set; transacción multi-documento commit/abort sí exigiría replica set y no se fuerza en standalone local (solo sonda en `vivienda_euskadi_test`, prod sigue en 594). El pipeline de analisis solo lee.

## Recorrido de decisión a gate

1. **O1 (podes independizarte?)**: canonico **18-34 oficial -> 26,61% mediana oficial, 25,2% sobre 30 (40/159)**. Con **16-29 legacy** la mediana es 42,9% (oficial, no comparable): 16-29 queda solo legacy, ninguna conclusion lo usa como canonico. **Sensibilidad**: con IDW 252 -> 25,37% (47/252, 18,7%); el titular no cambia. Bootstrap (n_larga_solo_vivienda 67/60/39/37, distinto del n_anuncios Tier 204/126/50/39; no intercambiables): Bilbao 33.75–40.95, Getxo 27.54–31.77 y Donostia 32,4-45,8 se solapan, sin orden firme.
2. **O2 (municipios robustos?)**: solo 4 con n>=30: **Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39**. Advertencia: **Getxo 50 vs Vitoria-Gasteiz 39 = 11 anuncios (no 1, tras re-resolucion pisos)**; Barakaldo (n=6) queda fuera por n<30. Tier B 10-29 = 3 (Sopela 19, Zarautz 15, Santurtzi 11, solo indicativo, temporal!=larga); Tier C 1-9 = 57 sin precio municipal; Tier D 0 = 188 sin dato (+ contexto oficial). Nivel (tipología 4/54/194) es ortogonal a Tier (confianza 4/3/57/188): son ejes ortogonales, no intercambiables.
3. **O3 (trabajo + vivienda)**: paro Lanbide Mongo + precio m2 oficial; r(conteo parados jóvenes, alquiler) ~0,39 (conteos, no tasa), sin trade-off simple.
4. **O4 (limitaciones)**: proxy de renta, 93 IDW solo sensibilidad, 4 robustos, emancipacion solo CAE, mezcla de anos 2024/2026. VPO: flujo oficial 251/252 (Usansolo sin dato); stock historico sin fuente.
5. **Pipeline reproducible**: 11 pipelines (antes 10) + orden canonico + `huella_resultados` (SHA-256 `sort_keys=True`): dos ejecuciones del mismo estado dan la misma huella (ver salida de `run_analisis_mongo`) y los mismos 8 CSV `mongo_*` (doble SHA identico, `EXPORTS_8`) y 28+8 PNG (28 resultados + 8 anexo desde los 11 pipelines; antes 12 únicos / 13 emitidos de DuckDB) (ver `docs/matriz_indicadores.md`).
6. **Los 10 criterios** (detalle abajo): raw inmutable, silver utf-8-sig, esfuerzo 18-34, robustos n>=30, pipelines con huella, performance explain, tests, trazabilidad, cobertura 159+IDW, cadena HDFS+Kafka.
7. **Integridad**: `scripts/gate_extremo_a_extremo.py --offline` (354 SHA + 188 silver + lag 0) y `transform/run_all.py --check` (34/34 OK) y `scripts/verificar_gobernanza.py` (46 requisitos, 45 scripts / 34 DAG, 188, 11 pipelines).
8. **Tests**: `pytest tests -q` = 236 passed + 2 skipped (238 collected), sin `data/raw` en `git status`. CI en rama `master` (`.github/workflows/quality-gate.yml` push a `master` + `pull_request` + `workflow_dispatch` vivo manual `GATE_LIVE=1`); antes disparaba en `main` y no corría en `master`. Anuncios vigentes 594 (843 raw → 594 tras dedup + cuarentena 45; 759 histórico pre-v5).

## Los 10 criterios y su laguna

| # | Criterio | Cumple | Laguna (si no se corrige) |
|---|---|---|---|
| 1 | Raw inmutable y manifest | 352 raw canónicos en HDFS + manifest local 354 SHA (2 alias legacy) + 188 silver SHA-256, gate offline OK | Sin `.FROZEN`/huella reproducible no hay defensa de no he tocado raw. |
| 2 | Silver utf-8-sig y `codigo_ine` 5 digitos | 252 municipios, zfill en transform | Araba 4 digitos rompe joins; sin `utf-8-sig` mojibake. |
| 3 | Esfuerzo canonico 18-34 | O1 = 26,61% oficial, 25,2% >30, reproducible en Mongo y CSV | Confundir 16-29 (42,9%) con 18-34 invalida O1; 16-29 sigue legacy. |
| 4 | Robustos n>=30 y sensibles | Bilbao 204, Donostia 126, Getxo 50, Vitoria 39 (diferencia Getxo-Vitoria 11, no 1) | Rankear a Barakaldo 38,49% sin n es el error que visa O2. |
| 5 | Pipelines y huella reproducible | 11 pipelines (antes 10) + orden canonico + SHA-256 en `run_analisis`; gobernanza 46/45/11 | Sin orden canonico, empates de `$sort` dan huellas distintas. |
| 6 | Performance Mongo (índices/explain) | COLLSCAN 594 -> IXSCAN 1 en `test_indexes_explain` con ESR | Sin indice compuesto el lookup es full scan. |
| 7 | Tests y gate | 236 passed + 2 skipped, `run_all --check` 34/34 OK, gobernanza TODO OK, FAIL 07 paro-cero conocido sin enmascarar | Gate rojo = no cierre; no hay cierre parcial. |
| 8 | Trazabilidad de fuentes | 5 indicadores con fuente + pipeline en `matriz_indicadores` | Tasa paro aprox (NaN) o renta como salario real destruye la defensa. |
| 9 | Cobertura 159 + sensibilidad IDW | Oficial 159 mediana 26,61; con IDW 252 -> 25,37 (47 > 30) | Usar los 252 como si fueran 159 oficiales exagera cobertura. |
| 10 | Cadena HDFS centro + Kafka centro | HDFS 352 canónicos con SHA igual (manifest 354) + Kafka `vivienda_euskadi` RF1 lag 0 tras recarga de 352 (topic viejo `anuncios_inmobiliarios` eliminado) | Si se promete cadena sin verificarla, la defensa cae por sobreventa. |

## FAQ oral (para la defensa)

- **Replica sets**: MongoDB local es standalone sin replica set. La atomicidad de un documento no lo exige; la transacción multi-documento commit/abort sí. No forzamos replica set sobre el standalone; solo sonda en `vivienda_euskadi_test` (ver `docs/modelo_mongodb.md`).
- **Shard key**: candidato conceptual `codigo_ine` (distribución por municipio) frente a `portal` (baja cardinalidad, skew); a esta escala no shardeamos (594 anuncios, 252 municipios). No hay sharding implementado.
- **ESR**: Equality, Sort, Range. El índice `{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}` respeta ese orden para la consulta real de `explain_before_after`.
- **Costes**: índice ESR + `portal_id` cobertura y 2dsphere sparse; 24 índices en 16 vivas (16 `_id` + 8 de negocio). El coste de escritura se asume frente a evitar un COLLSCAN de 594 por consulta. Los 8 PNG de anexo se conservan sin coste extra salvo disco.
- **594 vs 759**: 759 es histórico pre-v5; 843 raw → 594 vigente tras re-resolucion pisos + cuarentena de 45 fuera de Euskadi. Usar 759 hoy infla la cobertura.
- **352 vs 354**: 352 ficheros canónicos publicados en HDFS; 354 entradas SHA en manifest local `docs/raw_manifest_sha256.txt` (2 alias legacy no publicados). El gate verifica 354; el canónico citado en defensa es 352. 356 en disco local incluye `.FROZEN`/`.gitkeep`.
- **Topic viejo vs nuevo**: `anuncios_inmobiliarios` (VM legacy, 3 particiones en demo) eliminado 2026-11-06 con sus datos; vigente `vivienda_euskadi` en `10.22.87.215:9092` 1 partición RF 1 grupo `hdfs_centro` (productor de manifiesto → consumidor que sube a HDFS). RF 1 justificado como single node sin HA.

## Cierre de sesion

Mostrar en orden: `scripts/gate_extremo_a_extremo.py --offline`, `scripts/verificar_gobernanza.py`, `transform/run_all.py --check`, pytest 236+2s, huella de `run_analisis`, explain COLLSCAN 594→IXSCAN 1 y tabla de 4 robustos (Getxo 50 vs Vitoria 39 sin ranking firme; Tier B 10-29 = 3 solo indicativo). Todo lectura; no se hace commit ni push en la demo.

## Falsación (qué nos tumbaría)

- **Falsación exterior**: una fuente externa independiente (no Fotocasa/Pisos/RealtyAPI) que muestre que en Bilbao/Donostia/Getxo/Vitoria el precio medio o el esfuerzo difieren >10% del nuestro con n>=30 y misma ventana temporal tumba la comparación firme. En concreto, si una revisión de subtítulo/título mostrara que alguno de los 45 fuera de Euskadi (Logroño/Castro/Ampuero) está en Euskadi, la cuarentena seria errónea; la cuarentena es reversible y `cuarentena_pisos.csv` permite reabrirlos.
- **Falsación por no-ascensor (no comparable)**: el grupo con ascensor vs sin ascensor no es comparable para precio: la muestra con ascensor es sistemáticamente distinta (edificios recientes, capitales). No se compara precio sin estratificar por ascensor; un estudio que mostrara que la diferencia de esfuerzo desaparece al estratificar por ascensor falsaría la lectura de precio como tensión pura de mercado.
- **Precio solo en 62/252**: el precio medio de anuncios es observable solo en 62 de 252 municipios con anuncio real (resto `None`, sin imputación IDW/comarcal). Cualquier conclusión de precio en los 190 sin precio es inválida; el esfuerzo 252 es contextual sobre 159 oficiales, no estimación oficial donde n<30.
