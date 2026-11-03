import pandas as pd, numpy as np, json, os, glob

BASE='data/raw'
DIM=pd.read_csv(os.path.join(BASE,'dim_municipios.csv'))
DIM_CODES=set(str(x).zfill(5) for x in DIM['codigo_ine'])
def norm(s):
    s=str(s).strip().lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]:
        s=s.replace(a,b)
    return s
DIM_NORM={norm(x):x for x in DIM['nombre_canonico']}
# variant map
VARMAP={}
for _,r in DIM.iterrows():
    VARMAP[norm(r['nombre_canonico'])]=r['nombre_canonico']
    for v in str(r['variantes']).split(','):
        VARMAP[norm(v)]=r['nombre_canonico']

def valid_code(x):
    if pd.isna(x): return False
    try:
        i=int(float(x))
        s=str(i).zfill(5)
        return len(s)==5 and s in DIM_CODES
    except: return False

def iqr_outliers(series):
    s=series.dropna()
    q1=s.quantile(0.25); q3=s.quantile(0.75); iqr=q3-q1
    hi=q3+1.5*iqr; lo=q1-1.5*iqr
    out=s[(s>hi)|(s<lo)]
    return len(out), float(lo), float(hi), float(s.min()) if len(s) else None, float(s.max()) if len(s) else None

print('='*80)
print('INVENTARIO REAL (FASE 0)')
print('='*80)
fot=pd.read_csv(os.path.join(BASE,'anuncios_fotocasa.csv'))
pis=pd.read_csv(os.path.join(BASE,'anuncios_pisos.csv'))
rea=pd.read_csv(os.path.join(BASE,'anuncios_realtyapi.csv'))
alq=pd.read_csv(os.path.join(BASE,'alquiler_municipal.csv'))
print('dim_municipios:', DIM.shape, 'territorios:', DIM['territorio'].value_counts().to_dict())

for name,df in [('fotocasa',fot),('pisos',pis),('realtyapi',rea)]:
    print('\n---',name,'---')
    print('rows',len(df))
    if 'codigo_ine' in df.columns:
        vc=df['codigo_ine'].apply(valid_code)
        print('codigo_ine valid %', round(100*vc.mean(),2), 'n_valid', int(vc.sum()))
    if name=='fotocasa':
        mcol='municipio'
    elif name=='pisos':
        mcol='municipio_busqueda' if 'municipio_busqueda' in df.columns else 'municipio'
    else:
        mcol='municipio'
    # precio_m2
    if 'precio_eur' in df.columns and 'superficie_m2' in df.columns:
        pm=df['precio_eur']/df['superficie_m2']
        valid_price = (df['precio_eur']>0) & (df['superficie_m2'].between(10,600)) & df['superficie_m2'].notna()
        print('valid price+superficie(10-600):', int(valid_price.sum()), 'muns:', df.loc[valid_price,mcol].nunique() if mcol in df.columns else None)
        print('superficie null %', round(100*df['superficie_m2'].isna().mean(),2))
        if 'habitaciones' in df.columns:
            sup_ok = df['superficie_m2'].between(15,300) & df['superficie_m2'].notna()
            hab_ok = df['habitaciones'].notna()
            print('sup 15-300 & hab notnull %', round(100*(sup_ok & hab_ok).mean(),2), 'n', int((sup_ok & hab_ok).sum()))
    if mcol in df.columns:
        counts=df.groupby(mcol).size()
        print('municipios unicos', df[mcol].nunique())
        print('n>=30:', int((counts>=30).sum()), 'n 5-29:', int(((counts>=5)&(counts<30)).sum()), 'n<5:', int((counts<5).sum()))

print('\n--- alquiler_municipal ---')
print('rows',len(alq),'municipios',alq['municipio'].nunique())
print('distritos por municipio describe:')
print(alq.groupby('municipio').size().describe())
print('codigo_ine present:', 'codigo_ine' in alq.columns)

print('\n'+'='*80)
print('ENTITY RESOLUTION (FASE 1)')
print('='*80)
for name,df,mcol in [('fotocasa',fot,'municipio'),('pisos',pis,'municipio_busqueda'),('realtyapi',rea,'municipio')]:
    if 'codigo_ine' in df.columns:
        vc=df['codigo_ine'].apply(valid_code)
        print(name,'codigo_ine valid %', round(100*vc.mean(),2))
