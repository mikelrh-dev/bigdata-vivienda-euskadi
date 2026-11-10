# vpo-sin-staging — Delta

## ADDED Requirements

### Requirement: VPO-STAGING-01 — Descarga sin staging

El extractor SHALL descargar el CSV oficial en memoria y validarlo antes de
escribir en `data/raw/`. SHALL NOT crear ni usar `data/staging/`.

#### Scenario: Descarga validada sin escritura

- GIVEN la URL oficial del indicador 73
- WHEN se ejecuta `extract/26_vpo_terminadas.py` sin `--promote`
- THEN valida al menos 252 códigos de 5 dígitos (el origen trae 272, incluidos disueltos) con valores 2024 en rango
- AND no escribe en `data/raw/` ni crea `data/staging/`

#### Scenario: Promoción con el mismo SHA

- GIVEN un payload validado cuyo SHA coincide con el raw existente
- WHEN se ejecuta `--promote`
- THEN informa de que el raw ya existe con el mismo SHA
- AND no reescribe el fichero ni cambia su mtime

#### Scenario: Promoción con SHA distinto

- GIVEN un payload validado cuyo SHA no coincide con el raw existente
- WHEN se ejecuta `--promote`
- THEN aborta con un mensaje de raw inmutable
- AND no modifica el fichero existente

### Requirement: VPO-STAGING-02 — Validación offline

El extractor SHALL permitir validar el raw existente sin red mediante
`--desde-raw`, conservando `--sin-descargar` como alias.

#### Scenario: Validación del raw

- GIVEN `data/raw/udalmap_vpo_terminadas.csv` existente
- WHEN se ejecuta `--desde-raw`
- THEN valida al menos 252 códigos de 5 dígitos y 2024 sin descargar
- AND no escribe en raw

### Requirement: VPO-STAGING-03 — Bronce y HDFS intactos

La eliminación de staging SHALL NOT alterar los bytes de
`data/raw/udalmap_vpo_terminadas.csv`, su entrada en el manifest ni la copia
de HDFS.

#### Scenario: Mismo SHA en local y HDFS

- GIVEN el raw local y su copia HDFS
- WHEN se ejecuta el nuevo flujo y la verificación
- THEN ambos conservan el SHA
  `70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706`
- AND `pytest tests/test_raw_inmutable.py` pasa
