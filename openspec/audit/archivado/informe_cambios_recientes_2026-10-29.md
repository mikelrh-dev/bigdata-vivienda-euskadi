# Informe de cambios recientes — 2026-10-29

## Resumen

Se han implementado mejoras en la capa Silver sin alterar `data/raw/` (inmutable),
incluyendo hotfix de padding INE, canonicalización de entidades, rescate NLP,
brecha de género y desempleo juvenil real con mitigaciones.

## Hotfix INE (Paso 0)
- `codigo_ine` se fuerza a `str` + `.zfill(5)` en `calcular_renta_joven.py`
  y `calcular_tension_social.py`.
- Corrige la pérdida de ceros a la izquierda en 51 códigos de Álava.

## T1 — Canonicalización de entidades
- `transform/unificar_anuncios.py` usa `transform/muni_resolve.py` para resolver
  código INE (directo, mapeo manual, fuzzy ≥85 %).
- Mapeos forzados: Donostia, Arrasate, Vitoria, Arrankudiaga.
- Filtra registros inválidos (ej. Madrid, `codigo_ine=None`).
- Donostia unificada: 130 anuncios (antes 80 + 50).
- Total anuncios: 869 (antes 871).

## T2 — Rescate NLP (Pisos.com)
- Nuevo script `transform/rescatar_features_nlp.py`.
- Aplica regex sobre `titulo`/`subtitulo` para nulos residuales de `superficie_m2`
  y `habitaciones`, con sanity bounds (15–500 m², ≤10 hab).
- Resultado: 0 rescates (los nulos no contenían patrón).
- `unificar_anuncios.py` ahora propaga `habitaciones`, `titulo`, `subtitulo`.

## T4 — Brecha de género
- Merge de renta por sexo desde `udalmap_indicadores_adicionales.csv`.
- Nuevas columnas en `dim_municipios_enriquecido.csv`:
  `esfuerzo_alquiler_hombres_pct`, `esfuerzo_alquiler_mujeres_pct`,
  `brecha_esfuerzo_genero_pp` (0 nulos).

## T3 — Desempleo juvenil real
- Estimación de población 16–24: `(pob_0_19 * 4/20) + (pob_20_64 * 5/45)`.
- `ocupados_16_24 = poblacion_16_24 * (tasa_ocupacion_juvenil_16_24_pct / 100)`.
- `activos_16_24 = ocupados_16_24 + paro_joven_menores_25`.
- `tasa_desempleo_juvenil_real_pct = paro / activos * 100`.
- Mitigaciones: `activos < 20 → null`, clip [0, 100], cap `4 × tasa_paro_lanbide_pct`.
- Resultado: 53 municipios sin tasa (no robustos), max 20,6 %.

## Impacto en tests y datos
- `pytest -q`: 59 passed.
- `dim_municipios_enriquecido.csv`: 252 × 65, `codigo_ine` 5 dígitos.
- `anuncios_unificados.csv`: 869 filas con `habitaciones`, `titulo`, `subtitulo`.

## Deuda técnica restante
- Entity resolution: Donostia unificada (código), pero variante textual resuelta.
- Superficie/habitaciones ausentes en pisos.com (no rescatables por NLP).
- Raw HTML de Fotocasa no persistido.
- `extract/09_realtyapi.py` con literal `PY` suelto.
- Distancias truncadas (5.000 de ~180.000 pares).
- Infraestructura (HDFS, Kafka, MongoDB) pendiente.

## Commits
- `225c116` feat(silver): fix INE padding, canonicalize entities, add NLP rescue and demographic bounds
EOF