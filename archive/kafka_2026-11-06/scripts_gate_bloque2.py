"""Gate extremo a extremo Bloque 2 (paso 7) versionado.

Encadena HDFS (solo lectura) -> Kafka -> MongoDB por codigo_ine con
10 anuncios deterministas, sin subir raw ni crear carpeta en HDFS.

Uso:
    .venv/Scripts/python.exe scripts/gate_bloque2.py

Pasos:
  0. HDFS leg = LISTSTATUS previo vía storage/hdfs_utils.get_client()
     (status/list sobre /data y /data/raw). Cero escrituras, cero
     subida de raw/procesado, sin crear carpeta.
  1. Subset determinista: primeros 10 de read_anuncios() ordenados por
     (portal, id_anuncio); huella SHA256 = sha256(json.dumps(subset,
     sort_keys=True, ensure_ascii=False).encode('utf-8')).
  2. Produce 10 a anuncios_inmobiliarios (KafkaProducer + Future
     add_callback/add_errback, kafka-python 2.2.3).
  3. Consume 10 con grupo 'anuncios' (storage.kafka_consumer.consume,
     max_messages=10, commit manual, upsert portal+id_anuncio).
  4. Verifica en Mongo: cada uno consultable por portal+id_anuncio+
     codigo_ine (1 doc), total anuncios, municipios, lag por partición.
  5. Imprime VERIFICADOS 10/10, HUELLA_SHA, TOTAL, MUNICIPIOS, LAG y
     GATE PASS/FAIL; exit 0 solo si 10/10 + total>=759 + lag 0.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


GATE_N = 10
HDFS_BASE = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data"
HDFS_RAW = HDFS_BASE + "/raw"


def huella_subset(subset: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(subset, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def hdfs_leg() -> bool:
    """LISTSTATUS previo solo lectura; sin escritura ni crear carpeta."""
    from storage.hdfs_utils import get_client

    client = get_client()
    try:
        base_list = client.list(HDFS_BASE)
        raw_list = client.list(HDFS_RAW)
        status_raw = client.status(HDFS_RAW)
    except Exception as exc:  # noqa: BLE001
        print(f"HDFS_LEG FAIL {exc}")
        return False
    print(f"HDFS_LEG LIST_BASE {base_list}")
    print(f"HDFS_LEG LIST_RAW_COUNT {len(raw_list)}")
    print(f"HDFS_LEG STATUS_RAW childrenNum={status_raw.get('childrenNum')}")
    print("HDFS_LEG CERO_ESCRITURAS NO_SUBIDO_RAW")
    print("HDFS_LEG CERO_ESCRITURAS NO_SUBIDO_PROCESADO")
    return True


def produce_subset(subset: list[dict]) -> int:
    from kafka import KafkaProducer

    from storage.kafka_producer import (
        _on_send_error,
        _on_send_success,
        get_bootstrap_servers,
        get_topic,
        serialize_anuncio,
    )

    topic = get_topic()
    producer = KafkaProducer(bootstrap_servers=get_bootstrap_servers())
    try:
        for anuncio in subset:
            key, value = serialize_anuncio(anuncio)
            future = producer.send(topic, key=key, value=value)
            future.add_callback(_on_send_success)
            future.add_errback(_on_send_error)
        producer.flush()
    finally:
        producer.close()
    return len(subset)


def lag_report() -> int:
    """Lag LOG-END - CURRENT por partición con el grupo anuncios."""
    from kafka import KafkaConsumer, TopicPartition

    from storage.kafka_producer import get_bootstrap_servers, get_topic

    consumer = KafkaConsumer(
        bootstrap_servers=get_bootstrap_servers(),
        group_id="anuncios",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    try:
        parts = consumer.partitions_for_topic(get_topic())
        tps = [TopicPartition(get_topic(), p) for p in sorted(parts)]
        consumer.assign(tps)
        end = consumer.end_offsets(tps)
        total_lag = 0
        for tp in tps:
            committed = consumer.committed(tp)
            lag = (end[tp] - committed) if committed is not None else end[tp]
            total_lag += lag
            print(f"LAG p{tp.partition} CURRENT {committed} LOG_END {end[tp]} LAG {lag}")
        print(f"LAG_TOTAL {total_lag}")
        return total_lag
    finally:
        consumer.close()


def main() -> int:
    from storage.kafka_consumer import consume
    from storage.kafka_producer import read_anuncios
    from storage.mongo import get_collection

    ok_hdfs = hdfs_leg()

    anuncios = read_anuncios()
    subset = sorted(
        anuncios, key=lambda a: (str(a.get("portal")), str(a.get("id_anuncio")))
    )[:GATE_N]
    print(f"SUBSET {len(subset)}")
    for a in subset:
        print(
            f"  {a.get('portal')}:{a.get('id_anuncio')} "
            f"codigo_ine={a.get('codigo_ine')} municipio={a.get('municipio')}"
        )
    huella = huella_subset(subset)
    print(f"HUELLA_ESPERADA {huella}")

    n_prod = produce_subset(subset)
    print(f"PRODUCIDOS {n_prod}")

    n_cons = consume(group_id="anuncios", max_messages=GATE_N)
    print(f"CONSUME_RET {n_cons}")

    coll = get_collection("anuncios")
    verificados = 0
    for a in subset:
        doc = coll.find_one(
            {
                "portal": a.get("portal"),
                "id_anuncio": a.get("id_anuncio"),
                "codigo_ine": a.get("codigo_ine"),
            }
        )
        ok = doc is not None
        n_ine = coll.count_documents(
            {
                "portal": a.get("portal"),
                "id_anuncio": a.get("id_anuncio"),
                "codigo_ine": a.get("codigo_ine"),
            }
        )
        print(
            f"{a.get('portal')} {a.get('id_anuncio')} "
            f"esperado_ine {a.get('codigo_ine')} "
            f"en_mongo {(doc.get('codigo_ine') if doc else None)} "
            f"{'OK' if ok else 'FALLO'} CONSULTA_POR_CODIGO_INE {n_ine} doc(s)"
        )
        if ok and n_ine == 1:
            verificados += 1

    total = coll.count_documents({})
    municipios = get_collection("municipios").count_documents({})
    lag = lag_report()
    print(f"VERIFICADOS {verificados}/10")
    print(f"HUELLA_SHA {huella}")
    print(f"TOTAL {total}")
    print(f"MUNICIPIOS {municipios}")
    if ok_hdfs and verificados == GATE_N and total >= 759 and lag == 0:
        print("GATE PASS")
        return 0
    print("GATE FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
