# mongodb-y-analisis — Delta

## ADDED Requirements

### Requirement: AGREGACION-02 — Novena pipeline de VPO terminada

El sistema SHALL exponer la VPO terminada municipal mediante un pipeline de
agregación propio sobre la colección `vpo_municipal`, integrado en el orden
canónico y, por tanto, en la huella de resultados.

#### Scenario: Ejecución municipal
- GIVEN la colección `vpo_municipal` con 252 documentos
- WHEN se ejecuta `pipeline_vpo_terminadas()`
- THEN devuelve 251 filas (excluye el municipio sin dato)
- AND cada fila incluye `codigo_ine`, `municipio`, `territorio` y el valor por mil

#### Scenario: Reproducibilidad
- GIVEN dos ejecuciones consecutivas de `run_all_estandar()`
- WHEN se calcula `huella_resultados`
- THEN las dos huellas coinciden e incluyen la novena pipeline

#### Scenario: El flujo no se presenta como stock
- GIVEN una fila con `vpo_terminadas_por_mil` alto
- WHEN se redacta la conclusión
- THEN se describe como VPO terminada 2020-2024
- AND no se infiere stock histórico
