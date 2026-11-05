# Trazabilidad VM — bigdata-vivienda-euskadi

Principio: cada comando ejecutado en la VM 192.168.201.162 y en el clúster centro HDFS 10.22.87.215 debe quedar guardado en este único .md con formato total de `plan/PLAN_10.md` sección 4: fecha, objetivo, máquina y usuario, comando exacto, salida literal completa y conclusión. Ningún log salva secretos. Plan: `plan/PLAN_10.md` bloque 1 paso 1. Fuentes: `docs/kafka_vm.md`, `.env.example` (`VM_HOST=192.168.201.162`, `VM_KAFKA_PORT=9094`, `HDFS_URL=http://10.22.87.215:50070`, `HDFS_USER=iabd-user15`). Sin cambios en código: solo este `.md` nuevo.

### 2026-11-05 Bloque 1 arranque Kafka (entrada primaria)

Fecha: 2026-11-05
Objetivo: comprobar broker arriba tras arranque manual del 2026-11-05
Máquina: VM 192.168.201.162 usuario mikel
Comando:
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162
    ~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties
Salida literal:
    LISTEN 0 50 *:9093 users:((java,pid=1832,fd=135))
    LISTEN 0 50 *:9094 users:((java,pid=1832,fd=218))
    anuncios_inmobiliarios
    __consumer_offsets
Conclusión: broker arriba en 9094 con topic de 3 particiones, arranque manual pid 1832 verificado

### 2026-11-05 verificación solo lectura Kafka (sin producción)

Fecha: 2026-11-05
Objetivo: verificar broker vivo sin producir ni consumir, solo lectura
Máquina: VM 192.168.201.162 usuario mikel
Comando:
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "ss -tlnp | grep -E ':9093|:9094'; ~/kafka/bin/kafka-topics.sh --list --bootstrap-server 192.168.201.162:9094; ~/kafka/bin/kafka-topics.sh --describe --topic anuncios_inmobiliarios --bootstrap-server 192.168.201.162:9094; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --all-groups --describe; ~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ps aux | grep kafka | grep -v grep | awk '{print $1, $2, $8, $9, $11, $12, $13}'"
Salida literal:
    LISTEN 0      50                 *:9093             *:*    users:(("java",pid=1832,fd=135))
    LISTEN 0      50                 *:9094             *:*    users:(("java",pid=1832,fd=218))
    anuncios_inmobiliarios
    __consumer_offsets
    Topic: anuncios_inmobiliarios	TopicId: J045oausTPeWCBdy624l5A	PartitionCount: 3	ReplicationFactor: 1	Configs: min.insync.replicas=2,segment.bytes=1073741824,max.message.bytes=1048588
        Topic: anuncios_inmobiliarios	Partition: 0	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:
        Topic: anuncios_inmobiliarios	Partition: 1	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:
        Topic: anuncios_inmobiliarios	Partition: 2	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:
    anuncios_inmobiliarios:0:0
    anuncios_inmobiliarios:1:0
    anuncios_inmobiliarios:2:1
    mikel 1832 Sl 15:02 java -Xmx1G -Xms1G
Conclusión: broker sigue arriba pid 1832 iniciado Thu Nov 5 15:02:29 2026, topic anuncios_inmobiliarios con 3 particiones, offsets 0/0/1, sin grupos de consumo descritos, sin producción

### 2026-11-05 Bloque 2 HDFS inventario local vs HDFS LISTSTATUS (paso 5, tarea 1.1)

Fecha: 2026-11-05
Objetivo: inventario local procesado con SHA y LISTSTATUS WebHDFS via storage/hdfs_utils.py, cero escrituras
Máquina: clúster centro HDFS http://10.22.87.215:50070 usuario iabd-user15, desde Windows (repo bigdata-vivienda-euskadi)
Comando:
    .venv/Scripts/python.exe -c "from storage.hdfs_utils import get_client; c=get_client(); print('URL',c.url); print('USER',c._session.params.get('user.name')); print('STATUS_BASE',c.status('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data')); print('LIST_BASE',c.list('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data')); raw=c.list('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw'); print('LIST_RAW_COUNT',len(raw)); print('LIST_RAW_SAMPLE',raw[:10]); print('STATUS_RAW',c.status('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw'))"
Salida literal:
    URL http://10.22.87.215:50070
    USER iabd-user15
    STATUS_BASE {'accessTime': 0, 'blockSize': 0, 'childrenNum': 1, 'fileId': 2850393, 'group': 'iabd', 'length': 0, 'modificationTime': 1793819308659, 'owner': 'iabd-user15', 'pathSuffix': '', 'permission': '755', 'replication': 0, 'storagePolicy': 0, 'type': 'DIRECTORY'}
    LIST_BASE ['raw']
    LIST_RAW_COUNT 200
    LIST_RAW_SAMPLE ['.FROZEN', '.gitkeep', 'ECVI_cifras_interanuales_es_2025T4.xlsx', 'ECVI_es_2026T2.xlsx', 'ECVI_otros_inmuebles_2025T4.xlsx', 'alquiler_distrito_seccion_original.csv', 'alquiler_municipal.csv', 'alquiler_municipal.json', 'alquiler_municipio_original.csv', 'alquiler_seccion.csv']
    STATUS_RAW {'accessTime': 0, 'blockSize': 0, 'childrenNum': 200, 'fileId': 2850772, 'group': 'iabd', 'length': 0, 'modificationTime': 1793821405519, 'owner': 'iabd-user15', 'pathSuffix': '', 'permission': '755', 'replication': 0, 'storagePolicy': 0, 'type': 'DIRECTORY'}
Conclusión: base /user/iabd-user15/bigdata_reto/vivienda_euskadi/data contiene solo raw (childrenNum 1, LIST_BASE ['raw']); raw con 200 entradas de nivel superior (childrenNum 200). Procesado NO está en HDFS. Local raw 355 ficheros (351 sin legacy_obsoleto_no_usar) no modificado. Cero escrituras.

### 2026-11-05 Bloque 2 HDFS dry-run subida procesado (paso 5, tarea 1.2)

Fecha: 2026-11-05
Objetivo: listar lo que subiría (ficheros/bytes/SHA) sin subir procesado sin confirmación profesora; cero escrituras
Máquina: local Windows repo bigdata-vivienda-euskadi, destino HDFS /user/iabd-user15/bigdata_reto/vivienda_euskadi/data/procesado
Comando:
    .venv/Scripts/python.exe scripts/upload_procesado.py --dry-run
    .venv/Scripts/python.exe scripts/upload_procesado.py