# variantes fotocasa
fot_var=set(fot['municipio'].unique())-set(DIM['nombre_canonico'].unique())
print('fotocasa municipio values not canonical:', len(fot_var))
print(sorted(list(fot_var))[:10])
# realtyapi municipio variant
rea_var=set(rea['municipio'].unique())-set(DIM['nombre_canonico'].unique())
print('realtyapi municipio not canonical:', sorted(list(rea_var))[:10])
# alquiler match
alq_mun=set(norm(x) for x in alq['municipio'].unique())
dim_norm=set(norm(x) for x in DIM['nombre_canonico'].unique())
print('alquiler distinct', len(alq_mun), 'matched', len(alq_mun & dim_norm), 'unmatched', len(alq_mun-dim_norm))
# eustat
renta=pd.read_csv(os.path.join(BASE,'eustat_renta_municipal.csv'), low_memory=False)
renta['codigo']=renta['ámbitos territoriales'].astype(str).str.strip()
mun_renta=renta[renta['codigo'].str.match(r'^\d{5}$')]
print('eustat ambitos unicos total', renta['ámbitos territoriales__etiqueta'].nunique())
print('eustat 5-digit ambitos', mun_renta['ámbitos territoriales__etiqueta'].nunique())
print('eustat non-5-digit ambitos', renta['ámbitos territoriales__etiqueta'].nunique()-mun_renta['ámbitos territoriales__etiqueta'].nunique())
# filter 2024 renta total total
rr=mun_renta[(mun_renta['periodo']==mun_renta['periodo'].max()) & (mun_renta['tipo de renta__etiqueta']=='Renta total') & (mun_renta['sexo__etiqueta']=='Total')]
print('eustat renta 2024 municipios', rr['ámbitos territoriales__etiqueta'].nunique())

print('\n'+'='*80)
print('COBERTURA MUESTRAL (FASE 2)')
print('='*80)
# counts combined
for name,df,mcol in [('fotocasa',fot,'municipio'),('pisos',pis,'municipio_busqueda'),('realtyapi',rea,'municipio')]:
    c=df.groupby(mcol).size()
    print(name,'muns',df[mcol].nunique(),'min',c.min(),'max',c.max())
# fotocasa temporal
if 'alquiler_temporal' in fot.columns:
    fot['pm2']=fot['precio_eur']/fot['superficie_m2']
    tmp=fot[fot['alquiler_temporal']==True]
    lng=fot[fot['alquiler_temporal']==False]
    print('fotocasa temporal n',len(tmp),'mean pm2',round(tmp['pm2'].mean(),2))
    print('fotocasa larga n',len(lng),'mean pm2',round(lng['pm2'].mean(),2))
# combined anuncios per municipality (long-term + temporal valid pm2)
valid_fot=fot[(fot['precio_eur']>0)&(fot['superficie_m2'].between(10,600))]
valid_pis=pis[(pis['precio_eur']>0)&(pis['superficie_m2'].between(10,600))]
print('combined valid listings:', len(valid_fot)+len(valid_pis), 'muns:', pd.concat([valid_fot['municipio'], valid_pis['municipio_busqueda']]).nunique())
# alquiler n muestral?
print('alquiler columns:', list(alq.columns))
print('alquiler has n_contratos:', any('n' in c.lower() or 'contrat' in c.lower() for c in alq.columns))

print('\n'+'='*80)
print('CALIDAD ESTADISTICA (FASE 3)')
print('='*80)
for name,df in [('fotocasa',fot),('pisos',pis),('realtyapi',rea)]:
    if 'precio_eur' in df and 'superficie_m2' in df:
        pm=(df['precio_eur']/df['superficie_m2'])
        pm=pm.replace([np.inf,-np.inf],np.nan).dropna()
        n,lo,hi,mn,mx=iqr_outliers(pm)
        print(name,'pm2 n',len(pm),'mean',round(pm.mean(),2),'median',round(pm.median(),2),'min',round(pm.min(),2),'max',round(pm.max(),2),'outliers',n,'bounds',round(lo,2),round(hi,2))
