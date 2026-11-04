# Verification Report: renta-joven-18-34

**Fecha:** 2026-11-04
**Comando de tests:** .venv/Scripts/python -m pytest tests -q
**Resultado:** 108 passed, 2 skipped, exit 0. verificar_fase_datos OK 18/18 exit 0.

## Cumplimiento

| Spec | Estado | Evidencia |
|---|---|---|
| JOVEN-18-34 renta 18-34 ponderada anchura | PASS | calcular_renta_joven.py con ponderacion 2/5/5/5 sobre 17 años en contrato y yaml |
| Esfuerzo 18-34 etichetado con legacy | PASS | count municipios con esfuerzo_18_34 252/252 y legacy 16_29 252/252 |
| Subgrupos CAE sin fingir municipal | PASS | 18-24 y 25-34 como escalares CAE documentados |
| Poblacion 18-34 est con metodo | PASS | poblacion_18_34_est 252/252 con metodo 0.10*(0-19)+0.333*(20-64) |

## Issues

- Ninguno critico. Paro 30-34 y poblacion fina no implementados, queda fuera de alcance como decision.

## Veredicto

PASS. Listo para archive y sync de spec.
