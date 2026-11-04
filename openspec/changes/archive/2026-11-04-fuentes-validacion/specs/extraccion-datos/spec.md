# Delta for extraccion-datos

## ADDED Requirements

### Requirement: GATE-JOIN-01 — Nueva fuente con join previo

El sistema MUST NOT crear un extractor nuevo sin antes ejecutar un join real contra dim_municipios 252. La validación SHALL contar municipios alcanzados, filas y códigos INE de 5 dígitos. Solo una cobertura documentada alta autoriza el extractor.

#### Scenario: Fuente con cobertura insuficiente no entra

- GIVEN una fuente candidata sin join
- WHEN se evalúa su alta
- THEN el sistema la marca baja
- AND no se crea extractor ni carga en Mongo

#### Scenario: Fuente con cobertura alta entra con provenance

- GIVEN una fuente con municipios alcanzados documentados
- WHEN se aprueba el extractor
- THEN el raw guarda fuente, url, fecha, n_registros y sha256
- AND el manifest se regenera

## MODIFIED Requirements

### Requirement: COMPLEMENTARIOS-01 — Salarios y población

El sistema SHALL incluir información complementaria de **salarios**, población
y al menos otro indicador relevante. La población 15-29 SHALL NOT derivarse de bandas 0-19 y 20-64; requiere bandas de 5 años o quinquenios. El salario SHALL NOT anunciarse como municipal sin tabla con ámbito municipal y edad.
(Previously: población municipal sin exigir bandas finas y salario sin granularidad explícita.)

#### Scenario: El salario está presente y es real

- GIVEN que Eustat no publica salario municipal por edad
- WHEN se incorpora el salario
- THEN proviene del INE (EPA, salario medio por grupo de edad) o del dato
  oficial del Observatorio Vasco de la Juventud
- AND el valor NO se simula ni se inventa

#### Scenario: La población por municipio está disponible

- GIVEN la tabla de población de Eustat
- WHEN se extrae
- THEN cada municipio tiene su población y su código INE
