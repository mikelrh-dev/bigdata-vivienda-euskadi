# R1 — Recopilación dirigida de anuncios (2026-10-28)

## Objetivo
Ampliar cobertura municipal de anuncios en Fotocasa y Pisos.com para los municipios sin alquiler oficial (93) y municipios con <5 anuncios.

## Ejecución
- Fotocasa: scraping dirigido por municipio (scrapear_provincia con ruta por municipio) para 93 municipios, max 3 páginas. HTML crudo guardado por municipio.
- Pisos.com: scraping dirigido por municipio (scrapear_municipio) para 93 municipios, max 3 páginas. Fusión por URL de detalle.

## Resultados (antes → después)

| Métrica | Antes | Después |
|---|---:|---:|
| Fotocasa anuncios | 470 | 471 |
| Fotocasa municipios | 57 | 61 |
| Fotocasa mun >=30 | 3 | 3 |
| Pisos anuncios | 218 | 230 |
| Pisos municipios | 29 | 37 |
| Pisos mun >=30 | 0 | 2 |
| Combinado municipios con anuncios | 71 | 83 |
| Combinado mun >=30 | 4 | 5 |

## Observaciones
- La mayoría de los municipios pequeños (sin alquiler oficial) no tienen anuncios en Fotocasa ni Pisos.com (0 resultados). Esto es una limitación real de los portales, no un fallo de scraping.
- Los municipios con listings nuevos son pequeños (Elburgo, Lanestosa, Elantxobe, Usansolo, Zeberio, etc.) con n<30.
- No se alcanzó el objetivo de n>=30 en nuevos municipios; solo se mejoró cobertura marginal (+12 Pisos, +1 Fotocasa).
- Los anuncios temporales siguen sin separar (pendiente R3).

## Gaps que persisten
- 169 municipios (252-83) siguen sin ningún anuncio.
- Solo 5 municipios con n>=30 combinado.
- Pisos: superficie válida 85.3% (pendiente R3).
- Alquiler oficial sigue en 159/252 (pendiente R2).

## Conclusión
R1 aporta datos reales adicionales pero no resuelve la cobertura municipal. La limitación es estructural: los portales no tienen listings en municipios pequeños. Recomendación: aceptar gap y marcar esos municipios como "sin dato de portal"; usar alquiler oficial (Eustat) como fuente principal para los 159 y análisis comarcal para el resto. No seguir invirtiendo en scraping de municipios sin listings.

## Próximos pasos
- R2: alquiler portal para 93 sin dato (opcional, baja expectativa).
- R3: separar temporal/larga y depurar superficie.
- Documentar gaps en informe final.