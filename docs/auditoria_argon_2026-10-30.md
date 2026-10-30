# Auditoría de la carpeta argon/ — Conclusiones

Repo: bigdata-vivienda-euskadi | Modo: solo lectura | Fecha: 2026-10-30
Fuentes: resultados de 3 subagentes (claims cuantitativos, parámetros de datos, consistencia OpenSpec).

## 1. Claims cuantitativos (argon/*.md vs repo)

| Claim | Declarado | Real | Estado |
|---|---|---|---|
| Archivos data/raw | 313 datos (+.FROZEN=314) | 317 datos (319 entradas incl. .FROZEN + .gitkeep) | MISMATCH |
| .FROZEN | existe, 0 bytes, mode 644 | existe, 0 bytes, mode 644 | OK |
| Manifest SHA-256 | 312/313 entradas | 317 entradas, todos los hashes coinciden | MISMATCH conteo, integridad OK |
| .gitkeep en data/raw | declarado ausente | presente (0 bytes) | MISMATCH |
| Silver data/procesado | 96 datos (+.gitkeep=97) | 101 datos (+.gitkeep=102) | MISMATCH |
| pytest | 59 passed | 59 passed (2.47s) | OK |
| Inmutabilidad raw (manifest) | inmutable, test verde | test_raw_inmutable pasa, 317/317 hashes coinciden; pero 18 archivos raw son escribibles y raw difiere del backup (22 modificados, 21 añadidos) | MISMATCH (estricta) |

## 2. Parámetros de datos (argon vs data/raw)

Discrepancias principales:
- Territorio Bizkaia: argon dice 112, real 113 (sum 252 OK).
- Municipios robustos (n>=30): argon dice 4 (Bilbao, Donostia, Vitoria, Getxo); real 6 (añade Abanto y Ciérvana 31 y Ayala/Aiara 30).
- Municipios sin anuncios: argon dice 170; real 168.
- Fotocasa: argon 57 municipios; real 60 canónicos (61 variantes raw incl. Las Rozas Madrid).
- Anuncios unificados: argon 873; real 873 (fotocasa 473, pisos 261, realtyapi 139).
- Pisos: argon 230; raw 235 (230 = enriquecido).
- Fotocasa detalle codigo_ine: argon 55/252; real 60/252.
- Alquiler municipal: argon 253x18 con codigo_ine; real 253x15 sin codigo_ine (cobertura 159/252 por municipio OK).
- ECVI XLSX: argon 2; real 3.
- GeoJSON: argon 0x0; real wrapper con 252 features.
- Pisos geo_invalida: argon 235/235; real 261 (todos los pisos en unificado).
- Archivos no listados en inventario: 5 anuncios directed nuevos, distancias_b5m_gipuzkoa.json, distancias_municipios.zip.

Verificados sin discrepancia: 252 municipios, haversine 63504, capitales 252, html_fotocasa 101, fotocasa 471, realtyapi 139, habitaciones (fotocasa 155, pisos 46), ECVI CSV 65, GTFS 13, shapefile 5, comarcas 20, tests 59.

## 3. Consistencia con OpenSpec / estado del proyecto

Gaps detectados:
- Fases no reconciliadas: argon usa fases 0-10; openspec/plan/fases.md usa 0-9 con alcance/estado distinto (ej. salarios "pendiente" allí).
- Puntuación de preguntas: informe_preguntas_respuesta.md dice media 8.2/10 (42 preguntas), estado_proyecto dice 8.6/10, README_ARGON dice 8.6. Contradicción.
- README_proyecto.md (argon) desactualizado vs README raíz en varios puntos (dim_municipios_enriquecido 252x65 vs 252x44; cobertura 85 vs 71 municipios con anuncios). README raíz referencia openspec/plan/PLAN.md inexistente.
- Errores de nombres de archivo en argon: extract/04_b5m.py -> real 04_b5m_geo.py; extract/08_pisos.py -> real 08_pisos_scraper.py; transform/limpieza.py y transform/enrich.py no existen aún; docs plan_* viven en docs/legacy/; docs/informe_resultados.md no creado.
- Deuda desactualizada: "05_fotocasa no persiste HTML" es falso (escribe data/raw/html_fotocasa/); "09_realtyapi stray PY" y "08_pisos no extrae superficie/habitaciones" también desactualizados.
- Drift de conteos vs repo: raw 319 vs doc 313; manifest 317 vs 312; silver 101 vs 96; unificados 873/84 muns con 6 >=30 (docs dicen 873-872/85 y 4-7).

Veredicto: los docs de argon son útiles como radiografía y coinciden con el contrato en lo macro (extracción hecha, infra pendiente), pero su metadata (scores, conteos, nombres de archivo, deuda) está inconsistente/desactualizada y no debe tratarse como autoritativa hasta reconciliarse.

## 4. Conclusiones

- La auditoría de datos (framework_auditoria_completo2) se mantiene: métricas reales ya guardadas en docs/auditoria_framework_completo2_2026-10-30.md.
- La carpeta argon/ tiene valor informativo pero requiere reconciliación de conteos y nombres antes de usarse como fuente de verdad.
- Riesgo principal: claims stale (HTML no persistido, stray PY, superficie faltante) ya resueltos en el repo pero aún documentados como deuda.

## 5. Plan de corrección (esperar OK)

1. Actualizar argon/inventario_datos.md: raw 317, manifest 317, silver 101, geojson 252 features, alquiler 253x15 sin codigo_ine, ECVI xlsx 3, fotocasa 60 canónicos, unificados 873.
2. Actualizar argon/metodologia.md: 6 municipios robustos, 168 sin anuncios, fotocasa 60, pisos 235 raw/230 enriquecido.
3. Reconciliar puntuación de preguntas (8.2 vs 8.6) y elegir una fuente.
4. Corregir nombres de archivos y rutas en argon docs (04_b5m_geo.py, 08_pisos_scraper.py, legacy/, etc.).
5. Marcar deuda resuelta (HTML persistido, superficie/habitaciones extraídos, stray PY).
6. Alinear fases entre argon y openspec/plan/fases.md.
PY