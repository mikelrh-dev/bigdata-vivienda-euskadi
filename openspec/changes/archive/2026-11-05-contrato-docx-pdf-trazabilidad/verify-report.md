# Verify report: Contrato docx-PDF trazabilidad (2026-11-05)

## Alcance

- Archivo editado por esta tarea: `openspec/specs/contrato-reto/spec.md`
- Archivos creados: `openspec/changes/2026-11-05-contrato-docx-pdf-trazabilidad/proposal.md` y `verify-report.md`
- Fuentes cotejadas: `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y
  `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`
- HEAD: 4fb22d8

## Cotejo literal

- BDA RA1: PDF líneas 72-79. Sin diferencias literales.
- SBD RA1: PDF líneas 85-94, peso 46,7 % línea 87. Sin diferencias literales.
- SBD RA3: PDF líneas 98-109, peso 13,3 % línea 100. Sin diferencias literales.
- SBD RA4: PDF líneas 113-123, peso 40 % línea 115. Sin diferencias literales.
- Tema 8 sección 16: docx líneas 228-252, pesos 15/15/20/15/10/15/10.
  Sin diferencias literales.
- No se corrigió texto literal porque no hubo diferencia.

## Verificación real

Comando: `.venv/Scripts/python.exe -m pytest tests/test_contrato.py -q`

```text
......................................................                   [100%]
54 passed in 0.65s
EXIT:0
```

Comando: `.venv/Scripts/python.exe extract/generar_manifest.py --verify`

```text
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\docs\raw_manifest_sha256.txt (353 entradas, 0 errores)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\data\procesado\manifest_sha256.txt (184 entradas, 0 errores)
EXIT:0
```

## Git status

Antes:

```text
?? docs/analisis_vault_vs_rubrica.md
```

Después:

```text
M openspec/specs/contrato-reto/spec.md
 M openspec/specs/mongodb-y-analisis/spec.md
?? docs/analisis_vault_vs_rubrica.md
?? openspec/changes/2026-11-05-contrato-docx-pdf-trazabilidad/
```

No se hizo `git add`, commit ni push.

## Riesgos

- HDFS procesado, Kafka Python vivo, integración extremo a extremo y
  tensión/paro en silver quedan como SHOULD porque hoy no están
  cerrados. No se elevan a SHALL para no romper contrato.
- `openspec/specs/mongodb-y-analisis/spec.md` aparece modificado por
  trabajo paralelo ajeno a esta tarea; no se editó aquí.
