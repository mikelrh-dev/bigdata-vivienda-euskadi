import pandas as pd
df = pd.read_csv('data/raw/certificados_energeticos_araba_completo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
print('Tipo edificio:', df['Tipo edificio'].value_counts().to_dict())
print('Alcance edificio:', df['Alcance edificio'].value_counts().to_dict())
print('Calificacion energetica:', df['Calificación energética'].value_counts().to_dict())