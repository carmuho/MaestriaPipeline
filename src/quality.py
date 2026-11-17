import logging

import pandas as pd

logger = logging.getLogger(__name__)

COLUMNAS_REQUERIDAS = {
    "fecha",
    "categoria",
    "sucursal",
    "precio",
    "promocion",
    "inventario",
    "demanda",
}


class QualityError(ValueError):
    """Error cuando los datos no cumplen el esquema de calidad requerido."""


class Quality:
    """Valida el esquema y calcula indicadores básicos de calidad."""

    def revisar_calidad(self, df: pd.DataFrame) -> dict:
        """Valida las columnas requeridas y devuelve un perfil del DataFrame."""
        logger.info("Iniciando revisión de calidad de los datos.")
        try:
            if not isinstance(df, pd.DataFrame):
                raise TypeError("El argumento df debe ser un pandas DataFrame.")

            # Reportar el esquema faltante antes de calcular indicadores del contenido.
            faltantes = COLUMNAS_REQUERIDAS.difference(df.columns)
            if faltantes:
                raise QualityError(
                    f"Faltan columnas obligatorias: {sorted(faltantes)}"
                )

            perfil = {
                "filas": int(len(df)),
                "columnas": int(len(df.columns)),
                "duplicados": int(df.duplicated().sum()),
                "valores_faltantes": {
                    nombre: int(cantidad)
                    for nombre, cantidad in df.isna().sum().items()
                },
                "tipos": {nombre: str(tipo) for nombre, tipo in df.dtypes.items()},
            }
        except (TypeError, ValueError):
            logger.exception("No se pudo completar la revisión de calidad.")
            raise

        logger.info(
            "Revisión de calidad completada: filas=%d, duplicados=%d",
            perfil["filas"],
            perfil["duplicados"],
        )
        return perfil