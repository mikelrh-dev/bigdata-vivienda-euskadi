import pandas as pd
import json

r=pd.read_csv('data/raw/eustat_renta_municipal.csv', low_memory=False)
print('periodo last 5:', sorted(r['periodo'].unique())[-5:])
print('tipo renta:', list(r['tipo de renta__etiqueta'].unique()))
print('sexo:', list(r['sexo__etiqueta'].unique()))
r['codigo']=r['ámbitos territoriales'].astype(str).str.strip()
mask = r['codigo'].str.match(r'^\d{5}$')
mun = r[mask]
print('mun rows', mun.shape, 'ambitos unicos', mun['ámbitos territoriales__etiqueta'].nunique())
maxp = mun['periodo'].max()
m = mun[mun['periodo']==maxp]
m = m[m['tipo de renta__etiqueta']=='Renta total']
m = m[m['sexo__etiqueta']=='Total']
print('m2024 shape', m.shape, 'muns', m['ámbitos territoriales__etiqueta'].nunique())
print(m.head(3).to_string(index=False))