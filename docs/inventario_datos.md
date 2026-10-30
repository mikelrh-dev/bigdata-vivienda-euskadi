# Inventario de datos — bigdata-vivienda-euskadi

> Generado por inspección automatizada (solo lectura) con pandas sobre `data/raw/`, `data/procesado/` y `data/resultados/`.
> Fecha de inventario: 2026-10-28. Total archivos inventariados: **325**.

## 1. Resumen ejecutivo

- **Archivos totales:** 325 (198 tabulares legibles, 127 no tabulares: HTML, ZIP, shapefile, logs, marcadores).
- **Volumen total en disco:** 380.7 MB (incluye 101 HTML y 13 ZIP GTFS).
- **Filas tabulares (suma):** 572,530 (incluye cabeceras múltiples/blancos en ECVI y originales Eustat).
- **Municipios de referencia (dimensión):** 252 (Álava 51 + Bizkaia 112 + Gipuzkoa 88).
- **Alquiler oficial:** 159 municipios con dato directo Eustat 2024; 93 municipios sin dato rescatados por comarca (`alquiler_municipal_completo.csv`, 252/252).
- **Anuncios (oferta):** Fotocasa y Pisos.com; cobertura 60 y 37 municipios respectivamente; RealtyAPI 3 municipios (opcional).
- **ECVI:** 65 CSV + 2 XLSX de compraventa (trimestral, territorial/comarcal, no municipal).
- **GTFS:** 13 ZIP de operadores de transporte público.
- **Shapefile:** 5 componentes (MUNICIPIOS_5000_ETRS89, EPSG:25830).
- **HTML Fotocasa:** 101 páginas (1 por municipio/provincia).

### Limitaciones principales
- Heterogeneidad de formatos: CSV multi-cabecera (Eustat, ECVI, Etxebide) no parseable estándar; se requiere `skiprows`/limpieza.
- Cobertura parcial de anuncios: Fotocasa 60/252 municipios, Pisos.com 37/252, RealtyAPI 3/252.
- Alquiler oficial: solo 159/252 municipios con dato directo; 93 imputados por comarca (menor precisión).
- ECVI no es municipal (territorial/comarcal) y los CSV son tablas anchas con cabeceras anidadas.
- GTFS y HTML son binarios/texto no tabular; requieren extracción específica.
- Nulos/outliers presentes en varias fuentes (ver columna 'Nulos / outliers').
- `data/resultados/` solo contiene `.gitkeep` (resultados aún no generados).
- Algunos archivos JSON son listas de strings (municipios/códigos), sin columnas tabulares.

### Volumen por categoría

| Categoría | Archivos | Filas (suma) | Tamaño (MB) |
|---|---:|---:|---:|
| Anuncios (portales inmobiliarios) | 28 | 7,175 | 10.1 |
| Anuncios (HTML crudo Fotocasa) | 101 | 0 | 73.8 |
| Anuncios (transformaciones) | 4 | 1,412 | 1.6 |
| Alquiler oficial (Eustat/territorial) | 8 | 4,185 | 0.5 |
| Alquiler oficial (EMAL fianzas) | 5 | 2,976 | 1.0 |
| Alquiler oficial (transformaciones) | 4 | 504 | 0.0 |
| Complementarios (Eustat: población, renta, PIB, tenencia) | 10 | 212,051 | 91.3 |
| Complementarios (ECVI compraventa) | 68 | 5,538 | 2.1 |
| Complementarios (emancipación juvenil) | 2 | 867 | 0.2 |
| Complementarios (Etxebide vivienda social) | 3 | 10,365 | 0.9 |
| Complementarios (INE) | 16 | 20,501 | 6.5 |
| Complementarios (SERPAVI renta fiscal) | 3 | 538 | 67.9 |
| Complementarios (renta municipal derivada) | 3 | 756 | 0.1 |
| Complementarios (servicios) | 4 | 3,674 | 1.5 |
| Complementarios (transformaciones) | 1 | 93 | 0.0 |
| Empleo (Lanbide) | 5 | 71,014 | 44.2 |
| Empleo (Udalmap) | 6 | 1,512 | 1.1 |
| Geografía (municipios/cartografía) | 3 | 504 | 10.6 |
| Geografía (distancias) | 4 | 127,519 | 5.5 |
| Geografía y accesibilidad (OSRM) | 2 | 504 | 0.0 |
| Geografía y transporte | 2 | 504 | 0.1 |
| Geografía (shapefile Euskadi) | 5 | 0 | 7.3 |
| Geografía (transformaciones) | 2 | 344 | 0.0 |
| Transformaciones y control (pipeline) | 16 | 951 | 0.1 |
| Metadatos y control | 3 | 0 | 0.0 |
| Legacy / obsoleto (no usar) | 4 | 99,043 | 5.9 |
| Geografía y transporte (GTFS) | 13 | 0 | 48.2 |

## 2. Inventario detallado por categoría

Columnas de cada tabla: **Archivo** (ruta relativa), **Tipo**, **Tamaño**, **Filas×Cols**, **Columnas principales**, **Cobertura municipal**, **Nulos / outliers**, **Pregunta del proyecto**.

### 2.1 Anuncios (portales inmobiliarios)

