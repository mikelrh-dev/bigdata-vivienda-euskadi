# Tasks: integracion-indicadores-10

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 150-250 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | 1 change, 2 unidades (gate / indicadores) |
| Delivery strategy | commit-per-unit |

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| 1 | Gate e2e PASS + trazabilidad | `pytest tests/test_kafka.py tests/test_mongo_orquestador.py -q` | `python scripts/gate_bloque2.py` + `docs/trazabilidad_vm.md` | Revertir gate + entrada trazabilidad |
| 2 | 5 indicadores + huellas | `pytest tests/test_contrato.py -q` | `python analysis/run_analisis_mongo.py` + `docs/matriz_indicadores.md` | Revertir matriz + CSV + test conteo |

## Phase 1: Spec + diseño (propose ya commiteado)

- [x] 1.1 `proposal.md` con scope HDFS procesado fuera y trazabilidad VM obligatoria.
- [x] 1.2 Deltas `specs/almacenamiento-y-streaming` (INTEGRACION-01, KAFKA-01) y `specs/presentacion-de-resultados` (INDICADORES-01 5 non-legacy).
- [x] 1.3 `design.md` con Mermaid y decisiones.

## Phase 2: Integración en vivo

- [x] 2.1 Ejecutar `ss -tlnp`, `kafka-topics --describe`, `kafka-console-consumer --max-messages 3` vía SSH y recopilar salidas en `docs/trazabilidad_vm.md`.
- [x] 2.2 Ejecutar `.venv/Scripts/python.exe scripts/gate_bloque2.py`, añadir Bloque con Fecha/Objetivo/Máquina/Comando/Salida/Conclusión en `docs/trazabilidad_vm.md`.
- [x] 2.3 Verificar `GATE PASS`, `TOTAL>=759`, lag 0, y cada anuncio consultable por `portal:id_anuncio` + `codigo_ine`.

## Phase 3: Indicadores

- [x] 3.1 Actualizar `docs/matriz_indicadores.md`: 5 non-legacy (VPO ‰ como 5º), legacy 16-29 como archivo, huellas regeneradas desde MongoDB (sin teclear).
- [x] 3.2 Regenerar `data/resultados/*.csv` con `analysis/run_analisis_mongo.py` si la huella cambia; verificar 253/253/3.
- [x] 3.3 Añadir `tests/test_contrato.py` (o nuevo `tests/test_indicadores.py`) que cuente 5 non-legacy y prohíba contar el legacy.
- [x] 3.4 Corregir `README.md:159` si el conteo de CSV (5) o G auto queda stale.

## Phase 4: Gate y cierre

- [x] 4.1 `pytest tests -q` verde (anotar counts passed/skipped, repetir harness si un test destructivo requiere `MONGO_ALLOW_DESTRUCTIVE`).
- [x] 4.2 `python scripts/verificar_fase_datos.py` exit 0.
- [x] 4.3 `verify-report.md` con evidencia literal de cada tarea y desviaciones.
- [ ] 4.4 Archivar el change y actualizar specs desplegados (sin tocar HDFS procesado).
