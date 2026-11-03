import pandas as pd
dim = pd.read_csv('data/procesado/dim_municipios.csv')
pop = pd.read_csv('data/raw/udalmap_indicadores_adicionales.csv')
dim['codigo_ine'] = dim['codigo_ine'].astype(str).str.zfill(5)
pop['codigo_ine'] = pop['codigo_ine'].astype(str).str.zfill(5)
df = dim.merge(pop[['codigo_ine','poblacion_total']], on='codigo_ine', how='left')
target = df[(df['poblacion_total'] > 5000) & (df['n_anuncios'] < 10)]
print('total municipios:', len(df))
print('target count:', len(target))
print(target[['codigo_ine','nombre_canonico','territorio','n_anuncios','poblacion_total']].to_string(index=False))