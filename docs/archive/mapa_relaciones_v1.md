# Mapa de Relaciones — BigData Vivienda Euskadi

> Regenerable: actualizar manualmente cuando cambien transforms, datos o preguntas.
> Renderiza en GitHub, VS Code (extensión Mermaid), Obsidian o https://mermaid.live

---

## 1. Flujo de datos (raw → silver → análisis → conclusiones)

```mermaid
flowchart LR
    A[Raw bronce<br/>303 archivos<br/>congelado .FROZEN] --> B[Silver procesado<br/>93 archivos<br/>regenerados]
    B --> C[Analisis DuckDB<br/>consultas SQL]
    C --> D[Conclusiones<br/>O1-O4 + 42 preguntas]
    D --> E[Dashboard visual<br/>8 graficos PNG]
    D --> F[Docs<br/>decision_salario_proxy.md<br/>conclusiones_finales.md]

    style A fill:#e74c3c,color:#fff
    style B fill:#2ecc71,color:#fff
    style C fill:#3498db,color:#fff
    style D fill:#f39c12,color:#fff
```

---

## 2. Dependencias entre transforms (qué script genera qué archivo)

```mermaid
graph TD
    subgraph Extract
        E1[01_eustat_api.py] --> R1[raw/eustat_*]
        E2[02_eustat_alquiler.py] --> R2[raw/alquiler_*]
        E5[05_fotocasa_scraper.py] --> R3[raw/anuncios_fotocasa*]
        E8[08_pisos_scraper.py] --> R4[raw/anuncios_pisos*]
        E10[10_ovj_salario.py] --> R5[raw/ovj_salario_joven_2024.json]
        E22[22_geo_areas_funcionales.py] --> R6[raw/areas_funcionales_municipios.csv]
    end

    subgraph Transform
        T1[corregir_empleo.py] --> S1[procesado/empleo_corregido]
        T2[validar_renta.py] --> S2[procesado/renta_validada]
        T3[dim_municipios.py] --> S3[procesado/dim_municipios]
        T4[parsear_secciones.py] --> S4[procesado/secciones]
        T5[generar_distancias.py] --> S5[procesado/distancias]
        T6[unificar_anuncios.py] --> S6[procesado/anuncios_unificados]
        T7[generar_fingerprint.py] --> S7[procesado/fingerprint]
        T8[generar_municipios_faltantes_93.py] --> S8[procesado/municipios_faltantes_93]
        T9[generar_analisis_variables_base.py] --> S9[procesado/analisis_variables_base]
        T10[generar_emancipacion_tier3_93.py] --> S10[procesado/emancipacion_tier3_93]
        T11[generar_poblacion_joven_municipal.py] --> S11[procesado/poblacion_joven_municipal]
        T12[asignar_area_funcional_ecvi.py] --> S12[procesado/municipio_area_funcional_ecvi]
        T13[calcular_renta_joven.py] --> S13[procesado/dim_municipios_enriquecido]
        T14[generar_dashboard_completo.py] --> S14[procesado/../resultados/*.png]
    end

    R1 --> T2
    R2 --> T1
    R3 --> T6
    R4 --> T6
    R5 --> T13
    R6 --> T12
    S3 --> T9
    S6 --> T7
    S11 --> T13
```

---

## 3. Mapa pregunta → archivo → conclusión

```mermaid
graph LR
    subgraph Preguntas
        O1[O1: ¿Puede independizarse?]
        O2[O2: ¿Qué municipios viables?]
        O3[O3: ¿Trabajo + vivienda barata?]
        O4[O4: ¿Limitaciones?]
    end

    subgraph Archivos
        F1[dim_municipios_enriquecido.csv]
        F2[anuncios_unificados.csv]
        F3[analisis_variables_base.csv]
        F4[metodologia.md]
    end

    subgraph Conclusiones
        C1[No. Esfuerzo 40.5-76.3%]
        C2[Solo 6 robustos]
        C3[Correlacion espuria r=+0.385]
        C4[10 gaps documentados]
    end

    O1 --> F1 --> C1
    O2 --> F2 --> C2
    O3 --> F3 --> C3
    O4 --> F4 --> C4
```

### Bloque A — Accesibilidad
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| A1 Esfuerzo mediano | dim_municipios_enriquecido.csv | mediana 40.5-76.3% |
| A2 % >30% | dim_municipios_enriquecido.csv | 100% de 159 municipios |
| A3 Fiscal vs salarial | decision_salario_proxy.md | intervalo [40.5-76.3%] |
| A4 Oficial vs anuncios | alquiler_municipal_completo.csv | 159 directo + 93 comarcal |
| A5 Sin dato | alquiler_municipal_completo.csv | 93 imputados por comarca |
| A6 Temporal vs larga | anuncios_unificados.csv | modalidad separada |

