# Design: vpo-sin-staging

## Context

`extract/26_vpo_terminadas.py` descargaba a `data/staging/vpo/indicator.csv`,
validaba ese fichero y, con `--promote`, lo copiaba a
`data/raw/udalmap_vpo_terminadas.csv`. El staging es byte a byte igual al raw
(35.427 B, SHA `70a2937a…1294706`) y está ignorado por git.

## Decisions

### D-01: validación en memoria

`descargar()` devuelve `bytes`; `validar(payload)` decodifica latin-1 y parsea
con `csv.reader(io.StringIO(...), delimiter=";")`. No hay fichero intermedio.

*Alternativa rechazada:* usar `tempfile`. Funcionaría, pero mantiene un fichero
temporal y un modo de fallo adicional sin mejorar la trazabilidad.

### D-02: `--desde-raw` sustituye a `--sin-descargar`

El modo offline lee `RAW_CSV` y lo valida. Se conserva `--sin-descargar` como
alias para no romper comandos existentes.

### D-03: promoción idempotente y no destructiva

`promover(payload)` calcula el SHA antes de tocar nada:

- si el raw no existe: `assert_raw_writable(...)` y escritura;
- si existe con el mismo SHA: no-op, sin reescribir ni cambiar mtime;
- si existe con otro SHA: `SystemExit` y no se modifica.

Esto convierte el bronce en append-only de facto para este extractor.

## Architecture

```
URL oficial
   │  requests.get -> bytes
   ▼
validar(payload)  (>=252 códigos de 5 dígitos, 2024, rango 0-100)
   │
   ├─ sin --promote ──> no escribe raw
   │
   └─ --promote ──> promover(payload)
                        │
                        ├─ raw ausente -> guard + write
                        ├─ mismo SHA   -> no-op
                        └─ otro SHA    -> abort
```

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| El origen cambia y se pierde la versión anterior | El SHA distinto se rechaza; el raw y HDFS conservan la versión congelada |
| `--sin-descargar` deja de encontrar staging | Alias a `--desde-raw`, que lee el raw existente |
| El test de inmutabilidad detecta un fichero nuevo | No se crea ningún fichero en raw; solo se lee |
| HDFS se desincroniza | No cambian los bytes; se verifica SHA local vs HDFS antes/después |

## Migration

1. Sustituir el extractor.
2. Borrar `data/staging/`.
3. Actualizar docs y `.gitignore`.
4. Verificar SHA local, manifest, HDFS y tests de inmutabilidad.