_Archivos: 28_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/anuncios_fotocasa.csv` | CSV | 135.4 KB | 471×26 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, precio_eur, municipio … | nombre_canonico: 60/252; municipio: 56/252 | 1693 nulos en 12 cols (trastero:432, parking:383, terraza:329); outliers>3σ: 25 en 6 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa.json` | JSON | 778.9 KB | 471×36 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; municipio: 56/252 | 2710 nulos en 18 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 33 en 8 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_detalle.json` | JSON | 903.8 KB | 470×20 | id_anuncio, codigo_ine, anio_fuente, planta, antiguedad_cod, orientacion_cod … | codigo_ine: 55/252 | 129 nulos en 6 cols (distrito_detalle:114, antiguedad_cod:3, cert_energetico:3); outliers>3σ: 60 en 9 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_enriquecido.json` | JSON | 1.0 MB | 471×47 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; ubicacion.nombre_canonico: 60/252 | 3065 nulos en 22 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 36 en 9 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_enriquecido_geo.json` | JSON | 1.2 MB | 471×55 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; ubicacion.nombre_canonico: 60/252 | 3065 nulos en 22 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 36 en 9 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_enriquecido_meta.json` | JSON | 1.2 MB | 471×53 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; ubicacion.nombre_canonico: 60/252 | 3065 nulos en 22 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 36 en 9 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_geo.json` | JSON | 991.8 KB | 471×44 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; municipio: 56/252 | 2710 nulos en 18 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 33 en 8 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_habitaciones.csv` | CSV | 43.6 KB | 155×19 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, precio_eur, precio_reducido_eur … | codigo_ine: 9/252; nombre_canonico: 9/252 | 257 nulos en 6 cols (precio_reducido_eur:134, barrio:75, superficie_m2:22); outliers>3σ: 24 en 6 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_habitaciones.json` | JSON | 190.8 KB | 155×35 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 9/252; municipio_busqueda: 9/252 | 843 nulos en 14 cols (parking:155, jardin:155, trastero:152); outliers>3σ: 33 en 7 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_habitaciones_geo.json` | JSON | 263.5 KB | 155×43 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 9/252; municipio_busqueda: 9/252 | 843 nulos en 14 cols (parking:155, jardin:155, trastero:152); outliers>3σ: 33 en 7 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_habitaciones_meta.json` | JSON | 240.5 KB | 155×41 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 9/252; municipio_busqueda: 9/252 | 843 nulos en 14 cols (parking:155, jardin:155, trastero:152); outliers>3σ: 33 en 7 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_larga.csv` | CSV | 47.6 KB | 167×26 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, precio_eur, municipio … | codigo_ine: 46/252; nombre_canonico: 46/252 | 613 nulos en 10 cols (trastero:144, parking:123, barrio:109); outliers>3σ: 22 en 6 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_meta.json` | JSON | 922.0 KB | 471×42 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; municipio: 56/252 | 2710 nulos en 18 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 33 en 8 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_fotocasa_temporal.csv` | CSV | 88.1 KB | 304×26 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, precio_eur, municipio … | nombre_canonico: 37/252; municipio: 35/252 | 1080 nulos en 12 cols (trastero:288, parking:260, terraza:225); outliers>3σ: 19 en 6 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos.csv` | CSV | 109.3 KB | 235×19 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; codigo_ine: 37/252 | 521 nulos en 9 cols (tipo_inmueble:232, nombre_canonico:218, precio_eur:22); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos.json` | JSON | 242.9 KB | 235×28 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; ubicacion.municipio: 37/252 | 1946 nulos en 18 cols (ubicacion.coords.lat:235, ubicacion.coords.lon:235, ubicacion.barrio:235); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_busqueda.csv` | CSV | 114.3 KB | 235×21 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | codigo_ine: 42/252; nombre_canonico: 38/252 | 360 nulos en 9 cols (tipo_inmueble:232, nombre_canonico:57, precio_eur:22); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_enriquecido.json` | JSON | 240.0 KB | 230×28 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; ubicacion.municipio: 37/252 | 1881 nulos en 13 cols (ubicacion.coords.lat:230, ubicacion.coords.lon:230, ubicacion.barrio:230); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_enriquecido_geo.json` | JSON | 311.2 KB | 230×34 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; ubicacion.municipio: 37/252 | 1881 nulos en 13 cols (ubicacion.coords.lat:230, ubicacion.coords.lon:230, ubicacion.barrio:230); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_enriquecido_meta.json` | JSON | 311.2 KB | 230×34 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; ubicacion.municipio: 37/252 | 1881 nulos en 13 cols (ubicacion.coords.lat:230, ubicacion.coords.lon:230, ubicacion.barrio:230); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_geo.json` | JSON | 219.6 KB | 230×23 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; nombre_canonico_resuelto: 30/252 | 501 nulos en 7 cols (tipo_inmueble:227, nombre_canonico:218, precio_eur:22); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_habitaciones.csv` | CSV | 12.0 KB | 46×16 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, precio_eur, municipio_busqueda … | codigo_ine: 5/252; nombre_canonico: 5/252 | 186 nulos en 5 cols (tipo_inmueble:46, superficie_m2:46, habitaciones:46); outliers>3σ: 2 en 1 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_habitaciones.json` | JSON | 32.7 KB | 46×17 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 5/252; nombre_canonico: 5/252 | 186 nulos en 5 cols (tipo_inmueble:46, superficie_m2:46, habitaciones:46); sin outliers>3σ | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_habitaciones_geo.json` | JSON | 47.1 KB | 46×23 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 5/252; nombre_canonico: 5/252 | 186 nulos en 5 cols (tipo_inmueble:46, superficie_m2:46, habitaciones:46); sin outliers>3σ | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_habitaciones_meta.json` | JSON | 47.1 KB | 46×23 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 5/252; nombre_canonico: 5/252 | 186 nulos en 5 cols (tipo_inmueble:46, superficie_m2:46, habitaciones:46); sin outliers>3σ | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_pisos_meta.json` | JSON | 219.6 KB | 230×23 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; nombre_canonico_resuelto: 30/252 | 501 nulos en 7 cols (tipo_inmueble:227, nombre_canonico:218, precio_eur:22); outliers>3σ: 18 en 5 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_realtyapi.csv` | CSV | 24.0 KB | 139×17 | id_anuncio, precio_eur, municipio_busqueda, municipio, provincia, distrito … | municipio_busqueda: 3/252; codigo_ine: 3/252 | 79 nulos en 3 cols (barrio:65, exterior:8, planta:6); outliers>3σ: 20 en 4 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |
| `data/raw/anuncios_realtyapi.json` | JSON | 312.5 KB | 139×25 | id_anuncio, url, precio_eur, moneda, operacion, tipo_inmueble … | municipio_busqueda: 3/252; nombre_canonico_resuelto: 3/252 | 220 nulos en 5 cols (tipo_extendido:139, barrio:65, exterior:8); outliers>3σ: 14 en 3 cols | ¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio? |

### 2.2 Anuncios (HTML crudo Fotocasa)

_Archivos: 101_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/html_fotocasa/Abaltzisketa_pagina_1.html` | HTML | 488.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ajangiz_pagina_1.html` | HTML | 667.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Albiztur_pagina_1.html` | HTML | 489.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Alkiza_pagina_1.html` | HTML | 788.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Altzaga_pagina_1.html` | HTML | 488.5 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Altzo_pagina_1.html` | HTML | 489.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Amoroto_pagina_1.html` | HTML | 574.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arakaldo_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arama_pagina_1.html` | HTML | 489.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arantzazu_pagina_1.html` | HTML | 809.3 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Armiñón_pagina_1.html` | HTML | 570.5 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arraia-Maeztu_pagina_1.html` | HTML | 491.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arrankudiaga-Zollo_pagina_1.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arratzu_pagina_1.html` | HTML | 626.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arratzua-Ubarrundia_pagina_1.html` | HTML | 598.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Arrieta_pagina_1.html` | HTML | 1021.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Artea_pagina_1.html` | HTML | 618.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Artzentales_pagina_1.html` | HTML | 1020.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Aulesti_pagina_1.html` | HTML | 572.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Añana_pagina_1.html` | HTML | 558.3 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Baliarrain_pagina_1.html` | HTML | 489.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Barrundia_pagina_1.html` | HTML | 505.8 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Beizama_pagina_1.html` | HTML | 491.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Belauntza_pagina_1.html` | HTML | 512.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Berantevilla_pagina_1.html` | HTML | 675.8 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Bernedo_pagina_1.html` | HTML | 497.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Bidania-Goiatz_pagina_1.html` | HTML | 489.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Elantxobe_pagina_1.html` | HTML | 619.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Elburgo/Burgelu_pagina_1.html` | HTML | 1.3 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Elciego_pagina_1.html` | HTML | 706.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Elduain_pagina_1.html` | HTML | 546.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ereño_pagina_1.html` | HTML | 608.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Errezil_pagina_1.html` | HTML | 717.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Errigoiti_pagina_1.html` | HTML | 837.5 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ezkio-Itsaso_pagina_1.html` | HTML | 504.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Fruiz_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Gabiria_pagina_1.html` | HTML | 504.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Gaintza_pagina_1.html` | HTML | 489.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Galdames_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Gamiz-Fika_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Garai_pagina_1.html` | HTML | 586.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Gaztelu_pagina_1.html` | HTML | 489.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Gizaburuaga_pagina_1.html` | HTML | 559.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Hernialde_pagina_1.html` | HTML | 558.3 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ibarrangelu_pagina_1.html` | HTML | 669.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Iruraiz-Gauna_pagina_1.html` | HTML | 492.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ispaster_pagina_1.html` | HTML | 560.8 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Izurtza_pagina_1.html` | HTML | 586.8 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Kortezubi_pagina_1.html` | HTML | 647.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Kripan_pagina_1.html` | HTML | 539.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Kuartango_pagina_1.html` | HTML | 493.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Lagrán_pagina_1.html` | HTML | 497.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Lanestosa_pagina_1.html` | HTML | 568.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Lantarón_pagina_1.html` | HTML | 569.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Larraul_pagina_1.html` | HTML | 788.5 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Laukiz_pagina_1.html` | HTML | 1.1 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Leintz-Gatzaga_pagina_1.html` | HTML | 538.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Leza_pagina_1.html` | HTML | 542.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Maruri-Jatabe_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Mendata_pagina_1.html` | HTML | 710.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Mendexa_pagina_1.html` | HTML | 546.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Meñaka_pagina_1.html` | HTML | 1.1 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Moreda de Álava/Moreda Araba_pagina_1.html` | HTML | 921.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Morga_pagina_1.html` | HTML | 994.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Munitibar-Arbatzegi Gerrikaitz_pagina_1.html` | HTML | 613.3 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Murueta_pagina_1.html` | HTML | 713.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Mutiloa_pagina_1.html` | HTML | 512.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Muxika_pagina_1.html` | HTML | 891.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Nabarniz_pagina_1.html` | HTML | 574.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Navaridas_pagina_1.html` | HTML | 573.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Orendain_pagina_1.html` | HTML | 497.3 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Orexa_pagina_1.html` | HTML | 496.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Peñacerrada-Urizaharra_pagina_1.html` | HTML | 610.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Samaniego_pagina_1.html` | HTML | 625.5 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Sukarrieta_pagina_1.html` | HTML | 667.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Trucios-Turtzioz_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ubide_pagina_1.html` | HTML | 516.6 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Usansolo_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Zalduondo_pagina_1.html` | HTML | 498.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Zambrana_pagina_1.html` | HTML | 740.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Zeberio_pagina_1.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Zerain_pagina_1.html` | HTML | 504.1 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Zigoitia_pagina_1.html` | HTML | 587.2 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/Ziortza-Bolibar_pagina_1.html` | HTML | 568.0 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/araba_alava_pagina_1.html` | HTML | 896.4 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_1.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_10.html` | HTML | 1.1 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_11.html` | HTML | 872.3 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_12.html` | HTML | 712.7 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_2.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_3.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_4.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_5.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_6.html` | HTML | 1.1 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_7.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_8.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/bizkaia_pagina_9.html` | HTML | 1012.9 KB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/gipuzkoa_pagina_1.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/gipuzkoa_pagina_2.html` | HTML | 1.1 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/gipuzkoa_pagina_3.html` | HTML | 1.0 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |
| `data/raw/html_fotocasa/gipuzkoa_pagina_4.html` | HTML | 1.2 MB | — | — | — | — | Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa. |

### 2.3 Anuncios (transformaciones)

_Archivos: 4_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/procesado/anuncios_fotocasa_filtrado.csv` | CSV | 386.0 KB | 471×42 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; municipio: 56/252 | 3171 nulos en 20 cols (motivo_outlier:451, trastero:432, jardin:429); outliers>3σ: 54 en 10 cols | ¿Cómo se filtran/enriquecen/geolocalizan los anuncios para el análisis? |
| `data/procesado/anuncios_fotocasa_filtrado.json` | JSON | 862.5 KB | 471×42 | codigo_ine, nombre_canonico, anio_fuente, id_anuncio, uuid_anuncio, precio_eur … | nombre_canonico: 60/252; municipio: 56/252 | 2720 nulos en 19 cols (trastero:432, jardin:429, precio_reducido_eur:419); outliers>3σ: 54 en 10 cols | ¿Cómo se filtran/enriquecen/geolocalizan los anuncios para el análisis? |
| `data/procesado/anuncios_pisos_filtrado.csv` | CSV | 115.3 KB | 235×24 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; codigo_ine: 37/252 | 556 nulos en 10 cols (tipo_inmueble:232, motivo_outlier:225, precio_m2_calculado:28); outliers>3σ: 32 en 7 cols | ¿Cómo se filtran/enriquecen/geolocalizan los anuncios para el análisis? |
| `data/procesado/anuncios_pisos_filtrado.json` | JSON | 285.1 KB | 235×34 | id_anuncio, precio_eur, precio_texto, titulo, subtitulo, tipo_inmueble … | municipio_busqueda: 37/252; ubicacion.municipio: 37/252 | 1974 nulos en 19 cols (ubicacion.coords.lat:235, ubicacion.coords.lon:235, ubicacion.barrio:235); outliers>3σ: 32 en 7 cols | ¿Cómo se filtran/enriquecen/geolocalizan los anuncios para el análisis? |

### 2.4 Alquiler oficial (Eustat/territorial)

_Archivos: 8_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/alquiler_distrito_seccion_original.csv` | CSV (multi-cab.) | 16.8 KB | 197×15 | Municipio, Distrito, Sección, Unnamed: 3, Unnamed: 4, Unnamed: 5 … | Municipio: 20/252 | 398 nulos en 15 cols (Municipio:174, Distrito:172, Sección:4); outliers>3σ: 11 en 9 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_municipal.csv` | CSV | 26.5 KB | 253×15 | territorio, municipio, distrito, renta_media_eur_m2_media, renta_media_eur_m2_mediana, renta… | municipio: 159/252 (sin codigo_ine) | Sin nulos; outliers>3σ: 44 en 13 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_municipal.json` | JSON | 177.0 KB | 253×18 | territorio, municipio, distrito, renta_media_eur_m2_media, renta_media_eur_m2_mediana, renta… | municipio: 159/252; nombre_canonico_resuelto: 159/252 | Sin nulos; outliers>3σ: 38 en 12 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_municipio_original.csv` | CSV (multi-cab.) | 22.1 KB | 265×14 | Municipio, Distrito, Unnamed: 2, Unnamed: 3, Unnamed: 4, Unnamed: 5 … | Municipio: 159/252 | 256 nulos en 14 cols (Municipio:100, Distrito:12, Unnamed: 2:12); outliers>3σ: 29 en 9 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_seccion.csv` | CSV | 161.0 KB | 1569×19 | territorio, municipio, codigo_ine, nombre_canonico, distrito, seccion … | municipio: 159/252; codigo_ine: 159/252 | 1569 nulos en 1 cols (territorio:1569); outliers>3σ: 193 en 14 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_seccion_a_original.csv` | CSV (multi-cab.) | 72.5 KB | 860×15 | Municipio, Distrito, Sección, Unnamed: 3, Unnamed: 4, Unnamed: 5 … | Municipio: 74/252 | 1564 nulos en 15 cols (Municipio:783, Distrito:729, Sección:4); outliers>3σ: 79 en 10 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_seccion_b_original.csv` | CSV (multi-cab.) | 44.5 KB | 524×15 | Municipio, Distrito, Sección, Unnamed: 3, Unnamed: 4, Unnamed: 5 … | Municipio: 65/252 | 935 nulos en 15 cols (Municipio:456, Distrito:427, Sección:4); outliers>3σ: 42 en 10 cols | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |
| `data/raw/alquiler_territorial_original.csv` | CSV (multi-cab.) | 19.8 KB | 264×13 | Unnamed: 0, Renta media (euros/m2 mes), Unnamed: 2, Unnamed: 3, Unnamed: 4, Cuantía media ar… | — | 87 nulos en 13 cols (Renta media (euros/m2 mes):7, Unnamed: 2:7, Unnamed: 3:7); sin outliers>3σ | ¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)? |

