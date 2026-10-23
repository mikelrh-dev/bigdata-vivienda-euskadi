# Plan del Reto Intermodal SBD + BDA
## ¿Dónde pueden vivir los jóvenes en Euskadi?

Documento de planificación generado a partir de un análisis del PDF del
reto y de la verificación real de las fuentes de datos y del entorno.

---

## 0. Resumen del reto

**Pregunta a responder:** ¿Puede una persona joven independizarse en
Euskadi con su salario? ¿Qué municipios ofrecen mejores posibilidades
de emancipación y por qué?

**Objetivo:** construir un sistema de recogida, almacenamiento y análisis
de datos (todo en Python) que demuestre la respuesta con **datos reales**.

**Recorrido de los datos:**

```
Fuentes (API + scraping)
   → HDFS (originales)
   → Kafka (simulación de anuncios nuevos)
   → MongoDB (crudo)
   → PyMongo (limpieza y transformación)
   → Aggregation Pipeline (indicadores)
   → Gráficos + informe (conclusiones)
```

**Ámbito:** TODO EUSKADI (Álava, Bizkaia, Gipuzkoa).

**Entregables:**
1. Código fuente (scripts Python organizados y documentados)
2. Datos (ficheros en HDFS + base de datos MongoDB)
3. Arquitectura (esquema del recorrido de los datos)
4. Informe de resultados (gráficos, tablas, conclusiones)
5. Demostración (ejecución del sistema + decisiones técnicas)

**Rúbricas a cubrir (del PDF):**

BDA — RA1
| Criterio | Nivel máximo (10 pts) |
|---|---|
| Extracción | Automatiza API **y** scraping |
| Almacenamiento HDFS | Organiza originales y procesados y demuestra su recuperación |
| Kafka | Productor y consumidor Python funcionan y procesan mensajes |
| Integración | Demuestra el flujo completo hasta MongoDB |

SBD — RA3
| Criterio | Nivel máximo (10 pts) |
|---|---|
| Modelado MongoDB | Justifica el modelo y las relaciones entre datos |
| Operaciones PyMongo | Inserta, actualiza y elimina; automatiza y comprueba resultados |
| Consultas | Filtros, proyecciones, ordenaciones + campos anidados/arrays |
| Aggregation Pipeline | ≥4 etapas diferentes combinadas en indicadores complejos |

SBD — RA4
| Criterio | Nivel máximo (10 pts) |
|---|---|
| Gráficos | ≥3 tipos adecuados a los datos |
| Datos utilizados | Genera gráficos directamente desde consultas PyMongo |
| Presentación | Títulos, unidades, leyendas + facilita comparar municipios |
| Interpretación | Relaciona resultados y explica sus implicaciones |

---

## 1. Entorno detectado (Windows 11)

| Componente | Estado |
|---|---|
| Java 22 | YA instalado (necesario para HDFS y Kafka) |
| Docker 29.7 + Compose v5.5 | YA instalado, **demonio NO arrancado** |
| WSL2 Ubuntu | YA instalado (parado) — plan B |
| Espacio en disco | 251 GB libres |
| Python | Varios (3.10, 3.12, 3.14, conda) |
| `mongod` local | NO instalado → MongoDB en Docker |
| `pymongo` | Solo en Python 3.10 (4.17) |
| `pandas` / `matplotlib` / `seaborn` | En 3.10 y 3.12, no juntos con `pymongo` |
| `kafka-python` | NO instalado en ningún venv |

**Decisión:** crear un venv NUEVO y dedicado. No reutilizar los entornos
de Anaconda ni otros venvs del equipo.

---

## 2. Arquitectura propuesta

