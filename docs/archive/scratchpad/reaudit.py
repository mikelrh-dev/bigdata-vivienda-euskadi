import json, pandas as pd, os
BASE='data/raw'
PROC='data/procesado'
print("CWD check done")

# dim municipios
dim=pd.read_csv(f'{BASE}/dim_municipios.csv')
print("dim_municipios rows", len(dim), "unique codigo_ine", dim['codigo_ine'].nunique() if 'codigo_ine' in dim else 'NA')
print("dim cols", list(dim.columns)[:10])

# anuncios raw
for f in ['anuncios_fotocasa.csv','anuncios_pisos.csv','anuncios_realtyapi.csv']:
    p=f'{BASE}/{f}'
    if os.path.exists(p):
        df=pd.read_csv(p)
        print(f, "rows", len(df), "cols", list(df.columns)[:15])
    else:
        print(f, "MISSING")

print("\n--- anuncios_unificados ---")
if os.path.exists(f'{PROC}/anuncios_unificados.csv'):
    au=pd.read_csv(f'{PROC}/anuncios_unificados.csv', dtype={'codigo_ine':str})
    print("shape", au.shape)
    print("portal counts:\n", au['portal'].value_counts() if 'portal' in au else au.get('fuente'))
    print("codigo_ine nulls", au['codigo_ine'].isna().sum() if 'codigo_ine' in au else 'NA')
    print("codigo_ine nunique", au['codigo_ine'].nunique())
    # valid price/m2
    if 'precio_eur_m2' in au.columns:
        valid=au[au['precio_eur_m2'].notna() & (au['precio_eur_m2']>0)]
    elif 'precio_eur' in au and 'superficie_m2' in au:
        au['pm2']=au['precio_eur']/au['superficie_m2']
        valid=au[au['pm2'].notna() & (au['pm2']>0) & au['superficie_m2'].notna() & (au['superficie_m2']>0)]
    print("valid pm2 rows", len(valid))
    # per municipality counts
    col_mun='municipio' if 'municipio' in au.columns else None
    print("mun col", col_mun)
    counts=valid.groupby('codigo_ine').size() if 'codigo_ine' in valid.columns else valid.groupby(col_mun).size()
    print("municipios with any valid", counts.shape[0])
    print(">=30:", (counts>=30).sum(), " 10-29:", ((counts>=10)&(counts<30)).sum(), " 5-9:", ((counts>=5)&(counts<10)).sum(), " <5:", (counts<5).sum())
    print("top10 counts:\n", counts.sort_values(ascending=False).head(10).to_string())
    # superficie/habitaciones completeness
    print("superficie notnull", au['superficie_m2'].notna().sum() if 'superficie_m2' in au else 'NA', "of", len(au))
    print("habitaciones notnull", au['habitaciones'].notna().sum() if 'habitaciones' in au else 'NA')
    print("modalidad counts:\n", au['modalidad'].value_counts() if 'modalidad' in au else 'NA')
    print("columns", list(au.columns))
else:
    print("no unificado")

print("\n--- fotocasa raw ---")
fot=pd.read_csv(f'{BASE}/anuncios_fotocasa.csv')
print("fotocasa rows", len(fot), "mun", fot['municipio'].nunique())
print("cols", list(fot.columns))
print("superficie notnull", fot['superficie_m2'].notna().sum() if 'superficie_m2' in fot else 'NA')
print("habitaciones notnull", fot['habitaciones'].notna().sum() if 'habitaciones' in fot else 'NA')
# modalidad/temporal
print(fot.columns.tolist())
# temporal flag
for c in fot.columns:
    if 'temp' in c.lower() or 'modal' in c.lower() or 'tipo' in c.lower():
        print(c, fot[c].value_counts().to_dict())

print("\n--- pisos raw ---")
pis=pd.read_csv(f'{BASE}/anuncios_pisos.csv')
print("pisos rows", len(pis), "mun", pis['municipio'].nunique() if 'municipio' in pis else pis.get('municipio_busqueda').nunique())
print("cols", list(pis.columns))

print("\n--- realtyapi raw ---")
rea=pd.read_csv(f'{BASE}/anuncios_realtyapi.csv')
print("realty rows", len(rea), "mun", rea['municipio'].nunique() if 'municipio' in rea else 'NA')
print("cols", list(rea.columns))

print("\n--- alquiler municipal ---")
alq=pd.read_csv(f'{BASE}/alquiler_municipal.csv')
print("alq rows", len(alq), "mun", alq['municipio'].nunique())
print("cols", list(alq.columns))
# completo
if os.path.exists(f'{PROC}/alquiler_municipal_completo.csv'):
    alc=pd.read_csv(f'{PROC}/alquiler_municipal_completo.csv', dtype={'codigo_ine':str})
    print("completo shape", alc.shape, "cols", list(alc.columns)[:20])
    print("metodo counts", alc['metodo_imputacion'].value_counts().to_dict() if 'metodo_imputacion' in alc else 'NA')

