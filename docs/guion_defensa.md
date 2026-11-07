# Guion Tema 8 (1 página)

> Para la defensa completa de 12 minutos con reparto por persona: `docs/guion_defensa_12min.md`.

Entrada: `README.md` O1-O4, `docs/conclusiones_municipios.md`, `docs/matriz_indicadores.md`. Presentacion offline actual: HDFS centro `http://10.22.87.215:50070` solo lectura + Kafka clúster centro `10.22.87.215:9092` topic `anuncios_inmobiliarios` 1 partición (lag 0 verificado en `openspec/audit/informe_auditoria_2026-11-06_v2.md`).

## Tema 8: embedding, índices, atomicidad

- **Embedding**: cada anuncio se almacena embebido en `municipios` (`ubicacion.codigo_ine`, `demografia`, `empleo`, `demanda_social`) con `alquiler_municipal` por `$lookup`; documentos agregados, no referencias sueltas.
- **Índices**: `anuncios` pasa de COLLSCAN a IXSCAN con indice compuesto (`ubicacion.codigo_ine`, `modalidad`, `precio_eur`) + cobertura de `portal_id` (`explain_before_after`, test `test_indexes_explain`).
- **Atomicidad**: escrituras al vuelo por documento (upsert idempotente en `storage/load_mongo.py`, índice único `(portal, id_anuncio)`), sin operaciones multi-documento parciales en la cadena; el pipeline de analisis solo lee.

## Recorrido de decisión a gate

1. **O1 (podes independizarte?)**: canonico **18-34 oficial -> 26,61% mediana oficial, 25,2% sobre 30 (40/159)**. Con **16-29 legacy** la mediana es 42,9% (oficial, no comparable): 16-29 queda solo legacy, ninguna conclusion lo usa como canonico. **Sensibilidad**: con IDW 252 -> 25,37% (47/252, 18,7%); el titular no cambia. Bootstrap (n_larga_solo_vivienda 67/60/39/37, distinto del n_anuncios Tier 204/126/50/39; no intercambiables): Bilbao 33.75–40.95, Getxo 27.54–31.77 y Donostia 32,4-45,8 se solapan, sin orden firme.
2. **O2 (municipios robustos?)**: solo 4 con n>=30: **Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39**. Advertencia: **Getxo 50 vs Vitoria-Gasteiz 39 = 11 anuncios (no 1, tras re-resolucion pisos)**; Barakaldo (n=6) queda fuera por n<30. Tier B 10-29 = 3 (Sopela 19, Zarautz 15, Santurtzi 11, solo indicativo, temporal!=larga); Tier C 1-9 = 57 sin precio municipal; Tier D 0 = 188 sin dato (+ contexto oficial). Nivel (tipología 4/54/194) es ortogonal a Tier (confianza 4/3/57/188): son ejes ortogonales, no intercambiables.
3. **O3 (trabajo + vivienda)**: paro Lanbide Mongo + precio m2 oficial; r(conteo parados jóvenes, alquiler) ~0,39 (conteos, no tasa), sin trade-off simple.
4. **O4 (limitaciones)**: proxy de renta, 93 IDW solo sensibilidad, 4 robustos, emancipacion solo CAE, mezcla de anos 2024/2026. VPO: flujo oficial 251/252 (Usansolo sin dato); stock historico sin fuente.
5. **Pipeline reproducible**: 10 pipelines + orden canonico + `huella_resultados` (SHA-256 `sort_keys=True`): dos ejecuciones del mismo estado dan la misma huella (ver salida de `run_analisis_mongo`) y los mismos 6 CSV (`mongo_*.csv` doble SHA identico) y 12 PNG únicos de 13 emitidos (ver `docs/matriz_indicadores.md`).
6. **Los 10 criterios** (detalle abajo): raw inmutable, silver utf-8-sig, esfuerzo 18-34, robustos n>=30, pipelines con huella, performance explain, tests, trazabilidad, cobertura 159+IDW, cadena HDFS+Kafka.
7. **Integridad**: `generar_manifest.py --verify` (352 raw en HDFS + 188 silver) y `transform/run_all.py --check` (exit 0).
8. **Tests**: `pytest tests -q` = 177 passed + 1 skipped destructivo separado, sin `data/raw` en `git status`.