### Bloque B — Mercado laboral
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| B1 Paro juvenil | analisis_variables_base.csv | tasa_paro_lanbide_pct |
| B2 Ocupación vs precio | analisis_variables_base.csv | correlación espuria |
| B3 Afiliación SS | analisis_variables_base.csv | afiliacion_ss_16_24_pct |
| B4 Trade-off paro/precio | analisis_variables_base.csv | r=+0.385 espuria |
| B5 Paro larga duración | lanbide_paro_juvenil.csv | paro_larga_duracion |
| B6 Tasa desempleo real | — | LIMITACIÓN: falta población activa joven |

### Bloque C — Vivienda stock y calidad
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| C1 VPO | udalmap_empleo_corregido.csv | 93.6% ceros |
| C2 Antigüedad | udalmap_empleo_corregido.csv | antiguedad_media_anyos |
| C3 Confort/ascensor | udalmap_empleo_corregido.csv | indice_confort |
| C4 Superficie media | anuncios_unificados.csv | superficie_m2 |
| C5 Cert. energético | anuncios_fotocasa_detalle.json | 467/470 |
| C6 Licencias nueva construcción | udalmap_empleo_corregido.csv | licencias_nueva_por_mil |

### Bloque D — Geografía
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| D1 Distancia capital | analisis_variables_base.csv | dist_centroide_comarca_km |
| D2 Conectividad GTFS | transporte_paradas_municipio_enriquecido.csv | expediciones_dia |
| D3 OSRM vs Haversine | municipios_faltantes_93.csv | distancias_capitales.csv |
| D4 Rural vs urbano | analisis_variables_base.csv | tipologia_mercado |
| D5 Densidad población | eustat_demografia_renta_252.csv | poblacion_total |

### Bloque E — Demografía
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| E1 Población extranjera | — | LIMITACIÓN: no en silver |
| E2 Variación población | — | LIMITACIÓN: no en silver |
| E3 Envejecimiento | — | LIMITACIÓN: no en silver |
| E4 Renta por sexo | eustat_renta_edad.csv | brecha 1612 vs 1437 (2022) |

### Bloque F — Comparaciones
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| F1 Temporal vs larga | anuncios_unificados.csv | modalidad |
| F2 Oficial vs anuncios | alquiler_municipal_completo.csv | 159 + 93 |
| F3 Periféricos vs capital | analisis_variables_base.csv | tipologia_mercado |
| F4 Álava vs Bizkaia vs Gipuzkoa | analisis_variables_base.csv | comparativa TH |
| F5 Compraventa vs alquiler | municipio_area_funcional_ecvi.csv | 15 áreas funcionales |

### Bloque G — Calidad y limitaciones
| Pregunta | Archivo | Conclusión |
|----------|---------|------------|
| G1 Sin dato alquiler | alquiler_municipal_completo.csv | 93 comarcal |
| G2 n<5 anuncios | anuncios_unificados.csv | no usados en ranking |
| G3 Proxy renta | decision_salario_proxy.md | falacia ecológica |
| G4 Emancipación territorial | eustat_renta_edad.csv | solo CAE |
| G5 Mezcla de años | metodologia.md | 2026 vs 2024 |
| G6 Fuentes no automatizadas | inventario_datos.md | SERPAVI, OSM, Idealista |

---

## 4. Arquitectura del proyecto

```mermaid
flowchart TB
    subgraph Extract
        E[extract/*.py<br/>01-22 + auxiliares]
    end
    subgraph Transform
        T[transform/*.py<br/>grupo A + nuevos]
    end
    subgraph Data
        R[data/raw/<br/>303 archivos<br/>congelado]
        P[data/procesado/<br/>93 archivos silver]
    end
    subgraph Docs
        D[docs/*.md<br/>inventario, trazabilidad<br/>metodologia, decision_proxy]
    end
    subgraph Viz
        V[data/resultados/<br/>8 PNG + dashboard.html]
    end

    E --> R
    R --> T
    T --> P
    P --> V
    P --> D
    R --> D

    style R fill:#e74c3c,color:#fff
    style P fill:#2ecc71,color:#fff
    style V fill:#3498db,color:#fff
```

---

## 5. Leyenda de fuentes

| Abreviatura | Significado |
|-------------|-------------|
| Eustat | Instituto Vasco de Estadística |
| OVJ | Observatorio Vasco de la Juventud (Irekia) |
| Lanbide | Servicio Vasco de Empleo |
| Udalmap | Indicadores municipales Euskadi |
| GTFS | General Transit Feed Specification |
| OSRM | Open Source Routing Machine |
| ECVI | Encuesta de Condiciones de Vida (INE) |
| SERPAVI | Sistema Estatal de Referencia de Precios de Alquiler |

---

## Notas de regeneración

- Este archivo es **texto estático**. Cuando cambien transforms, datos o preguntas, actualizar las tablas y diagramas manualmente.
- Los diagramas Mermaid se renderizan en GitHub, VS Code (extensión), Obsidian o https://mermaid.live
- Para generar PNG estático: `npm install -g @mermaid-js/mermaid-cli` → `mmdc -i docs/mapa_relaciones.md -o mapa_relaciones.png`
PY