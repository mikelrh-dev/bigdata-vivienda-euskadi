# Design: Fase 1 — Obtención y procesado de datos

## Decisiones

### D1 — Universo trifinario
- **Elegido**: Trifinario (CAE → comarca → municipio robusto).
- **Rechazado**: Solo municipios con dato oficial (excluye 93 comarcales).
- **Razón**: Responde las 4 preguntas del PDF sin sobrevender.

### D2 — Población joven
- **Elegido**: Verificar INE Padrón Continuo primero. Si existe → incorporar; si no → fallback Eustat y eliminar Pipeline 3.
- **Rechazado**: Usar solo Eustat (grupos 0-19/20-64) sin verificar INE.
- **Razón**: Evita dependencia silenciosa; documenta el alcance real.

### D3 — Pisos geo
- **Elegido**: Flag `geo_invalida=True` + excluir de geo; usar para precio por municipio de búsqueda.
- **Rechazado**: Mapear barrio → municipio (error añadido).
- **Razón**: Honestidad analítica; no inventar geo.

### D4 — Dedup
- **Elegido**: Generar `property_fingerprint` (sha256) en JSON. No upsert aún.
- **Rechazado**: Upsert directo en Mongo (eso es Fase 3).
- **Razón**: Preparación sin infraestructura.

### D5 — Raw inmutable
- **Elegido**: Revertir in-place; congelar `data/raw/`; escribir solo en `data/procesado/`.
- **Rechazado**: Normalizar en raw (ya pasó, rompe HDFS).
- **Razón**: HDFS necesita originales tal cual.

### D6 — Fórmula canónica
- **Elegido**: `esfuerzo_joven_pct = alquiler_anual / renta_joven_estimada × 100`. Solo documentar.
- **Rechazado**: Calcular en Pandas (roba protagonismo a Mongo).
- **Razón**: Mongo es la unión definitiva.

### D7 — Fuentes nuevas
- **Elegido**: No perseguir; cerrar gaps con lo que hay. Excepción: verificar D2.
- **Rechazado**: Buscar Idealista/OSM (bloqueados).
- **Razón**: Priorizar cierre de gaps con datos existentes.

## Arquitectura de datos (Fase 1)

```mermaid
flowchart LR
    accTitle: Flujo de datos Fase 1
    accDescr: Extract → Normalize → Prepare → Freeze
    A[Extract\nscripts 01-21] --> B[Normalize\ndata/procesado/]
    B --> C[Prepare\nfingerprint + geo flag]
    C --> D[Freeze\ndata/raw inmutable]
    D --> E[Ready for\nHDFS + Kafka + Mongo]
```

## Limitaciones conocidas
- D2 puede no existir (INE Padrón Continuo municipal por edad quinquenal).
- Los originales de `data/raw/` fueron reescritos in-place; puede que no haya backup.
- Contradicciones internas (números distintos) deben reconciliarse antes de congelar.
- Reproducibilidad no verificada (requirements.txt incompleto).
