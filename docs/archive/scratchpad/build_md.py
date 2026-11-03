import json, os

ROOT="C:/Users/mikel/Documents/bigdata-vivienda-euskadi"
D=json.load(open("C:/Users/mikel/AppData/Local/hermes/cache/scratch/meta_scan2.json",encoding="utf-8"))

def cat_of(rel):
    low=rel.lower()
    name=os.path.basename(rel).lower()
    if "legacy_obsoleto" in low: return "Legacy / obsoleto (no usar)"
    if "html_fotocasa" in low: return "Anuncios (HTML crudo Fotocasa)"
    if "gtfs" in low: return "Geografía y transporte (GTFS)"
    if "shp_euskadi" in low: return "Geografía (shapefile Euskadi)"
    if "procesado" in low:
        if "anuncio" in name: return "Anuncios (transformaciones)"
        if "alquiler" in name: return "Alquiler oficial (transformaciones)"
        if "emancip" in name: return "Complementarios (transformaciones)"
        if any(k in name for k in ["empleo","udalmap","lanbide","paro"]): return "Empleo (transformaciones)"
        if any(k in name for k in ["municip","distancia","geo"]): return "Geografía (transformaciones)"
        return "Transformaciones y control (pipeline)"
    if name.startswith("anuncios_"): return "Anuncios (portales inmobiliarios)"
    if name.startswith("alquiler_"): return "Alquiler oficial (Eustat/territorial)"
    if name.startswith("emal_"): return "Alquiler oficial (EMAL fianzas)"
    if name.startswith("eustat_"): return "Complementarios (Eustat: población, renta, PIB, tenencia)"
    if "ecvi" in name: return "Complementarios (ECVI compraventa)"
    if name.startswith("emancipacion_"): return "Complementarios (emancipación juvenil)"
    if name.startswith("etxebide_"): return "Complementarios (Etxebide vivienda social)"
    if name.startswith("ine_"): return "Complementarios (INE)"
    if name.startswith("serpavi_"): return "Complementarios (SERPAVI renta fiscal)"
    if name.startswith("renta_municipal_"): return "Complementarios (renta municipal derivada)"
    if name.startswith("educacion_") or name.startswith("salud_"): return "Complementarios (servicios)"
    if name.startswith("lanbide_"): return "Empleo (Lanbide)"
    if name.startswith("udalmap_"): return "Empleo (Udalmap)"
    if name.startswith("osrm_"): return "Geografía y accesibilidad (OSRM)"
    if name.startswith("transporte_"): return "Geografía y transporte"
    if name.startswith("dim_municipios") or name.startswith("municipios_") or name.startswith("municipios_euskadi"): return "Geografía (municipios/cartografía)"
    if name.startswith("distancias_"): return "Geografía (distancias)"
    if name.endswith(".log") or name=="manifest_sha256.txt" or name==".gitkeep" or name.endswith(".txt") or name.endswith(".bak_r1"):
        return "Metadatos y control"
    return "Otros / sin categoría"

CAT_ORDER=[
 "Anuncios (portales inmobiliarios)",
 "Anuncios (HTML crudo Fotocasa)",
 "Anuncios (transformaciones)",
 "Alquiler oficial (Eustat/territorial)",
 "Alquiler oficial (EMAL fianzas)",
 "Alquiler oficial (transformaciones)",
 "Complementarios (Eustat: población, renta, PIB, tenencia)",
 "Complementarios (ECVI compraventa)",
 "Complementarios (emancipación juvenil)",
 "Complementarios (Etxebide vivienda social)",
 "Complementarios (INE)",
 "Complementarios (SERPAVI renta fiscal)",
 "Complementarios (renta municipal derivada)",
 "Complementarios (servicios)",
 "Complementarios (transformaciones)",
 "Empleo (Lanbide)",
 "Empleo (Udalmap)",
 "Empleo (transformaciones)",
 "Geografía (municipios/cartografía)",
 "Geografía (distancias)",
 "Geografía y accesibilidad (OSRM)",
 "Geografía y transporte",
 "Geografía (shapefile Euskadi)",
 "Geografía (transformaciones)",
 "Transformaciones y control (pipeline)",
 "Metadatos y control",
 "Legacy / obsoleto (no usar)",
 "Otros / sin categoría",
]

