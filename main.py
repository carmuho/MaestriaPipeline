from pathlib import Path
import logging

from src.data_loader import DataLoader
from src.quality import Quality
from src.cleaning import limpiar_datos
from src.preprocessing import Preprocessing
from src.visualization import Visualization
from src.reporting import Reporting

BASE_PATH = Path(__file__).parent
logging.basicConfig(
    filename=BASE_PATH / "outputs" / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def ejecutar() -> None:
  
    ruta = BASE_PATH / "data" / "ventas_boreal_simulado.csv"
    datos_originales = DataLoader(ruta).load()
    visualization = Visualization()
    reporting = Reporting()
    quality = Quality()
    
    calidad_antes = quality.revisar_calidad(datos_originales)
    visualization.generar_visualizaciones(
        datos_originales,
        BASE_PATH / "outputs/figures/Datos_Originales",
    )
    reporting.guardar_json(calidad_antes, BASE_PATH / "outputs/reports/quality_before.json")

    datos_limpios = limpiar_datos(datos_originales)
    calidad_despues = quality.revisar_calidad(datos_limpios)
    reporting.guardar_json(calidad_despues, BASE_PATH / "outputs/reports/quality_after.json")

    preprocessing = Preprocessing()
    preparado = preprocessing.crear_variables(datos_limpios)
    X, y = preprocessing.separar_xy(preparado)
    preparado.to_csv(BASE_PATH / "outputs/reports/prepared_data.csv", index=False)
    visualization.generar_visualizaciones(datos_limpios, BASE_PATH / "outputs/figures")

    logging.info("Pipeline preliminar completado: %s filas, %s predictores", len(preparado), X.shape[1])
    print("Calidad antes:", calidad_antes)
    print("Calidad despues:", calidad_despues)
    print("Matriz preparada X:", X.shape, "Variable objetivo y:", y.shape)


if __name__ == "__main__":
    ejecutar()
