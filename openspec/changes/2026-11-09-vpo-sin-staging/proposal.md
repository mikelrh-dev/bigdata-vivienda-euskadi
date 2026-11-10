# Proposal: vpo-sin-staging

## Why

`data/staging/vpo/indicator.csv` es una copia byte a byte de
`data/raw/udalmap_vpo_terminadas.csv`. No aporta una capa nueva: duplica el
bronce y ensucia la estructura de carpetas. El flujo puede validar el CSV en
memoria y promoverlo a raw solo cuando corresponda.

## What Changes

- `extract/26_vpo_terminadas.py` descarga en memoria, valida y, solo con
  `--promote`, escribe en `data/raw/` con `assert_raw_writable`.
- `--desde-raw` (alias histórico `--sin-descargar`) valida el raw existente
  sin red.
- `--promote` no reescribe si el SHA coincide; se niega si difiere. El bronce
  no se sobrescribe.
- Se elimina `data/staging/` y su entrada en `.gitignore`.
- Se actualizan las referencias de `cierre-suficiencia-auditoria` que describían
  staging.

## Impact

- `data/raw/udalmap_vpo_terminadas.csv` no cambia: mismo SHA
  `70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706`.
- `docs/raw_manifest_sha256.txt`, `data/procesado/vpo_municipal.csv`, Mongo y
  HDFS raw quedan intactos.
- No se añaden tests nuevos; la verificación se hace con la suite existente y
  sondas directas de `validar`/`promover`.

## Out of Scope

- HDFS `procesado` sigue en 404 (gap C2 de la auditoría).
- Nuevas versiones del CSV oficial: exigirían un raw nuevo con otro nombre.
- Recarga de Mongo o regeneración del silver.

## Risks

| Riesgo | Mitigación |
|---|---|
| `--sin-descargar` deja de leer staging | Se mantiene como alias de `--desde-raw`, que lee el raw existente |
| Un `--promote` con fuente cambiada pisa el raw | El SHA distinto se rechaza antes de escribir |
| Pérdida de la copia pre-promoción | El raw y HDFS conservan los mismos bytes; el manifest sigue siendo la verdad |