```
 Eustat API (bankupx) ───────────────┐
 Eustat ExtractorBlob (alquiler) ────┤
 euskadi.eus CSV (emancipación) ─────┤
 b5m API (geo) ──────────────────────┼──► [Python] extracción
 INE API (wstempus) ─────────────────┤
 INE / ENALQ (xlsx) ─────────────────┤
 Catastro / CartoCiudad (opcional) ──┤
 Fotocasa (scraping) ────────────────┘        │
                                              ▼
                                     ┌──────────────┐
                                     │     HDFS     │  /raw/       (crudo)
                                     │ NameNode +   │  /procesado/ (normalizado)
                                     │ DataNode     │
                                     └──────┬───────┘
                                            │  kafka_producer.py (Windows)
                                            ▼
                                     ┌──────────────┐
                                     │ Apache Kafka │  ← VM UBUNTU SERVER
                                     │ topic:       │     IP:9092 (KRaft)
                                     │ anuncios_    │
                                     │ inmobiliarios│
                                     └──────┬───────┘
                                            │  kafka_consumer.py (Windows)
                                            ▼
                                     ┌──────────────┐
                                     │   MongoDB    │  ← Docker en Windows
                                     │  (PyMongo)   │
                                     └──────┬───────┘
                                            │
                ┌───────────────────────────┼───────────────────────────┐
                ▼                           ▼                           ▼
        Limpieza PyMongo            Aggregation Pipeline          Gráficos + informe
        (duplicados, nulos,         $match, $group, $sort,        matplotlib/seaborn
         tipos, unidades)           $project, $lookup, $facet      (≥3 tipos)
```

**Windows (Docker):** HDFS + MongoDB, un solo `docker-compose.yml`.
**VM Ubuntu Server:** Kafka, otro `docker-compose.yml` (o tarball).

---

## 3. Fuentes API (NO requieren registro) — verificadas

### 3.1 API Eustat (bankupx) — JSON, abierto, sin key

```
GET  https://www.eustat.eus/bankupx/api/v1/es/DB/{ID_PX}
     → metadatos (título, variables, valores)
POST a la misma URL con body:
     {"query":[],"response":{"format":"json"}}
     → dataset completo
```

Verificado: devuelve JSON de cientos de KB. El ámbito territorial tiene
**276 valores** (todos los municipios con código INE).

| ID de tabla | Contenido |
|---|---|
| `PX_010154_cepv1_ep06b.px` | Población por municipio y grupo de edad |
| `PX_173402_crpf_rpf_rp11s.px` | Renta personal media por municipio (€) |
| `PX_173402_crpf_rpf_rp03.px` | Renta personal media **por edad** (18-19, 20-24, 25-29, 30-34...) y tipo de renta (del trabajo, disponible) |
| `PX_170120_cpibmun_pibmun03b.px` | PIB por municipio |
| `PX_122404_cemv_viv09a.px` | Viviendas por régimen de tenencia (alquiler/propiedad) por municipio |

> **Nota:** la API **no** trae el precio del alquiler municipal; eso va
> por el ExtractorBlob (sección 3.3).

### 3.2 API INE (wstempus) — JSON, abierto, sin key

```
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tabla}
```

Verificado: devuelve hasta 14 MB (9.999 series). Documentación oficial en
`ine.es/dyngs/DAB` (incluye un `wstempus.yaml` OpenAPI).

| Tabla | Contenido |
|---|---|
| `69301` | Población residente por municipio |
| `69302` | Hogares, viviendas, hogares unipersonales |
| `69303` | Tasa de actividad / desempleo |
| `69316` | Indicadores Urbanos: alquiler y compraventa (por conurbación) |
| `69323` | Indicadores Urbanos: vivienda |
| `69330` | Indicadores Urbanos completo (9.999 series) |

> **LIMITACIÓN VERIFICADA:** el alquiler por municipio está publicado para
> 820 municipios, pero **todos los vascos vienen a `None`** (INE no
> publica alquiler en regímenes forales). SÍ sirve para población,
> hogares, viviendas y precios de compraventa.

### 3.3 Eustat ExtractorBlob — CSV/XLSX, abierto, sin key

```
https://es.eustat.eus/comun/ExtractorBlob.ashx?id=alquiler_vivienda~2/tbl_0024628_c.csv
```

Verificado: **271 filas** con, por municipio (y distrito):
renta media €/m²/mes (media, mediana, P25, P75), cuantía media del
alquiler €/mes, superficie construida media m². Año 2024.
**Cubre los 3 territorios** (secciones Araba/Álava, Bizkaia, Gipuzkoa).

