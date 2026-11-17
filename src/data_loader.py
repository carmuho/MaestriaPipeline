import logging
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd

# Configuración del sistema de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(
            'errores_lectura.log', encoding='utf-8'
        ),  # Guarda en archivo
        logging.StreamHandler(),  # Muestra también en consola
    ],
)

logger = logging.getLogger(__name__)


class DataLoaderError(Exception):
    """Error base para fallos al leer una fuente de datos."""


class UnsupportedDataFormatError(DataLoaderError, ValueError):
    """Se solicita un formato que no tiene un lector registrado."""


def _validate_path(ruta: Path | None, fuente: str) -> Path:
    if ruta is None:
        raise ValueError(f"Debe indicar una ruta para cargar {fuente}.")
    if not ruta.exists():
        logger.error(f"No se encontro la fuente de datos: '{ruta}': {e}")
        raise FileNotFoundError(f"No se encontro la fuente de datos: {ruta}")
    return ruta


class _SourceReader(ABC):
    """Interfaz común para los lectores concretos de cada fuente."""

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Lee la fuente y devuelve su contenido como DataFrame."""


class _CSVReader(_SourceReader):
    def __init__(self, ruta: Path | None):
        self.ruta = ruta

    def load(self) -> pd.DataFrame:
        ruta = _validate_path(self.ruta, "el archivo CSV")
        try:
            return pd.read_csv(ruta, parse_dates=["fecha"])
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
            raise DataLoaderError(f"No se pudo leer el archivo CSV '{ruta}'.") from exc


class _JSONReader(_SourceReader):
    def __init__(self, ruta: Path | None):
        self.ruta = ruta

    def load(self) -> pd.DataFrame:
        ruta = _validate_path(self.ruta, "el archivo JSON")
        try:
            return pd.read_json(ruta)
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            raise DataLoaderError(f"No se pudo leer el archivo JSON '{ruta}'.") from exc


class _TXTReader(_SourceReader):
    def __init__(self, ruta: Path | None, separador: str | None):
        self.ruta = ruta
        self.separador = separador

    def load(self) -> pd.DataFrame:
        ruta = _validate_path(self.ruta, "el archivo TXT")
        try:
            return pd.read_csv(
                ruta,
                sep=self.separador,
                engine="python" if self.separador is None else "c",
            )
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
            raise DataLoaderError(f"No se pudo leer el archivo TXT '{ruta}'.") from exc


class _SQLReader(_SourceReader):
    def __init__(
        self,
        ruta: Path | None,
        consulta: str | None,
        conexion: Any | None,
    ):
        self.ruta = ruta
        self.consulta = consulta
        self.conexion = conexion

    def load(self) -> pd.DataFrame:
        if not self.consulta:
            raise ValueError("Debe indicar una consulta SQL.")
        if self.conexion is not None:
            return self._execute(self.conexion)

        ruta = _validate_path(self.ruta, "la base de datos SQLite")
        conexion = None
        try:
            conexion = sqlite3.connect(ruta)
            return self._execute(conexion)
        except sqlite3.Error as exc:
            raise DataLoaderError(f"No se pudo abrir la base de datos SQLite '{ruta}'.") from exc
        finally:
            # Solo se cierra la conexión creada aquí; las conexiones externas pertenecen al llamador.
            if conexion is not None:
                conexion.close()

    def _execute(self, conexion: Any) -> pd.DataFrame:
        try:
            return pd.read_sql_query(self.consulta, conexion)
        except (sqlite3.Error, pd.errors.DatabaseError) as exc:
            raise DataLoaderError("No se pudo ejecutar la consulta SQL indicada.") from exc


class DataLoaderFactory:
    """Construye el lector adecuado según el formato de la fuente."""

    @staticmethod
    def create(
        formato: str,
        *,
        ruta: Path | None,
        consulta: str | None = None,
        conexion: Any | None = None,
        separador: str | None = None,
    ) -> _SourceReader:
        # Cada formato queda aislado en su lector, evitando mezclar sus reglas de lectura.
        if formato == "csv":
            return _CSVReader(ruta)
        if formato == "json":
            return _JSONReader(ruta)
        if formato == "txt":
            return _TXTReader(ruta, separador)
        if formato == "sql":
            return _SQLReader(ruta, consulta, conexion)
        raise UnsupportedDataFormatError(
            f"Formato no compatible: {formato}. "
            "Los formatos admitidos son csv, json, txt y sql."
        )


class DataLoader:
    """Facade compatible que delega la lectura a DataLoaderFactory."""

    def __init__(
        self,
        ruta: str | Path | None = None,
        formato: str | None = None,
        consulta: str | None = None,
        conexion: Any | None = None,
        separador: str | None = None,
    ):
        self.ruta = Path(ruta) if ruta is not None else None
        extension = self.ruta.suffix.lower().lstrip(".") if self.ruta is not None else None
        formatos_sqlite = {"db", "sqlite", "sqlite3"}
        self.formato = (
            formato.lower().lstrip(".")
            if formato is not None
            else "sql" if extension in formatos_sqlite else extension
        )
        self.consulta = consulta
        self.conexion = conexion
        self.separador = separador

    @staticmethod
    def cargar_csv(ruta: str | Path) -> pd.DataFrame:
        """Carga un CSV comercial y convierte la columna fecha a datetime."""
        return DataLoader(ruta, formato="csv").load()

    def load(self) -> pd.DataFrame:
        """Crea el lector del formato configurado y carga los datos."""
        logger.info(
            "Iniciando carga de datos: formato=%s, ruta=%s",
            self.formato,
            self.ruta,
        )
        try:
            if self.formato is None:
                raise ValueError("Debe indicar la ruta o el formato de los datos.")

            lector = DataLoaderFactory.create(
                self.formato,
                ruta=self.ruta,
                consulta=self.consulta,
                conexion=self.conexion,
                separador=self.separador,
            )
            data = lector.load()
        except (DataLoaderError, OSError, ValueError, sqlite3.Error):
            logger.exception(
                "Error al cargar datos: formato=%s, ruta=%s",
                self.formato,
                self.ruta,
            )
            raise

        logger.info(
            "Carga completada: formato=%s, filas=%d, columnas=%d",
            self.formato,
            len(data),
            len(data.columns),
        )
        return data

    def leer_csv(self) -> pd.DataFrame:
        """Alias de compatibilidad; carga la fuente configurada."""
        return self.load()

