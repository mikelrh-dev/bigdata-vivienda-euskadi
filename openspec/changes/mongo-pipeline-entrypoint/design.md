# Design: mongo-pipeline-entrypoint

## Technical Approach

El script `scripts/run_mongo_pipeline.py` inserta la raíz del repo en `sys.path`, importa `load_all`, `clean_all`, `ensure_indexes`, `pipeline_indicadores_municipio` y `ping` a nivel de módulo (la importación valida dependencias sin conectar). `main(argv=None)` usa `argparse` con `--dry-run`: en dry-run solo comprueba `ping()` y vuelve sin llamar a las cuatro funciones; fuera de dry-run las llama en el orden fijo y suma recursivamente `modified_count` y `deleted_count` del dict anidado de `clean_all`. El test carga el módulo por ruta con `importlib.util.spec_from_file_location`, sustituye las cuatro funciones y `ping` por dobles con monkeypatch y comprueba orden. strict_tdd es false según `openspec/config.yaml`: modo estándar, test escrito junto a la implementación y ejecutado con runtime real.

## Architecture Decisions

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| Imports a nivel de módulo | Importar en `main` ocultaría errores de import en dry-run y el test no podría parchear símbolos del módulo | Elegida: imports arriba; dry-run valida imports por el hecho de haber importado |
| `sys.path.insert(0, ROOT)` | Ejecutar `python scripts/run_mongo_pipeline.py` pone `scripts/` como `sys.path[0]`, no la raíz | Elegida: inserción explícita antes de importar `storage`/`analysis` |
| Suma recursiva de contadores | `clean_all` devuelve dict anidado con `modified_count`/`deleted_count` en muchos nodos, sin total directo | Elegida: recorrido recursivo que suma ambas claves en cualquier nivel |
| Test por `importlib` desde ruta | `scripts/` no es paquete y no hay `conftest.py` que ajuste `sys.path` | Elegida: carga por ruta y monkeypatch de los símbolos del módulo |

## Data Flow

    main(argv) -> --dry-run? -> ping() -> exit 0
               -> load_all() -> clean_all() -> ensure_indexes() -> pipeline_indicadores_municipio()
               -> print(load_all, modified_count, deleted_count, número indicadores)

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `scripts/run_mongo_pipeline.py` | Create | `main` con cadena en orden, conteos y `--dry-run` con ping |
| `tests/test_mongo_pipeline.py` | Create | `test_pipeline_entrypoint_existe` y `test_dry_run_no_muta_prod` con monkeypatch |
| `openspec/changes/mongo-pipeline-entrypoint/` | Create | proposal, delta spec, design, tasks, verify-report |

## Interfaces / Contracts

`main(argv=None) -> int`: exit 0 en éxito, 1 si el ping falla en dry-run. Imprime `load_all`, `modified_count`, `deleted_count` y número de indicadores en ejecución normal; en dry-run imprime estado de imports y ping sin llamar a las funciones de carga. Las cuatro funciones se importan como símbolos del módulo para permitir monkeypatch: `load_all`, `clean_all`, `ensure_indexes`, `pipeline_indicadores_municipio`, más `ping`.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit/integration con mock | Orden de llamada y conteos impresos | `test_pipeline_entrypoint_existe`: espías, asserts de orden, conteo productivo lector antes y después |
| Unit con mock | Dry-run no muta | `test_dry_run_no_muta_prod`: espías con `assert not called`, `ping` parcheado a True |
| Runtime real | Dry-run contra MongoDB en marcha | `.venv/Scripts/python.exe scripts/run_mongo_pipeline.py --dry-run`, exit code y salida reales |

## Threat Matrix

N/A — no hay routing, shell, subprocess, VCS/PR automation, clasificación de ejecutables ni process integration. El script solo invoca funciones Python existentes en el mismo proceso.

## Migration / Rollout

No migration required. La base productiva no se toca en esta ronda: la ejecución completa queda para el operador tras esta verificación.

## Open Questions

- Ninguna.