Salida literal (con --dry-run, exit 0; sin --dry-run, exit 2 REFUSADO):
    DESTINO_HDFS /user/iabd-user15/bigdata_reto/vivienda_euskadi/data/procesado
    N_FICHEROS 187 MANIFEST 184
    .gitkeep 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 SIN_MANIFEST
    _meta/acta_ingesta.md 715 08f15fd39f2f2d098b2e9d1fe20e8e5ed13e387f964ed9f952b6cd9d23baf8e9 OK
    _meta/alquiler_municipal.json.meta.json 436 a6d9f8449eda4c7e2db0a44a909ff3e67da341e6c830fc5bfcf0ace2da6bd4d2 OK
    _meta/anuncios_faltantes_fotocasa_batch1_20261029_230030.json.meta.json 446 067c9c491f415ec24d86f39af6ebc5d8aaddadc0c7b7ae24fca553c1c1a66bc6 OK
    _meta/anuncios_faltantes_pisos_batch1_20261029_230030.json.meta.json 442 205c4300e51f64670e20c14593a6cf814f00f46f9eb2fe708ca07290ff8caecc OK
    _meta/anuncios_fotocasa.json.meta.json 414 b75961497bab2a0e6148654997a3d5ee1103f7309ddb86565bdc00c6d8af2c38 OK
    _meta/anuncios_fotocasa_detalle.json.meta.json 447 ead1f3b5b78d0833312d021fdac8e01028e8a33c6484c03671b2780ac9fbe3ca OK
    _meta/anuncios_fotocasa_dirigido_20261029.json.meta.json 436 a9ba23284c59a5c21ad262eec8cbde0af39f7751a9d98bcb81b700af85eb2c11 OK
    _meta/anuncios_fotocasa_dirigido_20261029_223523.json.meta.json 445 4fc194abea8a983a90dd7e225efff39682b59c83997b14acf10072285e0247be OK
    _meta/anuncios_fotocasa_enriquecido.json.meta.json 426 379d1da38e47451e86b789e57f0792b1116c77eb7c454db89b07d75645413fa2 OK
    _meta/anuncios_fotocasa_enriquecido_geo.json.meta.json 430 01ab0520a47fdc6407b0177640c18643fcec1d9aac9e0ef54b0c5a5a421283f8 OK
    _meta/anuncios_fotocasa_enriquecido_meta.json.meta.json 431 c1ddb8e28b5d36c172bedbd797fb2ef6131cd8c0b28f05999d85cd5291470d4a OK
    _meta/anuncios_fotocasa_geo.json.meta.json 418 07a84a5e7a5bfcff935e507de8886e9f51b02ad6fb391a043813d6d23bc81058 OK
    _meta/anuncios_fotocasa_habitaciones.json.meta.json 442 6481ba2f3a53932f67e226ada2acb31e6ec4cdd6e8045c85f3d6d23547d6b50c OK
    _meta/anuncios_fotocasa_habitaciones_geo.json.meta.json 446 a9778bce2ad693b4d7ac9682d5dc9d45ccc6e60779cdb9554801f269d757a170 OK
    _meta/anuncios_fotocasa_habitaciones_meta.json.meta.json 447 edab51e587770318c4a4cd61ba2dc64812d4439d612cd3be180c10d0c95a31c7 OK
    _meta/anuncios_fotocasa_meta.json.meta.json 419 aac855931a1b5b698a821604fd2fab175fe6491ee661c31a01f81e92799e32b1 OK
    _meta/anuncios_pisos.json.meta.json 404 6664a4a94fd4919fc305f8f238aef6d30b61a1d323e4be692668fe12e3d7710f OK
    _meta/anuncios_pisos_dirigido_20261029.json.meta.json 420 1190c360d015a25f1793cdd82d0fad424f7771852454eb2aaf53874a0c9a88e3 OK
    _meta/anuncios_pisos_enriquecido.json.meta.json 424 7503d9669b555cb3eb7b1549cf0009833f2ef23cd3b57e423cbeed217f43edfc OK
    _meta/anuncios_pisos_enriquecido_geo.json.meta.json 428 203e390aae35e6b0db9b99e6842986d4c65aa4d6217f608d83f91695d0586b5f OK
    _meta/anuncios_pisos_enriquecido_meta.json.meta.json 429 8f58b495b680109c3b93bc045e648a1cac7ea8215936e3cf3e5194af02ad5b6e OK
    _meta/anuncios_pisos_geo.json.meta.json 416 147b822f0b98d7ad80138f2ae84d688792c05ab3a232f15a3f94a26972322a0e OK
    _meta/anuncios_pisos_habitaciones.json.meta.json 438 54efff16c5af4cb86e3dc7351a487046107117717314593e56631c1735444a54 OK
    _meta/anuncios_pisos_habitaciones_geo.json.meta.json 442 109157316dad674c766f876ce66af43ed1a848ffb0f55bd3bb3b177294f4e44b OK
    _meta/anuncios_pisos_habitaciones_meta.json.meta.json 443 6879a98b0cc4461958875e5e021bd9173095045a56bfa0755412467fb955fca0 OK
    _meta/anuncios_pisos_meta.json.meta.json 417 1664484d5986abd9240aa02172d1edc173c5ad0ccaecf31fb98a902a51ee604a OK
    _meta/anuncios_realtyapi.json.meta.json 414 ef937f00827d69f33a802a858652a3ac2aae38a99ef9f26d006f9dff7e4e6a33 OK
    _meta/b5m_catalogo.json.meta.json 476 49fb22fc858f064c4ed7d27e5c2860a995d9b7194ec4fed1283b8a05035ade29 OK
    _meta/csvs_index.json 20829 984edb3cd910fa30b56fe99387660d8b463e19edfc8e5331b8e6da5fb7bcd88b OK
    _meta/dim_municipios.json.meta.json 429 e2c57d049923fbebe190d2750c9ba5ab7df75c76536aa6fc11d5c4805fb4da64 OK
    _meta/distancias_b5m_gipuzkoa.json.meta.json 460 0e8af8590e72421588a48fea6304b20680734887aba66cf2b5f6b20d4160dc72 OK
    _meta/distancias_municipios.json.meta.json 483 b19eb7d1b307c6ef5151116e2b9824b7e7939cf6d4a45d67aaa8afe0ddeb3438 OK
    _meta/educacion_centros.json.meta.json 572 c210a85e2a4d6303a33631aa40845ed5541ca8fbb2f46ca058270880acc65270 OK
    _meta/emal_fianzas.json.meta.json 515 336fd4f8795635ccedd7b9ad9ca606540ccfc9c558926b3fcfe5cb68c12a5828 OK
    _meta/emal_fianzas_ampliado.json.meta.json 386 f143e0784cc77fdc18b04a2ff453cf73c6dc6c0a72116f1094fbf3054067f831 OK
    _meta/emancipacion_juventud_resumen.json.meta.json 608 9c061a0dbd8eac86340327377e79246942977afde718c89d137085829e23bc12 OK
    _meta/etxebide_promociones.json.meta.json 474 005ce6b4b7b75191a86edc6b12ce96e645d59f88facb0d5aeb0c731489a47ed6 OK
    _meta/etxebide_solicitudes.json.meta.json 497 700ad2f744fe274a4e3588582bb6b56463e2383d8f12f32681221e08451eefc0 OK
    _meta/eustat_pib_municipal.json.meta.json 451 5878d14aa98bd670da9ec62cf97f2da268b29fedb1d4b6076fb9048c04e0b7bb OK
    _meta/eustat_poblacion_edad.json.meta.json 446 ae03361465a219412066d3982547f98045dd017c4d4566bebd9df1299a0557aa OK
    _meta/eustat_renta_edad.json.meta.json 442 2d0ebfcb4c826e69aef077af20b167e54d0efa68780fd14fbdab3309d6bca159 OK
    _meta/eustat_renta_municipal.json.meta.json 450 463640dedbc6fa12a2d56790531c98957b1b149e43c090a09d03b05d7d5bcbe8 OK
    _meta/eustat_tenencia.json.meta.json 438 a58158a78d58d585924f497e9615705d2e93dfb2d7f2c1adab028505ca948f63 OK
    _meta/index.json 30924 922b501b261542710bdfa21aa56301cd2de541e7356e09bc4318348c55305e6f OK
    _meta/ine_69301.json.meta.json 420 a2a3efb79d90353b0f34d1e2586a1e9cd318092256096afdfd95df2b197076aa OK
    _meta/ine_69302.json.meta.json 420 56d4b868d97da788cb1cf391b59d17c9abe8ac2dd7c74955adf07b6247a11d36 OK
    _meta/ine_69303.json.meta.json 418 0c67dd6a88965cf91e958c298a1ecfe598491b3a09f802f8bb29d46bf2013e3a OK
    _meta/ine_69323.json.meta.json 420 51e383b6bad5718fa444ee22b646a2875033500eb313193cd1480429b64fdee9 OK
    _meta/ine_69330.json.meta.json 420 2ff18b3360c6de50cd9c750fcfa03c55f7742704f3f0207b2a155b6584adbe99 OK
    _meta/ine_atlas_renta.json.meta.json 418 7eeb83a94f533ce55029cb4a037f8b7c41dab9e3a1966b1267130a404ab86638 OK
    _meta/ine_salarios_decil.json.meta.json 407 e292ff2639656b82ab30600fd24e662a65a9eaf1a5580d51a23c390763cbc6d4 OK
    _meta/ine_salarios_edad.json.meta.json 407 456870ef3c7cb80089fedefe9045816d06f13c3426a6a676bd91a71903f39973 OK
    _meta/ingestion_manifest.json 103911 977713811ea14ae3795cb7d0f1ca6d595787572e8e1dc49d61f6dd4f5837fc1c SIN_MANIFEST
    _meta/lanbide_paro_historico_joven.json.meta.json 423 4960c631c1cdea67a8bdf5fb865d5f1f9fe95a71f030b80330ecfc634a767c0f OK
    _meta/lanbide_paro_juvenil.json.meta.json 409 9ddc67027a8a84df1c4f5eda24b025369dc0005f2cec2c1b5e0862eceb15b216 OK
    _meta/municipios_gipuzkoa_lista.json.meta.json 421 e8f1b9325fe1483dbcba83af38a7a04d3df175e7576c3dbfcbebfce518c0fbc8 OK
    _meta/nombres_normalizados_map.json 1995 7cc87b2ddb427e6f37cfeecfe4cc88c264a502d92e2341e9acfb2ad259974a15 OK
    _meta/osrm_tiempos_capitales.json.meta.json 426 9cb13bc884b3d0f74f4a1b4df3ba492a3dee4efd57e7cdd1bd05741cef4529ca OK
    _meta/ovj_salario_joven_2024.json.meta.json 483 4b79bef146f173bb25f7c3ef4cb2d1f8a33e0516decee19827e5067d5d9e647a OK
    _meta/renta_municipal_completa.json.meta.json 392 b3adb4ff3b50b887560259014f5cc139dc8ed7525464355841c76712b5b5f435 OK
    _meta/salud_centros.json.meta.json 571 dab56131f103da638a0f470ba311b7a891660a374eed6c6df66a5fd78ddfdfef OK
    _meta/serpavi_renta_municipal.json.meta.json 431 cb1383429241ba4441061e7ef56ade82c5ad115eb85e3f4de825be9c17f87945 OK
    _meta/transporte_paradas_municipio.json.meta.json 459 b0b7780ff3dc4ac9a5df237a8b98b404bdd3709f819ee46a446821bc4a81f77e OK
    _meta/udalmap_empleo.json.meta.json 463 f16501dccfbf4390b10bace7a574ff8a48902f67d6696ba085ab79253736b748 OK
    _meta/udalmap_empleo_corregido.json.meta.json 422 8f33cc1e36cef38ebb6dfd9d539b4c8a02d10f3f1adffdc142ee5772f1933a8b OK
    _meta/udalmap_extendido.json.meta.json 390 c65f0912d556a6d749195ac7d0e2067aadc4224f2f92029af3f825bc481dff12 OK
    _meta/udalmap_indicadores_adicionales.json.meta.json 442 d1e166ee31ea03b20b495bc97e3050ea065b547fb7fff2686b57c93e15136b2a OK
    alquiler_municipal_completo.csv 38524 241b68f6463d19ad9b16185587168a1fef61b1182be5f6eea9c9a4eb238ff4bc OK
    alquiler_municipal_enriquecido.csv 27024 1a1510d0ecdbe75e25461561cf7c277dcc834ab56fc8aa0881fae8da9265aa78 OK
    alquiler_municipal_enriquecido.json 180534 4334f5bf1a4096623619eb9910b956cd3c357f720cfaeb1b7102c0e494b156f3 OK
    alquiler_municipal_normalizado.json 154205 6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b OK
    alquiler_seccion.csv 177357 63d9995fe226205e40acbee7d3651b6c2696803ffa2667c317919b1e157f08dd OK
    alquiler_seccion_resumen.csv 5100 61cc9ad437bc5404990662915aa64e6ff529a1e2ea102678128bde66279788a4 OK
    analisis_variables_base.csv 106608 8ee170a661143878511615a62eb4b466d3ed7995bb2b05d913467559df1e6cc8 OK
    anuncios_faltantes_fotocasa_batch1_20261029_230030_normalizado.json 6460 bf244efe8d2ac8fa625a741e0dd6be829838a3ea1bd9ad78beff09267b321dcd OK
    anuncios_faltantes_pisos_batch1_20261029_230030_normalizado.json 44516 a7379f971e9d8f40c500ca005ba5f4087d361b4e88b468cf2603ffaa38726104 OK
    anuncios_fotocasa_detalle_normalizado.json 925500 222c3af0720ef9756d620f72bcccfbdc87a4f51190309e4f3837dc966bf5eea8 OK
    anuncios_fotocasa_dirigido_20261029_223523_normalizado.json 122356 1f4a4a6dfcc4746c8eb6c77ce853ee771f024891de9c4e09184331b52cdeb28e OK
    anuncios_fotocasa_dirigido_20261029_normalizado.json 8870 cf72ee4e7fe8c345f214046de89f17221fb1a4129cd347da0cb2d80cc89c9212 OK
    anuncios_fotocasa_enriquecido.csv 138638 f09921551428923231d10fe05f0b05ecb0d895ce13d93ee00598d670b2ce542a OK
    anuncios_fotocasa_enriquecido.json 797845 ee7d498d0fd7dfc5515544430b64865934ee4af8759ab39a4b778d9b4659df6e OK
    anuncios_fotocasa_enriquecido_geo_normalizado.json 1278677 22262bb64df56ab1359ad2f80ae7e6d2f8d701950223d504e119920928838637 OK
    anuncios_fotocasa_enriquecido_meta_normalizado.json 1207236 4697a85b3cd4f9f9196f7c9258114ddef7a851631a99bbf597306fdcce85273e OK
    anuncios_fotocasa_enriquecido_normalizado.json 1055103 8e736c15c6f618ffdafcf9ad4cbffa55fd08fb655cf92c67df9c3467af7b81ae OK
    anuncios_fotocasa_filtrado.csv 395310 c10297fc8a43a80a8bb0b7feaa7df581e360c28b9785f4a473c47231d01577b3 OK
    anuncios_fotocasa_filtrado.json 883405 7df0342a4601b3e557fd9737b072dbd1500af7783db4c1ea1aea120bc388c6a8 OK
    anuncios_fotocasa_geo_normalizado.json 1015564 e9bd9587fea4b800330aee20cf8e61d89efe580261d8b450147ec732c2e81c6b OK
    anuncios_fotocasa_habitaciones_geo_normalizado.json 269851 0d3ebac05ff4727553db85860cc57f53a6c854c9569f49e696ad55076ab29a24 OK
    anuncios_fotocasa_habitaciones_meta_normalizado.json 246224 432aac303d30666e03b90560c51f8fa2abded9c18b4b1d00615a94883a30fb63 OK
    anuncios_fotocasa_habitaciones_normalizado.json 195384 df9c3f2e6d01c1d8b445c69583786b63c15e7cf1501718f09391a80e8c86d9e1 OK
    anuncios_fotocasa_meta_normalizado.json 944123 601f62b60cf0a045b6c828969065d0a8287f53ebed5c8d16005c48ef27551fda OK
    anuncios_fotocasa_normalizado.json 797642 2cbc0cbd65ee5319433d6c1a6fb8c6ad9cca75bb98db6244ee2c497a0089d63a OK
    anuncios_habitaciones_unificados.csv 33824 4f7f639c212d2b8fae3e585cf5127e56601f9fd87b4ce489eb12e4410c2049b8 OK
    anuncios_pisos_dirigido.csv 58765 a4d1593244ec1008df7bc8d547368a985b81bbee0e750e41eb4d3eab36bb0e29 OK
    anuncios_pisos_dirigido.json 267558 17a983eed274d463c286b7627996bb90cd3d4d790102d359acc1e9f0511cd7c6 OK
    anuncios_pisos_dirigido_20261029_normalizado.json 561369 02655dc5574aac2e5cb253400b6eb83e2c4c29d00312d9fe1e651a67136b239a OK
    anuncios_pisos_enriquecido.csv 114418 431da7325b50fa0a328e21fb3d9fb40953c8d5c48a60bef258c2d1f86d156ce9 OK
    anuncios_pisos_enriquecido.json 248819 a20911a55a5f8f9151a55b36083e3b3b508ff2fd1f779dbab0b272eff2a2cc64 OK
    anuncios_pisos_enriquecido_geo_normalizado.json 318713 32482ae482a6b317db4bcc7d4247a53b7f6a243a3f6ce2bef2687b3b5645c080 OK
    anuncios_pisos_enriquecido_meta_normalizado.json 318713 32482ae482a6b317db4bcc7d4247a53b7f6a243a3f6ce2bef2687b3b5645c080 OK
    anuncios_pisos_enriquecido_normalizado.json 245803 cf8cf19bedb9e6cde8fc0a3a602f1a06d7837af4e514fa5def0fa8ea822b390e OK
    anuncios_pisos_filtrado.csv 118095 e9dae1252d43e34b54aa749d769abc9c67d17c4f46515aa620e7820fdbb12ee4 OK
    anuncios_pisos_filtrado.json 292109 0fdfe823737375a45189eb9a541a600506810e500fe3bde06d5fcd76d76cd022 OK
    anuncios_pisos_geo_normalizado.json 224822 103b235fb4bbcdbbc5af1ef5349e70d64a4108083088f5ecd503a23af94b9fb8 OK
    anuncios_pisos_habitaciones_geo_normalizado.json 48275 e9ed74778fea6edb7ef319178224b584910e365a548dd0243a02beafd34c18a0 OK
    anuncios_pisos_habitaciones_meta_normalizado.json 48275 e9ed74778fea6edb7ef319178224b584910e365a548dd0243a02beafd34c18a0 OK
    anuncios_pisos_habitaciones_normalizado.json 33463 432777d910df3289bc36558359c17fd243b4b28ca1435bbd723beb8d40b5f89c OK
    anuncios_pisos_meta_normalizado.json 224822 103b235fb4bbcdbbc5af1ef5349e70d64a4108083088f5ecd503a23af94b9fb8 OK
    anuncios_pisos_normalizado.json 248698 8cef71a0d674be4d1964c130de0b8de02ab148bc2e6465010002bc2a6f45502a OK
    anuncios_realtyapi_enriquecido.csv 24538 f7ffb17367b4ffbb493541e29cc128911a2c75d339cefc73aac4f88ee99f555c OK
    anuncios_realtyapi_enriquecido.json 319974 8d7a9fc8a8eee96c7567ac2fa292671fbc4327f2cfefb77d23923c95f076cf62 OK
    anuncios_realtyapi_normalizado.json 319974 8d7a9fc8a8eee96c7567ac2fa292671fbc4327f2cfefb77d23923c95f076cf62 OK
    anuncios_unificados.csv 137714 fa58cc39ed6d4c3ad3684fa2cdf7180d88ee213c6bde8d67156bef7a0ab6982a OK
    anuncios_unificados.json 660546 7c3cfe5e21ca46b0b17301068fddd363a3469c82b547f1d58f975f20232ed451 OK
    anuncios_vivienda_residencial.csv 54081 6ffb8af896cc7d8eb3bc9a73752d3993bb82cc450121fe1b02532db59b7a3aba OK
    anuncios_vivienda_residencial_filtrado.csv 66337 f1e9f8ce4f7369ae374a4b21f9037f9a34e3a535caccf32d6d50a3baf18b2085 OK
    anuncios_vivienda_temporal.csv 20515 0e832bc536450e7a99b50f6b8f5c4af89146a05f85ee125e67fbc79760d73941 OK
    b5m_catalogo_normalizado.json 54692 5bc632da6662b0ded3c395da8279b6808ef489427319d1fa7559e6932558f362 OK
    cert_energetico_moda_municipio.csv 2304 8fc1bf2138246bc6c458d935b90b4165336563c58014af330480a7939e256c69 OK
    cert_energetico_municipal_252.csv 10882 67fffd0aff75dea8d4547a5169fe2c8731d146fa9d2f009cc7c3ba1fd75cf632 OK
    cobertura_anuncios.csv 8176 1b43ae6fb4e8a2178490c2a301133c63f1feebe82d7e35c8be92252a217cfdfd OK
    comparativa_compra_alquiler_af.csv 944 80ffbd83052de50b8b75837a942b1cb95843823f6af999a2d284e0b4d58495ab OK
    dedup_report.json 180932 da1365976f10822a503e9366af0b5f169bb51fbe06bb30f3e354ae17ababdde6 OK
    dim_municipios.csv 23087 f0b44b5899920941587125254962d40ffa93ab1799e14633a8a3062df4d7260c OK
    dim_municipios.json 93954 f2a1c510f7d5df0b0d137f14e7a5fa91c7a394aae9a8982f9273fc751f255a52 OK
    dim_municipios_enriquecido.csv 263451 02df6ea84a1464678b6bca2cad60cc4d3948cae90aadf6866c43765a948f9c91 OK
    dim_municipios_normalizado.json 94076 38a55f0460ab9dca4459e46c0db5e6d92a2359c6e511df64f34f7dee6c70b28e OK
    dim_municipios_renta.csv 251910 3e4357abc58d680378c3bf2e79112785b633d23a2cac60b709839f887ce240bb OK
    dim_municipios_tension.csv 5934 ff0d0a98b047c29feda9413cfee07f168868664053844bddf5fd4ed01acb6b6d OK
    distancias_b5m_gipuzkoa_normalizado.json 91986422 aa2777afe3be79c18e227cb1ecf82cf4f59a8abc6a6f99be0a692f3a5ff5934a OK
    distancias_capitales_252.csv 23662 9b840cb6ff1f5b093f7159288994f8bacc5c34f043f0774c84e63d88b5eb8f3f OK
    distancias_haversine_252.csv 1197690 8063dca6d3ff7fc24a7ec9dba6b30fee7835bdbf12924f8376d1e0b593e535ca OK
    distancias_municipios_normalizado.json 7040296 57f8e6f42189605cdaf44d820a1e02356861e142375b31e6961bf9c7150c4437 OK
    ecvi_compraventa_limpio.csv 1929 7db38bc0edb62e228384586ae93e1e38a2b04d9ae4369f2d4b89b03b572f15d2 OK
    ecvi_compraventa_limpio.json 7436 1b243b63f162cfda44e851eff7e18555309056afd9b99c2a95331760dd4aec3b OK
    educacion_centros_normalizado.json 937077 0558a569d946a0fb76bdd4e98863be4c459f581162b40981503ecce2f6e1ba90 OK
    emal_fianzas_ampliado_normalizado.json 398803 941104ec63ab91aba8075fa8ffd8a7fafefc88772b8026ec69237b8b01810177 OK
    emal_fianzas_normalizado.json 234451 66474adf41369c89635d0dff12bfeda472afdecc58cd9b038c5676c93be852a4 OK
    emancipacion_juventud_resumen_normalizado.json 1609 c95828626f43ff6ebf065b1e5bb15011667c56b04dfd6c0ef363999111767471 OK
    emancipacion_tier3_93.csv 14461 56c4f30be80a4b9d096255030edc10a55e13c388d2fb7a7e4143fd12c8499b20 OK
    etxebide_promociones_normalizado.json 343590 b3d5d68cad600eb4aaa826f3cf5a8d4ab2a99ca70a017c9b0ebeb8c3e0b77168 OK
    etxebide_solicitudes_normalizado.json 726346 86e429c635880d631890d6e7334a266b63da39c3dd7d18958d5bb2395ec01630 OK
    eustat_demografia_renta_252.csv 17022 7677f62b46febc29f9e9b226183abf488a088e5374f839fe6beb079b2eed0ea9 OK
    eustat_demografia_renta_252.json 92176 61c776a24229f954c249c9f6db41d0affd35fe2d005cfaea0ab053f90f5aa2f9 OK
    eustat_pib_municipal_normalizado.json 4447975 9853bd17376f4f68de2163bafba7d0c8b411efa1a1c78586cb8236384a00675e OK
    eustat_poblacion_edad_normalizado.json 37906473 1cd537abe7f712e5b82a08103855e81bc7ee92e6b8212c6f0781c99cc1af2cfd OK
    eustat_renta_edad_normalizado.json 2163588 b4c16125cefdb691fd430db5a885dec9294e4d2a530402725d7e4b8e0678a7e2 OK
    eustat_renta_municipal_normalizado.json 36674095 8adc5685ed1b8e6e2af28e7eadced8eef624df238d342e678634257e660f7ef7 OK
    eustat_tenencia_normalizado.json 1328953 2ae2088c9806bda3553c59f509da5d81aec6e9deaf581676c239199d3f5f07ec OK
    f4_pisos_informe.csv 2445 2c16d0695bdbacf853f23b63fb2b9c999a9043d9f28395d806616a1cae5e43cf OK
    f4_pisos_objetivo.json 747 3949b89c401b5a5dc5ba340b751b8c5c15334ffbd8dd46017f5c9f9c33b4406d OK
    fotocasa_dirigido_informe.csv 1173 3bdf075bd8fd9d8d5f7e45227db37361d9a53b36376df67947f56f4915bd9106 OK
    ine_69301_normalizado.json 1085568 f7300af7bf090c30158a09e6c1d6516720033b3f2ca02b3a5d83c2aeca613c31 OK
    ine_69302_normalizado.json 637736 bfd93e4b7723cfb99e0c1fade61dd06ae20dce43ac35d5f21bf7df6c845d4ec5 OK
    ine_69303_normalizado.json 220174 808f142d18e7e1e4e18ba75df8bae8237f7ab8e76b23c80ff3dedcb6e204d99f OK
    ine_69323_normalizado.json 467977 b80371328856f189983cf1b3f1a7608d838f41047244ebefc2c25ace3e39be00 OK
    ine_69330_normalizado.json 2453688 16b12c0e5101b709e3d7975a5a1e2c6fc3b85bee01ff1a37cc097ec99c4792a6 OK
    ine_atlas_renta_normalizado.json 45276 9a2aadb2b2ef2c63a29cb14f2d289b622ff571afca896ee2d661b7a4307fdcdc OK
    ine_salarios_decil_normalizado.json 7714 5fd6d68e691f354d2e6b714510837d9d83fdb0c6e33db47c1943377ce6730f06 OK
    ine_salarios_edad_normalizado.json 76505 b50c6626b5ce99f6b7f712b2bb5824fb6690b98ce42b6db410f2fc03c416a16e OK
    informe_entity_resolution.csv 461 eaf87e2e540106894ab0e262f580786f10e77b46602b2ad327c05abe8c169c5c OK
    lanbide_paro_historico_joven_normalizado.json 17219032 76e20ea9dcbcff32201a723128a87714ac7a7e9a780b927960742440950be361 OK
    lanbide_paro_juvenil_normalizado.json 90076 c471a474d911ff8a330457b54a48baaa6291db5a3d9c0c9ef6fa94b99e359cb0 OK
    manifest_sha256.txt 19393 f8d5ef23326dce1d0f050fe0f3e82db4a675dfa3c2bce1e2530d7ad93c726574 SIN_MANIFEST
    municipio_area_funcional_ecvi.csv 22724 949dbc70628c9b86377627e99d0bb754d86811f0e56bc3a5f61e67211fa16e6a OK
    municipios_euskadi_252.geojson 11019045 fd3dd102f08a5944621fae7aa2f6759a1c6113aef12179ab8f84402827d364c2 OK
    municipios_faltantes_93.csv 5779 c7b4faa3b1c9e525da54f3ec778388220a45d6edf24c6623a97b0ca90a60dffe OK
    municipios_gipuzkoa_lista_normalizado.json 17018 72f87fd169b6b3f73813d9fad0ef23a1b91e2a375b6ef34abda05541ed5ac5da OK
    osrm_tiempos_capitales_normalizado.json 41223 b8849948b5da553d3a9c3c62bbe7fb00d6be089b800ed0114089fdc7794cee26 OK
    ovj_salario_joven_2024_normalizado.json 1067 f3eb7c9cc9eabf0796b35be08bc51c11839dc57b8e3fa6f1b97e86952dd16079 OK
    pob_rank.csv 1832 0c68a4eeb9e556abfbe79dc0c7e64ae410426702c0d21ed16677e93eb93db251 OK
    poblacion_joven_municipal.csv 35924 e56c446056e820f381977b9eec1032920adbe7431e6cede37b68748b7eb964ad OK
    renta_municipal_completa_normalizado.json 52323 7cf2981d6c0beac63e9cfdf98a95d4fba8f391313f1b12fb631f989830cdaad3 OK
    renta_municipal_referencia.csv 46106 c0ca1af62116a6ffba52f64fc07438c95835fa6413ffc827e4eb82ebb788c609 OK
    run_manifest.json 57637 48bef0c7fb26ab027d1d54b5e4c52b02e9bec48742e1a79d9083bb05b6296ecb OK
    salud_centros_normalizado.json 268760 d9f64607e208eafc4c258e11e47759e4e88a53619f9eb98f6a3af6fe3374e558 OK
    serpavi_renta_imputado.csv 22595 f4f79ae42f6b062d38a7b1d171e8368b913cb21dae374aa366ee259a564d2ad1 OK
    serpavi_renta_municipal_normalizado.json 74833 35d87a216ca8142adf35aacc88eff65e71151c41a6973839ae72b80caaba9e47 OK
    transporte_paradas_municipio_enriquecido.csv 24351 4c5d07d465acaeabca834234b2285906c52d6536f17c426e86af7a90afd7a603 OK
    transporte_paradas_municipio_normalizado.json 58719 36df500c912aa4a4ab9ddaa08c8655acea90f1ac922cdc6218450a78889cb1f9 OK
    udalmap_empleo_corregido.csv 90924 c1985b48b057339c870787938549543534f8af44eb744fdc6f549065af19d24c OK
    udalmap_empleo_corregido.json 325913 c8780c2937240e18bcb9702b965c6cf3184cd489300c2ddeb3075a3e64808c98 OK
    udalmap_empleo_corregido_normalizado.json 325913 c8780c2937240e18bcb9702b965c6cf3184cd489300c2ddeb3075a3e64808c98 OK
    udalmap_empleo_normalizado.json 238284 817212814b9e7263577f82466baf5efefce3cb59e1c05855909619ba5c033a80 OK
    udalmap_extendido_normalizado.json 161038 aa85d76bb98b5c63dc288e118eb32bf05b85107f20eb5a82364f448400e93695 OK
    udalmap_indicadores_adicionales_normalizado.json 372277 46dbfbf489af7456910e6fbbb0e82ed10282d1daa565c32f112bb2fd4780a6f5 OK
    TOTAL_FICHEROS 187 TOTAL_BYTES 238344685 OK 184 SIN_MANIFEST 3
    DRY_RUN_OK CERO_ESCRITURAS NO_SUBIDO
    REFUSADO: sin confirmación de la profesora no se sube procesado (usa --dry-run)
