"""Interfaces previstas para la siguiente iteracion del framework."""


def entrenar_modelo(*args, **kwargs):
    """Punto de extension futuro para modelos supervisados de regresion."""
    raise NotImplementedError(
        "El entrenamiento completo pertenece a una iteracion posterior del proyecto."
    )
