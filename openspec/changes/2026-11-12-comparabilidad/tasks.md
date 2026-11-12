# Tasks — Contrato de comparabilidad

## 1. Contrato (P0)

- [ ] 1.1 Crear `config/comparabilidad.yaml` (capas, unidades, vintages, denominadores, aliases legacy).
- [ ] 1.2 Crear `docs/matriz-comparabilidad.md` (métrica × unidad/vintage/denominador/capa/comparabilidad).
- [ ] 1.3 Crear `analysis/comparabilidad.py` (helpers puros: `filtrar_capa`, `es_capa`, `etiqueta_vintage`, `canonico_esfuerzo`, `assert_misma_unidad`).
- [ ] 1.4 Crear `tests/test_comparabilidad.py` (config, matriz doc vs config, helpers).
- [ ] 1.5 Corregir `config/parametros_estudio.yaml`: `renta` = INE Atlas renta_hogar 2024; `paro` = Udalmap 2024 general 16-64.

## 2. Figuras (P0)

- [ ] 2.1 `transform/generar_figuras_N.py` N1/N2: capas separadas (oficial 159 / IDW 93 / gris sin dato) y caption.
- [ ] 2.2 `analysis/run_analisis_mongo.py` A1/A2: filtrar `metodo_imputacion=oficial`.
- [ ] 2.3 `analysis/run_analisis_mongo.py` F: media oficial por TH separada del IDW.
- [ ] 2.4 `analysis/run_analisis_mongo.py` P: etiquetas con año/unidad + nota no comparable.
- [ ] 2.5 `analysis/run_analisis_mongo.py` H6: eje €/habitación + aviso.
- [ ] 2.6 `analysis/run_analisis_mongo.py` H8: n por modalidad + aviso (H8b intacto).
- [ ] 2.7 `analysis/run_analisis_mongo.py` H10: alinear rango con la tensión.
- [ ] 2.8 `analysis/run_analisis_mongo.py` I: corregir comentario (media vs mediana).
- [ ] 2.9 `analysis/mongo_aggregations.py` `pipeline_alquiler_por_municipio`: proyectar `metodo_imputacion`.

## 3. Datos y deck (P1)

- [ ] 3.1 `transform/calcular_tension_social.py`: usar `esfuerzo_joven_pct_18_34` con fallback declarado; documentar delta.
- [ ] 3.2 `analysis/sensibilidad.py`: `esfuerzo_anuncios_pct_no_comparable` + columnas `aviso` y `mezcla_vintage`.
- [ ] 3.3 `README.md`: 64/252 con anuncio, 60/252 con precio observable; eliminar 83/252 y 62/252 con anuncio.
- [ ] 3.4 `docs/presentacion_v2/guion.md`: D6 (capas), D8 (años por columna), D9 (rango de la tensión).
- [ ] 3.5 `docs/presentacion_v2/index.html`: caption del mapa y tabla D8 con años.
- [ ] 3.6 `data/resultados/README.md`: conteos y aviso del bootstrap.

## 4. Verificación (P0)

- [ ] 4.1 `pytest tests -q` verde (237+ passed, 2 skipped).
- [ ] 4.2 `python scripts/run_pipeline.py --fase silver` regenera tensión/enriquecido.
- [ ] 4.3 `python scripts/run_pipeline.py --fase mongo --allow-mongo-write` recarga la tensión embebida.
- [ ] 4.4 `python scripts/run_pipeline.py --fase gold` regenera figuras y CSV.
- [ ] 4.5 `python scripts/run_pipeline.py --check` 0 errores.
- [ ] 4.6 Escribir `verify-report.md`.