### 2.5 Alquiler oficial (EMAL fianzas)

_Archivos: 5_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/emal_barrios_municipios_2016_2025.xlsx` | XLSX | 251.1 KB | 56×5 | Tabla ancha multi-cabecera | — | 208 nulos en 5 cols (Unnamed: 3:56, Unnamed: 4:55, Unnamed: 0:48); sin outliers>3σ | ¿Cuántas fianzas de alquiler se registran (proxy de rotación/mercado)? |
| `data/raw/emal_fianzas.csv` | CSV | 48.8 KB | 730×9 | codigo_ine, municipio, anio, fianzas, renta_media_eur_mes, renta_media_eur_m2_mes … | codigo_ine: 73/252; municipio: 67/252 | 62 nulos en 5 cols (renta_media_eur_mes:20, renta_media_eur_m2_mes:20, alquileres_vigentes_2024:10); outliers>3σ: 99 en 5 cols | ¿Cuántas fianzas de alquiler se registran (proxy de rotación/mercado)? |
| `data/raw/emal_fianzas.json` | JSON | 229.0 KB | 730×9 | codigo_ine, municipio, anio, fianzas, renta_media_eur_mes, renta_media_eur_m2_mes … | codigo_ine: 69/252; municipio: 67/252 | 62 nulos en 5 cols (renta_media_eur_mes:20, renta_media_eur_m2_mes:20, alquileres_vigentes_2024:10); outliers>3σ: 99 en 5 cols | ¿Cuántas fianzas de alquiler se registran (proxy de rotación/mercado)? |
| `data/raw/emal_fianzas_ampliado.csv` | CSV | 131.2 KB | 730×13 | codigo_ine, municipio, anio, fianzas, renta_media_eur_mes, renta_media_eur_m2_mes … | codigo_ine: 73/252; municipio: 67/252 | 64 nulos en 6 cols (renta_media_eur_mes:20, renta_media_eur_m2_mes:20, alquileres_vigentes_2024:10); outliers>3σ: 128 en 6 cols | ¿Cuántas fianzas de alquiler se registran (proxy de rotación/mercado)? |
| `data/raw/emal_fianzas_ampliado.json` | JSON | 389.4 KB | 730×13 | codigo_ine, municipio, anio, fianzas, renta_media_eur_mes, renta_media_eur_m2_mes … | codigo_ine: 69/252; municipio: 67/252 | 64 nulos en 6 cols (renta_media_eur_mes:20, renta_media_eur_m2_mes:20, alquileres_vigentes_2024:10); outliers>3σ: 29 en 1 cols | ¿Cuántas fianzas de alquiler se registran (proxy de rotación/mercado)? |

### 2.6 Alquiler oficial (transformaciones)

_Archivos: 4_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/procesado/alquiler_municipal_completo.csv` | CSV | 29.2 KB | 252×19 | codigo_ine, territorio, municipio, distrito, nivel_geografico, renta_media_eur_m2_media … | codigo_ine: 252/252; municipio: 252/252 | 186 nulos en 2 cols (nombre_canonico:93, anio_fuente:93); outliers>3σ: 18 en 12 cols | ¿Cómo se completa el alquiler a los 93 municipios sin dato (comarca)? |
| `data/procesado/alquiler_rescatado_seccion.csv` | CSV | 54 B | 0×4 | codigo_ine, nombre_canonico, n_secciones, mediana_m2 | — | Sin nulos; sin outliers>3σ | ¿Cómo se completa el alquiler a los 93 municipios sin dato (comarca)? |
| `data/procesado/alquiler_seccion_resumen.csv` | CSV | 5.0 KB | 159×6 | codigo_ine, municipio, n_secciones, renta_mediana_min, renta_mediana_max, rango_intra_municipal | codigo_ine: 159/252; municipio: 159/252 | Sin nulos; outliers>3σ: 8 en 4 cols | ¿Cómo se completa el alquiler a los 93 municipios sin dato (comarca)? |
| `data/procesado/r1_sin_alquiler.json` | JSON | 1.6 KB | 93×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |

### 2.7 Complementarios (Eustat: población, renta, PIB, tenencia)

