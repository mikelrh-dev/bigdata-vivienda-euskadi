# Verificación de estado — fase de datos e infraestructura (2026-11-01)

Verificación read-only. No se modificaron datos ni código.

## 1. Comandos ejecutados y resultados

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | 77 passed, 1.96s |
| `.venv/Scripts/python.exe verificar_fase_datos.py` (raíz) | 15/15 PASS, exit 0 |
| `.venv/Scripts/python.exe transform/run_all.py --check` | exit 1: 7 scripts `DESACTUALIZADO` + 1 `SIN-DECLARAR` |
| `extract/generar_manifest.py --verify` | raw OK (314 entradas, 0 errores); silver FAIL (85 errores) |
| `run_manifest.json` | 35 scripts, todos `rc=0` |

## 2. Estado por WP (fase de datos)

| WP | Estado | Evidencia clave |
|---|---|---|
| WP-01 Orquestador declarativo | Parcial | `transform/run_all.py`: 35 `SCRIPTS` + 7 `EXCLUIDOS`, Kahn, manifest; dry-run exit 0. Falta DoD test `test_run_all_orquesta_todos_los_scripts`. |
| WP-02 Un escritor dim gold | Done | Solo `construir_dim_gold.py` escribe `dim_municipios_enriquecido.csv`. |
| WP-03 `n_anuncios` real | Done | Gate 06: real=759, crudo=843; `aplicar_cobertura_mercado.py`. |
| WP-04 Ceros/clip | Done | `corregir_empleo.py` bruto/flag/mask; gate 07 PASS. |
| WP-05 Brecha eliminada | Done | `brecha_ocupacion_actividad_pct` ausente en gold (gate 08). |
| WP-06 Esfuerzo canónico | Done | `esfuerzo_joven_pct` en base y renta; gate 09 PASS. |
| WP-07 Metadata única | Parcial | `extract/_common.py` valida raw; sidecars en `_meta`; gate 03 59/59. Validación estricta solo en raw; tests dedicados ausentes. |
| WP-08 Manifests | Parcial | Raw verify OK (314). Silver manifest stale: 85 faltantes (`_meta/*`). |
| WP-09 Nombres estables | Parcial | 3 ficheros con timestamp en `data/procesado` (`anuncios_*_20261029_*_normalizado.json`). |
| WP-10 Lectura tipada | Parcial | `transform/` pasa AST test; `extract/` tiene 2 `pd.read_csv` sin `dtype` (`10_scraping_faltantes.py`, `_common.py`). |
| WP-11 Fallback Eustat | Missing | `_ratio_fiscal_desde_eustat()` usa constantes silenciosas; no `flag_ratio_fiscal`. |
| WP-12 Cobertura | Missing | No existe `cobertura_anuncios.csv` ni `nivel_fiabilidad`. |
| WP-13 Higiene/docs | Parcial | `openspec/project.md` stale (314/96/59 vs 319/180/77); `requirements.txt` sin `hdfs`. |
| WP-14 Gate | Done | `verificar_fase_datos.py`: 15/15, exit 0. |
| WP-15 `renta_origen` por fila | Missing | `renta_municipal_completa.csv`: `renta_origen` = `Eustat+INE_Atlas` en 252/252. |
| WP-16 dim fuera de raw | Missing | 7+ extractores siguen leyendo `data/raw/dim_municipios.json`. |
| WP-17 Ingestion manifest | Missing | `data/raw/ingestion_manifest.json` no existe. |
| WP-18 Metadata salario | Missing | `ovj_salario_joven_2024.json` y `emancipacion_juventud_resumen.json` sin bloque `metadata`. |
| WP-19 Archivar auditorías | Done | `openspec/audit/archivado/` (19 docs); vigentes: rev.2, plan, contrauditoría. |
| WP-20 Reglas portables | Done | `docs/reglas_limpieza.md` presente (R1–R7). |

## 3. Problemas estructurales

- Tests: 77 vs ~85 previstos; faltan ~8 tests DoD (WP-01, 07, 08, 09, 10, 11, 12, 13).
- Raw: 59 JSON vs plan 60; sidecars 60 (uno extra).
- `run_all --check`: 7 stale + 1 sin declarar; no cumple criterio “sin faltan salidas”.
- Silver manifest no verifica; 3 nombres con timestamp; 2 lecturas sin `dtype` en `extract/`.
- Documentación de inventario/cifras desactualizada (`AGENT.md`, `openspec/project.md`).

Causa del staleness: reescrituras in-place de `dim_municipios.csv` y `anuncios_unificados.csv` actualizan mtime y vuelven stale a downstream. No es error de datos, pero impide `--check` limpio.

## 4. Estado de infraestructura (fases 2–9)

No existe ninguno de los entregables de infraestructura:

- `storage/`, `analysis/`, `visualization/`, `notebooks/` — ausentes
- `docker-compose.yml`, `plan/arquitectura.md` — ausentes
- `transform/limpieza.py`, `transform/enrich.py` — ausentes (hay scripts equivalentes con otros nombres)

Dependencias:
- `pymongo==4.17.0` y `kafka-python-ng==2.2.3` presentes en `requirements.txt`
- No hay cliente HDFS (`hdfs`/`webhdfs`/`pyhdfs`) en requirements ni instalado
- Docker Desktop + Compose disponibles (docker 29.7.2, compose v5.5.1), pero sin compose file en repo

Specs de almacenamiento/análisis/presentación existen en `openspec/specs/`, todas en estado pendiente.

## 5. Conclusiones

1. La fase de datos está **sustancialmente hecha pero no cerrada al 10/10**: gate 15/15 y pipeline 35/0, pero faltan WP-11, WP-12, WP-15, WP-16, WP-17, WP-18 y varios tests DoD.
2. La reproducibilidad del pipeline es **funcional** (ejecución completa sin fallos), pero **no verificable con `--check`** por staleness estructural de reescrituras in-place.
3. La infraestructura (HDFS, Kafka, MongoDB, análisis, visualización, informe) **no ha empezado**: no hay módulos, compose ni notebooks. Las dependencias Python necesarias sí están declaradas (salvo cliente HDFS).
4. Antes de pasar a infraestructura, conviene cerrar los WP faltantes de datos y resolver el `--check` para dejar un punto de partida limpio.

## 6. Próximos pasos recomendados

A. Cerrar trazabilidad de datos: WP-17, WP-15, WP-18, WP-12, WP-16, WP-11.  
B. Actualizar `openspec/project.md` y `AGENT.md` con cifras reales (316/180/77).  
C. Resolver staleness estructural de `run_all --check` (reordenar dependencias o tocar salidas downstream).  
D. Regenerar pipeline desde `data/procesado` vacío y revalidar gate + pytest (~85).  
E. Solo entonces iniciar infraestructura: docker-compose HDFS+Mongo, `storage/`, Kafka, análisis, visualización, informe.