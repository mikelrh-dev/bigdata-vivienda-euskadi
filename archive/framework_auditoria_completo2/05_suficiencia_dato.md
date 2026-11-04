# 05 · Suficiencia del dato — ¿podemos responder "dónde vivir"? Gate GO/NO-GO

> No audita filas, audita CAPACIDAD DE RESPUESTA con error <20%. Absorbe el antiguo `03_framework_dato_puro` + `stats/entity_audit`.

## Verdad base

`data/procesado/dim_municipios.csv` = 252 municipios (Álava 51 + Bizkaia 112 + Gipuzkoa 88). Todo % es sobre 252.

## Fases (en orden, con comandos)

**F0 Inventario real:** por cada fuente contar registros VÁLIDOS (precio>0, superficie 10-600, `codigo_ine` 5 dígitos), municipios únicos, % sobre 252. `df['codigo_ine'].nunique()`, `groupby('codigo_ine').size().describe()`.

**F1 Entity resolution:** % `codigo_ine` que cruza con dim (objetivo 100% en silver); variantes mapeadas; Eustat sin las 24 filas agregado.

**F2 Cobertura muestral (la que decide):** por fuente de anuncios `counts = groupby('codigo_ine').size()`:
- n≥30 fiable (media estable) · n 5-29 indicativo (mediana + advertencia) · n<5 solo comarca/territorio.
- Separar temporal vs larga estancia (Fotocasa): si difieren >15% en €/m², nunca mezclar.
- Alquiler oficial: exigir nº municipios + nº distritos + `n` muestral si existe; sin `n`, P1 (media de 2 o 200 contratos vale igual).

**F3 Calidad y sesgos:** IQR por fuente (€/m²), superficie válida 15-300 + habitaciones no nulas, Pearson renta vs alquiler (si r<0.3 documentar que el precio no lo explica la renta), parseo `;`+`"` en emancipación/ECVI.

**F4 Validez de dominio:** paro/actividad/ocupación 0-100 (negativos = P1 fórmula); distancias completas 252/252 (dedup); salario nacional ≠ municipal (usar renta como proxy y decirlo); años mezclados → columna `año_fuente`.

## Veredicto (SÍ/NO + nivel)

| Pregunta | Criterio GO | Si no llega |
|----------|-------------|-------------|
| Ranking 252 por coste con error <20% | n≥30 o dato oficial con `n` conocido en suficientes municipios | Solo ranking comarcal + capitales (documentarlo, no inflarlo) |
| Tasa esfuerzo = alquiler/renta para 252 | renta 252/252 (Eustat + proxy INE declarado) y alquiler oficial o estimado con método por fila | NO-GO hasta completar proxy |
| "Dónde hay trabajo + vivienda barata" | paro válido 0-100 + distancias 252/252 | NO-GO hasta corregir |

**Plantilla de veredicto:** "Datos suficientes para ___ (n≥30 en __ municipios, oficial __/252). Insuficientes para ___. Recomendación: ___." + 🟢 GO / 🟡 GO con deuda / 🔴 NO-GO.
