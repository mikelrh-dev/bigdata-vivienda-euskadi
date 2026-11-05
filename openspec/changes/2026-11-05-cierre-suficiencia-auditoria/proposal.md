# Proposal: cierre-suficiencia-auditoria

## Intent

La auditoría de 2026-11-05 deja el proyecto defendible pero con deuda medida: el manifest silver no verifica (hash de `dim_municipios_tension.csv`), hay dos definiciones de esfuerzo vivas (media en silver, mediana en el pipeline canónico), ocho afirmaciones de docs contradicen los datos y la VPO se declara "sin dato" cuando existe un indicador municipal oficial sin integrar. Este change cierra esa deuda sin tocar `data/raw` salvo append autorizado y sin Kafka/HDFS.

## Scope

### In Scope
- D1: regenerar `dim_municipios_enriquecido.csv` y ambos manifests; dejar `--verify` y `run_all --check` en exit 0.
- D3: corregir las cifras falsas de docs (VPO 100 % sin dato, 15 colecciones, 130 tests, 169 sin anuncios, 86 duplicados, lagunas silver, índice de resultados, C1 parcial).
- D2: una sola definición de esfuerzo (cuantía **mediana**, ya canónica en `matriz_indicadores.md`), recarga de Mongo, regeneración de los 5 CSV y de la huella.
- D4/D5: diccionario de columnas canónicas y corrección del nombre de la comparativa (4 robustos, no 3).
- Fase 3: integrar el indicador municipal oficial "VPO terminadas en el último quinquenio (‰ habitantes)" (Open Data Euskadi, indicador 73) como colección `vpo_municipal`.
- Fase 5: sensibilidad del IDW y bootstrap de la mediana de los 4 robustos.
- Fase 6: informe final trazable a CSV/Mongo.
- Fase 8: archivar en `openspec/changes/archive/` los changes ya implementados.

### Out of Scope
- Kafka y HDFS (aparcados por decisión del 2026-11-05).
- Re-scraping de los 169 municipios sin anuncios.
- Salario municipal por edad (no existe fuente).
- `git push` y cualquier escritura en producción ajena a la recarga local de Mongo.

## Capabilities

### New Capabilities
- `vpo-municipal`: indicador municipal de VPO terminada (flujo quinquenal), separado del stock no disponible.

### Modified Capabilities
- `presentacion-de-resultados`: INDICADORES-01 (una definición de esfuerzo), CONCLUSION-01 (cifras corregidas), PREPARACION-VISUALIZACION-01 (CSV regenerados con huella).
- `mongodb-y-analisis`: AGREGACION-01 (pipeline VPO alineado), nueva colección `vpo_municipal`.

## Approach

1. Congelar el estado en rama y regenerar gold/manifests (D1).
2. Corregir docs con las cifras medidas (D3).
3. Cambiar `generar_analisis_variables_base.py` a `cuantia_media_eur_mes_mediana`, recorrer la cadena silver, recargar Mongo y regenerar CSV (D2).
4. Descargar el indicador 73 a `data/staging/`, parsearlo, validarlo y solo entonces promoverlo a raw con guard y manifest (Fase 3).
5. Análisis de sensibilidad y bootstrap como scripts de `analysis/` (Fase 5).
6. Informe final sin cifras tecleadas (Fase 6).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `transform/generar_analisis_variables_base.py` | Modified | Esfuerzo con cuantía mediana |
| `extract/26_vpo_terminadas.py` | New | Descarga + promoción a raw con guard |
| `transform/limpiar_vpo_municipal.py` | New | Parser del indicador 73 |
| `storage/load_mongo.py` | Modified | Colección `vpo_municipal` |
| `analysis/sensibilidad.py` | New | IDW + bootstrap |
| `docs/*.md`, `data/resultados/*` | Modified | Cifras, índice, huella, informe |
| `tests/test_vpo_municipal.py` | New | Cobertura y rangos del indicador |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cambiar media→mediana mueve la tensión social | Med | Recalcular y actualizar las cifras en docs y guion |
| Añadir un fichero a raw rompe tests que fijan 353 | High | Staging primero; manifest y contadores en el mismo commit |
| El parser del CSV oficial falla | Med | Staging aislado; 2-3 iteraciones sin tocar raw |
| Recarga de Mongo altera prod local | Med | `replace_collection` ya usado por el proyecto; verificar conteos 252/759/5040 |

## Rollback Plan

Cada fase va en su commit sobre `cierre/suficiencia-auditoria`. Revertir un commit restaura gold, docs o CSV sin afectar a las demás fases. El raw solo cambia en la Fase 3 y su rollback es borrar el fichero nuevo y regenerar manifests.

## Dependencies

- Mongo local en `localhost:27017` (15 colecciones medidas).
- Red para el CSV del indicador 73 (validado HTTP 200 el 2026-11-05).

## Success Criteria

- [ ] `generar_manifest.py --verify` exit 0 (raw y silver).
- [ ] `run_all.py --check` exit 0.
- [ ] `pytest tests -q` verde (130 + nuevos).
- [ ] Un único valor de esfuerzo 18-34 por municipio en todos los artefactos.
- [ ] `vpo_municipal` con 252 municipios y rango 0-50 ‰.
- [ ] Informe final con cada cifra trazable a `data/resultados/`.
