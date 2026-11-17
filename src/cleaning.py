import pandas as pd


class Cleaning:
    """Aplica reglas preliminares de limpieza sobre un DataFrame."""

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = df

    def limpiar_datos(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        """Aplica reglas preliminares de limpieza, sin modelar."""
        data = self.df if df is None else df
        if data is None:
            raise ValueError("Debe proporcionar un DataFrame para limpiar.")

        limpio = data.copy().drop_duplicates()
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

    def clean(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        return self.limpiar_datos(df)

    def __call__(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        return self.limpiar_datos(df)


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Compatibilidad con el API anterior."""
    return Cleaning().limpiar_datos(df)
