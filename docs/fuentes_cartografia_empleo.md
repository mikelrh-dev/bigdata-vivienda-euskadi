# Fuentes de cartografía y empleo/actividad juvenil (investigación, oct 2026)

Complemento a `config/fuentes.yaml`. Objetivo: completar cobertura geográfica
(Álava + Bizkaia, Euskadi completo) y socioeconómica (empleo/actividad joven).

## 1. Cartografía municipal — Euskadi completo (Álava + Bizkaia + Gipuzkoa)

| Fuente | URL | Formato | Cobertura | Granularidad | Fecha |
|---|---|---|---|---|---|
| Open Data Euskadi — Límites Administrativos del País Vasco | https://www.geo.euskadi.eus/cartografia/DatosDescarga/Limites/MUNICIPIOS_5000_ETRS89.zip | SHP (ETRS89, UTM 30) | CAPV completa (251 municipios: Álava 51 + Bizkaia 112 + Gipuzkoa 88) | Polígono municipal (mapa maestro) | Actualizado 07/05/2025 |
| Open Data Euskadi — mismo, Comarcas | https://www.geo.euskadi.eus/cartografia/DatosDescarga/Limites/COMARCAS_5000_ETRS89.zip | SHP | CAPV | Comarca | 07/05/2025 |
| Open Data Euskadi — Territorios Históricos | https://www.geo.euskadi.eus/cartografia/DatosDescarga/Limites/TERRITORIOS_5000_ETRS89.zip | SHP | CAPV | Territorio histórico (Álava/Bizkaia/Gipuzkoa) | 07/05/2025 |
| Open Data Euskadi — Áreas Funcionales | https://www.geo.euskadi.eus/cartografia/DatosDescarga/Limites/AREAS_FUNCIONALES_5000_ETRS89.zip | SHP | CAPV | Área funcional | 07/05/2025 |
| datos.gob.es — Límites Administrativos del País Vasco | https://datos.gob.es/es/catalogo/a16003011-limites-administrativos-del-pais-vasco1 | SHP | CAPV | Municipios/Comarcas/Áreas/Territorios/CA | — |
| IGN/CNIG — Límites y Unidades Administrativas (España) | https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos | SHP / GML / GPKG | Toda España (incl. Euskadi) | Municipio/Provincia/CCAA | SHP 28/07/2026; GML 10/08/2026 |
| IGN/CNIG — Límites Histórico | https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos | GPKG | España | Municipio | 2023 / 2024 |
| IGN/CNIG — API-Features (WFS) Unidades Administrativas | https://www.ign.es/web/en/ign/portal/rcc-area-rcc (data.europa.eu) | WFS / API | España | Municipio | — |
| Open Data Euskadi — Registro entidades locales | https://opendata.euskadi.eus/catalogo/-/entidades-locales-de-euskadi/ | JSON / GEOJSON | CAPV | Entidad local (municipio, mancomunidad, cuadrilla, concejo) | — |
| Open Data Euskadi — Pueblos de Euskadi | https://opendata.euskadi.eus/contenidos/ds_recursos_turisticos/pueblos_euskadi_turismo/opendata/pueblos.geojson | GEOJSON | CAPV | Pueblo (80,78 KB) | — |
| WMS visualización cartografía base | https://www.geo.euskadi.eus/WMS_KARTOGRAFIA | WMS | CAPV | Visualización (límites, callejero, MDT) | — |
| Eustat — LurData / info territorial | https://www.eustat.eus/municipal/datos_estadisticos/info_territorial.html | Web/GIS | CAPV | Municipio | — |
| Eurostat GISCO — LAU (Local Administrative Units) | https://gisco-services.ec.europa.eu/distribution/v2/lau/download/ | SHP/TopoJSON/GeoJSON/GDB/SVG/parquet | Europa (España incl.) | Municipio (LAU) | Versiones 2011–2024, escala 1:1M |
| Eurostat GISCO — Administrative Units | https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units | Varios | Europa | NUTS/LAU | — |

## 2. Secciones censales (INE)

| Fuente | URL | Formato | Cobertura | Granularidad | Fecha |
|---|---|---|---|---|---|
| INE — Cartografía secciones censales (descarga) | https://www.ine.es/dyngs/DAB/index.htm?cid=1389 | SHP (UTM 30) | Toda España (incl. Euskadi) | Sección censal / distrito | Series desde 2007 hasta actualidad (Censo Electoral y Padrón) |
| INE — GeoServer OGC Features (API) | https://www.ine.es/geoserver/ogc/features/v1/collections | OGC API Features (JSON/GeoJSON) | España | Sección censal / distrito | — |
| INE — Callejero Censo Electoral | https://ine.es/dyngs/DAB/es/index.htm?cid=1390 | ASCII (ZIP) | España | Vía/tramo por sección | — |

