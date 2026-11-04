# Fuentes de salario/renta de población joven (18-34)

Investigación de fuentes oficiales/abiertas para complementar el alquiler municipal 2024 (Euskadi).  
Conclusión principal: **no existe salario joven a nivel municipal**. Solo hay renta personal media municipal (sin edad) y salario/renta joven a nivel CA/nacional. Para municipio hay que usar proxies.

## Tabla de fuentes

| Fuente | URL | Cobertura geográfica | Granularidad | Periodicidad | Último dato | Variable útil |
|---|---|---|---|---|---|---|
| Eustat — Renta personal media por edad (PX_173402_crpf_rpf_rp03.px) | https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp03.px | CA Euskadi | CA x sexo x edad (18-19, 20-24, 25-29, 30-34…) x tipo de renta | Anual | 2024 (19/10/2026) | Renta personal media joven CA (proxy salario) |
| Eustat — Renta personal media municipal (PX_173402_crpf_rpf_rp11s.px) | https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp11s.px | CA Euskadi (276 ámbitos: municipios/comarcas) | Municipio x sexo x tipo de renta (total 18+) | Anual | 2024 | Renta personal media municipal (proxy principal) |
| Eustat — Población por municipio/grupo edad (PX_010154_cepv1_ep06b.px) | https://www.eustat.eus/bankupx/api/v1/es/DB/PX_010154_cepv1_ep06b.px | CA Euskadi (municipios) | Municipio x sexo x grupo edad (0-19, 20-64, 65+) | Anual | 2025 (ref. 01/01/2025) | Población municipal (solo grupos amplios) |
| Eustat — Estadística Renta Personal y Familiar | https://es.eustat.eus/estadisticas/tema_160/opt_1/tipo_3/ti_Estadistica_de_renta_personal_y_familiar/temas.html | CA Euskadi | CA/municipio/barrio/sección; edad quinquenal a nivel CA | Anual | 2024 (19/10/2026) | Renta joven 18-34: 15.914 €/año (2024) |
| Observatorio Vasco de la Juventud — Empleo y situación económica (Open Data Euskadi) | https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_empleo_econom/opendata/iovj-empleo-economico.csv | CA Euskadi | CA joven (18-34 / 16-29) x sexo | Semanal (datos OVJ) | 23/10/2026 | Salario neto medio joven: 1.564 €/mes (2024) |
| Observatorio Vasco de la Juventud — Emancipación y vivienda | https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv | CA Euskadi | CA joven | Semanal | 23/10/2026 | Coste teórico acceso vivienda joven |
| INE — EPA Decil de salarios (tablas 66239/66252) | https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/66239 | España | Nacional x grupo edad (16-24, 25-34…) x decil x jornada | Anual | 2024 | Salario bruto joven (1.372,8 € <25; 2.131,6 € 25-34) |
| INE — EPA Salarios medios por CCAA y decil | https://www.ine.es/dynt3/inebase/es/index.htm?padre=2584&dh=1 | España (CCAA) | CCAA x decil (sin edad) | Anual | 2024 | Distribución salarial por CCAA |
| INE — EES cuatrienal 2022 (tablas 36873, 36875, 36877, 36883, 36894) | https://www.ine.es/jaxiT3/Tabla.htm?t=36873&L=0 | España incl. País Vasco | CCAA x sexo x edad (<25, 25-34, 35-44…) | Cuatrienal | 2022 | Salario anual por CCAA y edad joven |
| INE — EAES (tabla 28189) | https://www.ine.es/jaxiT3/Tabla.htm?t=28189&L=0 | España | Nacional x sexo x edad (quinquenal) | Anual | 2024 | Salario anual por edad |
| INE — ECV: renta por persona/UC por edad y sexo | https://datos.gob.es/es/catalogo/conjuntos-datos?tags_es=Sueldos+y+salarios | España | Nacional x edad x sexo | Anual | 2024 (series recientes) | Renta (no salario) joven |
| INE — Atlas de Distribución de Renta de los Hogares (ADRH) | https://datos.gob.es/es/catalogo/conjuntos-datos?tags_ca=Renta+neta+media+por+persona__es | Municipios (España) | Municipio x renta media/mediana | Anual | 2023/2024 | Renta municipal proxy (sin edad) |
| AEAT — Mercado de trabajo y pensiones (por provincia, edad y sexo) | https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/mercado/2024/jrubik3085b187e857f83444026f13b50d507a40df8760.html | Provincias TRFC (excluye País Vasco/Navarra) | Provincia x tramo edad (18-25…) | Anual | 2024 | Salario medio anual joven (no Euskadi) |
| Eurostat — ilc_di03 (renta media/mediana por edad y sexo) | https://ec.europa.eu/eurostat/databrowser/product/page/ilc_di03$defaultview | Países UE (España nacional) | Nacional x edad x sexo | Anual | 2025 | Renta joven (no municipal) |
| Eurostat — nama_10r_2hhinc / tgs00026 (renta disponible hogares NUTS2) | https://ec.europa.eu/eurostat/databrowser/view/nama_10r_2hhinc/ | NUTS2 (incluye País Vasco) | Región NUTS2 | Anual | 2024 | Renta regional (sin edad) |
| datos.gob.es (portal) | https://datos.gob.es/es/ | España | Catálogo (INE, AEAT, etc.) | Variable | Variable | Acceso a datasets anteriores |
| opendata.euskadi.eus (portal) | https://opendata.euskadi.eus/ | CA Euskadi | Municipio/CA | Variable | Variable | OVJ, Udalmap, Eustat |
| Eustat vía Open Data Donostia (renta familiar/personal) | https://opendata.euskadi.eus/catalogo/-/renta-familiar-y-personal/ | Donostia (barrio/unidad menor) | Barrio/unidad menor | Anual | 2024-2025 | Renta municipal muy granular (solo Donostia) |

## Conclusión operativa

- **Salario joven municipal: no existe** en Euskadi ni en España.
- Mejor proxy municipal: **Eustat renta personal media municipal** (total 18+, 2024) combinada con ratio edad/total de **Eustat renta por edad** (CA) o salario neto joven OVJ (1.564 €/mes, 2024).
- Para comparación entre CCAA: **INE EES 2022** (CCAA x edad) o EPA/AEAT (más recientes pero sin edad o sin Euskadi).
- Para análisis joven nacional: **INE EPA 2024** (salario bruto por edad) y **Eurostat ilc_di03**.
