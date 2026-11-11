"""Utilidades comunes para los scripts de extracción.

Reexporta las rutas canónicas de ``paths.py`` y ofrece un cliente HTTP con
reintentos, logging y escritura de JSON/raw.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import requests

# ─── Raíz del proyecto y capas de datos ───────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import (  # noqa: E402
    DATA_DIR,
    PROCESADO_DIR,
    RAW_DIR,
    RESULTADOS_DIR,
    ensure_dirs,
)

# Directory creation belongs to the command that owns the output. Importing
# extraction helpers must not create or mutate any data layer.


# ─── Logging ──────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


# ─── HTTP con reintentos ──────────────────────────────────────
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


class Cliente:
    """Cliente HTTP con reintentos, pausas y logging."""

    def __init__(
        self,
        nombre: str,
        headers: dict | None = None,
        reintentos: int = 4,
        espera_inicial: float = 1.5,
        timeout: int = 60,
        delay: float = 1.0,
    ):
        self.log = get_logger(nombre)
        self.reintentos = reintentos
        self.espera_inicial = espera_inicial
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({**DEFAULT_HEADERS, **(headers or {})})
        self._ultima = 0.0

    def _espera_educada(self) -> None:
        """No machacar el servidor: espera entre peticiones."""
        if self.delay <= 0:
            return
        transcurrido = time.time() - self._ultima
        if transcurrido < self.delay:
            time.sleep(self.delay - transcurrido)

    def get(self, url: str, **kwargs) -> requests.Response:
        return self._peticion("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self._peticion("POST", url, **kwargs)

    def _peticion(self, metodo: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        ultimo_error: Exception | None = None

        for intento in range(1, self.reintentos + 1):
            self._espera_educada()
            try:
                resp = self.session.request(metodo, url, **kwargs)
                self._ultima = time.time()
                if resp.status_code < 400:
                    return resp
                ultimo_error = RuntimeError(
                    f"HTTP {resp.status_code} para {url}"
                )
            except requests.RequestException as exc:  # timeout, DNS, red
                ultimo_error = exc

            if intento < self.reintentos:
                espera = self.espera_inicial * (2 ** (intento - 1))
                self.log.warning(
                    "Reintento %d/%d para %s (espera %.1fs): %s",
                    intento, self.reintentos, url, espera, ultimo_error,
                )
                time.sleep(espera)

        raise RuntimeError(
            f"Fallo definitivo tras {self.reintentos} intentos: {url} "
            f"({ultimo_error})"
        )

    def descargar(self, url: str, destino: Path, **kwargs) -> Path:
        """Descarga un fichero binario/texto y lo guarda."""
        destino.parent.mkdir(parents=True, exist_ok=True)
        resp = self.get(url, **kwargs)
        destino.write_bytes(resp.content)
        self.log.info("Guardado %s (%.1f KB)", destino.name, len(resp.content) / 1024)
        return destino


# ─── Lectura CSV segura (fase crudos, sin proxys) ─────────────────


def leer_csv_seguro(path, **kwargs):
    """read_csv con dtype=str + utf-8-sig y codigo_ine zfill(5).

    Reglas plan crudos: todo read_csv con dtype=str y encoding utf-8.
    Normaliza codigo_ine a 5 dígitos (01/20/48) si existe la columna.
    """
    from pathlib import Path as _Path

    import pandas as _pd

    kwargs.setdefault("dtype", str)
    kwargs.setdefault("encoding", "utf-8-sig")
    kwargs.setdefault("low_memory", False)
    df = _pd.read_csv(_Path(path), **kwargs)
    if "codigo_ine" in df.columns:
        df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)
    return df


# ─── Escritura de datos ───────────────────────────────────────
# Metadata mínima: 4 campos. `fecha_extraccion` y `n_registros` se rellenan
# solos; `fuente` y `url` los declara cada extractor. No se valida ni se
# rechaza: si falta un dato, se escribe igual y se avisa por log.
METADATA_MINIMA = ("fuente", "url", "fecha_extraccion", "n_registros")


def write_raw(nombre: str | Path, contenido: bytes) -> Path:
    """Escribe un fichero en ``raw/`` una sola vez y de forma atómica."""
    destino = Path(nombre)
    if destino.parent == Path("."):
        destino = RAW_DIR / destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + ".tmp")
    temporal.write_bytes(contenido)
    temporal.replace(destino)
    return destino


def guardar_json(destino: Path, datos, metadata: dict | None = None) -> Path:
    from datetime import datetime

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(metadata or {})
    if isinstance(datos, list):
        meta.setdefault("n_registros", len(datos))
    meta.setdefault(
        "fecha_extraccion",
        datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    faltan = [k for k in METADATA_MINIMA if meta.get(k) in (None, "", [])]
    if faltan:
        get_logger("guardar_json").warning(
            "%s: metadata sin %s", destino.name, ", ".join(faltan)
        )
    destino.write_text(
        json.dumps({"metadata": meta, "datos": datos}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return destino
