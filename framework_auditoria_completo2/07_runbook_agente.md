# 07 · Runbook del agente auditor (copy-paste + formato informe)

## Prompt (pegar tal cual, rellenar [FASE])

```markdown
Actúa como Principal Data Engineer + Data Scientist del proyecto bigdata-vivienda-euskadi.
MODO: SOLO LECTURA (prohibido modificar data/, extract/, transform/, tests/ hasta que yo autorice el plan).

1. Lee framework_auditoria_completo2/README.md, 01, 02 y el módulo [03_extraccion | 04_transformacion | 05_suficiencia | 06_readiness].
2. Lee openspec/specs/contrato-reto/spec.md + config/parametros_estudio.yaml.
3. Ejecuta (no supongas): `python framework_auditoria_completo2/diagnostico.py`,
   `python transform/run_all.py --check`, `python verificar_fase_datos.py`, `pytest tests/ -q`.
   Para dudas finas usa pandas (`nunique`, `groupby.size`, `corr`, IQR) y `grep`.
4. Devuelve EXCLUSIVAMENTE el informe de abajo. Sin refactors, sin "deberías".
```

## Comandos base (el agente los ejecuta, no los inventa)

- `python framework_auditoria_completo2/diagnostico.py`
- `python transform/run_all.py --check` · `python verificar_fase_datos.py` · `pytest tests/ -q`
- `git status --porcelain data/raw/` (debe estar limpio) · `git ls-files | grep -iE "\.env$|api\.txt"` (vacío salvo `.env.example`)
- `grep -rn "pd.read_csv(" transform/ | grep -v dtype` (vacío) · `grep -rn "http://" extract/17_osrm_tiempos.py` (vacío)

## Formato informe (obligatorio, nada fuera de esto)

1. **Métricas reales:** tabla `check | valor | comando/fuente` (conteos, %, tiempos, tests, gate).
2. **Rúbrica:** tabla `criterio | 0/3/7/10 o DIFERIDO | evidencia` (sin evidencia del 10 → 7).
3. **Hallazgos:** `P1 Crítico / P2 Alto / P3 Medio`, cada uno con `dónde (fichero:línea) + por qué baja nota o rompe futuro + cómo verificarlo`.
4. **Veredicto fase:** 🟢 GO / 🟡 GO con deuda / 🔴 NO-GO + frase de suficiencia (`05`) + frase Mongo (`06`).
5. **Plan quirúrgico:** `fichero → cambio → esfuerzo (min) → riesgo 0-10 → verificación`. Espera mi OK antes de editar.

## Prohibiciones del auditor

Pedir pipelines/explain/transacciones implementados · regenerar raw (scraping/descargas) · tocar `data/raw/` · puntuar 10 sin evidencia · auditar `openspec/plan/` (local no versionado).
