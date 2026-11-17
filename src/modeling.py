import logging
from typing import Any, NoReturn

logger = logging.getLogger(__name__)


class Modeling:
    """Interfaz para el entrenamiento de modelos de regresión."""

    def entrenar_modelo(self, *args: Any, **kwargs: Any) -> NoReturn:
        """Punto de extensión reservado para una iteración futura."""
        # El entrenamiento aún no forma parte del alcance funcional del proyecto.
        mensaje = (
            "El entrenamiento completo pertenece a una iteracion posterior "
            "del proyecto."
        )
        logger.warning("Se solicitó entrenar un modelo, pero la función no está implementada.")
        raise NotImplementedError(mensaje)
