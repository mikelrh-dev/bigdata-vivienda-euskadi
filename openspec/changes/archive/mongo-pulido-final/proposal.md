# Proposal: mongo-pulido-final

## Intent

Cerrar la pulido final de MongoDB y presentación: el generador de dashboard ya dice 4 robustos, pero el HTML sin regenerar y los documentos OpenSpec aún dicen 6 robustos y Mongo pendiente. La documentación y el dashboard deben reflejar el estado real medido.

## Scope

### In Scope

- Regenerar PNGs con `transform/generar_dashboard_completo.py` y corregir la línea 96 de `data/resultados/dashboard_completo.html` a 4 robustos con nombres y n.
- `openspec/project.md`: quitar análisis pendientes de la línea 6 y marcar hechos MongoDB, Aggregation Pipeline y Fase 3 (líneas 30, 31, 79).
- `openspec/specs/mongodb-y-analisis/spec.md` línea 4: Estado Pendiente a Hecho, alineado con RA3 e INDICES-01 y TRANSACCIONES-01.
- Artefactos SDD en `openspec/changes/mongo-pulido-final/`.

### Out of Scope

- No inventar HDFS ni Kafka como hechos: siguen pendientes en project.md.
- No tocar README.md, storage/*, analysis/*, transform/* (salvo ejecutar el generador) ni tests/*.
- No commit.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `mongodb-y-analisis`: estado Pendiente a Hecho (RA3, INDICES-01, TRANSACCIONES-01).
- `presentacion-de-resultados`: dashboard con 4 robustos, sin 6 robustos.

## Approach

Ejecutar el generador existente (ya corregido a 4 robustos en la línea 176) para regenerar los PNGs, corregir la conclusión O2 del HTML que el generador no emite, y alinear los dos documentos. Verificar con grep y pytest reales.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `data/resultados/dashboard_completo.html` | Modified | Línea 96: 6 a 4 robustos |
| `openspec/project.md` | Modified | Líneas 6, 30, 31, 79 |
| `openspec/specs/mongodb-y-analisis/spec.md` | Modified | Línea 4: Estado Hecho |
| `openspec/changes/mongo-pulido-final/` | Create | proposal, specs, design, tasks, verify-report |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| El generador no emite HTML y la corrección es manual | High | Editar solo la línea 96 dentro de los ficheros permitidos y reportarlo |
| Inventar HDFS/Kafka como hechos | Med | No tocar filas 28, 29, 76, 78 de project.md |

## Rollback Plan

Revertir los 3 ficheros con git checkout sobre esos paths y borrar `openspec/changes/mongo-pulido-final/`. Los PNGs regenerados son salidas deterministas del script.

## Dependencies

- `.venv/Scripts/python.exe` con duckdb y matplotlib para el generador.
- MongoDB accesible para los tests de geo y comparativa.

## Success Criteria

- [ ] grep sin 6 robustos en el HTML y en project.md.
- [ ] grep sin Mongo pendiente en project.md.
- [ ] pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py exit 0.
