# Proposal: bloque-4-conclusiones-entrega

## Intent

Cerrar RA4 (PLAN_10 16-18): indicadores, respuesta y guion verificables. Tensión social y paro Lanbide siguen en silver, falta matriz O1-O4 cerrada y el guion no refleja la cadena offline actual.

## Scope

### In Scope
- 16. Indicadores 5 con pipeline Mongo verdadero para tensión social y paro Lanbide; si no es viable, declararlos silver con justificación. Sin perder `metodo_imputacion` ni `fillna` mediana sin flag `is_imputed`.
- 17. Respuesta con 4 robustos (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39) y matriz O1-O4: mediana 26,61 oficial 18-34, 25,2% sobre 30. Advertir Getxo 40 vs Vitoria 39 (1 anuncio).
- 18. Guion Tema 8 (1 página): embedding, índices, atomicidad, cadena offline HDFS centro + Kafka pid 1832, 16-29 legacy (canónico 18-34).

### Out of Scope
- Sin tocar `data/raw` ni raw HDFS; sin carpeta nueva; sin subir procesado.
- Prod intacta por defecto (solo lectura o test con `MONGO_ALLOW_DESTRUCTIVE=1`).
- Sin código en esta fase; sin git add/commit/push.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- presentacion-de-resultados: INDICADORES-01, PREPARACION-VISUALIZACION-01, CONCLUSION-01.
- mongodb-y-analisis: AGREGACION-01 (pipeline tensión/paro o silver justificado).

## Approach

Pipeline mínimo en `analysis/` o justificación silver; CSV canónicos con huella; matriz O1-O4 en `docs/conclusiones_municipios.md`; guion en `docs/guion_defensa.md`; comandos VM/Mongo en `docs/trazabilidad_vm.md` (Fecha/Objetivo/Máquina/Comando/Salida/Conclusión).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `analysis/mongo_aggregations.py` | Modified | Pipeline tensión/paro o salida silver |
| `docs/matriz_indicadores.md`, `conclusiones_municipios.md` | Modified | O1-O4, 4 robustos, huella 253/253/3 |
| `docs/guion_defensa.md` | Modified | Guion Tema 8, 10 criterios, lagunas |
| `docs/trazabilidad_vm.md` | Modified | Entrada por comando |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Sin fuente Lanbide en Mongo para pipeline | Med | Silver justificado; no inventar valores |
| `fillna` sin `is_imputed` oculta imputación | Med | Exigir `metodo_imputacion` + flag |
| Getxo 40 vs Vitoria 39 leído como ranking firme | High | Citar n y advertencia en matriz/guion |
| Tocar raw/HDFS o prod | High | Solo lectura; prod intacta por defecto |

## Rollback Plan

Revertir docs y CSV regenerados (sin commit); prod y raw/HDFS intactos.

## Dependencies

- Bloque 3 archivado (759 anuncios, pytest 130). HDFS centro solo lectura, Kafka pid 1832, PLAN_10 16-18.

## Success Criteria

- [ ] CSV 253 y 253 y 3 auto con huella.
- [ ] Comparativa 4 con paro Lanbide no nulo (o silver justificado).
- [ ] O1-O4: mediana 26,61, 25,2% sobre 30, advertencia Getxo/Vitoria.
- [ ] Guion 1 página, 10 criterios, lagunas, 16-29 legacy.
- [ ] `git status` sin `data/raw`; procesado sin subir; prod intacta.
