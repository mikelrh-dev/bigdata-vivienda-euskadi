# Auditoría de residuos DuckDB y basura — 2026-11-09

**Alcance:** árbol completo del proyecto, archivo por archivo.  
**Resultado:** no hay bases `.duckdb`, `.db` ni `.wal`; quedan **6 artefactos que todavía ejecutan o importan DuckDB**, además de referencias históricas y documentación.  
**Acción:** esta auditoría es de solo lectura. No se ha borrado ni movido nada.

## Veredicto rápido

- **No existe una carpeta `legacy/`.** El área legacy real es `archive/`, `docs/archive/` y `openspec/changes/archive/`; `requirements-legacy.txt` es solo un fichero de dependencias.
- **El residuo más grave no es un script viejo:** `tests/test_fuentes_validacion.py` ejecuta `scripts/validar_fuentes_nuevas.py`, que hace `import duckdb`. `duckdb` no está en `requirements.txt` ni en `uv.lock`; el test pasa solo porque sigue instalado en `.venv`.
- **4 scripts legacy de DuckDB** siguen fuera de `archive/`: `launch_duckdb_ui.py`, `auditoria_duckdb.py`, `generar_dashboard_visual.py` y `generar_dashboard_completo.py`.
- **README sigue invocando dos de esos scripts** en el paso 5. En un entorno limpio, ese paso falla.
- **1.511 rutas auditadas**, 625 versionadas y 886 no versionadas; **1,19 GB**. Se generó una fila por ruta.
- **136 candidatos** (12,0 MB): 100 artefactos generados, 10 backups históricos, 5 scripts de scratch, 4 residuos DuckDB, 2 activos, 2 duplicados y el resto documentación/decisiones.
- **No se tocó** `data/raw`, `data/procesado`, Mongo, HDFS, Kafka, `.env` ni `api.txt`.

## 1. DuckDB: qué queda de verdad

### 1.1. Artefactos que ejecutan o importan DuckDB

| Fichero | Tipo | Estado | Riesgo | Acción propuesta |
|---|---|---|---|---|
| `tests/test_fuentes_validacion.py` | test activo | Ejecuta el script de validación | **Alto**: dependencia oculta; falla en instalación limpia | Borrar o reescribir el test y el script; no mantener una prueba de una decisión cerrada |
| `scripts/validar_fuentes_nuevas.py` | one-off 2026-11-04 | `import duckdb`; valida 3 fuentes candidatas | **Alto**: su test está en la suite, pero `duckdb` no está declarado | Migrar a `csv`/`pandas` si se quiere conservar, o mover a `archive/` y sacar el test |
| `scripts/launch_duckdb_ui.py` | lanzador local | Ignorado por git, sin referencias | Medio: arranca una UI y mantiene el proceso vivo | **Borrar**; es local y no aporta al pipeline |
| `transform/auditoria_duckdb.py` | auditoría one-off | Escribe `scratchpad/auditoria_duckdb.md` | Medio: no está en el DAG, pero sigue en `transform/` | Mover a `archive/legacy_duckdb/` o borrar |
| `transform/generar_dashboard_visual.py` | dashboard legacy | 5 gráficos con `duckdb.query` sobre CSV | Medio: ya no es la fuente de evidencia | Mover a `archive/legacy_duckdb/`; actualizar README |
| `transform/generar_dashboard_completo.py` | dashboard legacy | 8 gráficos; incluye literales antiguos (173/113/40) | Medio: puede confundirse con evidencia | Mover a `archive/legacy_duckdb/`; actualizar README y `docs/README.md` |

**Comprobación de la dependencia oculta**

```text
Entorno actual:              pytest tests/test_fuentes_validacion.py -> 1 passed
requirements.txt:            sin duckdb
requirements-legacy.txt:     duckdb==2.0.0
uv.lock:                     sin duckdb
Simulación sin duckdb:       pytest tests/test_fuentes_validacion.py -> 1 failed
```

La simulación se hizo con un `duckdb.py` temporal en `PYTHONPATH` que lanza `ModuleNotFoundError`; no se tocó `.venv` ni el repositorio. Es la prueba de que el test verde actual no es reproducible desde cero.

### 1.2. Ficheros que solo mencionan DuckDB

