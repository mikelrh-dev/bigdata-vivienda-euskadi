# Exploration: esfuerzo_mercado_2026

## Current State

El sistema actual calcula **esfuerzo canónico 2024** en `transform/calcular_renta_joven.py` usando:
- **Alquiler municipal oficial 2024** (Eustat, 159 municipios con dato real, 93 IDW) — colección `alquiler_municipal` en Mongo
- **Salario joven OVJ 2024** — 1.564 €/mes (tramo 18-34) y 1.381 €/mes (tramo 16-29) desde `data/raw/ovj_salario_joven_2024.json`
- **Proxy fiscal Eustat 2024** — ratios ponderados por tramos de edad sobre renta total CAE (28.170 €)

El esfuerzo canónico se persiste en `dim_municipios_enriquecido.csv` y se carga a Mongo en la colección `municipios` (campo `demografia.esfuerzo_joven_pct_18_34`, etc.). La pipeline `pipeline_indicadores_municipio` en `analysis/mongo_aggregations.py` lo expone combinando `alquiler.cuantia_media_eur_mes_mediana` + `demografia.renta_joven_estimada_18_34`.

**Nuevo requisito**: añadir una **capa de esfuerzo de mercado 2026** = precio de anuncio 2026 (desde `anuncios_vivienda_residencial_filtrado.csv`, 594 anuncios post-dedup) + salario joven OVJ 2024 **ajustado por IPC** a 2026. **No debe tocar** el esfuerzo canónico 2024 existente.

Fuentes disponibles:
- `data/procesado/anuncios_vivienda_residencial_filtrado.csv` — 594 filas, columnas: `precio_eur`, `precio_m2_calculado`, `superficie_m2`, `habitaciones`, `modalidad`, `codigo_ine`, `municipio`, `portal`, `es_outlier_iqr`, `iqr_excluido`, etc. (año 2026)
- `data/raw/ovj_salario_joven_2024.json` — salario base 1.564 €/mes (18-34), 1.381 €/mes (16-29)
- IPC 2024→2026: necesita fuente externa (INE) o valor asumido documentado

Manifiestos de integridad:
- `docs/raw_manifest_sha256.txt` (354 entradas) — verifica `data/raw/`
- `data/procesado/manifest_sha256.txt` (182 entradas) — verifica `data/procesado/`
- `scripts/verificar_fase_datos.py` check 01 y 17 validan SHA-256 de ambos manifiestos
- `scripts/gate_extremo_a_extremo.py` valida 354 raw / 182 silver / 14 colecciones / 0 duplicados / lag 0

## Affected Areas

- `data/procesado/anuncios_vivienda_residencial_filtrado.csv` — fuente de precios de anuncio 2026 (ya existe, no se toca)
- `data/raw/ovj_salario_joven_2024.json` — salario base OVJ 2024 (ya existe, no se toca)
- `storage/load_mongo.py` — **sí** si enfoque A (nueva colección `esfuerzo_mercado_2026`); **sí** si enfoque B (añadir campos a `municipios`)
- `analysis/mongo_aggregations.py` — **sí** (nueva pipeline `pipeline_esfuerzo_mercado_2026` en ambos enfoques)
- `transform/calcular_renta_joven.py` — **NO** (esfuerzo canónico 2024, intocable)
- `transform/construir_dim_gold.py` — **NO** (tabla gold canónica, intocable)
- `scripts/verificar_fase_datos.py` — **sí** (añadir check de nueva colección/manifiesto)
- `scripts/gate_extremo_a_extremo.py` — **sí** (añadir colección a `EXPECTED_COLLECTIONS`)
- `openspec/specs/mongodb-y-analisis/spec.md` — **sí** (documentar nueva capacidad/requisito)

## Approaches

### 1. **Colección nueva `esfuerzo_mercado_2026` en Mongo** (Recomendado)

