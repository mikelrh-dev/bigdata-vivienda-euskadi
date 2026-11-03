import pandas as pd, numpy as np

alq = pd.read_csv('data/raw/alquiler_municipal.csv', dtype=str, encoding='utf-8-sig')
dim = pd.read_csv('data/raw/dim_municipios.csv', dtype=str, encoding='utf-8-sig')
udal = pd.read_csv('data/raw/udalmap_empleo.csv', dtype=str, encoding='utf-8-sig')
lanb = pd.read_csv('data/raw/lanbide_paro_juvenil.csv', dtype=str, encoding='utf-8-sig')
osrm = pd.read_csv('data/raw/osrm_tiempos_capitales.csv', dtype=str, encoding='utf-8-sig')
eustat_r = pd.read_csv('data/raw/eustat_renta_municipal.csv', dtype=str, low_memory=False, encoding='utf-8-sig')
serp = pd.read_csv('data/raw/serpavi_renta_municipal.csv', dtype=str, encoding='utf-8-sig')

a = alq[['codigo_ine','renta_media_eur_m2_mediana']].copy()
a['codigo_ine']=a['codigo_ine'].str.zfill(5)
a['renta_alq']=pd.to_numeric(a['renta_media_eur_m2_mediana'],errors='coerce')
a = a.drop_duplicates('codigo_ine', keep='first')

rm = eustat_r[eustat_r['ámbitos territoriales'].astype(str).str.len().isin([4,5])]
rm = rm[rm['ámbitos territoriales'].astype(str).str[:2].isin(['01','20','48'])]
rm = rm[rm['tipo de renta__etiqueta']=='Renta disponible']
rm = rm[rm['sexo__etiqueta']=='Total']
rm = rm[rm['periodo']==rm['periodo'].max()][['ámbitos territoriales','Renta personal media de la C.A. de Euskadi (euros)']]
rm.columns=['codigo_ine','renta_disp']
rm['codigo_ine']=rm['codigo_ine'].str.zfill(5)
rm['renta_disp']=pd.to_numeric(rm['renta_disp'],errors='coerce')

df = dim.merge(a[['codigo_ine','renta_alq']],on='codigo_ine',how='left')
df = df.merge(rm,on='codigo_ine',how='left')
df = df.merge(udal[['codigo_ine','tasa_paro_lanbide_pct']],on='codigo_ine',how='left')
df = df.merge(lanb[['codigo_ine','tasa_paro_joven_pct']],on='codigo_ine',how='left')
df = df.merge(osrm[['codigo_ine','minutos_Bilbao','minutos_Vitoria-Gasteiz','minutos_Donostia-San Sebastian']],on='codigo_ine',how='left')

df['renta_alq']=pd.to_numeric(df['renta_alq'],errors='coerce')
df['renta_disp']=pd.to_numeric(df['renta_disp'],errors='coerce')
df['renta_mensual']=df['renta_disp']/12
df['alq_60m2']=df['renta_alq']*60
df['esfuerzo_pct']=df['alq_60m2']/df['renta_mensual']*100

print("=== ESFUERZO POR NIVEL 1 (capitales/comarcas con alquiler) ===")
n1 = df[df['tipologia_mercado']=='Nivel1_Mercado_Dinamico']
print(n1[['codigo_ine','nombre_canonico','renta_alq','renta_disp','esfuerzo_pct','tasa_paro_lanbide_pct','tasa_paro_joven_pct']].to_string(index=False))

print("\n=== DISTRIBUCION ESFUERZO (159 munis con dato) ===")
e = df['esfuerzo_pct'].dropna()
print("n:",len(e))
print("min/max/mean/median:", round(e.min(),1), round(e.max(),1), round(e.mean(),1), round(e.median(),1))
print("municipios con esfuerzo >40%:", (e>40).sum())
print("municipios con esfuerzo >30%:", (e>30).sum())
print("municipios con esfuerzo <25%:", (e<25).sum())

print("\n=== ESFUERZO POR TERRITORIO (media) ===")
print(df.groupby('territorio')['esfuerzo_pct'].agg(['count','mean','median','min','max']).round(1).to_string())

print("\n=== TOP 10 MAYOR ESFUERZO ===")
print(df.sort_values('esfuerzo_pct',ascending=False).head(10)[['codigo_ine','nombre_canonico','territorio','renta_alq','renta_disp','esfuerzo_pct']].to_string(index=False))

print("\n=== TOP 10 MENOR ESFUERZO ===")
print(df.sort_values('esfuerzo_pct').head(10)[['codigo_ine','nombre_canonico','territorio','renta_alq','renta_disp','esfuerzo_pct']].to_string(index=False))

print("\n=== EUSTAT renta disponible: rango ===")
print("min/max/mean renta_disp:", round(df['renta_disp'].min(),0), round(df['renta_disp'].max(),0), round(df['renta_disp'].mean(),0))
print("n con dato:", df['renta_disp'].notna().sum())

print("\n=== PARO JUVENIL: cuantos municipios con 0%? ===")
lj = pd.to_numeric(df['tasa_paro_joven_pct'],errors='coerce')
print("munis con paro_joven=0:", (lj==0).sum())
print("munis con paro_joven>0:", (lj>0).sum())
print("munis con paro_joven NaN:", lj.isna().sum())
# cuantos jovenes parados en total
lanb2 = pd.read_csv('data/raw/lanbide_paro_juvenil.csv', dtype=str, encoding='utf-8-sig')
lanb2['pj']=pd.to_numeric(lanb2['paro_joven_menores_25'],errors='coerce')
print("total paro joven:", lanb2['pj'].sum())
print("municipios con paro_joven>50:", (lanb2['pj']>50).sum())

print("\n=== EIBAR/DURANGO/TOLOSA en datos? ===")
for name in ['Eibar','Durango','Tolosa']:
    r = df[df['nombre_canonico'].str.contains(name,case=False,na=False)]
    print(r[['codigo_ine','nombre_canonico','renta_alq','esfuerzo_pct','tasa_paro_lanbide_pct','minutos_Bilbao','minutos_Donostia-San Sebastian']].to_string(index=False) if len(r) else name+" NO ENCONTRADO")

print("\n=== OSRM: tiempo medio a capital mas cercana ===")
df['min_bilbao']=pd.to_numeric(df['minutos_Bilbao'],errors='coerce')
df['min_vitoria']=pd.to_numeric(df['minutos_Vitoria-Gasteiz'],errors='coerce')
df['min_donostia']=pd.to_numeric(df['minutos_Donostia-San Sebastian'],errors='coerce')
df['min_capital']=df[['min_bilbao','min_vitoria','min_donostia']].min(axis=1)
print("min a capital: mean/median/max:", round(df['min_capital'].mean(),1), round(df['min_capital'].median(),1), round(df['min_capital'].max(),1))
print("munis >60min de cualquier capital:", (df['min_capital']>60).sum())
print("munis >45min:", (df['min_capital']>45).sum())

print("\n=== ETXEBIDE data? ===")
import os
print("files etxebide:", [f for f in os.listdir('data/raw') if 'etxeb' in f.lower() or 'bizilagun' in f.lower()])

print("\n=== TENENCIA (vivienda vacia) sample ===")
ten = pd.read_csv('data/raw/eustat_tenencia.csv', dtype=str, encoding='utf-8-sig')
print("cols:", list(ten.columns)[:8])
print("regimen unique:", ten.iloc[:,2].unique()[:10] if ten.shape[1]>2 else 'n/a')
PY