groups={c:[] for c in CAT_ORDER}
for r in D:
    c=cat_of(r["rel"])
    if c not in groups:
        groups[c]=[]
        CAT_ORDER.append(c)
    groups[c].append(r)

def size_str(n):
    if n is None: return "—"
    if n>=1024*1024: return f"{n/1024/1024:.1f} MB"
    if n>=1024: return f"{n/1024:.1f} KB"
    return f"{n} B"

def type_str(r):
    ext=r["ext"]
    m={".csv":"CSV",".json":"JSON",".xlsx":"XLSX",".xls":"XLS",".geojson":"GeoJSON",".html":"HTML",".zip":"ZIP",".shp":"SHP",".dbf":"DBF",".shx":"SHX",".prj":"PRJ",".cpg":"CPG",".log":"Log",".txt":"TXT",".bak_r1":"Backup JSON","":"(sin ext)"}
    base=m.get(ext, ext or "—")
    info=r.get("read_info") or ""
    if ("skiprows=" in info and "skiprows=0" not in info) or "multi-cab" in info:
        base+=" (multi-cab.)"
    if info.startswith("ERR"):
        base+=" (error lectura)"
    return base

def cols_str(r):
    cols=r.get("columns")
    if not cols: return "—"
    if all(str(c).startswith("Unnamed") for c in cols):
        return "Tabla ancha multi-cabecera"
    if cols==["valor"]:
        return "Lista de strings (1 col)"
    s=", ".join(str(c) for c in cols[:6])
    if len(cols)>6:
        s+=" …"
    if len(s)>95:
        s=s[:92]+"…"
    return s

def cov_str(r):
    cov=r.get("coverage") or {}
    if cov:
        items=sorted(cov.items(), key=lambda kv: kv[1].get("coverage",0), reverse=True)
        out=[]
        for k,v in items[:2]:
            if v.get("coverage",0)>0:
                out.append(f"{k}: {v['coverage']}/252")
        if out:
            return "; ".join(out)
    name=r["rel"].lower()
    if "ecvi" in name: return "Territorial (CAE/TH/comarcas)"
    return "—"

def nulls_str(r):
    if r.get("read_info","").startswith("ERR"):
        return f"Error: {r['read_info'][:60]}"
    if r["rows"] is None:
        return "—"
    total=r.get("total_nulls",0) or 0
    nulls=r.get("nulls") or {}
    if total==0:
        nt="Sin nulos"
    else:
        top=sorted(nulls.items(), key=lambda kv: kv[1], reverse=True)[:3]
        nt=f"{total} nulos en {len(nulls)} cols ({', '.join(f'{k}:{v}' for k,v in top)})"
    outs=r.get("outliers_3sd") or {}
    if outs:
        nt+=f"; outliers>3σ: {sum(outs.values())} en {len(outs)} cols"
    else:
        nt+="; sin outliers>3σ"
    return nt

