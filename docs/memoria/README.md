# Memoria del proyecto

Esta carpeta contiene la memoria técnica explicativa. El Markdown es la fuente;
el DOCX y el PDF se generan y no se editan a mano.

## Mapa

| Archivo | Se edita | Función |
|---|---|---|
| `_guion.md` | Sí | Alcance, mapa de rúbrica, figuras y estado |
| `_documento.json` | Sí | Portada: título, autor, fecha |
| `_cifras.json` | No (salvo `infra.*` y `verif.*`) | Autoridad única de cifras, generada |
| `_cifras.md` | No | Tabla legible de `_cifras.json` |
| `01-…` a `08-…`, `anexos.md` | Sí | Capítulos; usan `{{clave}}`, no números |
| `figuras/` | No (se copian) | PNG con nombre estable |
| `build.py` | Sí | Refresco, validación y exportación |
| `memoria.md`, `.docx`, `.html`, `.pdf` | No | Artefactos generados |

## Flujo

```bash
# 1. Congelar las cifras del día (requiere MongoDB o el _facts.json de NB04)
python docs/memoria/build.py --refresh

# 2. Comprobar que no hay tokens rotos, figuras ausentes ni TODO
python docs/memoria/build.py --check

# 3. Generar Markdown, DOCX y HTML
python docs/memoria/build.py --build

# 4. Generar el PDF con Chrome
python docs/memoria/build.py --pdf
```

## Cómo se escribe un capítulo

```markdown
<!-- cap: 3 | titulo: Cómo se construyó | criterios: C5, C6, C7, C8 | estado: borrador -->
# 3. Cómo se construyó

El pipeline procesa {{silver.manifest}} ficheros de silver…
```

- Las cifras se escriben como `{{clave}}`; `build.py` las sustituye.
- Si un token no existe, `--check` falla y dice el capítulo y la clave.
- Las figuras se referencian como `figuras/fig-mapa-2024.png` con un pie que
  incluya la fuente.
- Los metadatos del capítulo son el comentario `<!-- cap: … -->` de la primera
  línea; no se borra.

## De dónde salen las cifras

| Grupo | Fuente |
|---|---|
| `mongo.*` | `vaultVivienda/notebooklm/NB04-BDA-Mongo/_facts.json` (generado por `scripts/nb_acta_mongo.py`) |
| `datos.*` | `data/resultados/mongo_*.csv` y la colección `etxebide_promociones` |
| `gold.*` | `data/resultados/*.csv`, `*.png` y `anexo/*.png` |
| `raw.*`, `silver.*` | `data/raw`, `data/procesado` y sus manifiestos |
| `infra.*`, `verif.*` | Valores manuales fechados; se conservan entre refrescos |

`_cifras.json` se versiona para que la memoria se pueda construir sin MongoDB.
Si cambia un dato, se ejecuta `--refresh` y se revisa el diff de `_cifras.json`.

## Estado

- Capítulos: esqueletos con objetivo y secciones; falta la prosa final.
- Figuras: 8 copiadas; faltan las de arquitectura y modelo.
- Portada: autor genérico pendiente de sustituir.