_Archivos: 10_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/eustat_pib_municipal.csv` | CSV | 926.9 KB | 13248×6 | ámbitos territoriales, ámbitos territoriales__etiqueta, tipo de medida, tipo de medida__etiq… | ámbitos territoriales: 252/252; ámbitos territoriales__etiqueta: 252/252 | Sin nulos; sin outliers>3σ | ¿Cuál es el PIB municipal (proxy de actividad)? |
| `data/raw/eustat_pib_municipal.json` | JSON | 4.2 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Cuál es el PIB municipal (proxy de actividad)? |
| `data/raw/eustat_poblacion_edad.csv` | CSV | 5.3 MB | 89424×9 | ámbitos territoriales, ámbitos territoriales__etiqueta, grandes grupos de edad cumplida, gra… | ámbitos territoriales: 252/252; ámbitos territoriales__etiqueta: 252/252 | Sin nulos; sin outliers>3σ | ¿Cuántos habitantes/jóvenes hay por municipio? |
| `data/raw/eustat_poblacion_edad.json` | JSON | 36.2 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Cuántos habitantes/jóvenes hay por municipio? |
| `data/raw/eustat_renta_edad.csv` | CSV | 390.1 KB | 6426×8 | sexo, sexo__etiqueta, tipo de renta, tipo de renta__etiqueta, edad, edad__etiqueta … | — | Sin nulos; outliers>3σ: 25 en 1 cols | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/eustat_renta_edad.json` | JSON | 2.1 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/eustat_renta_municipal.csv` | CSV | 5.8 MB | 98532×8 | ámbitos territoriales, ámbitos territoriales__etiqueta, tipo de renta, tipo de renta__etique… | ámbitos territoriales: 252/252; ámbitos territoriales__etiqueta: 252/252 | Sin nulos; sin outliers>3σ | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/eustat_renta_municipal.json` | JSON | 35.0 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/eustat_tenencia.csv` | CSV | 180.0 KB | 4416×6 | ámbitos territoriales, ámbitos territoriales__etiqueta, régimen de tenencia, régimen de tene… | ámbitos territoriales: 252/252; ámbitos territoriales__etiqueta: 252/252 | Sin nulos; sin outliers>3σ | ¿Qué peso tiene el alquiler vs propiedad por municipio? |
| `data/raw/eustat_tenencia.json` | JSON | 1.3 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Qué peso tiene el alquiler vs propiedad por municipio? |

### 2.8 Complementarios (ECVI compraventa)

_Archivos: 68_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/ECVI_cifras_interanuales_es_2025T4.xlsx` | XLSX | 396.2 KB | 90×3 | Tabla ancha multi-cabecera | Territorial (CAE/TH/comarcas) | 218 nulos en 3 cols (Unnamed: 0:84, Unnamed: 2:71, Unnamed: 1:63); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ECVI_es_2026T2.xlsx` | XLSX | 933.3 KB | 54×5 | Tabla ancha multi-cabecera | Territorial (CAE/TH/comarcas) | 205 nulos en 5 cols (Unnamed: 3:54, Unnamed: 4:53, Unnamed: 0:47); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ECVI_otros_inmuebles_2025T4.xlsx` | XLSX | 272.3 KB | 41×3 | Tabla ancha multi-cabecera | Territorial (CAE/TH/comarcas) | 64 nulos en 3 cols (Unnamed: 0:34, Unnamed: 2:20, Unnamed: 1:10); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_ndice.csv` | CSV | 2.5 KB | 90×3 | Tabla ancha multi-cabecera | Territorial (CAE/TH/comarcas) | 218 nulos en 3 cols (Unnamed: 0:84, Unnamed: 2:71, Unnamed: 1:63); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t1_1.csv` | CSV | 6.1 KB | 100×13 | T1.1 Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de… | Territorial (CAE/TH/comarcas) | 274 nulos en 13 cols (Unnamed: 2:23, Unnamed: 3:23, Unnamed: 5:23); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t1_2.csv` | CSV | 6.3 KB | 99×13 | T1.2 Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre… | Territorial (CAE/TH/comarcas) | 262 nulos en 13 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 5:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t1_3.csv` | CSV | 8.4 KB | 99×13 | T1.3. Precio medio por metro cuadrado construido de las transacciones de compraventa de vivi… | Territorial (CAE/TH/comarcas) | 262 nulos en 13 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 5:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t2.csv` | CSV | 5.7 KB | 99×10 | T2 Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de i… | Territorial (CAE/TH/comarcas) | 197 nulos en 10 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 5:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t3_1.csv` | CSV | 17.6 KB | 85×63 | Tabla 3.1 Número de transacciones de compraventa de vivienda (libre y protegida) por trimest… | Territorial (CAE/TH/comarcas) | 1211 nulos en 63 cols (Unnamed: 2:20, Unnamed: 4:20, Unnamed: 6:20); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t3_2.csv` | CSV | 11.6 KB | 84×32 | Tabla 3.2 Precio medio total de las transacciones de compraventa de vivienda libre, por trim… | Territorial (CAE/TH/comarcas) | 591 nulos en 32 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t3_2_1.csv` | CSV | 11.0 KB | 84×32 | Tabla 3.2.1 Precio medio total de las transacciones de compraventa de vivienda usada libre, … | Territorial (CAE/TH/comarcas) | 591 nulos en 32 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t3_3.csv` | CSV | 12.6 KB | 84×32 | Tabla 3.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de … | Territorial (CAE/TH/comarcas) | 591 nulos en 32 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t3_3_1.csv` | CSV | 12.0 KB | 84×32 | Tabla 3.3.1 Precio medio por metro cuadrado construido de las transacciones de compraventa d… | Territorial (CAE/TH/comarcas) | 591 nulos en 32 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t4_1.csv` | CSV | 22.1 KB | 85×93 | Tabla 4.1 Número de transacciones de compraventa de vivienda (libre y protegida) por trimest… | Territorial (CAE/TH/comarcas) | 1796 nulos en 93 cols (Unnamed: 2:20, Unnamed: 4:20, Unnamed: 6:20); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t4_2.csv` | CSV | 16.4 KB | 84×47 | Tabla 4.2 Precio medio total de las transacciones de compraventa de vivienda libre, por trim… | Territorial (CAE/TH/comarcas) | 876 nulos en 47 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t4_2_1.csv` | CSV | 16.0 KB | 84×47 | Tabla 4.2.1 Precio medio total de las transacciones de compraventa de vivienda usada libre, … | Territorial (CAE/TH/comarcas) | 876 nulos en 47 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t4_3.csv` | CSV | 17.9 KB | 84×47 | Tabla 4.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de … | Territorial (CAE/TH/comarcas) | 876 nulos en 47 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t4_3_1.csv` | CSV | 17.5 KB | 84×47 | Tabla 4.3.1 Precio medio por metro cuadrado construido de las transacciones de compraventa d… | Territorial (CAE/TH/comarcas) | 876 nulos en 47 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t5_1.csv` | CSV | 10.9 KB | 85×37 | Tabla 5.1 Número de transacciones de compraventa de vivienda (libre y protegida) por trimest… | Territorial (CAE/TH/comarcas) | 812 nulos en 37 cols (Unnamed: 26:74, Unnamed: 25:73, Unnamed: 2:20); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t5_2.csv` | CSV | 7.2 KB | 84×19 | Tabla 5.2. Precio medio total de las transacciones de compraventa de vivienda libre, por tri… | Territorial (CAE/TH/comarcas) | 344 nulos en 19 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t5_2_1.csv` | CSV | 6.6 KB | 84×19 | Tabla 5.2.1 Precio medio total de las transacciones de compraventa de vivienda usada libre, … | Territorial (CAE/TH/comarcas) | 344 nulos en 19 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t5_3.csv` | CSV | 7.9 KB | 84×19 | Tabla 5.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de … | Territorial (CAE/TH/comarcas) | 398 nulos en 19 cols (Unnamed: 13:73, Unnamed: 1:19, Unnamed: 2:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_cifras_interanuales_es_2025t4_t5_3_1.csv` | CSV | 7.2 KB | 84×19 | Tabla 5.3.1 Precio medio por metro cuadrado construido de las transacciones de compraventa d… | Territorial (CAE/TH/comarcas) | 344 nulos en 19 cols (Unnamed: 1:19, Unnamed: 2:19, Unnamed: 3:19); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_composici_n_de_zonas_y_distrito.csv` | CSV | 2.8 KB | 107×5 | Vitoria-Gasteiz, Unnamed: 1, Unnamed: 2, Unnamed: 3, Unnamed: 4 | Territorial (CAE/TH/comarcas) | 120 nulos en 5 cols (Unnamed: 4:92, Unnamed: 2:9, Unnamed: 3:9); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_ndice.csv` | CSV | 2.9 KB | 54×5 | Tabla ancha multi-cabecera | Territorial (CAE/TH/comarcas) | 205 nulos en 5 cols (Unnamed: 3:54, Unnamed: 4:53, Unnamed: 0:47); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t1_1.csv` | CSV | 8.9 KB | 66×32 | Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de insc… | Territorial (CAE/TH/comarcas) | 247 nulos en 32 cols (Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de inscripción en el registro según territorio histórico (capitales y resto del territorio histórico) y tipo de vivienda (*):46, Unnamed: 1:7, Unnamed: 6:7); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t1_2.csv` | CSV | 13.1 KB | 65×32 | Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de i… | Territorial (CAE/TH/comarcas) | 216 nulos en 32 cols (Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según territorio histórico (capitales y resto del territorio histórico) y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 6:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t1_3.csv` | CSV | 14.5 KB | 65×32 | Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda l… | Territorial (CAE/TH/comarcas) | 216 nulos en 32 cols (Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según territorio histórico (capitales y resto del territorio histórico) y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 6:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t1_4.csv` | CSV | 13.8 KB | 64×42 | Distribución en porcentaje de las transacciones de compraventa de vivienda por  trimestre de… | Territorial (CAE/TH/comarcas) | 237 nulos en 42 cols (Distribución en porcentaje de las transacciones de compraventa de vivienda por  trimestre de inscripción en el registro y  segun territorio histórico (capitales y resto del territorio histórico) tipo de vivienda (nueva, usada) y nivel de protección (libre, VPO):46, Unnamed: 1:5, Unnamed: 3:5); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t2_1.csv` | CSV | 10.6 KB | 67×47 | Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de insc… | Territorial (CAE/TH/comarcas) | 399 nulos en 47 cols (Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de inscripción en el registro según área funcional y tipo de vivienda (*):46, Unnamed: 1:8, Unnamed: 3:8); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t2_2.csv` | CSV | 14.2 KB | 65×47 | Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de i… | Territorial (CAE/TH/comarcas) | 307 nulos en 47 cols (Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según área funcional y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t2_3.csv` | CSV | 15.4 KB | 65×47 | Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda l… | Territorial (CAE/TH/comarcas) | 307 nulos en 47 cols (Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según área funcional y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t3_1.csv` | CSV | 5.3 KB | 67×23 | Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de insc… | Territorial (CAE/TH/comarcas) | 215 nulos en 23 cols (Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de inscripción en el registro según municipio >40.000 habitantes y tipo de vivienda (*):46, Unnamed: 1:8, Unnamed: 3:8); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t3_2.csv` | CSV | 6.5 KB | 65×23 | Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de i… | Territorial (CAE/TH/comarcas) | 171 nulos en 23 cols (Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según municipio >40.000 habitantes y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t3_3.csv` | CSV | 7.0 KB | 65×23 | Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda l… | Territorial (CAE/TH/comarcas) | 171 nulos en 23 cols (Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según municipio >40.000 habitantes y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t4_1.csv` | CSV | 5.6 KB | 68×24 | Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de insc… | Territorial (CAE/TH/comarcas) | 245 nulos en 24 cols (Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de inscripción en el registro según zonas OFIN de Vitoria-Gasteiz y tipo de vivienda (*):46, Unnamed: 1:9, Unnamed: 3:9); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t4_2.csv` | CSV | 6.7 KB | 65×23 | Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de i… | Territorial (CAE/TH/comarcas) | 171 nulos en 23 cols (Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según zonas OFIN de Vitoria-Gasteiz y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t4_3.csv` | CSV | 7.3 KB | 65×23 | Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda l… | Territorial (CAE/TH/comarcas) | 171 nulos en 23 cols (Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según zonas OFIN de Vitoria-Gasteiz y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t5_1.csv` | CSV | 6.6 KB | 67×30 | Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de insc… | Territorial (CAE/TH/comarcas) | 269 nulos en 30 cols (Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de inscripción en el registro según distritos de Bilbao y tipo de vivienda (*):46, Unnamed: 7:9, Unnamed: 1:8); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t5_2.csv` | CSV | 8.1 KB | 65×29 | Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de i… | Territorial (CAE/TH/comarcas) | 205 nulos en 29 cols (Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según distritos de Bilbao y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t5_3.csv` | CSV | 8.6 KB | 65×29 | Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda l… | Territorial (CAE/TH/comarcas) | 205 nulos en 29 cols (Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según distritos de Bilbao y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t6_1.csv` | CSV | 5.3 KB | 67×24 | Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de insc… | Territorial (CAE/TH/comarcas) | 222 nulos en 24 cols (Número de transacciones de compraventa de vivienda (libre y protegida) por trimestre de inscripción en el registro según zonas OFIN de Donostia / San Sebastián y tipo de vivienda (*):46, Unnamed: 1:8, Unnamed: 3:8); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t6_2.csv` | CSV | 6.4 KB | 65×23 | Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de i… | Territorial (CAE/TH/comarcas) | 171 nulos en 23 cols (Precio medio total de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según zonas OFIN de Donostia / San Sebastián y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t6_3.csv` | CSV | 6.9 KB | 65×23 | Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda l… | Territorial (CAE/TH/comarcas) | 171 nulos en 23 cols (Precio medio por metro cuadrado construido de las transacciones de compraventa de vivienda libre, por trimestre de inscripción en el registro, según zonas OFIN de Donostia / San Sebastián y tipo de vivienda (€):46, Unnamed: 1:6, Unnamed: 3:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t7_2.csv` | CSV | 5.8 KB | 65×12 | Precio medio total de las transacciones de compraventa de vivienda protegida, por trimestre … | Territorial (CAE/TH/comarcas) | 109 nulos en 12 cols (Precio medio total de las transacciones de compraventa de vivienda protegida, por trimestre de inscripción en el registro y según territorio histórico (capitales y resto del territorio histórico):46, Unnamed: 1:6, Unnamed: 2:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_es_2026t2_t7_3.csv` | CSV | 4.6 KB | 65×12 | Precio medio por metro cuadrado de las transacciones de compraventa de vivienda protegida, p… | Territorial (CAE/TH/comarcas) | 109 nulos en 12 cols (Precio medio por metro cuadrado de las transacciones de compraventa de vivienda protegida, por trimestre de inscripción en el registro, según territorio histórico (capitales y resto del territorio histórico):46, Unnamed: 1:6, Unnamed: 2:6); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_ndice.csv` | CSV | 1.9 KB | 41×3 | Tabla ancha multi-cabecera | Territorial (CAE/TH/comarcas) | 64 nulos en 3 cols (Unnamed: 0:34, Unnamed: 2:20, Unnamed: 1:10); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t1_1.csv` | CSV | 4.6 KB | 101×11 | T1.1 Número de transacciones de compraventa de locales por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 240 nulos en 11 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 4:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t1_2.csv` | CSV | 5.6 KB | 116×8 | T1.2 Precio medio total de las transacciones de compraventa de locales, por trimestre de ins… | Territorial (CAE/TH/comarcas) | 189 nulos en 8 cols (Unnamed: 1:27, Unnamed: 3:27, Unnamed: 5:27); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t1_3.csv` | CSV | 6.1 KB | 116×8 | T1.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de local… | Territorial (CAE/TH/comarcas) | 189 nulos en 8 cols (Unnamed: 1:27, Unnamed: 3:27, Unnamed: 5:27); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t2_1.csv` | CSV | 7.0 KB | 86×32 | T2.1 Número de transacciones de compraventa de locales por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 654 nulos en 32 cols (Unnamed: 1:21, Unnamed: 2:21, Unnamed: 3:21); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t2_2.csv` | CSV | 10.0 KB | 86×47 | T2.2 Número de transacciones de compraventa de locales por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 968 nulos en 47 cols (Unnamed: 2:21, Unnamed: 3:21, Unnamed: 4:21); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t2_3.csv` | CSV | 4.5 KB | 86×19 | T2.3 Número de transacciones de compraventa de locales por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 380 nulos en 19 cols (Unnamed: 2:21, Unnamed: 3:21, Unnamed: 4:21); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t3_1.csv` | CSV | 4.0 KB | 101×11 | T3.1 Número de transacciones de compraventa de naves por trimestre de inscripción en el regi… | Territorial (CAE/TH/comarcas) | 240 nulos en 11 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 4:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t3_2.csv` | CSV | 4.2 KB | 101×8 | T3.2 Precio medio total de las transacciones de compraventa de naves, por trimestre de inscr… | Territorial (CAE/TH/comarcas) | 168 nulos en 8 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 5:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t3_3.csv` | CSV | 4.2 KB | 101×8 | T3.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de naves… | Territorial (CAE/TH/comarcas) | 168 nulos en 8 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 5:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t4_1.csv` | CSV | 5.0 KB | 101×11 | T4.1 Número de transacciones de compraventa de garajes por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 240 nulos en 11 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 4:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t4_2.csv` | CSV | 4.4 KB | 101×8 | T4.2 Precio medio total de las transacciones de compraventa de garajes, por trimestre de ins… | Territorial (CAE/TH/comarcas) | 168 nulos en 8 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 5:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t4_3.csv` | CSV | 5.4 KB | 101×8 | T4.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de garaj… | Territorial (CAE/TH/comarcas) | 168 nulos en 8 cols (Unnamed: 1:24, Unnamed: 3:24, Unnamed: 5:24); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t5_1.csv` | CSV | 7.3 KB | 87×32 | T5.1 Número de transacciones de compraventa de garajes por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 685 nulos en 32 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 4:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t5_2.csv` | CSV | 10.3 KB | 87×47 | T5.2 Número de transacciones de compraventa de garajes por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 1015 nulos en 47 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 4:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t5_3.csv` | CSV | 4.8 KB | 87×19 | T5.3 Número de transacciones de compraventa de garajes por trimestre de inscripción en el re… | Territorial (CAE/TH/comarcas) | 399 nulos en 19 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 4:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t6_1.csv` | CSV | 4.5 KB | 102×11 | T6.1 Número de transacciones de compraventa de trasteros por trimestre de inscripción en el … | Territorial (CAE/TH/comarcas) | 251 nulos en 11 cols (Unnamed: 1:25, Unnamed: 3:25, Unnamed: 4:25); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t6_2.csv` | CSV | 4.2 KB | 102×8 | T6.2 Precio medio total de las transacciones de compraventa de trasteros, por trimestre de i… | Territorial (CAE/TH/comarcas) | 176 nulos en 8 cols (Unnamed: 1:25, Unnamed: 3:25, Unnamed: 5:25); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t6_3.csv` | CSV | 5.3 KB | 102×8 | T6.3 Precio medio por metro cuadrado construido de las transacciones de compraventa de trast… | Territorial (CAE/TH/comarcas) | 176 nulos en 8 cols (Unnamed: 1:25, Unnamed: 3:25, Unnamed: 5:25); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t7_1.csv` | CSV | 7.5 KB | 87×44 | T7.1 Número de transacciones de compraventa de trasteros por trimestre de inscripción en el … | Territorial (CAE/TH/comarcas) | 1728 nulos en 44 cols (Unnamed: 32:87, Unnamed: 33:87, Unnamed: 34:87); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t7_2.csv` | CSV | 9.9 KB | 87×47 | T7.2 Número de transacciones de compraventa de trasteros por trimestre de inscripción en el … | Territorial (CAE/TH/comarcas) | 1015 nulos en 47 cols (Unnamed: 2:22, Unnamed: 3:22, Unnamed: 4:22); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |
| `data/raw/ecvi_ecvi_otros_inmuebles_2025t4_t7_3.csv` | CSV | 6.7 KB | 87×45 | T7.3 Número de transacciones de compraventa de trasteros por trimestre de inscripción en el … | Territorial (CAE/TH/comarcas) | 2660 nulos en 45 cols (Unnamed: 19:87, Unnamed: 20:87, Unnamed: 21:87); sin outliers>3σ | ¿Cómo evoluciona el mercado de compraventa (transacciones, precios)? |

### 2.9 Complementarios (emancipación juvenil)

_Archivos: 2_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/emancipacion_juventud.csv` | CSV | 157.1 KB | 866×9 | Indicador, Periodo, Valor, Categoría 1, Categoría 1-Valor, Categoría 2 … | — | 2776 nulos en 4 cols (Categoría 3:866, Categoría 3-Valor:866, Categoría 2:522); outliers>3σ: 21 en 1 cols | ¿Cuál es la tasa de emancipación juvenil y el coste de acceso? |
| `data/raw/emancipacion_juventud_resumen.json` | JSON | 1.5 KB | 1×6 | url, n_filas, anno_min, anno_max, indicadores, fecha_extraccion | — | Sin nulos; sin outliers>3σ | ¿Cuál es la tasa de emancipación juvenil y el coste de acceso? |

### 2.10 Complementarios (Etxebide vivienda social)

_Archivos: 3_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/etxebide_indicador_86.csv` | CSV | 36.6 KB | 285×22 | Indicadores municipales de sostenibilidad: Solicitudes de vivienda que constan en Etxebide (… | Indicadores municipales de sostenibilidad: Solicitudes de vivienda que constan en Etxebide (? habitantes): 201/252 | 135 nulos en 22 cols (Unnamed: 1:11, Unnamed: 3:7, Unnamed: 2:6); sin outliers>3σ | ¿Cuál es la demanda de vivienda social (solicitudes Etxebide)? |
| `data/raw/etxebide_solicitudes.csv` | CSV | 138.1 KB | 5040×4 | codigo_ine, municipio, anio, etxebide_solicitudes_por_mil | codigo_ine: 252/252; municipio: 247/252 | 1 nulos en 1 cols (etxebide_solicitudes_por_mil:1); outliers>3σ: 11 en 1 cols | ¿Cuál es la demanda de vivienda social (solicitudes Etxebide)? |
| `data/raw/etxebide_solicitudes.json` | JSON | 709.3 KB | 5040×4 | codigo_ine, municipio, anio, etxebide_solicitudes_por_mil | municipio: 247/252; codigo_ine: 201/252 | 1 nulos en 1 cols (etxebide_solicitudes_por_mil:1); outliers>3σ: 11 en 1 cols | ¿Cuál es la demanda de vivienda social (solicitudes Etxebide)? |

### 2.11 Complementarios (INE)

_Archivos: 16_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/ine_69301.csv` | CSV | 398.1 KB | 4407×6 | ambito, indicador, segmento, anyo, valor, codigo_serie | — | 952 nulos en 2 cols (anyo:476, valor:476); outliers>3σ: 4 en 1 cols | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69301.json` | JSON | 1.0 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69302.csv` | CSV | 234.1 KB | 2599×6 | ambito, indicador, segmento, anyo, valor, codigo_serie | — | 90 nulos en 2 cols (anyo:45, valor:45); outliers>3σ: 3 en 1 cols | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69302.json` | JSON | 622.8 KB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69303.csv` | CSV | 79.8 KB | 904×6 | ambito, indicador, segmento, anyo, valor, codigo_serie | — | Sin nulos; outliers>3σ: 6 en 1 cols | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69303.json` | JSON | 215.0 KB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69323.csv` | CSV | 175.4 KB | 1863×6 | ambito, indicador, segmento, anyo, valor, codigo_serie | — | 804 nulos en 2 cols (anyo:402, valor:402); outliers>3σ: 48 en 2 cols | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69323.json` | JSON | 457.0 KB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69330.csv` | CSV | 900.9 KB | 9999×6 | ambito, indicador, segmento, anyo, valor, codigo_serie | — | 602 nulos en 2 cols (anyo:301, valor:301); outliers>3σ: 11 en 1 cols | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_69330.json` | JSON | 2.3 MB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis? |
| `data/raw/ine_atlas_renta.csv` | CSV | 10.0 KB | 252×5 | codigo_ine, nombre_canonico, renta_atlas, anio_renta, renta_origen | codigo_ine: 252/252; nombre_canonico: 252/252 | Sin nulos; outliers>3σ: 4 en 1 cols | ¿Renta municipal para los 51 municipios faltantes (INE Atlas)? |
| `data/raw/ine_atlas_renta.json` | JSON | 44.2 KB | 252×5 | codigo_ine, nombre_canonico, renta_atlas, anio_renta, renta_origen | nombre_canonico: 252/252; codigo_ine: 201/252 | Sin nulos; outliers>3σ: 4 en 1 cols | ¿Renta municipal para los 51 municipios faltantes (INE Atlas)? |
| `data/raw/ine_salarios_decil.csv` | CSV | 1.7 KB | 20×7 | ambito, subambito, indicador, grupo_edad_o_decil, anyo, valor_eur … | — | 2 nulos en 2 cols (anyo:1, valor_eur:1); sin outliers>3σ | ¿Cuál es el salario de referencia (EPA nacional) para calcular esfuerzo? |
| `data/raw/ine_salarios_decil.json` | JSON | 7.5 KB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Cuál es el salario de referencia (EPA nacional) para calcular esfuerzo? |
| `data/raw/ine_salarios_edad.csv` | CSV | 14.1 KB | 198×7 | ambito, subambito, indicador, grupo_edad_o_decil, anyo, valor_eur … | — | 9 nulos en 3 cols (grupo_edad_o_decil:3, anyo:3, valor_eur:3); outliers>3σ: 8 en 2 cols | ¿Cuál es el salario de referencia (EPA nacional) para calcular esfuerzo? |
| `data/raw/ine_salarios_edad.json` | JSON | 74.7 KB | 1×2 | metadata, datos | — | Sin nulos; sin outliers>3σ | ¿Cuál es el salario de referencia (EPA nacional) para calcular esfuerzo? |

### 2.12 Complementarios (SERPAVI renta fiscal)

_Archivos: 3_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/serpavi_renta_municipal.csv` | CSV | 14.4 KB | 249×9 | codigo_ine, municipio, provincia_codigo, renta_m2_mes_eur, anio_renta, n_declaraciones … | codigo_ine: 249/252; municipio: 248/252 | 445 nulos en 5 cols (renta_m2_mes_eur:89, anio_renta:89, n_declaraciones:89); outliers>3σ: 7 en 5 cols | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/serpavi_renta_municipal.json` | JSON | 73.0 KB | 249×9 | codigo_ine, municipio, provincia_codigo, renta_m2_mes_eur, anio_renta, n_declaraciones … | municipio: 248/252; codigo_ine: 199/252 | 445 nulos en 5 cols (renta_m2_mes_eur:89, anio_renta:89, n_declaraciones:89); outliers>3σ: 7 en 5 cols | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/serpavi_renta_municipal.xlsx` | XLSX | 67.9 MB | 40×3 | Sistema Estatal Índices Alquiler de Vivienda, Unnamed: 1, Unnamed: 2 | — | 12 nulos en 2 cols (Unnamed: 1:6, Unnamed: 2:6); sin outliers>3σ | ¿Cuál es la renta media municipal (proxy de ingresos)? |

### 2.13 Complementarios (renta municipal derivada)

_Archivos: 3_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/renta_municipal_completa.csv` | CSV | 51.0 KB | 252×9 | codigo_ine, nombre_canonico, renta_atlas, anio_renta, renta_origen, renta_eustat … | codigo_ine: 252/252; nombre_canonico: 252/252 | Sin nulos; outliers>3σ: 17 en 4 cols | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/renta_municipal_completa.json` | JSON | 51.0 KB | 252×6 | codigo_ine, nombre_canonico, renta_atlas, anio_renta, renta_origen, renta_eustat | nombre_canonico: 252/252; codigo_ine: 201/252 | Sin nulos; outliers>3σ: 9 en 2 cols | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/renta_municipal_referencia.csv` | CSV | 49.0 KB | 252×8 | codigo_ine, nombre_canonico, renta_hogar_atlas_eur, renta_personal_eustat_eur, renta_joven_e… | codigo_ine: 252/252; nombre_canonico: 252/252 | Sin nulos; outliers>3σ: 13 en 3 cols | ¿Cuál es la renta media municipal (proxy de ingresos)? |

### 2.14 Complementarios (servicios)

_Archivos: 4_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/educacion_centros.csv` | CSV | 272.1 KB | 1309×20 | codigo_ine, nombre_centro, nombre_centro_eu, tipo_centro, tipo_centro_eu, genero … | codigo_ine: 197/252; municipio_nombre: 196/252 | 1335 nulos en 7 cols (web:1049, fax:277, tipo_centro:2); outliers>3σ: 128 en 4 cols | ¿Qué servicios (centros educativos/sanitarios) contextualizan la habitabilidad? |
| `data/raw/educacion_centros.json` | JSON | 915.1 KB | 1309×20 | codigo_ine, nombre_centro, nombre_centro_eu, tipo_centro, tipo_centro_eu, genero … | municipio_nombre: 196/252; codigo_ine: 166/252 | Sin nulos; sin outliers>3σ | ¿Qué servicios (centros educativos/sanitarios) contextualizan la habitabilidad? |
| `data/raw/salud_centros.csv` | CSV | 111.6 KB | 528×12 | codigo_ine, nombre_centro, tipo_centro, alias, osi, latitud … | codigo_ine: 231/252; municipio_nombre: 230/252 | 7 nulos en 1 cols (osi:7); outliers>3σ: 1 en 1 cols | ¿Qué servicios (centros educativos/sanitarios) contextualizan la habitabilidad? |
| `data/raw/salud_centros.json` | JSON | 262.5 KB | 528×12 | codigo_ine, nombre_centro, tipo_centro, alias, osi, latitud … | municipio_nombre: 230/252; codigo_ine: 185/252 | Sin nulos; sin outliers>3σ | ¿Qué servicios (centros educativos/sanitarios) contextualizan la habitabilidad? |

### 2.15 Complementarios (transformaciones)

_Archivos: 1_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/procesado/emancipacion_tier3_93.csv` | CSV | 13.6 KB | 93×15 | codigo_ine, nombre_canonico, paro_lanbide, osrm_min, n_paradas, tiene_educacion … | codigo_ine: 93/252; nombre_canonico: 93/252 | 93 nulos en 1 cols (alquiler_eur_m2:93); outliers>3σ: 6 en 5 cols | ¿Cuál es la tasa de emancipación juvenil y el coste de acceso? |

### 2.16 Empleo (Lanbide)

_Archivos: 5_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/lanbide_paro_historico.xlsx` | XLSX | 25.7 MB | 11960×23 | Matriz de datos históricos de demandantes activos parados, Unnamed: 1, Unnamed: 2, Unnamed: … | — | 22 nulos en 22 cols (Unnamed: 1:1, Unnamed: 2:1, Unnamed: 3:1); sin outliers>3σ | ¿Cuál es el paro juvenil municipal (Lanbide)? |
| `data/raw/lanbide_paro_historico_joven.csv` | CSV | 2.0 MB | 29275×18 | anio, trimestre, codigo_ine, municipio, poblacion, poblacion_activa … | codigo_ine: 252/252; municipio: 250/252 | 255 nulos en 2 cols (municipio:251, tasa_paro_joven_ratio_pct:4); outliers>3σ: 4965 en 14 cols | ¿Cuál es el paro juvenil municipal (Lanbide)? |
| `data/raw/lanbide_paro_historico_joven.json` | JSON | 16.4 MB | 29275×18 | anio, trimestre, codigo_ine, municipio, poblacion, poblacion_activa … | municipio: 250/252; codigo_ine: 201/252 | 255 nulos en 2 cols (municipio:251, tasa_paro_joven_ratio_pct:4); outliers>3σ: 4965 en 14 cols | ¿Cuál es el paro juvenil municipal (Lanbide)? |
| `data/raw/lanbide_paro_juvenil.csv` | CSV | 13.3 KB | 252×12 | codigo_ine, municipio, anio, trimestre, paro_total, paro_joven_menores_25 … | codigo_ine: 252/252; municipio: 250/252 | Sin nulos; outliers>3σ: 26 en 8 cols | ¿Cuál es el paro juvenil municipal (Lanbide)? |
| `data/raw/lanbide_paro_juvenil.json` | JSON | 87.9 KB | 252×12 | codigo_ine, municipio, anio, trimestre, paro_total, paro_joven_menores_25 … | municipio: 250/252; codigo_ine: 201/252 | Sin nulos; outliers>3σ: 26 en 8 cols | ¿Cuál es el paro juvenil municipal (Lanbide)? |

### 2.17 Empleo (Udalmap)

_Archivos: 6_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/udalmap_empleo.csv` | CSV | 35.6 KB | 252×24 | codigo_ine, nombre_canonico, territorio, tasa_actividad_pct, tasa_ocupacion_pct, tasa_paro_a… | codigo_ine: 252/252; nombre_canonico: 252/252 | 252 nulos en 1 cols (tasa_paro_aprox_pct:252); outliers>3σ: 62 en 18 cols | ¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio? |
| `data/raw/udalmap_empleo.json` | JSON | 232.7 KB | 252×24 | codigo_ine, nombre_canonico, territorio, tasa_actividad_pct, tasa_ocupacion_pct, tasa_paro_a… | nombre_canonico: 252/252; codigo_ine: 201/252 | 252 nulos en 1 cols (tasa_paro_aprox_pct:252); outliers>3σ: 62 en 18 cols | ¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio? |
| `data/raw/udalmap_empleo_corregido.csv` | CSV | 87.6 KB | 252×27 | codigo_ine, nombre_canonico, territorio, tasa_actividad_pct, tasa_ocupacion_pct, tasa_paro_a… | codigo_ine: 252/252; nombre_canonico: 252/252 | 252 nulos en 1 cols (tasa_paro_aprox_pct:252); outliers>3σ: 64 en 19 cols | ¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio? |
| `data/raw/udalmap_empleo_corregido.json` | JSON | 310.0 KB | 252×27 | codigo_ine, nombre_canonico, territorio, tasa_actividad_pct, tasa_ocupacion_pct, tasa_paro_a… | nombre_canonico: 252/252; codigo_ine: 201/252 | 252 nulos en 1 cols (tasa_paro_aprox_pct:252); outliers>3σ: 64 en 19 cols | ¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio? |
| `data/raw/udalmap_indicadores_adicionales.csv` | CSV | 52.8 KB | 252×34 | codigo_ine, nombre_canonico, territorio, viviendas_desocupadas_pct, viviendas_mas_50_anios_p… | codigo_ine: 252/252; nombre_canonico: 252/252 | Sin nulos; outliers>3σ: 109 en 27 cols | ¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio? |
| `data/raw/udalmap_indicadores_adicionales.json` | JSON | 363.6 KB | 252×34 | codigo_ine, nombre_canonico, territorio, viviendas_desocupadas_pct, viviendas_mas_50_anios_p… | nombre_canonico: 252/252; codigo_ine: 201/252 | Sin nulos; outliers>3σ: 109 en 27 cols | ¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio? |

### 2.19 Geografía (municipios/cartografía)

_Archivos: 3_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/dim_municipios.csv` | CSV | 22.0 KB | 252×9 | codigo_ine, nombre_canonico, territorio, nombre_normalizado, variantes, n_anuncios … | codigo_ine: 252/252; nombre_canonico: 252/252 | Sin nulos; outliers>3σ: 2 en 1 cols | ¿Dónde están los municipios y cómo se identifican (dimensión)? |
| `data/raw/dim_municipios.json` | JSON | 91.6 KB | 252×9 | codigo_ine, nombre_canonico, territorio, nombre_normalizado, variantes, n_anuncios … | nombre_canonico: 252/252; nombre_normalizado: 252/252 | Sin nulos; outliers>3σ: 2 en 1 cols | ¿Dónde están los municipios y cómo se identifican (dimensión)? |
| `data/raw/municipios_euskadi.geojson` | GeoJSON | 10.5 MB | 252 features | — | — | Sin nulos; sin outliers>3σ | ¿Dónde están los municipios y cómo se identifican (dimensión)? |

### 2.20 Geografía (distancias)

_Archivos: 4_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/distancias_capitales.csv` | CSV | 24.0 KB | 259×11 | codigo_ine, nombre, territorio, comarca, centroide_lat, centroide_lon … | codigo_ine: 252/252; nombre: 230/252 | Sin nulos; outliers>3σ: 4 en 1 cols | ¿Qué distancias hay entre municipios/capitales? |
| `data/raw/distancias_capitales_252.csv` | CSV | 24.3 KB | 252×12 | codigo_ine, nombre, territorio, comarca, centroide_lat, centroide_lon … | codigo_ine: 252/252; nombre: 229/252 | Sin nulos; outliers>3σ: 4 en 1 cols | ¿Qué distancias hay entre municipios/capitales? |
| `data/raw/distancias_haversine_252.csv` | CSV | 1.1 MB | 63504×3 | origen_codigo, destino_codigo, km_haversine | — | Sin nulos; outliers>3σ: 20 en 1 cols | ¿Qué distancias hay entre municipios/capitales? |
| `data/raw/distancias_municipios.json` | JSON | 4.4 MB | 63504×3 | origen_codigo, destino_codigo, km_haversine | — | Sin nulos; outliers>3σ: 20 en 1 cols | ¿Qué distancias hay entre municipios/capitales? |

### 2.21 Geografía y accesibilidad (OSRM)

_Archivos: 2_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/osrm_tiempos_capitales.csv` | CSV | 5.5 KB | 252×4 | codigo_ine, minutos_Vitoria-Gasteiz, minutos_Bilbao, minutos_Donostia-San Sebastian | codigo_ine: 252/252 | Sin nulos; outliers>3σ: 1 en 1 cols | ¿Cuántos minutos de conducción a las capitales? |
| `data/raw/osrm_tiempos_capitales.json` | JSON | 40.2 KB | 252×4 | codigo_ine, minutos_Vitoria-Gasteiz, minutos_Bilbao, minutos_Donostia-San Sebastian | codigo_ine: 201/252 | Sin nulos; outliers>3σ: 1 en 1 cols | ¿Cuántos minutos de conducción a las capitales? |

### 2.22 Geografía y transporte

_Archivos: 2_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/transporte_paradas_municipio.csv` | CSV | 14.1 KB | 252×6 | codigo_ine, municipio, territorio, n_paradas, n_operadores, operadores | codigo_ine: 252/252; municipio: 229/252 | 70 nulos en 1 cols (operadores:70); outliers>3σ: 5 en 2 cols | ¿Qué oferta de transporte público hay por municipio? |
| `data/raw/transporte_paradas_municipio.json` | JSON | 53.2 KB | 252×6 | codigo_ine, municipio, territorio, n_paradas, n_operadores, operadores | municipio: 229/252; codigo_ine: 201/252 | Sin nulos; outliers>3σ: 5 en 2 cols | ¿Qué oferta de transporte público hay por municipio? |

### 2.23 Geografía (shapefile Euskadi)

_Archivos: 5_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/shp_euskadi/MUNICIPIOS_5000_ETRS89.cpg` | CPG | 5 B | — | — | — | — | Cartografía municipal (límites, EPSG:25830). |
| `data/raw/shp_euskadi/MUNICIPIOS_5000_ETRS89.dbf` | DBF | 158.5 KB | — | — | — | — | Cartografía municipal (límites, EPSG:25830). |
| `data/raw/shp_euskadi/MUNICIPIOS_5000_ETRS89.prj` | PRJ | 404 B | — | — | — | — | Cartografía municipal (límites, EPSG:25830). |
| `data/raw/shp_euskadi/MUNICIPIOS_5000_ETRS89.shp` | SHP | 7.2 MB | — | — | — | — | Cartografía municipal (límites, EPSG:25830). |
| `data/raw/shp_euskadi/MUNICIPIOS_5000_ETRS89.shx` | SHX | 2.1 KB | — | — | — | — | Cartografía municipal (límites, EPSG:25830). |

### 2.24 Geografía (transformaciones)

_Archivos: 2_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/procesado/municipios_faltantes_93.csv` | CSV | 5.6 KB | 93×5 | codigo_ine, nombre_canonico, territorio, poblacion, tipologia_mercado | codigo_ine: 93/252; nombre_canonico: 93/252 | Sin nulos; outliers>3σ: 1 en 1 cols | ¿Qué 93 municipios no tienen alquiler directo? |
| `data/procesado/r1_municipios_objetivo.json` | JSON | 4.0 KB | 251×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |

### 2.25 Transformaciones y control (pipeline)

_Archivos: 16_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/procesado/.gitkeep` | (sin ext) | 0 B | — | — | — | — | Marcador de directorio (sin datos). |
| `data/procesado/analisis_variables_base.csv` | CSV | 61.9 KB | 252×33 | codigo_ine, nombre_canonico, territorio, tipologia_mercado, n_anuncios, tiene_alquiler_ofici… | codigo_ine: 252/252; nombre_canonico: 252/252 | 651 nulos en 7 cols (renta_media_eur_m2_media:93, cuantia_media_eur_mes_media:93, superficie_media_m2_media:93); outliers>3σ: 57 en 19 cols | Control, rescate y calidad del pipeline de datos. |
| `data/procesado/f4_fotocasa.log` | Log | 19.7 KB | — | — | — | — | Log de ejecución del pipeline. |
| `data/procesado/f4_pisos_informe.csv` | CSV | 3.7 KB | 93×3 | codigo_ine, municipio, estado | codigo_ine: 93/252; municipio: 93/252 | Sin nulos; sin outliers>3σ | ¿Scraping dirigido a municipios con n anuncios bajo (Fase 4)? |
| `data/procesado/f4_pisos_objetivo.json` | JSON | 443 B | 40×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Scraping dirigido a municipios con n anuncios bajo (Fase 4)? |
| `data/procesado/f4_pisos_objetivo.json.bak_r1` | Backup JSON | 443 B | — | — | — | — | ¿Scraping dirigido a municipios con n anuncios bajo (Fase 4)? |
| `data/procesado/informe_calidad_f5.csv` | CSV | 414 B | 4×8 | fuente, n, mediana_eur_m2, q1, q3, corte_sup … | — | Sin nulos; sin outliers>3σ | ¿Informe de calidad/consistencia de datos? |
| `data/procesado/informe_entity_resolution.csv` | CSV | 327 B | 8×5 | fichero, total, con_codigo, sin_codigo, no_resueltos | — | 8 nulos en 1 cols (no_resueltos:8); sin outliers>3σ | ¿Informe de calidad/consistencia de datos? |
| `data/procesado/pob_rank.csv` | CSV | 1.9 KB | 275×1 | cod | — | Sin nulos; sin outliers>3σ | Control, rescate y calidad del pipeline de datos. |
| `data/procesado/r1_batch_1.json` | JSON | 411 B | 30×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |
| `data/procesado/r1_batch_2.json` | JSON | 411 B | 30×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |
| `data/procesado/r1_batch_3.json` | JSON | 473 B | 30×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |
| `data/procesado/r1_batch_4.json` | JSON | 41 B | 3×1 | Lista de strings (1 col) | — | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |
| `data/procesado/r1_fotocasa_informe.csv` | CSV | 2.6 KB | 93×2 | municipio, estado | municipio: 93/252 | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |
| `data/procesado/r1_pisos_informe.csv` | CSV | 2.6 KB | 93×2 | municipio, estado | municipio: 93/252 | Sin nulos; sin outliers>3σ | ¿Rescate de alquiler municipal por comarca (R1)? |
| `data/procesado/v1_detalle.log` | Log | 596 B | — | — | — | — | Log de ejecución del pipeline. |

### 2.26 Metadatos y control

_Archivos: 3_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/.gitkeep` | (sin ext) | 0 B | — | — | — | — | Marcador de directorio (sin datos). |
| `data/raw/manifest_sha256.txt` | TXT | 4.2 KB | — | — | — | — | Manifest SHA-256 de verificación (replay-raw). |
| `data/resultados/.gitkeep` | (sin ext) | 0 B | — | — | — | — | Marcador de directorio (sin datos). |

### 2.27 Legacy / obsoleto (no usar)

_Archivos: 4_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/legacy_obsoleto_no_usar/LEEME.txt` | TXT | 330 B | — | — | — | — | Histórico obsoleto (no usar). |
| `data/raw/legacy_obsoleto_no_usar/distancias_capitales.csv` | CSV | 24.0 KB | 259×11 | codigo_ine, nombre, territorio, comarca, centroide_lat, centroide_lon … | codigo_ine: 252/252; nombre: 230/252 | Sin nulos; outliers>3σ: 4 en 1 cols | Histórico obsoleto (no usar). |
| `data/raw/legacy_obsoleto_no_usar/eustat_renta_municipal.csv` | CSV | 5.8 MB | 98532×8 | ámbitos territoriales, ámbitos territoriales__etiqueta, tipo de renta, tipo de renta__etique… | ámbitos territoriales: 252/252; ámbitos territoriales__etiqueta: 252/252 | Sin nulos; sin outliers>3σ | ¿Cuál es la renta media municipal (proxy de ingresos)? |
| `data/raw/legacy_obsoleto_no_usar/udalmap_empleo.csv` | CSV | 35.6 KB | 252×24 | codigo_ine, nombre_canonico, territorio, tasa_actividad_pct, tasa_ocupacion_pct, tasa_paro_a… | codigo_ine: 252/252; nombre_canonico: 252/252 | 252 nulos en 1 cols (tasa_paro_aprox_pct:252); outliers>3σ: 62 en 18 cols | Histórico obsoleto (no usar). |

### 2.29 Geografía y transporte (GTFS)

_Archivos: 13_

| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |
|---|---|---:|---:|---|---|---|---|
| `data/raw/gtfs/bizkaibus.zip` | ZIP | 19.4 MB | — | — | — | — |  |
| `data/raw/gtfs/dbus.zip` | ZIP | 4.2 MB | — | — | — | — |  |
| `data/raw/gtfs/euskotren.zip` | ZIP | 1.2 MB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_ekialdebus.zip` | ZIP | 1.1 MB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_euskotren_bus.zip` | ZIP | 859.6 KB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_goierrialdea.zip` | ZIP | 801.4 KB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_guipuzkoana.zip` | ZIP | 424.9 KB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_pesa.zip` | ZIP | 1.4 MB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_tbh.zip` | ZIP | 761.0 KB | — | — | — | — |  |
| `data/raw/gtfs/lurraldebus_tolosaldea.zip` | ZIP | 339.6 KB | — | — | — | — |  |
| `data/raw/gtfs/metro_bilbao.zip` | ZIP | 944.6 KB | — | — | — | — |  |
| `data/raw/gtfs/renfe_cercanias.zip` | ZIP | 15.8 MB | — | — | — | — |  |
| `data/raw/gtfs/tuvisa.zip` | ZIP | 1011.0 KB | — | — | — | — |  |

## 3. Esquemas destacados (columnas completas de datasets clave)

### `data/raw/dim_municipios.csv`

- Filas: 252 | Columnas: 9 | Nulos totales: 0
- Columnas:
  - `codigo_ine`
  - `nombre_canonico`
  - `territorio`
  - `nombre_normalizado`
  - `variantes`
  - `n_anuncios`
  - `tiene_alquiler_oficial`
  - `tiene_fianzas_emal`
  - `tipologia_mercado`

### `data/raw/alquiler_municipal.csv`

- Filas: 253 | Columnas: 18 | Nulos totales: 0
- Columnas:
  - `territorio`
  - `municipio`
  - `distrito`
  - `renta_media_eur_m2_media`
  - `renta_media_eur_m2_mediana`
  - `renta_media_eur_m2_p25`
  - `renta_media_eur_m2_p75`
  - `cuantia_media_eur_mes_media`
  - `cuantia_media_eur_mes_mediana`
  - `cuantia_media_eur_mes_p25`
  - `cuantia_media_eur_mes_p75`
  - `superficie_media_m2_media`
  - `superficie_media_m2_mediana`
  - `superficie_media_m2_p25`
  - `superficie_media_m2_p75`
  - `codigo_ine`
  - `nombre_canonico`
  - `anio_fuente`

### `data/raw/alquiler_seccion.csv`

- Filas: 1569 | Columnas: 19 | Nulos totales: 1569
- Columnas:
  - `territorio`
  - `municipio`
  - `codigo_ine`
  - `nombre_canonico`
  - `distrito`
  - `seccion`
  - `renta_media_eur_m2_media`
  - `renta_media_eur_m2_mediana`
  - `renta_media_eur_m2_p25`
  - `renta_media_eur_m2_p75`
  - `cuantia_media_eur_mes_media`
  - `cuantia_media_eur_mes_mediana`
  - `cuantia_media_eur_mes_p25`
  - `cuantia_media_eur_mes_p75`
  - `superficie_media_m2_media`
  - `superficie_media_m2_mediana`
  - `superficie_media_m2_p25`
  - `superficie_media_m2_p75`
  - `anio_fuente`

### `data/raw/anuncios_fotocasa.csv`

- Filas: 471 | Columnas: 26 | Nulos totales: 1693
- Columnas:
  - `codigo_ine`
  - `nombre_canonico`
  - `anio_fuente`
  - `id_anuncio`
  - `precio_eur`
  - `municipio`
  - `provincia`
  - `codigo_postal`
  - `barrio`
  - `distrito`
  - `comarca`
  - `latitud`
  - `longitud`
  - `superficie_m2`
  - `habitaciones`
  - `banos`
  - `exterior`
  - `ascensor`
  - `parking`
  - `terraza`
  - `trastero`
  - `alquiler_temporal`
  - `tipo_inmueble`
  - `profesional`
  - `publicado`
  - `url_detalle`

### `data/raw/anuncios_pisos.csv`

- Filas: 235 | Columnas: 19 | Nulos totales: 521
- Columnas:
  - `id_anuncio`
  - `precio_eur`
  - `precio_texto`
  - `titulo`
  - `subtitulo`
  - `tipo_inmueble`
  - `superficie_m2`
  - `habitaciones`
  - `banos`
  - `url_detalle`
  - `municipio_busqueda`
  - `total_resultados`
  - `codigo_ine`
  - `nombre_canonico_resuelto`
  - `anio_fuente`
  - `es_busqueda_no_ubicacion`
  - `ubicacion`
  - `equipamiento`
  - `nombre_canonico`

### `data/raw/anuncios_realtyapi.csv`

- Filas: 139 | Columnas: 17 | Nulos totales: 79
- Columnas:
  - `id_anuncio`
  - `precio_eur`
  - `municipio_busqueda`
  - `municipio`
  - `provincia`
  - `distrito`
  - `barrio`
  - `tipo_inmueble`
  - `superficie_m2`
  - `habitaciones`
  - `banos`
  - `planta`
  - `exterior`
  - `url`
  - `codigo_ine`
  - `nombre_canonico`
  - `anio_fuente`

### `data/raw/eustat_renta_municipal.csv`

- Filas: 98532 | Columnas: 8 | Nulos totales: 0
- Columnas:
  - `ámbitos territoriales`
  - `ámbitos territoriales__etiqueta`
  - `tipo de renta`
  - `tipo de renta__etiqueta`
  - `sexo`
  - `sexo__etiqueta`
  - `periodo`
  - `Renta personal media de la C.A. de Euskadi (euros)`

### `data/raw/eustat_poblacion_edad.csv`

- Filas: 89424 | Columnas: 9 | Nulos totales: 0
- Columnas:
  - `ámbitos territoriales`
  - `ámbitos territoriales__etiqueta`
  - `grandes grupos de edad cumplida`
  - `grandes grupos de edad cumplida__etiqueta`
  - `sexo`
  - `sexo__etiqueta`
  - `periodo`
  - `periodo__etiqueta`
  - `Población de la C.A. de Euskadi`

### `data/raw/eustat_pib_municipal.csv`

- Filas: 13248 | Columnas: 6 | Nulos totales: 0
- Columnas:
  - `ámbitos territoriales`
  - `ámbitos territoriales__etiqueta`
  - `tipo de medida`
  - `tipo de medida__etiqueta`
  - `periodo`
  - `Producto interior bruto (PIB) de la C.A. de Euskadi`

### `data/raw/eustat_tenencia.csv`

- Filas: 4416 | Columnas: 6 | Nulos totales: 0
- Columnas:
  - `ámbitos territoriales`
  - `ámbitos territoriales__etiqueta`
  - `régimen de tenencia`
  - `régimen de tenencia__etiqueta`
  - `periodo`
  - `Viviendas de la C.A. de Euskadi `

### `data/raw/emancipacion_juventud_resumen.json`

- Filas: 1 | Columnas: 6 | Nulos totales: 0
- Columnas:
  - `url`
  - `n_filas`
  - `anno_min`
  - `anno_max`
  - `indicadores`
  - `fecha_extraccion`

### `data/raw/etxebide_solicitudes.csv`

- Filas: 5040 | Columnas: 4 | Nulos totales: 1
- Columnas:
  - `codigo_ine`
  - `municipio`
  - `anio`
  - `etxebide_solicitudes_por_mil`

### `data/raw/udalmap_empleo.csv`

- Filas: 252 | Columnas: 24 | Nulos totales: 252
- Columnas:
  - `codigo_ine`
  - `nombre_canonico`
  - `territorio`
  - `tasa_actividad_pct`
  - `tasa_ocupacion_pct`
  - `tasa_paro_aprox_pct`
  - `tasa_paro_lanbide_pct`
  - `tasa_ocupacion_juvenil_16_24_pct`
  - `etxebide_solicitudes_por_mil`
  - `etxebide_adjudicadas_por_100`
  - `vpo_adjudicadas_por_mil`
  - `vpo_terminadas_por_mil`
  - `licencias_nueva_por_mil`
  - `trabaja_fuera_pct`
  - `afiliacion_ss_16_24_pct`
  - `renta_familiar_eur`
  - `renta_personal_total_eur`
  - `renta_personal_disponible_eur`
  - `renta_trabajo_pct`
  - `superficie_media_m2`
  - `antiguedad_media_anyos`
  - `cert_energetico_por_mil`
  - `suelo_urbanizable_pct`
  - `anio_fuente`

### `data/raw/lanbide_paro_juvenil.csv`

- Filas: 252 | Columnas: 12 | Nulos totales: 0
- Columnas:
  - `codigo_ine`
  - `municipio`
  - `anio`
  - `trimestre`
  - `paro_total`
  - `paro_joven_menores_25`
  - `poblacion`
  - `poblacion_activa`
  - `paro_menores_20`
  - `paro_20_24`
  - `paro_25_29`
  - `tasa_paro_joven_pct`

### `data/raw/osrm_tiempos_capitales.csv`

- Filas: 252 | Columnas: 4 | Nulos totales: 0
- Columnas:
  - `codigo_ine`
  - `minutos_Vitoria-Gasteiz`
  - `minutos_Bilbao`
  - `minutos_Donostia-San Sebastian`

### `data/raw/transporte_paradas_municipio.csv`

- Filas: 252 | Columnas: 6 | Nulos totales: 70
- Columnas:
  - `codigo_ine`
  - `municipio`
  - `territorio`
  - `n_paradas`
  - `n_operadores`
  - `operadores`

### `data/raw/serpavi_renta_municipal.csv`

- Filas: 249 | Columnas: 9 | Nulos totales: 445
- Columnas:
  - `codigo_ine`
  - `municipio`
  - `provincia_codigo`
  - `renta_m2_mes_eur`
  - `anio_renta`
  - `n_declaraciones`
  - `metodo`
  - `renta_m2_p25`
  - `renta_m2_p75`

### `data/raw/educacion_centros.csv`

- Filas: 1309 | Columnas: 20 | Nulos totales: 1335
- Columnas:
  - `codigo_ine`
  - `nombre_centro`
  - `nombre_centro_eu`
  - `tipo_centro`
  - `tipo_centro_eu`
  - `genero`
  - `municipio_codigo`
  - `municipio_nombre`
  - `territorio`
  - `dependencia`
  - `titularidad`
  - `direccion`
  - `codigo_postal`
  - `telefono`
  - `fax`
  - `email`
  - `web`
  - `coord_x_utm30`
  - `coord_y_utm30`
  - `anio_fuente`

### `data/raw/salud_centros.csv`

- Filas: 528 | Columnas: 12 | Nulos totales: 7
- Columnas:
  - `codigo_ine`
  - `nombre_centro`
  - `tipo_centro`
  - `alias`
  - `osi`
  - `latitud`
  - `longitud`
  - `direccion`
  - `municipio_nombre`
  - `codigo_postal`
  - `provincia`
  - `anio_fuente`

### `data/raw/distancias_capitales_252.csv`

- Filas: 252 | Columnas: 12 | Nulos totales: 0
- Columnas:
  - `codigo_ine`
  - `nombre`
  - `territorio`
  - `comarca`
  - `centroide_lat`
  - `centroide_lon`
  - `dist_bilbao_km`
  - `dist_donostia_km`
  - `dist_vitoria_km`
  - `capital_mas_cercana`
  - `dist_centroide_comarca_km`
  - `anio_fuente`

### `data/procesado/alquiler_municipal_completo.csv`

- Filas: 252 | Columnas: 19 | Nulos totales: 186
- Columnas:
  - `codigo_ine`
  - `territorio`
  - `municipio`
  - `distrito`
  - `nivel_geografico`
  - `renta_media_eur_m2_media`
  - `renta_media_eur_m2_mediana`
  - `renta_media_eur_m2_p25`
  - `renta_media_eur_m2_p75`
  - `cuantia_media_eur_mes_media`
  - `cuantia_media_eur_mes_mediana`
  - `cuantia_media_eur_mes_p25`
  - `cuantia_media_eur_mes_p75`
  - `superficie_media_m2_media`
  - `superficie_media_m2_mediana`
  - `superficie_media_m2_p25`
  - `superficie_media_m2_p75`
  - `nombre_canonico`
  - `anio_fuente`

### `data/procesado/analisis_variables_base.csv`

- Filas: 252 | Columnas: 33 | Nulos totales: 651
- Columnas:
  - `codigo_ine`
  - `nombre_canonico`
  - `territorio`
  - `tipologia_mercado`
  - `n_anuncios`
  - `tiene_alquiler_oficial`
  - `renta_eustat`
  - `renta_hogar`
  - `renta_atlas`
  - `renta_joven_estimada_16_29`
  - `tasa_actividad_pct`
  - `tasa_ocupacion_pct`
  - `tasa_paro_lanbide_pct`
  - `tasa_ocupacion_juvenil_16_24_pct`
  - `trabaja_fuera_pct`
  - `afiliacion_ss_16_24_pct`
  - `renta_familiar_eur`
  - `renta_personal_total_eur`
  - `renta_personal_disponible_eur`
  - `superficie_media_m2`
  - `antiguedad_media_anyos`
  - `dist_bilbao_km`
  - `dist_donostia_km`
  - `dist_vitoria_km`
  - `capital_mas_cercana`
  - `dist_centroide_comarca_km`
  - `renta_media_eur_m2_media`
  - `cuantia_media_eur_mes_media`
  - `superficie_media_m2_media`
  - `alquiler_anual`
  - `esfuerzo_renta_hogar`
  - `esfuerzo_renta_eustat`
  - `esfuerzo_renta_joven`

## 4. Notas de uso

- Todos los archivos bajo `data/raw/`, `data/procesado/` y `data/resultados/` son datos generados (ignorados por git).
- `data/resultados/` está vacío salvo `.gitkeep` (fases de análisis/visualización pendientes).
- Los archivos `legacy_obsoleto_no_usar/` no deben usarse (versiones anteriores).
- Para verificación de integridad: `extract/main_ingest.py --mode replay-raw` compara SHA-256 con `data/raw/manifest_sha256.txt`.
