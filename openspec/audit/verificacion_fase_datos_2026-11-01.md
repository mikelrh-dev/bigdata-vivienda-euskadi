# Verificación de estado — fase de datos e infraestructura (actualizado)

Verificación read-only tras los commits Bloque A/B/C del otro agente. No se modificaron datos ni código en esta verificación.

## 1. Comandos ejecutados y resultados

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | 82 passed, 3.97s |
| `.venv/Scripts/python.exe verificar_fase_datos.py` (raíz) | 15/15 PASS, exit 0 |
| `.venv/Scripts/python.exe transform/run_all.py --check` | exit 1: 6 scripts `DESACTUALIZADO` |
| `extract/generar_manifest.py --verify` | raw OK (314 entradas); silver FAIL (faltan sidecars `_meta/*`) |
| `run_manifest.json` | 35 scripts, todos `rc=0` |

## 2. Estado por WP (fase de datos) tras Bloque A/B/C

| WP | Estado | Evidencia clave |
|---|---|---|
| WP-01 Orquestador declarativo | Parcial | `transform/run_all.py`: 35 `SCRIPTS` + 7 `EXCLUIDOS`; dry-run OK. Falta DoD test `test_run_all_orquesta_todos_los_scripts`. |
| WP-02 Un escritor dim gold | Done | Solo `construir_dim_gold.py` escribe `dim_municipios_enriquecido.csv`. |
| WP-03 `n_anuncios` real | Done | Gate 06: real=759, crudo=843. |
| WP-04 Ceros/clip | Done | `corregir_empleo.py` bruto/flag/mask; gate 07 PASS. |
| WP-05 Brecha eliminada | Done | `brecha_ocupacion_actividad_pct` ausente en gold (gate 08). |
| WP-06 Esfuerzo canónico | Done | `esfuerzo_joven_pct` en base y renta; gate 09 PASS. |
| WP-07 Metadata única | Parcial | `extract/_common.py` valida raw; sidecars en `_meta`; gate 03 59/59. Validación estricta solo en raw; tests dedicados ausentes. |
| WP-08 Manifests | Parcial | Raw verify OK (314). Silver manifest stale: faltan sidecars `_meta/*`. |
| WP-09 Nombres estables | Parcial | 3 ficheros con timestamp en `data/procesado` (`anuncios_*_20261029_*_normalizado.json`) + sidecars. |
| WP-10 Lectura tipada | Parcial | `transform/` pasa AST test; `extract/` tiene 2 lecturas sin `dtype` (`_common.py`, `10_opendata_bizilagun_etxebide.py`). |
| WP-11 Fallback Eustat | Parcial | `flag_ratio_fiscal` existe en `dim_municipios_renta.csv`, pero todos los valores son `calculado` (no distingue eustat vs fallback). |
| WP-12 Cobertura | Done (artefacto) | `data/procesado/cobertura_anuncios.csv` existe (252 filas + header, `nivel_fiabilidad`). |
| WP-13 Higiene/docs | Parcial | `openspec/project.md` stale (314/96/59 vs 319/180/82); `requirements.txt` sin `hdfs`. |
| WP-14 Gate | Done | `verificar_fase_datos.py`: 15/15, exit 0. |
| WP-15 `renta_origen` por fila | Missing | `renta_municipal_completa.csv`: `renta_origen` sigue siendo `Eustat+INE_Atlas` en 252/252. |
| WP-16 dim fuera de raw | Missing | 8 extractores siguen leyendo `data/raw/dim_municipios.json`. |
| WP-17 Ingestion manifest | Parcial | Existe en `data/procesado/_meta/ingestion_manifest.json`, no en `data/raw/ingestion_manifest.json`. |
| WP-18 Metadata salario | Missing | `ovj_salario_joven_2024.json` y `emancipacion_juventud_resumen.json` sin bloque `metadata` estándar. |
| WP-19 Archivar auditorías | Done | `openspec/audit/archivado/` (19 docs); vigentes: rev.2, plan, contrauditoría. |
| WP-20 Reglas portables | Done | `docs/reglas_limpieza.md` presente (R1–R7). |

## 3. Problemas estructurales

- Tests: 82 vs ~85 previstos; faltan ~3 tests DoD.
- `run_all --check`: exit 1, 6 scripts `DESACTUALIZADO` por reescrituras in-place de `dim_municipios.csv` y `anuncios_unificados.csv`.
- Silver manifest no verifica (faltan sidecars `_meta/*`).
- 3 ficheros con timestamp en `data/procesado` (+ sidecars).
- 2 lecturas sin `dtype` en `extract/`.
- Documentación de inventario/cifras desactualizada (`AGENT.md`, `openspec/project.md`).

## 4. Estado de infraestructura (fases 2–9)

Sin cambios: no existe `storage/`, `analysis/`, `visualization/`, `notebooks/`, `docker-compose.yml`, `plan/arquitectura.md`. Dependencias `pymongo` y `kafka-python-ng` presentes; falta cliente HDFS. Docker Desktop + Compose disponibles.

## 5. Conclusiones

1. El otro agente (Bloque A/B/C) avanzó WP-12, WP-11 y WP-17 parcialmente, y los tests subieron a 82.
2. Aún faltan WP-15, WP-16, WP-18 y ajustes de WP-09/10/11/13/17 para cerrar la fase de datos al 10/10.
3. La reproducibilidad del pipeline es funcional (35/0), pero `--check` sigue fallando por staleness estructural.
4. La infraestructura sigue sin empezar.

## 6. Próximos pasos recomendados

A. Cerrar WP-15, WP-16, WP-18 y reubicar WP-17 en `data/raw/`.  
B. Resolver staleness estructural de `run_all --check`.  
C. Actualizar `openspec/project.md` y `AGENT.md` (319/180/82) y añadir `hdfs` a requirements.  
D. Regenerar pipeline desde `data/procesado` vacío y revalidar gate + pytest (~85).  
E. Iniciar infraestructura: docker-compose HDFS+Mongo, `storage/`, Kafka, análisis, visualización, informe.