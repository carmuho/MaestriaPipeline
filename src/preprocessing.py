import logging

import pandas as pd

logger = logging.getLogger(__name__)


class Preprocessing:
    """Genera variables y separa predictores de la variable objetivo."""

    def crear_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega variables temporales a partir de la columna ``fecha``."""
        logger.info("Iniciando generación de variables temporales.")
        try:
            if not isinstance(df, pd.DataFrame):
                raise TypeError("El argumento df debe ser un pandas DataFrame.")
            if "fecha" not in df.columns:
                raise ValueError("No existe la columna requerida: fecha.")
            if not pd.api.types.is_datetime64_any_dtype(df["fecha"]):
                raise TypeError("La columna 'fecha' debe tener valores de tipo datetime.")

            # Se conserva la fecha original y se agregan componentes útiles para análisis temporal.
            resultado = df.copy()
            resultado["mes"] = resultado["fecha"].dt.month
            resultado["dia_semana"] = resultado["fecha"].dt.dayofweek
        except (TypeError, ValueError):
            logger.exception("No se pudieron generar las variables temporales.")
            raise

        logger.info("Variables temporales generadas: filas=%d", len(resultado))
        return resultado

    def separar_xy(
        self,
        df: pd.DataFrame,
        objetivo: str = "demanda",
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Separa predictores ``X`` y objetivo ``y`` sin entrenar un modelo."""
        logger.info("Iniciando separación de predictores y objetivo: objetivo=%s", objetivo)
        try:
            if not isinstance(df, pd.DataFrame):
                raise TypeError("El argumento df debe ser un pandas DataFrame.")
            if objetivo not in df.columns:
                raise ValueError(f"No existe la variable objetivo: {objetivo}")
            if "fecha" not in df.columns:
                raise ValueError("No existe la columna requerida: fecha.")

            # La fecha se conserva en los datos preparados, pero se excluye de los predictores.
            X = df.drop(columns=[objetivo, "fecha"])
            y = df[objetivo]
        except (TypeError, ValueError):
            logger.exception("No se pudieron separar los predictores y el objetivo.")
            raise

        logger.info("Separación completada: filas=%d, predictores=%d", len(X), X.shape[1])
        return X, y