Conclusión: procesado listo en local con 187 ficheros, 238344685 bytes, 184 OK contra manifest_sha256.txt (184), 3 SIN_MANIFEST (.gitkeep, _meta/ingestion_manifest.json, manifest_sha256.txt, esperados). DRY_RUN_OK CERO_ESCRITURAS NO_SUBIDO. Sin --dry-run rehúsa (exit 2). HDFS sigue solo con raw.

### 2026-11-05 Bloque 2 Kafka lectura inicial y peek de mensaje previo (paso 6, tarea 2.1)

Fecha: 2026-11-05
Objetivo: listar topic, offsets y grupos sobre 192.168.201.162:9094 antes de producir; inspeccionar mensaje previo sin consumir con grupo anuncios
Máquina: VM 192.168.201.162 usuario mikel
Comando:
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-topics.sh --describe --topic anuncios_inmobiliarios --bootstrap-server 192.168.201.162:9094; ~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --all-groups --describe"
    timeout 30 .venv/Scripts/python.exe -c "from kafka import KafkaConsumer; c=KafkaConsumer('anuncios_inmobiliarios', bootstrap_servers='192.168.201.162:9094', group_id='peek_bloque2', auto_offset_reset='earliest', enable_auto_commit=False); try: for m in c: print(m.topic,m.partition,m.offset,m.key,m.value[:500]); break; finally: c.close()"
Salida literal:
    Topic: anuncios_inmobiliarios    TopicId: J045oausTPeWCBdy624l5A    PartitionCount: 3    ReplicationFactor: 1    Configs: min.insync.replicas=2,segment.bytes=1073741824,max.message.bytes=1048588
        Topic: anuncios_inmobiliarios    Partition: 0    Leader: 1    Replicas: 1    Isr: 1    Elr:     LastKnownElr:
        Topic: anuncios_inmobiliarios    Partition: 1    Leader: 1    Replicas: 1    Isr: 1    Elr:     LastKnownElr:
        Topic: anuncios_inmobiliarios    Partition: 2    Leader: 1    Replicas: 1    Isr: 1    Elr:     LastKnownElr:
    anuncios_inmobiliarios:0:0
    anuncios_inmobiliarios:1:0
    anuncios_inmobiliarios:2:1
    TOPIC anuncios_inmobiliarios PART 2 OFFSET 0 KEY None VAL b'{"precio": 850, "municipio": "Bilbao"}'
Conclusión: topic anuncios_inmobiliarios 3 particiones, offsets 0/0/1, sin grupo anuncios creado. Mensaje previo en p2/o0 sin portal/id_anuncio (manual), será descartado por el consumidor; no afecta a los 759. Sin cron, sin console-producer.

### 2026-11-05 Bloque 2 Kafka productor Python 759 (paso 6, tarea 2.2)

Fecha: 2026-11-05
Objetivo: publicar los 759 anuncios con clave portal:id_anuncio, topic/partition/offset via callback
Máquina: broker VM 192.168.201.162:9094 topic anuncios_inmobiliarios, desde Windows
Comando:
    timeout 120 .venv/Scripts/python.exe C:/Users/mikel/AppData/Local/hermes/cache/scratch/publish_adapter.py
       # adapter en scratch (fuera del repo): sys.path repo + CallbackProducer que envuelve KafkaProducer real
       # y traduce send(callback=...) de storage.kafka_producer.produce() a Future.add_callback/add_errback,
       # porque kafka-python 2.2.3 real no admite callback como kwarg de send.
       # Entrypoint directo `.venv/Scripts/python.exe -m storage.kafka_producer` FALLA: TypeError: KafkaProducer.send() got an unexpected keyword argument 'callback' (ver verify-report).
       # Se reutiliza storage.kafka_producer.produce() con inyección (mismo patrón que tests con MagicMock), sin tocar storage/.
