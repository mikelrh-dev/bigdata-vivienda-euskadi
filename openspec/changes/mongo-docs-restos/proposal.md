# Proposal: mongo-docs-restos

## Intent

Cuatro restos de texto contradicen el estado medido de MongoDB: 13 colecciones, 8 pipelines, 36 tests Mongo aprobados y 4 robustos (Bilbao 48020 n 173, Donostia 20069 n 113, Getxo 48044 n 40, Vitoria 01059 n 39). La fuente de verdad es brief/RETO 1Evaluacion SBD-BDAv2.pdf; el texto pendiente antiguo queda desechado.

## Scope

### In Scope

- Dashboard: 6 robustos por 4 robustos con nombres y n.
- openspec/project.md: MongoDB fuera de pendientes; HDFS y Kafka quedan pendientes separados.
- Spec presentacion-de-resultados: Estado Pendiente por Hecho alineado con RA4 v2.
- docs/arquitectura_datos.md: enlace a archive/framework_auditoria_completo2/06_readiness_mongo_infra.md.

### Out of Scope

- README.md, storage, analysis, tests y otros docs.
- Regenerar dashboards o datos; cambiar logica de generacion.
- Inventar estado de HDFS o Kafka.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- presentacion-de-resultados: el estado pasa de Pendiente a Hecho alineado con RA4 v2.

## Approach

Edits textuales de una linea en cada fichero, sin cambios de logica. Verificacion con git grep sobre ficheros tracked fuera de archive e historial, mas pytest de Mongo.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| transform/generar_dashboard_completo.py | Modified | Linea 176: 4 robustos con nombres y n |
| openspec/project.md | Modified | Linea 6: MongoDB hecho, HDFS/Kafka pendientes |
| openspec/specs/presentacion-de-resultados/spec.md | Modified | Linea 4: Estado Hecho alineado con RA4 v2 |
| docs/arquitectura_datos.md | Modified | Linea 4: enlace a archive/ |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Tocar ficheros fuera de alcance | Low | Solo los 4 ficheros listados |
| Inventar estado de HDFS/Kafka | Low | Mantener su texto pendiente |
| Enlace archive inexistente | Low | Confirmado con git ls-files |

## Rollback Plan

Revertir las 4 ediciones de una linea; los artefactos SDD quedan en openspec/changes/mongo-docs-restos sin commitear.

## Dependencies

- Estado medido previo: 13 colecciones, 8 pipelines, 36 passed Mongo, 4 robustos.

## Success Criteria

- [ ] git grep de 6 robustos fuera de archive/historial solo deja historial archive.
- [ ] Sin Mongo pendiente en README, arquitectura, modelo, preguntas, project y transform.
- [ ] pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py -q con exit 0.
