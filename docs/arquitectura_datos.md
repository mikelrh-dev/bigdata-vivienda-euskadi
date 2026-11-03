# Arquitectura de datos — recorrido origen → análisis

Entregable §3 del PDF (esquema del recorrido). Fase actual: obtencion + transformacion.
HDFS / Kafka / MongoDB = futuro (readiness en `framework_auditoria_completo2/06_readiness_mongo_infra.md`).

```mermaid
flowchart LR
    subgraph Fuentes["Fuentes reales"]
        API["APIs: Eustat, INE, Euskadi OpenData, Bizilagun/Etxebide, GTFS, OSRM"]
        SCR["Scraping: Fotocasa + Pisos.com\n(HTML crudo en data/raw/html_fotocasa/)"]
        OPT["RealtyAPI (opcional, por env)"]
    end
    subgraph Extract["extract/ (38 scripts)"]
        ING["main_ingest.py + _common.py\n(Cliente, logs, sidecars)"]
    end
    subgraph RAW["data/raw/ — INMUTABLE\n314 ficheros + manifest SHA-256 + .FROZEN"]
    end
    subgraph Transform["transform/ (43 scripts, run_all.py)"]
        UNI["unificar_anuncios.py\n(dedup portal+id, fingerprint,\ncuarentena, IQR flags)"]
        ENR["enriquecedores + vistas\n(mercado, renta, tension, GTFS, distancias)"]
        DIM["dim_municipios.csv (252)\n+ analisis_variables_base.csv"]
    end
    subgraph Silver["data/procesado/ — SILVER\n119 ficheros, BOM utf-8-sig"]
    end
    subgraph QA["Puerta de calidad"]
        GATE["verificar_fase_datos.py (18/18)\n+ pytest (83 passed)\n+ run_all --check (35/35)"]
    end
    subgraph Futuro["Futuro (no implementado)"]
        MONGO[("MongoDB\n(PyMongo, aggregation)")]
        HK["HDFS (/raw, /procesado)\n+ Kafka (anuncios)"]
    end
    API --> ING
    SCR --> ING
    OPT --> ING
    ING --> RAW
    RAW --> UNI
    UNI --> ENR
    ENR --> DIM
    UNI --> Silver
    ENR --> Silver
    DIM --> Silver
    Silver --> GATE
    GATE -->|"GO con deuda"| MONGO
    GATE -->|"GO con deuda"| HK
```

## Tabla de flujos

| # | Origen | Script | Destino | n |
|---|--------|--------|---------|---|
| 1 | APIs + scraping | `extract/main_ingest.py` | `data/raw/` | 314 |
| 2 | `anuncios_*_enriquecido_geo.json` + RealtyAPI | `transform/unificar_anuncios.py` | `anuncios_unificados.json/.csv` | 759, 83 mun |
| 3 | unificados + oficiales + complementarios | `transform/` (vistas) | `dim_municipios.csv`, `analisis_variables_base.csv`, `alquiler_municipal_completo.csv` (252) | 252 |
| 4 | silver | gate + tests | veredicto GO/NO-GO | 18/18, 83 passed |
| 5 | silver (futuro) | PyMongo load | MongoDB | — |
| 6 | raw/silver (futuro) | HDFS + Kafka | `/raw`, `/procesado`, topic anuncios | — |

## Decisiones clave

- Raw append-only con `_raw_guard` + manifest + `.FROZEN` (contrato en `docs/contrato_datos_raw.md`).
- Joins siempre por `codigo_ine` (5 dígitos), nunca por nombre (`muni_resolve.py`).
- Nulos con flag + método (`R1`, `R6`, `R8`, `R9` en `docs/reglas_limpieza.md`); outliers marcados, no borrados.
- Limitaciones declaradas: cobertura anuncios 83/252 (4 robustos), Pisos geo aproximada, equipamiento solo RealtyAPI, renta joven = proxy.
