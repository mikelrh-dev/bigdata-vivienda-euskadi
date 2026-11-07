# Tasks: mongo-limpieza-crud-test

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 90-140 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Tests no destructivos de limpieza y CRUD | PR 1 | .venv/Scripts/python.exe -m pytest tests/test_mongo.py -q | MongoDB local en marcha con base vivienda_euskadi_test | tests/test_mongo.py y carpeta del cambio |

## Phase 1: Artefactos SDD

- [x] 1.1 Crear proposal.md, delta spec, design.md y tasks.md en openspec/changes/mongo-limpieza-crud-test/.

## Phase 2: Tests

- [x] 2.1 Reescribir test_clean_mongo: 3 documentos temporales, 4 operaciones y contadores exactos, sin tocar producción.
- [x] 2.2 Reescribir test_crud_demo: demo_crud_operations sobre temporal de test con contadores y drop final.

## Phase 3: Verificación

- [x] 3.1 Ejecutar .venv/Scripts/python.exe -m pytest tests/test_mongo.py -q y confirmar 25 passed, 0 skipped, exit code 0.
- [x] 3.2 Revisar código con code-review-and-quality y data-audit: solo tests/test_mongo.py modificado, sin commit.