def question(r, cat):
    name=os.path.basename(r["rel"]).lower()
    base={
     "Anuncios (portales inmobiliarios)": "¿Qué oferta de alquiler existe (precio, m², habitaciones) y a qué precio por municipio?",
     "Anuncios (HTML crudo Fotocasa)": "Fuente cruda de scraping Fotocasa (1 página/municipio); alimenta anuncios_fotocasa.",
     "Anuncios (transformaciones)": "¿Cómo se filtran/enriquecen/geolocalizan los anuncios para el análisis?",
     "Alquiler oficial (Eustat/territorial)": "¿Cuál es el alquiler medio oficial por municipio (Eustat 2024)?",
     "Alquiler oficial (EMAL fianzas)": "¿Cuántas fianzas de alquiler se registran (proxy de rotación/mercado)?",
     "Alquiler oficial (transformaciones)": "¿Cómo se completa el alquiler a los 93 municipios sin dato (comarca)?",
     "Complementarios (Eustat: población, renta, PIB, tenencia)": "¿Cuál es la capacidad económica y estructura de hogares por municipio?",
     "Complementarios (ECVI compraventa)": "¿Cómo evoluciona el mercado de compraventa (transacciones, precios)?",
     "Complementarios (emancipación juvenil)": "¿Cuál es la tasa de emancipación juvenil y el coste de acceso?",
     "Complementarios (Etxebide vivienda social)": "¿Cuál es la demanda de vivienda social (solicitudes Etxebide)?",
     "Complementarios (INE)": "¿Qué referencia nacional (población, salarios, atlas renta) complementa el análisis?",
     "Complementarios (SERPAVI renta fiscal)": "¿Cuál es la renta fiscal municipal (SERPAVI/MIVAU)?",
     "Complementarios (renta municipal derivada)": "¿Cómo se completa la renta municipal para análisis?",
     "Complementarios (servicios)": "¿Qué servicios (centros educativos/sanitarios) contextualizan la habitabilidad?",
     "Complementarios (transformaciones)": "¿Cómo se transforman variables complementarias para el modelo?",
     "Empleo (Lanbide)": "¿Cuál es el paro juvenil municipal (Lanbide)?",
     "Empleo (Udalmap)": "¿Qué indicadores de empleo/actividad (Udalmap) hay por municipio?",
     "Empleo (transformaciones)": "¿Cómo se limpian/corrijen los datos de empleo?",
     "Geografía (municipios/cartografía)": "¿Dónde están los municipios y cómo se identifican (dimensión)?",
     "Geografía (distancias)": "¿Qué distancias hay entre municipios/capitales?",
     "Geografía y accesibilidad (OSRM)": "¿Cuántos minutos de conducción a las capitales?",
     "Geografía y transporte": "¿Qué oferta de transporte público hay por municipio?",
     "Geografía (shapefile Euskadi)": "Cartografía municipal (límites, EPSG:25830).",
     "Geografía (transformaciones)": "¿Cómo se generan GeoJSON/distancias para Mongo (2dsphere)?",
     "Transformaciones y control (pipeline)": "Control, rescate y calidad del pipeline de datos.",
     "Metadatos y control": "Control de calidad/manifest/auditoría del pipeline.",
     "Legacy / obsoleto (no usar)": "Histórico obsoleto (no usar).",
     "Otros / sin categoría": "Sin categoría asignada.",
    }.get(cat,"")
    if "salarios" in name: return "¿Cuál es el salario de referencia (EPA nacional) para calcular esfuerzo?"
    if "atlas" in name: return "¿Renta municipal para los 51 municipios faltantes (INE Atlas)?"
    if "pib" in name: return "¿Cuál es el PIB municipal (proxy de actividad)?"
    if "tenencia" in name: return "¿Qué peso tiene el alquiler vs propiedad por municipio?"
    if "poblacion" in name: return "¿Cuántos habitantes/jóvenes hay por municipio?"
    if "renta_edad" in name or "renta_municipal" in name: return "¿Cuál es la renta media municipal (proxy de ingresos)?"
    if "emancipacion" in name: return "¿Cuál es la tasa de emancipación juvenil y el coste de acceso?"
    if "municipios_faltantes" in name: return "¿Qué 93 municipios no tienen alquiler directo?"
    if "f4_pisos" in name: return "¿Scraping dirigido a municipios con n anuncios bajo (Fase 4)?"
    if "r1_" in name: return "¿Rescate de alquiler municipal por comarca (R1)?"
    if "informe_calidad" in name or "informe_entity" in name: return "¿Informe de calidad/consistencia de datos?"
    if name.endswith(".log"): return "Log de ejecución del pipeline."
    if name==".gitkeep": return "Marcador de directorio (sin datos)."
    if name=="manifest_sha256.txt": return "Manifest SHA-256 de verificación (replay-raw)."
    return base

