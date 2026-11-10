# Reglas de limpieza y transformación (WP-20)

Reglas aplicadas en la capa silver (pandas) con su **predicado portable**
para la fase MongoDB. Cada regla indica: dónde se detecta, dónde se
trata, y el operador Mongo equivalente para la fase siguiente.

Convenciones: `codigo_ine` siempre string de 5 dígitos (`$toString` +
relleno en Mongo). Lectura CSV con `dtype=str, encoding=utf-8-sig`.

## R1. Paro registrado cero → nulo con flag (WP-04)

- **Detecta:** `transform/corregir_empleo.py`.
- **Regla:** `tasa_paro_lanbide_pct == 0` con pocos activos es artefacto,
  no medición. Se conserva el valor publicado en
  `tasa_paro_lanbide_bruto`, se escribe `NaN`, `paro_registrado_cero=true`,
  `tasa_paro_valida=false`.
- **Mongo:** `{$set: {tasa_paro_lanbide_bruto: "$tasa_paro_lanbide_pct"}}`,
  `{$set: {tasa_paro_lanbide_pct: {$cond: [{$lte: ["$tasa_paro_lanbide_pct", 0]}, "$$REMOVE", "$tasa_paro_lanbide_pct"]}}}`.
- **Test:** `test_wp04_ceros_a_nulo_con_flag`.

## R2. Ningún clip contra techo nulo o cero (WP-04)

- **Detecta:** `transform/generar_analisis_variables_base.py`
  (`tasa_desempleo_juvenil_real_pct`).
- **Regla:** todo `clip(upper=cap)` exige `cap.gt(0)`; un techo 0/Nulo
  anularía un valor calculado correctamente.
- **Mongo:** `{$cond: [{$gt: ["$cap", 0]}, {$min: ["$v", "$cap"]}, "$v"]}`.
- **Test:** `test_wp04_sin_clip_contra_cero`.

## R3. Brecha ocupación−actividad eliminada (WP-05)

- **Regla:** las tasas de Udalmap no comparten base (248/252 dan
  ocupación > actividad), así que la resta no mide ninguna brecha.
  Columna prohibida en gold: `brecha_ocupacion_actividad_pct`.
- **Mongo:** no computar; si existe, `{$unset: "brecha_ocupacion_actividad_pct"}`.
- **Test:** `test_wp05_sin_brecha_ocupacion_actividad`.

## R4. Esfuerzo canónico único (WP-06)

- **Regla:** el único esfuerzo para ordenar municipios es
  `esfuerzo_joven_pct = alquiler_anual / renta_joven_estimada_16_29 × 100`
  (base municipal fiscal). El resto (`esfuerzo_min/max/ovj/ajustado`,
  brechas de género) son referencias diagnósticas, no ranking.
- **Mongo (fase siguiente):** agregado sobre la colección de renta con
  el mismo numerador/denominador; el índice de tensión usa este campo
  con fallback a `esfuerzo_max_pct` donde falte.
- **Tests:** `test_wp06_esfuerzo_canonico_unico`,
  `test_wp06_tension_usa_canonico`.

## R5. Recuento de anuncios post-dedup (WP-03/WP-12)

- **Regla:** `n_anuncios` = anuncios únicos post-dedup por `codigo_ine`
  (`transform/aplicar_cobertura_mercado.py`); el crudo se conserva en
  `n_anuncios_raw`. Total: 843 crudos → 594 vigentes (759 era el pre-v5; 45 en cuarentena fuera de Euskadi).
- **Mongo:** `{$group: {_id: "$codigo_ine", n_anuncios: {$sum: 1}}}`
  sobre la colección deduplicada por `property_fingerprint`.
- **Test:** `test_wp12_cobertura_mercado`, `test_wp03_n_anuncios_real`.

## R6. Fallback de periodo con método declarado (WP-11)

- **Regla:** si falta el periodo objetivo, usar el máximo disponible y
  registrarlo en la columna `metodo` (`periodo=...`). Nunca nulo
  silencioso.
- **Mongo:** `$ifNull` con rama documentada + campo `metodo`.
- **Test:** `test_wp11_fallback_poblacion_joven`.

## R7. Higiene de tipos y encoding (WP-10/WP-13)

- **Regla:** toda lectura `dtype=str, encoding=utf-8-sig`; toda
  escritura `encoding=utf-8-sig`; `codigo_ine` con `zfill(5)`.
- **Tests:** `test_wp10_lectura_tipografica`, `test_wp13_higiene_escritura`
  (barren `transform/*.py`).

## R8. Precio/m2 e IQR como flags, nunca como filtro (WP-19)

- **Regla:** `precio_m2_calc = precio_eur/superficie_m2` (2 decimales,
  `None` si falta alguno); `es_outlier_iqr` = flag IQR global
  post-cuarentena (`[Q1-1.5·IQR, Q3+1.5·IQR]`, bounds en log). La
  cuarentena dura (`superficie<10`, `pm2>100`) ya descartó lo imposible;
  el IQR solo asesora. Ambos viven en `auditoria` (JSON) y como columnas
  (CSV). Precio nulo ⇒ `auditoria.motivo_precio_nulo` ∈
  {`geo_aproximada` (Pisos, `geo_invalida=true`), `origen_sin_precio`}.
- **Mongo:** `$addFields: {precio_m2_calc: {$cond: [...]} }`; IQR con
  `$percentile` o cálculo en Python pre-carga.
- **Test:** `test_wp19_precio_nulo_con_motivo`.

## R9. Equipamiento solo RealtyAPI (sin dato ≠ sin equipamiento)

- **Regla:** solo RealtyAPI trae equipamiento real (máx ~84 registros).
  El resto lleva `[]` = **sin dato**, no vivienda vacía. No imputar.
- **Mongo:** no indexar ni filtrar por este array salvo segmento RealtyAPI.
