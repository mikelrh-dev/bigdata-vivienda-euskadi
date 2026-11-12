# Proposal: esfuerzo_mercado_2026

## Intent

Añadir una **capa de esfuerzo de mercado 2026** como nueva colección en MongoDB (`esfuerzo_mercado_2026`) que combine:
- **Precio de anuncio 2026**: desde `data/procesado/anuncios_vivienda_residencial_filtrado.csv` (594 anuncios post-dedup, medianas y precios medios por municipio)
- **Salario joven OVJ 2024 ajustado por IPC oficial INE 2024→2026**: factor IPC descargado del INE, guardado en `data/raw/ipc_ine_2024_2026.csv` con manifiesto SHA

**Sin tocar** el esfuerzo canónico 2024 existente (colección `municipios`, campos `demografia.esfuerzo_joven_pct_*`, pipeline `pipeline_indicadores_municipio`, `transform/calcular_renta_joven.py`, `dim_municipios_enriquecido.csv`).

---

## Scope

### In Scope (toca)
- **Nueva colección Mongo**: `esfuerzo_mercado_2026` (252 documentos, uno por municipio)
- **Nuevo loader**: `load_esfuerzo_mercado_2026()` en `storage/load_mongo.py` usando patrón `replace_collection` (staging + backup + rename atómico)
- **Nueva pipeline**: `pipeline_esfuerzo_mercado_2026()` en `analysis/mongo_aggregations.py`
- **Script de cálculo IPC**: `scripts/descargar_ipc_ine.py` — descarga IPC medio anual 2024 y 2026 del INE, calcula factor, guarda CSV + manifiesto
- **Intermedio silver**: `data/procesado/esfuerzo_mercado_2026.csv` (persiste cálculo por municipio para trazabilidad)
- **Manifiesto SHA**: actualizar `data/procesado/manifest_sha256.txt` (+1 entrada → 183)
- **Gate e2e**: actualizar `EXPECTED_SILVER = 183` y `EXPECTED_COLLECTIONS` (+ `esfuerzo_mercado_2026` → 15) en `scripts/gate_extremo_a_extremo.py`
- **Verificación fase datos**: nuevo check en `scripts/verificar_fase_datos.py` (conteo 252, campos obligatorios, esfuerzo calculado)
- **Índices**: añadir índice compuesto en `ensure_indexes()` para `esfuerzo_mercado_2026`
- **Spec**: documentar nueva capacidad en `openspec/specs/mongodb-y-analisis/spec.md`

### Out of Scope (NO toca)
- `transform/calcular_renta_joven.py` — esfuerzo canónico 2024 (intocable)
- `transform/construir_dim_gold.py` — tabla gold canónica (intocable)
- `data/procesado/dim_municipios_enriquecido.csv` — esfuerzo canónico persistido (intocable)
- Colección `municipios` — no se añaden campos ni se modifica loader
- Colección `indicadores` — no se modifica
- `pipeline_indicadores_municipio` — no se modifica
- `data/raw/ovj_salario_joven_2024.json` — solo lectura
- `data/procesado/anuncios_vivienda_residencial_filtrado.csv` — solo lectura

---

## Approach

**Enfoque 1: Colección nueva `esfuerzo_mercado_2026`** (recomendado en exploration.md)

### Documento tipo (por municipio, `_id` = `codigo_ine` zfill 5)
```json
{
  "_id": "48001",
  "nombre": "Bilbao",
  "territorio": "Bizkaia",
  "precio_anuncio_2026": {
    "medio_eur": 1450,
    "mediana_eur": 1350,
    "mediana_m2_winsorizada": 18.5,
    "n_anuncios": 204,
    "n_precio": 198
  },
  "salario_joven_2026_ipc": {
    "18_34_eur_mes": 1620,
    "16_29_eur_mes": 1430,
    "ipc_factor": 1.036,
    "fuente_ipc": "INE 2024-2026"
  },
  "esfuerzo_mercado_pct": {
    "18_34": 38.2,
    "16_29": 41.5
  },
  "metadatos": {
    "fuente_precio": "anuncios_vivienda_residencial_filtrado 2026",
    "fuente_salario": "OVJ 2024 + IPC",
    "fecha_calculo": "2026-11-12"
  }
}
```

