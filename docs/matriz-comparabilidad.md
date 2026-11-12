# Matriz de comparabilidad

Qué es comparable con qué y qué no. Capas: oficial 159 / IDW 93 / contexto
252. Fuente única: `config/comparabilidad.yaml`.

| Métrica | Unidad | Vintage | Denominador / base | Capa | Comparable con | Regla |
|---|---|---|---|---|---|---|
| `esfuerzo_joven_pct_18_34` | % | 2024 | `renta_hogar` INE Atlas 2024 | oficial 159 | esfuerzo 18-34 de otros municipios | canónico |
| `esfuerzo_joven_pct` | % | 2024 | `renta_joven_estimada_16_29` | oficial 159 | solo legacy 16-29 | no mezclar con 18-34 |
| `cuantia_alquiler_mes` | €/mes | 2024 | stock Eustat Bizilagun | oficial 159 | alquiler oficial 2024 | no comparable con asking 2026 |
| `precio_medio_eur` | €/mes | 2026 | asking Fotocasa/Pisos/RealtyAPI | anuncios 64 | precio de anuncio 2026 | no comparable con oficial 2024 |
| `mediana_eur_m2` (modalidades) | €/m² | 2026 | asking, superficie 10-500 | anuncios | temporal vs larga (mismo portal) | usar €/m², no €/mes |
| `esfuerzo_anuncios_pct` | % | 2026/2024 | asking 2026 / renta 2024 | mixto | no comparable | llevar sufijo `_no_comparable` |
| `tension_demanda_social` | 0-100 | 2024 | percentil Etxebide + percentil esfuerzo 18-34 | oficial | tensión 2024 | alinear al canónico 18-34 |
| `tasa_paro_lanbide_pct` | % | 2024 | paro general 16-64 Udalmap | oficial 252 | paro general 2024 | no es paro juvenil 2026 |
| `renta_joven_estimada_18_34` | € | 2024 | `renta_hogar` INE Atlas × ratio CAE | oficial 252 | renta joven 2024 | proxy, no salario |

## Casos detectados

1. Mapa/histograma con 159 oficial + 93 IDW: separar capas.
2. Tabla D8 con esfuerzo 2024 y precio 2026: etiquetar por columna.
3. Gráfico P con oficial 2024 y anuncios 2026: declarar no comparable.
4. H8 con €/mes temporal vs larga: derivar a H8b (€/m²) y mostrar n.
5. F y `pipeline_alquiler_por_municipio` promediando oficial + IDW: exponer capa.
6. `dim_municipios_enriquecido.csv` con 5+ variantes de esfuerzo: declarar denominador.
7. H10 con tensión 16-29 y eje 18-34: alinear.
8. H6 con €/habitación y €/vivienda: separar unidades.
9. Declaración del denominador (Eustat RPF vs INE Atlas): corregir a INE Atlas.
10. Declaración del paro (Lanbide 2026 vs Udalmap 2024): corregir a Udalmap 2024 general 16-64.
11. `bootstrap_robustos.csv` mezclando 2026/2024: etiquetar no comparable.
12. Conteos de cobertura sobreestimados: corregir a 64/252 con anuncio y 60/252 con precio.
