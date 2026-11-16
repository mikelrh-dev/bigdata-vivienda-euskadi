# `analysis/` — preguntas sobre el gold y sobre Mongo

`run_analisis_mongo.py` es el orquestador: `PIPELINE_ORDER` fija los 11 pipelines y su orden. `scripts/verificar_gobernanza.py` comprueba que sigan siendo 11.

## Aquí `validar_*` no significa «verificador del gate»

Los verificadores del contrato son `scripts/verificar_*`. Los `validar_*` de esta carpeta son **pasos de análisis que contrastan una fuente**:

| Fichero | Qué hace |
|---|---|
| `validar_alquiler_serpavi.py` | Contrasta el alquiler oficial 2024 (Eustat) con una fuente fiscal independiente (SERPAVI). Es un paso de `scripts/regenerar_capa_2026.py` y su CSV lo espera `tests/test_reproducibilidad_silver.py` |
| `validar_portales_2026.py` | Sensibilidad de la capa 2026 al portal de origen de los anuncios. También es paso de `regenerar_capa_2026.py` |

Renombrarlos o moverlos rompe `regenerar_capa_2026` y un test. Se quedan donde están.

## La cadena 2026 no está en el DAG de silver

`calibrar_premium_oferta.py` es el **paso 4** de `scripts/regenerar_capa_2026.py` (no está en `transform/run_all.py` porque necesita silver ya construido). Escribe `data/resultados/premium_oferta_2026.csv`, que figura en `SALIDAS` y se hashea al final de la cadena.

→ Si cambias su salida, actualiza también `SALIDAS`; es lo que detecta una regeneración incompleta.

## Inventario

El resto de ficheros y su cometido se listan solos:

```bash
python scripts/inventario_codigo.py
```
