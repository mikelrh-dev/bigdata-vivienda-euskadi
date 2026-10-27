# Entity Resolution Audit — Municipalities

Baseline: `dim_municipios.json` — 252 distinct municipalities, 252 unique `codigo_ine`, 6 with multiple variants (Arrankudiaga-Zollo, Arrasate/Mondragón, Bilbao, Donostia/San Sebastián, Getxo, Vitoria-Gasteiz).

## Summary

| Source | Key field | Distinct muns covered | Matched to dim | Unmatched source values | dim muns missing | codigo_ine present |
|---|---|---:|---:|---:|---:|---|
| alquiler_municipal.csv | municipio | 159 | 159 | 0 | 93 | No |
| anuncios_fotocasa.json | municipio | 57 | 57 | 0 | 195 | No |
| anuncios_pisos.json | municipio_busqueda | 30 | 30 | 0 | 222 | No |
| anuncios_realtyapi.json | municipio / municipio_busqueda | 3 | 3 | 0 | 249 | No |
| eustat_renta_municipal.json | ámbitos territoriales (code) + etiqueta | 252 | 252 | 0 | 0 | Yes |
| eustat_pib_municipal.json | ámbitos territoriales (code) + etiqueta | 252 | 252 | 0 | 0 | Yes |
| eustat_poblacion_edad.json | ámbitos territoriales (code) + etiqueta | 252 | 252 | 0 | 0 | Yes |
| udalmap_empleo.csv | codigo_ine + nombre_canonico | 252 | 252 | 0 | 0 | Yes |

Notes: 'Unmatched source values' counts source distinct values that could not be mapped to any dim municipio (after name normalization). All sources map 100% of their distinct values; gaps are coverage (dim municipios absent from source), not resolution failures.

## Per-source details

### alquiler_municipal.csv
- Key field: `municipio`
- Distinct municipalities covered: 159
- Matched to dim_municipios: 159
- Unmatched source values: 0
- dim municipios missing from source: 93
- codigo_ine present: No
- Consistency: Canonical names (0 variants); no codigo_ine

### anuncios_fotocasa.json
- Key field: `municipio`
- Distinct municipalities covered: 57
- Matched to dim_municipios: 57
- Unmatched source values: 0
- dim municipios missing from source: 195
- codigo_ine present: No
- Consistency: 4 variant names; no codigo_ine

### anuncios_pisos.json
- Key field: `municipio_busqueda`
- Distinct municipalities covered: 30
- Matched to dim_municipios: 30
- Unmatched source values: 0
- dim municipios missing from source: 222
- codigo_ine present: No
- Consistency: Canonical names; no codigo_ine

### anuncios_realtyapi.json
- Key field: `municipio / municipio_busqueda`
- Distinct municipalities covered: 3
- Matched to dim_municipios: 3
- Unmatched source values: 0
- dim municipios missing from source: 249
- codigo_ine present: No
- Consistency: municipio has non-standard "Donostia-San Sebastián" (normalizes to canonical); municipio_busqueda canonical; no codigo_ine

### eustat_renta_municipal.json
- Key field: `ámbitos territoriales (code) + etiqueta`
- Distinct municipalities covered: 252
- Matched to dim_municipios: 252
- Unmatched source values: 0
- dim municipios missing from source: 0
- codigo_ine present: Yes
- Consistency: codigo_ine present as ambito code; label == canonical; 24 aggregate rows (CA/provinces/comarcas) to filter

### eustat_pib_municipal.json
- Key field: `ámbitos territoriales (code) + etiqueta`
- Distinct municipalities covered: 252
- Matched to dim_municipios: 252
- Unmatched source values: 0
- dim municipios missing from source: 0
- codigo_ine present: Yes
- Consistency: same as above

### eustat_poblacion_edad.json
- Key field: `ámbitos territoriales (code) + etiqueta`
- Distinct municipalities covered: 252
- Matched to dim_municipios: 252
- Unmatched source values: 0
- dim municipios missing from source: 0
- codigo_ine present: Yes
- Consistency: same as above

### udalmap_empleo.csv
- Key field: `codigo_ine + nombre_canonico`
- Distinct municipalities covered: 252
- Matched to dim_municipios: 252
- Unmatched source values: 0
- dim municipios missing from source: 0
- codigo_ine present: Yes
- Consistency: codigo_ine present; name/territory consistent

