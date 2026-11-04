# Design: mongo-pulido-final

## Technical Approach

Regenerar las salidas con el generador existente y alinear la documentación con el estado medido. El generador ya contiene la corrección de 4 robustos (línea 176); el HTML de conclusiones no lo emite ningún script, así que su línea 96 se corrige a mano dentro de los ficheros permitidos.

## Architecture Decisions

| Decision | Tradeoff | Choice |
|----------|----------|--------|
| Regenerar PNGs vs editar el HTML completo | El HTML no tiene fuente generadora; reescribirlo entero inventaría estructura | Ejecutar el script y editar solo la línea 96 del HTML |
| Marcar HDFS/Kafka como hechos | Sería falso: las filas 28 y 29 siguen pendientes y no hay evidencia nueva | No tocar HDFS ni Kafka; solo MongoDB y Aggregation |
| Editar la spec completa vs el encabezado | La spec ya describe los requisitos reales; solo el estado está desfasado | Cambiar únicamente la línea 4 a Estado Hecho |

## Data Flow

```
transform/generar_dashboard_completo.py (línea 176: 4 robustos)
        │ ejecuta con .venv/Scripts/python.exe
        ▼
data/resultados/*.png (8 PNGs del bloque A-G)
        │
        ▼
data/resultados/dashboard_completo.html línea 96 (corrección manual: 6 → 4 robustos)
        │
        ▼
openspec/project.md + openspec/specs/mongodb-y-analisis/spec.md (estado alineado)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `data/resultados/dashboard_completo.html` | Modify | Línea 96: 6 robustos a 4 robustos con n |
| `openspec/project.md` | Modify | Líneas 6, 30, 31, 79 |
| `openspec/specs/mongodb-y-analisis/spec.md` | Modify | Línea 4: Estado Hecho |
| `openspec/changes/mongo-pulido-final/` | Create | proposal, specs, design, tasks, verify-report |

## Interfaces / Contracts

Sin cambios de interfaz. Solo texto de estado en documentos y una fila de conclusión en el HTML.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit/integration | grep sin 6 robustos en HTML y project; grep sin Mongo pendiente en project | grep real con exit code |
| Integration | tests/test_mongo_geo.py y tests/test_mongo_comparativa.py | `.venv/Scripts/python.exe -m pytest ... -q`, exit 0 |
| Runtime | El generador produce los PNGs | Ejecutar `transform/generar_dashboard_completo.py` y contar salidas |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required.

## Open Questions

Ninguna bloqueante. Nota: el docstring del generador dice que guarda PNGs y dashboard.html, pero el script solo genera PNGs; la corrección del HTML es manual y queda documentada en el verify-report.
