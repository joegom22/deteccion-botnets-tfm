import os
import joblib
import pandas as pd
from src.DataLoader import DataLoader

MODEL_PATHS = {
    "XGBoost": "./pipelines/pipeline_xgboost.sav",
    "MLP": "./pipelines/pipeline_mlp.sav"
}

def load_pipeline(model_name):
    """
    Carga la pipeline entrenada.
    
    Args:
        model_name (str): The name of the model to load.
    """
    return joblib.load(MODEL_PATHS[model_name])

def analyze_traffic(data, model):
    """
    Analyze traffic data and return predictions.

    Args:
        data (list): Raw traffic data to be analyzed.
        model (str): The machine learning model to use for analysis.
    
    Returns:
        list: Predictions based on the input data.
    """
    loader = DataLoader()
    df = loader.load_dataset(data, "csv")
    model_pipeline = load_pipeline(model)
    predictions = model_pipeline.predict(df)
    probabilities = model_pipeline.predict_proba(df)[:, 1]
    results = pd.DataFrame({
        "FlowID": range(len(df)),
        "Prediction": predictions,
        "Probability": probabilities
    })
    results.to_csv('/app/shared/predictions.csv')
    return {"path": "/app/shared/predictions.csv"}