| Fichero | Qué hace | Decisión |
|---|---|---|
| `README.md` | Paso 5 invoca `generar_dashboard_visual.py` y `generar_dashboard_completo.py`; además cita la cifra histórica de DuckDB | **Editar**: sustituir por `analysis/run_analisis_mongo.py` o retirar el paso legacy |
| `transform/run_all.py` | `EXCLUIDOS` contiene `auditoria_duckdb.py` y los dos dashboards | **Editar** después de moverlos |
| `.gitignore` | Ignora `launch_duckdb_ui.py`, `scratchpad/auditoria_duckdb.md` y `scratchpad/*.py` | **Editar** solo cuando se borren los ficheros |
| `analysis/run_analisis_mongo.py` | Docstring: «sin DuckDB» y «dejar atrás esa dependencia» | **Editar opcional**; no es código muerto |
| `docs/guion_defensa.md` | «antes 12 únicos / 13 emitidos de DuckDB» | **Editar opcional**; es una traza histórica |
| `docs/pendiente_duckdb_pymongo_2026-11-05.md` | Documento de deuda ya resuelta | **Mover a `docs/archive/2026-11/`** o borrar |
| `requirements-legacy.txt` | `duckdb==2.0.0` | **Conservar mientras exista el archivo legacy**; borrar al final |
| `docs/README.md`, `docs/auditoria_10_10_SDD_2026-11-05.md`, `docs/analisis_vault_vs_rubrica.md` | Referencian los dashboards/literales legacy | **Revisar**: no son basura, pero están desalineados |
| `data/resultados/dashboard.html`, `dashboard_completo.html` | HTML manuales con mención histórica | **Conservar** como artefacto de presentación; no son código |
| `docs/archive/**`, `openspec/audit/**`, `openspec/changes/archive/**`, `vaultVivienda/**` | Referencias históricas o fuera del repo | **Conservar**; no forman parte de la limpieza |

**Conteo:** 61 ficheros contienen la cadena `duckdb`; 25 están en `openspec/` histórico, 16 en `docs/` (14 de ellos en `docs/archive`), 5 en el vault ignorado, 3 en la caché de Graphify y 2 en `data/resultados`. El detalle está en `duckdb_referencias.csv`.

### 1.3. Orden de limpieza recomendado

1. **Cortar la dependencia oculta:** mover `validar_fuentes_nuevas.py` y su test a `archive/` o reescribirlos sin DuckDB. Es el único cambio que afecta a la reproducibilidad de la suite.
2. **Sacar los 4 legacy de la zona activa:** `launch_duckdb_ui.py` se borra; los otros tres se mueven a `archive/legacy_duckdb/`.
3. **Actualizar referencias:** `README.md`, `transform/run_all.py`, `.gitignore`, `docs/README.md` y el guion.
4. **Mover la documentación resuelta:** `docs/pendiente_duckdb_pymongo_2026-11-05.md` a `docs/archive/2026-11/`.
5. **Borrar `requirements-legacy.txt`** solo si ya no queda ningún script legacy que conservar.

No conviene borrar `requirements-legacy.txt` antes de decidir si los dashboards se archivan o se eliminan: si se archivan, el archivo puede seguir siendo la dependencia del kit legacy.

## 2. Otra basura fuera de legacy

### 2.1. Borrado local seguro (no versionado o generado)

| Ruta | Ficheros | Tamaño | Motivo |
|---|---:|---:|---|
| `graphify-out/` | 67 | 1,26 MB | Caché AST de Graphify, ignorada; se regenera |
| `demo-kpi/` y `demo-mapa/` (solo `.hyperframes/`, `renders/`, `out.mp4`) | 30 | 8,86 MB | Render local ignorado; los GIF/WebP versionados se conservan |
| `logs/raw_guard_audit.log` | 1 | 13,6 KB | Log regenerable; `_raw_guard` lo vuelve a crear |
| `scratchpad/build_mapa.py` | 1 | 31,9 KB | Prototipo local; el activo es `transform/generar_mapa_esquema.py` |
| `scratchpad/check_mapa.py`, `check_mapa2.py` | 2 | 6,4 KB | Comprobaciones one-off sin referencias |
| `scratchpad/mapa_norm.json` | 1 | 43,2 KB | Salida intermedia del prototipo de mapa |
| `scratchpad/sha1.txt`, `sha2.txt` | 2 | 1,4 KB | Duplicados byte a byte; no referenciados |
| `.atl/` | 2 | 32,3 KB | Caché del registro de skills; no es fuente |
| `.freebuff/project-id` | 1 | 37 B | Metadato del agente; no es fuente |

**Total de borrado local seguro:** unos **10,2 MB**, sin tocar código versionado ni datos.

### 2.2. Archivar, no borrar sin decisión

