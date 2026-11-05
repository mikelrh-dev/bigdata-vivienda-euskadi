# Guion de defensa (10 criterios)

Entrada: `README.md` O1-O4, `docs/conclusiones_municipios.md`, `docs/matriz_indicadores.md`. Presentacion offline, sin HDFS ni Kafka (no estan en clase).

## Recorrido decision a gate

1. **Decision O1 (podes independizarte?)**: esfuerzo canonico 18-34 oficial -> 26,61% mediana oficial, 25,2% sobre 30 (40/159). Con 16-29 legacy la mediana oficial es 43,5% (100% sobre 30), por eso se cita 18-34 como canonico y 16-29 solo legacy.
2. **Decision O2 (municipios robustos?)**: solo 4 con n>=30 (`conclusiones_municipios`): Bilbao 173, Donostia 113, Getxo 40, Vitoria 39. El ranking fino de Barakaldo 38,49% sobre Donostia queda fuera por n<30.
3. **Decision O3 (trabajo + vivienda)**: paro Lanbide municipal + precio m2 oficial; r(paro juvenil, alquiler) ~0,385, sin trade-off simple.
4. **Decision O4 (limitaciones)**: proxy de renta, 93 IDW, 4 robustos, emancipacion solo CAE, mezcla de anos.
5. **Pipeline reproducible**: `analysis/run_analisis_mongo.py` orden canonico + `huella_resultados` (SHA-256 de `sort_keys=True`): dos ejecuciones limpias dan la misma huella y los mismos 3 CSV (`mongo_esfuerzo_por_municipio`, `mongo_alquiler_por_municipio`, `mongo_modalidades`).
6. **Performance**: `analysis/mongo_indexes.py` `explain_before_after` en `anuncios` (759 anuncios): antes `COLLSCAN`, despues `IXSCAN` con indice compuesto (`ubicacion.codigo_ine`, `modalidad`, `precio_eur`) y cobertura de `portal_id`. El test `test_indexes_explain` aserta `before==COLLSCAN` y `after==IXSCAN`.
7. **Integridad**: `python extract/generar_manifest.py --verify` (manifest raw 353 y silver 184) y `python transform/run_all.py --check` (staleness por script, exit 0).
8. **Tests**: `.venv/Scripts/python.exe -m pytest tests -q` debe dar 130 passed.

## Los 10 criterios y su laguna

| # | Criterio | Cumple | Laguna (si no se corrige) |
|---|---|---|---|
| 1 | Raw inmutable y manifest | 353 raw + 184 silver SHA-256, `--verify` exit 0 | Sin `.FROZEN`/huella reproducible no hay defensa de no he tocado raw. |
| 2 | Silver utf-8-sig y `codigo_ine` 5 digitos | 252 municipios, zfill en transform | Araba 4 digitos rompe joins; sin `utf-8-sig` mojibake. |
| 3 | Esfuerzo canonico 18-34 | O1 = 26,61% oficial, 25,2% >30, reproducible en Mongo y CSV | Confundir 16-29 (43,5%) con 18-34 invalida O1. |
| 4 | Robustos n>=30 y sensibles | Bilbao 173, Donostia 113, Getxo 40, Vitoria 39 (1 anuncio de diferencia) | Rankear a Barakaldo 38,49% sin n es el error que visa O2. |
| 5 | Pipelines y huella reproducible | 8 pipelines + orden canonico + SHA-256 en `run_analisis` | Sin orden canonico, empates de `$sort` dan huellas distintas. |
| 6 | Performance Mongo (explain) | COLLSCAN 759 -> IXSCAN 1 en `test_indexes_explain` | Sin indice compuesto el lookup es full scan. |
| 7 | Tests y gate | 130 passed en `.venv`, `run_all --check` exit 0 | Gate rojo = no cierre; no hay cierre parcial. |
| 8 | Trazabilidad de fuentes | 5 indicadores con fuente + pipeline en `matriz_indicadores` | Tasa paro aprox (NaN) o renta como salario real destruye la defensa. |
| 9 | Cobertura 159 + sensibilidad IDW | Oficial 159 mediana 26,61; IDW 93 mediana 23,38 | Usar los 252 como si fueran 159 oficiales exagera cobertura. |
| 10 | Offline sin HDFS/Kafka | Solo offline, documentado | Si se promete HDFS/Kafka sin clase, la defensa cae por sobreventa. |

## Cierre de sesion

Mostrar en orden: manifest verify, manifest check, pytest 130, huella de `run_analisis`, explain COLLSCAN/IXSCAN y tabla de 4 robustos. Todo offline; no se hace commit ni push en la demo.
