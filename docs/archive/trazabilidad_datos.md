# Trazabilidad de datos — Fase 1

> Generado tras ejecutar las tareas de gestión de datos (Fase 1).  
> Referencia: `docs/inventario_datos.md` (inventario completo de 325 archivos crudos) y `docs/plan_gestion_datos_fase1.md`.

## Transformaciones ejecutadas

| Tarea | Script | Entrada (origen) | Salida (destino) | Filas | Motivo |
|---|---|---|---|---|---|
| 1.1 Normalizar `codigo_ine` | `transform/normalizar_json_crudos.py` | `data/raw/*.json` (47) | `data/procesado/*_normalizado.json` (47) | — | Forzar `str.zfill(5)` en `codigo_ine` raíz y `ubicacion.codigo_ine`; eliminar `None`. |
| 1.2 Limpiar ECVI | `transform/limpiar_ecvi.py` | `data/raw/ecvi_ecvi_es_2026t2_t{1,2,3}_{2,3}.csv` (6) | `data/procesado/ecvi_compraventa_limpio.json` + `.csv` | 29 | Parser de cabeceras múltiples → columnas nombradas (territorio, área funcional, municipio). |
| 1.3 Desglosar Eustat | `transform/limpiar_eustat_demografia.py` | `data/raw/eustat_renta_municipal.csv`, `eustat_poblacion_edad.csv` | `data/procesado/eustat_demografia_renta_252.json` + `.csv` | 252 | Renta personal (ambos/hombres/mujeres), renta disponible, población total, año. `poblacion_joven_15_29` = null (no disponible en fuente). |
| 1.4 Unificar anuncios | `transform/unificar_anuncios.py` | `anuncios_fotocasa_enriquecido_geo.json`, `anuncios_pisos_enriquecido_geo.json`, `anuncios_realtyapi.json` | `data/procesado/anuncios_unificados.json` + `.csv` | 840 | Esquema único: `ubicacion` anidada + `equipamiento` array + `auditoria`. |

## Relación con inventario de datos

- `docs/inventario_datos.md` inventaria los **325 archivos crudos** (198 tabulares + 127 no tabulares) en `data/raw/`, `data/procesado/` (pre-Fase 1) y `data/resultados/`.
- Tras Fase 1, `data/procesado/` contiene **nuevos archivos normalizados/limpios** (47 JSON normalizados + ECVI + Eustat demografía + anuncios unificados). Estos archivos **no estaban en el inventario original** y deben añadirse en la próxima regeneración del inventario.
- `data/raw/` **no se modificó** (solo lectura).

## Limitaciones documentadas

- `poblacion_joven_15_29` queda null (Eustat solo ofrece grupos 0-19, 20-64, >=65).
- ECVI solo cubre territorios, áreas funcionales y 7 municipios >40k hab.
- Anuncios unificados: solo Fotocasa tiene `equipamiento` array; Pisos/RealtyAPI vacío.
- Modalidad inferida por heurística (temporal si `alquiler_temporal`=true, habitación si tipo contiene "habitación", resto larga_estancia).

## Micro-tareas Fase 1.5 (ejecutadas)

| Tarea | Script | Entrada | Salida | Impacto |
|---|---|---|---|---|
| A. Verificar udalmap JSON | (verificación) | `udalmap_empleo_corregido.json`, `udalmap_indicadores_adicionales.json` | — | C6/C2/C3/E1-E3/B6: datos ya presentes en JSON normalizado |
| B. Enriquecer GTFS | `transform/enriquecer_gtfs_conectividad.py` | 13 ZIPs en `data/raw/gtfs/` + `municipios_euskadi.geojson` | `data/procesado/transporte_paradas_municipio_enriquecido.csv` (252) | D2: 6→9 |
| C. Enriquecer equipamiento RealtyAPI | `transform/enriquecer_equipamiento_realtyapi.py` | `anuncios_unificados.json` + `anuncios_realtyapi.json` | `anuncios_unificados.json` + `.csv` actualizados | C4/C5: parcial (139/840) |
