import pandas as pd
import logging
import seaborn as sns
import matplotlib.pyplot as plt

class DataProcessor:
    def __init__(self, file_path: str) -> None:
        """
        Initialize the DataProcessor object.

        This constructor sets up the initial state of the DataProcessor,
        including the file path for the dataset, an empty DataFrame,
        and a configured logger.

        Args:
            - file_path (str): The path to the CSV file containing the dataset to be processed.

        Attributes:
            - file_path (str): Stores the path to the dataset file.
            - df (pandas.DataFrame or None): Will store the loaded dataset, initially set to None.
            -outliers (dict): Stores the detected outliers for each column, initially set to an empty dictionary.
            - logger (logging.Logger): Configured logger for the class instance.
        """
        self.file_path = file_path
        self.df = None
        self.outliers = {}
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_dataset(self) -> None:
        """
        Load the dataset from the specified CSV file into a pandas DataFrame.

        This method attempts to read the CSV file specified by self.file_path
        and load it into the self.df attribute. If successful, it logs an info
        message. If an error occurs during the loading process, it logs an
        error message with details of the exception.

        Raises:
            Exception: Any exception that occurs during the file reading process
                       is caught and logged.
        """
        try:
            self.df = pd.read_csv(self.file_path)
            self.logger.info(f"Dataset loaded successfully from {self.file_path}")
        
        except Exception as e:
            self.logger.error(f"Error loading dataset: {str(e)}")
    
    def clean_dataset(self) -> None:
        """
        Clean the loaded dataset by removing null values and duplicate entries.

        This method performs two cleaning operations on the loaded dataset:
            1. Removes any rows with null values.
            2. Removes any duplicate data rows.

        The cleaning operations are performed in-place, that is, modifying the original DataFrame.
        If no dataset has been loaded (self.df is None), a warning message is logged.
        """
        if self.df is not None:
            self.df.dropna(inplace=True)
            self.df.drop_duplicates(inplace=True)
            self.logger.info("Dataset cleaned successfully.")
        else:
            self.logger.watning("No dataset has been loaded.")        
    
    def detect_outliers(self, columns: list = None) -> None:
        """
        Detect outliers in specified columns of the dataset.

        This function identifies outliers in the specified columns of the dataset
        using IQR for numeric columns and Frequency Distribution for categorical ones.
        It processes each column individually and stores the indices of detected outliers.

        Args:
            columns (list): A list of column names to check for outliers. Defaults to all columns in the dataset.

        Raises:
            ValueError: If a specified column doesn't exist in the dataset.                        
        """ 
        columns = columns if columns else self.df.columns.tolist()
        for column in columns:
            if column in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[column]):               
                    logging.info(f"Using Interquartile Range (IQR) method to detect outliers in numerical column '{column}'.")
                    
                    Q1 = self.df[column].quantile(0.25)
                    Q3 = self.df[column].quantile(0.75)

                    IQR = Q3 - Q1

                    lower_limit = Q1 - 1.5 * IQR
                    upper_limit = Q3 + 1.5 * IQR

                    outliers = self.df[(self.df[column] < lower_limit) | (self.df[column] > upper_limit)].index

                    self.outliers[column] = outliers.tolist()
                elif pd.api.types.is_string_dtype(self.df[column]):
                    logging.info(f"Using Frequency Distribution to detect outliers in categorical column {column}.")
                    category_counts = self.df[column].value_counts(normalize=True)

                    outlier_categories = category_counts[category_counts < 0.10].index.tolist()
                    if outlier_categories:
                        self.logger.info(f"Detected outlier categories in column '{column}': {outlier_categories}")

                        for category in outlier_categories:
                            indexes = self.df[self.df[column] == category].index.tolist()
                            self.outliers[category] = indexes
                    else:
                        self.logger.info(f"No outlier categories detected in column '{column}'.")
            else:
                raise ValueError(f"Column '{column}' does not exist in the dataset.")
        
    def detect_correlation(self, column1s: list) -> None:
        """
        Detect correlation between specified columns of the dataset.

        This function calculates the Pearson correlation coefficient between each pair of specified columns
        and stores the results in a DataFrame.

        Args:
            columns (list): A list of column names to check correlation by pairs.

        Raises:
            ValueError: If a specified column doesn't exist in the dataset.                        
        """ 
        columns = columns if columns else self.df.columns.tolist()

        missing = [col for col in columns if col not in self.df.columns]
    
        if missing:
            raise ValueError(f"Columns {missing} do not exist in the dataset.")
        
        correlation_matrix = self.df[columns].corr(method='pearson')

        plt.figure(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)

        plt.title("Matriz de Correlación (Filtrada)")
        plt.show()
        