# Propuesta — VPO: unidades, escala y lectura regenerable

## Problema

El indicador 73 de Udalmap se publica en ‰ (por mil habitantes) y se acumula
en una ventana móvil de cinco años. En la documentación y en el deck se lee a
veces como si fuera un porcentaje anual, y la serie de VPO usa dos paneles con
escalas distintas (CAE/Bizkaia/Gipuzkoa frente a Araba/Álava). El resultado es
correcto, pero la comparación visual y oral puede inducir a error: 40,1 ‰ no es
un 40 %, sino un 4,01 % acumulado en cinco años; 2,7 ‰ no es un 2,7 %, sino un
0,27 %.

Además, el gráfico H5 titula «Los 15 municipios con más VPO terminada» cuando
el eje es una tasa por mil habitantes, no un número de viviendas.

## Objetivo

Corregir la representación y la lectura en figuras, memoria, README y deck,
sin cambiar los datos ni los cálculos. Todo debe regenerarse desde los scripts
del repositorio.

## Alcance

- `transform/generar_figuras_N.py`: serie VPO con escala común y zoom.
- `analysis/run_analisis_mongo.py`: título y nota del H5.
- `docs/memoria/06-resultados.md`, `docs/memoria/anexos.md` y tokens de
  `docs/memoria/build.py` / `_cifras.json`.
- `README.md` y `docs/presentacion_v2/index.html` / `guion.md`.
- `config/vintage_figuras.yaml` solo si cambia la etiqueta de la figura.

## Fuera de alcance

- No se modifican `data/raw`, `data/procesado`, Mongo ni los valores del
  indicador.
- No se añaden cifras absolutas que no estén en una fuente regenerable del
  repositorio.
- No se toca el deck antiguo `docs/presentacion/`.

## Criterios de aceptación

1. La serie VPO usa una escala común para los cuatro territorios y un panel
   de zoom explícito para CAE/Bizkaia/Gipuzkoa; no hay dos escalas silenciosas.
2. Las anotaciones de la serie incluyen la conversión a % y el carácter
   acumulado de cinco años.
3. El H5 dice «mayor tasa» y aclara que es una tasa, no un conteo de viviendas.
4. Memoria, README y deck usan la misma fórmula y las mismas conversiones:
   2,7 ‰ = 0,27 %; 11,5 ‰ = 1,15 %; 40,1 ‰ = 4,01 %.
5. Las menciones a Etxebide dicen «5.040 registros municipio-año», no
   «5.040 solicitudes».
6. `python transform/generar_figuras_N.py`, la regeneración de H5, la
   sincronización de figuras y `python docs/memoria/build.py --all` reproducen
   los artefactos sin pasos manuales.