print("\n--- renta ---")
renta=pd.read_csv(f'{BASE}/eustat_renta_municipal.csv')
print("eustat renta rows", len(renta), "ambitos unicos", renta['ámbitos territoriales__etiqueta'].nunique() if 'ámbitos territoriales__etiqueta' in renta else 'NA')
# filter municipality-level: 5-digit ambito code?
print("sample ambito code", renta['ámbitos territoriales__código'].head().tolist() if 'ámbitos territoriales__código' in renta else 'NA')
# how many 5-digit?
if 'ámbitos territoriales__código' in renta:
    code=renta['ámbitos territoriales__código'].astype(str)
    print("codes len5", (code.str.len()==5).sum(), "total", len(code))
    print("unique len5", code[code.str.len()==5].nunique())
# renta completa
if os.path.exists(f'{PROC}/renta_municipal_completa.csv') or os.path.exists(f'{BASE}/renta_municipal_completa.csv'):
    for p in [f'{PROC}/renta_municipal_completa.csv', f'{BASE}/renta_municipal_completa.csv']:
        if os.path.exists(p):
            rmc=pd.read_csv(p, dtype={'codigo_ine':str})
            print("renta_completa", p, rmc.shape, list(rmc.columns)[:15])
# serpavi
if os.path.exists(f'{BASE}/serpavi_renta_municipal.csv'):
    ser=pd.read_csv(f'{BASE}/serpavi_renta_municipal.csv')
    print("serpavi rows", len(ser), "cols", list(ser.columns)[:15], "mun", ser.iloc[:,0].nunique() if len(ser) else 0)
# renta referencia
if os.path.exists(f'{BASE}/renta_municipal_referencia.csv'):
    ref=pd.read_csv(f'{BASE}/renta_municipal_referencia.csv')
    print("renta_ref rows", len(ref), "cols", list(ref.columns)[:15])

print("\n--- paro/empleo ---")
ud=pd.read_csv(f'{BASE}/udalmap_empleo.csv')
print("udalmap rows", len(ud), "cols", list(ud.columns))
print("tasa_paro describe:\n", ud['tasa_paro_aprox_pct'].describe() if 'tasa_paro_aprox_pct' in ud else 'NA')
print("neg paro count", (ud['tasa_paro_aprox_pct']<0).sum() if 'tasa_paro_aprox_pct' in ud else 'NA')
# corregido
uc=pd.read_csv(f'{BASE}/udalmap_empleo_corregido.csv')
print("corregido rows", len(uc), "cols", list(uc.columns))
# any new tasa
for c in uc.columns:
    if 'paro' in c.lower() or 'desempleo' in c.lower() or 'tasa' in c.lower():
        print("COL", c, "nulls", uc[c].isna().sum(), "min", uc[c].min(), "max", uc[c].max())
# dim enriquecido
for p in [f'{PROC}/dim_municipios_enriquecido.csv', f'{BASE}/dim_municipios_enriquecido.csv']:
    if os.path.exists(p):
        de=pd.read_csv(p, dtype={'codigo_ine':str})
        print("dim_enr", p, de.shape)
        for c in de.columns:
            if 'desempleo' in c.lower() or 'paro' in c.lower() or 'tasa' in c.lower():
                print("  ", c, "nulls", de[c].isna().sum(), "min", de[c].min(), "max", de[c].max())

print("\n--- GTFS ---")
gt=pd.read_csv(f'{BASE}/transporte_paradas_municipio.csv')
print("gtfs rows", len(gt), "cols", list(gt.columns))
print("nulls:\n", gt.isna().sum().to_dict())
# paradas por 1000 hab?
for c in gt.columns:
    if 'parada' in c.lower() or '1000' in c.lower() or 'hab' in c.lower():
        print(c, gt[c].describe().to_dict())
# gtfs dir
print("gtfs dir files", os.listdir(f'{BASE}/gtfs')[:10])
# municipios geojson
import json
mj=json.load(open(f'{BASE}/municipios_euskadi.geojson'))
print("geojson features", len(mj.get('features',[])), "crs", mj.get('crs'))
print("geojson properties sample", list(mj['features'][0]['properties'].keys()) if mj.get('features') else 'NA')

print("\n--- distancias ---")
dc=pd.read_csv(f'{BASE}/distancias_capitales.csv')
print("dist_capitales rows", len(dc), "cols", list(dc.columns), "mun", dc.iloc[:,0].nunique() if len(dc) else 0)
dc2=pd.read_csv(f'{BASE}/distancias_capitales_252.csv')
print("dist_capitales_252 rows", len(dc2), "cols", list(dc2.columns))
dh=pd.read_csv(f'{BASE}/distancias_haversine_252.csv')
print("haversine rows", len(dh), "cols", list(dh.columns))
print("haversine nulls", dh.isna().sum().to_dict())
osrm=pd.read_csv(f'{BASE}/osrm_tiempos_capitales.csv')
print("osrm rows", len(osrm), "cols", list(osrm.columns))
# json distancias
dj=json.load(open(f'{BASE}/distancias_municipios.json'))
print("dist_municipios.json len", len(dj), type(dj))
if isinstance(dj, dict):
    print("keys sample", list(dj.keys())[:5])
    # count pairs?
    total=0
    for k,v in list(dj.items())[:3]:
        print(k, type(v), (len(v) if hasattr(v,'__len__') else v))
# zip
print("zip exists", os.path.exists(f'{BASE}/distancias_municipios.zip'))

print("\n--- html_fotocasa ---")
hp=f'{BASE}/html_fotocasa'
print("html_fotocasa exists", os.path.isdir(hp), "count", len(os.listdir(hp)) if os.path.isdir(hp) else 0)

print("\n--- tests ---")
PY