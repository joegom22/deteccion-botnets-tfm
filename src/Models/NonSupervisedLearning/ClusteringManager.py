import pandas as pd
import numpy as np
import logging

from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score

class ClusteringManager:
    def __init__(self, train_dataset: pd.DataFrame, test_dataset: pd.DataFrame) -> None:
        """
        Initialize the ClusteringManager object.

        This constructor sets up the initial state of the ClusteringManager,
        including the dataset to be clustered.

        Args:
            - train_dataset (pd.DataFrame): The DataFrame containing the training dataset to be clustered.
            - test_dataset (pd.DataFrame): The DataFrame containing the testing dataset to be clustered.
        """
        self.train_dataset = train_dataset
        self.test_dataset = test_dataset
        self.models = {}
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def make_model(self, model_name: str = "KMEANS", n_clusters_method: str = "SILHOUETTE") -> None:
        """
        Create a new clustering model with the specified name.

        This method initializes a new clustering model based on the provided name,
        and stores it in the self.models dictionary with the given name.

        Args:
            - model_name (str): The name for the new clustering model. Defaults to "KMEANS".
            - n_clusters_method (str): The method to determine the optimal number of clusters when model is KMEANS. Defaults to "SILHOUETTE".
        """
        if model_name == "KMEANS":
            if n_clusters_method == "SILHOUETTE":
                for i in range(0, 8):
                    silhouette_scores = []
                    model = KMeans(n_clusters=i+2)
                    model.fit(self.train_dataset)
                    silhouette_avg = silhouette_score(self.train_dataset, model.labels_)
                    silhouette_scores.append(silhouette_avg)
                    k = np.argmax(silhouette_scores) + 2
            else:
                self.logger.warning(f"Unsupported n_clusters_method: {n_clusters_method}. Defaulting to 4 clusters.")
                k = 4

            model = KMeans(n_clusters=k)
            self.models[model_name] = model
        elif model_name == "DBSCAN":
            model = DBSCAN()
            self.models[model_name] = model
        elif model_name == "AGGLOMERATIVE":
            model = AgglomerativeClustering()
            self.models[model_name] = model
        else:
            self.logger.warning(f"Unsupported clustering model: {model_name}")
    
    def train_model(self, model_name: str, force_create: bool = True) -> None:
        """
        Train the specified clustering model.

        This method trains the specified clustering model using the dataset,
        and stores the trained model in the self.models dictionary.

        Args:
            - model_name (str): The name of the clustering model to train.
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
    
    def predict_clusters(self, model_name: str) -> pd.Series:
        """
        Predict the clusters for the test dataset using the specified clustering model.

        This method returns a Series containing the predicted clusters for the test dataset
        using the specified clustering model.

        Args:
            - model_name (str): The name of the clustering model to use for prediction.

        Returns:
            - pd.Series: A Series containing the predicted clusters for the test dataset.
        """
        if model_name not in self.models:
            self.logger.warning(f"Model {model_name} has not been trained.")
            clustered_series = pd.Series()
        else:
            clustered_series = self.models[model_name].predict(self.test_dataset)
            self.logger.info(f"Predicted clusters using model: {model_name}")

        return clustered_series
    
    def evaluate_clusters(self, model_name: str) -> None:
        """
        Evaluate the clustering quality using different metrics.

        This method computes the Silhouette Score and Davies-Bouldin Score 
        to evaluate the quality of the clustering produced by the specified model.

        Args:
            - model_name (str): The name of the clustering model to evaluate.
        """
        if model_name not in self.models:
            self.logger.warning(f"Model {model_name} has not been trained.")

        else:
            model = self.models[model_name]
            labels = model.labels_

            silhouette_avg = silhouette_score(self.train_dataset, labels)
            self.logger.info(f"Silhouette Score for model {model_name}: {silhouette_avg}")

            db_score = davies_bouldin_score(self.train_dataset, labels)
            self.logger.info(f"Davies-Bouldin Score for model {model_name}: {db_score}")