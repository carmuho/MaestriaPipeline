from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class Visualization:
    """Genera gráficos exploratorios para analizar la demanda."""

    def generar_visualizaciones(
        self,
        df: pd.DataFrame,
        carpeta: str | Path,
    ) -> list[Path]:
        """Guarda la distribución de demanda y su relación con promociones."""
        carpeta = Path(carpeta)
        carpeta.mkdir(parents=True, exist_ok=True)
        archivos = []

        # El histograma muestra la distribución general de las unidades demandadas.
        distribucion = carpeta / "distribucion_demanda.png"
        plt.figure(figsize=(8, 5))
        sns.histplot(data=df, x="demanda", kde=True, color="steelblue")
        plt.title("Distribucion de la demanda")
        plt.xlabel("Unidades demandadas")
        plt.ylabel("Frecuencia")
        plt.tight_layout()
        plt.savefig(distribucion, dpi=160)
        plt.close()
        archivos.append(distribucion)

        # El diagrama de caja permite comparar demanda entre registros con/sin promoción.
        promociones = carpeta / "demanda_por_promocion.png"
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df, x="promocion", y="demanda", color="lightblue")
        plt.title("Demanda segun presencia de promocion")
        plt.xlabel("Promocion: 0 = No, 1 = Si")
        plt.ylabel("Unidades demandadas")
        plt.tight_layout()
        plt.savefig(promociones, dpi=160)
        plt.close()
        archivos.append(promociones)
        return archivos
