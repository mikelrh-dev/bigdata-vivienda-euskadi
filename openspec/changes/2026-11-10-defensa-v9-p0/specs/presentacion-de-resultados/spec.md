# Delta for Presentación de resultados

## MODIFIED Requirements

### Requirement: CONCLUSION-01 — Guion Tema 8 de 1 página con 10 criterios, terminología y cifras verificables

El sistema SHALL redactar en `docs/guion_defensa.md` un guion Tema 8 de 1
página centrado en embedding, índices y atomicidad, con la cadena offline
HDFS centro + Kafka pid 1832. SHALL documentar los 10 criterios y las lagunas,
y MUST NOT dejar 16-29 sin marcar: 16-29 SHALL marcarse legacy y el canónico
es 18-34. El modelo SHALL describirse con terminología correcta: **embedding**
de demografía/empleo/demanda social en `municipios`; **referencing** por
`codigo_ine` para `anuncios` y `etxebide_promociones`. No se sobrecorrige
`docs/guion_defensa_12min.md:144`, que ya es correcta. Las cifras SHALL ser
verificables: `anuncios` 594 (nunca 759 como vigente), explain IXSCAN real con
el filtro documentado (`20069` → 1 doc; `48020` → 8; `48001` → 0), 24 índices
en 16 colecciones vivas tras restaurar, 235 passed + 2 skipped, 11 pipelines y
8 CSV. La cadena offline SHALL limitarse a lectura de HDFS centro y MUST
NOT tocar `data/raw` ni raw HDFS, ni crear carpeta nueva, ni subir procesado;
prod intacta por defecto (solo lectura o test con
`MONGO_ALLOW_DESTRUCTIVE=1`).
(Previously: guion con terminología de embedding aplicada a anuncios y cifras
sin verificar (IXSCAN 1, 759, 10 pipelines, 14 colecciones).)

#### Scenario: Guion de 1 página con cadena actual

- GIVEN `docs/guion_defensa.md`
- WHEN se revisa el guion Tema 8
- THEN tiene 1 página con embedding, índices, atomicidad y HDFS centro + Kafka pid 1832
- AND constan los 10 criterios y las lagunas documentadas
- AND el modelo usa embedding en `municipios` y referencing por `codigo_ine` para `anuncios`/`etxebide_promociones`

#### Scenario: Cifras verificables y sin 759 vigente

- GIVEN el guion y el estado real (Mongo, HDFS, docs)
- WHEN se contrasta cada cifra con `grep` y sondas read-only
- THEN 594, IXSCAN con filtro `20069`/`48020`, 24 índices, 235+2, 11 pipelines y 8 CSV coinciden con la evidencia
- AND ninguna cifra errónea (759/10/14/177/24 sin contexto) queda como vigente

#### Scenario: 16-29 marcado legacy

- GIVEN el guion Tema 8 y la matriz O1-O4
- WHEN aparece el rango 16-29
- THEN está marcado legacy y el canónico es 18-34
- AND ninguna conclusión usa 16-29 como rango canónico

## Nota de alcance (pendiente, fuera de este cambio)

Las contradicciones pre-existentes siguen abiertas (C-2,
`openspec/audit/v9_2026-11-10/verificacion_rubrica_fixes.md:97-102`):
`openspec/project.md:38` (Kafka→Mongo), `openspec/project.md:30` (Docker
Desktop) y `docs/guion_defensa.md:5` (HDFS/Kafka como disponibles). Este
cambio no las resuelve; el barrido P1 deberá ampliarse en una ronda posterior.
