from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def generar_visualizaciones(df: pd.DataFrame, carpeta: str | Path) -> list[Path]:
    """Genera dos visualizaciones exploratorias preliminares."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    archivos = []

    p1 = carpeta / "distribucion_demanda.png"
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x="demanda", kde=True, color="steelblue")
    plt.title("Distribucion de la demanda")
    plt.xlabel("Unidades demandadas")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(p1, dpi=160)
    plt.close()
    archivos.append(p1)

    p2 = carpeta / "demanda_por_promocion.png"
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="promocion", y="demanda", color="lightblue")
    plt.title("Demanda segun presencia de promocion")
    plt.xlabel("Promocion: 0 = No, 1 = Si")
    plt.ylabel("Unidades demandadas")
    plt.tight_layout()
    plt.savefig(p2, dpi=160)
    plt.close()
    archivos.append(p2)
    return archivos
