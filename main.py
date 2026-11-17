from pathlib import Path
import logging

from src.data_loader import cargar_csv
from src.quality import revisar_calidad
from src.cleaning import limpiar_datos
from src.preprocessing import crear_variables, separar_xy
from src.visualization import generar_visualizaciones
from src.reporting import guardar_json

BASE = Path(__file__).parent
logging.basicConfig(
    filename=BASE / "outputs" / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def ejecutar() -> None:
    """Ejecuta el alcance funcional del Avance 2, sin entrenar modelos."""
    ruta = BASE / "data" / "ventas_boreal_simulado.csv"
    bruto = cargar_csv(ruta)
    calidad_antes = revisar_calidad(bruto)
    guardar_json(calidad_antes, BASE / "outputs/reports/quality_before.json")

    limpio = limpiar_datos(bruto)
    calidad_despues = revisar_calidad(limpio)
    guardar_json(calidad_despues, BASE / "outputs/reports/quality_after.json")

    preparado = crear_variables(limpio)
    X, y = separar_xy(preparado)
    preparado.to_csv(BASE / "outputs/reports/prepared_data.csv", index=False)
    generar_visualizaciones(limpio, BASE / "outputs/figures")

    logging.info("Pipeline preliminar completado: %s filas, %s predictores", len(preparado), X.shape[1])
    print("Calidad antes:", calidad_antes)
    print("Calidad despues:", calidad_despues)
    print("Matriz preparada X:", X.shape, "Variable objetivo y:", y.shape)


if __name__ == "__main__":
    ejecutar()
