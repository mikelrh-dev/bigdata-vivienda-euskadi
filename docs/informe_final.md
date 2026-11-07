# Informe final — vivienda y emancipación juvenil en Euskadi

Fecha: 2026-11-05. Rama: `cierre/suficiencia-auditoria`. Todas las cifras de
este informe salen de `data/resultados/` o de Mongo; ninguna está tecleada a
mano sin artefacto que la respalde.

## 1. Veredicto

**GO con deuda acotada.** El proyecto responde las cuatro preguntas del reto
con datos reales y una cadena reproducible, y la deuda detectada en la
auditoría queda cerrada o declarada:

| Deuda | Estado |
|---|---|
| Manifest silver no verificaba | Cerrada: `--verify` exit 0 (354 raw / 188 silver) |
| Dos definiciones de esfuerzo | Cerrada: mediana canónica en silver, Mongo y CSV |
| Ocho cifras falsas en docs | Cerrada: VPO, colecciones, tests, duplicados, sin anuncios |
| VPO "sin dato" | Parcial: flujo oficial integrado; stock sigue sin fuente |
| Ranking de 252 municipios | Cerrada: ranking n>=30 (4 rankeables; resto `n_insuficiente`, Barakaldo n=6 bloqueado) |
| Salario/desempleo juvenil real | Proxy declarado; sin fuente municipal |

## 2. Cadena de datos

```
356 ficheros raw (354 con hash)  →  188 silver (188 con manifest)
        →  Mongo 14 colecciones  →  10 aggregation pipelines
        →  5 CSV canónicos + comparativa + VPO + sensibilidad
```

- Raw inmutable con `.FROZEN`, guard y manifest SHA-256.
- Silver regenerado desde raw; `run_all.py --check` sin avisos.
- Mongo local con 252 municipios, 594 anuncios, 5040 solicitudes Etxebide,
  406 promociones y 252 documentos de VPO municipal.
- Recarga vigente: **594 anuncios** (326 larga estancia + 268 temporal),
  **188 municipios Tier D en cero** (sin anuncios) y **Bilbao 204 anuncios
  como máximo**. Paro Lanbide 252/252 (0 imputadas). 759 era el pre-change.
- Huella agregada de los pipelines:
  `f26264b6c9ec024a27b36a99546dffdc71bb4cdd5aff61fc8519e15b17fa19d0`
  (dos ejecuciones consecutivas, misma huella).

## 3. Base de datos

| Métrica | Valor |
|---|---:|
| Municipios de referencia | 252 |
| Anuncios unificados | 594 (326 larga estancia, 268 temporal) |
| Municipios con anuncios | 64 |
| Municipios sin anuncios | 188 |
| Alquiler oficial Eustat | 159/252 |
| Alquiler imputado IDW | 93/252 |
| Municipios robustos (n≥30) | 4 |
| Promociones Etxebide | 406 en 77 municipios |
| Viviendas en promociones | 0 (`NumViviendas` vacío 406/406) |
| VPO terminada 2024 | 251/252 (Usansolo sin dato) |

No hay duplicados: 1.828 anuncios transformados → 873 tras dedup portal+id
(955 eliminados) → 639 tras dedup `property_fingerprint` (234 cross-portal) →
594 tras cuarentena pisos (45); 0 duplicados de fingerprint.

## 4. Resultados (O1–O4)

### O1 — ¿Puede un joven independizarse?

- Esfuerzo canónico 18-34 (cuantía mediana Eustat): **26,61 %** de la renta
  anual en los 159 municipios con alquiler oficial.
- **40 de 159** municipios superan el 30 % (25,2 %).
- Si se añaden los 93 imputados: mediana 25,37 % y 47/252 sobre 30 % (18,7 %).
- La emancipación municipal no es defendible: la renta es un proxy, no el
  salario real del joven.

### O2 — ¿Qué municipios son viables?

Solo 4 municipios tienen muestra suficiente. Esfuerzo canónico y n
(`ranking_esfuerzo.csv`: solo n_anuncios>=30; el resto es `n_insuficiente`):

| Municipio | `codigo_ine` | n | Esfuerzo 18-34 |
|---|---|---:|---:|
| Donostia | 20069 | 126 | 38,17 % |
| Bilbao | 48020 | 204 | 37,69 % |
| Vitoria-Gasteiz | 01059 | 39 | 33,37 % |
| Getxo | 48044 | 50 | 28,60 % |

