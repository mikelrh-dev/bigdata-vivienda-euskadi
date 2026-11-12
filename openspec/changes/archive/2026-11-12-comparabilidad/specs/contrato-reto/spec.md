# contrato-reto — Delta

## MODIFIED Requirements

### Requirement: Indicador canónico de esfuerzo (enmienda 2026-11-04, 18-34)

El indicador canónico de esfuerzo joven es `esfuerzo_joven_pct_18_34`
(`alquiler_anual / renta_joven_estimada_18_34 × 100`), donde
`renta_joven_estimada_18_34 = renta_hogar_INE_Atlas_2024 × (renta_media_18_34_CAE / renta_media_total_CAE)`
con ponderación por anchura sobre bandas Eustat CAE 2024 18-19 (2 años),
20-24 (5), 25-29 (5) y 30-34 (5):
`ratio_18_34 = (2×1599 + 5×8156 + 5×20109 + 5×25609)/17/28170`.
La base municipal es `renta_hogar` del Atlas de INE 2024 (Bilbao 47.550), no la
renta personal de Eustat RPF 2024 (28.521), que queda como contraste. Los
subgrupos `renta_joven_estimada_18_24` y `renta_joven_estimada_25_34` son
escalares CAE sobre la renta municipal (mismo ratio nacional); el ranking
municipal por edad es idéntico entre subgrupos y **no** se interpreta como
renta municipal por edad. `esfuerzo_joven_pct` (base `renta_joven_estimada_16_29`)
queda como legacy para comparabilidad hasta archive. `esfuerzo_ovj_referencia_pct`
(salario OVJ neto 2024, constante autonómica) es una referencia y **no se usa
para ordenar municipios**. Las variantes antiguas en fracción
(`esfuerzo_renta_*`) quedan retiradas.
(Previously: base `renta_municipal_18plus` sin concretar la fuente.)

#### Scenario: Renta 18-34 con ponderación explícita

- GIVEN Eustat CAE 2024 con 1599, 8156, 20109, 25609 y total 28170
- WHEN se calcula `renta_joven_estimada_18_34`
- THEN `ratio = (2*1599+5*8156+5*20109+5*25609)/17/28170`
- AND el nivel municipal es `renta_hogar` INE Atlas 2024 por ratio

#### Scenario: Denominador canónico declarado

- GIVEN `data/procesado/analisis_variables_base.csv`
- WHEN se lee el denominador de `esfuerzo_joven_pct_18_34`
- THEN la base es `renta_hogar` INE Atlas 2024 (Bilbao 47.550), no Eustat RPF (28.521)

#### Scenario: Subgrupos CAE sin fingir municipal

- GIVEN bandas 18-24 y 25-34 CAE
- WHEN se calculan `renta_joven_estimada_18_24` y `_25_34`
- THEN ambos son escalares CAE sobre renta municipal
- AND el ranking municipal por edad se declara idéntico

#### Scenario: Esfuerzo 18-34 etiquetado

- GIVEN `renta_18_34` y `alquiler_anual`
- WHEN se calcula `esfuerzo_joven_pct_18_34`
- THEN el campo se guarda y el `esfuerzo_16_29` legacy se conserva

#### Scenario: Paro y población no renombrados

- GIVEN paro_menores_25 y población 0-19/20-64
- WHEN se migra a 18-34
- THEN paro y población mantienen sus bandas reales
- AND `poblacion_18_34_est` se etiqueta como estimación