Otras tablas disponibles: `tbl_0024627` (territorial),
`tbl_0024629`/`tbl_0024630`/`tbl_0024631` (distrito y sección censal).
Idiomas: `_c` castellano, `_e` euskera. Formatos: `.csv` y `.xlsx`.

> Esta fuente cuenta como **extracción automatizada / scraping**.

### 3.4 API b5m Gipuzkoa — JSON/GeoJSON, abierto, sin key

```
https://b5m.gipuzkoa.eus/api/2.0/datasets
```

- `GFA_DSET_MB.geojson` → límites municipales + `CODMUNIINE`
- `GFA_DSET_DISTM_CSV.zip` → distancias entre municipios

> Solo Gipuzkoa. Para Álava/Bizkaia usar la lista de municipios de Eustat.

### 3.5 API Catastro (INSPIRE) — WFS/WMS, abierto, sin registro

```
http://ovc.catastro.meh.es/INSPIRE/wfsAD.aspx?request=GetCapabilities
```

Direcciones, parcelas, antigüedad de edificios. Sirve para enriquecer
cada anuncio (año de construcción, número de viviendas del edificio).

### 3.6 API CartoCiudad (geocoder) — abierto, sin registro

```
https://www.cartociudad.es/geocoder/api/geocoder
```

Geocodificación de direcciones de anuncios.

### 3.7 CSV directo euskadi.eus (emancipación / juventud)

```
https://www.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv
```

Verificado: **867 filas**, 16 indicadores, datos hasta 2024:
- Tasa de emancipación, edad media de emancipación
- **Coste de acceso a la vivienda en alquiler** por grupo de edad
  (18-24, 25-29, 30-34) y territorio histórico
- Sobreesfuerzo económico (hipoteca/renta)
- Jóvenes inscritos en Etxebide

### 3.8 Dato oficial de salario joven (contexto)

- **Salario neto medio de la juventud asalariada 18-34 en 2024:
  1.564 €/mes** (incluidas pagas extra).
- Fuente: Observatorio Vasco de la Juventud / "Claves de la
  Emancipación en Euskadi". Verificado en euskadi.eus.
- **No** está por municipio: sirve como referencia general de Euskadi.

---

## 4. Fuentes API que SÍ requieren registro

| API | Registro | Plan gratis | Comentario |
|---|---|---|---|
| **Idealista Search API** (oficial) | Formulario + aprobación (`developers.idealista.com/access-request`) | Sí (revisan el proyecto) | La mejor fuente de precios de oferta. **Recomendado pedirla** |
| RealtyAPI.io (Idealista no oficial) | Cuenta en su web | 25.000 peticiones/mes | Servicio no oficial; puede cambiar |
| RapidAPI "Idealista API" | Cuenta RapidAPI | BASIC gratis (límite bajo) | PRO 20 $/mes |
| Apify (Pisos.com/Fotocasa/Idealista) | Cuenta Apify | 5 $ de crédito | Ejecutan el scraping por ti |
| WebScrapingAPI / ScraperAPI / Spider.cloud | Cuenta | Muy limitado | Servicios de scraping |

### Veredicto

- **Ninguna es imprescindible.** Fotocasa (scraping propio) + Eustat/INE
  (API abiertas) ya cubren el criterio de extracción al máximo nivel.
- El único **plus real** es la API oficial de Idealista. Recomiendo
  pedirla explicando que es un trabajo académico; si la aprueban, mejor,
  y si no, Fotocasa basta.
- **No vale la pena:**
  - SERPAVI (Ministerio Vivienda): SPA cerrada (403/404, sin API abierta).
    El dato de alquiler ya lo da Eustat mejor.
  - MITMA precios de vivienda: 403.
  - datos.gob.es: 403.
  - Idealista por scraping directo: 403 (DataDome).

---

## 5. Fuentes de SCRAPING (verificadas)

### 5.1 Fotocasa — sin key, VERIFICADO en las 3 provincias

```
GET https://www.fotocasa.es/es/alquiler/viviendas/{provincia}/todas-las-zonas/l
```

Los anuncios están en un `<script type="application/json">`:

```
initialSearch.result.realEstates[]
  ├─ price / rawPrice / reducedPrice
  ├─ address: municipality, zipCode, neighborhood, city, county
  ├─ coordinates: latitude, longitude
  ├─ features (habitaciones, m²)
  ├─ date, description
  └─ detail, detailWithParams, multimedia
```

**Cobertura real comprobada:**

| Provincia | URL | Anuncios |
|---|---|---|
| Gipuzkoa | `gipuzkoa-provincia/todas-las-zonas/l` | 115 |
| Bizkaia | `bizkaia-provincia/todas-las-zonas/l` | 352 |
| Álava | `araba-alava-provincia/todas-las-zonas/l` | 16 |
| **Total** | | **≈ 483** |

- Paginación: `/l/2`, `/l/3`... (30 anuncios por página)
- `robots.txt`: prohíbe `/_sysutils/`, `/backwebs/`, `/buscar/`,
  `/clientbin/`, `/complements/`. **NO prohíbe `/es/alquiler/viviendas/`**
  → scraping legítimo a ritmo razonable.
- Recomendado: pausas entre peticiones, user-agent correcto, guardar el
  HTML crudo en HDFS.

### 5.2 Eustat ExtractorBlob

Ver sección 3.3. Cuenta como extracción automatizada.

### 5.3 Bloqueadas (no perder tiempo)

- **Idealista**: 403 (DataDome)
- **Yaencontre**: 403
- **Pisos.com**: 404 en las URLs probadas
- **Habitaclia**: 404

---

## 6. División de trabajo: VM Ubuntu Server vs Windows

```
┌──────────────────────────────────────────────────────────────┐
│ EN LA VM UBUNTU SERVER                                         │
│   Infraestructura Kafka                                        │
│    - Instalar Kafka (Docker o tarball)                         │
│    - Modo KRaft (sin Zookeeper), 1 broker                      │
│    - Topic: anuncios_inmobiliarios                             │
│    - Puerto 9092 abierto (ufw allow 9092)                      │
│    - advertised.listeners = IP de la VM                        │
│   Lo que desarrollas: SOLO configuración/arranque.             │
│   No va código Python del pipeline aquí (salvo opción B).       │
└───────────────────────────────┬──────────────────────────────┘
                                │ red (Windows ↔ VM, puerto 9092)
┌───────────────────────────────▼──────────────────────────────┐
│ AQUÍ (WINDOWS 11)                                              │
│   1.  Entorno: venv Python 3.12 + requirements.txt             │
│   2.  Docker Compose: HDFS (NameNode+DataNode) + MongoDB       │
│   3.  Extracción: 01_eustat_api.py, 02_eustat_alquiler.py,     │
│       03_euskadi_emancipacion.py, 04_b5m_geo.py,               │
│       05_fotocasa_scraper.py, 06_ine_api.py                    │
│   4.  HDFS: subir /raw/ y /procesado/                           │
│   5.  kafka_producer.py  → publica en la VM                    │
│   6.  kafka_consumer.py  → lee de la VM → MongoDB              │
│   7.  Limpieza + transformación con PyMongo                    │
│   8.  Aggregation Pipeline (≥4 etapas)                        │
│   9.  Gráficos + informe (matplotlib/seaborn + notebook)       │
│  10.  Docs: arquitectura.md, informe_resultados.md             │
└──────────────────────────────────────────────────────────────┘
```

### Opción A (recomendada)
Productor y consumidor en **Windows**, Kafka en la **VM**.
Demuestra comunicación entre máquinas con código propio en ambos
extremos. Más simple de depurar.

### Opción B (más realista)
El productor corre en la **VM** (publica en su Kafka local) y el
consumidor en **Windows** (lee y escribe en MongoDB de Windows).
Más "distribuido" pero más complejo.

> Se recomienda A para el primer intento.

---

## 7. Estructura del proyecto

