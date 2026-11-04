# Design: renta-joven-18-34

## Decisiones

- Ponderacion por anchura (2/5/5/5 sobre 17 años), no media simple. Corrige sesgo de bandas desiguales.
- Patron aditivo: campos nuevos coexisten con legacy, dashboards y Mongo leen ambos durante transicion.
- Paro y poblacion: sin renombrar. Poblacion 18-34 estimada con misma formula transparente ya usada y etiquetada _est.
- Lanbide 30-34 y poblacion fina quedan como nueva extraccion futura, no bloquean esta migracion.

## Alternativas descartadas

- Renombrado destructivo 16_29->18_34: rechazado porque rompe contrato, tests y comparabilidad.
- Media simple de bandas: rechazada por sesgo de anchura.
