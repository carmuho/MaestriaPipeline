from pathlib import Path
import numpy as np
import pandas as pd


def generar_datos_simulados(n: int = 300, semilla: int = 42) -> pd.DataFrame:
    """Genera datos sinteticos solo para comprobar el flujo preliminar."""
    rng = np.random.default_rng(semilla)
    df = pd.DataFrame({
        "fecha": pd.date_range("2026-01-01", periods=n, freq="D"),
        "categoria": rng.choice(["A", "B", "C"], n),
        "sucursal": rng.choice(["Norte", "Centro", "Sur"], n),
        "precio": np.round(rng.normal(120, 25, n).clip(30, 230), 2),
        "promocion": rng.integers(0, 2, n),
        "inventario": rng.integers(20, 250, n),
    })
    efecto_categoria = df["categoria"].map({"A": 20, "B": 8, "C": -4})
    df["demanda"] = (
        75 - 0.22 * df["precio"] + 18 * df["promocion"]
        + 0.12 * df["inventario"] + efecto_categoria
        + rng.normal(0, 10, n)
    ).round().clip(lower=0)

    # Problemas deliberados para validar calidad y limpieza.
    df.loc[rng.choice(n, 10, replace=False), "precio"] = np.nan
    df.loc[rng.choice(n, 7, replace=False), "categoria"] = None
    df.loc[rng.choice(n, 4, replace=False), "demanda"] *= 4
    return pd.concat([df, df.iloc[:5]], ignore_index=True)


if __name__ == "__main__":
    destino = Path(__file__).parent / "data" / "ventas_boreal_simulado.csv"
    destino.parent.mkdir(exist_ok=True)
    generar_datos_simulados().to_csv(destino, index=False)
    print(f"Dataset sintetico creado: {destino}")
