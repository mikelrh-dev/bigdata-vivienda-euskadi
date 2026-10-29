# Reauditoría features v2 — 2026-10-29

## Alcance

Auditoría read-only de las 4 features de Data Science implementadas en la capa silver
(IDW, salario ajustado, comparativa compra/alquiler por área funcional, tensión social)
y de su impacto sobre el contrato OpenSpec.

## Features implementadas

### 1. Imputación espacial IDW (T1)
- Script: `transform/completar_alquiler_comarca.py` (lógica IDW).
- 93 municipios sin dato directo imputados con los 5 vecinos más cercanos (p=2).
- Columna `metodo_imputacion` ('oficial' vs 'IDW_5_vecinos') + `idw_vecinos`.
- **Limitación**: estimación espacial, no dato real; municipios aislados heredan valores lejanos.

### 2. Salario joven ajustado al riesgo local (T2)
- Script: `transform/calcular_renta_joven.py`.
- Driver único: paro joven Lanbide (z-score truncado [-1,+1], banda ±15 %).
- `salario_joven_ajustado_local_eur` (mediana 1.402 €) y `esfuerzo_ajustado_pct` (mediana 41,6 %).
- **Limitación**: proxy de riesgo, no salario observado; el OVJ es nacional.

### 3. Comparativa compra vs alquiler por área funcional (T3)
- Script: `transform/generar_mercado_area_funcional.py`.
- 15 áreas funcionales: mediana alquiler libre vs compraventa libre (ECVI).
- Ratio 237–557 meses de alquiler; `precio_m2_usada_eur` 100 % nulo (solo libre).
- **Limitación**: ECVI agregado a área; no municipal.

### 4. Índice de tensión social (T4)
- Script: `transform/calcular_tension_social.py`.
- Etxebide 2024 (252 mun) + esfuerzo OVJ; índice 0–100 y categoría (baja/media/alta).
- Resultado: 76 alta, 93 media, 83 baja.
- **Limitación**: Etxebide mide solicitudes, no oferta; narrativa de tensión de demanda.

## Impacto en tests

- `pytest -q`: 59 passed (sin regresiones).
- Nuevas columnas en `dim_municipios_enriquecido.csv`: 52 → 55.

## Deuda técnica restante

- Entity resolution: Donostia aparece dividida (80 + 50 anuncios) por variante no mapeada.
- Superficie/habitaciones ausentes en pisos.com.
- Raw HTML de Fotocasa no persistido (EXTRACCION-01).
- `extract/09_realtyapi.py` con literal `PY` suelto (NameError al importar).
- Distancias truncadas (5.000 de ~180.000 pares).
- Infraestructura (HDFS, Kafka, MongoDB) pendiente.

## Conclusión

Las 4 features elevan la capacidad analítica sin violar la inmutabilidad de raw.
El contrato OpenSpec sigue siendo la fuente de verdad; las features son proxy/estimación
documentadas, no dato real. Recomendado actualizar `specs/contrato-reto/spec.md` si
se quieren formalizar como requisitos.
EOF