# Statistical Cross-Analysis Audit — Vivienda Euskadi

**Scope:** Price distributions, salary levels, employment rates, distance–price correlation, outliers/gaps, data sufficiency.  
**Source data:** `data/raw/` (alquiler_municipal.csv, anuncios_pisos.csv, anuncios_fotocasa.csv, udalmap_empleo.csv, distancias_capitales.csv, ine_salarios_edad.csv, eustat_renta_municipal.csv).  
**No project files were modified.**

## 1. Dataset coverage

| Dataset | Rows | Municipalities | Coverage vs 252 |
|---|---|---|---|
| Alquiler municipal (official rent, €/m²) | 253 district rows | 159 | 63% |
| Anuncios pisos.com (valid price/m²) | 193 | 29 | 11% |
| Anuncios fotocasa (valid price/m²) | 469 (289 temporal + 180 long-term) | 54 | 21% |
| Udalmap empleo | 252 | 252 | 100% |
| Distancias a capitales | 252 (municipalities) | 252 | 100% |
| INE salarios por edad | 198 series | nacional (no municipal) | n/a |
| Eustat renta personal 2024 | 201 municipalities | 201 | 80% |

## 2. Price distributions (€/m²)

### 2.1 Alquiler oficial (municipal, media de distritos)
- n municipalities = 159; mean = 8.03 €/m²; median = 7.80; std = 1.75; min = 4.70 (Campezo/Kanpezu); max = 14.74 (Donostia/San Sebastián).
- 122 of 159 municipalities have a single district; only 1 (Bilbao) has 9 districts.
- IQR outlier (high): Donostia/San Sebastián (14.74; upper bound 12.71). No low outliers.

Top prices: Donostia 14.74, Bilbao 11.83, Zarautz 11.75, Hondarribia 11.70, Getxo 11.67.  
Bottom: Campezo/Kanpezu 4.70, Karrantza 4.80, Ayala/Aiara 5.10, Lapuebla 5.10, Okondo 5.30.

### 2.2 Anuncios pisos.com (price/m²)
- n valid = 193 (20 missing price, 5 missing surface); mean = 15.95; median = 15.00; std = 6.75; min = 3.91; max = 43.92.
- IQR outliers (high): 9 listings (30.00–43.92 €/m²).
- Per-municipality counts: 29 municipalities; min 1, max 27 (Abanto y Ciérvana-Abanto Zierbena); 0 municipalities ≥30.

### 2.3 Anuncios fotocasa (price/m²)
- n valid = 469 (9 missing price, 4 missing surface); mean = 18.91; median = 17.50; std = 8.01; min = 1.60; max = 83.33.
- Temporal rentals are 289/469 (62%) and inflate the mean; long-term only (n=180): mean = 16.12, median = 15.45.
- IQR outliers (high): 13 listings (upper bound 36.11).
- Per-municipality counts: 54 municipalities; min 1, max 200 (Bilbao); only 3 municipalities ≥30 (Bilbao 200, Donostia 80, Getxo 40).

### 2.4 Combined anuncios per municipality (long-term + temporal, valid price/m²)
- 68 municipalities with any listing; total 662 valid listings.
- ≥30 listings: 3 (Bilbao, Donostia/San Sebastián, Getxo).
- ≥10 listings: 15; ≥5 listings: 26; 42 municipalities have ≤4 listings.

## 3. Salary levels by age group (INE, 2024, monthly €)

National only (no municipal breakdown).

| Age group | Salary (€/month) |
|---|---|
| 16–24 | 1,372.8 |
| 25–34 | 2,131.6 |
| 35–44 | 2,399.8 |
| 45–54 | 2,591.6 |
| 55+ | 2,680.7 |
| All ages | 2,385.6 |

Decile spread (full-time, total): decil 1 = 710–997 €, decil 10 = 4,701–5,836 € across age groups. Part-time series has gaps (NaN) in decil 10 for several age groups (2022 values only).

## 4. Employment rates by municipality (Udalmap, n=252)

| Indicator | Mean | Std | Min | Max |
|---|---|---|---|---|
| Tasa actividad (%) | 49.79 | 3.20 | 40.63 (Elantxobe) | 60.09 (Zalduondo) |
| Tasa ocupación (%) | 54.86 | 4.74 | 41.39 (Lanestosa) | 74.14 (Baliarrain) |
| Tasa paro aprox. (%) | −10.10 | 4.73 | −32.46 (Baliarrain) | 4.01 (Lanestosa) |

Note: `tasa_paro_aprox_pct` is negative for most municipalities (definition/derivation issue in source), so treat as relative indicator, not literal unemployment.  
IQR outliers (small municipalities): actividad 3 (Elantxobe, Arakaldo, Zalduondo); ocupación 6 (Lanestosa, Aduna, Irura, Astigarraga, Orendain, Baliarrain); paro 4 (Baliarrain, Orendain, Alkiza, Lanestosa). Coverage is complete (252/252).

## 5. Distance to capitals vs price

Correlation (Pearson) between municipal rent (€/m², official) and distance (km), n=159:

| Distance variable | r |
|---|---|
| Nearest capital | −0.608 |
| Bilbao | −0.070 |
| Donostia | −0.220 |
| Vitoria-Gasteiz | +0.554 |

Interpretation: rent falls with distance to the nearest capital (r=−0.61); the Vitoria correlation is positive because inland/Álava municipalities are cheaper and farther from the coastal capitals.  
Anuncios (median price/m² per municipality) vs nearest capital: fotocasa r≈0.00 (n=54), pisos r≈0.05 (n=29) — no robust distance signal at municipality level due to small samples and capital-city dominance.

## 6. Outliers & gaps summary

- **Price outliers:** alquiler Donostia/San Sebastián (14.74). Anuncios: 9 pisos listings (30.00–43.92), 13 fotocasa listings (up to 83.33, mostly temporal/small surface).  
- **Employment outliers:** 6 small municipalities on ocupación, 4 on paro (likely small-base volatility).  
- **Coverage gaps:** 93/252 municipalities (37%) lack official alquiler data; 184/252 have no anuncios; salary data is national only; renta municipal (Eustat 2024) covers 201/252 (renta vs price r=+0.17, n=139 — weak).  
- **Price vs renta:** weak positive correlation (r=+0.17), suggesting rent levels track income only modestly.

## 7. Data sufficiency verdict

- **Official alquiler (district aggregates):** adequate coverage (159 municipalities) but no disclosed sample size per district; district-level aggregation (1–9 per municipality) limits within-municipality dispersion analysis.  
- **Anuncios:** **insufficient for robust per-municipality conclusions.** Only 3 municipalities reach the ≥30-listing threshold (Bilbao 200, Donostia 80, Getxo 40); 42 municipalities have ≤4 listings. Per-municipality mean/median prices for small n are unstable (single-listing municipalities).  
- **Salary:** national-level only; cannot support municipality-level affordability analysis.  
- **Employment & distance:** full coverage (252/252), suitable for municipal-level analysis.  
- **Recommendation:** aggregate anuncios to comarca/territory level or collect more listings before per-municipality inference; treat anuncios per-municipality stats as indicative only; use official alquiler for municipal comparison and anuncios for distributional/outlier exploration. Save derived tables in `scratchpad/` if further modeling is needed.
PYEOF