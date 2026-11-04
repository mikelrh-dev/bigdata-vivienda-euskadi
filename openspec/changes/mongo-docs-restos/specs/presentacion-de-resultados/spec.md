# Delta for presentacion-de-resultados

## MODIFIED Requirements

### Requirement: Estado de la capacidad presentacion-de-resultados

La capacidad SHALL constar como Hecho, alineada con RA4 v2 (procesamiento, analisis y preparacion de resultados segun brief/RETO 1Evaluacion SBD-BDAv2.pdf).
(Previously: Estado Pendiente.)

#### Scenario: Estado coherente con MongoDB hecho

- GIVEN MongoDB implementado con 13 colecciones y 8 pipelines
- WHEN se lee openspec/specs/presentacion-de-resultados/spec.md
- THEN el Estado es Hecho alineado con RA4 v2
- AND el resto del contenido del spec no cambia

## ADDED Requirements

### Requirement: Coherencia de conteo de robustos

El dashboard SHALL declarar 4 robustos con nombres y n: Bilbao 48020 n 173, Donostia 20069 n 113, Getxo 48044 n 40, Vitoria 01059 n 39.

#### Scenario: Dashboard sin 6 robustos

- GIVEN transform/generar_dashboard_completo.py linea 176
- WHEN se busca 6 robustos en ficheros tracked fuera de archive/historial
- THEN no hay resultados en codigo fuente
- AND la linea declara 4 robustos con nombres y n

### Requirement: MongoDB fuera de pendientes

openspec/project.md SHALL NOT listar MongoDB como pendiente; HDFS y Kafka SHALL quedar como pendientes separados sin inventar su estado.

#### Scenario: Project sin Mongo pendiente

- GIVEN openspec/project.md linea 6
- WHEN se busca Mongo pendiente en project
- THEN no hay resultados
- AND HDFS y Kafka siguen pendientes

### Requirement: Enlace archive verificado

docs/arquitectura_datos.md SHALL enlazar archive/framework_auditoria_completo2/06_readiness_mongo_infra.md, ruta confirmada con git ls-files.

#### Scenario: Enlace archive correcto

- GIVEN docs/arquitectura_datos.md linea 4
- WHEN se resuelve el enlace
- THEN apunta a archive/framework_auditoria_completo2/06_readiness_mongo_infra.md
