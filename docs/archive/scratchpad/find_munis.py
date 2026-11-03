import pandas as pd
df = pd.read_csv('data/raw/certificados_energeticos_bizkaia_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
munis = df['Municipio'].unique()
for m in munis:
    ml = m.lower()
    if 'bilbao' in ml or 'donostia' in ml or 'vitoria' in ml or 'arrasate' in ml or 'mondragon' in ml:
        print(repr(m))