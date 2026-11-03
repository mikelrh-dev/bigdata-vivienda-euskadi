import pandas as pd
import json
dim = pd.read_csv('data/procesado/dim_municipios.csv')
pop = pd.read_csv('data/raw/udalmap_indicadores_adicionales.csv')
dim['codigo_ine'] = dim['codigo_ine'].astype(str).str.zfill(5)
pop['codigo_ine'] = pop['codigo_ine'].astype(str).str.zfill(5)
df = dim.merge(pop[['codigo_ine','poblacion_total']], on='codigo_ine', how='left')
target = df[(df['poblacion_total'] > 5000) & (df['n_anuncios'] < 10)]
codes = target['codigo_ine'].tolist()
with open('data/procesado/f4_pisos_objetivo.json','w',encoding='utf-8') as f:
    json.dump(codes, f, ensure_ascii=False, indent=2)
print('written', len(codes))