| Ruta | Ficheros | Tamaño | Por qué no borrar directamente |
|---|---:|---:|---|
| `scratchpad/backup_t3prev/` | 5 | 923 KB | Backup previo a T3; versionado y útil para trazabilidad |
| `scratchpad/p1-1_backup_2026-11-07/` | 5 | 662 KB | Backup de silver citado en un cambio archivado; uno de sus CSV es idéntico al actual |
| `scratchpad/prototipo_pisos_ubicacion.py` | 1 | 12,4 KB | Prototipo citado en las tareas del cambio de pisos; ya hay flujo transform/test |
| `notebooks/Kafka_Ejercicio.ipynb` | 1 | 18,3 KB | Ejercicio de pedidos HDFS/Kafka ajeno al proyecto; versionado, sin referencias |
| `docs/pendiente_duckdb_pymongo_2026-11-05.md` | 1 | 1,2 KB | Documento resuelto; mejor a `docs/archive/2026-11/` |

Los backups de `scratchpad` no son «basura» en el sentido de archivos temporales: están versionados y uno está citado en un `archive-report`. Si no se necesita trazabilidad, se pueden borrar; si se quiere conservar, deben salir de `scratchpad/` y entrar en `archive/`.

### 2.3. Lo que no hay que tocar

- `data/raw/**` — 356 ficheros, raw inmutable.
- `data/procesado/**`, `data/resultados/**` — datos y artefactos de análisis.
- `archive/**`, `docs/archive/**`, `openspec/audit/**`, `openspec/changes/archive/**` — histórico/legacy deliberado.
- `demo-kpi/kpi.gif`, `kpi.webp`, `demo-mapa/mapa.gif`, `mapa.webp` — assets que usa el README.
- `brief/**` — PDF/DOCX del reto.
- `.env`, `api.txt` — secretos ignorados; no se leyó su contenido.
- `vaultVivienda/**` — vault ignorado, fuera del repositorio.
- `docs/presentacion/index.template.html` — plantilla fuente, no un «template» residual.
- `transform/construir_dim_gold.py` — el patrón `old` venía de **gold**, no de un archivo viejo.

## 3. Auditoría archivo por archivo

Se recorrieron **1.511 rutas** (el propio script de inventario incluido); cada una tiene tamaño, SHA-256, extensión, si está versionada, área, líneas con `duckdb`, tipo y veredicto.

- `inventario_archivo_por_archivo.csv` — **1.511 filas**, 12 columnas. Es el listado completo.
- `candidatos_limpieza.csv` — **136 filas** que no son «conservar».
- `duckdb_referencias.csv` — **61 filas** con la cadena `duckdb`.
- `candidatos_por_tipo.csv` — recuento por tipo.
- `resumen_inventario.json` — totales y grupos de duplicados.

**Reparto de los 1.511 ficheros:** 625 versionados, 886 no versionados; 1.186.976.024 bytes. Se excluyeron `.git/`, `.venv/`, `__pycache__/` y `.pytest_cache/` del recorrido, porque no son contenido del proyecto.

**Cobertura real:** todos los ficheros de texto se escanearon para `duckdb`; los binarios, ZIP, PDF, imágenes y vídeos se inventariaron y hashearon, no se interpretaron semánticamente. Los secretos (`.env`, `api.txt`) no se abrieron.

## 4. Comprobaciones

| Check | Resultado |
|---|---|
| `pytest tests/test_fuentes_validacion.py -q` | 1 passed en el entorno actual |
| Mismo test con DuckDB bloqueado en `PYTHONPATH` | **1 failed**: `ModuleNotFoundError: No module named duckdb` |
| `duckdb` en `requirements.txt` | No |
| `duckdb` en `uv.lock` | No |
| `duckdb` solo en `requirements-legacy.txt` | Sí, `duckdb==2.0.0` |
| Bases `.duckdb` / `.db` / `.wal` | 0 |
| `git status` | Solo los cambios previos del usuario y los artefactos de auditoría; sin cambios de código en esta sesión |

## 5. Límites

- No se ha ejecutado una instalación limpia completa; la dependencia oculta se demostró aislando el import de DuckDB.
- No se han abierto binarios, ZIP, PDF, imágenes ni vídeos; se clasificaron por ruta, extensión, tamaño y hash.
- No se ha leído el contenido de `.env` ni `api.txt` por seguridad.
- No se ha borrado, movido ni renombrado nada. Las acciones de la tabla son propuestas.

**Recomendación inmediata:** empezar por `validar_fuentes_nuevas.py` + `test_fuentes_validacion.py`, porque es el único residuo DuckDB que hoy forma parte de la suite y el que rompería una instalación limpia. Después, sacar los cuatro scripts legacy y actualizar README/run_all.
