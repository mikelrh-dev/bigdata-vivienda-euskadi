# extraccion-datos — Delta

## Purpose

Re-resolver la ubicación real de pisos.com (245 anuncios): el subtítulo/título manda; `municipio_busqueda` es búsqueda, NUNCA ubicación. Estado: propuesta (delta desde base Desplegada).

## MODIFIED Requirements

### Requirement: EXTRACCION-01 — Ubicación real desde subtítulo/título

El sistema SHALL conservar subtítulo y título al extraer (`extract/08_pisos_scraper.py`) con `es_busqueda_no_ubicacion=True`, y SHALL resolver el municipio SOLO por coincidencia textual en subtítulo/título contra variantes de `dim_municipios` + gazetteer barrio→municipio. `codigo_ine` SHALL NOT propagarse sin coincidencia textual. Lo no resuelto SHALL ir a fallback detalle o cuarentena (PISOS-02).

#### Scenario: Pisos re-resueltos con evidencia textual

- GIVEN raw pisos con subtítulo «Piso en Santutxu, Bilbao»
- WHEN se ejecuta `transform/unificar_anuncios.py` (`transform_pisos`)
- THEN `ubicacion.municipio=Bilbao` vía gazetteer y `origen_resolucion=subtitulo`

#### Scenario: Código sin texto no vale

- GIVEN anuncio con `codigo_ine` pero sin municipio en subtítulo/título
- WHEN se resuelve
- THEN no se asigna municipio y pasa a cuarentena motivada

## ADDED Requirements

### Requirement: PISOS-01 — Evidencia y orden de resolución

El sistema SHALL aplicar en orden: (1) subtítulo, (2) título, (3) gazetteer, (4) fallback detalle, (5) cuarentena. `municipio_busqueda` SHALL NOT usarse como ubicación en ningún paso.

#### Scenario: Orden verificable

- GIVEN anuncio con subtítulo ambiguo («Santutxu» sin municipio)
- WHEN corre `python transform/unificar_anuncios.py`
- THEN resuelve por gazetteer a Bilbao con `origen_resolucion=gazetteer`
- AND `pytest tests/test_pisos_ubicacion_real.py -q` → `245 passed` (o no-resueltos en cuarentena)

### Requirement: PISOS-02 — Cuarentena geo_invalida

El sistema SHALL marcar `geo_invalida=True` y cuarentena reversible a todo piso fuera de `dim_municipios`/Euskadi o sin subtítulo. SHALL NOT tocar Eustat/Lanbide. Raw sigue solo en HDFS; Kafka→HDFS, nunca Kafka→Mongo; sin Docker.

| Caso | Resultado |
|---|---|
| Subtítulo ambiguo | gazetteer o cuarentena, nunca búsqueda |
| Fuera de Euskadi | `geo_invalida=True`, reversible |
| Sin subtítulo | fallback detalle o cuarentena |

#### Scenario: Fuera de Euskadi en cuarentena

- GIVEN subtítulo «Piso en Madrid»
- WHEN se resuelve
- THEN `geo_invalida=True`, excluido de `dim_municipios` y conteos L1/L2
- AND `grep -c geo_invalida` en informe = anuncios fuera de Euskadi
