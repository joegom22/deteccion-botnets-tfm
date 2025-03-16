# `EDA`

Este directorio contiene módulos de soporte para el análisis exploratorio de datos (**EDA**) del dataset **BoT-IoT**.  

## Estructura del Directorio

```
/EDA
│── DataProcessor.py       # Clase para cargar y realizar análisis de Datasets
```

## Descripción de los Módulos

### 🔹 `data_loader.py`
- Carga el dataset desde un archivo CSV en un `pandas.DataFrame`.
- Maneja errores en la carga de datos.

### 🔹 `data_cleaning.py`
- Realiza la limpieza básica del dataset:
  - Elimina valores nulos.
  - Remueve duplicados.

## Uso de los Módulos

Puedes importar estos módulos en el análisis exploratorio de datos:

```python
from src.DataProcessor import DataProcessor
```
