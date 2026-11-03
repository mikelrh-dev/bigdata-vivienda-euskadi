import pandas as pd, os, json
BASE='data/raw'; PROC='data/procesado'
# raw fotocasa
fot=pd.read_csv(f'{BASE}/anuncios_fotocasa.csv')
print("FOTOCASA raw rows",len(fot),"mun",fot['municipio'].nunique())
print("  superficie notnull",fot['superficie_m2'].notna().sum(),"habitaciones notnull",fot['habitaciones'].notna().sum())
fot['pm2']=fot['precio_eur']/fot['superficie_m2']
valid=fot[fot['pm2'].notna()&(fot['pm2']>0)&fot['superficie_m2'].notna()&(fot['superficie_m2']>0)]
print("  valid pm2",len(valid),"mun",valid['municipio'].nunique())
print("  temporal",fot['alquiler_temporal'].value_counts().to_dict())
# pisos
pis=pd.read_csv(f'{BASE}/anuncios_pisos.csv')
print("PISOS raw rows",len(pis),"mun_busqueda",pis['municipio_busqueda'].nunique())
pis['pm2']=pis['precio_eur']/pis['superficie_m2']
validp=pis[pis['pm2'].notna()&(pis['pm2']>0)&pis['superficie_m2'].notna()&(pis['superficie_m2']>0)]
print("  valid pm2",len(validp),"mun",validp['municipio_busqueda'].nunique() if 'municipio_busqueda' in validp else validp['nombre_canonico_resuelto'].nunique())
print("  superficie notnull",pis['superficie_m2'].notna().sum(),"habitaciones notnull",pis['habitaciones'].notna().sum())
# realty
rea=pd.read_csv(f'{BASE}/anuncios_realtyapi.csv')
print("REALTY raw rows",len(rea),"mun",rea['municipio'].nunique())
rea['pm2']=rea['precio_eur']/rea['superficie_m2']
validr=rea[rea['pm2'].notna()&(rea['pm2']>0)&rea['superficie_m2'].notna()&(rea['superficie_m2']>0)]
print("  valid pm2",len(validr))
# unificado
au=pd.read_csv(f'{PROC}/anuncios_unificados.csv',dtype={'codigo_ine':str})
print("\nUNIFICADO rows",len(au),"mun (codigo_ine)",au['codigo_ine'].nunique())
print("  valid pm2", (au['precio_eur']/au['superficie_m2']).notna().sum())
au['pm2']=au['precio_eur']/au['superficie_m2']
v=au[au['pm2'].notna()&(au['pm2']>0)&au['superficie_m2'].notna()&(au['superficie_m2']>0)]
print("  valid rows",len(v),"mun",v['codigo_ine'].nunique())
cnt=v.groupby('codigo_ine').size()
print("  >=30:",(cnt>=30).sum(),"10-29:",((cnt>=10)&(cnt<30)).sum(),"5-9:",((cnt>=5)&(cnt<10)).sum(),"<5:",(cnt<5).sum())
print(cnt.sort_values(ascending=False).head(12).to_string())
# temporal fotocasa
print("\nFotocasa temporal counts:", fot['alquiler_temporal'].value_counts().to_dict())
# unificado modalidad per portal
print(au.groupby(['portal','modalidad']).size().to_string())
# superficie outlier
print("\nsuperficie max", au['superficie_m2'].max(), "min", au['superficie_m2'].min())
print("superficie<15 count", (au['superficie_m2']<15).sum(), ">300 count", (au['superficie_m2']>300).sum())
print("es_outlier_superficie counts", au['es_outlier_superficie'].value_counts().to_dict() if 'es_outlier_superficie' in au else 'NA')
# habitaciones
print("habitaciones nulls", au['habitaciones'].isna().sum())
# IQR outliers pm2
import numpy as np
for name,df in [('fotocasa',fot),('pisos',pis),('realty',rea)]:
    df=df.copy(); df['pm2']=df['precio_eur']/df['superficie_m2']
    v=df[df['pm2'].notna()&(df['pm2']>0)]
    q1,q3=v['pm2'].quantile([.25,.75]); iqr=q3-q1
    out=v[(v['pm2']>q3+1.5*iqr)|(v['pm2']<q1-1.5*iqr)]
    print(f"{name} IQR outliers pm2: {len(out)} (upper {q3+1.5*iqr:.2f})")
# fotocasa combined temporal vs longterm means
ft=fot[fot['alquiler_temporal']==True]; fl=fot[fot['alquiler_temporal']==False]
ftv=ft[ft['pm2'].notna()&(ft['pm2']>0)]; flv=fl[fl['pm2'].notna()&(fl['pm2']>0)]
print("fotocasa temporal mean pm2", round(ftv['pm2'].mean(),2), "n",len(ftv), "longterm mean", round(flv['pm2'].mean(),2),"n",len(flv))
# combined anuncios
print("\ncombined valid municipalities:", v['codigo_ine'].nunique())
