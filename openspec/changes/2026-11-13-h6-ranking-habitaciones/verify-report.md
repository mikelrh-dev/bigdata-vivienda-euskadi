# Verify report: 2026-11-13-h6-ranking-habitaciones

> **Actualización 2026-11-13:** H6 incorpora esfuerzo individual; el SHA vigente es
> `a2d22af91822d59daef9b42b13ed68e9b92fe706edd2a064881363ba6963d621` y la verificación
> actual está en `../2026-11-13-h6-esfuerzo-habitaciones/verify-report.md`.

**Fecha:** 2026-11-13 · **Rama:** `fix/regeneracion-procesado-resultados`

## Resultado

H6 pasa de mediana/min-max logarítmico a dos paneles:

- **Izquierda:** ranking n≥10 con IC95 bootstrap determinista; azul oscuro = firme (n≥30), azul claro = indicativo.
- **Derecha:** distribución de los 200 precios, mediana 640 €, Q1–Q3 500–1.200 €, 61 % ≤700 €; outlier máximo 109.000 € anotado y fuera del histograma (corte 2.500 €).

B4 cita 201 anuncios / 9 municipios / 200 con precio, Bilbao y Donostia como firmes, Vitoria y Barakaldo como indicativos, y Getxo y el resto fuera del ranking. No se mezcla con vivienda entera.

## Comandos ejecutados

```bash
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py
.venv/Scripts/python.exe -m pytest tests -q
git diff --check
```

## Evidencia

- `pipeline_habitaciones_precios()`: **200** documentos, todos con `precio_eur` y `codigo_ine`.
- H6 regenerado dos veces con el mismo SHA-256: `5f24bf447719a8d6d5c7981354c3a527f8d98a469d438477a77c5fa06b34475f`.
- `data/resultados/H6_habitaciones_mediana_rango.png` y `docs/presentacion_v2/assets/H6_habitaciones_mediana_rango.png`: **mismo SHA**.
- Huella gold: `e90498a0caa1a0674bf32a2b03a027d51c9707df426bc841c0c3ca99397a5cfc` (sin cambios en CSV).
- Verificador del deck: **56/56**.
- Suite completa: **exit 0**, 2 skipped.
- PDF: **30 páginas**; B4 en página 26; contiene “Mediana global 640 €”, “61 % ≤700 €” y “ranking n≥10”.
- `git diff --check`: **exit 0**.
- H8 no se toca: se retiró del set de sync; H8b sí se sincroniza porque es el asset de B5.

## Limitaciones

- **B4 desde cero sigue bloqueado** si se borra Mongo: falta el loader de `anuncios_habitaciones_unificados` en `storage/load_mongo.py` (deuda P3-06). H6 es reproducible desde Mongo y el asset se sincroniza solo; no se ha tocado silver.
- Solo Bilbao (96) y Donostia (66) tienen n≥30; Vitoria (12) y Barakaldo (11) son indicativos y sus IC se solapan. No se rankean los municipios con n=1–3.
- No se ha hecho commit ni push.
