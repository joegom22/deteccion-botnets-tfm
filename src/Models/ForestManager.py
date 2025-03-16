import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

class ForestManager:
    def __init__(self, train_dataset: pd.DataFrame, test_dataset: pd.DataFrame) -> None:
        """
        Initialize the ForestManager object.

        This constructor sets up the initial state of the ForestManager,
        including the training and testing datasets."
        """
        self.train_dataset = train_dataset
        self.test_dataset = test_dataset
        self.models = {}
    
    def make_model(self, model_name: str) -> None:
        """
        Create a new random forest model with the specified name.

        This method initializes a new random forest model based on the provided name,
        and stores it in the self.models dictionary with the given name.

        Args:
            - model_name (str): The name for the new random forest model.
        """
        if model_name == "RANDOM_FOREST":
            model = RandomForestClassifier()
            self.models[model_name] = model
        elif model_name == "ISOLATION_FOREST":
            model = IsolationForestClassifier()
            self.models[model_name] = model
        else:
            self.logger.warning(f"Unsupported model: {model_name}")
    
    def train_model(self, model_name: str, force_create: bool = True) -> None:
        """
        Train the specified random forest model.

        This method trains the specified random forest model using the training dataset,
        and stores the trained model in the self.models dictionary.

        Args:
            - model_name (str): The name of the random forest model to train.
            - force_create (bool): Whether to create the model if it does not exist. Defaults to True.
        """
        if model_name not in self.models and not force_create:
            self.logger.warning(f"Model {model_name} has not been created.")

        elif model_name not in self.models and force_create:
            self.make_model(model_name)
            self.logger.info(f"Created new clustering model: {model_name}")
            self.logger.info(f"Training model: {model_name}")
            self.models[model_name].fit(self.train_dataset)
        
        else:
            self.logger.info(f"Training model: {model_name}")
            self.models[model_name].fit(self.train_dataset)