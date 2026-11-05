# Plan para llevar el reto al 10 — bigdata-vivienda-euskadi

Fecha: 2026-11-05
Fuente de verdad: brief/RETO 1Evaluacion SBD-BDAv2.pdf y brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx
Base: specs/contrato-reto/spec.md y 5 specs alineados a PDF y DOCX el 2026-11-05, HEAD 6e5d09e y 30de15c
Estado: solo trazabilidad, sin subir procesado aún, sin gate completo aún, nota actual 7.8/10 en vault y 8.6 unificada tras revisión
Objetivo: cerrar cada criterio no 10 con evidencia ejecutada y trazabilidad total de VM en un único .md

## Principio de trazabilidad total VM

Cada comando ejecutado en la VM 192.168.201.162 y en el clúster centro HDFS 10.22.87.215 debe quedar guardado en un único .md de trazabilidad, por ejemplo docs/trazabilidad_vm.md, con estos campos por cada entrada:

  fecha
  objetivo de la comprobación
  máquina y usuario
  comando exacto
  salida literal completa
  conclusión

Nada se hace en VM sin dejar esa entrada. El log se añade tras cada comando y se verifica con git status y git diff. El ejemplo de formato está en la sección 4 del plan. Ningún log salva secretos.

## Puntos no 10 y orden de ejecución

### Bloque 1 — Deuda y trazabilidad sin código

1. Trazabilidad VM viva, risk 1 mejora 9
   Crear docs/trazabilidad_vm.md con formato total de la sección 4 y primar la entrada de arranque actual pid 1832 con comando de arranque y salida ss y kafka-topics list más README, VER y fecha. Sin cambios en código. Suaviza defensa y pases Tema 8.

2. Vault con salidas reales, risk 2 mejora 9
   Pegar en notas 11 y 12 y 14 salidas explain COLLSCAN a IXSCAN con nReturned y totalDocsExamined, matched_count y modified_count del CRUD y 5 consultas con resultado. Normalizar으면서 16-29 legacy a 18-34 canónico en tablas restantes y corregir docstring validar_renta.py de raw a procesado.

3. Mapa Tema 1 a 8 y checklist de sección 17, risk 1 mejora 7
   Tabla Tema1 a 8 y checklist de 11 ítems en vault 00-reto. Sin tocar código.

4. Di�usión de PgP85 con HTML y G, risk 2 mejora 3
   Marcar dashboard.html y dashboard_completo.html como manuales y dejar G_gaps sin tabla literal. Propuesta: añadir línea en README y en docs/diagramas que son manuales, y dejar solo 4 CSV auto como evidencia RA4.

### Bloque 2 — Infra en vivo con gate y sin regresión

5. HDFS solo raw firmado y procesado listo, risk 2 mejora 9
   Dejar en trabajo procesado listo en local con SHA firmado y lista de ficheros, y entrypoint de subida con --dry-run que liste lo que subiría. No subir procesado hasta que la profesora lo confirme. Con salida WebHDFS LISTSTATUS y SHA.

6. Kafka Python en vivo con 759, risk 2 mejora 8
   producer más consumer Python con grupo anuncios contra 9094, log con 759 enviados y 759 procesados, offsets con mínimo 759. Sin cron y sin consumir con console producer.

7. Gate extremo a extremo con codigo_ine común, risk 2 mejora 9
   Pipeline que sube raw a HDFS, publica 10 anuncios de prueba a Kafka, consume a Mongo con upsert y verifica codigo_ine en Mongo. Resultado: huella SHA y conteo con Mongo de 252 y anuncios con al menos 759.

### Bloque 3 — Mongo y PyMongo

8. Índices con evidencia pegada, risk 2 mejora 7
   explain executionStats antes y después con nReturned y coste en docs/modelo_mongodb.md, más geo, multikey y ESR parcial. Observa lectura pura con estimated_document_count y archivos con gl_10_10.pkl.

9. Modelado con 7 preguntas docx sección 5, risk 3 mejora 7
   Answer literal una a una: consulta junta, frecuencia, arrays sin límite, foto histórica, 1 a 1 1 a N N a M, campo de relación y tipos BSON, en docs/modelo_mongodb.md.

10. Backups y geo con origen claro, risk 3 mejora 5
    Declarar municipios backup e indicadores backup en modelo y subir geo desde 424 según silver. Sin tocar base productiva, lectura pura con colecciones contadas 15 y listing con 2 backups.

