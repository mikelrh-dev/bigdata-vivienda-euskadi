# Design: esfuerzo_mercado_2026

## Overview
Nueva colección isolada `esfuerzo_mercado_2026` (252 docs, `_id` = codigo_ine zfill 5) que combina precio de anuncio 2026 (silver CSV) con salario joven OVJ 2024 ajustado por IPC oficial INE 2024→2026. Carga atómica vía `replace_collection` (staging + backup + rename). Sin tocar `municipios`, `calcular_renta_joven.py` ni el esfuerzo canónico 2024.

## Data Model
| Field | Type | Description |
|-------|------|-------------|
| _id | string | codigo_ine zfill 5 (PK) |
| nombre | string | nombre canonico del municipio |
| territorio | string | Araba/Bizkaia/Gipuzkoa |
| precio_anuncio_2026 | object | {medio_eur, mediana_eur, mediana_m2_winsorizada, n_anuncios, n_precio} |
| salario_joven_2026_ipc | object | {18_34_eur_mes, 16_29_eur_mes, ipc_2024, ipc_2026, factor_ipc, ajustado_eur_mes, fuente_ipc} |
| esfuerzo_mercado_pct | object | {pct_18_34, pct_16_29} |
| metadatos | object | {fuente_precio, fuente_salario, fuente_ipc, fecha_calculo, vintage_numerador, vintage_denominador, flag_no_comparable} |

## Pipeline Design
### Nueva pipeline: `pipeline_esfuerzo_mercado_2026()`
Stages: `$match` (todos), `$lookup` a `municipios` por `_id` para nombre/territorio (si no se embeben en carga), `$project` con los 4 grupos de campos, `$sort` por `_id`.

### Pipelines existentes sin cambios
- `pipeline_indicadores_municipio` — NO MODIFICADO (esfuerzo canónico 2024).
- `pipeline_alquiler_por_municipio`, `pipeline_modalidades`, `pipeline_tier_por_municipio`, etc. — intactos.

## Indexes
| Collection | Index | Purpose |
|------------|-------|---------|
| `esfuerzo_mercado_2026` | {codigo_ine: 1} | unique lookup key (PK `_id` implícita) |
| `esfuerzo_mercado_2026` | {territorio: 1} | filtrado por territorio |

## Load Flow
1. `scripts/descargar_ipc_ine.py` → `data/raw/ipc_ine_2024_2026.csv` + manifiesto SHA en `docs/raw_manifest_sha256.txt`
2. `transform/calcular_esfuerzo_mercado_2026.py` → `data/procesado/esfuerzo_mercado_2026.csv` (252 filas)
3. `storage/load_mongo.py` → `load_esfuerzo_mercado_2026()` usa `replace_collection("esfuerzo_mercado_2026", docs)` staging+backup+rename atómico; registrar en `load_all()`
4. `analysis/mongo_indexes.py` → `ensure_indexes()` añade índice en nueva colección

## Gate Updates
- `EXPECTED_SILVER`: 182 → 183
- `EXPECTED_COLLECTIONS`: 14 → 15 (añadir `"esfuerzo_mercado_2026"`)
- Check 19 en `scripts/verificar_fase_datos.py`: conteo 252, campos obligatorios, esfuerzo calculado, sin nulos en salario_2026

## Rollback
1. `db.esfuerzo_mercado_2026.drop()`
2. Revertir manifiestos (`manifest_sha256.txt`, `docs/raw_manifest_sha256.txt`) al SHA previo
3. Revertir `EXPECTED_SILVER`/`EXPECTED_COLLECTIONS` en gate
Sin impacto en `municipios` ni canónico 2024.

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| IPC INE API no disponible | Fallback documentado con flag `fallback` en metadatos |
| Manifest SHA mismatch | Regenerar tras crear ficheros; gate verifica integridad |
| Carga falla a mitad | `replace_collection` atómico (staging+backup+rename) |
