# Spec: MERCADO-01 — Esfuerzo de mercado 2026

## ID
MERCADO-01

## Título
Esfuerzo de mercado 2026 (precio anuncio 2026 + salario joven 2024 ajustado IPC INE)

## Descripción
Nueva colección Mongo `esfuerzo_mercado_2026` que expone el esfuerzo de alquiler basado en precios de anuncio 2026, para municipios con cobertura de anuncio, sin modificar el esfuerzo canónico 2024.

## Requisitos funcionales
- **RF-01**: La colección `esfuerzo_mercado_2026` debe tener un documento por municipio con código INE (252 municipios máximo, solo los con anuncio tienen datos de precio).
- **RF-02**: Cada documento debe contener precio de anuncio 2026 (mediana, medio, n_anuncios), salario joven 2024 base, factor IPC INE 2024→2026, salario ajustado 2026, esfuerzo mercado % (18-34 y 16-29).
- **RF-03**: El esfuerzo mercado 2026 NO debe sobrescribir ni modificar el campo `esfuerzo_joven_pct_18_34` de la colección `municipios`.
- **RF-04**: El archivo `data/raw/ipc_ine_2024_2026.csv` debe estar en el manifiesto SHA de raw (`docs/raw_manifest_sha256.txt`).
- **RF-05**: El archivo `data/procesado/esfuerzo_mercado_2026.csv` debe estar en el manifiesto SHA de procesado (`data/procesado/manifest_sha256.txt`).
- **RF-06**: El gate e2e debe verificar `EXPECTED_SILVER = 183` y `EXPECTED_COLLECTIONS` incluye `esfuerzo_mercado_2026` (15 colecciones).
- **RF-07**: Debe existir un pipeline Mongo `pipeline_esfuerzo_mercado_2026()` que exponga la colección con lookup a `municipios`.

## Requisitos no funcionales
- **RNF-01**: Trazabilidad completa: cada documento debe tener metadatos con fuentes, fecha de cálculo, vintage num/den, flag_no_comparable.
- **RNF-02**: Inmutabilidad: el esfuerzo canónico 2024 permanece byte-idéntico.
- **RNF-03**: Reversibilidad: la colección puede eliminarse sin afectar a `municipios`.

## Escenarios
| Escenario | Descripción |
|-----------|-------------|
| Municipio con anuncio (Bilbao) | Esfuerzo mercado 2026 calculable y visible con `n_anuncios > 0` |
| Municipio sin anuncio | Documento existe pero sin precio (`n_anuncios = 0`), esfuerzo nulo o ausente |
| Comparación 2024 vs 2026 | Ambos valores accesibles por código INE sin mezcla de capas |

## Criterios de aceptación
- [ ] `data/raw/ipc_ine_2024_2026.csv` existe y está en `docs/raw_manifest_sha256.txt`
- [ ] `data/procesado/esfuerzo_mercado_2026.csv` existe y está en `data/procesado/manifest_sha256.txt`
- [ ] Colección Mongo `esfuerzo_mercado_2026` cargada con 252 documentos (o los que tengan anuncio)
- [ ] Pipeline `pipeline_esfuerzo_mercado_2026()` ejecuta sin errores
- [ ] Gate e2e pasa con `EXPECTED_SILVER=183` y `EXPECTED_COLLECTIONS=15`
- [ ] Check 19 en `verificar_fase_datos.py` pasa
- [ ] Esfuerzo canónico 2024 sin cambios (verificar hash de `mongo_esfuerzo_por_municipio.csv`)

## Referencia
- Diseño: `openspec/changes/esfuerzo-mercado-2026/design.md`
- Propuesta: `openspec/changes/esfuerzo-mercado-2026/proposal.md`
- Exploración: `openspec/changes/esfuerzo-mercado-2026/exploration.md`