## Los 10 criterios y su laguna

| # | Criterio | Cumple | Laguna (si no se corrige) |
|---|---|---|---|
| 1 | Raw inmutable y manifest | 352 raw en HDFS + 188 silver SHA-256, `--verify` exit 0 | Sin `.FROZEN`/huella reproducible no hay defensa de no he tocado raw. |
| 2 | Silver utf-8-sig y `codigo_ine` 5 digitos | 252 municipios, zfill en transform | Araba 4 digitos rompe joins; sin `utf-8-sig` mojibake. |
| 3 | Esfuerzo canonico 18-34 | O1 = 26,61% oficial, 25,2% >30, reproducible en Mongo y CSV | Confundir 16-29 (42,9%) con 18-34 invalida O1; 16-29 sigue legacy. |
| 4 | Robustos n>=30 y sensibles | Bilbao 204, Donostia 126, Getxo 50, Vitoria 39 (diferencia Getxo-Vitoria 11, no 1) | Rankear a Barakaldo 38,49% sin n es el error que visa O2. |
| 5 | Pipelines y huella reproducible | 10 pipelines + orden canonico + SHA-256 en `run_analisis` | Sin orden canonico, empates de `$sort` dan huellas distintas. |
| 6 | Performance Mongo (índices/explain) | COLLSCAN 594 -> IXSCAN 1 en `test_indexes_explain` | Sin indice compuesto el lookup es full scan. |
| 7 | Tests y gate | 177 passed + 1 skipped destructivo en `.venv`, `run_all --check` exit 0 | Gate rojo = no cierre; no hay cierre parcial. |
| 8 | Trazabilidad de fuentes | 5 indicadores con fuente + pipeline en `matriz_indicadores` | Tasa paro aprox (NaN) o renta como salario real destruye la defensa. |
| 9 | Cobertura 159 + sensibilidad IDW | Oficial 159 mediana 26,61; con IDW 252 -> 25,37 (47 > 30) | Usar los 252 como si fueran 159 oficiales exagera cobertura. |
| 10 | Cadena HDFS centro + Kafka centro | HDFS 352/352 con SHA igual + Kafka lag 0 tras recarga de 352 | Si se promete cadena sin verificarla, la defensa cae por sobreventa. |

## Cierre de sesion

Mostrar en orden: manifest verify, manifest check, pytest 177+1s, huella de `run_analisis`, explain COLLSCAN/IXSCAN y tabla de 4 robustos (Getxo 50 vs Vitoria 39 sin ranking firme; Tier B 10-29 = 3 solo indicativo). Todo lectura; no se hace commit ni push en la demo.

## Falsación (qué nos tumbaría)

- **Falsación exterior**: una fuente externa independiente (no Fotocasa/Pisos/RealtyAPI) que muestre que en Bilbao/Donostia/Getxo/Vitoria el precio medio o el esfuerzo difieren >10% del nuestro con n>=30 y misma ventana temporal tumba la comparación firme. En concreto, si una revisión de subtítulo/título mostrara que alguno de los 45 fuera de Euskadi (Logroño/Castro/Ampuero) está en Euskadi, la cuarentena seria errónea; la cuarentena es reversible y `cuarentena_pisos.csv` permite reabrirlos.
- **Falsación por no-ascensor (no comparable)**: el grupo con ascensor vs sin ascensor no es comparable para precio: la muestra con ascensor es sistemáticamente distinta (edificios recientes, capitales). No se compara precio sin estratificar por ascensor; un estudio que mostrara que la diferencia de esfuerzo desaparece al estratificar por ascensor falsaría la lectura de precio como tensión pura de mercado.
- **Precio solo en 62/252**: el precio medio de anuncios es observable solo en 62 de 252 municipios con anuncio real (resto `None`, sin imputación IDW/comarcal). Cualquier conclusión de precio en los 190 sin precio es inválida; el esfuerzo 252 es contextual sobre 159 oficiales, no estimación oficial donde n<30.
