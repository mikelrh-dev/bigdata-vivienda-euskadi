# Delta: almacenamiento-y-streaming (INTEGRACION-01, KAFKA-01)

## MODIFIED Requirements

### Requirement: INTEGRACION-01 — Flujo completo hasta MongoDB

El sistema SHALL cargar datos de 2 o más fuentes diferentes y SHALL relacionarlos mediante al menos 1 campo común (criterio RA1 Integración de fuentes v2, PDF línea 91). El sistema SHALL demostrar en vivo el flujo completo desde el origen hasta MongoDB con los componentes encadenados (flujo completo BDA-RA1, PDF línea 79) mediante `scripts/gate_bloque2.py` con salida completa registrada en `docs/trazabilidad_vm.md` (Fecha/Objetivo/Máquina/Comando/Salida/Conclusión). Cualquier comando ejecutado en la VM 192.168.201.162 o contra MongoDB/Kafka/HDFS SHALL recopilarse en `docs/trazabilidad_vm.md` sin omitir su salida.

#### Scenario: Flujo extremo a extremo ejecutado

- GIVEN fuente, HDFS, Kafka y MongoDB en marcha
- WHEN se ejecuta `.venv/Scripts/python.exe scripts/gate_bloque2.py`
- THEN el gate produce 10 anuncios a `anuncios_inmobiliarios`, los consume el grupo `anuncios` con upsert, y los 10 quedan consultables en Mongo por `portal:id_anuncio` + `codigo_ine`
- AND imprime `GATE PASS`, `HUELLA_SHA`, `TOTAL`, `MUNICIPIOS`, `LAG`
- AND la salida completa queda en `docs/trazabilidad_vm.md`

#### Scenario: Trazabilidad VM obligatoria

- GIVEN cualquier cambio o salida en la VM 192.168.201.162
- WHEN se ejecuta un comando por SSH o contra el broker
- THEN `docs/trazabilidad_vm.md` contiene una entrada con Fecha/Objetivo/Máquina/Comando exacto/Salida literal/Conclusión
- AND ningún secreto se incluye en la entrada

### Requirement: KAFKA-01 — Productor y consumidor en Python

El sistema SHALL tener un productor y un consumidor escritos en Python que funcionen sobre broker real y procesen mensajes (Kafka 4.3.1 KRaft, VM 192.168.201.162:9094). El sistema SHALL acreditar modo vivo con `ss -tlnp` LISTEN 9093/9094, `kafka-topics --describe` 3 particiones y consumo con `kafka-console-consumer` registrando el formato `portal:id_anuncio` JSON con precio y municipio, todo recopilado en `docs/trazabilidad_vm.md`.

#### Scenario: Productor y consumidor vivos

- GIVEN el broker en `192.168.201.162:9094`
- WHEN el productor publica y el consumidor lee
- THEN `ss -tlnp` muestra LISTEN 9093 y 9094, el topic tiene 3 particiones y los mensajes son JSON con precio y municipio
- AND el consumidor upserta en Mongo sin duplicar