11. Validar renta en run_all y docstring, risk 3 mejora 5
    Meter validar_renta.py en transform/run_all.py como paso o dejar justificación firmada. Puerta de salida total con pytest 130 y manifest.

12. Limpieza $unset y alias de consultas, risk 3 mejora 4
    Actualizar clean_mongo.py con $unset explícito y suma de deleted_count, y dejar una sola función canónica de anuncio por municipio, sin romper los actuales 759.

13. Consistencia con commit y abort en test, risk 4 mejora 5
    Transacción multidocumento sobre vivienda_euskadi_test con commit y abort o justificación READ con concerns por separado en docx sección 11.

14. Except genéricos a TypeError y ValueError con log, risk 3 mejora 6
    Pasar _money y ensure_indexes de except Exception a TypeError y ValueError, como ya hacen to_int y to_float.

15. Aggregation con CSV canónico por pipeline, risk 3 mejora 6
    Exportar pipeline_indicadores_municipio, pipeline_alquiler_por_municipio, pipeline_modalidades, pipeline_accesibilidad_extendida y pipeline_vpo_por_municipio a CSV canónico sin duplicar esfuerzo.

### Bloque 4 — Conclusiones y entrega

16. Indicadores 5 con pipeline Mongo verdadero, risk 4 mejora 9
    Crear pipeline Mongo propio para tensión social y paro Lanbide o declararlos silver con justificación. No perder metodo_imputacion en la salida final ni fillna mediana sin flag is_imputed.

17. Respuesta con 4 robustos y matriz por etapa, risk 3 mejora 8
    Comparativa a 4 con Vitoria y tabla O1 a O4 con mediana 26,61 oficial 18-34 y 25,2 sobre 30. Advertir Getxo 40 contra Vitoria 39 y 1 anuncio de diferencia.

18. Guion Tema 8 de 1 página, risk 2 mejora 9
    Embedding, índices y atomicidad con cadena offline actualizada a HDFS centro y Kafka pid 1832, sin dejar 16-29 sin marcar legacy.

## Gates por bloque

  Bloque 1: pytest tests/test_contrato.py en verde, 54 passed, más manifest 353 y 184 OK, git status limpio salvo nuevo trazabilidad_vm.md y vault
  Bloque 2: HDFS LISTSTATUS 200 sin legacy y SHA del 1 fichero, Kafka DESCRIBE 3 particiones y offsets 759, gate con inserciones en Mongo consultables por codigo_ine y 759 más 10 de prueba, pytest contrato 54 passed
  Bloque 3: pytest tests 130 passed, explain con COLLSCAN y IXSCAN y totalDocsExamined 1, pipelines 8 con stages $group y $lookup y $unwind, CRUD con matched_modified_deleted en test, consistencia en test sin tocar prod por defecto
  Bloque 4: CSV 253 y 253 y 3 auto con huella, comparativa 4 con paro Lanbide no nulo, guion Tema 8 con 10 criterios y lagunas documentadas

## Riesgos y límites

  HDFS procesado y Kafka Python vivo y gate e2e y tensión y paro en silver siguen en SHOULD hasta que se ejecuten los bloques 2 y 4
  Pesos Tema 8 15 15 20 15 10 15 10 no se suman a v2 46,7 13,3 40
  Clave de api.txt en historial 5166d32 sin rotación, queda fuera de este plan hasta que la rotés y dejes traza

## Secuencia recomendada

Seguir 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 en orden. 1 a 4 no tocan código y ya suben la nota. 5 a 7 cierran BDA. 8 a 15 cierran RA3 y Tema 8. 16 a 18 cierran RA4. Cada comando en VM se anota en docs/trazabilidad_vm.md.

## Formato ejemplo entrada en docs/trazabilidad_vm.md

### 2026-11-05 Bloque 2 Kafka arranque

Objetivo: comprobar broker arriba tras reboot
Máquina: VM 192.168.201.162 usuario mikel
Comando:
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162
    ~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties
Salida literal:
    LISTEN 0 50 *:9093 users:((java,pid=1832,fd=135))
    LISTEN 0 50 *:9094 users:((java,pid=1832,fd=218))
    anuncios_inmobiliarios
    __consumer_offsets
Conclusión: broker arriba en 9094 con topic de 3 particiones, Python aún sin enviar
