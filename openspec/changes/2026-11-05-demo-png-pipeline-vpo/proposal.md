# Proposal: demo-png-pipeline-vpo

## Intent

Cerrar los cuatro puntos que quedan entre el proyecto y una defensa sin
sorpresas: el exportador de PNG desde Mongo falla en Windows, el guion aún no
cita la VPO de flujo ni la sensibilidad, la secuencia de demo no está
cronometrada y `vpo_municipal` es una colección pasiva sin pipeline propio.

## Scope

### In Scope
- Arreglar `exportar_png_desde_mongo` para que escriba los 13 PNG en Windows.
- Añadir `pipeline_vpo_terminadas` como novena agregación y registrarla en
  el orden canónico (entra en la huella).
- Actualizar guion, datos finales y conteos de pipelines/ficheros.
- Ejecutar y cronometrar la secuencia completa de demo.

### Out of Scope
- Nuevos CSV canónicos (el pipeline entra en la huella, no en `EXPORTS_5`).
- Tocar `data/raw`, Kafka o HDFS.
- Renombrar la comparativa histórica.

## Capabilities

### Modified Capabilities
- `mongodb-y-analisis`: AGREGACION-02 (novena pipeline de VPO terminada).

## Approach

Guardar la figura en un `BytesIO` y escribir los bytes con `Path.write_bytes`,
sin dejar que PIL interprete la ruta. Registrar el pipeline en
`PIPELINE_ORDER` para que la huella lo cubra. Verificar con los 13 ficheros
>0 bytes y un test que exige 251 filas.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| La huella cambia al añadir el pipeline | High | Recalcular y actualizar todas las citas |
| El guardado en BytesIO falla igual | Low | Verificar tamaño de los 13 PNG |
| Docs con "8 pipelines" dispersos | Med | `grep` final antes del commit |

## Success Criteria

- [ ] 13 PNG generados, todos >0 bytes.
- [ ] 9 pipelines y huella nueva reproducible.
- [ ] Guion con VPO de flujo y sensibilidad.
- [ ] `pytest` verde y gate 18/18.
