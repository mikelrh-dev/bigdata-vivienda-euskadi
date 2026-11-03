# Spec delta: Fase 1 — Obtención y procesado de datos

## Requisitos

### REQ-1: Universo de análisis trifinario
- El sistema SHALL definir tres niveles de universo: CAE (Euskadi), comarca, municipio robusto (n≥30 anuncios).
- El sistema SHALL documentar explícitamente qué municipios tienen "sin dato" y cómo se tratan (comarcal vs exclusión).

### REQ-2: Población joven
- El sistema SHALL verificar si el INE Padrón Continuo proporciona población por edad quinquenal a nivel municipal.
- IF el INE Padrón Continuo existe, THEN el sistema SHALL incorporarlo como fuente de población joven 15-29.
- IF no existe, THEN el sistema SHALL usar fallback Eustat (0-19 / 20-64 / ≥65) y SHALL eliminar el Pipeline 3 del alcance.

### REQ-3: Inmutabilidad de data/raw
- El sistema SHALL NOT modificar archivos en `data/raw/` in place.
- El sistema SHALL escribir todos los datos normalizados en `data/procesado/`.
- El sistema SHALL congelar `data/raw/` (manifest SHA-256 verificable).

### REQ-4: Property fingerprint
- El sistema SHALL generar `property_fingerprint` (sha256) en `anuncios_unificados.json` para cada anuncio.
- El fingerprint SHALL basarse en `codigo_ine | superficie (±5 m²) | habitaciones | precio (±50 EUR)`.

### REQ-5: Flag geo_invalida
- El sistema SHALL marcar `geo_invalida=True` en todos los anuncios de Pisos.com (235/235).
- El sistema SHALL excluir anuncios con `geo_invalida=True` de agregaciones espaciales.
- El sistema SHALL usar anuncios de Pisos para precio por municipio de búsqueda (no geo).

### REQ-6: Fórmula canónica de esfuerzo
- El sistema SHALL documentar en `docs/metodologia.md` la fórmula única: `esfuerzo_joven_pct = alquiler_anual / renta_joven_estimada × 100`.
- El sistema SHALL NOT calcular KPIs finales en Pandas (eso es Mongo).

### REQ-7: Documentación canónica
- El sistema SHALL crear `docs/metodologia.md` como fuente única de verdad (universo, KPIs, fuentes, vintage, sesgos).
- El sistema SHALL crear `config/parametros_estudio.yaml` con fórmulas, umbrales, n_min=30, pesos, vintage.
- El sistema SHALL crear contratos en OpenSpec: layout HDFS, mensaje Kafka, JSON Schema de 6 colecciones.

### REQ-8: Reproducibilidad
- El sistema SHALL completar `requirements.txt` con todas las dependencias.
- El sistema SHALL verificar que el proyecto arranca en clon limpio.

### REQ-9: Reconciliación de contradicciones
- El sistema SHALL tener un solo número por métrica en todos los documentos.
- El sistema SHALL archivar auditorías antiguas en `openspec/archive/`.

## Escenarios

### Escenario 1: Verificación de inmutabilidad
- Given que `data/raw/` está congelado
- When se ejecuta cualquier script de transformación
- Then el script escribe solo en `data/procesado/`
- And `data/raw/` no se modifica.

### Escenario 2: Generación de fingerprint
- Given que `anuncios_unificados.json` tiene 840 anuncios
- When se ejecuta el script de fingerprint
- Then cada anuncio tiene `property_fingerprint` (sha256)
- And el fingerprint es determinista (mismo input → mismo hash).

### Escenario 3: Flag geo_invalida
- Given que Pisos tiene 235 anuncios con geo inválida
- When se unifican los anuncios
- Then todos los anuncios de Pisos tienen `geo_invalida=True`
- And se excluyen de agregaciones espaciales.

### Escenario 4: Fórmula canónica
- Given que existe `docs/metodologia.md`
- When se busca la fórmula de esfuerzo
- Then aparece una sola fórmula: `esfuerzo_joven_pct = alquiler_anual / renta_joven_estimada × 100`
- And no hay variantes en otros documentos.

### Escenario 5: Reproducibilidad
- Given un clon limpio del repositorio
- When se instalan dependencias con `pip install -r requirements.txt`
- Then todos los scripts de transformación ejecutan sin error.