lines=[]
lines.append("# Inventario de datos — bigdata-vivienda-euskadi")
lines.append("")
lines.append("> Generado por inspección automatizada (solo lectura) con pandas sobre `data/raw/`, `data/procesado/` y `data/resultados/`.")
lines.append("> Fecha de inventario: 2026-10-28. Total archivos inventariados: **325**.")
lines.append("")
total_size=sum(r["size"] for r in D)
total_rows=sum(r["rows"] or 0 for r in D)
tab=[r for r in D if r["rows"] is not None]
lines.append("## 1. Resumen ejecutivo")
lines.append("")
lines.append(f"- **Archivos totales:** {len(D)} ({len(tab)} tabulares legibles, {len(D)-len(tab)} no tabulares: HTML, ZIP, shapefile, logs, marcadores).")
lines.append(f"- **Volumen total en disco:** {total_size/1024/1024:.1f} MB (incluye 101 HTML y 13 ZIP GTFS).")
lines.append(f"- **Filas tabulares (suma):** {total_rows:,} (incluye cabeceras múltiples/blancos en ECVI y originales Eustat).")
lines.append("- **Municipios de referencia (dimensión):** 252 (Álava 51 + Bizkaia 112 + Gipuzkoa 88).")
lines.append("- **Alquiler oficial:** 159 municipios con dato directo Eustat 2024; 93 municipios sin dato rescatados por comarca (`alquiler_municipal_completo.csv`, 252/252).")
lines.append("- **Anuncios (oferta):** Fotocasa y Pisos.com; cobertura 60 y 37 municipios respectivamente; RealtyAPI 3 municipios (opcional).")
lines.append("- **ECVI:** 65 CSV + 2 XLSX de compraventa (trimestral, territorial/comarcal, no municipal).")
lines.append("- **GTFS:** 13 ZIP de operadores de transporte público.")
lines.append("- **Shapefile:** 5 componentes (MUNICIPIOS_5000_ETRS89, EPSG:25830).")
lines.append("- **HTML Fotocasa:** 101 páginas (1 por municipio/provincia).")
lines.append("")
lines.append("### Limitaciones principales")
lines.append("- Heterogeneidad de formatos: CSV multi-cabecera (Eustat, ECVI, Etxebide) no parseable estándar; se requiere `skiprows`/limpieza.")
lines.append("- Cobertura parcial de anuncios: Fotocasa 60/252 municipios, Pisos.com 37/252, RealtyAPI 3/252.")
lines.append("- Alquiler oficial: solo 159/252 municipios con dato directo; 93 imputados por comarca (menor precisión).")
lines.append("- ECVI no es municipal (territorial/comarcal) y los CSV son tablas anchas con cabeceras anidadas.")
lines.append("- GTFS y HTML son binarios/texto no tabular; requieren extracción específica.")
lines.append("- Nulos/outliers presentes en varias fuentes (ver columna 'Nulos / outliers').")
lines.append("- `data/resultados/` solo contiene `.gitkeep` (resultados aún no generados).")
lines.append("- Algunos archivos JSON son listas de strings (municipios/códigos), sin columnas tabulares.")
lines.append("")
lines.append("### Volumen por categoría")
lines.append("")
lines.append("| Categoría | Archivos | Filas (suma) | Tamaño (MB) |")
lines.append("|---|---:|---:|---:|")
for c in CAT_ORDER:
    rs=groups.get(c,[])
    if not rs: continue
    lines.append(f"| {c} | {len(rs)} | {sum(r['rows'] or 0 for r in rs):,} | {sum(r['size'] for r in rs)/1024/1024:.1f} |")
