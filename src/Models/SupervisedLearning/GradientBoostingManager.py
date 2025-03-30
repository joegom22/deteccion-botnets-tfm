import pandas as pd
import numpy as np
import logging

from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class GradientBoostingManager:
    def __init__(self, train_features: pd.DataFrame, train_labels: pd.Series, test_features: pd.DataFrame, test_labels: pd.Series) -> None:
        """
        Initialize the GradientBoostingManager object.

        This constructor sets up the initial state of the GradientBoostingManager, 
        including the training and testing datasets.

        Args:
            - train_features (pd.DataFrame): Features of the training dataset.
            - train_labels (pd.Series): Labels of the training dataset.
            - test_features (pd.DataFrame): Features of the testing dataset.
            - test_labels (pd.Series): Labels of the testing dataset.
        """
        self.train_features = train_features
        self.train_labels = train_labels
        self.test_features = test_features
        self.test_labels = test_labels
        self.models = {}
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def make_model(self, model_name: str = "XGBOOST", params: dict = None) -> None:
        """
        Create a new Gradient Boosting model with the specified name.

        It supports the following models: XGBOOST, LIGHTGBM, and GRADIENTBOOST.

        Args:
            - model_name (str): The name for the new model. Defaults to "XGBOOST".
            - params (dict): A dictionary of hyperparameters for the model. Defaults to None.
        """
        default_params = {
            "XGBOOST": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 6, "use_label_encoder": False, "eval_metric": "logloss"},
            "LIGHTGBM": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": -1},
            "GRADIENTBOOST": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3}
        }

        params = params if params else default_params.get(model_name, {})

        if model_name == "XGBOOST":
            model = XGBClassifier(**params)
            self.models[model_name] = model
            self.logger.info(f"Created new model: {model_name} with params {params}")
        elif model_name == "LIGHTGBM":
            model = LGBMClassifier(**params)
            self.models[model_name] = model
            self.logger.info(f"Created new model: {model_name} with params {params}")
        elif model_name == "GRADIENTBOOST":
            model = GradientBoostingClassifier(**params)
            self.models[model_name] = model
            self.logger.info(f"Created new model: {model_name} with params {params}")
        else:
            self.logger.warning(f"Unsupported model: {model_name}")

    def train_model(self, model_name: str, force_create: bool = True) -> None:
        """
        Train the specified model.

        Args:
            - model_name (str): The name of the model to train.
            - force_create (bool): Whether to create the model if it does not exist. Defaults to True.
        """
        if model_name not in self.models and not force_create:
            self.logger.warning(f"Model {model_name} has not been created.")

        elif model_name not in self.models and force_create:
            self.make_model(model_name)
            self.logger.info(f"Created new model: {model_name}")
            self.logger.info(f"Training model: {model_name}")
            self.models[model_name].fit(self.train_features, self.train_labels)
        
        else:
            self.logger.info(f"Training model: {model_name}")
            self.models[model_name].fit(self.train_features, self.train_labels)

    def predict(self, model_name: str) -> pd.Series:
        """
        Make predictions on the test dataset using the specified model.

        Args:
            - model_name (str): The name of the model to use for prediction.

        Returns:
            - pd.Series: A Series containing the predicted labels for the test dataset.
        """
        if model_name not in self.models:
            self.logger.warning(f"Model {model_name} has not been trained.")
            predictions = pd.Series(dtype="int")
        else:
            predictions = pd.Series(self.models[model_name].predict(self.test_features))
            self.logger.info(f"Predictions made using model: {model_name}")

        return predictions

    def evaluate_model(self, model_name: str) -> None:
        """
        Evaluate the model's performance using accuracy, precision, recall, and F1-score.

        Args:
            - model_name (str): The name of the model to evaluate.
        """
        if model_name not in self.models:
            self.logger.warning(f"Model {model_name} has not been trained.")
            return

        predictions = self.predict(model_name)
        accuracy = accuracy_score(self.test_labels, predictions)
        precision = precision_score(self.test_labels, predictions, average="weighted", zero_division=0)
        recall = recall_score(self.test_labels, predictions, average="weighted", zero_division=0)
        f1 = f1_score(self.test_labels, predictions, average="weighted", zero_division=0)

        self.logger.info(f"Model {model_name} - Accuracy: {accuracy:.4f}")
        self.logger.info(f"Model {model_name} - Precision: {precision:.4f}")
        self.logger.info(f"Model {model_name} - Recall: {recall:.4f}")
        self.logger.info(f"Model {model_name} - F1 Score: {f1:.4f}")
