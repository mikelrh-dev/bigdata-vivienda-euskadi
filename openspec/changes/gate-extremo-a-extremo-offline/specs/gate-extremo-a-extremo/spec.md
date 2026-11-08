# Delta for gate-extremo-a-extremo

## ADDED Requirements

### Requirement: E2E offline hermético

El sistema MUST ejecutar el gate por defecto en modo `--offline` sin red,
sin tocar `data/raw`/`.FROZEN` ni escribir en servicios reales.

#### Scenario: Gate offline pasa en seco

- GIVEN el repo checkout con manifiestos locales
- WHEN se ejecuta `python scripts/gate_extremo_a_extremo.py --offline`
- THEN exit 0, sin red ni escrituras fuera de `tmp_path`.

### Requirement: Integración Mongo con mongomock o skip

El sistema MUST validar la lógica Mongo sobre mongomock; sin mongomock el
test MUST quedar en skip, nunca en fallo ni conectado al centro.

#### Scenario: mongomock ausente

- GIVEN sin `mongomock`
- WHEN corre `pytest tests/test_integracion_mongo.py`
- THEN el módulo queda `skipped`.

### Requirement: Modo vivo opt-in con GATE_LIVE=1

El sistema MUST exigir `GATE_LIVE=1` para `--vivo`; sin la variable MUST
abortar (exit 2) sin red. En vivo MUST comprobar HDFS
`10.22.87.215:50070` y Kafka `10.22.87.215:9092`.

#### Scenario: Vivo sin flag

- GIVEN `GATE_LIVE` ausente o distinto de `1`
- WHEN se ejecuta `--vivo`
- THEN exit 2 sin conexiones al centro.

### Requirement: Umbrales estrictos del gate

El sistema MUST aplicar: manifiesto raw 354 entradas SHA-256, silver 188,
14 colecciones esperadas, 0 duplicados en reintentos y lag 0.

#### Scenario: Umbral incumplido

- GIVEN un manifiesto con 353 entradas o SHA distinto
- WHEN se verifica offline
- THEN el check falla con exit != 0 y detalle del fichero.

### Requirement: PENDA-01 centro solo en vivo

El sistema MUST NOT conectar a HDFS/Kafka centro en modo offline; esa
comprobación queda pendiente para mañana en clase.

#### Scenario: Offline nunca toca el centro

- GIVEN modo `--offline` (defecto)
- WHEN se corre el gate
- THEN 0 conexiones a `10.22.87.215`; PENDA-01 pendiente.
