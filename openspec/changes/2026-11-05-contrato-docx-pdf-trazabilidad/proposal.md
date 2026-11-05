# Proposal: Contrato docx-PDF trazabilidad

## Intent

Alinear `openspec/specs/contrato-reto/spec.md` con las fuentes primarias
`brief/RETO 1Evaluacion SBD-BDAv2.pdf` y
`brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, sin romper tests ni
pipelines y sin cambios de código Python.

## Scope

### In Scope

- Cabecera de trazabilidad con PDF y docx, fecha 2026-11-05, en
  `openspec/specs/contrato-reto/spec.md`.
- Cotejo literal de tablas BDA RA1, SBD RA1, RA3, RA4 y pesos
  46,7/13,3/40 contra PDF, con referencia de línea.
- Mapa trazable docx secciones 5, 9, 10, 12, 4/14/15/17 a requisitos
  existentes: MODELO-01, INDICES-01, DISTRIBUIDA-01, PYMONGO-PRO-01,
  ENTREGABLES-01.
- Nota de extensiones propias P-01 a P-08, canónico 18-34 y
  CARGA-SEGURA como extensión, no requisito v2.

### Out of Scope

- Cambios de código Python, pipelines, índices o datos.
- Nuevos requisitos con SHALL que puedan romper tests.
- Push, git add o commit.

## Approach

- Solo edición de `openspec/specs/contrato-reto/spec.md` más propuesta y
  informe en esta carpeta.
- SHALL solo donde ya cumplimos; SHOULD donde no cumplimos (HDFS
  procesado, Kafka Python vivo, integración extremo a extremo,
  tensión/paro en silver).
- Verificación con `pytest tests/test_contrato.py` y
  `extract/generar_manifest.py --verify`.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Faltan cadenas que exige `test_p08` | Bajo | Solo inserciones, sin borrados de criterios/requisitos |
| Confundir pesos Tema 8 con v2 | Bajo | Cabecera y mapa separan 46,7/13,3/40 de sección 16 |
| Nuevos SHALL que rompen contrato | Bajo | Mapeo a requisitos existentes, SHOULD en no cubiertos |
| Archivo ajeno modificado en paralelo | Medio | No se toca; se registra en git status |

## Success Criteria

- [ ] Cabecera y referencias PDF/docx presentes.
- [ ] Tablas literales cotejadas, sin diferencias pendientes.
- [ ] Mapa docx 5/9/10/12/4/14/15/17 mapeado sin requisitos nuevos.
- [ ] `pytest tests/test_contrato.py -q` en verde.
- [ ] `generar_manifest.py --verify` en verde.
