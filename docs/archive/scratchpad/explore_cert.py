import pandas as pd

df = pd.read_csv('data/raw/certificados_energeticos_araba.csv', sep=';', encoding='utf-8-sig')
print('Uso principal:', df['Uso principal'].value_counts().to_dict())
calif_cols = [c for c in df.columns if 'Calif. energ' in c and 'total' in c]
print('Calif cols:', calif_cols)
if calif_cols:
    print('Calif energia total:', df[calif_cols[0]].value_counts().to_dict())
print('Total filas:', len(df))
print('Municipios unicos:', df['Municipio'].nunique())
print('Cod municipio sample:', df['Cod. municipio'].unique()[:10].tolist())
print('Municipio sample:', df['Municipio'].unique()[:10].tolist())