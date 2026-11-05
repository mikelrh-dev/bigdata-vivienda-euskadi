# Delta for presentacion-de-resultados (bloque-4)

## ADDED Requirements

### Requirement: RESPUESTA-01 — Respuesta comparativa de 4 robustos con matriz O1-O4

El sistema SHALL compare 4 municipios robustos —Bilbao 173, Donostia 113,
Getxo 40, Vitoria-Gasteiz 39 anuncios— con paro Lanbide no nulo o silver
justificado, y SHALL documentar la matriz O1-O4 en
`docs/conclusiones_municipios.md` con mediana 26,61 (oficial 18-34) y 25,2%
sobre 30. La matriz SHALL advertir que Getxo 40 vs Vitoria-Gasteiz 39 difiere
en 1 anuncio y MUST NOT leerse como ranking firme entre esos dos. La
comparativa SHALL registrarse en `docs/trazabilidad_vm.md` (Fecha/Objetivo/
Máquina/Comando/Salida/Conclusión) y MUST NOT tocar `data/raw` ni raw HDFS,
ni crear carpeta nueva, ni subir procesado.

#### Scenario: Cuatro robustos con paro no nulo

- GIVEN los 4 robustos Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39
- WHEN se genera la comparativa en `docs/conclusiones_municipios.md`
- THEN el paro Lanbide no es nulo o consta justificación silver
- AND la salida está trazada en `docs/trazabilidad_vm.md`

#### Scenario: Matriz O1-O4 con advertencia Getxo/Vitoria

- GIVEN la matriz O1-O4 con mediana 26,61 y 25,2% sobre 30
- WHEN se lee la comparación Getxo 40 vs Vitoria-Gasteiz 39
- THEN figura la advertencia de 1 anuncio de diferencia
- AND NO se presenta como ranking firme

## MODIFIED Requirements

### Requirement: INDICADORES-01 — Cinco indicadores con pipeline Mongo verdadero o silver justificado

El sistema SHALL calcular 5 indicadores con pipeline Mongo verdadero para
tensión social y paro Lanbide, o SHALL declararlos silver con justificación
documentada y sin inventar valores. SHALL preservar `metodo_imputacion` y
MUST NOT aplicar `fillna` mediana sin flag `is_imputed`. Los CSV canónicos
con huella SHALL ser 253 y 253 filas y 3 automáticos (regenerables).
(Previously: 5 indicadores con 2+ fuentes y reproducibilidad desde MongoDB,
y tensión/paro en SHOULD por silver según `auditoria_lagunas_silver.csv`.)

#### Scenario: Pipeline verdadero o silver justificado

- GIVEN los 5 indicadores con tensión social y paro Lanbide
- WHEN se ejecutan las pipelines sobre MongoDB
- THEN existen pipelines Mongo reales o justificación silver documentada
- AND `metodo_imputacion` se preserva en la salida
- AND todo `fillna` mediana lleva flag `is_imputed`

#### Scenario: CSV canónicos con huella

- GIVEN los 5 indicadores calculados
- WHEN se resumen los resultados en `docs/matriz_indicadores.md`
- THEN constan los CSV 253 y 253 filas y 3 automáticos con huella
- AND regenerar reproduce los mismos resultados

### Requirement: CONCLUSION-01 — Guion Tema 8 de 1 página con 10 criterios y lagunas

El sistema SHALL redactar en `docs/guion_defensa.md` un guion Tema 8 de 1
página centrado en embedding, índices y atomicidad, con la cadena offline
HDFS centro + Kafka pid 1832. SHALL documentar los 10 criterios y las lagunas,
y MUST NOT dejar 16-29 sin marcar: 16-29 SHALL marcarse legacy y el canónico
es 18-34. La cadena offline SHALL limitarse a lectura de HDFS centro y MUST
NOT tocar `data/raw` ni raw HDFS, ni crear carpeta nueva, ni subir procesado;
prod intacta por defecto (solo lectura o test con
`MONGO_ALLOW_DESTRUCTIVE=1`).
(Previously: comparación de 3 municipios vinculada a indicadores, con
advertencia de muestra pequeña.)

#### Scenario: Guion de 1 página con cadena actual

- GIVEN `docs/guion_defensa.md`
- WHEN se revisa el guion Tema 8
- THEN tiene 1 página con embedding, índices, atomicidad y HDFS centro + Kafka pid 1832
- AND constan los 10 criterios y las lagunas documentadas

#### Scenario: 16-29 marcado legacy

- GIVEN el guion Tema 8 y la matriz O1-O4
- WHEN aparece el rango 16-29
- THEN está marcado legacy y el canónico es 18-34
- AND ninguna conclusión usa 16-29 como rango canónico
