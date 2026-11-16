# Spec: VPO — unidades, escala y lectura regenerable

## Objective

Corregir la lectura del indicador 73 de Udalmap (VPO terminada por 1.000
habitantes en cinco años) en figuras, memoria, README y deck, sin tocar datos ni
cálculos. La representación debe distinguir tasa de conteo, ‰ de % y escala
común de zoom, y todo debe regenerarse desde scripts.

## Tech Stack

Python 3.12 (`.venv`), pandas, matplotlib, PyMongo, Chrome headless, pytest.
Sin dependencias nuevas.

## Commands

```bash
.venv/Scripts/python.exe transform/generar_figuras_N.py
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/sincronizar_figuras.py
.venv/Scripts/python.exe docs/memoria/build.py --refresh --check --build --pdf
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py
.venv/Scripts/python.exe scripts/verificar_vintage_figuras.py
```

## Requirements

### Requirement: VPO-UNIDAD-01 — Tasa, no porcentaje anual

El sistema SHALL presentar el indicador como tasa acumulada de cinco años por
1.000 habitantes, con la conversión explícita a porcentaje (`pct = tasa / 10`).

#### Scenario: Lectura de 2,7 ‰
- GIVEN la tasa de CAE 2020-2024
- WHEN se lee en la figura o en la memoria
- THEN aparece «2,7 ‰ = 0,27 % en cinco años»
- AND no se presenta como «2,7 % anual»

#### Scenario: Pico de Araba/Álava
- GIVEN la tasa de Araba/Álava 2007-2011
- WHEN se cita su máximo
- THEN aparece «40,1 ‰ = 4,01 %»
- AND se aclara que no es un 40 %

### Requirement: VPO-ESCALA-01 — Escala común con zoom declarado

El sistema SHALL dibujar los cuatro territorios en una escala común y, si
amplía el detalle, declarar el zoom como ampliación del mismo dato.

#### Scenario: Serie 2004-2024
- GIVEN las series de CAE, Bizkaia, Gipuzkoa y Araba/Álava
- WHEN se genera `S_serie_vpo_2004_2024.png`
- THEN el panel izquierdo usa 0-44 ‰ para los cuatro
- AND el panel derecho rotula «Zoom 0-14 ‰» para CAE, Bizkaia y Gipuzkoa

### Requirement: VPO-H5-01 — Tasa frente a conteo

El sistema SHALL titular el H5 como tasa y advertir que no es un número de
viviendas, porque el pipeline solo publica `vpo_terminadas_por_mil`.

#### Scenario: Título del H5
- GIVEN `pipeline_vpo_terminadas`
- WHEN se genera `H5_vpo_terminadas_por_mil.png`
- THEN el título dice «mayor tasa de VPO terminada (‰)»
- AND el panel aclara «Tasa por 1.000 habitantes; no es número de viviendas»

### Requirement: VPO-TRAZABILIDAD-01 — Cifras regenerables

El sistema SHALL derivar las cifras de VPO de la memoria desde
`data/raw/udalmap_vpo_terminadas.csv` y no teclearlas en los capítulos.

#### Scenario: Refresco de tokens
- GIVEN el CSV raw de Udalmap
- WHEN se ejecuta `docs/memoria/build.py --refresh`
- THEN existen tokens `datos.vpo_*` para pico, 2024, ‰ y %
- AND `--check` resuelve todos los tokens sin cifras manuales

## Success Criteria

1. Serie con escala común y zoom declarado.
2. H5 con título de tasa y nota de unidad.
3. Memoria, README y deck con las mismas conversiones.
4. «5.040 solicitudes» sustituido por «5.040 registros municipio-año».
5. Verificadores de deck y vintage en verde.
6. Memoria y PDF del deck reconstruidos desde los scripts.
