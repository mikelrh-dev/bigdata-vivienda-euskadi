import pandas as pd
# Check if bilbao is subset of bizkaia
df_biz = pd.read_csv('data/raw/certificados_energeticos_bizkaia_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
df_bil = pd.read_csv('data/raw/certificados_energeticos_bilbao_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
print('Bizkaia filas:', len(df_biz))
print('Bilbao filas:', len(df_bil))
# Check column names
print('Bizkaia cols (first 5):', list(df_biz.columns[:5]))
print('Bilbao cols (first 5):', list(df_bil.columns[:5]))
# Check if Bilbao municipio exists in bizkaia
print('Bilbao in bizkaia?', 'Bilbao' in df_biz['Municipio'].unique())
# Check overlap by registro number
if 'Nº registro' in df_biz.columns and 'Nº registro' in df_bil.columns:
    overlap = set(df_biz['Nº registro']) & set(df_bil['Nº registro'])
    print('Overlap registros:', len(overlap))