## 3 capitals mapping

| Capital (codigo_ine) | alquiler | fotocasa | pisos | realtyapi municipio | realtyapi busqueda | eustat | udalmap |
|---|---|---|---|---|---|---|---|
| Donostia / San Sebastián (20069) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Vitoria-Gasteiz (01059) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Bilbao (48020) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |

All capitals map correctly in sources that include them. `anuncios_pisos.json` does not cover any of the 3 capitals (0 listings/searches for them). `anuncios_realtyapi.json` municipio field uses a non-standard spelling for Donostia (`Donostia-San Sebastián`) but normalizes to the canonical dim entry.

## Non-standard names (variants)

- `dim_municipios` variants: Arrankudiaga-Zollo ↔ 'Arrankudiaga / Zollo'; Arrasate/Mondragón ↔ 'Arrasate / Mondragón'; Donostia / San Sebastián ↔ 'Donostia - San Sebastián'; Vitoria-Gasteiz ↔ 'Vitoria - Gasteiz'; plus duplicate self-variants for Bilbao/Getxo.
- `anuncios_fotocasa.json`: 4 source names are variants (not canonical): 'Arrankudiaga / Zollo', 'Arrasate / Mondragón', 'Donostia - San Sebastián', 'Vitoria - Gasteiz'.
- `anuncios_realtyapi.json` (municipio): 'Donostia-San Sebastián' is not a listed variant but matches after normalization (spacing/slash).
- `alquiler_municipal.csv`, `anuncios_pisos.json`, `eustat_*`, `udalmap_empleo.csv`: all names canonical (0 variants).

## Gaps and recommendations

- **Coverage gaps (by design/small municipalities):** alquiler 93/252 missing; fotocasa 195/252; pisos 222/252; realtyapi 249/252 (only capitals). Eustat + udalmap cover all 252.
- **No codigo_ine in ad/rental sources:** alquiler, fotocasa, pisos, realtyapi lack `codigo_ine`. Add it at extraction/transform time to make joins deterministic; until then join by normalized name + territorio using dim variants.
- **Eustat aggregate rows:** 24 non-municipality ambitos (C.A., 3 provinces, 20 comarcas) share the same table. Filter to codes present in dim_municipios (or 5-digit codes) for municipality-level analysis.
- **RealtyAPI spelling:** standardize `municipio` to canonical (or prefer `municipio_busqueda`, which is canonical) and add 'Donostia-San Sebastián' as a dim variant if keeping raw.
- **Fotocasa variants:** map the 4 variant spellings to canonical via dim_municipios before aggregation.
- **Pisos search vs listing location:** `municipio_busqueda` is the search target; actual listings are neighborhoods (subtitulo). For municipality-level rent analysis, aggregate carefully or geocode listings.
- **Missing municipalities:** document as no-data rather than imputing; for small municipalities consider comarca/province fallbacks.

## Appendix — dim municipalities missing per source

### alquiler_municipal.csv (93 missing)
Abaltzisketa, Ajangiz, Albiztur, Alkiza, Altzaga, Altzo, Amoroto, Añana, Arakaldo, Arama, Arantzazu, Armiñón, Arraia-Maeztu, Arrankudiaga-Zollo, Arratzu, Arratzua-Ubarrundia, Arrieta, Artea, Artzentales, Aulesti, Baliarrain, Baños de Ebro/Mañueta, Barrundia, Beizama, Belauntza, Berantevilla, Bernedo, Bidania-Goiatz, Elantxobe, Elburgo/Burgelu, Elciego, Elduain, Elvillar/Bilar, Ereño, Errezil, Erriberagoitia/Ribera Alta, Errigoiti, Ezkio-Itsaso, Fruiz, Gabiria, Gaintza, Galdames, Gamiz-Fika, Garai, Gaztelu, Gizaburuaga, Harana/Valle de Arana, Hernialde, Ibarrangelu, Iruraiz-Gauna, Ispaster, Izurtza, Kortezubi, Kripan, Kuartango, Lagrán, Lanciego/Lantziego, Lanestosa, Lantarón, Larraul, Laukiz, Leintz-Gatzaga, Leza, Maruri-Jatabe, Mendata, Mendexa, Meñaka, Moreda de Álava/Moreda Araba, Morga, Munitibar-Arbatzegi Gerrikaitz, Murueta, Mutiloa, Muxika, Nabarniz, Navaridas, Orendain, Orexa, Peñacerrada-Urizaharra, Samaniego, San Millán/Donemiliaga, Sukarrieta, Trucios-Turtzioz, Ubide, Usansolo, Valdegovía/Gaubea, Villabuena de Álava/Eskuernaga, Yécora/Iekora, Zalduondo, Zambrana, Zeberio, Zerain, Zigoitia, Ziortza-Bolibar

