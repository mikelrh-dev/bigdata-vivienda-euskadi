<!-- cap: 9 | titulo: Anexos | criterios: Trazabilidad | estado: borrador -->
# 9. Anexos

## A. Mapa de la rúbrica

| ID | Criterio | Sección |
|---|---|---|
| C1 | Extracción mediante Python (API y scraping) | 2.1, 3.1 |
| C2 | Almacenamiento HDFS y recuperación | 2.3, 3.3 |
| C3 | Kafka: tópico, productor y consumidor | 2.3, 3.2 |
| C4 | Integración completa hasta MongoDB | 2.4, 3.4 |
| C5 | Integración de 2+ fuentes por campo común | 3.2, 4.2 |
| C6 | 2+ colecciones y relación embedding/referencing | 4.1, 4.2 |
| C7 | Limpieza: nulos, duplicados y tipos | 3.3, 7.2 |
| C8 | Automatización de carga, limpieza y transformación | 3.6, 8.3 |
| C9 | Modelado con decisión embedding/referencing explicada | 4.1 |
| C10 | CRUD con PyMongo y comprobación | 4.5 |
| C11 | 5 consultas útiles, anidados y 2+ condiciones | 5.3 |
| C12 | 3 pipelines, 5 etapas, `$group` y `$lookup`/`$unwind` | 5.2 |
| C13 | Índice y `explain()` con COLLSCAN/IXSCAN | 5.4 |
| C14 | Operación atómica y justificación de no transacción | 4.5 |
| C15 | Datos heterogéneos adaptados con PyMongo | 3.3, 4.3 |
| C16 | Script que ejecuta todos los análisis | 5.2, 8.3 |
| C17 | 5 indicadores con 2+ fuentes | 5.1, 6.1–6.4 |
| C18 | 3+ municipios comparados y conclusión ligada a indicador | 6.6 |
| C19 | 3+ conjuntos preparados para visualización | 6.1–6.5 |

## B. Glosario

| Término | Definición |
|---|---|
| `codigo_ine` | Código oficial de cinco dígitos que identifica un municipio |
| Raw | Copia inmutable del original, con SHA-256 y `.FROZEN` |
| Silver | CSV normalizado y cruzado por `codigo_ine` |
| Gold | CSV y PNG listos para el informe |
| Tier | Nivel de confianza A/B/C/D según cobertura y muestra |
| IDW | Interpolación por distancia inversa para municipios sin alquiler oficial |
| Esfuerzo | Porcentaje de la renta que consume el alquiler |

## C. Comandos

```bash
pytest -q tests
python scripts/verificar_gobernanza.py
python scripts/run_pipeline.py --check
python scripts/verificar_cifras_deck.py
python docs/memoria/build.py --check
python scripts/hdfs_recuperacion_un_fichero.py
```

## D. Índice de figuras

| Figura | Archivo | Sección |
|---|---|---|
| 6.1 | `figuras/fig-mapa-2024.png` | 6.1 |
| 6.2 | `figuras/fig-ranking-2024.png` | 6.2 |
| 6.3 | `figuras/fig-tier.png` | 6.2 |
| 6.4 | `figuras/fig-oficial-vs-anuncios.png` | 6.3 |
| 6.5 | `figuras/fig-modalidades.png` | 6.3 |
| 6.6 | `figuras/fig-vpo.png` | 6.4 |
| 6.7 | `figuras/fig-mapa-2026.png` | 6.5 |
| 6.8 | `figuras/fig-hist-2026.png` | 6.5 |
