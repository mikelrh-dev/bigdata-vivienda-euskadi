# Verification Report: mongo-respuesta-tres-robustos

## Veredicto

PASS — pytest real con exit code 0. Sin commit. La comparativa se genero ejecutando el modulo contra Mongo en vivo; el CSV y la tabla del informe coinciden con los valores de Mongo.

## Comandos y evidencia

| Comando | Resultado |
|---------|-----------|
| `.venv/Scripts/python.exe -m analysis.comparativa_mongo` | 3 filas impresas + `data/resultados/comparativa_3_municipios_mongo.csv (3 filas)`, exit code 0 |
| `.venv/Scripts/python.exe -m pytest tests/test_mongo_comparativa.py tests/test_mongo_geo.py -q` | `2 passed in 2.66s`, exit code 0 |

MongoDB responde en `localhost:27017` (base `vivienda_euskadi`). Valores del CSV: Bilbao 48020 n=173 esfuerzo 18-34 37,69 (exacto 37,68858146830279) / 16-29 60,70, precio medio 1695,59, cuantia 850,00, paro 9,71; Donostia 20069 n=113 38,17 / 61,48, 2462,89, 995,00, 5,82; Getxo 48044 n=40 28,60 / 46,06, 1527,50, 887,00, 6,40. Solo hay 4 municipios con n>=30 (Vitoria-Gasteiz 01059 n=39 queda fuera del top 3); 249/252 municipios con paro valido.

## Cobertura de requisitos

| Requisito | Escenario | Evidencia | Estado |
|-----------|-----------|-----------|--------|
| COMPARATIVA-MONGO-01 | Tres filas robustas con paro | `test_comparativa_tres_robustos_n30`: 3 filas ordenadas por n descendente, n>=30, paro no nulo | PASS |
| COMPARATIVA-MONGO-01 | CSV reproducible sin valores inventados | CSV generado por el modulo con 8 columnas y 3 filas; el test escribe en `tmp_path` y reliza codigo y n | PASS |
| COMPARATIVA-MONGO-01 | Informe cita la comparativa con advertencias | Seccion en `docs/informe_capacidad_mongo.md`: tabla de 3 filas, conclusion por municipio, advertencias de muestra pequena y proxy de renta | PASS |

## Diseno

`comparativa_tres_robustos(min_n=30, top_n=3, output_path=None)` reutiliza `pipeline_indicadores_municipio()`, filtra n>=30, toma 3 y hace `find_one` en `municipios` para `empleo.tasa_paro_lanbide_pct`. Conversión tolerante a `Decimal128` (el primer CSV salio con precio medio vacio por `float(Decimal128)`; corregido con fallback a `float(str(value))` y regenerado). strict_tdd false segun `openspec/config.yaml`: modo estandar.

## Issues

- Ninguno bloqueante. No se tocaron `analysis/run_analisis_mongo.py`, `storage/*`, `transform/*` ni `tests/test_mongo_orquestador.py`.
- WARNING: `data/resultados/comparativa_3_municipios_mongo.csv` no aparece en `git status` (ignorado por git): existe en disco y lo genera el modulo, pero no entraria en un commit sin forzar su inclusion.

## Ficheros

`analysis/comparativa_mongo.py` (nuevo, 121 lineas), `data/resultados/comparativa_3_municipios_mongo.csv` (nuevo, 4 lineas), `tests/test_mongo_comparativa.py` (nuevo, 38 lineas), `docs/informe_capacidad_mongo.md` (seccion anadida al final). Artefactos en `openspec/changes/mongo-respuesta-tres-robustos/`: proposal.md, specs/presentacion-de-resultados/spec.md, design.md, tasks.md, verify-report.md.
