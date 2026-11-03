import pandas as pd
for t in ['araba', 'bizkaia', 'gipuzkoa']:
    df = pd.read_csv(f'data/raw/certificados_energeticos_{t}_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
    munis = df['Municipio'].unique()
    for m in munis:
        ml = m.lower()
        if 'bilbao' in ml or 'donostia' in ml or 'vitoria' in ml or 'arrasate' in ml or 'mondragon' in ml:
            print(f'[{t}] {repr(m)}')