### Flujo de datos
1. **IPC INE**: `scripts/descargar_ipc_ine.py` → `data/raw/ipc_ine_2024_2026.csv` (raw) → manifiesto `docs/raw_manifest_sha256.txt` (+1)
2. **Cálculo silver**: script nuevo (ej. `transform/calcular_esfuerzo_mercado_2026.py`) lee:
   - `anuncios_vivienda_residencial_filtrado.csv` → agrega por `codigo_ine`: medio, mediana, winsorizada p1-99, n_anuncios, n_precio
   - `ovj_salario_joven_2024.json` → salario base 18-34 (1564) y 16-29 (1381)
   - `ipc_ine_2024_2026.csv` → factor = ipc_2026 / ipc_2024
   - Calcula salario_2026 = salario_2024 * factor
   - Calcula esfuerzo = (precio_medio_anuncio * 12) / salario_2026 * 100
   - Guarda `data/procesado/esfuerzo_mercado_2026.csv` (252 filas)
3. **Manifiesto silver**: actualizar `data/procesado/manifest_sha256.txt` (+1 entrada → 183)
4. **Carga Mongo**: `load_esfuerzo_mercado_2026()` en `storage/load_mongo.py` usa `replace_collection("esfuerzo_mercado_2026", docs)` (staging + backup + rename atómico)
5. **Pipeline**: `pipeline_esfuerzo_mercado_2026()` en `analysis/mongo_aggregations.py` expone la colección (opcional: `$lookup` a `municipios` para nombre/territorio si no se embeben)
6. **Índices**: `ensure_indexes()` añade índice en `esfuerzo_mercado_2026._id` (ya PK) + opcional `territorio`

### Razones del enfoque (consistencia con arquitectura actual)
- **Aislamiento garantizado**: el esfuerzo canónico 2024 (alquiler oficial Eustat + proxy fiscal/salarial) no se toca ni en código ni en datos
- **Patrón establecido**: ya existen capas separadas en `alquiler_municipal` (`metodo_imputacion`: oficial/IDW/contexto). Una colección por vintage/capa es el patrón
- **Carga segura**: usa `replace_collection` (staging + backup + rename atómico) ya probado en `load_mongo.py`
- **Trazabilidad**: cada doc lleva metadatos completos (fuente precio, fuente salario, factor IPC, fecha)
- **Reversible**: borrar la colección no afecta a nada más

---

## Files to create

| Ruta | Qué hace |
|------|----------|
| `scripts/descargar_ipc_ine.py` | Descarga IPC medio anual 2024 y 2026 del INE (API/web), calcula factor 2024→2026, guarda `data/raw/ipc_ine_2024_2026.csv` con columnas `anio, ipc_medio, fuente, fecha_extraccion` |
| `transform/calcular_esfuerzo_mercado_2026.py` | Lee anuncios 2026 + salario OVJ 2024 + IPC INE, agrega precios por municipio, calcula salario 2026 y esfuerzo mercado, guarda `data/procesado/esfuerzo_mercado_2026.csv` (252 filas) |
| `openspec/changes/esfuerzo-mercado-2026/design.md` | Diseño técnico (creado en fase Design) |
| `openspec/changes/esfuerzo-mercado-2026/tasks.md` | Lista de tareas (creado en fase Tasks) |

---

## Files to modify

