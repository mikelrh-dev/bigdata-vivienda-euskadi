# 01 · Alcance y reglas — fase Obtención + Transformación

## 1. Fuente de verdad

- `archivosReto/RETO 1Evaluacion SBD-BDA.pdf` → 8 objetivos + rúbricas RA1 (BDA), RA3 + RA4 (SBD). Es lo que pone nota.
- `archivosReto/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` → 10 bloques de evidencia Mongo + pesos (Modelado 15%, CRUD 15%, Aggregation 20%, Índices 15%, Transacciones 10%, PyMongo profesional 15%, Defensa 10%). En esta fase SOLO sirve para `06_readiness`, no para exigir implementación.

## 2. Los 8 objetivos del PDF, mapeados a fase

| # PDF | Objetivo | Fase actual (datos) | Futuro (infra/Mongo) |
|------|----------|---------------------|----------------------|
| 1 | Recopilar alquiler/compraventa via API **y** scraping | ✅ SÍ se audita (`03`) | — |
| 2 | Complementarios (salarios, población, otros) | ✅ SÍ se audita (`03`+`05`) | — |
| 3 | HDFS originales | ❌ NO (solo readiness: layout raw separado `raw/` vs `procesado/`) | HDFS real |
| 4 | Kafka productor/consumidor nuevos anuncios | ❌ NO | Kafka real |
| 5 | Guardar en MongoDB | ❌ NO (solo readiness `06`) | Mongo real |
| 6 | Limpieza/transform con PyMongo | ⚠️ PARCIAL: se audita limpieza en Python (`04`); la parte PyMongo es futura | PyMongo real |
| 7 | Consultas + Aggregation | ❌ NO (solo readiness: ¿silver permite esos pipelines?) | Mongo real |
| 8 | Presentar y justificar conclusiones | ⚠️ PARCIAL: se audita suficiencia + trazabilidad (`05`); gráficos finales son futuros | RA4 real |

**Consecuencia:** un auditor que pida "pipelines con 4 etapas" o "explain() antes/después" en esta fase está auditando fuera de alcance. Se marca como tal y no baja nota de fase datos.

## 3. Entregables que SÍ se exigen ya (PDF §Entregables)

1. Código Python organizado y documentado (`extract/`, `transform/`, `tests/`).
2. Datos: raw inmutable + silver trazable (el HDFS/Mongo vendrán después; el auditor verifica que el layout ya separa `data/raw/` vs `data/procesado/`).
3. Arquitectura: esquema del recorrido origen → raw → silver (puede ser `docs/` + `openspec/`).
4. Informe parcial: cobertura, metodología, limitaciones (no informe final).
5. Demo: `verificar_fase_datos.py --check` + `pytest` reproducibles.

## 4. Reglas raw inmutable (contrato)

- `data/raw/` es append-only. Ningún transform escribe ahí salvo captura dirigida con `_raw_guard` (`transform/_raw_guard.py`).
- Integridad: manifest SHA-256 + `.FROZEN` + tests `test_raw_inmutable.py` / `test_raw_guardrails.py`.
- Encoding/lectura: escritura raw en UTF-8 (BOM donde aplique a CSV Eustat); lectura silver con `dtype=str` para no perder el cero de Álava (`01xxx`); `codigo_ine` siempre 5 dígitos normalizado en silver.
- El auditor NUNCA regenera raw (no re-scrapea, no re-descarga) salvo que el plan autorice y quede registrado. Si falta una fuente, se documenta como gap, no se "arregla" tocando raw.

## 5. Mapa de carpetas que el auditor debe conocer

- `extract/` (38 scripts): API + scraping → `data/raw/`. Orquestador `extract/main_ingest.py`, común `extract/_common.py` (logger, Cliente, guardar_json), manifests `extract/generar_manifest.py`, `extract/normalizar_metadata.py`.
- `transform/` (43 scripts): raw → `data/procesado/`. Orquestador `transform/run_all.py` (SCRIPTS + EXCLUIDOS declarados), guard `transform/_raw_guard.py`, resolución nombres `transform/muni_resolve.py`, dimensiones `transform/dim_municipios.py`, vistas `transform/generar_*`, limpieza `transform/limpiar_*`, validación `transform/validar_renta.py` (QA bajo demanda).
- `tests/` + `verificar_fase_datos.py` (gate 18 checks) + `verificacion_crudos.py`: lo que el auditor ejecuta, no lo que edita.
- `docs/` (metodología, trazabilidad, gaps) + `openspec/specs/contrato-reto/spec.md` + `config/parametros_estudio.yaml`: el contrato que la auditoría verifica.
