# Design: mongo-orquestador-analisis

## Technical Approach

`analysis/run_analisis_mongo.py` importa los 8 pipelines a nivel de modulo y los resuelve por nombre desde `globals()` para permitir monkeypatch. `run_all_estandar()` ejecuta los 8 en orden fijo y devuelve dict nombre->filas. `huella_resultados` serializa con `json.dumps(..., sort_keys=True, default=...)` tras convertir `Decimal128` a texto numerico, y calcula SHA-256. `main` ejecuta dos veces, compara huellas, exporta 3 CSV con `csv.DictWriter` y `utf-8-sig` (contrato de encoding del proyecto), e imprime conteos y huella. strict_tdd es false: modo estandar.

## Architecture Decisions

| Opcion | Tradeoff | Decision |
|--------|----------|----------|
| Resolucion por `globals()` | Dict fijo de funciones impediria monkeypatch por nombre | Elegida: orden fijo como tupla de nombres, resolucion en tiempo de llamada |
| Huella SHA-256 sobre JSON ordenado | `repr` de dicts depende del orden de claves | Elegida: `sort_keys=True` y conversion explicita de `Decimal128` |
| Exportacion con union de claves | Usar solo claves de la primera fila perderia columnas raras | Elegida: union en orden de primera aparicion; hoy las claves son uniformes |
| `utf-8-sig` en CSV | Sin BOM rompe el contrato de CSV del proyecto | Elegida: `utf-8-sig` en escritura y lectura de tests |
| Orden canonico de filas | Varios `$sort` tienen una sola clave y MongoDB no ordena empates: dos ejecuciones reproducibles daban huellas distintas | Elegida: ordenar filas por serializacion ordenada en `run_all_estandar`, sin tocar los pipelines |

## Data Flow

    main -> run_all_estandar (8 pipelines en orden) -> huella1
         -> run_all_estandar -> huella2 == huella1 ?
         -> exportar_tres_csv (3 CSV) -> print conteos + huella

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `analysis/run_analisis_mongo.py` | Create | `run_all_estandar`, huella, `exportar_tres_csv`, `main` |
| `tests/test_mongo_orquestador.py` | Create | Orquestador en `tmp_path` y preparacion con cabeceras |
| `openspec/changes/mongo-orquestador-analisis/` | Create | proposal, spec, design, tasks, verify-report |

## Interfaces / Contracts

`run_all_estandar() -> dict[str, list[dict]]`: 8 claves en orden fijo. `huella_resultados(resultados) -> str`: SHA-256 hex. `exportar_tres_csv(resultados, out_dir) -> dict[str, Path]`: 3 ficheros. `main(argv=None) -> int`: 0 si huella coincide y exporta, 1 si difiere. CSV: `mongo_esfuerzo_por_municipio.csv` desde `pipeline_indicadores_municipio`, `mongo_alquiler_por_municipio.csv` desde `pipeline_alquiler_por_municipio`, `mongo_modalidades.csv` desde `pipeline_modalidades`.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Integracion real | Orquestador exporta 3 ficheros y reproduce conteos | `test_orquestador_analisis_exporta_tres_conjuntos`: ejecuta en `tmp_path`, aserta 3 ficheros y misma `n` en dos ejecuciones |
| Integracion real | Cabeceras y coincidencia con memoria | `test_preparacion_visualizacion_tres_conjuntos`: lee CSV con `csv.DictReader`, compara cabecera y conteo con pipelines en memoria |
| Runtime real | Script completo contra MongoDB | `.venv/Scripts/python.exe -m pytest tests/test_mongo_orquestador.py tests/test_mongo_geo.py -q` |

## Threat Matrix

N/A — no hay routing, shell, subprocess, VCS/PR automation, clasificacion de ejecutables ni process integration. El modulo solo invoca funciones Python existentes y escribe CSV.

## Migration / Rollout

No migration required. Solo lectura de MongoDB y escritura de CSV en `data/resultados/`.

## Open Questions

- Ninguna.
