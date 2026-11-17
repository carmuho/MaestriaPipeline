import pandas as pd
from src.cleaning import limpiar_datos
from src.quality import revisar_calidad
from src.preprocessing import crear_variables


def muestra():
    return pd.DataFrame({
        "fecha": pd.to_datetime(["2026-01-01", "2026-01-01"]),
        "categoria": [None, None],
        "sucursal": ["norte", "norte"],
        "precio": [100.0, 100.0],
        "promocion": [1, 1],
        "inventario": [50, 50],
        "demanda": [80.0, 80.0],
    })


def test_limpieza_elimina_duplicados_y_faltantes():
    limpio = limpiar_datos(muestra())
    assert len(limpio) == 1
    assert limpio["categoria"].isna().sum() == 0


def test_calidad_detecta_duplicado():
    perfil = revisar_calidad(muestra())
    assert perfil["duplicados"] == 1


def test_features_temporales():
    preparado = crear_variables(limpiar_datos(muestra()))
    assert "mes" in preparado.columns
    assert "dia_semana" in preparado.columns