```
BigDataReto/
├── plan/
│   ├── PLAN.md              ← este documento
│   ├── arquitectura.md      (esquema pedido)
│   └── informe_resultados.md
├── docker-compose.yml       (HDFS + MongoDB, Windows)
├── .env                     (IPs, puertos, credenciales — no a git)
├── requirements.txt
├── README.md
├── config/
│   └── fuentes.yaml         (URLs, IDs PX, municipios, provincias)
├── extract/
│   ├── 01_eustat_api.py     (población, renta por edad, renta municipal,
│   │                         tenencia, PIB)
│   ├── 02_eustat_alquiler.py (ExtractorBlob municipal, 3 territorios)
│   ├── 03_euskadi_emancipacion.py
│   ├── 04_b5m_geo.py
│   ├── 05_fotocasa_scraper.py (3 provincias + paginación + reintentos)
│   └── 06_ine_api.py        (wstempus: población/hogares/precios)
├── storage/
│   ├── hdfs_utils.py        (subir raw y procesado a HDFS)
│   ├── kafka_producer.py    (publica anuncios en la VM)
│   ├── kafka_consumer.py    (consume de la VM → MongoDB)
│   └── mongo_crud.py        (insert/update/delete con PyMongo)
├── transform/
│   ├── limpieza.py          (duplicados, nulos, tipos, €/m²)
│   └── enrich.py            (join anuncio↔municipio↔renta↔alquiler ref.)
├── analysis/
│   ├── pipeline_agregaciones.py ($match/$group/$sort/$project/$lookup/$facet)
│   └── indicadores.py       (esfuerzo %, ranking, accesibilidad)
├── visualization/
│   └── graficos.py          (barras, dispersión, mapa, boxplot)
├── notebooks/
│   └── informe.ipynb
└── data/
    ├── raw/                 (originales, tal cual llegan)
    ├── procesado/           (normalizado)
    └── resultados/          (indicadores, gráficos)
```

---

## 8. `requirements.txt` propuesto

```
pymongo
kafka-python-ng          # fork mantenido de kafka-python
pandas
numpy
matplotlib
seaborn
requests
beautifulsoup4
lxml
python-dotenv
pyyaml
jupyter
```

> Alternativa si `kafka-python-ng` da problemas con Python 3.12:
> `confluent-kafka` (tiene ruedas precompiladas para Windows).

---

## 9. Plan por fases

### FASE 0 — Entorno y VM (2-3 días). **EMPEZAR AQUÍ**

| Paso | Tarea |
|---|---|
| 0.1 | Windows: arrancar Docker Desktop; crear venv; instalar `requirements.txt` |
| 0.2 | Windows: `docker-compose.yml` (HDFS + MongoDB); verificar que se levantan y se conectan |
| 0.3 | VM: instalar y arrancar Kafka (KRaft), abrir 9092, IP fija |
| 0.4 | Prueba de fuego: producer Python (Windows) → Kafka (VM) → consumer Python (Windows) |
| 0.5 | Opcional: pedir API key de Idealista (tarda días) |

> Esta es la fase más crítica (red Windows↔VM, HDFS en Windows).
> Resolverla cuanto antes, no dejarla para el final.

### FASE 1 — Extracción (4-5 días)

| Paso | Tarea |
|---|---|
| 1.1 | Eustat API: población, renta por edad, renta municipal, tenencia |
| 1.2 | Alquiler municipal (ExtractorBlob) para los 3 territorios |
| 1.3 | Emancipación (CSV) + ENALQ (xlsx) + PIB municipal |
| 1.4 | INE API (wstempus): población/hogares/precios por municipio (NO alquiler) |
| 1.5 | Scraping Fotocasa: 3 provincias + paginación → ~500 anuncios |
| 1.6 | Guardar TODO en HDFS `/raw/` con metadatos (fecha, fuente, licencia) |

### FASE 2 — Kafka (2-3 días)

| Paso | Tarea |
|---|---|
| 2.1 | Productor Python → publica anuncios en el topic de la VM |
| 2.2 | Consumidor Python → lee del topic e inserta en MongoDB |
| 2.3 | Simular "nuevos anuncios" en tiempo real |

### FASE 3 — MongoDB: modelado + operaciones (3-4 días)

| Paso | Tarea |
|---|---|
| 3.1 | Diseñar colecciones y **justificar** el modelo: `anuncios`, `municipios`, `indicadores_eustat`, `emancipacion`, `geo_municipios` |
| 3.2 | insert/update/delete automáticos con comprobación de resultados |
| 3.3 | Consultas con filtros, proyecciones, ordenación, campos anidados/arrays |

