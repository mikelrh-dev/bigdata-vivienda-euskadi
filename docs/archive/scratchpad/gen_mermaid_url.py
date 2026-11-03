import base64, json, zlib, re

with open('docs/mapa_relaciones_v2.md', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'```mermaid\n(.*?)```', content, re.DOTALL)
if not match:
    print('No mermaid block found')
    exit(1)

diagram = match.group(1).strip()
print('Diagram length:', len(diagram))

compressed = zlib.compress(diagram.encode('utf-8'))
b64 = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f'https://mermaid.live/edit#pako:{b64}'
print('URL length:', len(url))

# Save URL to file
with open('scratchpad/mermaid_url.txt', 'w') as f:
    f.write(url)
print('URL guardada en scratchpad/mermaid_url.txt')