import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ReportingError(Exception):
    """Error al serializar o guardar un reporte."""


class Reporting:
    """Guarda reportes del pipeline en formatos persistentes."""

    def guardar_json(self, contenido: dict[str, Any], ruta: str | Path) -> None:
        """Serializa un diccionario y lo guarda como archivo JSON."""
        ruta = Path(ruta)
        logger.info("Guardando reporte JSON: ruta=%s", ruta)
        try:
            # Crear la carpeta permite escribir reportes aunque el directorio aún no exista.
            ruta.parent.mkdir(parents=True, exist_ok=True)
            json_contenido = json.dumps(contenido, indent=2, ensure_ascii=False)
            ruta.write_text(json_contenido, encoding="utf-8")
        except (OSError, TypeError, ValueError) as exc:
            logger.exception("No se pudo guardar el reporte JSON: ruta=%s", ruta)
            raise ReportingError(f"No se pudo guardar el reporte JSON '{ruta}'.") from exc

        logger.info("Reporte JSON guardado: ruta=%s", ruta)
