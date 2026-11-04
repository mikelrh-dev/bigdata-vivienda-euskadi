# Design: mongo-docs-restos

## Technical Approach

Cuatro ediciones textuales de una linea, una por fichero, sin tocar logica. Cada edicion sustituye solo el fragmento obsoleto y conserva el resto de la linea. La verificacion usa git grep sobre tracked (excluye data/resultados gitignored generados) y pytest acotado a Mongo.

## Architecture Decisions

| Decision | Alternativas | Tradeoff | Eleccion |
|----------|--------------|----------|----------|
| Dashboard linea 176 | Solo cambiar 6 por 4 / reescribir tabla | Reescribir rompe formato de tabla | Solo el texto de la celda: 4 robustos con nombres y n |
| project.md linea 6 | Añadir frase nueva / editar la existente | Frase nueva duplica estado | Editar la frase: HDFS/Kafka pendientes, MongoDB hecho |
| Spec Estado | Hecho / Alineado con RA4 v2 | Una sola palabra pierde contexto RA4 | Hecho, alineado con RA4 v2 |
| Enlace arquitectura | Quitar enlace / corregir ruta | Quitar pierde trazabilidad | Corregir a archive/, confirmado con git ls-files |

## Data Flow

Texto obsoleto -> edicion de una linea -> git grep + pytest Mongo -> verify-report.md

## File Changes

| File | Action | Description |
|------|--------|-------------|
| transform/generar_dashboard_completo.py | Modify | Linea 176: 4 robustos con nombres y n |
| openspec/project.md | Modify | Linea 6: MongoDB fuera de pendientes |
| openspec/specs/presentacion-de-resultados/spec.md | Modify | Linea 4: Estado Hecho RA4 v2 |
| docs/arquitectura_datos.md | Modify | Linea 4: enlace a archive/ |

## Interfaces / Contracts

Ninguna interfaz nueva. Sin cambios de API, esquema ni datos.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Grep | 6 robustos y Mongo pendiente | git grep tracked fuera de archive/historial |
| Unit/Integration | Mongo geo y comparativa | .venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py -q |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required.

## Open Questions

None.