| Ruta | Qué se cambia y por qué |
|------|------------------------|
| `storage/load_mongo.py` | Añadir `load_esfuerzo_mercado_2026()` que lee `data/procesado/esfuerzo_mercado_2026.csv` y hace `replace_collection("esfuerzo_mercado_2026", docs)`; registrar en `load_all()` |
| `analysis/mongo_aggregations.py` | Añadir `pipeline_esfuerzo_mercado_2026()` que expone la colección (proyección + sort); opcional `$lookup` a `municipios` para nombre/territorio |
| `analysis/mongo_indexes.py` | Añadir índice en `esfuerzo_mercado_2026` (PK `_id` ya implícito; opcional compuesto `territorio + nombre`) en `ensure_indexes()` |
| `scripts/verificar_fase_datos.py` | Añadir check 19: valida colección `esfuerzo_mercado_2026` (252 docs, campos obligatorios, esfuerzo calculado, sin nulos en salario_2026) |
| `scripts/gate_extremo_a_extremo.py` | `EXPECTED_SILVER = 183`; `EXPECTED_COLLECTIONS` añadir `"esfuerzo_mercado_2026"` (total 15) |
| `data/procesado/manifest_sha256.txt` | Añadir SHA256 de `esfuerzo_mercado_2026.csv` (1 entrada nueva → 183) |
| `docs/raw_manifest_sha256.txt` | Añadir SHA256 de `ipc_ine_2024_2026.csv` (1 entrada nueva → 355) |
| `openspec/specs/mongodb-y-analisis/spec.md` | Documentar nueva capacidad: requirement `MERCADO-01` (capa mercado 2026), scenario de carga, pipeline, gate |

---

## Risk assessment

| Riesgo | Nivel | Mitigación |
|--------|-------|------------|
| **Fuente IPC no disponible / API INE cambia** | Medio | Script con fallback documentado; flag `calculado|fallback` estilo WP-11 en metadatos; factor hardcodeado documentado si falla descarga |
| **Manifiestos SHA rotos** | Bajo | Actualización atómica de manifiestos tras generar ficheros; gate verifica integridad |
| **Gate e2e falla por colección nueva** | Bajo | `EXPECTED_COLLECTIONS` y `EXPECTED_SILVER` actualizados en mismo PR; `check_colecciones()` valida presencia en `load_mongo.py` |
| **Regresión en carga canónica** | Muy bajo | Colección nueva aislada; `load_municipios()` y `load_indicadores()` no se tocan; `replace_collection` atómico por colección |
| **Precios anuncio 2026 incompatibles con alquiler oficial 2024** | Medio | Documentado en spec (figura P ya declara no comparabilidad ratio 1.96; Spearman 0.18); metadatos en cada doc declaran vintage/fuente |
| **IPC medio anual vs mensual** | Bajo | Usar IPC *medio anual* 2024 y 2026 (coherente con salario anual = mensual × 12); validar en script |

---

## Alternatives considered

| Alternativa | Por qué se descarta |
|-------------|---------------------|
| **Campo embebido en `municipios` (enfoque 2)** | Toca `load_municipios()` (loader crítico, 252 docs); rompe inmutabilidad semántica de capa 2024; mayor superficie de prueba; cualquier bug afecta docs críticos; requiere regenerar `dim_municipios_enriquecido.csv` |
| **Pipeline que calcula on-the-fly sin persistir** | No permite gate/verificación; no hay trazabilidad de factor IPC usado; recálculo en cada query; no sigue patrón de capas persistidas (`alquiler_municipal`, `indicadores`) |
| **Usar IPC estimado/asumido sin descargar INE** | Usuario decidió: **fuente IPC = INE oficial**. Valor asumido requeriría flag `fallback` y auditoría manual; INE es fuente autoritativa y accesible |
| **Modificar `calcular_renta_joven.py` para añadir esfuerzo mercado** | Rompe separación canónico vs mercado; esfuerzo canónico usa alquiler oficial Eustat 2024 + proxy fiscal; mercado usa anuncios 2026 + salario IPC; son capas metodológicamente distintas |

---

## Decision

**Fuente IPC = INE oficial** (descargar IPC medio anual 2024 y 2026 del INE, guardar en `data/raw/ipc_ine_2024_2026.csv` con manifiesto SHA en `docs/raw_manifest_sha256.txt`).

Esta decisión fue tomada por el usuario antes de la fase Propuesta y se documenta aquí como requisito inmutable para la fase Design.

---

## Ready for Design

**Yes**. Todos los requisitos previos cubiertos:
- Exploration completada (`exploration.md` existe)
- Decisión IPC resuelta (INE oficial)
- Código base investigado y validado (loaders, pipelines, manifiestos, gates)
- Enfoque recomendado coherente con arquitectura actual (colección nueva, `replace_collection`, capas separadas)
- Archivos a crear/modificar identificados con rutas exactas
- Riesgos evaluados y mitigaciones definidas