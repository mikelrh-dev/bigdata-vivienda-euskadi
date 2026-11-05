# Guion Tema 8 (1 página)

Entrada: `README.md` O1-O4, `docs/conclusiones_municipios.md`, `docs/matriz_indicadores.md`. Presentacion offline actual: HDFS centro `http://10.22.87.215:50070` solo lectura + Kafka VM `192.168.201.162:9094` broker 4.3.1 KRaft pid 1832 (re-verificado en `docs/trazabilidad_vm.md`).

## Tema 8: embedding, índices, atomicidad

- **Embedding**: cada anuncio se almacena embebido en `municipios` (`ubicacion.codigo_ine`, `demografia`, `empleo`, `demanda_social`) con `alquiler_municipal` por `$lookup`; documentos agregados, no referencias sueltas.
- **Índices**: `anuncios` pasa de COLLSCAN a IXSCAN con indice compuesto (`ubicacion.codigo_ine`, `modalidad`, `precio_eur`) + cobertura de `portal_id` (`explain_before_after`, test `test_indexes_explain`).
- **Atomicidad**: escrituras al vuelo por documento (upsert idempotente desde Kafka, `storage/kafka_consumer.py`), sin operaciones multi-documento parciales en la cadena; el pipeline de analisis solo lee.

## Recorrido de decisión a gate

1. **O1 (podes independizarte?)**: canonico **18-34 oficial -> 26,61% mediana oficial, 25,2% sobre 30 (40/159)**. Con **16-29 legacy** la mediana es 43,5% (100% sobre 30): 16-29 queda solo legacy, ninguna conclusion lo usa como canonico.
2. **O2 (municipios robustos?)**: solo 4 con n>=30: **Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39**. Advertencia: **Getxo 40 vs Vitoria-Gasteiz 39 = 1 anuncio, no ranking firme**; Barakaldo (n=13) queda fuera por n<30.
3. **O3 (trabajo + vivienda)**: paro Lanbide Mongo + precio m2 oficial; r(paro juvenil, alquiler) ~0,385, sin trade-off simple.
4. **O4 (limitaciones)**: proxy de renta, 93 IDW solo sensibilidad, 4 robustos, emancipacion solo CAE, mezcla de anos 2024/2026.
5. **Pipeline reproducible**: 8 pipelines + orden canonico + `huella_resultados` (SHA-256 `sort_keys=True`): dos ejecuciones dan la misma huella y los mismos CSV 253/253/3 (ver `docs/matriz_indicadores.md`).
6. **Los 10 criterios** (detalle abajo): raw inmutable, silver utf-8-sig, esfuerzo 18-34, robustos n>=30, pipelines con huella, performance explain, tests, trazabilidad, cobertura 159+IDW, cadena HDFS+Kafka.
7. **Integridad**: `generar_manifest.py --verify` (353 raw + 184 silver) y `transform/run_all.py --check` (exit 0).
8. **Tests**: `pytest tests -q` = 130 passed, sin `data/raw` en `git status`.

## Los 10 criterios y su laguna

| # | Criterio | Cumple | Laguna (si no se corrige) |
|---|---|---|---|
| 1 | Raw inmutable y manifest | 353 raw + 184 silver SHA-256, `--verify` exit 0 | Sin `.FROZEN`/huella reproducible no hay defensa de no he tocado raw. |
| 2 | Silver utf-8-sig y `codigo_ine` 5 digitos | 252 municipios, zfill en transform | Araba 4 digitos rompe joins; sin `utf-8-sig` mojibake. |
| 3 | Esfuerzo canonico 18-34 | O1 = 26,61% oficial, 25,2% >30, reproducible en Mongo y CSV | Confundir 16-29 (43,5%) con 18-34 invalida O1; 16-29 sigue legacy. |
| 4 | Robustos n>=30 y sensibles | Bilbao 173, Donostia 113, Getxo 40, Vitoria 39 (1 anuncio de diferencia) | Rankear a Barakaldo 38,49% sin n es el error que visa O2. |
| 5 | Pipelines y huella reproducible | 8 pipelines + orden canonico + SHA-256 en `run_analisis` | Sin orden canonico, empates de `$sort` dan huellas distintas. |
| 6 | Performance Mongo (índices/explain) | COLLSCAN 759 -> IXSCAN 1 en `test_indexes_explain` | Sin indice compuesto el lookup es full scan. |
| 7 | Tests y gate | 130 passed en `.venv`, `run_all --check` exit 0 | Gate rojo = no cierre; no hay cierre parcial. |
| 8 | Trazabilidad de fuentes | 5 indicadores con fuente + pipeline en `matriz_indicadores` | Tasa paro aprox (NaN) o renta como salario real destruye la defensa. |
| 9 | Cobertura 159 + sensibilidad IDW | Oficial 159 mediana 26,61; IDW 93 mediana 23,38 | Usar los 252 como si fueran 159 oficiales exagera cobertura. |
| 10 | Cadena HDFS centro + Kafka pid 1832 | HDFS solo lectura + Kafka pid 1832 re-verificado en trazabilidad | Si se promete cadena sin verificarla, la defensa cae por sobreventa. |

## Cierre de sesion

Mostrar en orden: manifest verify, manifest check, pytest 130, huella de `run_analisis`, explain COLLSCAN/IXSCAN y tabla de 4 robustos (Getxo 40 vs Vitoria 39 sin ranking firme). Todo lectura; no se hace commit ni push en la demo.
