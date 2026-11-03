import json, glob, os
def find_codes(obj, path=''):
    codes=set()
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k=='codigo_ine':
                codes.add(str(v))
            else:
                codes |= find_codes(v, path+'/'+k)
    elif isinstance(obj, list):
        for item in obj:
            codes |= find_codes(item, path)
    return codes

for f in sorted(glob.glob('data/raw/*.json')):
    try:
        d=json.load(open(f,encoding='utf-8'))
    except Exception as e:
        print(f, 'ERR', e); continue
    codes=find_codes(d)
    if codes:
        minlen=min(len(c) for c in codes)
        print(f, 'n=', len(codes), 'minlen=', minlen, 'sample=', sorted(codes)[:3])