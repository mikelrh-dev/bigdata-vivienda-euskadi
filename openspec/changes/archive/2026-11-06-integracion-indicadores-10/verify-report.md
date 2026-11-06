# Verify report: integracion-indicadores-10

Fecha: 2026-11-06 · Rama: `master` (desde `cierre/suficiencia-auditoria` 790273e)
Change: `openspec/changes/2026-11-06-integracion-indicadores-10/`
Scope: INTEGRACION-01 (7>10) + INDICADORES-01 (7>10). HDFS procesado explícitamente fuera (solo-raw vigente). Toda salida VM recopilada en `docs/trazabilidad_vm.md`.

## Evidencia por tarea

### 2.1 Broker vivo sin SP (sin escrituras)
Comando:
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=6 mikel@192.168.201.162 "ss -tlnp | grep -E ':9093|:9094'; ~/kafka/bin/kafka-topics.sh --describe --topic anuncios_inmobiliarios --bootstrap-server 192.168.201.162:9094; ~/kafka/bin/kafka-console-consumer.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios --from-beginning --max-messages 2 --timeout-ms 15000"
Salida (resumen literal en trazabilidad):
    LISTEN *:9093 (java pid 1817), *:9094 (java pid 1817)
    Topic anuncios_inmobiliarios, PartitionCount 3, RF 1
    {"portal":"fotocasa","id_anuncio":"159915860",...,"precio_eur":995.0,"codigo_ine":"20055","municipio":"Arrasate/Mondragón"} ...

### 2.2 Gate e2e
Comando:
    .venv/Scripts/python.exe scripts/gate_bloque2.py
Salida:
    HDFS_LEG LIST_BASE ['raw'], LIST_RAW_COUNT 200, STATUS_RAW childrenNum=200, CERO_ESCRITURAS
    HUELLA_ESPERADA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
    PRODUCIDOS 10, Procesados: 10, CONSUME_RET 10
    CONSULTA_POR_CODIGO_INE 1 doc(s) x10 OK
    LAG_TOTAL 0, VERIFICADOS 10/10, TOTAL 759, MUNICIPIOS 252
    GATE PASS

### 2.3 Verificación Mongo
Cada anuncio del subset consultable por `portal:id_anuncio` + `codigo_ine` (1 doc), total 759 (upsert idempotente, no 769), municipios 252, lag 0.

### 3.1 Matriz 5 non-legacy
`docs/matriz_indicadores.md`: 1 esfuerzo 18-34, 2 tensión, 3 paro, 4 precio m2, 5 VPO terminadas ‰ (`vpo_terminadas_por_mil`, Open Data 73 + dim_municipios por `codigo_ine`). Legacy 16-29 archivado fuera de tabla, nota "NO cuenta como indicador".

### 3.2 CSV + huellas
    .venv/Scripts/python.exe analysis/run_analisis_mongo.py
    mongo_esfuerzo_por_municipio.csv: 252 filas (253 líneas)
    mongo_alquiler_por_municipio.csv: 252 filas (253 líneas)
    mongo_modalidades.csv: 2 filas (3 líneas)
    mongo_accesibilidad_extendida.csv: 252 filas (253 líneas)
    mongo_vpo_por_municipio.csv: 322 filas (323 líneas)
    mongo_vpo_terminadas_por_municipio.csv: 251 filas (252 líneas) [NUEVO]
    huella: 08665d03687bbbde663831de8872d129983252de1881027a2e243bfd86f4c30a
    reproducibilidad: ok
    sha256sum: esfuerzo 731d16..., alquiler ff39e8..., modalidades 71a729..., comparativa 9dc4e8..., terminadas d9a512...
Huellas actualizadas en matriz sin teclear (calculadas con `sha256sum`).

### 3.3 Test conteo
Nuevo `tests/test_indicadores.py`: filas ["1","2","3","4","5"], VPO presente, legacy fuera de conteo.

### 3.4 README
`README.md:159`: ya dice G auto desde `run_analisis_mongo.py` y 6 CSV (corregido "4 CSV" + G literal stale).

### 4.1 Suite completa
    .venv/Scripts/python.exe -m pytest tests -q
    137 passed in 13.72s
(136 anteriores + 1 nuevo test_indicadores; sin destructivos en prod)

### 4.2 Gate fase datos
    .venv/Scripts/python.exe scripts/verificar_fase_datos.py
    RESULTADO: OK 18/18 (manifest 354, dim 252, 11 pytest 27 passed, ...)

## Desviaciones
- `min.insync.replicas=2` con RF=1 permanece como limitación documentada (no bloqueó el gate).
- Tensión/paro siguen calculados en silver y expuestos por Mongo; matriz los declara "silver justificado" con `is_imputed`/`metodo_imputacion`.
- HDFS procesado sigue sin subirse (solo-raw 2026-11-05). HDFS-01 queda SHALL originales + SHOULD procesados.
- `mongo_vpo_por_municipio.csv` (322, promociones) sigue exportándose; el indicador 5 usa `mongo_vpo_terminadas_por_municipio.csv` (251).

## Veredicto
INTEGRACION-01 10/10 (gate PASS logueado), KAFKA-01 10/10 (vivo pid 1817), INDICADORES-01 10/10 (5 non-legacy con CSV y test). Pendiente archive (4.4).
