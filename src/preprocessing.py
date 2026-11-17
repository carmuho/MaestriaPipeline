import pandas as pd


def crear_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Genera variables temporales y conserva datos listos para preparacion ML."""
    resultado = df.copy()
    resultado["mes"] = resultado["fecha"].dt.month
    resultado["dia_semana"] = resultado["fecha"].dt.dayofweek
    return resultado


def separar_xy(df: pd.DataFrame, objetivo: str = "demanda"):
    """Separa predictores y variable objetivo sin entrenar un modelo."""
    if objetivo not in df.columns:
        raise ValueError(f"No existe la variable objetivo: {objetivo}")
    X = df.drop(columns=[objetivo, "fecha"])
    y = df[objetivo]
    return X, y
