# Design: fuentes-validacion

## Decisiones

- Validación efímera con scripts/validar_fuentes_nuevas.py sobre raw existentes, sin tocar raw ni Mongo. Solo lectura.
- Criterio alta: municipios alcanzados con codigo_ine 5 dígitos mayor o igual a 200 de 252 y fuente pública automatizable. Resto baja.
- Alokabide sin raw se clasifica baja hasta descarga futura, sin inventar cobertura.
- Scraping Nivel2 queda fuera de este cambio por riesgo medio; se deja como trabajo futuro con lista objetivo.

## Alternativas descartadas

- Crear 3 extractores a ciegas: rechazado porque repetiría el error de fuentes sin granularidad.
- Kafka/HDFS en este cambio: rechazado porque no cierra gaps de datos.
