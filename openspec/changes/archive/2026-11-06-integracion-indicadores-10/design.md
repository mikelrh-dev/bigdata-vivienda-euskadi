# Design: integracion-indicadores-10

## Architecture

<accTitle>Flujo Kafka-Mongo y 5 indicadores</accTitle>
<accDescr>Describe el gate extremo a extremo que encadena Kafka y MongoDB y el conteo de 5 indicadores distintos sin usar el legacy.</accDescr>

```mermaid
flowchart LR
    subgraph Gate[gate_bloque2.py]
        P[produce 10\nKafkaProducer + Future]
        C[consume 10\ngrupo anuncios\nupsert portal:id_anuncio]
        V[verify Mongo\nfind portal:id_anuncio\ncodigo_ine + LAG]
    end
    P --> C --> V
    P --> T[trazabilidad_vm.md\nFecha Objetivo Maquina\nComando Salida Conclusion]
    C --> M[(MongoDB\nvivienda_euskadi\n759+10)]
    subgraph Ind[Indicadores 5 non-legacy]
        I1[esfuerzo 18-34\nEustat oficial + renta]
        I2[tension social\nEtxebide + esfuerzo]
        I3[paro Lanbide\nmunicipal 2026]
        I4[precio m2\nEustat oficial]
        I5[VPO terminadas\nOpenData 73 + poblacion]
        L[esfuerzo 16-29 legacy\nNO cuenta]
    end
    I5 --> M
    classDef gate fill:#1f6feb,stroke:#222,stroke-width:1px
    classDef mongo fill:#2ea043,stroke:#222,stroke-width:1px
    classDef ind fill:#8957e5,stroke:#222,stroke-width:1px
    class P,C,V gate
    class M mongo
    class I1,I2,I3,I4,I5 ind
```

## Decisions

| Decision | Choice | Alternatives rejected | Why |
|----------|--------|-----------------------|-----|
| Gate subset 10, no 759 | 10 deterministas ordenados por (portal,id_anuncio) | 759 en gate | Evita inundar broker, reproduce `huella_subset` SHA256 estable; 759 ya está en topic |
| VPO como 5º indicador | `vpo_municipal` ‰ (0-50) desde Open Data Euskadi 73 + `dim_municipios` | Alquiler mediana anuncios (foto 2026) | VPO es oficial, municipal, 2 fuentes por `codigo_ine`, pipeline ya existe; precio anuncios es foto no comparable con precio oficial |
| Legacy 16-29 archivado | No cuenta como indicador | Contarlo como 5º | Sería el fallo de sobreventa detectado en defensa; el contrato ya lo marca legacy |
| Trazabilidad VM obligatoria | Toda salida VM > `docs/trazabilidad_vm.md` | Log aparte o chat | El repo ya usa ese patrón (Bloque 1); una sola fuente evita huecos de evidencia |
| HDFS procesado fuera | No se sube silver (solo-raw) | Subir 228M a `/procesado` | Decisión firmada 2026-11-05; silver regenerable, HDFS-01 queda SHALL originales + SHOULD procesados |

## Known Limitations

| Limitation | Evidence | Mitigation |
|------------|----------|------------|
| `min.insync.replicas=2` con RF=1 | `server.properties` vs topic RF=1 | Documentar como deuda; no cambia el gate por upsert idempotente |
| Tensión/paro calculados en silver, expuestos por Mongo | `calcular_tension_social.py`, `municipios.empleo` passthrough | Declarar silver justificado con flag/is_imputed; el conteo no cambia por el origen |
| Consumer `max_messages=2` con timeout TimeoutException | `kafka_vm.md` §6 | TimeoutException es terminación normal del consumidor, no fallo |