Salida literal (759 Publicado + 2 líneas finales, exit 0):
    Publicado topic=anuncios_inmobiliarios partition=0 offset=0
    Publicado topic=anuncios_inmobiliarios partition=0 offset=1
    Publicado topic=anuncios_inmobiliarios partition=0 offset=2
    Publicado topic=anuncios_inmobiliarios partition=0 offset=3
    Publicado topic=anuncios_inmobiliarios partition=0 offset=4
    Publicado topic=anuncios_inmobiliarios partition=0 offset=5
    Publicado topic=anuncios_inmobiliarios partition=0 offset=6
    Publicado topic=anuncios_inmobiliarios partition=0 offset=7
    Publicado topic=anuncios_inmobiliarios partition=0 offset=8
    Publicado topic=anuncios_inmobiliarios partition=0 offset=9
    Publicado topic=anuncios_inmobiliarios partition=0 offset=10
    Publicado topic=anuncios_inmobiliarios partition=0 offset=11
    Publicado topic=anuncios_inmobiliarios partition=0 offset=12
    Publicado topic=anuncios_inmobiliarios partition=0 offset=13
    Publicado topic=anuncios_inmobiliarios partition=0 offset=14
    Publicado topic=anuncios_inmobiliarios partition=0 offset=15
    Publicado topic=anuncios_inmobiliarios partition=0 offset=16
    Publicado topic=anuncios_inmobiliarios partition=0 offset=17
    Publicado topic=anuncios_inmobiliarios partition=0 offset=18
    Publicado topic=anuncios_inmobiliarios partition=0 offset=19
    Publicado topic=anuncios_inmobiliarios partition=0 offset=20
    Publicado topic=anuncios_inmobiliarios partition=0 offset=21
    Publicado topic=anuncios_inmobiliarios partition=0 offset=22
    Publicado topic=anuncios_inmobiliarios partition=0 offset=23
    Publicado topic=anuncios_inmobiliarios partition=0 offset=24
    Publicado topic=anuncios_inmobiliarios partition=0 offset=25
    Publicado topic=anuncios_inmobiliarios partition=0 offset=26
    Publicado topic=anuncios_inmobiliarios partition=0 offset=27
    Publicado topic=anuncios_inmobiliarios partition=0 offset=28
    Publicado topic=anuncios_inmobiliarios partition=0 offset=29
    Publicado topic=anuncios_inmobiliarios partition=0 offset=30
    Publicado topic=anuncios_inmobiliarios partition=0 offset=31
    Publicado topic=anuncios_inmobiliarios partition=0 offset=32
    Publicado topic=anuncios_inmobiliarios partition=0 offset=33
    Publicado topic=anuncios_inmobiliarios partition=0 offset=34
    Publicado topic=anuncios_inmobiliarios partition=0 offset=35
    Publicado topic=anuncios_inmobiliarios partition=0 offset=36
    Publicado topic=anuncios_inmobiliarios partition=0 offset=37
    Publicado topic=anuncios_inmobiliarios partition=0 offset=38
    Publicado topic=anuncios_inmobiliarios partition=0 offset=39
    Publicado topic=anuncios_inmobiliarios partition=0 offset=40
    Publicado topic=anuncios_inmobiliarios partition=0 offset=41
    Publicado topic=anuncios_inmobiliarios partition=0 offset=42
    Publicado topic=anuncios_inmobiliarios partition=0 offset=43
    Publicado topic=anuncios_inmobiliarios partition=0 offset=44
    Publicado topic=anuncios_inmobiliarios partition=0 offset=45
    Publicado topic=anuncios_inmobiliarios partition=0 offset=46
    Publicado topic=anuncios_inmobiliarios partition=0 offset=47
    Publicado topic=anuncios_inmobiliarios partition=0 offset=48
    Publicado topic=anuncios_inmobiliarios partition=0 offset=49
    Publicado topic=anuncios_inmobiliarios partition=0 offset=50
    Publicado topic=anuncios_inmobiliarios partition=0 offset=51
    Publicado topic=anuncios_inmobiliarios partition=0 offset=52
    Publicado topic=anuncios_inmobiliarios partition=0 offset=53
    Publicado topic=anuncios_inmobiliarios partition=0 offset=54
    Publicado topic=anuncios_inmobiliarios partition=0 offset=55
    Publicado topic=anuncios_inmobiliarios partition=0 offset=56
    Publicado topic=anuncios_inmobiliarios partition=0 offset=57
    Publicado topic=anuncios_inmobiliarios partition=0 offset=58
    Publicado topic=anuncios_inmobiliarios partition=0 offset=59
    Publicado topic=anuncios_inmobiliarios partition=0 offset=60
    Publicado topic=anuncios_inmobiliarios partition=0 offset=61
    Publicado topic=anuncios_inmobiliarios partition=0 offset=62
    Publicado topic=anuncios_inmobiliarios partition=0 offset=63
    Publicado topic=anuncios_inmobiliarios partition=2 offset=1
    Publicado topic=anuncios_inmobiliarios partition=2 offset=2
    Publicado topic=anuncios_inmobiliarios partition=2 offset=3
    Publicado topic=anuncios_inmobiliarios partition=2 offset=4
    Publicado topic=anuncios_inmobiliarios partition=2 offset=5
    Publicado topic=anuncios_inmobiliarios partition=2 offset=6
    Publicado topic=anuncios_inmobiliarios partition=2 offset=7
    Publicado topic=anuncios_inmobiliarios partition=2 offset=8
    Publicado topic=anuncios_inmobiliarios partition=2 offset=9
    Publicado topic=anuncios_inmobiliarios partition=2 offset=10
    Publicado topic=anuncios_inmobiliarios partition=2 offset=11
    Publicado topic=anuncios_inmobiliarios partition=2 offset=12
    Publicado topic=anuncios_inmobiliarios partition=2 offset=13
    Publicado topic=anuncios_inmobiliarios partition=2 offset=14
    Publicado topic=anuncios_inmobiliarios partition=2 offset=15
    Publicado topic=anuncios_inmobiliarios partition=2 offset=16
    Publicado topic=anuncios_inmobiliarios partition=2 offset=17
    Publicado topic=anuncios_inmobiliarios partition=2 offset=18
    Publicado topic=anuncios_inmobiliarios partition=2 offset=19
    Publicado topic=anuncios_inmobiliarios partition=2 offset=20
    Publicado topic=anuncios_inmobiliarios partition=2 offset=21
    Publicado topic=anuncios_inmobiliarios partition=2 offset=22
    Publicado topic=anuncios_inmobiliarios partition=2 offset=23
    Publicado topic=anuncios_inmobiliarios partition=2 offset=24
    Publicado topic=anuncios_inmobiliarios partition=2 offset=25
    Publicado topic=anuncios_inmobiliarios partition=2 offset=26
    Publicado topic=anuncios_inmobiliarios partition=2 offset=27
    Publicado topic=anuncios_inmobiliarios partition=2 offset=28
    Publicado topic=anuncios_inmobiliarios partition=2 offset=29
    Publicado topic=anuncios_inmobiliarios partition=2 offset=30
    Publicado topic=anuncios_inmobiliarios partition=2 offset=31
    Publicado topic=anuncios_inmobiliarios partition=2 offset=32
    Publicado topic=anuncios_inmobiliarios partition=2 offset=33
    Publicado topic=anuncios_inmobiliarios partition=2 offset=34
    Publicado topic=anuncios_inmobiliarios partition=2 offset=35
    Publicado topic=anuncios_inmobiliarios partition=2 offset=36
    Publicado topic=anuncios_inmobiliarios partition=2 offset=37
    Publicado topic=anuncios_inmobiliarios partition=2 offset=38
    Publicado topic=anuncios_inmobiliarios partition=2 offset=39
    Publicado topic=anuncios_inmobiliarios partition=2 offset=40
    Publicado topic=anuncios_inmobiliarios partition=2 offset=41
    Publicado topic=anuncios_inmobiliarios partition=2 offset=42
    Publicado topic=anuncios_inmobiliarios partition=2 offset=43
    Publicado topic=anuncios_inmobiliarios partition=2 offset=44
    Publicado topic=anuncios_inmobiliarios partition=2 offset=45
    Publicado topic=anuncios_inmobiliarios partition=2 offset=46
    Publicado topic=anuncios_inmobiliarios partition=2 offset=47
    Publicado topic=anuncios_inmobiliarios partition=2 offset=48
    Publicado topic=anuncios_inmobiliarios partition=2 offset=49
    Publicado topic=anuncios_inmobiliarios partition=2 offset=50
    Publicado topic=anuncios_inmobiliarios partition=2 offset=51
    Publicado topic=anuncios_inmobiliarios partition=2 offset=52
    Publicado topic=anuncios_inmobiliarios partition=2 offset=53
    Publicado topic=anuncios_inmobiliarios partition=2 offset=54
    Publicado topic=anuncios_inmobiliarios partition=2 offset=55
    Publicado topic=anuncios_inmobiliarios partition=2 offset=56
    Publicado topic=anuncios_inmobiliarios partition=2 offset=57
    Publicado topic=anuncios_inmobiliarios partition=2 offset=58
    Publicado topic=anuncios_inmobiliarios partition=2 offset=59
    Publicado topic=anuncios_inmobiliarios partition=2 offset=60
    Publicado topic=anuncios_inmobiliarios partition=1 offset=0
    Publicado topic=anuncios_inmobiliarios partition=1 offset=1
    Publicado topic=anuncios_inmobiliarios partition=1 offset=2
    Publicado topic=anuncios_inmobiliarios partition=1 offset=3
    Publicado topic=anuncios_inmobiliarios partition=1 offset=4
    Publicado topic=anuncios_inmobiliarios partition=1 offset=5
    Publicado topic=anuncios_inmobiliarios partition=1 offset=6
    Publicado topic=anuncios_inmobiliarios partition=1 offset=7
    Publicado topic=anuncios_inmobiliarios partition=1 offset=8
    Publicado topic=anuncios_inmobiliarios partition=1 offset=9
    Publicado topic=anuncios_inmobiliarios partition=1 offset=10
    Publicado topic=anuncios_inmobiliarios partition=1 offset=11
    Publicado topic=anuncios_inmobiliarios partition=1 offset=12
    Publicado topic=anuncios_inmobiliarios partition=1 offset=13
    Publicado topic=anuncios_inmobiliarios partition=1 offset=14
    Publicado topic=anuncios_inmobiliarios partition=1 offset=15
    Publicado topic=anuncios_inmobiliarios partition=1 offset=16
    Publicado topic=anuncios_inmobiliarios partition=1 offset=17
    Publicado topic=anuncios_inmobiliarios partition=1 offset=18
    Publicado topic=anuncios_inmobiliarios partition=1 offset=19
    Publicado topic=anuncios_inmobiliarios partition=1 offset=20
    Publicado topic=anuncios_inmobiliarios partition=1 offset=21
    Publicado topic=anuncios_inmobiliarios partition=1 offset=22
    Publicado topic=anuncios_inmobiliarios partition=1 offset=23
    Publicado topic=anuncios_inmobiliarios partition=1 offset=24
    Publicado topic=anuncios_inmobiliarios partition=1 offset=25
    Publicado topic=anuncios_inmobiliarios partition=1 offset=26
    Publicado topic=anuncios_inmobiliarios partition=1 offset=27
    Publicado topic=anuncios_inmobiliarios partition=1 offset=28
    Publicado topic=anuncios_inmobiliarios partition=1 offset=29
    Publicado topic=anuncios_inmobiliarios partition=1 offset=30
    Publicado topic=anuncios_inmobiliarios partition=1 offset=31
    Publicado topic=anuncios_inmobiliarios partition=1 offset=32
    Publicado topic=anuncios_inmobiliarios partition=1 offset=33
    Publicado topic=anuncios_inmobiliarios partition=1 offset=34
    Publicado topic=anuncios_inmobiliarios partition=1 offset=35
    Publicado topic=anuncios_inmobiliarios partition=1 offset=36
    Publicado topic=anuncios_inmobiliarios partition=1 offset=37
    Publicado topic=anuncios_inmobiliarios partition=1 offset=38
    Publicado topic=anuncios_inmobiliarios partition=1 offset=39
    Publicado topic=anuncios_inmobiliarios partition=1 offset=40
    Publicado topic=anuncios_inmobiliarios partition=1 offset=41
    Publicado topic=anuncios_inmobiliarios partition=1 offset=42
    Publicado topic=anuncios_inmobiliarios partition=1 offset=43
    Publicado topic=anuncios_inmobiliarios partition=1 offset=44
    Publicado topic=anuncios_inmobiliarios partition=1 offset=45
    Publicado topic=anuncios_inmobiliarios partition=1 offset=46
    Publicado topic=anuncios_inmobiliarios partition=1 offset=47
    Publicado topic=anuncios_inmobiliarios partition=1 offset=48
    Publicado topic=anuncios_inmobiliarios partition=1 offset=49
    Publicado topic=anuncios_inmobiliarios partition=1 offset=50
    Publicado topic=anuncios_inmobiliarios partition=1 offset=51
    Publicado topic=anuncios_inmobiliarios partition=1 offset=52
    Publicado topic=anuncios_inmobiliarios partition=1 offset=53
    Publicado topic=anuncios_inmobiliarios partition=1 offset=54
    Publicado topic=anuncios_inmobiliarios partition=1 offset=55
    Publicado topic=anuncios_inmobiliarios partition=1 offset=56
    Publicado topic=anuncios_inmobiliarios partition=1 offset=57
    Publicado topic=anuncios_inmobiliarios partition=1 offset=58
    Publicado topic=anuncios_inmobiliarios partition=1 offset=59
    Publicado topic=anuncios_inmobiliarios partition=1 offset=60
    Publicado topic=anuncios_inmobiliarios partition=1 offset=61
    Publicado topic=anuncios_inmobiliarios partition=1 offset=62
    Publicado topic=anuncios_inmobiliarios partition=1 offset=63
    Publicado topic=anuncios_inmobiliarios partition=1 offset=64
    Publicado topic=anuncios_inmobiliarios partition=1 offset=65
    Publicado topic=anuncios_inmobiliarios partition=1 offset=66
    Publicado topic=anuncios_inmobiliarios partition=1 offset=67
    Publicado topic=anuncios_inmobiliarios partition=1 offset=68
    Publicado topic=anuncios_inmobiliarios partition=1 offset=69
    Publicado topic=anuncios_inmobiliarios partition=1 offset=70
    Publicado topic=anuncios_inmobiliarios partition=1 offset=71
    Publicado topic=anuncios_inmobiliarios partition=1 offset=72
    Publicado topic=anuncios_inmobiliarios partition=1 offset=73
    Publicado topic=anuncios_inmobiliarios partition=2 offset=61
    Publicado topic=anuncios_inmobiliarios partition=1 offset=74
    Publicado topic=anuncios_inmobiliarios partition=1 offset=75
    Publicado topic=anuncios_inmobiliarios partition=1 offset=76
    Publicado topic=anuncios_inmobiliarios partition=1 offset=77
    Publicado topic=anuncios_inmobiliarios partition=1 offset=78
    Publicado topic=anuncios_inmobiliarios partition=2 offset=62
    Publicado topic=anuncios_inmobiliarios partition=0 offset=64
    Publicado topic=anuncios_inmobiliarios partition=2 offset=63
    Publicado topic=anuncios_inmobiliarios partition=0 offset=65
    Publicado topic=anuncios_inmobiliarios partition=0 offset=66
    Publicado topic=anuncios_inmobiliarios partition=0 offset=67
    Publicado topic=anuncios_inmobiliarios partition=0 offset=68
    Publicado topic=anuncios_inmobiliarios partition=0 offset=69
    Publicado topic=anuncios_inmobiliarios partition=0 offset=70
    Publicado topic=anuncios_inmobiliarios partition=0 offset=71
    Publicado topic=anuncios_inmobiliarios partition=0 offset=72
    Publicado topic=anuncios_inmobiliarios partition=0 offset=73
    Publicado topic=anuncios_inmobiliarios partition=0 offset=74
    Publicado topic=anuncios_inmobiliarios partition=0 offset=75
    Publicado topic=anuncios_inmobiliarios partition=0 offset=76
    Publicado topic=anuncios_inmobiliarios partition=0 offset=77
    Publicado topic=anuncios_inmobiliarios partition=0 offset=78
    Publicado topic=anuncios_inmobiliarios partition=0 offset=79
    Publicado topic=anuncios_inmobiliarios partition=0 offset=80
    Publicado topic=anuncios_inmobiliarios partition=0 offset=81
    Publicado topic=anuncios_inmobiliarios partition=0 offset=82
    Publicado topic=anuncios_inmobiliarios partition=0 offset=83
    Publicado topic=anuncios_inmobiliarios partition=0 offset=84
    Publicado topic=anuncios_inmobiliarios partition=0 offset=85
    Publicado topic=anuncios_inmobiliarios partition=0 offset=86
    Publicado topic=anuncios_inmobiliarios partition=0 offset=87
    Publicado topic=anuncios_inmobiliarios partition=0 offset=88
    Publicado topic=anuncios_inmobiliarios partition=0 offset=89
    Publicado topic=anuncios_inmobiliarios partition=0 offset=90
    Publicado topic=anuncios_inmobiliarios partition=0 offset=91
    Publicado topic=anuncios_inmobiliarios partition=0 offset=92
    Publicado topic=anuncios_inmobiliarios partition=0 offset=93
    Publicado topic=anuncios_inmobiliarios partition=0 offset=94
    Publicado topic=anuncios_inmobiliarios partition=0 offset=95
    Publicado topic=anuncios_inmobiliarios partition=0 offset=96
    Publicado topic=anuncios_inmobiliarios partition=0 offset=97
    Publicado topic=anuncios_inmobiliarios partition=0 offset=98
    Publicado topic=anuncios_inmobiliarios partition=0 offset=99
    Publicado topic=anuncios_inmobiliarios partition=0 offset=100
    Publicado topic=anuncios_inmobiliarios partition=0 offset=101
    Publicado topic=anuncios_inmobiliarios partition=0 offset=102
    Publicado topic=anuncios_inmobiliarios partition=0 offset=103
    Publicado topic=anuncios_inmobiliarios partition=0 offset=104
    Publicado topic=anuncios_inmobiliarios partition=0 offset=105
    Publicado topic=anuncios_inmobiliarios partition=0 offset=106
    Publicado topic=anuncios_inmobiliarios partition=0 offset=107
    Publicado topic=anuncios_inmobiliarios partition=0 offset=108
    Publicado topic=anuncios_inmobiliarios partition=0 offset=109
    Publicado topic=anuncios_inmobiliarios partition=0 offset=110
    Publicado topic=anuncios_inmobiliarios partition=0 offset=111
    Publicado topic=anuncios_inmobiliarios partition=0 offset=112
    Publicado topic=anuncios_inmobiliarios partition=0 offset=113
    Publicado topic=anuncios_inmobiliarios partition=0 offset=114
    Publicado topic=anuncios_inmobiliarios partition=0 offset=115
    Publicado topic=anuncios_inmobiliarios partition=0 offset=116
    Publicado topic=anuncios_inmobiliarios partition=0 offset=117
    Publicado topic=anuncios_inmobiliarios partition=0 offset=118
    Publicado topic=anuncios_inmobiliarios partition=0 offset=119
    Publicado topic=anuncios_inmobiliarios partition=0 offset=120
    Publicado topic=anuncios_inmobiliarios partition=0 offset=121
    Publicado topic=anuncios_inmobiliarios partition=0 offset=122
    Publicado topic=anuncios_inmobiliarios partition=0 offset=123
    Publicado topic=anuncios_inmobiliarios partition=0 offset=124
    Publicado topic=anuncios_inmobiliarios partition=0 offset=125
    Publicado topic=anuncios_inmobiliarios partition=0 offset=126
    Publicado topic=anuncios_inmobiliarios partition=0 offset=127
    Publicado topic=anuncios_inmobiliarios partition=0 offset=128
    Publicado topic=anuncios_inmobiliarios partition=0 offset=129
    Publicado topic=anuncios_inmobiliarios partition=0 offset=130
    Publicado topic=anuncios_inmobiliarios partition=0 offset=131
    Publicado topic=anuncios_inmobiliarios partition=0 offset=132
    Publicado topic=anuncios_inmobiliarios partition=0 offset=133
    Publicado topic=anuncios_inmobiliarios partition=0 offset=134
    Publicado topic=anuncios_inmobiliarios partition=0 offset=135
    Publicado topic=anuncios_inmobiliarios partition=0 offset=136
    Publicado topic=anuncios_inmobiliarios partition=0 offset=137
    Publicado topic=anuncios_inmobiliarios partition=0 offset=138
    Publicado topic=anuncios_inmobiliarios partition=2 offset=64
    Publicado topic=anuncios_inmobiliarios partition=2 offset=65
    Publicado topic=anuncios_inmobiliarios partition=2 offset=66
    Publicado topic=anuncios_inmobiliarios partition=2 offset=67
    Publicado topic=anuncios_inmobiliarios partition=2 offset=68
    Publicado topic=anuncios_inmobiliarios partition=2 offset=69
    Publicado topic=anuncios_inmobiliarios partition=2 offset=70
    Publicado topic=anuncios_inmobiliarios partition=2 offset=71
    Publicado topic=anuncios_inmobiliarios partition=2 offset=72
    Publicado topic=anuncios_inmobiliarios partition=2 offset=73
    Publicado topic=anuncios_inmobiliarios partition=2 offset=74
    Publicado topic=anuncios_inmobiliarios partition=2 offset=75
    Publicado topic=anuncios_inmobiliarios partition=2 offset=76
    Publicado topic=anuncios_inmobiliarios partition=2 offset=77
    Publicado topic=anuncios_inmobiliarios partition=2 offset=78
    Publicado topic=anuncios_inmobiliarios partition=2 offset=79
    Publicado topic=anuncios_inmobiliarios partition=2 offset=80
    Publicado topic=anuncios_inmobiliarios partition=2 offset=81
    Publicado topic=anuncios_inmobiliarios partition=2 offset=82
    Publicado topic=anuncios_inmobiliarios partition=2 offset=83
    Publicado topic=anuncios_inmobiliarios partition=2 offset=84
    Publicado topic=anuncios_inmobiliarios partition=2 offset=85
    Publicado topic=anuncios_inmobiliarios partition=2 offset=86
    Publicado topic=anuncios_inmobiliarios partition=2 offset=87
    Publicado topic=anuncios_inmobiliarios partition=2 offset=88
    Publicado topic=anuncios_inmobiliarios partition=2 offset=89
    Publicado topic=anuncios_inmobiliarios partition=2 offset=90
    Publicado topic=anuncios_inmobiliarios partition=2 offset=91
    Publicado topic=anuncios_inmobiliarios partition=2 offset=92
    Publicado topic=anuncios_inmobiliarios partition=2 offset=93
    Publicado topic=anuncios_inmobiliarios partition=2 offset=94
    Publicado topic=anuncios_inmobiliarios partition=2 offset=95
    Publicado topic=anuncios_inmobiliarios partition=2 offset=96
    Publicado topic=anuncios_inmobiliarios partition=2 offset=97
    Publicado topic=anuncios_inmobiliarios partition=2 offset=98
    Publicado topic=anuncios_inmobiliarios partition=2 offset=99
    Publicado topic=anuncios_inmobiliarios partition=2 offset=100
    Publicado topic=anuncios_inmobiliarios partition=2 offset=101
    Publicado topic=anuncios_inmobiliarios partition=2 offset=102
    Publicado topic=anuncios_inmobiliarios partition=2 offset=103
    Publicado topic=anuncios_inmobiliarios partition=2 offset=104
    Publicado topic=anuncios_inmobiliarios partition=2 offset=105
    Publicado topic=anuncios_inmobiliarios partition=2 offset=106
    Publicado topic=anuncios_inmobiliarios partition=2 offset=107
    Publicado topic=anuncios_inmobiliarios partition=2 offset=108
    Publicado topic=anuncios_inmobiliarios partition=2 offset=109
    Publicado topic=anuncios_inmobiliarios partition=2 offset=110
    Publicado topic=anuncios_inmobiliarios partition=2 offset=111
    Publicado topic=anuncios_inmobiliarios partition=2 offset=112
    Publicado topic=anuncios_inmobiliarios partition=2 offset=113
    Publicado topic=anuncios_inmobiliarios partition=2 offset=114
    Publicado topic=anuncios_inmobiliarios partition=2 offset=115
    Publicado topic=anuncios_inmobiliarios partition=2 offset=116
    Publicado topic=anuncios_inmobiliarios partition=2 offset=117
    Publicado topic=anuncios_inmobiliarios partition=2 offset=118
    Publicado topic=anuncios_inmobiliarios partition=2 offset=119
    Publicado topic=anuncios_inmobiliarios partition=2 offset=120
    Publicado topic=anuncios_inmobiliarios partition=2 offset=121
    Publicado topic=anuncios_inmobiliarios partition=2 offset=122
    Publicado topic=anuncios_inmobiliarios partition=2 offset=123
    Publicado topic=anuncios_inmobiliarios partition=2 offset=124
    Publicado topic=anuncios_inmobiliarios partition=2 offset=125
    Publicado topic=anuncios_inmobiliarios partition=2 offset=126
    Publicado topic=anuncios_inmobiliarios partition=2 offset=127
    Publicado topic=anuncios_inmobiliarios partition=2 offset=128
    Publicado topic=anuncios_inmobiliarios partition=2 offset=129
    Publicado topic=anuncios_inmobiliarios partition=2 offset=130
    Publicado topic=anuncios_inmobiliarios partition=2 offset=131
    Publicado topic=anuncios_inmobiliarios partition=2 offset=132
    Publicado topic=anuncios_inmobiliarios partition=2 offset=133
    Publicado topic=anuncios_inmobiliarios partition=2 offset=134
    Publicado topic=anuncios_inmobiliarios partition=2 offset=135
    Publicado topic=anuncios_inmobiliarios partition=1 offset=79
    Publicado topic=anuncios_inmobiliarios partition=1 offset=80
    Publicado topic=anuncios_inmobiliarios partition=1 offset=81
    Publicado topic=anuncios_inmobiliarios partition=1 offset=82
    Publicado topic=anuncios_inmobiliarios partition=1 offset=83
    Publicado topic=anuncios_inmobiliarios partition=1 offset=84
    Publicado topic=anuncios_inmobiliarios partition=1 offset=85
    Publicado topic=anuncios_inmobiliarios partition=1 offset=86
    Publicado topic=anuncios_inmobiliarios partition=1 offset=87
    Publicado topic=anuncios_inmobiliarios partition=1 offset=88
    Publicado topic=anuncios_inmobiliarios partition=1 offset=89
    Publicado topic=anuncios_inmobiliarios partition=1 offset=90
    Publicado topic=anuncios_inmobiliarios partition=1 offset=91
    Publicado topic=anuncios_inmobiliarios partition=1 offset=92
    Publicado topic=anuncios_inmobiliarios partition=1 offset=93
    Publicado topic=anuncios_inmobiliarios partition=1 offset=94
    Publicado topic=anuncios_inmobiliarios partition=1 offset=95
    Publicado topic=anuncios_inmobiliarios partition=1 offset=96
    Publicado topic=anuncios_inmobiliarios partition=1 offset=97
    Publicado topic=anuncios_inmobiliarios partition=1 offset=98
    Publicado topic=anuncios_inmobiliarios partition=1 offset=99
    Publicado topic=anuncios_inmobiliarios partition=1 offset=100
    Publicado topic=anuncios_inmobiliarios partition=1 offset=101
    Publicado topic=anuncios_inmobiliarios partition=1 offset=102
    Publicado topic=anuncios_inmobiliarios partition=1 offset=103
    Publicado topic=anuncios_inmobiliarios partition=1 offset=104
    Publicado topic=anuncios_inmobiliarios partition=1 offset=105
    Publicado topic=anuncios_inmobiliarios partition=1 offset=106
    Publicado topic=anuncios_inmobiliarios partition=1 offset=107
    Publicado topic=anuncios_inmobiliarios partition=1 offset=108
    Publicado topic=anuncios_inmobiliarios partition=1 offset=109
    Publicado topic=anuncios_inmobiliarios partition=1 offset=110
    Publicado topic=anuncios_inmobiliarios partition=1 offset=111
    Publicado topic=anuncios_inmobiliarios partition=1 offset=112
    Publicado topic=anuncios_inmobiliarios partition=1 offset=113
    Publicado topic=anuncios_inmobiliarios partition=1 offset=114
    Publicado topic=anuncios_inmobiliarios partition=1 offset=115
    Publicado topic=anuncios_inmobiliarios partition=1 offset=116
    Publicado topic=anuncios_inmobiliarios partition=1 offset=117
    Publicado topic=anuncios_inmobiliarios partition=1 offset=118
    Publicado topic=anuncios_inmobiliarios partition=1 offset=119
    Publicado topic=anuncios_inmobiliarios partition=1 offset=120
    Publicado topic=anuncios_inmobiliarios partition=1 offset=121
    Publicado topic=anuncios_inmobiliarios partition=1 offset=122
    Publicado topic=anuncios_inmobiliarios partition=1 offset=123
    Publicado topic=anuncios_inmobiliarios partition=1 offset=124
    Publicado topic=anuncios_inmobiliarios partition=1 offset=125
    Publicado topic=anuncios_inmobiliarios partition=1 offset=126
    Publicado topic=anuncios_inmobiliarios partition=1 offset=127
    Publicado topic=anuncios_inmobiliarios partition=1 offset=128
    Publicado topic=anuncios_inmobiliarios partition=1 offset=129
    Publicado topic=anuncios_inmobiliarios partition=1 offset=130
    Publicado topic=anuncios_inmobiliarios partition=1 offset=131
    Publicado topic=anuncios_inmobiliarios partition=1 offset=132
    Publicado topic=anuncios_inmobiliarios partition=1 offset=133
    Publicado topic=anuncios_inmobiliarios partition=1 offset=134
    Publicado topic=anuncios_inmobiliarios partition=1 offset=135
    Publicado topic=anuncios_inmobiliarios partition=1 offset=136
    Publicado topic=anuncios_inmobiliarios partition=1 offset=137
    Publicado topic=anuncios_inmobiliarios partition=1 offset=138
    Publicado topic=anuncios_inmobiliarios partition=1 offset=139
    Publicado topic=anuncios_inmobiliarios partition=1 offset=140
    Publicado topic=anuncios_inmobiliarios partition=1 offset=141
    Publicado topic=anuncios_inmobiliarios partition=1 offset=142
    Publicado topic=anuncios_inmobiliarios partition=1 offset=143
    Publicado topic=anuncios_inmobiliarios partition=1 offset=144
    Publicado topic=anuncios_inmobiliarios partition=1 offset=145
    Publicado topic=anuncios_inmobiliarios partition=1 offset=146
    Publicado topic=anuncios_inmobiliarios partition=1 offset=147
    Publicado topic=anuncios_inmobiliarios partition=1 offset=148
    Publicado topic=anuncios_inmobiliarios partition=1 offset=149
    Publicado topic=anuncios_inmobiliarios partition=1 offset=150
    Publicado topic=anuncios_inmobiliarios partition=1 offset=151
    Publicado topic=anuncios_inmobiliarios partition=1 offset=152
    Publicado topic=anuncios_inmobiliarios partition=0 offset=139
    Publicado topic=anuncios_inmobiliarios partition=0 offset=140
    Publicado topic=anuncios_inmobiliarios partition=0 offset=141
    Publicado topic=anuncios_inmobiliarios partition=0 offset=142
    Publicado topic=anuncios_inmobiliarios partition=0 offset=143
    Publicado topic=anuncios_inmobiliarios partition=0 offset=144
    Publicado topic=anuncios_inmobiliarios partition=0 offset=145
    Publicado topic=anuncios_inmobiliarios partition=0 offset=146
    Publicado topic=anuncios_inmobiliarios partition=0 offset=147
    Publicado topic=anuncios_inmobiliarios partition=0 offset=148
    Publicado topic=anuncios_inmobiliarios partition=0 offset=149
    Publicado topic=anuncios_inmobiliarios partition=0 offset=150
    Publicado topic=anuncios_inmobiliarios partition=0 offset=151
    Publicado topic=anuncios_inmobiliarios partition=0 offset=152
    Publicado topic=anuncios_inmobiliarios partition=0 offset=153
    Publicado topic=anuncios_inmobiliarios partition=0 offset=154
    Publicado topic=anuncios_inmobiliarios partition=0 offset=155
    Publicado topic=anuncios_inmobiliarios partition=0 offset=156
    Publicado topic=anuncios_inmobiliarios partition=0 offset=157
    Publicado topic=anuncios_inmobiliarios partition=0 offset=158
    Publicado topic=anuncios_inmobiliarios partition=0 offset=159
    Publicado topic=anuncios_inmobiliarios partition=0 offset=160
    Publicado topic=anuncios_inmobiliarios partition=0 offset=161
    Publicado topic=anuncios_inmobiliarios partition=0 offset=162
    Publicado topic=anuncios_inmobiliarios partition=0 offset=163
    Publicado topic=anuncios_inmobiliarios partition=0 offset=164
    Publicado topic=anuncios_inmobiliarios partition=0 offset=165
    Publicado topic=anuncios_inmobiliarios partition=0 offset=166
    Publicado topic=anuncios_inmobiliarios partition=0 offset=167
    Publicado topic=anuncios_inmobiliarios partition=0 offset=168
    Publicado topic=anuncios_inmobiliarios partition=0 offset=169
    Publicado topic=anuncios_inmobiliarios partition=0 offset=170
    Publicado topic=anuncios_inmobiliarios partition=0 offset=171
    Publicado topic=anuncios_inmobiliarios partition=0 offset=172
    Publicado topic=anuncios_inmobiliarios partition=0 offset=173
    Publicado topic=anuncios_inmobiliarios partition=0 offset=174
    Publicado topic=anuncios_inmobiliarios partition=0 offset=175
    Publicado topic=anuncios_inmobiliarios partition=0 offset=176
    Publicado topic=anuncios_inmobiliarios partition=0 offset=177
    Publicado topic=anuncios_inmobiliarios partition=0 offset=178
    Publicado topic=anuncios_inmobiliarios partition=0 offset=179
    Publicado topic=anuncios_inmobiliarios partition=0 offset=180
    Publicado topic=anuncios_inmobiliarios partition=0 offset=181
    Publicado topic=anuncios_inmobiliarios partition=0 offset=182
    Publicado topic=anuncios_inmobiliarios partition=0 offset=183
    Publicado topic=anuncios_inmobiliarios partition=0 offset=184
    Publicado topic=anuncios_inmobiliarios partition=0 offset=185
    Publicado topic=anuncios_inmobiliarios partition=0 offset=186
    Publicado topic=anuncios_inmobiliarios partition=0 offset=187
    Publicado topic=anuncios_inmobiliarios partition=0 offset=188
    Publicado topic=anuncios_inmobiliarios partition=0 offset=189
    Publicado topic=anuncios_inmobiliarios partition=0 offset=190
    Publicado topic=anuncios_inmobiliarios partition=0 offset=191
    Publicado topic=anuncios_inmobiliarios partition=0 offset=192
    Publicado topic=anuncios_inmobiliarios partition=0 offset=193
    Publicado topic=anuncios_inmobiliarios partition=0 offset=194
    Publicado topic=anuncios_inmobiliarios partition=0 offset=195
    Publicado topic=anuncios_inmobiliarios partition=0 offset=196
    Publicado topic=anuncios_inmobiliarios partition=2 offset=136
    Publicado topic=anuncios_inmobiliarios partition=2 offset=137
    Publicado topic=anuncios_inmobiliarios partition=2 offset=138
    Publicado topic=anuncios_inmobiliarios partition=2 offset=139
    Publicado topic=anuncios_inmobiliarios partition=2 offset=140
    Publicado topic=anuncios_inmobiliarios partition=2 offset=141
    Publicado topic=anuncios_inmobiliarios partition=2 offset=142
    Publicado topic=anuncios_inmobiliarios partition=2 offset=143
    Publicado topic=anuncios_inmobiliarios partition=2 offset=144
    Publicado topic=anuncios_inmobiliarios partition=2 offset=145
    Publicado topic=anuncios_inmobiliarios partition=2 offset=146
    Publicado topic=anuncios_inmobiliarios partition=2 offset=147
    Publicado topic=anuncios_inmobiliarios partition=2 offset=148
    Publicado topic=anuncios_inmobiliarios partition=2 offset=149
    Publicado topic=anuncios_inmobiliarios partition=2 offset=150
    Publicado topic=anuncios_inmobiliarios partition=2 offset=151
    Publicado topic=anuncios_inmobiliarios partition=2 offset=152
    Publicado topic=anuncios_inmobiliarios partition=2 offset=153
    Publicado topic=anuncios_inmobiliarios partition=2 offset=154
    Publicado topic=anuncios_inmobiliarios partition=2 offset=155
    Publicado topic=anuncios_inmobiliarios partition=2 offset=156
    Publicado topic=anuncios_inmobiliarios partition=2 offset=157
    Publicado topic=anuncios_inmobiliarios partition=2 offset=158
    Publicado topic=anuncios_inmobiliarios partition=2 offset=159
    Publicado topic=anuncios_inmobiliarios partition=2 offset=160
    Publicado topic=anuncios_inmobiliarios partition=2 offset=161
    Publicado topic=anuncios_inmobiliarios partition=2 offset=162
    Publicado topic=anuncios_inmobiliarios partition=2 offset=163
    Publicado topic=anuncios_inmobiliarios partition=2 offset=164
    Publicado topic=anuncios_inmobiliarios partition=2 offset=165
    Publicado topic=anuncios_inmobiliarios partition=2 offset=166
    Publicado topic=anuncios_inmobiliarios partition=2 offset=167
    Publicado topic=anuncios_inmobiliarios partition=2 offset=168
    Publicado topic=anuncios_inmobiliarios partition=2 offset=169
    Publicado topic=anuncios_inmobiliarios partition=2 offset=170
    Publicado topic=anuncios_inmobiliarios partition=2 offset=171
    Publicado topic=anuncios_inmobiliarios partition=2 offset=172
    Publicado topic=anuncios_inmobiliarios partition=2 offset=173
    Publicado topic=anuncios_inmobiliarios partition=2 offset=174
    Publicado topic=anuncios_inmobiliarios partition=2 offset=175
    Publicado topic=anuncios_inmobiliarios partition=2 offset=176
    Publicado topic=anuncios_inmobiliarios partition=2 offset=177
    Publicado topic=anuncios_inmobiliarios partition=2 offset=178
    Publicado topic=anuncios_inmobiliarios partition=2 offset=179
    Publicado topic=anuncios_inmobiliarios partition=2 offset=180
    Publicado topic=anuncios_inmobiliarios partition=2 offset=181
    Publicado topic=anuncios_inmobiliarios partition=2 offset=182
    Publicado topic=anuncios_inmobiliarios partition=2 offset=183
    Publicado topic=anuncios_inmobiliarios partition=2 offset=184
    Publicado topic=anuncios_inmobiliarios partition=2 offset=185
    Publicado topic=anuncios_inmobiliarios partition=2 offset=186
    Publicado topic=anuncios_inmobiliarios partition=2 offset=187
    Publicado topic=anuncios_inmobiliarios partition=2 offset=188
    Publicado topic=anuncios_inmobiliarios partition=2 offset=189
    Publicado topic=anuncios_inmobiliarios partition=2 offset=190
    Publicado topic=anuncios_inmobiliarios partition=2 offset=191
    Publicado topic=anuncios_inmobiliarios partition=2 offset=192
    Publicado topic=anuncios_inmobiliarios partition=1 offset=153
    Publicado topic=anuncios_inmobiliarios partition=1 offset=154
    Publicado topic=anuncios_inmobiliarios partition=1 offset=155
    Publicado topic=anuncios_inmobiliarios partition=1 offset=156
    Publicado topic=anuncios_inmobiliarios partition=1 offset=157
    Publicado topic=anuncios_inmobiliarios partition=1 offset=158
    Publicado topic=anuncios_inmobiliarios partition=1 offset=159
    Publicado topic=anuncios_inmobiliarios partition=1 offset=160
    Publicado topic=anuncios_inmobiliarios partition=1 offset=161
    Publicado topic=anuncios_inmobiliarios partition=1 offset=162
    Publicado topic=anuncios_inmobiliarios partition=1 offset=163
    Publicado topic=anuncios_inmobiliarios partition=1 offset=164
    Publicado topic=anuncios_inmobiliarios partition=1 offset=165
    Publicado topic=anuncios_inmobiliarios partition=1 offset=166
    Publicado topic=anuncios_inmobiliarios partition=1 offset=167
    Publicado topic=anuncios_inmobiliarios partition=1 offset=168
    Publicado topic=anuncios_inmobiliarios partition=1 offset=169
    Publicado topic=anuncios_inmobiliarios partition=1 offset=170
    Publicado topic=anuncios_inmobiliarios partition=1 offset=171
    Publicado topic=anuncios_inmobiliarios partition=1 offset=172
    Publicado topic=anuncios_inmobiliarios partition=1 offset=173
    Publicado topic=anuncios_inmobiliarios partition=1 offset=174
    Publicado topic=anuncios_inmobiliarios partition=1 offset=175
    Publicado topic=anuncios_inmobiliarios partition=1 offset=176
    Publicado topic=anuncios_inmobiliarios partition=1 offset=177
    Publicado topic=anuncios_inmobiliarios partition=1 offset=178
    Publicado topic=anuncios_inmobiliarios partition=1 offset=179
    Publicado topic=anuncios_inmobiliarios partition=1 offset=180
    Publicado topic=anuncios_inmobiliarios partition=1 offset=181
    Publicado topic=anuncios_inmobiliarios partition=1 offset=182
    Publicado topic=anuncios_inmobiliarios partition=1 offset=183
    Publicado topic=anuncios_inmobiliarios partition=1 offset=184
    Publicado topic=anuncios_inmobiliarios partition=1 offset=185
    Publicado topic=anuncios_inmobiliarios partition=1 offset=186
    Publicado topic=anuncios_inmobiliarios partition=1 offset=187
    Publicado topic=anuncios_inmobiliarios partition=1 offset=188
    Publicado topic=anuncios_inmobiliarios partition=1 offset=189
    Publicado topic=anuncios_inmobiliarios partition=1 offset=190
    Publicado topic=anuncios_inmobiliarios partition=1 offset=191
    Publicado topic=anuncios_inmobiliarios partition=1 offset=192
    Publicado topic=anuncios_inmobiliarios partition=1 offset=193
    Publicado topic=anuncios_inmobiliarios partition=1 offset=194
    Publicado topic=anuncios_inmobiliarios partition=1 offset=195
    Publicado topic=anuncios_inmobiliarios partition=1 offset=196
    Publicado topic=anuncios_inmobiliarios partition=1 offset=197
    Publicado topic=anuncios_inmobiliarios partition=1 offset=198
    Publicado topic=anuncios_inmobiliarios partition=1 offset=199
    Publicado topic=anuncios_inmobiliarios partition=1 offset=200
    Publicado topic=anuncios_inmobiliarios partition=1 offset=201
    Publicado topic=anuncios_inmobiliarios partition=1 offset=202
    Publicado topic=anuncios_inmobiliarios partition=1 offset=203
    Publicado topic=anuncios_inmobiliarios partition=1 offset=204
    Publicado topic=anuncios_inmobiliarios partition=1 offset=205
    Publicado topic=anuncios_inmobiliarios partition=1 offset=206
    Publicado topic=anuncios_inmobiliarios partition=1 offset=207
    Publicado topic=anuncios_inmobiliarios partition=1 offset=208
    Publicado topic=anuncios_inmobiliarios partition=1 offset=209
    Publicado topic=anuncios_inmobiliarios partition=0 offset=197
    Publicado topic=anuncios_inmobiliarios partition=0 offset=198
    Publicado topic=anuncios_inmobiliarios partition=0 offset=199
    Publicado topic=anuncios_inmobiliarios partition=0 offset=200
    Publicado topic=anuncios_inmobiliarios partition=0 offset=201
    Publicado topic=anuncios_inmobiliarios partition=0 offset=202
    Publicado topic=anuncios_inmobiliarios partition=0 offset=203
    Publicado topic=anuncios_inmobiliarios partition=0 offset=204
    Publicado topic=anuncios_inmobiliarios partition=0 offset=205
    Publicado topic=anuncios_inmobiliarios partition=0 offset=206
    Publicado topic=anuncios_inmobiliarios partition=0 offset=207
    Publicado topic=anuncios_inmobiliarios partition=0 offset=208
    Publicado topic=anuncios_inmobiliarios partition=0 offset=209
    Publicado topic=anuncios_inmobiliarios partition=0 offset=210
    Publicado topic=anuncios_inmobiliarios partition=0 offset=211
    Publicado topic=anuncios_inmobiliarios partition=0 offset=212
    Publicado topic=anuncios_inmobiliarios partition=0 offset=213
    Publicado topic=anuncios_inmobiliarios partition=0 offset=214
    Publicado topic=anuncios_inmobiliarios partition=0 offset=215
    Publicado topic=anuncios_inmobiliarios partition=0 offset=216
    Publicado topic=anuncios_inmobiliarios partition=0 offset=217
    Publicado topic=anuncios_inmobiliarios partition=0 offset=218
    Publicado topic=anuncios_inmobiliarios partition=0 offset=219
    Publicado topic=anuncios_inmobiliarios partition=0 offset=220
    Publicado topic=anuncios_inmobiliarios partition=0 offset=221
    Publicado topic=anuncios_inmobiliarios partition=0 offset=222
    Publicado topic=anuncios_inmobiliarios partition=0 offset=223
    Publicado topic=anuncios_inmobiliarios partition=0 offset=224
    Publicado topic=anuncios_inmobiliarios partition=0 offset=225
    Publicado topic=anuncios_inmobiliarios partition=0 offset=226
    Publicado topic=anuncios_inmobiliarios partition=0 offset=227
    Publicado topic=anuncios_inmobiliarios partition=0 offset=228
    Publicado topic=anuncios_inmobiliarios partition=0 offset=229
    Publicado topic=anuncios_inmobiliarios partition=0 offset=230
    Publicado topic=anuncios_inmobiliarios partition=0 offset=231
    Publicado topic=anuncios_inmobiliarios partition=0 offset=232
    Publicado topic=anuncios_inmobiliarios partition=0 offset=233
    Publicado topic=anuncios_inmobiliarios partition=0 offset=234
    Publicado topic=anuncios_inmobiliarios partition=0 offset=235
    Publicado topic=anuncios_inmobiliarios partition=0 offset=236
    Publicado topic=anuncios_inmobiliarios partition=0 offset=237
    Publicado topic=anuncios_inmobiliarios partition=0 offset=238
    Publicado topic=anuncios_inmobiliarios partition=0 offset=239
    Publicado topic=anuncios_inmobiliarios partition=0 offset=240
    Publicado topic=anuncios_inmobiliarios partition=0 offset=241
    Publicado topic=anuncios_inmobiliarios partition=0 offset=242
    Publicado topic=anuncios_inmobiliarios partition=0 offset=243
    Publicado topic=anuncios_inmobiliarios partition=0 offset=244
    Publicado topic=anuncios_inmobiliarios partition=0 offset=245
    Publicado topic=anuncios_inmobiliarios partition=0 offset=246
    Publicado topic=anuncios_inmobiliarios partition=0 offset=247
    Publicado topic=anuncios_inmobiliarios partition=0 offset=248
    Publicado topic=anuncios_inmobiliarios partition=0 offset=249
    Publicado topic=anuncios_inmobiliarios partition=0 offset=250
    Publicado topic=anuncios_inmobiliarios partition=0 offset=251
    Publicado topic=anuncios_inmobiliarios partition=0 offset=252
    Publicado topic=anuncios_inmobiliarios partition=0 offset=253
    Publicado topic=anuncios_inmobiliarios partition=0 offset=254
    Publicado topic=anuncios_inmobiliarios partition=0 offset=255
    Publicado topic=anuncios_inmobiliarios partition=0 offset=256
    Publicado topic=anuncios_inmobiliarios partition=2 offset=193
    Publicado topic=anuncios_inmobiliarios partition=2 offset=194
    Publicado topic=anuncios_inmobiliarios partition=2 offset=195
    Publicado topic=anuncios_inmobiliarios partition=2 offset=196
    Publicado topic=anuncios_inmobiliarios partition=2 offset=197
    Publicado topic=anuncios_inmobiliarios partition=2 offset=198
    Publicado topic=anuncios_inmobiliarios partition=2 offset=199
    Publicado topic=anuncios_inmobiliarios partition=2 offset=200
    Publicado topic=anuncios_inmobiliarios partition=2 offset=201
    Publicado topic=anuncios_inmobiliarios partition=2 offset=202
    Publicado topic=anuncios_inmobiliarios partition=2 offset=203
    Publicado topic=anuncios_inmobiliarios partition=2 offset=204
    Publicado topic=anuncios_inmobiliarios partition=2 offset=205
    Publicado topic=anuncios_inmobiliarios partition=2 offset=206
    Publicado topic=anuncios_inmobiliarios partition=2 offset=207
    Publicado topic=anuncios_inmobiliarios partition=2 offset=208
    Publicado topic=anuncios_inmobiliarios partition=2 offset=209
    Publicado topic=anuncios_inmobiliarios partition=2 offset=210
    Publicado topic=anuncios_inmobiliarios partition=2 offset=211
    Publicado topic=anuncios_inmobiliarios partition=2 offset=212
    Publicado topic=anuncios_inmobiliarios partition=2 offset=213
    Publicado topic=anuncios_inmobiliarios partition=2 offset=214
    Publicado topic=anuncios_inmobiliarios partition=2 offset=215
    Publicado topic=anuncios_inmobiliarios partition=2 offset=216
    Publicado topic=anuncios_inmobiliarios partition=2 offset=217
    Publicado topic=anuncios_inmobiliarios partition=2 offset=218
    Publicado topic=anuncios_inmobiliarios partition=2 offset=219
    Publicado topic=anuncios_inmobiliarios partition=2 offset=220
    Publicado topic=anuncios_inmobiliarios partition=2 offset=221
    Publicado topic=anuncios_inmobiliarios partition=2 offset=222
    Publicado topic=anuncios_inmobiliarios partition=2 offset=223
    Publicado topic=anuncios_inmobiliarios partition=2 offset=224
    Publicado topic=anuncios_inmobiliarios partition=2 offset=225
    Publicado topic=anuncios_inmobiliarios partition=2 offset=226
    Publicado topic=anuncios_inmobiliarios partition=2 offset=227
    Publicado topic=anuncios_inmobiliarios partition=2 offset=228
    Publicado topic=anuncios_inmobiliarios partition=2 offset=229
    Publicado topic=anuncios_inmobiliarios partition=2 offset=230
    Publicado topic=anuncios_inmobiliarios partition=2 offset=231
    Publicado topic=anuncios_inmobiliarios partition=2 offset=232
    Publicado topic=anuncios_inmobiliarios partition=2 offset=233
    Publicado topic=anuncios_inmobiliarios partition=2 offset=234
    Publicado topic=anuncios_inmobiliarios partition=2 offset=235
    Publicado topic=anuncios_inmobiliarios partition=2 offset=236
    Publicado topic=anuncios_inmobiliarios partition=2 offset=237
    Publicado topic=anuncios_inmobiliarios partition=2 offset=238
    Publicado topic=anuncios_inmobiliarios partition=2 offset=239
    Publicado topic=anuncios_inmobiliarios partition=2 offset=240
    Publicado topic=anuncios_inmobiliarios partition=2 offset=241
    Publicado topic=anuncios_inmobiliarios partition=1 offset=210
    Publicado topic=anuncios_inmobiliarios partition=1 offset=211
    Publicado topic=anuncios_inmobiliarios partition=1 offset=212
    Publicado topic=anuncios_inmobiliarios partition=1 offset=213
    Publicado topic=anuncios_inmobiliarios partition=1 offset=214
    Publicado topic=anuncios_inmobiliarios partition=1 offset=215
    Publicado topic=anuncios_inmobiliarios partition=1 offset=216
    Publicado topic=anuncios_inmobiliarios partition=1 offset=217
    Publicado topic=anuncios_inmobiliarios partition=1 offset=218
    Publicado topic=anuncios_inmobiliarios partition=1 offset=219
    Publicado topic=anuncios_inmobiliarios partition=1 offset=220
    Publicado topic=anuncios_inmobiliarios partition=1 offset=221
    Publicado topic=anuncios_inmobiliarios partition=1 offset=222
    Publicado topic=anuncios_inmobiliarios partition=1 offset=223
    Publicado topic=anuncios_inmobiliarios partition=1 offset=224
    Publicado topic=anuncios_inmobiliarios partition=1 offset=225
    Publicado topic=anuncios_inmobiliarios partition=1 offset=226
    Publicado topic=anuncios_inmobiliarios partition=1 offset=227
    Publicado topic=anuncios_inmobiliarios partition=1 offset=228
    Publicado topic=anuncios_inmobiliarios partition=1 offset=229
    Publicado topic=anuncios_inmobiliarios partition=1 offset=230
    Publicado topic=anuncios_inmobiliarios partition=1 offset=231
    Publicado topic=anuncios_inmobiliarios partition=1 offset=232
    Publicado topic=anuncios_inmobiliarios partition=1 offset=233
    Publicado topic=anuncios_inmobiliarios partition=1 offset=234
    Publicado topic=anuncios_inmobiliarios partition=1 offset=235
    Publicado topic=anuncios_inmobiliarios partition=1 offset=236
    Publicado topic=anuncios_inmobiliarios partition=1 offset=237
    Publicado topic=anuncios_inmobiliarios partition=1 offset=238
    Publicado topic=anuncios_inmobiliarios partition=1 offset=239
    Publicado topic=anuncios_inmobiliarios partition=1 offset=240
    Publicado topic=anuncios_inmobiliarios partition=1 offset=241
    Publicado topic=anuncios_inmobiliarios partition=1 offset=242
    Publicado topic=anuncios_inmobiliarios partition=1 offset=243
    Publicado topic=anuncios_inmobiliarios partition=1 offset=244
    Publicado topic=anuncios_inmobiliarios partition=1 offset=245
    Publicado topic=anuncios_inmobiliarios partition=1 offset=246
    Publicado topic=anuncios_inmobiliarios partition=1 offset=247
    Publicado topic=anuncios_inmobiliarios partition=1 offset=248
    Publicado topic=anuncios_inmobiliarios partition=1 offset=249
    Publicado topic=anuncios_inmobiliarios partition=1 offset=250
    Publicado topic=anuncios_inmobiliarios partition=1 offset=251
    Publicado topic=anuncios_inmobiliarios partition=1 offset=252
    Publicado topic=anuncios_inmobiliarios partition=1 offset=253
    Publicado topic=anuncios_inmobiliarios partition=1 offset=254
    Publicado topic=anuncios_inmobiliarios partition=1 offset=255
    Publicado topic=anuncios_inmobiliarios partition=1 offset=256
    Publicado topic=anuncios_inmobiliarios partition=1 offset=257
    Publicado topic=anuncios_inmobiliarios partition=1 offset=258
    Publicado topic=anuncios_inmobiliarios partition=1 offset=259
    Publicado topic=anuncios_inmobiliarios partition=1 offset=260
    Publicados 759 anuncios en anuncios_inmobiliarios
    ADAPTER_PUBLICADOS 759
