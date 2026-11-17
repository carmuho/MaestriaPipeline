from pathlib import Path
import pandas as pd


def cargar_csv(ruta: str | Path) -> pd.DataFrame:
    """Carga un CSV comercial y convierte la columna fecha a datetime."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {ruta}")
    return pd.read_csv(ruta, parse_dates=["fecha"])
