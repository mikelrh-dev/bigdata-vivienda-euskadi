# Spec: gate-extremo-a-extremo-offline (cambio)

## Purpose

Gate extremo a extremo automatizado: offline hoy (sin red, con fakes) y vivo
opt-in mañana en clase (HDFS/Kafka centro). F10 deja de ser parcial.

## Requirements

### Requirement: E2E offline hermético

El sistema MUST ejecutar el gate por defecto en modo `--offline` sin red,
sin tocar `data/raw`/`.FROZEN` y sin escribir en Mongo/HDFS/Kafka reales.

#### Scenario: Gate offline pasa en seco

- GIVEN el repo checkout con manifiestos locales
- WHEN se ejecuta `python scripts/gate_extremo_a_extremo.py --offline`
- THEN exit 0, sin intentos de red ni escrituras fuera de `tmp_path`.

#### Scenario: Hermeticidad con fakes

- GIVEN `tmp_path` y fakes de pipeline
- WHEN se ejecuta `tests/test_extremo_a_extremo.py`
- THEN todo pasa sin servicios externos (red bloqueada o ausente).

### Requirement: Integración Mongo con mongomock o skip

El sistema MUST validar la lógica Mongo sobre mongomock; si no está
instalado, el test MUST quedar en skip (no en fallo) y nunca conectar al
centro en offline.

#### Scenario: mongomock disponible

- GIVEN `mongomock` instalado
- WHEN corre `tests/test_integracion_mongo.py`
- THEN CRUD/índices/0 duplicados pasan sobre el fake.

#### Scenario: mongomock ausente

- GIVEN sin `mongomock`
- WHEN corre `pytest tests/test_integracion_mongo.py`
- THEN el módulo queda `skipped` con motivo importorskip.

### Requirement: Modo vivo opt-in con GATE_LIVE=1

El sistema MUST exigir `GATE_LIVE=1` para `--vivo`; sin la variable el
script MUST abortar (exit 2) sin red. En vivo MUST comprobar HDFS
`10.22.87.215:50070` y Kafka `10.22.87.215:9092`.

#### Scenario: Vivo sin flag

- GIVEN `GATE_LIVE` ausente o distinto de `1`
- WHEN se ejecuta `--vivo`
- THEN exit 2 con mensaje explícito, 0 conexiones al centro.

#### Scenario: Vivo mañana en clase

- GIVEN `GATE_LIVE=1` y centro alcanzable
- WHEN se ejecuta `GATE_LIVE=1 python scripts/gate_extremo_a_extremo.py --vivo`
- THEN comprueba HDFS/Kafka/Mongo y reporta; si aborta por SHA, se corrige
  y se reejecuta.

### Requirement: Umbrales estrictos del gate

El sistema MUST aplicar: manifiesto raw 354 entradas SHA-256, silver 188,
14 colecciones esperadas, 0 duplicados en reintentos (idempotencia) y
lag 0 en consumidores.

#### Scenario: Umbrales cumplidos

- GIVEN manifiestos locales y lista de 14 colecciones
- WHEN se verifica offline
- THEN 354/188/14/0/lag 0, todos los checks OK.

#### Scenario: Umbral incumplido

- GIVEN un manifiesto con 353 o un SHA distinto
- WHEN se verifica offline
- THEN el check falla con exit != 0 y detalle del fichero.

### Requirement: PENDA-01 centro solo en vivo

El sistema MUST NOT conectar a HDFS/Kafka centro en modo offline; esa
comprobación (PENDA-01) queda pendiente para mañana con el usuario en
clase y red del centro disponible.

#### Scenario: Offline nunca toca el centro

- GIVEN modo `--offline` (defecto)
- WHEN se corre el gate
- THEN 0 conexiones a `10.22.87.215`; PENDA-01 se reporta como pendiente.