### anuncios_fotocasa.json (195 missing)
Abaltzisketa, Aduna, Agurain/Salvatierra, Aia, Ajangiz, Albiztur, Alegia, Alegría-Dulantzi, Alkiza, Altzaga, Altzo, Amezketa, Amoroto, Andoain, Anoeta, Antzuola, Añana, Arakaldo, Arama, Aramaio, Arantzazu, Areatza, Aretxabaleta, Armiñón, Arraia-Maeztu, Arratzu, Arratzua-Ubarrundia, Arrieta, Arrigorriaga, Artea, Artzentales, Artziniega, Asparrena, Asteasu, Astigarraga, Ataun, Atxondo, Aulesti, Ayala/Aiara, Azkoitia, Azpeitia, Baliarrain, Balmaseda, Baños de Ebro/Mañueta, Barrika, Barrundia, Beasain, Bedia, Beizama, Belauntza, Berantevilla, Berastegi, Bergara, Bernedo, Berriatua, Berriz, Berrobi, Bidania-Goiatz, Busturia, Campezo/Kanpezu, Dima, Durango, Ea, Elantxobe, Elburgo/Burgelu, Elciego, Elduain, Elgeta, Elgoibar, Elvillar/Bilar, Ereño, Ermua, Errenteria, Errezil, Erriberagoitia/Ribera Alta, Errigoiti, Eskoriatza, Etxebarri, Etxebarria, Ezkio-Itsaso, Forua, Fruiz, Gabiria, Gaintza, Galdames, Gamiz-Fika, Garai, Gatika, Gaztelu, Getaria, Gizaburuaga, Gordexola, Güeñes, Harana/Valle de Arana, Hernialde, Ibarra, Idiazabal, Igorre, Ikaztegieta, Iruña Oka/Iruña de Oca, Irura, Iruraiz-Gauna, Ispaster, Itsasondo, Iurreta, Izurtza, Karrantza Harana/Valle de Carranza, Kortezubi, Kripan, Kuartango, Labastida/Bastida, Lagrán, Lanciego/Lantziego, Lanestosa, Lantarón, Lapuebla de Labarca, Larrabetzu, Larraul, Laudio/Llodio, Laukiz, Lazkao, Leaburu, Legazpi, Legorreta, Legutio, Leintz-Gatzaga, Lekeitio, Lemoa, Lemoiz, Leza, Lezama, Lizartza, Loiu, Mallabia, Mañaria, Markina-Xemein, Maruri-Jatabe, Mendaro, Mendexa, Moreda de Álava/Moreda Araba, Morga, Mundaka, Munitibar-Arbatzegi Gerrikaitz, Murueta, Mutiloa, Mutriku, Nabarniz, Navaridas, Olaberria, Ondarroa, Ordizia, Orendain, Orexa, Ormaiztegi, Orozko, Otxandio, Oyón-Oion, Peñacerrada-Urizaharra, Ribera Baja/Erriberabeitia, Samaniego, San Millán/Donemiliaga, Segura, Soraluze-Placencia de las Armas, Sukarrieta, Tolosa, Trucios-Turtzioz, Ubide, Ugao-Miraballes, Urduña/Orduña, Urkabustaiz, Urnieta, Urretxu, Usansolo, Usurbil, Valdegovía/Gaubea, Valle de Trápaga-Trapagaran, Villabona, Villabuena de Álava/Eskuernaga, Yécora/Iekora, Zaldibar, Zaldibia, Zalduondo, Zalla, Zaratamo, Zeanuri, Zeberio, Zegama, Zerain, Zestoa, Zigoitia, Ziortza-Bolibar, Zizurkil, Zuia, Zumaia, Zumarraga

