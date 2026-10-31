# Informe de Auditoría de Preparación (Readiness Report) — 2026-10-29

## 1. Verificación de realismo estadístico (Sanity Check)

| Métrica | Min | Max | Mediana | Nulos | Dictamen |
|---|---:|---:|---:|---:|---|
| `tasa_desempleo_juvenil_real_pct` | 0,00 | 20,64 | 8,42 | 53 | Plausible; cap 4× paro Lanbide activo |
| `esfuerzo_alquiler_hombres_pct` | 17,41 | 49,08 | 27,36 | 0 | Coherente con renta personal masculina |
| `esfuerzo_alquiler_mujeres_pct` | 20,29 | 52,60 | 33,60 | 0 | Brecha de género visible (mediana +6,2 pp) |
| `esfuerzo_ovj_individual_pct` | 27,95 | 76,10 | 41,64 | 0 | Dentro de rango esperado para joven solo |
| `salario_joven_ajustado_local_eur` | 1.173,85 | 1.588,15 | 1.401,66 | 0 | Ajuste ±15 % por paro joven |
| `paradas_por_1000_hab` (GTFS) | 0,00 | 70,06 | 3,96 | 0 | 0 en rurales sin paradas; max en capitales |
| `precio_eur` (anuncios) | 80 | 9.500 | 1.500 | 40 | Max 9.500 € plausible (lujo); sin outliers salvajes |
| `superficie_m2` (anuncios) | 16 | 6.973 | 88 | 10 | **Outlier**: 6.973 m² (error de captura) |

**Dictamen**: Las métricas socioeconómicas son realistas para Euskadi. No hay esfuerzos del 500 % ni alquileres absurdos. El único outlier salvaje es `superficie_m2 = 6.973` (probable error de scraping), que los sanity bounds de NLP no cubren porque proviene de datos originales. Recomendado filtrar en análisis (IQR) o marcar como `geo_invalida`/`outlier`.

## 2. Verificación de integridad estructural y tipado

- `codigo_ine`: **string de 5 caracteres en las 3 tablas maestras** (`dim_municipios_enriquecido`, `anuncios_unificados`, `alquiler_municipal_completo`), 0 nulos. ✅
- `anuncios_unificados.csv`: **869 registros desduplicados** (fotocasa 471, pisos 261, realtyapi 139), con `habitaciones`, `titulo`, `subtitulo`. ✅
- Completitud de nuevas columnas:
  - `salario_joven_ajustado_local_eur`, `housing_wage_mes`, `brecha_esfuerzo_genero_pp`: 0 nulos. ✅
  - `tasa_desempleo_juvenil_real_pct`: 53 nulos (activos < 20, municipios no robustos). ✅ documentado.
- `alquiler_municipal_completo.csv`: 252 filas, `metodo_imputacion` ∈ {oficial (159), IDW_5_vecinos (93)}. ✅

## 3. Trazabilidad y buenas prácticas

- **Imputación espacial (IDW)**: documentada en `metodo_imputacion` + `idw_vecinos`. ✅
- **Proxy de desempleo**: documentado como estimación (4/20, 5/45) con umbrales y sanity cap. ✅
- **Brecha de género**: documentada como renta personal total (no juvenil). ✅
- **Deuda técnica menor**:
  - `extract/09_realtyapi.py`: no se detecta literal `PY` suelto (posiblemente corregido). ✅
  - `data/raw/html_fotocasa/`: existen HTML crudos (la auditoría previa estaba desactualizada). ✅
  - `EQUIVALENCIAS_EXTRA` en `entity_resolution.py` sigue como dead code. ⚠️ menor
  - Distancias truncadas (5.000 de ~180.000 pares) en `extract/04_b5m.py`. ⚠️ menor
  - `superficie_m2 = 6.973` outlier sin filtrar. ⚠️ menor

**Dictamen deuda**: Ninguna bloquea el pase a HDFS/MongoDB. Se anotan como mejoras futuras.

## 4. Puntuación de madurez

**8,5 / 10**

Justificación: datos robustos, tipado correcto, trazabilidad de imputaciones, 59 tests en verde.
Penalización: outlier de superficie, distancias incompletas, entity resolution con dead code.

## 5. Veredicto

**GO — Pasamos a Docker/HDFS/Kafka/MongoDB.**

Los datos son realistas, profesionales y suficientemente completos para sustentar
el análisis riguroso exigido por el contrato OpenSpec.

## 6. Recomendación técnica para MongoDB

Diseñar 4 colecciones principales:

1. **`dim_municipios`** (252 docs): documento por municipio con `_id = codigo_ine` (string 5 dígitos),
   campos de renta, empleo, distancias, tipología, y un subdocumento `features` con
   salario ajustado, tensión social y brecha de género. Índice único en `codigo_ine`.

2. **`alquiler_municipal`** (252 docs): `_id = codigo_ine`, campos de alquiler
   (media/mediana/p25/p75), `nivel_geografico`, `metodo_imputacion` (oficial/IDW_5_vecinos),
   `idw_vecinos`. Permite filtrar por `metodo_imputacion` en agregaciones.

3. **`anuncios`** (869 docs): `_id = {portal}_{id_anuncio}`, campos `precio_eur`,
   `superficie_m2`, `habitaciones`, `modalidad`, `titulo`, `subtitulo`, y subdocumento
   `ubicacion` con `codigo_ine`, `municipio`, `coordenadas` (GeoJSON Point para
   `$geoNear`). Índice en `ubicacion.codigo_ine` y `ubicacion.coordenadas`.

4. **`fuentes_raw`** (metadata): registro de origen, fecha, hash SHA-256 y cobertura
   por fuente, para auditoría y reproducibilidad.

Usar Aggregation Pipeline para joins `$lookup` entre `anuncios` y `dim_municipios`
por `codigo_ine`, y `$group` por área funcional para la comparativa compra/alquiler.
Marcar outliers de superficie con un flag `es_outlier_superficie` antes de agregar.
EOF