# Informe Pre-Gold — T1/T2/T3 (2026-10-29)

## Objetivo
Ejecutar la contra-replanificación Pre-Gold sobre la capa Silver: segregación lógica del mercado, ampliación de volumen append-only y globbing validado, sin tocar `data/raw/` inmutable.

## Tarea 1 — Segregación lógica (Silver)
- Script: `transform/generar_vistas_mercado.py`
- Vistas generadas:
  - `anuncios_vivienda_residencial.csv`: **569** registros (modalidad != temporal, excluye habitaciones).
  - `anuncios_habitaciones_unificados.csv`: **201** registros (Fotocasa + Pisos normalizados, dedup por portal+url).
- El maestro `anuncios_unificados.json` se conserva para compatibilidad con tests y consumidores.

## Tarea 2 — Ampliación de volumen (Raw append-only)
- Nuevo extractor: `extract/09_fotocasa_dirigido.py` (scraping por municipio, append-only).
- Lotes generados:
  - `anuncios_fotocasa_dirigido_20261029.json` (5 anuncios, piloto).
  - `anuncios_fotocasa_dirigido_20261029_223523.json` (73 anuncios, lote completo).
- Registrados en `docs/raw_manifest_sha256.txt` (2 nuevas entradas).

## Tarea 3 — Globbing validado (Silver)
- `transform/unificar_anuncios.py` actualizado:
  - Schema guard: valida JSON, `datos` lista, metadata `n_anuncios`, claves básicas.
  - Patrones estrechos: `anuncios_pisos_dirigido_*.json` y `anuncios_fotocasa_dirigido_*.json`.
  - Logging de integrados/saltados.
- Resultado unificación: **872** anuncios (869 → 872 tras dedup).

## Tests
- `pytest -q`: **59 passed**, 0 fallos.

## Deuda remanente
- Cobertura muestral: solo 4 municipios con n≥30.
- Habitaciones no integradas en el unificado (vista separada disponible).
- Fotocasa directed con slug de municipios con barra (ej. Agurain/Salvatierra) falla por URL; requiere normalización de slug.

## Veredicto
T1–T3 completados y verificados. Pipeline de datos listo para siguiente ciclo (ampliación de muestra o infraestructura).