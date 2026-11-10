# Design: cierre-suficiencia-auditoria

## Context

Medición del 2026-11-05 sobre datos reales:

- `generar_manifest.py --verify` → exit 1: hash distinto en `dim_municipios_tension.csv`.
- `run_all.py --check` → exit 1: `construir_dim_gold.py` desactualizado.
- Esfuerzo 18-34: pipeline canónico usa `cuantia_media_eur_mes_mediana`; silver usa `cuantia_media_eur_mes_media`. Diferencia media 0,51 pp, máxima 2,78 pp, 37 municipios >1 pp.
- `pipeline_vpo_por_municipio` hereda el esfuerzo de `indicadores`, cargado desde silver → dos cifras por municipio.
- VPO: 406 promociones en 77 municipios, 0 viviendas (`NumViviendas` vacío 406/406 en origen).
- Indicador 73 de Open Data Euskadi disponible y municipal (2004-2024).

## Decisions

### D-01: cuantía mediana como definición canónica de esfuerzo
`docs/matriz_indicadores.md` ya declara `cuantia_media_eur_mes_mediana` como indicador canónico y el pipeline produce el 26,61 % defendido. Se alinea el silver a la mediana.

*Alternativa rechazada:* declarar media canónica. Obligaría a rehacer titulares, figuras y docs, y contradice la matriz.

*Consecuencia aceptada:* `esfuerzo_joven_pct`, `_16_29`, `_18_34`, `_18_24`, `_25_34` cambian; la tensión social (percentiles) se recalcula y sus conteos pueden moverse.

### D-02: validación en memoria antes de raw
El CSV nuevo se descarga en memoria, se parsea y valida ahí. Solo si cumple (252 municipios, rango, códigos de 5 dígitos) se promueve a `data/raw/` con `assert_raw_writable(reason)` y se regeneran manifests. No se crea `data/staging/`.

*Motivo:* el bronce es la cadena de custodia del proyecto; un parser fallido no debe invalidarla, y un estado intermedio persistente duplica el raw sin aportar trazabilidad.

### D-03: colección `vpo_municipal` separada
No se mezcla con `municipios.vivienda_contexto`: es una fuente nueva con su propio `fuente`, `anio_fuente` y procedencia. Permite citarla en RA3/RA4 sin reescribir el documento de municipios.

### D-04: el indicador es flujo, no stock
Se documenta explícitamente: "VPO terminadas 2020-2024 ‰ habitantes". El stock histórico sigue sin dato y así se declara. No se presenta como sustituto del stock.

### D-05: tests que fijan 353 se actualizan en el mismo commit
`tests/test_fase_datos.py` y `scripts/verificar_fase_datos.py` pasan a leer el conteo del manifest o a 354. Nunca se relaja la comprobación.

## Architecture

```
indicador 73 (CSV oficial)
        │  extract/26_vpo_terminadas.py (staging → raw, guard+hash)
        ▼
data/raw/udalmap_vpo_terminadas.csv
        │  transform/limpiar_vpo_municipal.py
        ▼
data/procesado/vpo_municipal.csv
        │  storage/load_mongo.py::load_vpo_municipal
        ▼
Mongo: vpo_municipal (252)
        │
        └─ análisis/informe (no entra en el esfuerzo canónico)
```

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| La tensión cambia al pasar a mediana | Recalcular, comparar y actualizar docs/guion con los valores nuevos |
| El CSV oficial trae bloques mezclados (territorio/comarca/municipio) | Parser por sección + validación de 252 códigos |
| Recargar Mongo duplica o pierde docs | `replace_collection` + verificación de conteos antes/después |
| Ruptura de tests por conteo raw | Actualizar contadores y manifest en el mismo commit |

## Migration

Sin migración de datos históricos. Los CSV canónicos se regeneran desde Mongo; el raw existente no se toca.

## Open Questions

- Ninguna bloqueante. Decidido mediana por coherencia con la matriz publicada.
