import pandas as pd

COLUMNAS_REQUERIDAS = {
    "fecha", "categoria", "sucursal", "precio",
    "promocion", "inventario", "demanda"
}


def revisar_calidad(df: pd.DataFrame) -> dict:
    """Valida esquema basico y devuelve indicadores de calidad."""
    faltantes = COLUMNAS_REQUERIDAS.difference(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(faltantes)}")
    return {
        "filas": int(len(df)),
        "columnas": int(len(df.columns)),
        "duplicados": int(df.duplicated().sum()),
        "valores_faltantes": {k: int(v) for k, v in df.isna().sum().items()},
        "tipos": {k: str(v) for k, v in df.dtypes.items()},
    }
