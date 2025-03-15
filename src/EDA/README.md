# `EDA`

Este directorio contiene módulos de soporte para el análisis exploratorio de datos (**EDA**) del dataset **BoT-IoT**.  

## Estructura del Directorio

```
/EDA
│── __init__.py          # Permite tratar EDA como un paquete
│── data_loader.py       # Módulo para cargar datos
│── data_cleaning.py     # Módulo para limpieza de datos
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
from src.data_loader import DataLoader
from src.data_cleaning import DataCleaning

# Cargar datos
loader = DataLoader("data/bot-iot/dataset.csv")
df = loader.load_data()

# Limpiar datos
cleaner = DataCleaning(df)
df = cleaner.clean_data()
```

📌 **Estos módulos son reutilizables y pueden emplearse en futuros análisis de datos.**
