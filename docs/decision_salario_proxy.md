# Decisión: Uso de renta municipal como proxy de salario joven

**Fecha:** 2026-10-29
**Contexto:** El proyecto necesita un indicador de capacidad económica municipal para calcular la tasa de esfuerzo (alquiler / ingresos joven).

## Fuentes verificadas

1. **OVJ (Observatorio Vasco de la Juventud)** — Irekia, 13/10/2025:
   - Salario neto medio asalariado 18-34 años (2024, pagas prorrateadas): **1.564 €/mes**
   - Salario neto medio asalariado 16-29 años (2024): **1.381 €/mes**
   - Fuente URL: https://www.irekia.euskadi.eus/es/news/105137
   - Archivo raw: `data/raw/ovj_salario_joven_2024.json`

2. **Eustat renta edad** — `data/raw/eustat_renta_edad.csv` (2024, sexo Total, CAE):
   - Renta fiscal media 18-19 años: 1.599 €/año
   - Renta fiscal media 20-24 años: 8.156 €/año
   - Renta fiscal media 25-29 años: 20.109 €/año
   - Renta fiscal media Total CAE: 28.170 €/año

## Proxies calculados

| Proxy | Fórmula | Ratio | Esfuerzo (mediana) |
|-------|---------|-------|-------------------|
| Fiscal (media simple 3 tramos) | (1599+8156+20109)/3 / 28170 | 0,3534 | 76,3% (max) |
| Salarial 18-34 (OVJ) | 1564*12 / 28170 | 0,6662 | 40,5% (min) |
| Salarial 16-29 (OVJ) | 1381*12 / 28170 | 0,5883 | — |

## Rango de esfuerzo

- **Esfuerzo mínimo (salarial):** mediana 40,5% — asume renta joven = salario neto asalariado.
- **Esfuerzo máximo (fiscal):** mediana 76,3% — asume renta joven = media simple de tramos fiscales.
- **Conclusión:** el esfuerzo real está en el intervalo **[40,5% – 76,3%]**, no en un único valor.

## Limitaciones

- El ratio fiscal es media simple (no ponderada por población) porque Eustat no publica población por tramo de edad a nivel municipal ni CAE.
- El salario OVJ es para Euskadi (CAE), no municipal. Se aplica como ratio uniforme a la renta personal total municipal.
- Mezcla de fuentes: renta fiscal (Eustat, 2024) + salario neto (OVJ, 2024). Ambos de 2024.
- Brecha sexo: OVJ publica series por sexo (hombres 1.566-1.498, mujeres 1.318-1.299 en 2022, último dato por sexo). Para 2024 solo hay total.

## Referencia en código

- `transform/calcular_renta_joven.py` → genera `data/procesado/dim_municipios_enriquecido.csv`
- Campos: `renta_joven_fiscal_proxy`, `renta_joven_salarial_18_34`, `renta_joven_salarial_16_29`, `esfuerzo_min_pct`, `esfuerzo_max_pct`
- Fuente raw: `data/raw/ovj_salario_joven_2024.json` (añadido sin modificar existentes)

## Alternativas descartadas

- Eustat PXWeb (PX_173402): solo da distribución por decil de renta familiar, no renta media por edad por TH. No útil.
- Valores de 2021 (1273€, 1558€ del Observatorio Vasco de la Vivienda): no comparables con datos 2024.
- Simular salario municipal: prohibido (datos reales).
PY