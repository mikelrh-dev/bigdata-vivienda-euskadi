# Design: mongo-geojson-real

## Technical Approach

Resolver el hueco entre el modelo documentado (GeoJSON Point + 2dsphere) y la carga real. El loader lee latitud y longitud reales del silver enriquecido, las valida y las embebe como `Point` en `load_anuncios`; un test dedicado recarga y cuenta valores vivos para habilitar la actualización documental.

## Architecture Decisions

| Opción | Compromiso | Decisión |
|---|---|---|
| `Point` directo desde silver por `id_anuncio`, solo `portal == "fotocasa"` | Simple, trazable, sin geometrías derivadas | **Elegida.** 424 de 428 fotocasa con coincidencia; resto `None` |
| Centroide municipal como fallback | Daria puntos a `pisos`/`realtyapi`, pero inventa precisión | **Rechazada.** Viola prohibición de inventar valores |
| Normalizar coordenadas en MongoDB con `$convert` | Movería parseo a la base y ocultaría la fuente silver | **Rechazada.** El silver ya trae `latitud`/`longitud` como texto validable |
| Validar con `to_float` + finito + rango en `_geo_point` | Descarta silenciosa a `None` los inválidos | **Elegida.** Garantiza 0 Point inválidos y test estricto `invalid == 0` |

## Data Flow

    anuncios_fotocasa_enriquecido.csv (471 filas)
        latitud, longitud, id_anuncio
            |
            v
    _lookup_fotocasa_geo() -> {id_anuncio: Point | None}
            |
            v
    load_anuncios() lee anuncios_unificados.csv (759 filas)
        portal == "fotocasa" ? geo_by_id[id] : None
            |
            v
    anuncios.ubicacion.coordenadas: Point[lon,lat] (424) | None (335)
            |
            v
    idx_anuncios_geo 2dsphere sparse -> consultas espaciales

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `storage/load_mongo.py` | Modify | `_geo_point(lat_raw, lon_raw)` valida con `to_float`, finito y rango `[-90,90]`/`[-180,180]`, retorna `{"type":"Point","coordinates":[lon,lat]}` o `None`; `_lookup_fotocasa_geo()` mapea `id_anuncio -> Point`; `load_anuncios()` usa el mapa por `id_anuncio` |
| `tests/test_mongo_geo.py` | Create | `test_anuncios_geojson_real` ejecuta `load_anuncios()`, recorre `ubicacion.coordenadas != None` y exige `puntos > 0` e `invalid == 0` |
| `docs/modelo_mongodb.md` | Modify | Línea 40 con conteo medido 424 de 759, fuente silver por `id_anuncio` y `None` resto, solo si el test pasa |

## Interfaces / Contracts

```python
def _geo_point(lat_raw, lon_raw) -> dict | None:
    # None si falta, no numérico, no finito o fuera de rango
    # {"type": "Point", "coordinates": [lon, lat]} en caso contrario

def _lookup_fotocasa_geo() -> dict[str, dict | None]:
    # key: id_anuncio como str; value: Point o None
    # {} si el CSV silver no existe o no se puede leer

def load_anuncios() -> int:
    # coordenadas = geo_by_id.get(id_anuncio) if portal == "fotocasa" else None
```

Índice existente sin cambios: `analysis/mongo_indexes.py` crea `idx_anuncios_geo` sobre `("ubicacion.coordenadas", "2dsphere")` con `sparse=True`.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | `_geo_point` con lat/lon válidas, vacías, `NaN`, fuera de rango | Cubierto por recorrido del test de integración con 0 inválidos |
| Integration | `load_anuncios()` persiste 424 Point reales y 335 `None` | `test_anuncios_geojson_real` recarga y cuenta en Mongo vivo, exit 0 |
| Integration | No regresión de carga | `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q` exit 0 (25 passed) |

## Threat Matrix

N/A — sin routing, comandos shell, subprocesos, automatización VCS/PR, clasificación de ejecutables ni integración de procesos.

## Migration / Rollout

Recarga idempotente vía `load_anuncios()` con `update_one(..., upsert=True)` sobre `portal + id_anuncio`. Sin migración de otro tipo; los documentos previos con `None` se sobrescriben por claves naturales. Mongo vivo verificado con 13 colecciones principales.

## Open Questions

Ninguna bloqueante. Los 4 `id_anuncio` fotocasa sin coincidencia en silver (182812522, 191125846, 191234371, 191247657) quedan `None` por diseño hasta que el silver los incluya; no se propone fallback.
