import os
import pandas as pd
from src.DataProcessor import DataProcessor
import pickle

def predict_data(data):
    """
    Load Pickle model and return predictions.

    Args:
        data (list): Preprocessed traffic data for analysis.
    """    
    with open('./models/model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    predictions = model.predict(data)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(data)
        probabilities = probabilities[:, 1]
    else:
        probabilities = [None] * len(predictions)

    return predictions, probabilities

def preprocess_data(file_path):
    """
    Preprocess the input data for prediction.

    Args:
        file_path (str): Path to the dataset file.
    
    Returns:
        DataFrame: Preprocessed data ready for prediction.
    """
    data_processor = DataProcessor(file_path=file_path)
    data_processor.clean_dataset()
    data_processor.normalize_columns()
    data_processor.onehot_encode_columns()
    return data_processor.df

def analyze_traffic(data):
    """
    Analyze traffic data and return predictions.

    Args:
        data (list): Raw traffic data to be analyzed.
    
    Returns:
        list: Predictions based on the input data.
    """
    preprocessed_data = preprocess_data(data)
    predictions, probabilities = predict_data(preprocessed_data)
    # Write a identifier, the predictions and the probabilities into a CSV
    ids = range(len(preprocessed_data))
    results = pd.DataFrame({
        "FlowID": ids,
        "Prediction": predictions,
        "Probability": probabilities
    })
    results.to_csv('/app/shared/predictions.csv', index=False)
    return {"results": results, "path": "/app/shared/predictions.csv"}