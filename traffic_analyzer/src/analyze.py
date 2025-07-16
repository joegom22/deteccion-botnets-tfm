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
    return predictions

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
    predictions = predict_data(preprocessed_data)
    return predictions