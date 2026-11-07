# contrato-reto — Delta

## Purpose

Fijar el texto Docker contractual: la arquitectura real es HDFS centro + Mongo local, sin Docker Compose en el repo. Estado: propuesta (delta desde base Aceptado).

## MODIFIED Requirements

### Requirement: ENTREGABLES-01 — Texto Docker obligatorio

El sistema SHALL describir la arquitectura como «HDFS centro + Mongo local sin Docker Compose en el repo». SHALL NOT afirmar Docker Compose, Docker como despliegue ni `(Docker)` en `AGENT.md`/`README.md` (incl. `README.md:100` y la etiqueta `mongo[Docker]`). Todo documento SHALL usar la frase contractual.
(Previously: `README.md:100` «Docker Compose HDFS + MongoDB» y `(Docker)` en `AGENT.md`.)

#### Scenario: Ninguna mención Docker vigente

- GIVEN `README.md` y `AGENT.md`
- WHEN se buscan con `grep -in "docker"`
- THEN toda mención dice «HDFS centro + Mongo local sin Docker Compose en el repo» y ninguna afirma despliegue Docker
- AND `grep -c "Docker Compose HDFS" README.md` → `0`

## ADDED Requirements

### Requirement: ARQUITECTURA-01 — Invariantes globales

El sistema SHALL mantener: sin Docker; HDFS solo raw 352; Kafka→HDFS, nunca Kafka→Mongo; sin imputar comarcal/IDW como municipal. Nivel (tipología 4/54/194) y Tier (confianza 4/3/57/188) SHALL tratarse como ejes ortogonales en metodología y guion.

#### Scenario: Invariantes verificables

- GIVEN los documentos del repo
- WHEN se revisan arquitectura, metodología y guion
- THEN constan las cuatro invariantes y la frase ortogonal Nivel/Tier
- AND ningún texto afirma Docker, Kafka→Mongo o precio comarcal municipal
