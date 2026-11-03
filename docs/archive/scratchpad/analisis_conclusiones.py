import pandas as pd, numpy as np

alq = pd.read_csv('data/raw/alquiler_municipal.csv', dtype=str, encoding='utf-8-sig')
dim = pd.read_csv('data/raw/dim_municipios.csv', dtype=str, encoding='utf-8-sig')
udal = pd.read_csv('data/raw/udalmap_empleo.csv', dtype=str, encoding='utf-8-sig')
lanb = pd.read_csv('data/raw/lanbide_paro_juvenil.csv', dtype=str, encoding='utf-8-sig')
osrm = pd.read_csv('data/raw/osrm_tiempos_capitales.csv', dtype=str, encoding='utf-8-sig')
serp = pd.read_csv('data/raw/serpavi_renta_municipal.csv', dtype=str, encoding='utf-8-sig')
eustat_r = pd.read_csv('data/raw/eustat_renta_municipal.csv', dtype=str, low_memory=False, encoding='utf-8-sig')
ten = pd.read_csv('data/raw/eustat_tenencia.csv', dtype=str, encoding='utf-8-sig')
fot = pd.read_csv('data/raw/anuncios_fotocasa.csv', dtype=str, encoding='utf-8-sig')

rm = eustat_r[eustat_r['ámbitos territoriales'].astype(str).str.len().isin([4,5])]
rm = rm[rm['ámbitos territoriales'].astype(str).str[:2].isin(['01','20','48'])]
rm = rm[rm['tipo de renta__etiqueta']=='Renta disponible']
rm = rm[rm['sexo__etiqueta']=='Total']
latest = rm['periodo'].max()
rm = rm[rm['periodo']==latest][['ámbitos territoriales','Renta personal media de la C.A. de Euskadi (euros)']]
rm.columns=['codigo_ine','renta_media']
rm['codigo_ine']=rm['codigo_ine'].str.zfill(5)
rm['renta_media']=pd.to_numeric(rm['renta_media'],errors='coerce')

a = alq[['codigo_ine','renta_media_eur_m2_mediana','cuantia_media_eur_mes_mediana']].copy()
a['codigo_ine']=a['codigo_ine'].str.zfill(5)
a['renta_alq']=pd.to_numeric(a['renta_media_eur_m2_mediana'],errors='coerce')
a = a.drop_duplicates('codigo_ine', keep='first')

df = dim.merge(a[['codigo_ine','renta_alq']],on='codigo_ine',how='left')
df = df.merge(rm,on='codigo_ine',how='left')
df = df.merge(udal[['codigo_ine','tasa_paro_lanbide_pct','tasa_actividad_pct','renta_familiar_eur']],on='codigo_ine',how='left')
df = df.merge(lanb[['codigo_ine','tasa_paro_joven_pct','paro_joven_menores_25']],on='codigo_ine',how='left')
df = df.merge(osrm[['codigo_ine','minutos_Bilbao','minutos_Vitoria-Gasteiz','minutos_Donostia-San Sebastian']],on='codigo_ine',how='left')

df['renta_anual']=pd.to_numeric(df['renta_media'],errors='coerce')
df['renta_mensual']=df['renta_anual']/12
df['alq_mensual']=pd.to_numeric(df['renta_alq'],errors='coerce')*60
df['esfuerzo_pct']=df['alq_mensual']/df['renta_mensual']*100

print("=== TOP 15 MUNICIPIOS: ALQUILER BAJO + PARO BAJO + ACCESIBLE ===")
sub = df[df['renta_alq'].notna()].copy()
sub['paro']=pd.to_numeric(sub['tasa_paro_lanbide_pct'],errors='coerce')
sub['min_bilbao']=pd.to_numeric(sub['minutos_Bilbao'],errors='coerce')
sub['score']=sub['renta_alq'].rank(ascending=True)+sub['paro'].rank(ascending=True)+sub['min_bilbao'].rank(ascending=True)
top = sub.sort_values('score').head(15)
print(top[['codigo_ine','nombre_canonico','territorio','renta_alq','paro','minutos_Bilbao','esfuerzo_pct','tipologia_mercado']].to_string(index=False))

print("\n=== DISTRIBUCION TIPOLOGIA ===")
print(df['tipologia_mercado'].value_counts().to_string())

print("\n=== NIVEL 1 (n>=30 anuncios) ===")
print(df[df['tipologia_mercado']=='Nivel1_Mercado_Dinamico'][['codigo_ine','nombre_canonico','renta_alq','tasa_paro_lanbide_pct','tipologia_mercado']].to_string(index=False))

print("\n=== PARO JUVENIL TOP 10 MAS BAJO ===")
lj = lanb.copy()
lj['paro_j']=pd.to_numeric(lj['tasa_paro_joven_pct'],errors='coerce')
lj = lj.merge(dim[['codigo_ine','nombre_canonico']],on='codigo_ine',how='left')
print(lj.sort_values('paro_j').head(10)[['codigo_ine','nombre_canonico','paro_joven_menores_25','tasa_paro_joven_pct']].to_string(index=False))

print("\n=== PARO JUVENIL TOP 10 MAS ALTO ===")
print(lj.sort_values('paro_j',ascending=False).head(10)[['codigo_ine','nombre_canonico','paro_joven_menores_25','tasa_paro_joven_pct']].to_string(index=False))

print("\n=== SERPAVI vs OFICIAL correlacion ===")
s = serp.copy()
s['codigo_ine']=s['codigo_ine'].str.zfill(5)
s['r']=pd.to_numeric(s['renta_m2_mes_eur'],errors='coerce')
m = s.merge(a[['codigo_ine','renta_alq']],on='codigo_ine')
print("n:",len(m),"corr:",round(m['r'].corr(m['renta_alq']),3))

print("\n=== SIN OFICIAL con SERPAVI? ===")
sin_oficial = set(dim['codigo_ine']) - set(a['codigo_ine'])
serp_ok = set(s[s['metodo']!='sin_dato']['codigo_ine'])
print("sin oficial:",len(sin_oficial),"con SERPAVI:",len(sin_oficial & serp_ok))

print("\n=== EDUCACION/SALUD ===")
edu = pd.read_csv('data/raw/educacion_centros.csv',dtype=str,encoding='utf-8-sig')
sal = pd.read_csv('data/raw/salud_centros.csv',dtype=str,encoding='utf-8-sig')
print("educacion munis:",edu['codigo_ine'].nunique(),"salud munis:",sal['codigo_ine'].nunique())

print("\n=== RESUMEN ===")
print("municipios con alquiler oficial:",df['renta_alq'].notna().sum())
print("municipios con renta municipal:",df['renta_media'].notna().sum())
print("municipios con paro juvenil:",df['tasa_paro_joven_pct'].notna().sum())
print("municipios con OSRM bilbao:",df['minutos_Bilbao'].notna().sum())
print("esfuerzo medio %:",round(df['esfuerzo_pct'].mean(),1))
print("esfuerzo mediana %:",round(df['esfuerzo_pct'].median(),1))
print("esfuerzo min %:",round(df['esfuerzo_pct'].min(),1))
print("esfuerzo max %:",round(df['esfuerzo_pct'].max(),1))
PY