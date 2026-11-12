# Spec: enriquecimiento de la capa 2026 (capa paralela, 2024 intacto)

## Objective

Reforzar la argumentación de 2026 sin tocar el esfuerzo canónico 2024 ni `data/raw`
ni `extract/`. La capa 2026 es una **capa de oferta** (precio de anuncio sobre salario
joven), no una segunda medición oficial. Todo añadido debe ser regenerable con `.py`
desde raw y declarar `n`, intervalo y supuesto.

Problemas que resuelve:

1. Anuncios con `motivo_exclusion` contaban en la mediana 2026 (10 de 297).
2. La comparación 26,61 % (2024) vs 79,3 % (2026) mezcla numerador, denominador y muestra.
3. No había intervalos de confianza: 31 de 52 municipios tenían n=1.
4. La cobertura se contaba por municipios (52/252) y no por población joven.
5. El ancla 2024 no estaba contrastada con una fuente fiscal independiente (SERPAVI).

## Tech Stack

Python 3.12 (`.venv`), pandas, numpy, matplotlib. Sin dependencias nuevas.

## Commands

```
python transform/run_all.py
python analysis/calibrar_premium_oferta.py
python analysis/comparar_esfuerzo_2024_2026_misma_base.py
python analysis/calcular_brecha_esfuerzo_2024_2026.py
python analysis/cobertura_representatividad_2026.py
python analysis/validar_alquiler_serpavi.py
python visuals/mapa_esfuerzo_mercado_2026.py
python visuals/graficos_esfuerzo_mercado_2026.py
python visuals/assets_presentacion_esfuerzo_mercado_2026.py
python scripts/regenerar_capa_2026.py        # todo lo anterior en orden
pytest -q
python scripts/verificar_gobernanza.py
python scripts/verificar_fase_datos.py
python scripts/gate_extremo_a_extremo.py --offline
```

## Project Structure

- `transform/` → silver (declarado en `transform/run_all.py`).
- `transform/_anuncios_2026.py` → librería: una sola definición del filtro de anuncios.
- `analysis/` → derivados analíticos; no orquestados por `run_all`, sí por
  `scripts/regenerar_capa_2026.py`.
- `visuals/` → figuras y assets de la presentación.
- `tests/` → pytest.

## Code Style

```python
def cargar_anuncios_2026() -> tuple[pd.DataFrame, dict[str, int]]:
    """Devuelve (anuncios válidos, contadores de auditoría)."""
```

Convenciones: docstring con entradas/salidas, `from __future__ import annotations`,
encoding `utf-8-sig`, `codigo_ine` siempre `zfill(5)`, sin literales de cifras en el deck.

## Testing Strategy

`tests/test_esfuerzo_mercado_2026.py` valida estructura y conciliación del CSV:
252 filas, `sum(n_anuncios_2026) == anuncios usados`, ningún `motivo_exclusion`
contado, orden de IC, coherencia de flags, columnas legacy presentes.

## Boundaries

- **Always:** preservar columnas existentes de los CSV; declarar `in`/`out` en el DAG;
  semilla fija en el bootstrap; documentar supuestos en el propio CSV.
- **Ask first:** cambiar el esfuerzo canónico 2024 o el contrato.
- **Never:** escribir en `data/raw`, modificar `extract/`, inventar cifras en el HTML,
  presentar la capa 2026 como oficial.

## Success Criteria

1. `esfuerzo_mercado_2026.csv` con 252 filas; 287 anuncios usados; 10 excluidos
   registrados en `n_excluidos_2026`.
2. IC95 % bootstrap por municipio con `ic95_lo ≤ mediana ≤ ic95_hi`.
3. `comparacion_esfuerzo_2024_2026_misma_base.csv` con 2024 y 2026 bajo el mismo
   denominador salarial.
4. `brecha_esfuerzo_2024_2026.csv` declara `tipo_diferencia` y el equivalente oficial
   calibrado, conservando `brecha_pp_18_34`.
5. `cobertura_representatividad_2026.csv` con la cobertura por población 18-34.
6. `validacion_alquiler_2024_serpavi.csv` con el contraste Eustat vs SERPAVI 2024.
7. Ningún fichero 2024 cambia de valor; `dim_municipios_enriquecido.csv` intacto.
8. `pytest`, gobernanza y fase de datos en el mismo estado que antes (FAIL 07 conocido).

## Open Questions

- El supuesto de premium constante (anuncio vs registrado) se publica como diagnóstico
  con `flag_calibracion`, nunca como medición oficial.
- IPC: el raw solo trae un valor fallback; no se sustituye (raw inmutable). Se publica
  banda de escenarios y `flag_ipc=fallback` visible.