Conclusión: 759 publicados con metadata topic/partition/offset. Offsets tras producir: anuncios_inmobiliarios:0:257 anuncios_inmobiliarios:1:261 anuncios_inmobiliarios:2:242 (suma 760 = 759 nuevos + 1 previo). Grupo anuncios aún no creado (GroupIdNotFoundException esperado).

### 2026-11-05 Bloque 2 Kafka consumidor Python 759 (paso 6, tarea 2.3)

Fecha: 2026-11-05
Objetivo: consumir con grupo anuncios, commit manual, upsert por portal+id_anuncio, sin duplicar
Máquina: broker VM 192.168.201.162:9094 grupo anuncios, MongoDB localhost:27017 vivienda_euskadi.anuncios
Comando:
    timeout 180 .venv/Scripts/python.exe -c "import sys; sys.path.insert(0, '.'); from storage.kafka_consumer import consume; n=consume(group_id='anuncios', max_messages=759); print(f'CONSUME_RET {n}')"
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    Mensaje sin portal/id_anuncio, se descarta: {'precio': 850, 'municipio': 'Bilbao'}
    Procesados: 759
    CONSUME_RET 759
    anuncios_inmobiliarios:0:257
    anuncios_inmobiliarios:1:261
    anuncios_inmobiliarios:2:242
    Consumer group 'anuncios' has no active members.
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
    anuncios        anuncios_inmobiliarios 0          257             257             0
    anuncios        anuncios_inmobiliarios 1          261             261             0
    anuncios        anuncios_inmobiliarios 2          242             242             0
    COUNT 759
    MUNICIPIOS 252
