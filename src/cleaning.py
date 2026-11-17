import pandas as pd


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica reglas preliminares de limpieza, sin modelar."""
    limpio = df.copy().drop_duplicates()
    limpio["categoria"] = (
        limpio["categoria"].fillna("DESCONOCIDA").astype(str).str.strip().str.upper()
    )
    limpio["sucursal"] = limpio["sucursal"].astype(str).str.strip().str.title()
    limpio["precio"] = pd.to_numeric(limpio["precio"], errors="coerce")
    limpio["precio"] = limpio["precio"].fillna(limpio["precio"].median())

    # Tratamiento preliminar de outliers de demanda mediante IQR.
    q1, q3 = limpio["demanda"].quantile([0.25, 0.75])
    iqr = q3 - q1
    limite_superior = q3 + (1.5 * iqr)
    limpio["demanda"] = limpio["demanda"].clip(upper=limite_superior)
    return limpio