Barakaldo (48013) tiene n=6 (`n_insuficiente`) y no ranking nunca por encima
de Donostia (n=126) ni de ningún Tier A. Getxo (50) y Vitoria (39) están
cerca en n, pero con esfuerzo e ICs que se solapan: no hay ranking firme
entre ambos, es una comparación.

### O3 — ¿Trabajo y vivienda barata?

No hay trade-off simple: conteo de parados jóvenes y alquiler correlacionan +0,39 (conteos, no tasa);
distancia mínima a capital y alquiler, −0,603. Los municipios baratos no son
sistemáticamente los de mejor empleo.

### O4 — Límites

Proxy de renta (falacia ecológica), 93 alquileres imputados, 4 robustos,
emancipación solo CAE, mezcla de años (2026 anuncios / 2024 renta), ECVI solo
territorial y VPO sin stock histórico.

## 5. Sensibilidad

**IDW vs oficial** (`data/resultados/sensibilidad_idw.csv`):

| Escenario | n | Mediana | >30 % |
|---|---:|---:|---:|
| Solo oficial | 159 | 26,61 % | 25,2 % |
| Oficial + IDW | 252 | 25,37 % | 18,7 % |

El signo del titular no cambia; la imputación rebaja la mediana 1,24 pp.

**Bootstrap de los 4 robustos** (`data/resultados/bootstrap_robustos.csv`,
10.000 remuestreos, semilla 42). El nivel lo fija Eustat; el intervalo mide
solo la dispersión de la muestra de anuncios:

| Municipio | n | Esfuerzo | IC 95 % | Amplitud |
|---|---:|---:|---|---:|
| Bilbao | 67 | 37,69 % | 33,75–40,95 | 7,20 pp |
| Donostia | 60 | 38,17 % | 32,44–45,80 | 13,36 pp |
| Getxo | 39 | 28,60 % | 27,54–31,77 | 4,24 pp |
| Vitoria-Gasteiz | 37 | 33,37 % | 30,80–39,40 | 8,60 pp |

Los intervalos de Bilbao y Donostia se solapan: el orden entre ambos no es
defendible. Getxo queda por debajo de los cuatro (IC 27,54–31,77 %, por
debajo del 30 % en casi todo el intervalo).

## 6. VPO: flujo oficial, no stock

El indicador 73 de Udalmap mide VPO **terminada en el último quinquenio** por
mil habitantes. Se integra como colección `vpo_municipal`:

- 252 filas, 251 con valor; Usansolo (48916, segregado en 2023) sin dato.
- Mediana 0,00 ‰ y máximo 62,55 ‰: es un flujo muy concentrado en pocos años.
- El origen publica 272 códigos; el parser descarta 20 comarcales o disueltos.
- El stock histórico de VPO sigue **sin dato**: `NumViviendas` viene vacío en
  406/406 promociones y no se imputa.

## 7. Reproducibilidad

```bash
.venv/Scripts/python.exe transform/run_all.py --check          # exit 0
.venv/Scripts/python.exe extract/generar_manifest.py --verify  # 354 / 188, 0 errores
.venv/Scripts/python.exe -m pytest tests -q                    # 177 passed + 1 skipped
.venv/Scripts/python.exe scripts/verificar_fase_datos.py       # OK 18/18
.venv/Scripts/python.exe -m storage.load_mongo                 # 14 colecciones
.venv/Scripts/python.exe analysis/run_analisis_mongo.py        # 10 pipelines + huella
.venv/Scripts/python.exe analysis/sensibilidad.py              # IDW + bootstrap
```

## 8. Artefactos de evidencia

- `data/resultados/mongo_esfuerzo_por_municipio.csv` (252)
- `data/resultados/mongo_alquiler_por_municipio.csv` (252)
- `data/resultados/mongo_vpo_por_municipio.csv` (322 filas, 77 municipios; `viviendas` vacío = sin dato, no stock cero)
- `data/resultados/comparativa_3_municipios_mongo.csv` (4 filas; nombre histórico)
- `data/resultados/sensibilidad_idw.csv`
- `data/resultados/bootstrap_robustos.csv`
- `docs/datos_finales_conclusiones_2026-11-05.md` (huella y conteos)
- `docs/diccionario_columnas.md` (qué columna manda)
- `docs/matriz_indicadores.md` (indicador canónico y pipeline)