### FASE 4 — Limpieza y transformación con PyMongo (3 días)

| Paso | Tarea |
|---|---|
| 4.1 | Duplicados (mismo anuncio re-publicado), nulos, tipos, unidades |
| 4.2 | Normalizar €/m² y cruzar cada anuncio con su municipio (INE) y con la renta |

### FASE 5 — Aggregation Pipeline (3-4 días)

| Paso | Tarea |
|---|---|
| 5.1 | ≥4 etapas distintas: `$match`, `$group`, `$sort`, `$project`, `$lookup`, `$facet` |
| 5.2 | Indicadores: alquiler medio por municipio, % esfuerzo (alquiler/renta joven), ranking de accesibilidad, €/m² |

### FASE 6 — Visualización e informe (3-4 días)

| Paso | Tarea |
|---|---|
| 6.1 | ≥3 tipos de gráficos con títulos, unidades y leyendas |
| 6.2 | Generados **directamente** desde consultas PyMongo |
| 6.3 | Conclusiones: qué municipios y por qué, respaldado en los datos |

---

## 10. Decisiones abiertas

### a) Características de la VM (bloquean el diseño de Kafka)
- ¿Tiene Docker instalado, o solo Java, o nada?
- ¿Qué IP tiene y cómo está conectada (bridged / NAT)?
- ¿La IP es fija o cambia?
- ¿Tiene salida a internet?

### b) ¿Pedir la API de Idealista?
Recomendado pedirla (tarda); mientras tanto, Fotocasa cubre el scraping.

### c) Salario/renta joven por municipio (decisión de modelo clave)
Eustat da:
- `renta personal media por edad` → nivel **Euskadi** (no municipal)
- `renta personal media por municipio` → **municipal** (sin desglose de edad)

**Propuesta de modelo:**
- Renta joven 18-34 (Eustat `rp03`, por edad) → nivel Euskadi
- Renta personal media por municipio (Eustat `rp11s`) → municipal
- Coste de acceso a la vivienda en alquiler 18-24 / 25-29 / 30-34
  (CSV emancipación) → por territorio

Con eso se calcula el % de esfuerzo por municipio y por edad.
**Conviene confirmarlo con el profesor antes de cerrar.**

### d) ¿Incluir compraventa como contraste?
El foco es alquiler. Recomendado: alquiler como eje, compraventa solo
como dato complementario.

### e) Formato de la demo
Se puntúa "ejecución del sistema". Preparar un guion:
levantar compose → arrancar Kafka en la VM → correr productor →
ver el consumidor insertar en MongoDB → lanzar una agregación →
mostrar un gráfico.

---

## 11. Riesgos

| Riesgo | Mitigación |
|---|---|
| Red Windows↔VM (IP dinámica, firewall, NAT) | IP fija, `ufw allow 9092`, probar en Fase 0 |
| HDFS en Windows | Plan B: WSL2 o contenedor único namenode+datanode |
| Fotocasa cambia el HTML | Scraper aislado con reintentos; guardar HTML crudo en HDFS |
| INE API no da alquiler en Euskadi | Ya identificado: no usarlo para alquiler |
| Dejar limpieza/agregación para el final | Es la mitad de la nota (SBD) y depende de Fase 1 |
| Kafka: Zookeeper añade complejidad | Usar modo KRaft |

---

## 12. Primeros pasos concretos

1. Arrancar Docker Desktop en Windows y comprobar `docker info`.
2. Crear el venv e instalar `requirements.txt`.
3. En la VM: instalar y arrancar Kafka (KRaft) y abrir el 9092.
4. (Opcional, en paralelo) Pedir la API key de Idealista.

---

## 13. Próximos artefactos a preparar

Cuando se respondan las preguntas de la sección 10a (características de
la VM) y se decida lo de la API de Idealista:

- `docker-compose.yml` de Windows (HDFS + MongoDB)
- `requirements.txt` definitivo
- Configuración de Kafka para la VM (Docker o tarball, según elijas)
- `config/fuentes.yaml` con las URLs e IDs verificados
