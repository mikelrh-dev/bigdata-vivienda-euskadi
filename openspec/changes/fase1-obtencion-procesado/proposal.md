# Propuesta: Fase 1 — Obtención y procesado de datos (sin infraestructura)

## Objetivo
Transformar el corpus actual en un conjunto de datos listo para las fases HDFS + Kafka + Mongo + análisis + presentación, con un método canónico único y defensible. Mongo será la herramienta de unión definitiva; Pandas solo normaliza y prepara.

## Alcance
- Fase 1 del plan maestro: saneamiento, consolidación, definición canónica de KPIs, contratos de integración.
- NO incluye HDFS, Kafka, Mongo, Aggregation, gráficos, informe, demo.

## Decisiones de diseño (D1-D7)
- D1: Universo trifinario (CAE → comarca → municipio robusto).
- D2: Verificar INE Padrón Continuo (municipio, 15-29). Si existe → usar; si no → fallback Eustat y eliminar Pipeline 3.
- D3: Flag `geo_invalida=True` en Pisos (235/235). Excluir de geo; usar para precio por municipio de búsqueda.
- D4: Generar `property_fingerprint` en `anuncios_unificados.json` (sha256). No upsert aún.
- D5: Revertir in-place: mover corrección de `codigo_ine` a `data/procesado/`. Congelar `data/raw/`.
- D6: Fórmula canónica: `esfuerzo_joven_pct = alquiler_anual / renta_joven_estimada × 100`. Solo documentar.
- D7: No perseguir fuentes nuevas; cerrar gaps con lo que hay. Excepción: verificar D2.

## Artefactos a crear
- `docs/metodologia.md` — fuente única de verdad (universo, KPIs, fuentes, vintage, sesgos).
- `openspec/specs/almacenamiento-y-streaming/spec.md` — layout HDFS + Kafka (solo documentar).
- `openspec/specs/mongodb-y-analisis/spec.md` — modelo 6 colecciones (campos exactos, _id, índices, 4 pipelines).
- `openspec/specs/presentacion-de-resultados/spec.md` — 40 preguntas → 3 gráficos → 4 figuras → conclusión.
- `config/parametros_estudio.yaml` — fórmulas, umbrales, n_min=30, pesos, vintage.

## Criterios de salida
- Un solo método/fórmula documentado.
- Cero contradicciones entre docs.
- `data/raw/` inmutable (congelado).
- `data/procesado/` con todos los datos normalizados, fingerprint, flag geo.
- Contratos documentados (no implementados).
- `requirements.txt` completo.
- Reproducibilidad verificada (clon limpio).

## Riesgos
- D2 puede no existir (INE Padrón Continuo municipal por edad quinquenal). Verificar antes de congelar.
- Los originales de `data/raw/` fueron reescritos in-place; puede que no haya backup. Verificar si se pueden regenerar.
- Contradicciones internas (números distintos para las mismas métricas) deben reconciliarse antes de cualquier congelamiento.
