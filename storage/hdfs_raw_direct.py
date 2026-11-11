"""Upload raw files directly to HDFS over WebHDFS, without Kafka manifests."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "data" / "raw"
DEFAULT_DEST = "/user/iabd-user7/bigdata_reto/vivienda_euskadi/data/raw"


def iter_files(raw_dir: Path | str = DEFAULT_RAW_DIR) -> list[Path]:
    root = Path(raw_dir)
    return sorted(
        p for p in root.rglob("*")
        if p.is_file() and "legacy_obsoleto_no_usar" not in p.parts
    )


def upload_raw(
    raw_dir: Path | str = DEFAULT_RAW_DIR,
    dest: str | None = None,
    client=None,
    limit: int | None = None,
) -> dict[str, int]:
    """Upload local raw files directly; passing a client enables offline tests."""
    root = Path(raw_dir).resolve()
    destination = (dest or os.getenv("HDFS_RAW_DEST") or DEFAULT_DEST).rstrip("/")
    files = iter_files(root)
    if limit is not None:
        files = files[:limit]
    if client is None:
        from hdfs import InsecureClient

        client = InsecureClient(
            os.getenv("HDFS_URL", "http://10.22.87.215:50070"),
            user=os.getenv("HDFS_RAW_USER", "iabd-user7"),
            timeout=60,
        )
    client.makedirs(destination)
    uploaded = 0
    for local in files:
        rel = local.relative_to(root).as_posix()
        # Fail closed on paths that could escape the configured HDFS root.
        if PurePosixPath(rel).is_absolute() or ".." in PurePosixPath(rel).parts:
            raise ValueError(f"Ruta raw no válida: {rel!r}")
        parent = PurePosixPath(rel).parent
        if str(parent) != ".":
            client.makedirs(f"{destination}/{parent}")
        client.upload(f"{destination}/{rel}", str(local), overwrite=True)
        uploaded += 1
    return {"uploaded": uploaded}


if __name__ == "__main__":
    print(upload_raw())
