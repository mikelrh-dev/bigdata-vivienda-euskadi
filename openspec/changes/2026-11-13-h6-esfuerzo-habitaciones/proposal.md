# Proposal: 2026-11-13-h6-esfuerzo-habitaciones

## Intent

B4 ya muestra el precio de una habitación, pero no lo traduce a esfuerzo. Añadir la tasa de esfuerzo individual con el mismo denominador del bloque 2026: salario joven ajustado 18-34 (1.718,65 €/mes). Así se puede decir si una habitación es asumible en solitario, sin confundirla con el esfuerzo de una vivienda entera.

## Scope

- Calcular `mediana_precio_habitacion / salario_joven_2026 * 100` en `run_analisis_mongo.py`.
- Mostrar el esfuerzo global en H6 y el global + Donostia/Bilbao en B4.
- Verificar los tres valores desde los CSV.
- Reexportar PDF.

## Out of Scope

- Cambiar el CSV de habitaciones o el gold de 53.
- Usar renta de hogar o imputar salarios locales.
- Cambiar la definición del esfuerzo 2026 existente.
- Commit/push.

## Success Criteria

- [ ] H6 anota esfuerzo mediano 37,2 %.
- [ ] B4 cita 37,2 % global, 69,8 % Donostia y 34,9 % Bilbao.
- [ ] H6 sigue siendo determinista y el asset del deck coincide con gold.
- [ ] 59/59 checks, tests y PDF de 30 páginas.
