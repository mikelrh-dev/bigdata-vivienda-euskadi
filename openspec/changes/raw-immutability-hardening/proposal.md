# Proposal: Endurecimiento de inmutabilidad de datos raw

## Intent

Los datos crudos en `data/raw/` solo están protegidos por convención (marcador `.FROZEN` escribible, manifest SHA-256, dos smoke tests). Los transforms pueden escribir raw por defecto. Se busca hacer raw inmutable por diseño, documentar un contrato de datos, lots dirigidos con nombre único temporal, temp dir seguro en Windows, corregir el lookup exacto de `muni_resolve`, dedup determinista con columnas aditivas y añadir guardrails tests. Solo adquisición + limpieza; sin infra/Mongo/Kafka.

## Scope

### In Scope

- `enriquecer_codigo_ine.py`: default silver; raw requiere `--write-raw --reason`.
- `f4_pisos_dirigido.py`: filename con segundos + token; sin sobrescritura; append-only.
- `22_geo_areas_funcionales.py`: temp bajo proyecto/`tempfile.gettempdir()`, crear dirs.
- `muni_resolve.py`: claves normalizadas con `norm()`; fuzzy fallback.
- `unificar_anuncios.py`: dedup determinista (input ordenado, prioridad, reporte); downstream añade columnas o archivos separados, nunca reduce.
- `transform/_raw_guard.py`: `assert_raw_writable(reason)`.
- `docs/data_contract.md` (o spec): reglas raw, manifest, inventario, esquemas, salidas procesadas.
- Guardrails: manifest completo, sin writes raw en transforms, f4 nombre único, geo temp, muni_resolve acentos/barras, superset de columnas.

### Out of Scope

- Infra (Mongo, Kafka, HDFS), OS-level read-only raw, abstracción RawWriter completa (fase posterior).

## Capabilities

### New Capabilities

- `contrato-datos`: contrato de datos raw/procesado (manifest, inventario, esquemas, superset de columnas).
- `inmutabilidad-raw`: raw inmutable por defecto, opt-in razonado, guard compartido, sin writes raw en transforms.

### Modified Capabilities

- `extraccion-datos`: rutas raw, temp dir Windows-safe, lots dirigidos con nombre temporal, completitud del manifest.

## Approach

Convención + guardrails estáticos (recomendado en exploración). Defaults seguros, flags explícitos para mutación, tests AST/grep y de contrato. Mantiene los 59 tests existentes. Rechaza OS-level (fricción Windows) y abstracción completa (fuera de alcance).

## Affected Areas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `extract/22_geo_areas_funcionales.py` | Modified | temp dir + raw write |
| `extract/main_ingest.py` | Modified | único orquestador de inventario raw |
| `transform/enriquecer_codigo_ine.py` | Modified | default silver, `_check_frozen` |
| `transform/f4_pisos_dirigido.py` | Modified | filename temporal, append-only |
| `transform/muni_resolve.py` | Modified | lookup exacto normalizado |
| `transform/unificar_anuncios.py` | Modified | dedup determinista |
| `transform/generar_fingerprint.py` et al. | Modified | columnas aditivas |
| `transform/_raw_guard.py` | New | guard compartido |
| `tests/test_raw_inmutable.py` | Modified | guardrails ampliados |
| `docs/data_contract.md` | New | contrato de datos |

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Default silver sorprende callers | Med | aviso de deprecación + `--write-raw` |
| Scan estático evitable por paths dinámicos | Med | escanear literales `RAW_DIR`/`data/raw` y `open(...,"w")` |
| Drift manifest (312 vs 317) | Med | reconciliar antes de nuevos lots |
| Cambio muni_resolve altera dedup | Med | comparar before/after |
| Temp Windows | Low | crear dirs, honrar `TMPDIR` |

## Rollback Plan

Revertir commit; restaurar defaults anteriores (`--silver` opcional); mantener manifest original. Los lots dirigidos nuevos son aditivos (no destructivos). Tests de guardrail se pueden desactivar solo con justificación.

## Dependencies

- Python 3.12, pytest. Sin nuevas dependencias.

## Success Criteria

- [ ] `enriquecer_codigo_ine.py` por defecto no escribe raw.
- [ ] Ningún transform escribe raw salvo `f4` vía guard.
- [ ] Lots dirigidos con nombre único (segundos + token), sin colisión.
- [ ] Temp bajo proyecto/`gettempdir()`, nunca `/tmp` hardcodeado.
- [ ] `muni_resolve` resuelve variantes acentuadas/barras.
- [ ] Salidas derivadas no tienen menos columnas que `anuncios_unificados.csv`.
- [ ] Manifest completo (sin huérfanos).
- [ ] 59 tests existentes siguen pasando + nuevos guardrails.

## Proposal question round

Preguntas propuestas (no se pudo consultar al usuario por ser subagente):

1. ¿El default de `enriquecer_codigo_ine.py` pasa a silver para todos los callers existentes o solo en CI?
2. ¿El contrato de datos vive en `docs/data_contract.md` o como spec `contrato-datos`?
3. ¿Se acepta reconciliar el drift del manifest (312 vs 317) en este mismo cambio?

Supuestos: defaults seguros; contrato como spec + doc; reconciliación incluida.