Crea colección independiente con documentos por municipio:
```json
{
  "_id": "48001",
  "nombre": "Bilbao",
  "territorio": "Bizkaia",
  "precio_anuncio_2026": { "medio_eur": 1450, "mediana_eur": 1350, "mediana_m2_winsorizada": 18.5, "n_anuncios": 204, "n_precio": 198 },
  "salario_joven_2026_ipc": { "18_34_eur_mes": 1620, "16_29_eur_mes": 1430, "ipc_factor": 1.036, "fuente_ipc": "INE 2024-2026" },
  "esfuerzo_mercado_pct": { "18_34": 38.2, "16_29": 41.5 },
  "metadatos": { "fuente_precio": "anuncios_vivienda_residencial_filtrado 2026", "fuente_salario": "OVJ 2024 + IPC", "fecha_calculo": "2026-11-12" }
}
```

- **Pros**: Aislamiento total del canónico 2024; riesgo cero de regresión en `municipios`/`indicadores`; consultas separadas y claras; sigue patrón de capas separadas (`alquiler_municipal` tiene oficial/IDW/contexto); carga idempotente vía `replace_collection` existente; fácil de versionar/borrar.
- **Contras**: Una colección extra que mantener; joins necesarios para comparar canónico vs mercado; pipeline de agregación adicional.
- **Effort**: Medium (nuevo loader + pipeline + tests + gate updates)

### 2. **Campo adicional en documento `municipios`**

Añade `esfuerzo_mercado_2026` como subdocumento embebido en cada doc de `municipios`.

- **Pros**: Todo en un documento; consultas unificadas sin `$lookup`; una sola colección para leer.
- **Contras**: Toca `load_municipios()` en `load_mongo.py` (riesgo de romper carga canónica); toca `construir_dim_gold.py` si se quiere persistir en CSV gold; rompe inmutabilidad semántica de `municipios` (capa 2024 vs 2026 mezcladas); mayor superficie de prueba; cualquier bug en loader afecta a 252 docs críticos.
- **Effort**: Medium-High (modifica loader crítico + gold builder + tests de regresión completos)

## Recommendation

**Enfoque 1: Colección nueva `esfuerzo_mercado_2026`**.

Razones:
1. **Aislamiento garantizado**: el esfuerzo canónico 2024 (alquiler oficial Eustat + proxy fiscal/salarial) no se toca ni en código ni en datos.
2. **Consistencia con arquitectura actual**: ya existen capas separadas en `alquiler_municipal` (`metodo_imputacion`: oficial/IDW/contexto). Una colección por vintage/capa es el patrón establecido.
3. **Carga segura**: usa `replace_collection` (staging + backup + rename atómico) ya probado en `load_mongo.py`.
4. **Trazabilidad**: cada doc lleva metadatos completos (fuente precio, fuente salario, factor IPC, fecha).
5. **Reversible**: borrar la colección no afecta a nada más.

## Risks

1. **Fuente IPC no definida**: el ajuste 2024→2026 requiere IPC oficial (INE). Si se usa valor asumido, debe documentarse explícitamente con flag `calculado|fallback` (estilo WP-11 en `calcular_renta_joven.py`).
2. **Manifiestos SHA**: añadir fichero intermedio en `data/procesado/` (ej. `esfuerzo_mercado_2026.csv`) requiere actualizar `data/procesado/manifest_sha256.txt` y `gate_extremo_a_extremo.py` (EXPECTED_SILVER 182→183).
3. **Gate de colecciones**: `EXPECTED_COLLECTIONS` en `gate_extremo_a_extremo.py` pasa de 14 a 15; `load_mongo.py` debe cargarla en `load_all()`.
4. **Verificación fase datos**: `verificar_fase_datos.py` necesitará check que valide la nueva colección (conteo 252, campos obligatorios, esfuerzo calculado).
5. **Coherencia de precios**: los anuncios 2026 ya tienen filtros M1 (precio_m2 3-50, superficie 10-500, habitaciones entero, IQR, winsorización). La nueva pipeline debe reusar esa lógica, no duplicarla.

## Ready for Proposal

**Yes**. El orchestrator debe presentar al usuario la propuesta con:
- Alcance: nueva colección Mongo `esfuerzo_mercado_2026` + pipeline de agregación + loader + tests + actualización gates/manifiestos.
- Fuera de alcance: modificar `calcular_renta_joven.py`, `construir_dim_gold.py`, `dim_municipios_enriquecido.csv`, esfuerzo canónico 2024.
- Decisión pendiente del usuario: **fuente IPC 2024→2026** (INE oficial vs valor asumido documentado). Esto debe resolverse antes del diseño.