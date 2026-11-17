# Lumina ML Framework - Avance 2

Prototipo preliminar y modular en Python para cargar, validar, limpiar, transformar y visualizar datos comerciales, dejandolos preparados para un modelo futuro de prediccion de demanda.

## Requisitos
Python 3.11+ recomendado.

## Instalacion
```bash
pip install -r requirements.txt
```

## Ejecucion
```bash
python generate_sample_data.py
python main.py
```

## Pruebas
```bash
pytest -q
```

## Salidas
`outputs/reports/quality_before.json`, `quality_after.json`, `prepared_data.csv` y graficas en `outputs/figures/`.

Los datos generados son sinteticos y solo sirven para validar el flujo tecnico del Avance 2.
