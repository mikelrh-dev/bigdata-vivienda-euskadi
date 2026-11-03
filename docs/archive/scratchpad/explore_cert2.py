import pandas as pd

df = pd.read_csv('data/raw/certificados_energeticos_araba_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
print('Columns with uso/uso:', [c for c in df.columns if 'uso' in c.lower() or 'Uso' in c])
print('Columns with calif:', [c for c in df.columns if 'Calif' in c or 'calif' in c.lower()])
print('Total filas:', len(df))
print('Municipios unicos:', df['Municipio'].nunique())