Conclusión: Procesados 759, mensaje previo sin portal/id_anuncio descartado y no contado. Mongo anuncios 759 (upsert sin duplicar), municipios 252. Offsets log-end 257/261/242 suma 760, grupo anuncios lag 0, offsets >=759. Desviación honesta: entrada `python -m storage.kafka_consumer` sin límite bloquearía tras vaciar; se acota con max_messages=759 (mismo código consume(), mismo grupo/commit/upsert).

### 2026-11-05 Bloque 2 Gate e2e produce 10 de prueba (paso 7, tarea 3.1)

Fecha: 2026-11-05
Objetivo: publicar 10 anuncios deterministas (primeros 10 ordenados por portal,id_anuncio) a Kafka
Máquina: broker VM 192.168.201.162:9094 grupo anuncios (offsets antes 257/261/242)
Comando:
    timeout 60 .venv/Scripts/python.exe C:/Users/mikel/AppData/Local/hermes/cache/scratch/publish_adapter.py 10
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    SUBSET 10
      fotocasa:131393829 codigo_ine=01059 municipio=Vitoria-Gasteiz
      fotocasa:159915860 codigo_ine=20055 municipio=Arrasate/Mondragón
      fotocasa:161991304 codigo_ine=48020 municipio=Bilbao
      fotocasa:162213906 codigo_ine=48020 municipio=Bilbao
      fotocasa:176108369 codigo_ine=48044 municipio=Getxo
      fotocasa:176108408 codigo_ine=48044 municipio=Getxo
      fotocasa:176113409 codigo_ine=48044 municipio=Getxo
      fotocasa:176216653 codigo_ine=48054 municipio=Leioa
      fotocasa:176216662 codigo_ine=48016 municipio=Berango
      fotocasa:176219963 codigo_ine=48054 municipio=Leioa
    Publicado topic=anuncios_inmobiliarios partition=0 offset=257
    Publicado topic=anuncios_inmobiliarios partition=0 offset=258
    Publicado topic=anuncios_inmobiliarios partition=0 offset=259
    Publicado topic=anuncios_inmobiliarios partition=2 offset=242
    Publicado topic=anuncios_inmobiliarios partition=2 offset=243
    Publicado topic=anuncios_inmobiliarios partition=2 offset=244
    Publicado topic=anuncios_inmobiliarios partition=1 offset=261
    Publicado topic=anuncios_inmobiliarios partition=1 offset=262
    Publicado topic=anuncios_inmobiliarios partition=1 offset=263
    Publicado topic=anuncios_inmobiliarios partition=1 offset=264
    ADAPTER_PUBLICADOS 10 en anuncios_inmobiliarios
    anuncios_inmobiliarios:0:260
    anuncios_inmobiliarios:1:265
    anuncios_inmobiliarios:2:245
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
    anuncios        anuncios_inmobiliarios 0          257             260             3
    anuncios        anuncios_inmobiliarios 1          261             265             4
    anuncios        anuncios_inmobiliarios 2          242             245             3