## 3. Catastro INSPIRE (parcelas)

| Fuente | URL | Formato | Cobertura | Granularidad | Fecha |
|---|---|---|---|---|---|
| DG Catastro — INSPIRE Parcelas Catastrales (WFS/ATOM) | https://www.catastro.hacienda.gob.es/webinspire/index.html | WFS / GML / ATOM | España **excepto** País Vasco y Navarra | Parcela catastral | Actualizado al invocar |
| DG Catastro — INSPIRE Edificios (BU) | https://ovc.catastro.meh.es/INSPIRE/wfsBU.aspx | WFS (GML 3.2.1) | España excepto PV/Navarra | Edificio | — |
| b5m Gipuzkoa — INSPIRE parcelas (WFS) | https://b5m.gipuzkoa.eus/inspire/wfs/gipuzkoa_wfs_cp | WFS | Gipuzkoa | Parcela catastral | — |
| b5m Gipuzkoa — INSPIRE unidades administrativas (WFS) | https://b5m.gipuzkoa.eus/inspire/wfs/gipuzkoa_wfs_au | WFS | Gipuzkoa | Unidad administrativa | — |
| b5m Gipuzkoa — INSPIRE edificios (WFS) | https://b5m.gipuzkoa.eus/inspire/wfs/gipuzkoa_wfs_bu | WFS | Gipuzkoa | Edificio | — |
| Bizkaia (Diputación Foral) — INSPIRE Parcelas | https://geo.bizkaia.eus/arcgisserverinspire/rest/services/Catastro/Annex1/MapServer/exts/InspireFeatureDownload/service?REQUEST=GetCapabilities&SERVICE=WFS&VERSION=2.0.0 | WFS (GML) | Bizkaia | Parcela catastral | Metadatos: creación 2000-01-01, publicación 2021-01-01 |
| Bizkaia — Metadatos INSPIRE parcelas | https://apli.bizkaia.eus/apps/Danok/INSPIRE/inspireBizkaiaParcelsMetadata.xml | XML (ISO 19115) | Bizkaia | — | — |
| IDEE — Monitorización servicios INSPIRE | https://www.idee.es/monitorizacion-de-servicios | Web | España | Listado de servicios (PV: Gipuzkoa + Bizkaia) | — |
| Nota: Álava no tiene servicio INSPIRE propio listado en IDEE; usar CNIG/IGN o geo.euskadi para límites. Parcelas de Álava: consultar Diputación Foral de Álava (no localizado en esta búsqueda). | — | — | Álava | Parcela | — |

## 4. Datos socioeconómicos — empleo/actividad juvenil por municipio

| Fuente | URL | Formato | Cobertura | Granularidad | Fecha |
|---|---|---|---|---|---|
| INE — Tabla 69303 "Aspectos económicos" (Indicadores Urbanos Ciudades) | https://www.ine.es/jaxiT3/Tabla.htm?t=69303 | CSV/XLSX/JSON (descarga) | 113 municipios seleccionados (incl. Bilbao, Donostia/San Sebastián, Vitoria-Gasteiz) | Municipio; indicadores: tasa de desempleo, tasa de actividad, proporción ocupados 20-64, proporción empleo en servicios/industria, renta neta media | 2010–2025 |
| INE — Tasas de actividad/paro/empleo por CC.AA. y grupos de edad | https://www.ine.es/jaxi/Tabla.htm?path=/t22/e308/pae/px/l0/&file=02007.px | PX/CSV | CC.AA. (incl. PV) | CC.AA. × sexo × edad (16-19, 20-24, 25-54, 55+) | Trimestral (EPA) |
| INE — Tasas de actividad, paro y empleo por CC.AA., sexo y grupos de edad | https://www.ine.es/jaxiT3/Tabla.htm?t=1117 | Web/CSV | CC.AA. | CC.AA. × sexo × edad | — |
| Eustat — Censo de población y viviendas. Actividad (banco de datos) | https://es.eustat.eus/banku/id_050407/indexlistaopera.html | PX/CSV | CAPV (municipal, >40.000 hab. para algunas tablas) | Municipio × relación con actividad × edad × sexo × sector | 2010–2025 (anual) |
| Eustat — Actividad, ocupación y paro (tablas) | https://es.eustat.eus/estadisticas/tema_131/opt_4/tipo_1/temas.html | Web/CSV | CAPV (municipal/provincial/CA) | Municipio/comarca/TH/CA × sexo | 01/01/2025 (publ. 19/08/2026) |
| Eustat — Estadística municipal de actividad | https://www.eustat.eus/document/est_munic_pob_activa_c.aspx | Doc/metadata | CAPV | Municipio | — |
| LANBIDE — Paro registrado por municipio (Euskadi) | https://www.lanbide.euskadi.eus/estadistica/principales-colectivos-de-la-demanda-por-municipio-y-ramas-de-actividad-durante-el-2026/weblan00-estadisticas/es/ | Web/CSV | CAPV | Municipio × rama de actividad × colectivo | Mensual, 2026 |
| LANBIDE — Principales colectivos de la demanda por municipio y ramas | https://www.lanbide.euskadi.eus/estadistica/... | Web | CAPV | Municipio | 2026 |
| Eustat — Emancipación juvenil (ya en uso) | https://www.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv | CSV | CAPV | 16 indicadores, municipal | hasta 2024 |
| Eustat — PIB municipal (ya en uso) | (ver fuentes.yaml) | PX | CAPV | Municipio | — |

