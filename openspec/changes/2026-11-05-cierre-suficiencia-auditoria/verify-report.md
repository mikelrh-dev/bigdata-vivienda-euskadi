# Verify report — cierre-suficiencia-auditoria

Fecha: 2026-11-05. Rama `cierre/suficiencia-auditoria`.

## Evidencia por unidad

### U1 — Gold, manifests y docs

```
$ python transform/construir_dim_gold.py
OK: ...dim_municipios_enriquecido.csv (252 filas, 91 cols)

$ python extract/generar_manifest.py --verify
OK: docs/raw_manifest_sha256.txt (353 entradas, 0 errores)
OK: data/procesado/manifest_sha256.txt (184 entradas, 0 errores)

$ python transform/run_all.py --check
(exit 0)
```

Cifras corregidas y verificadas contra los datos: 169 municipios sin anuncios,
86 duplicados (845→759, 10,18 %), 15 colecciones (entonces), 130 tests,
`auditoria_lagunas_silver.csv` regenerado (40 CSV), C1 a Parcial.

### U2 — Una sola definición de esfuerzo

Cambio: `transform/generar_analisis_variables_base.py` usa
`cuantia_media_eur_mes_mediana` (con la media solo como contraste).

```
$ python -m storage.load_mongo
{... 'indicadores': 252, 'vpo_municipal': 252}

$ python analysis/run_analisis_mongo.py
huella: d7e673240f9290422d0eb3801592da542d4a8db7bacb48510e641b519f8845ca
reproducibilidad: ok (dos ejecuciones con la misma huella)

Delta VPO vs indicadores (77 municipios):
max 0.0495 pp; 0 casos > 0.05 pp  → solo redondeo a un decimal
```

Tensión recalculada: **76 alta / 103 media / 73 baja** (antes 75/104/73).
Canónicos sin cambio de titular: mediana oficial 26,61 %, 40/159 > 30 %
(25,2 %); global 25,37 %, 47/252 (18,7 %).

### U3 — VPO municipal oficial

```
$ python extract/26_vpo_terminadas.py --promote
staging OK: 272 municipios, 2024 0.00-62.55 ‰
sha256 raw: 70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706

$ python transform/limpiar_vpo_municipal.py
descartados 20 codigos sin municipio vivo (comarcas/disueltos)
Generado ...vpo_municipal.csv: 252 filas, 6 cols
VPO terminadas 2024: mediana 0.00 ‰, max 62.55 ‰, sin dato 1

$ python -m pytest tests/test_vpo_municipal.py -q
6 passed
```

`vpo_municipal` = 252 documentos. Manifest: 354 raw / 185 silver, 0 errores.
`ingestion_manifest.json` = 354 ficheros e incluye el CSV nuevo. Gate 18/18.

### U4 — Sensibilidad e informe

```
$ python analysis/sensibilidad.py
oficial_159  159  26.61  40  25.2
idw_252      252  25.37  47  18.7

Bilbao 48020 51 37.69 32.32-42.40
Donostia 20069 51 38.17 32.44-45.80
Getxo 48044 31 28.60 28.60-32.99
Vitoria 01059 37 33.37 30.80-39.40
```

## Gate final

```
$ python -m pytest tests -q
136 passed

$ python extract/generar_manifest.py --verify
OK: docs/raw_manifest_sha256.txt (354 entradas, 0 errores)
OK: data/procesado/manifest_sha256.txt (185 entradas, 0 errores)

$ python transform/run_all.py --check
(exit 0, sin avisos)

$ python scripts/verificar_fase_datos.py
RESULTADO: OK 18/18

$ git status --short
(sin cambios pendientes tras el commit de cierre)
```

## Desviaciones declaradas

1. **D5 (renombrar la comparativa) no se ejecuta.** El nombre
   `comparativa_3_municipios_mongo.csv` aparece en 26 referencias y en el
   material de defensa; renombrarlo rompe citas sin aportar dato. Se mantiene
   el nombre y se documenta que contiene 4 filas (`data/resultados/README.md`).
2. **D6 (archivar changes) queda diferido.** Hay 15 changes con
   `verify-report.md` pero sin merge de su delta en `openspec/specs/`. Archivarlos
   sin fusionar la spec perdería requisitos; se deja como deuda SDD explícita.
3. **Getxo: IC inferior = valor puntual.** No es un error de cálculo: la
   mediana de precios es muy estable en la remuestra; se reporta tal cual.

## Conclusión

GO con deuda acotada. La deuda que impedía defender el proyecto (manifests
rotos, dos esfuerzos, cifras falsas, VPO sin dato) está cerrada con evidencia
literal. Las tres desviaciones son decisiones documentadas, no fallos ocultos.
