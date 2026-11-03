# Tasks: Fase 1 — Obtención y procesado de datos

## 1. Reconciliar contradicciones
- [x] 1.1 Crear `docs/metodologia.md` con un solo número por métrica (Fotocasa=471, robustos=4, Pearson=0.2094, tests=57).
- [ ] 1.2 Archivar auditorías antiguas en `openspec/archive/`.
- [ ] 1.3 Actualizar README.md con números canónicos.

## 2. Verificar D2 (población joven)
- [ ] 2.1 Consultar INE wstempus por municipio y edad quinquenal.
- [ ] 2.2 Si existe → incorporar como fuente; si no → fallback Eustat y eliminar Pipeline 3.

## 3. Revertir in-place (D5)
- [ ] 3.1 Verificar si `data/raw/` se puede regenerar desde scripts de extracción.
- [ ] 3.2 Si sí → regenerar `data/raw/` y mover normalización a `data/procesado/`.
- [ ] 3.3 Si no → documentar que raw está modificado y marcar como limitación.

## 4. Generar property_fingerprint (D4)
- [x] 4.1 Crear script `transform/generar_fingerprint.py` que añada `property_fingerprint` a `anuncios_unificados.json`.
- [x] 4.2 Verificar determinismo (mismo input → mismo hash).

## 5. Flag geo_invalida (D3)
- [x] 5.1 Actualizar `transform/unificar_anuncios.py` para añadir `geo_invalida=True` a Pisos.
- [x] 5.2 Re-ejecutar unificación y verificar.

## 6. Reproducibilidad
- [x] 6.1 Completar `requirements.txt` con todas las dependencias.
- [ ] 6.2 Verificar clon limpio (instalar deps, ejecutar scripts).

## 7. Documentar contratos
- [ ] 7.1 Crear `openspec/specs/almacenamiento-y-streaming/spec.md` con layout HDFS + Kafka.
- [ ] 7.2 Crear `openspec/specs/mongodb-y-analisis/spec.md` con modelo 6 colecciones.
- [ ] 7.3 Crear `openspec/specs/presentacion-de-resultados/spec.md` con 40 preguntas → 3 gráficos.
- [x] 7.4 Crear `config/parametros_estudio.yaml` con fórmulas, umbrales, n_min=30.

## 8. Verificación
- [x] 8.1 Ejecutar `pytest` → todos passed.
- [ ] 8.2 Verificar cero contradicciones entre docs.
- [ ] 8.3 Verificar `data/raw/` inmutable.
