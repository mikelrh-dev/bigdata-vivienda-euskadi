import pandas as pd
for t in ['araba', 'bizkaia', 'gipuzkoa']:
    df = pd.read_csv(f'data/raw/certificados_energeticos_{t}_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
    munis = df['Municipio'].unique()
    for m in munis:
        ml = m.lower()
        if 'bil' in ml or 'don' in ml or 'vit' in ml or 'gast' in ml or 'arras' in ml:
            print(f'[{t}] {repr(m)}')