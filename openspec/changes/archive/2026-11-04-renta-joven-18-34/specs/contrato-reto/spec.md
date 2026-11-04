# Delta for contrato-reto

## ADDED Requirements

### Requirement: JOVEN-18-34 — Canonico de renta y emancipacion

El sistema SHALL usar 18 a 34 anos como canonico de renta y emancipacion joven. La renta SHALL construirse con bandas Eustat CAE 18-19, 20-24, 25-29, 30-34 y ponderacion explicita por anchura. Los subgrupos 18-24 y 25-34 SHALL ser escalares CAE, no tasas municipales.

#### Scenario: Renta 18-34 con ponderacion explicita

- GIVEN Eustat CAE 2024 con 1599, 8156, 20109, 25609 y total 28170
- WHEN se calcula renta_joven_estimada_18_34
- THEN ratio = (2*1599+5*8156+5*20109+5*25609)/17/28170
- AND el nivel municipal es renta municipal 18+ por ratio

#### Scenario: Subgrupos CAE sin fingir municipal

- GIVEN bandas 18-24 y 25-34 CAE
- WHEN se calculan renta_joven_estimada_18_24 y _25_34
- THEN ambos son escalares CAE sobre renta municipal
- AND el ranking municipal por edad se declara identico

## MODIFIED Requirements

### Requirement: Indicador canonico de esfuerzo — 18 a 34

El indicador canonico de esfuerzo joven es esfuerzo_joven_pct_18_34 (alquiler_anual / renta_joven_estimada_18_34 x 100). esfuerzo_joven_pct_16_29 queda como legacy para comparabilidad hasta archive. esfuerzo_ovj_referencia_pct es referencia y no ordena municipios.
(Previously: esfuerzo_joven_pct con base 16_29)

#### Scenario: Esfuerzo 18-34 etichetado

- GIVEN renta_18_34 y alquiler_anual
- WHEN se calcula esfuerzo_joven_pct_18_34
- THEN el campo se guarda y el esfuerzo_16_29 legacy se conserva

#### Scenario: Paro y poblacion no renombrados

- GIVEN paro_menores_25 y poblacion 0-19/20-64
- WHEN se migra a 18-34
- THEN paro y poblacion mantienen sus bandas reales
- AND poblacion_18_34_est se etiqueta como estimacion