Conclusión: 10 publicados con metadata (3/4/3 por partición). Log-end 260/265/245 suma 770, lag 3/4/3 suma 10. Sin cron, sin console-producer.

### 2026-11-05 Bloque 2 Gate e2e consume 10 a Mongo (paso 7, tarea 3.2)

Fecha: 2026-11-05
Objetivo: consumir los 10 con upsert sin duplicar
Máquina: broker VM 192.168.201.162:9094 grupo anuncios, MongoDB localhost:27017 vivienda_euskadi.anuncios
Comando:
    timeout 120 .venv/Scripts/python.exe -c "import sys; sys.path.insert(0, '.'); from storage.kafka_consumer import consume; n=consume(group_id='anuncios', max_messages=10); print(f'CONSUME_RET {n}')"
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    Procesados: 10
    CONSUME_RET 10
    anuncios_inmobiliarios:0:260
    anuncios_inmobiliarios:1:265
    anuncios_inmobiliarios:2:245
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
    anuncios        anuncios_inmobiliarios 0          260             260             0
    anuncios        anuncios_inmobiliarios 1          265             265             0
    anuncios        anuncios_inmobiliarios 2          245             245             0
Conclusión: Procesados 10, lag 0, offsets grupo = log-end 260/265/245. Mongo seguirá en 759 por upsert idempotente (mismos 10 ya existentes).

### 2026-11-05 Bloque 2 Gate e2e verificación Mongo por codigo_ine y huella SHA (paso 7, tarea 3.3)

Fecha: 2026-11-05
Objetivo: verificar que los 10 son consultables por codigo_ine en MongoDB y registrar huella SHA
Máquina: MongoDB localhost:27017 vivienda_euskadi.anuncios y municipios
Comando:
    .venv/Scripts/python.exe -c "from storage.mongo import get_collection; from storage.kafka_producer import read_anuncios; subset ordenado; verificar cada doc por portal/id_anuncio y por codigo_ine; huella SHA256 del subset"
Salida literal:
    TOTAL 759
    fotocasa 131393829 esperado_ine 01059 en_mongo 01059 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 159915860 esperado_ine 20055 en_mongo 20055 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 161991304 esperado_ine 48020 en_mongo 48020 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 162213906 esperado_ine 48020 en_mongo 48020 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176108369 esperado_ine 48044 en_mongo 48044 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176108408 esperado_ine 48044 en_mongo 48044 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176113409 esperado_ine 48044 en_mongo 48044 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176216653 esperado_ine 48054 en_mongo 48054 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176216662 esperado_ine 48016 en_mongo 48016 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176219963 esperado_ine 48054 en_mongo 48054 OK
      CONSULTA_POR_CODIGO_INE 1 doc(s)
    VERIFICADOS 10/10
    HUELLA_SHA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
    MUNICIPIOS 252
Conclusión: 10/10 consultables por codigo_ine (cada consulta portal+id+codigo_ine devuelve 1), total anuncios 759, municipios 252, huella SHA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25. Gate PASS.

### 2026-11-05 Bloque 2 regresión offline y manifest (paso 7 cierre)

Fecha: 2026-11-05
Objetivo: regresión sin tocar data/raw ni storage/; manifest 353/184
Máquina: local Windows repo bigdata-vivienda-euskadi
Comando:
    .venv/Scripts/python.exe -m pytest tests/test_contrato.py -q
    wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt
Salida literal:
    ......................................................                   [100%]
    54 passed in 0.75s
      353 docs/raw_manifest_sha256.txt
      184 data/procesado/manifest_sha256.txt
      537 total
Conclusión: 54 passed, manifest 353/184 OK, data/raw intacto, storage/ sin tocar (solo nuevo scripts/upload_procesado.py). Sin git add/commit/push.

### 2026-11-05 Bloque 2 fixer Kafka offsets base solo lectura (SSH)

Fecha: 2026-11-05
Objetivo: confirmar offsets/log-end/lag antes de los fixes en vivo sin producir ni consumir
Máquina: VM 192.168.201.162 usuario mikel
Comando:
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-topics.sh --describe --topic anuncios_inmobiliarios --bootstrap-server 192.168.201.162:9094; ~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    Topic: anuncios_inmobiliarios	TopicId: J045oausTPeWCBdy624l5A	PartitionCount: 3	ReplicationFactor: 1	Configs: min.insync.replicas=2,segment.bytes=1073741824,max.message.bytes=1048588
        Topic: anuncios_inmobiliarios	Partition: 0	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:
        Topic: anuncios_inmobiliarios	Partition: 1	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:
        Topic: anuncios_inmobiliarios	Partition: 2	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:
    anuncios_inmobiliarios:0:260
    anuncios_inmobiliarios:1:265
    anuncios_inmobiliarios:2:245
    Consumer group 'anuncios' has no active members.
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID     HOST            CLIENT-ID
    anuncios        anuncios_inmobiliarios 0          260             260             0               -               -               -
    anuncios        anuncios_inmobiliarios 1          265             265             0               -               -               -
    anuncios        anuncios_inmobiliarios 2          245             245             0               -               -               -
Conclusión: base 260/265/245 lag 0 (759+previo+10 previos), topic 3 particiones. Sin escritura.

### 2026-11-05 Bloque 2 fixer HDFS recuperacion 1 fichero solo lectura (paso 5, SHA cerrado)

Fecha: 2026-11-05
Objetivo: recuperar 1 fichero raw de HDFS y comparar SHA-256+tamaño con local, sin escritura ni crear carpeta, para cerrar SHA del 1 fichero
Máquina: clúster centro HDFS http://10.22.87.215:50070 usuario iabd-user15, desde Windows (repo bigdata-vivienda-euskadi)
Comando:
    timeout 120 .venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py alquiler_distrito_seccion_original.csv
Salida literal:
    FICHERO alquiler_distrito_seccion_original.csv
    HDFS_PATH /user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/alquiler_distrito_seccion_original.csv
    LOCAL_SIZE 17243 SHA b0e3583f42ae4b0a888cb6b7096ee57a2c9f420c3c229fb86a56e94f4f1f5134
    REMOTE_SIZE 17243 SHA b0e3583f42ae4b0a888cb6b7096ee57a2c9f420c3c229fb86a56e94f4f1f5134
    HDFS_REC OK SHA_TAMANO_IGUALES
    HDFS_REC CERO_ESCRITURAS NO_CARPETA_NUEVA
Conclusión: SHAs y tamaños iguales (17243 bytes, b0e3583f...f5134 coincide con primera línea de docs/raw_manifest_sha256.txt). Solo status/read, cero escrituras, sin carpeta nueva. Discrepancia 355/353/200 anotada en verify-report.md.

### 2026-11-05 Bloque 2 fixer adapter versionado publica 10 (paso 6, Future)

Fecha: 2026-11-05
Objetivo: publicar 10 deterministas con scripts/publish_adapter.py versionado (Future.add_callback/add_errback, kafka-python 2.2.3)
Máquina: broker VM 192.168.201.162:9094 (offsets antes 260/265/245)
Comando:
    timeout 60 .venv/Scripts/python.exe scripts/publish_adapter.py 10
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    SUBSET 10
      fotocasa:131393829 codigo_ine=01059 municipio=Vitoria-Gasteiz
      fotocasa:159915860 codigo_ine=20055 municipio=Arrasate/Mondragón
      fotocasa:161991304 codigo_ine=48020 municipio=Bilbao
      fotocasa:162213906 codigo_ine=48020 municipio=Bilbao
      fotocasa:176108369 codigo_ine=48044 municipio=Getxo
      fotocasa:176108408 codigo_ine=48044 municipio=Getxo
      fotocasa:176113409 codigo_ine=48044 municipio=Getxo
      fotocasa:176216653 codigo_ine=48054 municipio=Leioa
      fotocasa:176216662 codigo_ine=48016 municipio=Berango
      fotocasa:176219963 codigo_ine=48054 municipio=Leioa
    Publicado topic=anuncios_inmobiliarios partition=0 offset=260
    Publicado topic=anuncios_inmobiliarios partition=0 offset=261
    Publicado topic=anuncios_inmobiliarios partition=0 offset=262
    Publicado topic=anuncios_inmobiliarios partition=2 offset=245
    Publicado topic=anuncios_inmobiliarios partition=2 offset=246
    Publicado topic=anuncios_inmobiliarios partition=2 offset=247
    Publicado topic=anuncios_inmobiliarios partition=1 offset=265
    Publicado topic=anuncios_inmobiliarios partition=1 offset=266
    Publicado topic=anuncios_inmobiliarios partition=1 offset=267
    Publicado topic=anuncios_inmobiliarios partition=1 offset=268
    ADAPTER_PUBLICADOS 10 en anuncios_inmobiliarios
    anuncios_inmobiliarios:0:263
    anuncios_inmobiliarios:1:269
    anuncios_inmobiliarios:2:248
    Consumer group 'anuncios' has no active members.
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID     HOST            CLIENT-ID
    anuncios        anuncios_inmobiliarios 0          260             263             3               -               -               -
    anuncios        anuncios_inmobiliarios 1          265             269             4               -               -               -
    anuncios        anuncios_inmobiliarios 2          245             248             3               -               -               -
Conclusión: 10 publicados con metadata (3/4/3), log-end 263/269/248, lag 3/4/3. storage/kafka_producer.py ya usa Future, adapter versionado sin scratch.

### 2026-11-05 Bloque 2 fixer consume 10 a Mongo (paso 6/7)

