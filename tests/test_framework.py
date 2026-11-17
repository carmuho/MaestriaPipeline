import json
import logging
import sqlite3

import pandas as pd
import pytest
from src.cleaning import Cleaning, limpiar_datos
from src.data_loader import (
    DataLoader,
    DataLoaderError,
    UnsupportedDataFormatError
)
from src.quality import Quality, QualityError
from src.preprocessing import Preprocessing
from src.reporting import Reporting, ReportingError
from src.visualization import Visualization
from src.modeling import Modeling


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
    perfil = Quality().revisar_calidad(muestra())
    assert perfil["duplicados"] == 1


def test_quality_clase_registra_resultado_y_error(caplog):
    with caplog.at_level(logging.INFO, logger="src.quality"):
        perfil = Quality().revisar_calidad(muestra())

    assert perfil["filas"] == 2
    assert "Revisión de calidad completada" in caplog.text

    with caplog.at_level(logging.ERROR, logger="src.quality"):
        with pytest.raises(QualityError, match="Faltan columnas obligatorias"):
            Quality().revisar_calidad(pd.DataFrame({"fecha": []}))

    assert "No se pudo completar la revisión de calidad" in caplog.text


def test_clases_exponen_interface_objetual():
    limpio = Cleaning().limpiar_datos(muestra())
    assert len(limpio) == 1
    assert DataLoader.cargar_csv.__name__ == "cargar_csv"


def test_data_loader_lee_json_y_txt(tmp_path, caplog):
    json_path = tmp_path / "ventas.json"
    txt_path = tmp_path / "ventas.txt"
    json_path.write_text('[{"producto":"A","precio":10}]', encoding="utf-8")
    txt_path.write_text("producto;precio\nA;10\n", encoding="utf-8")

    with caplog.at_level(logging.INFO, logger="src.data_loader"):
        json_data = DataLoader(json_path).load()
        txt_data = DataLoader(txt_path, separador=";").load()

    assert json_data.to_dict("records") == [{"producto": "A", "precio": 10}]
    assert txt_data.to_dict("records") == [{"producto": "A", "precio": 10}]
    assert "Iniciando carga de datos" in caplog.text
    assert "Carga completada" in caplog.text


def test_data_loader_informa_formato_no_soportado(tmp_path):
    with pytest.raises(UnsupportedDataFormatError, match="Formato no compatible"):
        DataLoader(tmp_path / "ventas.xlsx").load()


def test_data_loader_envuelve_errores_de_lectura_json(tmp_path, caplog):
    json_path = tmp_path / "ventas.json"
    json_path.write_text("{", encoding="utf-8")

    with caplog.at_level(logging.ERROR, logger="src.data_loader"):
        with pytest.raises(DataLoaderError, match="No se pudo leer el archivo JSON"):
            DataLoader(json_path).load()

    assert "Error al cargar datos" in caplog.text


def test_data_loader_conserva_carga_csv(tmp_path):
    csv_path = tmp_path / "ventas.csv"
    csv_path.write_text("fecha,producto\n2026-01-01,A\n", encoding="utf-8")

    data = DataLoader(csv_path).load()
    legacy_data = DataLoader(csv_path).load()

    assert pd.api.types.is_datetime64_any_dtype(data["fecha"])
    pd.testing.assert_frame_equal(data, legacy_data)


def test_data_loader_lee_consulta_sql_desde_sqlite(tmp_path):
    database_path = tmp_path / "ventas.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE ventas (producto TEXT, precio INTEGER)")
        connection.execute("INSERT INTO ventas VALUES ('A', 10)")

    data = DataLoader(
        database_path,
        formato="sql",
        consulta="SELECT producto, precio FROM ventas",
    ).load()

    assert data.to_dict("records") == [{"producto": "A", "precio": 10}]


def test_features_temporales():
    preparado = Preprocessing().crear_variables(limpiar_datos(muestra()))
    assert "mes" in preparado.columns
    assert "dia_semana" in preparado.columns


def test_preprocessing_clase_separa_predictores_y_objetivo():
    preparado = Preprocessing().crear_variables(muestra())
    X, y = Preprocessing().separar_xy(preparado)

    assert "fecha" not in X.columns
    assert "demanda" not in X.columns
    assert y.equals(preparado["demanda"])


def test_preprocessing_valida_fecha_y_registra_error(caplog):
    with caplog.at_level(logging.ERROR, logger="src.preprocessing"):
        with pytest.raises(ValueError, match="No existe la columna requerida: fecha"):
            Preprocessing().crear_variables(pd.DataFrame({"demanda": [1]}))

    assert "No se pudieron generar las variables temporales" in caplog.text


def test_separar_xy_compatibilidad_y_objetivo_inexistente():
    X, y = Preprocessing().separar_xy(muestra())

    assert "fecha" not in X.columns
    assert y.name == "demanda"
    with pytest.raises(ValueError, match="No existe la variable objetivo"):
        Preprocessing().separar_xy(muestra(), "ventas")


def test_visualization_clase_y_funcion_compatibilidad(tmp_path):
    class_files = Visualization().generar_visualizaciones(muestra(), tmp_path / "class")

    assert [path.name for path in class_files] == [
        "distribucion_demanda.png",
        "demanda_por_promocion.png",
    ]


def test_reporting_guarda_json_y_registra_operacion(tmp_path, caplog):
    reporte = {"resultado": "válido", "filas": 3}
    ruta = tmp_path / "reportes" / "calidad.json"

    with caplog.at_level(logging.INFO, logger="src.reporting"):
        Reporting().guardar_json(reporte, ruta)

    assert json.loads(ruta.read_text(encoding="utf-8")) == reporte
    assert "Guardando reporte JSON" in caplog.text
    assert "Reporte JSON guardado" in caplog.text


def test_reporting_informa_error_de_serializacion(tmp_path, caplog):
    with caplog.at_level(logging.ERROR, logger="src.reporting"):
        with pytest.raises(ReportingError, match="No se pudo guardar el reporte JSON"):
            Reporting().guardar_json({"dato": object()}, tmp_path / "reporte.json")

    assert "No se pudo guardar el reporte JSON" in caplog.text


def test_modeling_registra_y_expone_entrenamiento_no_implementado(caplog):
    with caplog.at_level(logging.WARNING, logger="src.modeling"):
        with pytest.raises(NotImplementedError, match="iteracion posterior"):
            Modeling().entrenar_modelo()

