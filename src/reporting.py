from pathlib import Path
import json


def guardar_json(contenido: dict, ruta: str | Path) -> None:
    """Guarda un diccionario como evidencia de trazabilidad."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, indent=2, ensure_ascii=False), encoding="utf-8")
