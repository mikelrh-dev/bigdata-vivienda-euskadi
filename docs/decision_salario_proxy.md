# Decisión: Uso de renta municipal como proxy de salario

**Fecha:** 2026-10-27  
**Contexto:** El proyecto necesita un indicador de capacidad económica municipal para calcular la tasa de esfuerzo (alquiler / ingresos).

## Problema

No existe salario municipal por edad disponible gratuitamente:
- INE salarios por edad (`ine_salarios_edad.csv`) es **nacional** (1.372,8 € para 16-24 años).
- Eustat no publica salario municipal por edad.
- Observatorio Vasco de la Juventud no ofrece dato municipal.

## Decisión

Usar la **renta media municipal (Eustat, 2024)** como proxy de capacidad económica.

### Justificación
1. La renta municipal captura el nivel de ingresos del hogar, que es el determinante principal de la capacidad de pago del alquiler.
2. Es el único indicador económico disponible a nivel municipal para los 252 municipios.
3. La correlación Pearson renta vs alquiler es r = 0.2094 (débil), lo que indica que el precio de alquiler no se explica únicamente por la renta local. Esto se documentará en el informe final.

### Limitaciones
- La renta es un proxy, no un salario. No refleja la distribución por edad ni la precariedad juvenil.
- Mezclar renta (2024) con alquiler (2024) es coherente temporalmente.
- Para una defensa rigurosa, se debe advertir que la tasa de esfuerzo calculada es orientativa, no exacta.

### Alternativas descartadas
- Salario nacional (INE): no es municipal, inútil para ranking.
- Simular salario municipal: prohibido (los datos deben ser reales).
- Observatorio Vasco de la Juventud: sin dato municipal.

### Referencia en código
- `renta_municipal_completa.csv` → campo `renta_eustat` (Euros/año, 2024).
- `transform/completar_alquiler_comarca.py` → usa renta como proxy en análisis.
PY