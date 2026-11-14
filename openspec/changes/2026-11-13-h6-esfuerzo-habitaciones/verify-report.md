# Verify report: 2026-11-13-h6-esfuerzo-habitaciones

**Fecha:** 2026-11-13 · **Rama:** `fix/regeneracion-procesado-resultados`

## Resultado

Se añade esfuerzo individual:

```text
esfuerzo_pct = mediana_precio_habitacion / salario_joven_2026_ajustado_18_34 * 100
```

- Salario joven 2026 ajustado: **1.718,65 €/mes** (252 filas, valor constante).
- Global: **640 € / 1.718,65 € = 37,2 %**.
- Donostia: **1.200 € = 69,8 %**.
- Bilbao: **600 € = 34,9 %**.

H6 lo muestra en el título del panel de distribución; B4 lo desarrolla con el global y las dos capitales. Es esfuerzo **individual**, no de hogar, y no se compara con la vivienda entera.

## Comandos ejecutados

```bash
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py
.venv/Scripts/python.exe -m pytest tests -q
git diff --check
```

## Evidencia

- H6 regenerado dos veces con el mismo SHA-256: `a2d22af91822d59daef9b42b13ed68e9b92fe706edd2a064881363ba6963d621`.
- `data/resultados/H6_habitaciones_mediana_rango.png` y `docs/presentacion_v2/assets/H6_habitaciones_mediana_rango.png`: mismo SHA.
- Huella gold sin cambios: `e90498a0caa1a0674bf32a2b03a027d51c9707df426bc841c0c3ca99397a5cfc`.
- Verificador del deck: **59/59**.
- Suite completa: **exit 0**, 2 skipped.
- PDF: **30 páginas**; B4 en página 26; texto completo con 640 €, 61 % ≤700 €, 37,2 %, 69,8 % y 34,9 %.
- Revisión visual de la página 26: H6 y B4 sin desbordamiento.
- `git diff --check`: **exit 0**.

## Limitaciones

- **Esfuerzo individual**, no de hogar ni neto: una habitación sobre el salario joven 2026. No debe presentarse como tasa de esfuerzo familiar.
- El salario es constante para todos los municipios (mediana del bloque 2026); no se imputan salarios locales.
- **B4 desde cero sigue bloqueado** si se borra Mongo: falta el loader de `anuncios_habitaciones_unificados` en `storage/load_mongo.py` (deuda P3-06). H6 es reproducible desde Mongo.
- Solo Bilbao (96) y Donostia (66) tienen n≥30; Vitoria (12) y Barakaldo (11) son indicativos.
- No se ha hecho commit ni push.
