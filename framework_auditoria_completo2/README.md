# Framework de auditoría — fase Obtención + Transformación

**Proyecto:** bigdata-vivienda-euskadi · **Pregunta reto:** ¿puede una persona joven independizarse en Euskadi con su salario?
**Fuentes de verdad:** `archivosReto/RETO 1Evaluacion SBD-BDA.pdf` (8 objetivos + rúbricas RA1/RA3/RA4) y `archivosReto/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (10 evidencias Mongo + pesos).
**Alcance de este framework:** auditar SOLO obtención + transformación (objetivos 1, 2, 6-parcial Python, 8-parcial). HDFS / Kafka / Mongo / Aggregation / índices / transacciones / sharding se auditan SOLO como *readiness* (¿dejamos la base lista para no re-trabajar?), no como implementación.

## Ficheros (8 md + 1 script, límite 10)

| # | Fichero | Qué es | Cuándo usarlo |
|---|---------|--------|---------------|
| 0 | `README.md` (este) | Índice + semáforo + orden de lectura | Siempre primero |
| 1 | `01_alcance_y_reglas.md` | Alcance fase actual, fuera de alcance, reglas raw inmutable | Para no auditar lo que no toca |
| 2 | `02_rubrica_auditable.md` | Rúbrica PDF+DOCX traducida a checks 0/3/7/10 verificables | Para puntuar sin inventar |
| 3 | `03_extraccion.md` | Módulo API + scraping (objetivos 1-2) | Tras tocar `extract/` o `data/raw/` |
| 4 | `04_transformacion.md` | Módulo limpieza + entity resolution (objetivo 6-parcial) | Tras tocar `transform/` o `data/procesado/` |
| 5 | `05_suficiencia_dato.md` | ¿Podemos responder la pregunta? Gate GO/NO-GO a fase Mongo | Antes de saltar a infra/Mongo |
| 6 | `06_readiness_mongo_infra.md` | Contrato que silver debe cumplir para que Mongo sea trivial | Al cerrar fase datos |
| 7 | `07_runbook_agente.md` | Prompt copy-paste + comandos + formato informe P1/P2/P3 | Para lanzar al agente auditor |
| — | `diagnostico.py` | Chequeo rápido ejecutable (raw/silver/cobertura/tipos) | `python framework_auditoria_completo2/diagnostico.py` |

Lo anterior (`01_plantilla_maestra`, `02_modulos_fase`, `03_framework_dato_puro`, `04_auditoria_actualizada`, `entity_audit`, `stats_audit`) queda **absorbido** en estos 8: nada se pierde, se compacta y se ancla a rúbrica.

## Orden de uso (3 pasos)

1. **Rigor:** `01` → `02` (¿qué se exige para el 10?) → `03` + `04` (¿extracción y transformación lo cumplen?).
2. **Ciencia:** `05` (¿los datos bastan para responder con error <20%? Sin SÍ aquí, no seguir a Mongo).
3. **Futuro:** `06` (¿silver deja Mongo/infra sin re-trabajo?) → `07` (lanzar auditoría con prompt).

## Semáforo de fase (lo que el auditor debe concluir)

- 🟢 **GO a Mongo/infra:** raw inmutable OK + gate `verificar_fase_datos.py` 18/18 + `pytest` en verde + `05` dice SÍ (o SÍ con limitaciones comarcales documentadas) + `06` sin P1.
- 🟡 **GO con deuda:** todo lo anterior pero con P2 documentados (cobertura parcial anuncios, Idealista sin key, Pisos geo aproximada).
- 🔴 **NO-GO:** cualquier P1 en `03`/`04`/`05` (raw tocado, codigo_ine roto, tipos que impiden BSON, renta/paros incoherentes sin documentar).

## Reglas de oro (no negociables)

1. **Raw inmutable:** `data/raw/` no se edita a mano. Solo append via extractor + `_raw_guard` + manifest SHA-256 + `.FROZEN`. El auditor lo verifica, no lo repara.
2. **Empírico o nada:** ningún "parece correcto". Todo hallazgo trae comando + número (conteo, %, `nunique`, `pytest`, gate).
3. **Rúbrica manda:** el 10 de cada criterio está definido en `02`. Sin evidencia del umbral 10, se puntúa 7.
4. **Mongo futuro, no presente:** prohibido pedir pipelines/índices/transacciones implementados. Solo `06_readiness`.
