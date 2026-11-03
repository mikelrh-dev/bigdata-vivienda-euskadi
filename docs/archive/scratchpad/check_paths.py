import re, os
text=open('docs/inventario_datos.md',encoding='utf-8').read()
paths=set(re.findall(r'`([^`]+)`', text))
data_paths=set(p for p in paths if p.startswith('data/'))
actual=set()
for root,_,fs in os.walk('data'):
    for fn in fs:
        actual.add(os.path.join(root,fn).replace(chr(92),"/"))
print('doc data paths', len(data_paths), 'actual', len(actual))
print('missing', len(actual-data_paths))
print('extra', len(data_paths-actual))
if actual-data_paths:
    print(list(actual-data_paths)[:10])