## 5. Ofertas de empleo

| Fuente | URL | Formato | Cobertura | Granularidad | Fecha |
|---|---|---|---|---|---|
| Fotocasa — alquiler (ya en uso, anuncios vivienda, no empleo) | https://www.fotocasa.es/es/alquiler/viviendas | Scraping HTML/JSON | Gipuzkoa/Bizkaia/Álava | Anuncio | oct 2026 |
| LANBIDE — ofertas de empleo | https://www.lanbide.euskadi.eus | Web | CAPV | Oferta × municipio | Actual |
| Nota: no se localizó un dataset abierto de ofertas de empleo por municipio en Euskadi con API pública (LANBIDE publica estadísticas de demanda/paro, no ofertas abiertas descargables). Para ofertas abiertas: scraping o API no pública. | — | — | — | — | — |

## 6. Distancias entre municipios

| Fuente | URL | Formato | Cobertura | Granularidad | Fecha |
|---|---|---|---|---|---|
| b5m Gipuzkoa — Distancia entre municipios | https://b5m.gipuzkoa.eus/web5000/es/distancia-entre-municipios | CSV (ZIP) / Web | **Solo Gipuzkoa** (126 municipios) + 4 territorios limítrofes (Álava, Bizkaia, Navarra, Pirineos Atlánticos) | Par de municipios (distancia por carretera, OSRM/OpenStreetMap) | Último cálculo 08/08/2024; 180.488 distancias |
| b5m Gipuzkoa — distancias CSV (descarga) | https://b5m.gipuzkoa.eus/datasets/GFA_DSET_DISTM_CSV.zip | CSV (ZIP) | Solo Gipuzkoa | Par de municipios (km) | 08/08/2024 |

**Conclusión sobre distancias:** NO existe un dataset abierto de distancias entre municipios para Álava ni Bizkaia equivalente al de b5m. Opciones para completar cobertura:
1. Calcular matriz de distancias con OSRM (router de OpenStreetMap) para los 251 municipios de Euskadi (equivalente al método de b5m; reproducible con osrm-backend o API pública).
2. Usar centroides de los polígonos municipales (geo.euskadi SHP) y calcular distancia euclidiana/Haversine como aproximación (menos preciso, sin red viaria).
3. Distancia a capital de TH (indicador Euskadi) para accesibilidad básica.

## 7. Resumen de cobertura y recomendaciones

- **Cartografía municipal Euskadi completo:** usar `MUNICIPIOS_5000_ETRS89.zip` de Open Data Euskadi (SHP, ETRS89 UTM30, 251 municipios, actualizado 07/05/2025). Reemplaza/combina con `municipios_gipuzkoa.geojson` (b5m, solo 126). Convertir SHP→GeoJSON con geopandas/fiona y filtrar por código INE para unificar.
- **Secciones censales:** INE (SHP, toda España) si se necesita granularidad intra-municipal; no necesario para el reto (municipios bastan).
- **Catastro INSPIRE:** DG Catastro cubre España excepto PV/Navarra; para Gipuzkoa b5m WFS; para Bizkaia Diputación Foral WFS; para Álava no localizado (consultar Diputación Foral de Álava). Opcional para el reto.
- **Empleo/actividad juvenil por municipio:** INE 69303 solo 113 ciudades (incluye las 3 capitales vascas) pero no todos los municipios. Eustat "Censo de población y viviendas. Actividad" da datos municipales anuales (2010–2025) con edad y sexo, pero algunas tablas solo para municipios >40.000 hab. LANBIDE da paro registrado por municipio (mensual). Recomendado: combinar Eustat (actividad municipal) + LANBIDE (paro registrado) + INE 69303 (capitales).
- **Distancias:** solo Gipuzkoa (b5m). Para Euskadi completo, calcular con OSRM o aproximar con centroides. No hay fuente abierta equivalente para Álava/Bizkaia.
- **Ofertas de empleo abiertas:** no hay dataset público descargable por municipio; LANBIDE publica estadísticas de demanda. Para ofertas reales: scraping o API no pública.