### anuncios_pisos.json (222 missing)
Abaltzisketa, Agurain/Salvatierra, Aia, Aizarnazabal, Ajangiz, Albiztur, Alegia, Alegría-Dulantzi, Alkiza, Altzaga, Altzo, Amezketa, Amorebieta-Etxano, Amoroto, Amurrio, Anoeta, Antzuola, Añana, Arakaldo, Arama, Arantzazu, Areatza, Aretxabaleta, Armiñón, Arraia-Maeztu, Arrankudiaga-Zollo, Arrasate/Mondragón, Arratzu, Arratzua-Ubarrundia, Arrieta, Artea, Artzentales, Artziniega, Asparrena, Asteasu, Ataun, Atxondo, Aulesti, Azkoitia, Azpeitia, Baliarrain, Balmaseda, Baños de Ebro/Mañueta, Barrundia, Beasain, Bedia, Beizama, Belauntza, Berantevilla, Berastegi, Bergara, Bernedo, Berriz, Berrobi, Bidania-Goiatz, Bilbao, Campezo/Kanpezu, Deba, Dima, Donostia / San Sebastián, Durango, Eibar, Elantxobe, Elburgo/Burgelu, Elciego, Elduain, Elgeta, Elgoibar, Elorrio, Elvillar/Bilar, Ereño, Ermua, Errezil, Erriberagoitia/Ribera Alta, Errigoiti, Eskoriatza, Etxebarri, Etxebarria, Ezkio-Itsaso, Forua, Fruiz, Gabiria, Gaintza, Galdakao, Galdames, Gamiz-Fika, Garai, Gautegiz Arteaga, Gaztelu, Gernika-Lumo, Getaria, Getxo, Gizaburuaga, Gorliz, Güeñes, Harana/Valle de Arana, Hernani, Hernialde, Hondarribia, Ibarra, Ibarrangelu, Idiazabal, Igorre, Ikaztegieta, Irun, Iruña Oka/Iruña de Oca, Irura, Iruraiz-Gauna, Ispaster, Itsasondo, Iurreta, Izurtza, Karrantza Harana/Valle de Carranza, Kortezubi, Kripan, Kuartango, Labastida/Bastida, Lagrán, Lanciego/Lantziego, Lanestosa, Lantarón, Lapuebla de Labarca, Larrabetzu, Larraul, Laukiz, Lazkao, Leaburu, Legazpi, Legorreta, Legutio, Leintz-Gatzaga, Leioa, Lekeitio, Lemoa, Lemoiz, Leza, Lezama, Lezo, Lizartza, Loiu, Mallabia, Mañaria, Markina-Xemein, Maruri-Jatabe, Mendaro, Mendata, Mendexa, Meñaka, Moreda de Álava/Moreda Araba, Morga, Mundaka, Mungia, Munitibar-Arbatzegi Gerrikaitz, Murueta, Mutiloa, Mutriku, Muxika, Nabarniz, Navaridas, Oiartzun, Olaberria, Ondarroa, Oñati, Ordizia, Orendain, Orexa, Orio, Ormaiztegi, Orozko, Ortuella, Otxandio, Pasaia, Peñacerrada-Urizaharra, Plentzia, Portugalete, Ribera Baja/Erriberabeitia, Samaniego, San Millán/Donemiliaga, Santurtzi, Segura, Sestao, Sondika, Sopela, Soraluze-Placencia de las Armas, Sukarrieta, Tolosa, Trucios-Turtzioz, Ubide, Ugao-Miraballes, Urduliz, Urduña/Orduña, Urkabustaiz, Urnieta, Urretxu, Usansolo, Usurbil, Valdegovía/Gaubea, Valle de Trápaga-Trapagaran, Villabona, Villabuena de Álava/Eskuernaga, Vitoria-Gasteiz, Yécora/Iekora, Zaldibar, Zaldibia, Zalduondo, Zalla, Zambrana, Zamudio, Zaratamo, Zarautz, Zeanuri, Zeberio, Zegama, Zerain, Zestoa, Zierbena, Zigoitia, Ziortza-Bolibar, Zizurkil, Zuia, Zumaia, Zumarraga

