# Validación de fuentes nuevas 2026-11-04

Fecha: 2026-11-04
Método: scripts/validar_fuentes_nuevas.py sobre raw existentes, join contra dim 252.

## Resultado

- eustat_poblacion_edad: bandas Total, 0-19, 20-64, >=65. poblacion_15_29_derivable False. Baja: no se puede derivar 15-29.
- eustat_renta_edad: columnas sexo, tipo, edad, periodo y renta media CAE. renta_edad_municipal False. Baja: sin ambito municipal, no es salario municipal.
- Alokabide: alokabide_raw [] y cobertura 0. Baja: sin raw ni join, no se crea extractor.
- Nivel2 para scraping dirigido: 66 municipios Nivel2. Candidato futuro, fuera de este cambio.

## Decisión

Ninguna fuente es alta con lo que hay en disco. Se corta el extractor y se deja sin dato. Se mantiene EMAL 73, Eustat 252 como fuentes planas con proxy declarado y sin imputar.

## Evidencia

- poblacion_bandas ['20 - 64', 'Total', '0 - 19', '>= 65']
- renta_edad_cols sin ámbito municipal
- pytest 108 passed, 2 skipped
