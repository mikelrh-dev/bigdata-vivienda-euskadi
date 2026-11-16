# Tareas — VPO: unidades, escala y lectura

- [x] **T1. Serie VPO con escala común + zoom**
  - Archivo: `transform/generar_figuras_N.py`
  - Acceptance: `S_serie_vpo_2004_2024.png` muestra los cuatro territorios en
    escala común y un zoom 0–14 para CAE/Bizkaia/Gipuzkoa; anota ‰ y %.
  - Verify: regenerar y abrir el PNG; `verificar_vintage_figuras.py`.

- [x] **T2. H5: título de tasa y nota de unidad**
  - Archivo: `analysis/run_analisis_mongo.py`
  - Acceptance: el panel izquierdo dice «mayor tasa de VPO terminada (‰)» y
    advierte que no es número de viviendas.
  - Verify: regenerar H5 y abrir el PNG.

- [x] **T3. Tokens de memoria derivados del raw**
  - Archivos: `docs/memoria/build.py`, `docs/memoria/_cifras.json`
  - Acceptance: existen tokens `datos.vpo_*` para CAE/Araba, pico/2024, ‰ y %;
    se calculan desde `data/raw/udalmap_vpo_terminadas.csv`.
  - Verify: `python docs/memoria/build.py --refresh` y `--check`.

- [x] **T4. Memoria: fórmula, conversiones y anexo**
  - Archivos: `docs/memoria/06-resultados.md`, `docs/memoria/anexos.md`
  - Acceptance: §6.3 explica la fórmula, el denominador medio y VPO+VVSS; la
    tabla pico/2024 usa tokens; el glosario aclara ‰ y VPO.
  - Verify: `python docs/memoria/build.py --check --build`.

- [x] **T5. README y deck: misma lectura**
  - Archivos: `README.md`, `docs/presentacion_v2/index.html`,
    `docs/presentacion_v2/guion.md`, `docs/presentacion_v2/README.md`
  - Acceptance: 2,7 ‰ = 0,27 %, 11,5 ‰ = 1,15 %, 40,1 ‰ = 4,01 %; H5 se
    describe como tasa; «5.040 solicitudes» pasa a «5.040 registros
    municipio-año».
  - Verify: `grep` de las cadenas prohibidas y revisión del HTML.

- [x] **T6. Reconstrucción y verificación**
  - Acceptance: figuras regeneradas, sincronizadas, memoria en 4 formatos,
    deck PDF actualizado y verificadores en verde.
  - Verify: `verificar_cifras_deck.py`, `verificar_vintage_figuras.py`,
    `docs/memoria/build.py --check`, `pytest` focalizado.