### anuncios_realtyapi.json (249 missing)
Abadiño, Abaltzisketa, Abanto y Ciérvana-Abanto Zierbena, Aduna, Agurain/Salvatierra, Aia, Aizarnazabal, Ajangiz, Albiztur, Alegia, Alegría-Dulantzi, Alkiza, Alonsotegi, Altzaga, Altzo, Amezketa, Amorebieta-Etxano, Amoroto, Amurrio, Andoain, Anoeta, Antzuola, Añana, Arakaldo, Arama, Aramaio, Arantzazu, Areatza, Aretxabaleta, Armiñón, Arraia-Maeztu, Arrankudiaga-Zollo, Arrasate/Mondragón, Arratzu, Arratzua-Ubarrundia, Arrieta, Arrigorriaga, Artea, Artzentales, Artziniega, Asparrena, Asteasu, Astigarraga, Ataun, Atxondo, Aulesti, Ayala/Aiara, Azkoitia, Azpeitia, Bakio, Baliarrain, Balmaseda, Baños de Ebro/Mañueta, Barakaldo, Barrika, Barrundia, Basauri, Beasain, Bedia, Beizama, Belauntza, Berango, Berantevilla, Berastegi, Bergara, Bermeo, Bernedo, Berriatua, Berriz, Berrobi, Bidania-Goiatz, Busturia, Campezo/Kanpezu, Deba, Derio, Dima, Durango, Ea, Eibar, Elantxobe, Elburgo/Burgelu, Elciego, Elduain, Elgeta, Elgoibar, Elorrio, Elvillar/Bilar, Erandio, Ereño, Ermua, Errenteria, Errezil, Erriberagoitia/Ribera Alta, Errigoiti, Eskoriatza, Etxebarri, Etxebarria, Ezkio-Itsaso, Forua, Fruiz, Gabiria, Gaintza, Galdakao, Galdames, Gamiz-Fika, Garai, Gatika, Gautegiz Arteaga, Gaztelu, Gernika-Lumo, Getaria, Getxo, Gizaburuaga, Gordexola, Gorliz, Güeñes, Harana/Valle de Arana, Hernani, Hernialde, Hondarribia, Ibarra, Ibarrangelu, Idiazabal, Igorre, Ikaztegieta, Irun, Iruña Oka/Iruña de Oca, Irura, Iruraiz-Gauna, Ispaster, Itsasondo, Iurreta, Izurtza, Karrantza Harana/Valle de Carranza, Kortezubi, Kripan, Kuartango, Labastida/Bastida, Lagrán, Laguardia, Lanciego/Lantziego, Lanestosa, Lantarón, Lapuebla de Labarca, Larrabetzu, Larraul, Lasarte-Oria, Laudio/Llodio, Laukiz, Lazkao, Leaburu, Legazpi, Legorreta, Legutio, Leintz-Gatzaga, Leioa, Lekeitio, Lemoa, Lemoiz, Leza, Lezama, Lezo, Lizartza, Loiu, Mallabia, Mañaria, Markina-Xemein, Maruri-Jatabe, Mendaro, Mendata, Mendexa, Meñaka, Moreda de Álava/Moreda Araba, Morga, Mundaka, Mungia, Munitibar-Arbatzegi Gerrikaitz, Murueta, Muskiz, Mutiloa, Mutriku, Muxika, Nabarniz, Navaridas, Oiartzun, Okondo, Olaberria, Ondarroa, Oñati, Ordizia, Orendain, Orexa, Orio, Ormaiztegi, Orozko, Ortuella, Otxandio, Oyón-Oion, Pasaia, Peñacerrada-Urizaharra, Plentzia, Portugalete, Ribera Baja/Erriberabeitia, Samaniego, San Millán/Donemiliaga, Santurtzi, Segura, Sestao, Sondika, Sopela, Sopuerta, Soraluze-Placencia de las Armas, Sukarrieta, Tolosa, Trucios-Turtzioz, Ubide, Ugao-Miraballes, Urduliz, Urduña/Orduña, Urkabustaiz, Urnieta, Urretxu, Usansolo, Usurbil, Valdegovía/Gaubea, Valle de Trápaga-Trapagaran, Villabona, Villabuena de Álava/Eskuernaga, Yécora/Iekora, Zaldibar, Zaldibia, Zalduondo, Zalla, Zambrana, Zamudio, Zaratamo, Zarautz, Zeanuri, Zeberio, Zegama, Zerain, Zestoa, Zierbena, Zigoitia, Ziortza-Bolibar, Zizurkil, Zuia, Zumaia, Zumarraga

### eustat_renta_municipal.json (0 missing)
_(none)_

### eustat_pib_municipal.json (0 missing)
_(none)_

### eustat_poblacion_edad.json (0 missing)
_(none)_

### udalmap_empleo.csv (0 missing)
_(none)_
