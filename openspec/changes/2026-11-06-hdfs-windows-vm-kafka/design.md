# Design: hdfs-windows-vm-kafka

## Architecture

<accTitle>Flujo Windows Kafka VM y Hadoop</accTitle>
<accDescr>Describe el flujo Windows Kafka VM y Hadoop con manifiesto por Kafka y put WebHDFS desde la VM.</accDescr>

```mermaid
flowchart LR
    subgraph W[Windows]
        RAW[data/raw 352 fich 861M]
        P[kafka_raw_producer.py\nmanifiesto filename+sha+size]
    end
    subgraph VM[VM 192.168.201.162]
        K[kafka broker\nanuncios_inmobiliarios\ngrupo hdfs_vm]
        C[kafka_hdfs_uploader.py\nconsume manifest\ny hace put WebHDFS]
        STG[staging /staging/raw\ncopia bytes por scp]
        HDFSUTILS[hdfs_utils.py\nupload_raw_excluding_legacy]
    end
    subgraph H[HDFS centro]
        HD[hadoop 10.22.87.215:50070\n/data/raw]
    end
    P --> K --> C --> STG --> HDFSUTILS --> HD
    classDef win fill:#1f6feb,stroke:#222,stroke-width:1px
    classDef vm fill:#2ea043,stroke:#222,stroke-width:1px
    classDef h fill:#8957e5,stroke:#222,stroke-width:1px
    class RAW,P win
    class K,C,STG,HDFSUTILS vm
    class HD h
```

## Decisions

| Decision | Choice | Alternatives rejected | Why |
|----------|--------|-----------------------|-----|
| Kafka lleva manifiesto, no bytes crudos | `kafka_raw_producer.py` envía JSON {rel, size, sha} por Kafka; los bytes viajan por `scp` a `/staging/raw` | Enviar binarios por Kafka | Ficheros de hasta 114M exceden `max.message.bytes` (1M) y serían ineficientes |
| Consumidor VM hace put WebHDFS | `kafka_hdfs_uploader.py` escucha grupo `hdfs_vm` y para cada manifiesto sube con `hdfs_utils.upload_raw_excluding_legacy` + `read_file_sha256` | Put desde Windows directo | La profe exige bytes pasan por la VM |
| Subset de prueba 10 primero, luego full | Gate produce 10 manifiesto para validar extremo a extremo, luego se escala al full | Subir 861M a la primera | Evita perder tiempo si el venv falla |
| venv en la VM con `hdfs==2.7.3` | `~/.venv` + `pip install hdfs==2.7.3` | Apt / sin venv (sin pip) | Hoy la VM no tiene pip; venv aísla y reproduce Windows |

## Known Limitations

| Limitation | Evidence | Mitigation |
|------------|----------|------------|
| Kafka transporta control, no datos grandes | 114M fichero > 1M límite | Documentar: Kafka orquesta, `scp` lleva bytes |
| HDFS raw vacío (0 hijos, tras borrado 2026-11-06) | `LISTSTATUS raw=0` | Re-subida vía este flujo; estado resumible nuevo |
| VM 8 GB libres (55%) | `df -h ~` | Staging 861 MB cabe; borrar staging tras subir |