# superficie valida
for name,df in [('fotocasa',fot),('pisos',pis),('realtyapi',rea)]:
    if 'superficie_m2' in df.columns:
        sup_ok=df['superficie_m2'].between(15,300) & df['superficie_m2'].notna()
        hab_ok=df['habitaciones'].notna() if 'habitaciones' in df.columns else pd.Series([False]*len(df))
        print(name,'sup 15-300 & hab notnull %', round(100*(sup_ok & hab_ok).mean(),2), 'n', int((sup_ok & hab_ok).sum()), 'of', len(df))
# correlacion renta vs alquiler
# aggregate alquiler per municipio mean pm2
alq['pm2']=alq['renta_media_eur_m2_media']
agg=alq.groupby('municipio', as_index=False)['pm2'].mean()
# map to dim norm
agg['norm']=agg['municipio'].map(norm)
rr2=rr.copy()
rr2['norm']=rr2['ámbitos territoriales__etiqueta'].map(norm)
merged=agg.merge(rr2[['norm','Renta personal media de la C.A. de Euskadi (euros)']], on='norm', how='inner')
print('renta vs alquiler merged n', len(merged))
print('pearson r', round(merged['pm2'].corr(merged['Renta personal media de la C.A. de Euskadi (euros)']),3))
# emancipacion parse
em=pd.read_csv(os.path.join(BASE,'emancipacion_juventud.csv'), delimiter=';', quotechar='"')
print('emancipacion shape', em.shape, 'indicadores', em['Indicador'].nunique())

print('\n'+'='*80)
print('VALIDEZ DOMINIO (FASE 4)')
print('='*80)
ud=pd.read_csv(os.path.join(BASE,'udalmap_empleo.csv'))
for col in ['tasa_actividad_pct','tasa_ocupacion_pct','tasa_paro_lanbide_pct','tasa_paro_aprox_pct']:
    if col in ud.columns:
        s=ud[col]
        print(col,'min',s.min(),'max',s.max(),'null',int(s.isna().sum()),'mean',round(s.mean(),2) if s.notna().any() else None)
print('udalmap rows',len(ud),'muns',ud['codigo_ine'].nunique())
# distancias
cap=pd.read_csv(os.path.join(BASE,'distancias_capitales.csv'))
cap252=pd.read_csv(os.path.join(BASE,'distancias_capitales_252.csv'))
hav=pd.read_csv(os.path.join(BASE,'distancias_haversine_252.csv'))
print('capitales 259 dup codigo', int(cap['codigo_ine'].duplicated().sum()))
print('capitales 252 rows', len(cap252))
print('haversine rows', len(hav), 'NaN', int(hav['km_haversine'].isna().sum()), 'origenes', hav['origen_codigo'].nunique())
# distancias_municipios.json
dm=json.load(open(os.path.join(BASE,'distancias_municipios.json')))
print('distancias_municipios.json len', len(dm) if hasattr(dm,'__len__') else dm)
# salarios
sal=pd.read_csv(os.path.join(BASE,'ine_salarios_edad.csv'))
print('salarios ambito unique', list(sal['ambito'].unique()) if 'ambito' in sal.columns else None)
print('salarios shape', sal.shape)
# geojson
gj=json.load(open(os.path.join(BASE,'municipios_euskadi.geojson')))
gd=gj['datos']
print('geojson features', len(gd['features']), 'crs', gd['crs'])

print('\n'+'='*80)
print('MODULO A')
print('='*80)
print('html_fotocasa files', len(glob.glob(os.path.join(BASE,'html_fotocasa','*.html'))))
print('pisos superficie non-null %', round(100*pis['superficie_m2'].notna().mean(),2), 'n', int(pis['superficie_m2'].notna().sum()))
print('fotocasa superficie non-null %', round(100*fot['superficie_m2'].notna().mean(),2))
print('realtyapi superficie non-null %', round(100*rea['superficie_m2'].notna().mean(),2))
# tests
print('\n'+'='*80)
print('PYTEST')
print('='*80)