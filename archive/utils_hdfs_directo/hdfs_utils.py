"""Cliente HDFS/WebHDFS reutilizable para el clúster central (HDFS-01).

Sin credenciales en código: lee HDFS_URL y HDFS_USER de entorno,
inyecta InsecureClient como inyección de dependencia, expone get_client()
(versión simple y con overrides) y helpers puros: upload_raw_excluding_legacy,
get_status, read_file_sha256, ping y delete_recursive.

La subida replica data/raw entero a la ruta remota raw separada de procesado,
excluye data/raw/legacy_obsoleto_no_usar y registra el avance por fichero en
data/_hdfs_state/hdfs_upload_raw.json para reanudar tras caída sin re-subir.

Ejemplo mínimo:
    from storage.hdfs_utils import get_client, upload_raw_excluding_legacy

    client = get_client()
    upload_raw_excluding_legacy(client)

Ejemplo de test doble:
    from storage.hdfs_utils import Client, read_file_sha256

    assert read_file_sha256(client, hdfs_path) == sha_local
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_HDFS_URL = "http://10.22.87.215:50070"
DEFAULT_HDFS_USER = "iabd-user15"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "data" / "raw"
STATE_DIR = ROOT / "data" / "_hdfs_state"
DEFAULT_HDFS_BASE = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data"
DEFAULT_HDFS_RAW = DEFAULT_HDFS_BASE + "/raw"

# Public type alias para tests con mocks y pyright.
from hdfs import InsecureClient

Client = InsecureClient


def get_hdfs_url() -> str:
    """URL WebHDFS según entorno, sin cachear en import."""
    uri = os.getenv("HDFS_URL")
    if uri and uri.strip() and "localhost" not in uri.lower():
        return uri.strip()
    return DEFAULT_HDFS_URL


def get_hdfs_user() -> str:
    """Usuario WebHDFS según entorno, sin cachear en import."""
    user = os.getenv("HDFS_USER")
    if user and user.strip():
        return user.strip()
    return DEFAULT_HDFS_USER



def get_client(url: str | None = None, user: str | None = None) -> Client:
    """Devuelve InsecureClient reutilizable para el clúster central.

    Lee HDFS_URL y HDFS_USER de entorno como defecto (mismo patrón que
    storage.mongo.get_mongo_uri para MONGO_URI).
    Permite overrides explícitos para tests con monkeypatch.
    """
    return InsecureClient(url or get_hdfs_url(), user=user or get_hdfs_user())


def _sha_local(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_raw_files(raw_dir: Path) -> list[Path]:
    return sorted(
        p for p in raw_dir.rglob("*") if p.is_file() and "legacy_obsoleto_no_usar" not in p.parts
    )


def _load_done(state_path: Path) -> set[str]:
    if not state_path.exists() or state_path.stat().st_size == 0:
        return set()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(x) for x in data}
        if isinstance(data, dict):
            return {str(k) for k in data}
        return set()
    except Exception:
        try:
            return {
                line.strip()
                for line in state_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        except Exception:
            return set()


def _save_done(state_path: Path, done: set[str]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(sorted(done), indent=2) + "\n", encoding="utf-8")


def upload_raw_excluding_legacy(
    client: Client | None = None,
    raw_dir: Path | str | None = None,
    hdfs_path: str | None = None,
    state_dir: Path | str | None = None,
) -> dict[str, int]:
    """Sube raw entero excluyendo legacy_obsoleto_no_usar.

    Replica bronce inmutable incluidos .FROZEN, .gitkeep, CSV, HTML en
    html_fotocasa, JSON, ZIP, XLSX, geojson, shp_euskadi y gtfs.
    Destino por defecto: DEFAULT_HDFS_RAW (.../data/raw), separado de procesado.
    Devuelve {uploaded, deduped}. No toca data/procesado ni el legacy.
    """
    c = client if client is not None else get_client()
    src = Path(raw_dir) if raw_dir is not None else DEFAULT_RAW_DIR
    if not src.exists():
        raise FileNotFoundError(str(src))
    sdir = Path(state_dir) if state_dir is not None else STATE_DIR
    state_path = sdir / "hdfs_upload_raw.json"
    done = _load_done(state_path)
    dest_base = (hdfs_path or DEFAULT_HDFS_RAW).rstrip("/")
    uploaded = 0
    deduped = 0
    for f in _iter_raw_files(src):
        rel = f.relative_to(src).as_posix()
        hdfs_file = f"{dest_base}/{rel}"
        if rel in done:
            deduped += 1
            continue
        with f.open("rb") as fp:
            data = fp.read()
        c.write(hdfs_file, data=data, overwrite=True)
        # Anota progreso por fichero para no re-subir ante caída.
        done.add(rel)
        _save_done(state_path, done)
        uploaded += 1
    return {"uploaded": uploaded, "deduped": deduped}


def get_status(client: Client | None = None, hdfs_path: str | None = None) -> dict | None:
    c = client if client is not None else get_client()
    return c.status(hdfs_path or DEFAULT_HDFS_BASE)


def read_file_sha256(client: Client | None = None, hdfs_path: str = "") -> str:
    """Descarga un fichero HDFS y devuelve su SHA-256 hex."""
    c = client if client is not None else get_client()
    h = hashlib.sha256()
    with c.read(hdfs_path) as reader:
        for chunk in iter(lambda: reader.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ping(client: Client | None = None) -> bool:
    c = client if client is not None else get_client()
    try:
        c.status(DEFAULT_HDFS_BASE)
        return True
    except Exception:
        return False


def delete_recursive(client: Client | None = None, hdfs_path: str = "") -> bool:
    c = client if client is not None else get_client()
    return c.delete(hdfs_path, recursive=True)


if __name__ == "__main__":
    print(upload_raw_excluding_legacy(get_client()))
