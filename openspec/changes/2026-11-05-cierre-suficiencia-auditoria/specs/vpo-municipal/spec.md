# vpo-municipal — Delta

## ADDED Requirements

### Requirement: VPO-MUNICIPAL-01 — Indicador municipal de VPO terminada

El sistema SHALL integrar el indicador oficial "Viviendas protegidas (VPO) terminadas en el último quinquenio (‰ habitantes)" de Open Data Euskadi con granularidad municipal y año de referencia explícito, sin presentarlo como stock histórico.

#### Scenario: Cobertura municipal completa
- GIVEN el CSV oficial del indicador 73 descargado en `data/raw/`
- WHEN se ejecuta `transform/limpiar_vpo_municipal.py`
- THEN `data/procesado/vpo_municipal.csv` contiene 252 municipios con `codigo_ine` de 5 dígitos
- AND cada fila declara `anio_fuente`, `fuente` y el valor `vpo_terminadas_por_mil`

#### Scenario: Valores fuera de rango rechazados
- GIVEN un valor negativo o superior a 50 ‰
- WHEN se valida el CSV
- THEN el test falla y el pipeline no publica el dato

#### Scenario: Stock no disponible se declara
- GIVEN que el origen no publica `NumViviendas`
- WHEN se redacta el informe
- THEN la VPO se describe como flujo quinquenal oficial
- AND el stock histórico se marca como "sin dato", sin inferencias

### Requirement: VPO-MUNICIPAL-02 — Trazabilidad del bronce

El sistema SHALL incorporar el fichero nuevo a `data/raw` solo mediante extractor con `assert_raw_writable`, hash en `docs/raw_manifest_sha256.txt` y actualización de los contadores de tests.

#### Scenario: Promoción con guard
- GIVEN el CSV validado en `data/staging/vpo/`
- WHEN se ejecuta `extract/26_vpo_terminadas.py --promote`
- THEN el fichero queda en `data/raw/` con su hash en el manifest
- AND `generar_manifest.py --verify` devuelve exit 0

## MODIFIED Requirements

### Requirement: INDICADORES-01 — Una sola definición de esfuerzo

El esfuerzo 18-34 SHALL calcularse con `cuantia_media_eur_mes_mediana` en silver, Mongo y los CSV canónicos, de forma que un municipio tenga un único valor en todos los artefactos.

#### Scenario: Coincidencia entre artefactos
- GIVEN un municipio con promociones VPO
- WHEN se comparan `mongo_vpo_por_municipio.csv` y `mongo_esfuerzo_por_municipio.csv`
- THEN `esfuerzo_joven_pct_18_34` coincide en ambos