Fecha: 2026-11-05
Objetivo: consumir los 10 del adapter con upsert sin duplicar
Máquina: broker VM 192.168.201.162:9094 grupo anuncios, MongoDB localhost:27017 vivienda_euskadi.anuncios
Comando:
    timeout 120 .venv/Scripts/python.exe -c "import sys; sys.path.insert(0, '.'); from storage.kafka_consumer import consume; n=consume(group_id='anuncios', max_messages=10); print(f'CONSUME_RET {n}')"
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    Procesados: 10
    CONSUME_RET 10
    anuncios_inmobiliarios:0:263
    anuncios_inmobiliarios:1:269
    anuncios_inmobiliarios:2:248
    Consumer group 'anuncios' has no active members.
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID     HOST            CLIENT-ID
    anuncios        anuncios_inmobiliarios 0          263             263             0               -               -               -
    anuncios        anuncios_inmobiliarios 1          269             269             0               -               -               -
    anuncios        anuncios_inmobiliarios 2          248             248             0               -               -               -
Conclusión: Procesados 10, lag 0, offsets grupo = log-end 263/269/248. Mongo 759 por upsert idempotente.

### 2026-11-05 Bloque 2 fixer gate versionado e2e 10 PASS (paso 7)

Fecha: 2026-11-05
Objetivo: gate Kafka->Mongo por codigo_ine con 10 deterministas vía scripts/gate_bloque2.py (HDFS leg = LISTSTATUS previo, sin subir raw), huella SHA + conteos + lag 0
Máquina: broker VM 192.168.201.162:9094 grupo anuncios, MongoDB localhost:27017, HDFS centro http://10.22.87.215:50070 usuario iabd-user15
Comando:
    timeout 180 .venv/Scripts/python.exe scripts/gate_bloque2.py
    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "~/kafka/bin/kafka-get-offsets.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios; ~/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 192.168.201.162:9094 --group anuncios --describe"
Salida literal:
    HDFS_LEG LIST_BASE ['raw']
    HDFS_LEG LIST_RAW_COUNT 200
    HDFS_LEG STATUS_RAW childrenNum=200
    HDFS_LEG CERO_ESCRITURAS NO_SUBIDO_RAW
    HDFS_LEG CERO_ESCRITURAS NO_SUBIDO_PROCESADO
    SUBSET 10
      fotocasa:131393829 codigo_ine=01059 municipio=Vitoria-Gasteiz
      fotocasa:159915860 codigo_ine=20055 municipio=Arrasate/Mondragón
      fotocasa:161991304 codigo_ine=48020 municipio=Bilbao
      fotocasa:162213906 codigo_ine=48020 municipio=Bilbao
      fotocasa:176108369 codigo_ine=48044 municipio=Getxo
      fotocasa:176108408 codigo_ine=48044 municipio=Getxo
      fotocasa:176113409 codigo_ine=48044 municipio=Getxo
      fotocasa:176216653 codigo_ine=48054 municipio=Leioa
      fotocasa:176216662 codigo_ine=48016 municipio=Berango
      fotocasa:176219963 codigo_ine=48054 municipio=Leioa
    HUELLA_ESPERADA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
    Publicado topic=anuncios_inmobiliarios partition=0 offset=269
    Publicado topic=anuncios_inmobiliarios partition=0 offset=270
    Publicado topic=anuncios_inmobiliarios partition=0 offset=271
    Publicado topic=anuncios_inmobiliarios partition=2 offset=254
    Publicado topic=anuncios_inmobiliarios partition=2 offset=255
    Publicado topic=anuncios_inmobiliarios partition=2 offset=256
    Publicado topic=anuncios_inmobiliarios partition=1 offset=277
    Publicado topic=anuncios_inmobiliarios partition=1 offset=278
    Publicado topic=anuncios_inmobiliarios partition=1 offset=279
    Publicado topic=anuncios_inmobiliarios partition=1 offset=280
    PRODUCIDOS 10
    Procesados: 10
    CONSUME_RET 10
    fotocasa 131393829 esperado_ine 01059 en_mongo 01059 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 159915860 esperado_ine 20055 en_mongo 20055 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 161991304 esperado_ine 48020 en_mongo 48020 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 162213906 esperado_ine 48020 en_mongo 48020 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176108369 esperado_ine 48044 en_mongo 48044 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176108408 esperado_ine 48044 en_mongo 48044 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176113409 esperado_ine 48044 en_mongo 48044 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176216653 esperado_ine 48054 en_mongo 48054 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176216662 esperado_ine 48016 en_mongo 48016 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    fotocasa 176219963 esperado_ine 48054 en_mongo 48054 OK CONSULTA_POR_CODIGO_INE 1 doc(s)
    LAG p0 CURRENT 272 LOG_END 272 LAG 0
    LAG p1 CURRENT 281 LOG_END 281 LAG 0
    LAG p2 CURRENT 257 LOG_END 257 LAG 0
    LAG_TOTAL 0
    VERIFICADOS 10/10
    HUELLA_SHA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
    TOTAL 759
    MUNICIPIOS 252
    GATE PASS
    anuncios_inmobiliarios:0:272
    anuncios_inmobiliarios:1:281
    anuncios_inmobiliarios:2:257
    Consumer group 'anuncios' has no active members.
    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID     HOST            CLIENT-ID
    anuncios        anuncios_inmobiliarios 0          272             272             0               -               -               -
    anuncios        anuncios_inmobiliarios 1          281             281             0               -               -               -
    anuncios        anuncios_inmobiliarios 2          257             257             0               -               -               -
Conclusión: GATE PASS, 10/10 por codigo_ine, huella e32c3d3...faf25, TOTAL 759, MUNICIPIOS 252, lag 0. HDFS leg solo LISTSTATUS, cero escrituras. Dos intentos previos del script fallaron en lag_report (assign/subscribe y seek_to_end) tras produce+consume; corregidos y re-ejecutados hasta PASS.
### 2026-11-05 Bloque 2 fixer regresion offline y manifest (cierre)

Fecha: 2026-11-05
Objetivo: regresión final sin tocar data/raw; manifest 353/184 intactos
Máquina: local Windows repo bigdata-vivienda-euskadi
Comando:
    .venv/Scripts/python.exe -m pytest tests/test_contrato.py -q
    .venv/Scripts/python.exe -m pytest tests/test_kafka.py -q
    wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt
Salida literal:
    ......................................................                   [100%]
    54 passed in 0.67s
    ...                                                                      [100%]
    3 passed in 0.21s
      353 docs/raw_manifest_sha256.txt
      184 data/procesado/manifest_sha256.txt
      537 total
Conclusión: 54 passed test_contrato + 3 passed test_kafka (Future 759), manifest 353/184 OK, data/raw intacto. Ficheros fixer: storage/kafka_producer.py, tests/test_kafka.py, scripts/publish_adapter.py, scripts/gate_bloque2.py, scripts/hdfs_recuperacion_un_fichero.py, openspec proposal/verify-report, docs/trazabilidad_vm.md. Sin git add/commit/push, sin HDFS escritura, sin data/raw tocado.

### 2026-11-05 Bloque 3 explain antes/después COLLSCAN→IXSCAN totalDocsExamined 1 (tarea 1.1, INDICES-01)

Fecha: 2026-11-05
Objetivo: ejecutar `explain_before_after()` sin índice ESR y con él; guardar COLLSCAN antes e IXSCAN después con `nReturned`/`totalDocsExamined=1`
Máquina: local Windows repo bigdata-vivienda-euskadi, MongoDB localhost:27017 vivienda_euskadi
Comando:
    .venv/Scripts/python.exe -c "from analysis.mongo_indexes import explain_before_after; import pprint; pprint.pprint(explain_before_after())"
    .venv/Scripts/python.exe analysis/run_analisis_mongo.py
Salida literal:
    {'after': {'executionTimeMillis': 8, 'nReturned': 1, 'stage': 'IXSCAN', 'totalDocsExamined': 1, 'totalKeysExamined': 1}, 'before': {'executionTimeMillis': 1, 'nReturned': 1, 'stage': 'COLLSCAN', 'totalDocsExamined': 759, 'totalKeysExamined': 0}, 'filtro': {'modalidad': 'larga_estancia', 'precio_eur': {'$lte': Decimal128('1000')}, 'ubicacion.codigo_ine': '48001'}}
    explain before: stage=COLLSCAN nReturned=1 totalDocsExamined=759 totalKeysExamined=0
    explain after: stage=IXSCAN nReturned=1 totalDocsExamined=1 totalKeysExamined=1
    explain filtro: {'ubicacion.codigo_ine': '48001', 'modalidad': 'larga_estancia', 'precio_eur': {'$lte': Decimal128('1000')}}
    mongo_esfuerzo_por_municipio.csv: 252 filas -> data/resultados/mongo_esfuerzo_por_municipio.csv
    mongo_alquiler_por_municipio.csv: 252 filas -> data/resultados/mongo_alquiler_por_municipio.csv
    mongo_modalidades.csv: 2 filas -> data/resultados/mongo_modalidades.csv
    mongo_accesibilidad_extendida.csv: 252 filas -> data/resultados/mongo_accesibilidad_extendida.csv
    mongo_vpo_por_municipio.csv: 322 filas -> data/resultados/mongo_vpo_por_municipio.csv
    pipelines: ['pipeline_indicadores_municipio', 'pipeline_alquiler_por_municipio', 'pipeline_modalidades', 'pipeline_top_municipios_por_esfuerzo', 'pipeline_esfuerzo_por_sexo', 'pipeline_accesibilidad_extendida', 'pipeline_udalmap_extendido_osrm', 'pipeline_vpo_por_municipio']
    n={'pipeline_indicadores_municipio': 252, 'pipeline_alquiler_por_municipio': 252, 'pipeline_modalidades': 2, 'pipeline_top_municipios_por_esfuerzo': 10, 'pipeline_esfuerzo_por_sexo': 252, 'pipeline_accesibilidad_extendida': 252, 'pipeline_udalmap_extendido_osrm': 252, 'pipeline_vpo_por_municipio': 322}
    huella: 6812b63bb3f2155ceab5511801d073d571b1347600336d9ffc63683549b26f72
    reproducibilidad: ok (dos ejecuciones con la misma huella)
Conclusión: COLLSCAN (759 examinados) → IXSCAN (totalDocsExamined=1, nReturned=1) con filtro ubicacion.codigo_ine=48001 + modalidad=larga_estancia + precio_eur $lte Decimal128(1000) e índice ESR {ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}. `run_analisis_mongo.py` imprime las dos líneas explain y genera 5 CSV. Prod anuncios 759 intacto.

### 2026-11-05 Bloque 3 listings Mongo lectura pura 15 colecciones + geo 424 (tareas 2.1-2.2, RESPALDO-01)

Fecha: 2026-11-05
Objetivo: listing db.getCollectionNames() de vivienda_euskadi (lectura pura, 15 colecciones incl. municipios__backup e indicadores__backup) y conteo geo 424 Point
Máquina: local Windows repo bigdata-vivienda-euskadi, MongoDB localhost:27017 vivienda_euskadi
Comando:
    mongosh --quiet vivienda_euskadi --eval 'db.getCollectionNames().length'
    mongosh --quiet vivienda_euskadi --eval 'db.getCollectionNames()'
    mongosh --quiet vivienda_euskadi --eval 'db.anuncios.countDocuments({"ubicacion.coordenadas": {"$type": "object"}})'
    .venv/Scripts/python.exe -c "from storage.mongo import get_collection; c=get_collection('anuncios'); print(c.count_documents({})); print(get_collection('municipios').count_documents({})); print(get_collection('indicadores').count_documents({})); print(get_collection('municipios__backup').count_documents({})); print(get_collection('indicadores__backup').count_documents({}))"
Salida literal:
    15
    ['udalmap_extendido', 'anuncios', 'indicadores__backup', 'etxebide_promociones', 'municipios__backup', 'certificados_energeticos', 'indicadores', 'municipios', 'udalmap_empleo', 'emancipacion_juventud', 'etxebide_solicitudes', 'ecvi_compraventa', 'udalmap_indicadores', 'alquiler_municipal', 'osrm_tiempos']
    424
    759
    252
    252
    252
    252
Conclusión: 15 colecciones con backups 252/252, anuncios 759, municipios 252, geo 424 Point reales (resto None por falta de silver). Documentado en docs/modelo_mongodb.md (backups vía replace_collection staging+backup+rename, nunca drop() directo; geo 2dsphere sparse).

### 2026-11-05 Bloque 3 limpieza canónica $unset y commit/abort solo test (tareas 3.1/3.3, LIMPIEZA-01/TRANSACCIONES-01)

Fecha: 2026-11-05
Objetivo: verificar función canónica única con update_many $unset (matched/modified/deleted) en ambas colecciones solo sobre test DB y sonda commit/abort solo en test con prod 759 invariante sin MONGO_ALLOW_DESTRUCTIVE
Máquina: local Windows repo bigdata-vivienda-euskadi, MongoDB localhost:27017 vivienda_euskadi_test (prod solo lectura por conteo)
Comando:
    .venv/Scripts/python.exe -m pytest tests/test_mongo_pymongo_pro.py tests/test_mongo_indices.py -q
    .venv/Scripts/python.exe -m pytest tests/test_mongo_consistencia.py -q
Salida literal:
    ...                                                                      [100%]
    3 passed in 0.72s
    ..                                                                       [100%]
    2 passed in 0.54s
Conclusión: clean_obsolete_fields (update_many $unset) devuelve matched/modified/deleted en anuncios y municipios solo sobre vivienda_euskadi_test; sonda commit/abort aborta o es rechazada en standalone sin tocar prod (759 invariante, MONGO_ALLOW_DESTRUCTIVE sin definir).

### 2026-11-05 Bloque 3 gate final 130 passed, manifest 353/184, data/raw intacto (tareas 2.4/4.2)

Fecha: 2026-11-05
Objetivo: gate Bloque 3: pytest 130, 5 CSV con recuentos 252/252/2+252/322, manifest intacto, git status data/raw vacío, cero escrituras HDFS/raw
Máquina: local Windows repo bigdata-vivienda-euskadi
Comando:
    .venv/Scripts/python.exe analysis/run_analisis_mongo.py
    .venv/Scripts/python.exe -m pytest tests -q
    wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt
    git status --short
    git status --short data/raw
    .venv/Scripts/python.exe -c "from storage.mongo import get_collection; print(get_collection('anuncios').count_documents({}))"
Salida literal:
    explain before: stage=COLLSCAN nReturned=1 totalDocsExamined=759 totalKeysExamined=0
    explain after: stage=IXSCAN nReturned=1 totalDocsExamined=1 totalKeysExamined=1
    mongo_esfuerzo_por_municipio.csv: 252 filas
    mongo_alquiler_por_municipio.csv: 252 filas
    mongo_modalidades.csv: 2 filas
    mongo_accesibilidad_extendida.csv: 252 filas
    mongo_vpo_por_municipio.csv: 322 filas
    n={'pipeline_indicadores_municipio': 252, 'pipeline_alquiler_por_municipio': 252, 'pipeline_modalidades': 2, 'pipeline_top_municipios_por_esfuerzo': 10, 'pipeline_esfuerzo_por_sexo': 252, 'pipeline_accesibilidad_extendida': 252, 'pipeline_udalmap_extendido_osrm': 252, 'pipeline_vpo_por_municipio': 322}
    huella: 6812b63bb3f2155ceab5511801d073d571b1347600336d9ffc63683549b26f72
    reproducibilidad: ok (dos ejecuciones con la misma huella)
    ..........................................................               [100%]
    130 passed in 5.60s
      353 docs/raw_manifest_sha256.txt
      184 data/procesado/manifest_sha256.txt
      537 total
    (git status --short data/raw sin salida)
    759
Conclusión: 130 passed, 5 CSV (252/252/2 + 252/322), manifest 353/184 intactos, data/raw intacto, anuncios 759, cero escrituras HDFS (no se tocó data/raw local ni raw HDFS, no carpeta nueva, no subida procesado).