lines.append("")
lines.append("## 2. Inventario detallado por categoría")
lines.append("")
lines.append("Columnas de cada tabla: **Archivo** (ruta relativa), **Tipo**, **Tamaño**, **Filas×Cols**, **Columnas principales**, **Cobertura municipal**, **Nulos / outliers**, **Pregunta del proyecto**.")
lines.append("")

for ci,c in enumerate(CAT_ORDER, start=1):
    rs=groups.get(c,[])
    if not rs: continue
    rs_sorted=sorted(rs, key=lambda r: r["rel"])
    lines.append(f"### 2.{ci} {c}")
    lines.append("")
    lines.append(f"_Archivos: {len(rs_sorted)}_")
    lines.append("")
    lines.append("| Archivo | Tipo | Tamaño | Filas×Cols | Columnas principales | Cobertura municipal | Nulos / outliers | Pregunta del proyecto |")
    lines.append("|---|---|---:|---:|---|---|---|---|")
    for r in rs_sorted:
        rows=r["rows"]; cols=r["cols"]
        rc = "—" if rows is None else f"{rows}×{cols}"
        lines.append(f"| `{r['rel']}` | {type_str(r)} | {size_str(r['size'])} | {rc} | {cols_str(r)} | {cov_str(r)} | {nulls_str(r)} | {question(r,c)} |")
    lines.append("")

lines.append("## 3. Esquemas destacados (columnas completas de datasets clave)")
lines.append("")
key_files=[
 "data/raw/dim_municipios.csv",
 "data/raw/alquiler_municipal.csv",
 "data/raw/alquiler_seccion.csv",
 "data/raw/anuncios_fotocasa.csv",
 "data/raw/anuncios_pisos.csv",
 "data/raw/anuncios_realtyapi.csv",
 "data/raw/eustat_renta_municipal.csv",
 "data/raw/eustat_poblacion_edad.csv",
 "data/raw/eustat_pib_municipal.csv",
 "data/raw/eustat_tenencia.csv",
 "data/raw/emancipacion_juventud_resumen.json",
 "data/raw/etxebide_solicitudes.csv",
 "data/raw/udalmap_empleo.csv",
 "data/raw/lanbide_paro_juvenil.csv",
 "data/raw/osrm_tiempos_capitales.csv",
 "data/raw/transporte_paradas_municipio.csv",
 "data/raw/serpavi_renta_municipal.csv",
 "data/raw/educacion_centros.csv",
 "data/raw/salud_centros.csv",
 "data/raw/distancias_capitales_252.csv",
 "data/procesado/alquiler_municipal_completo.csv",
 "data/procesado/analisis_variables_base.csv",
]
idx={r["rel"]:r for r in D}
for kf in key_files:
    r=idx.get(kf)
    if not r or not r.get("columns"):
        continue
    lines.append(f"### `{kf}`")
    lines.append("")
    lines.append(f"- Filas: {r['rows']} | Columnas: {r['cols']} | Nulos totales: {r['total_nulls']}")
    lines.append("- Columnas:")
    for col in r["columns"]:
        lines.append(f"  - `{col}`")
    lines.append("")

lines.append("## 4. Notas de uso")
lines.append("")
lines.append("- Todos los archivos bajo `data/raw/`, `data/procesado/` y `data/resultados/` son datos generados (ignorados por git).")
lines.append("- `data/resultados/` está vacío salvo `.gitkeep` (fases de análisis/visualización pendientes).")
lines.append("- Los archivos `legacy_obsoleto_no_usar/` no deben usarse (versiones anteriores).")
lines.append("- Para verificación de integridad: `extract/main_ingest.py --mode replay-raw` compara SHA-256 con `data/raw/manifest_sha256.txt`.")
lines.append("")

out=os.path.join(ROOT,"docs","inventario_datos.md")
os.makedirs(os.path.dirname(out),exist_ok=True)
with open(out,"w",encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written", out, "chars", sum(len(l) for l in lines))
