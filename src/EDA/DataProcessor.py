import pandas as pd
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re
import random

class DataProcessor:
    def __init__(self, file_path: str, attack_type: str = None) -> None:
        """
        Initialize the DataProcessor object.

        This constructor sets up the initial state of the DataProcessor,
        including the file path for the dataset, an empty DataFrame,
        and a configured logger.

        Args:
            - file_path (str): The path to the CSV file containing the dataset to be processed.
            - attack_type (str): The type of attack to be detected in the dataset. Defaults to "All".

        Attributes:
            - file_path (str): Stores the path to the dataset file.
            - df (pandas.DataFrame or None): Will store the loaded dataset, initially set to None.
            -outliers (dict): Stores the detected outliers for each column, initially set to an empty dictionary.
            - logger (logging.Logger): Configured logger for the class instance.
        """
        self.file_path = file_path
        self.df = None
        self.outliers = {}
        self.attack_type = attack_type if attack_type else "All"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_dataset(self, file_type) -> None:
        """
        Load the dataset from the specified file into a pandas DataFrame based on the provided file type.
        
        This method uses the provided file type to determine how to process the file. It supports 
        CSV and Zeek log files.

        Raises:
            ValueError: If the provided file type is unsupported.
        """
        if file_type == "csv":
            self._load_csv()
        elif file_type == "zeek":
            self._load_zeek()
        elif file_type == "txt":
            self._load_pcapg()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


    def _load_csv(self) -> None:
        """
        Helper method to load standard CSV files into a pandas DataFrame.
        """
        try:
            self.df = pd.read_csv(self.file_path, header=None, low_memory=False)
            self.df = self.df.drop(self.df.columns[0], axis=1)
            self.logger.info(f"CSV file loaded successfully: {self.df.head()}")
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {str(e)}")
    
    def _load_pcapg(self) -> None:
        """
        Helper method to load PCAPG-formatted TXT files into a pandas DataFrame.

        Assumes the first line contains headers and that the file is comma-delimited.
        """
        try:
            # Contar total de filas (sin cargar en memoria)
            #with open(self.file_path, "r") as f:
            #    total_lines = sum(1 for _ in f) - 1  # menos la cabecera
            #    sample_size = total_lines // 40
#
            #if sample_size  >= total_lines:
            #    skip = []
            #else:
            #    # Elegir líneas a saltar aleatoriamente (excluyendo la cabecera = línea 0)
            #    skip = sorted(random.sample(range(1, total_lines + 1), total_lines - sample_size))
#
            ## Leer el archivo saltando las filas seleccionadas
            self.df = pd.read_csv(self.file_path, sep=",", header=0, low_memory=False)
            self.logger.info(f"PCAPG-formatted file sampled successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns.")
    
        except Exception as e:
            self.logger.error(f"Error loading PCAPG sample: {str(e)}")


    def _load_zeek(self) -> None:
        """
        Helper method to load Zeek logs into a pandas DataFrame.
        
        This method expects a Zeek log format with headers starting with '#fields'
        and data separated by tabs or multiple spaces.
        """
        headers = []
        types = []
        data_lines = []
        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#fields"):
                    headers = re.split(r"\t+|\s{2,}", line)[1:]
                elif line.startswith("#types"):
                    types = re.split(r"\t+|\s{2,}", line)[1:]
                elif not line.startswith("#"):
                    data_lines.append(re.split(r"\t+|\s{2,}", line))

        df = pd.DataFrame(data_lines, columns=headers)

        df.replace('-', np.nan, inplace=True)

        convert_dict = {
            "time": float,
            "port": str,
            "interval": float,
            "count": pd.to_numeric,
            "bool": lambda x: "1" if x == "T" else "0",
        }
        for col, col_type in zip(headers, types):
            if col_type in convert_dict:
                df[col] = df[col].apply(convert_dict[col_type])
        
        print(df.head())

        self.df = df
    
    def clean_dataset(self, drop_nulls: bool = False) -> None:
        """
        Clean the loaded dataset by removing duplicate entries and, optionally, null ones.

        This method performs two cleaning operations on the loaded dataset:
            1. Removes any rows with null values.
            2. Removes any duplicate data rows.

        The cleaning operations are performed in-place, that is, modifying the original DataFrame.
        If no dataset has been loaded (self.df is None), a warning message is logged.

        Args:
            drop_nulls (bool): If True, remove rows with null values. Defaults to False.
        """
        if self.df is not None:
            original_count = self.df.shape[0]

            if drop_nulls:
                self.df = self.df.dropna()

            self.df = self.df.drop_duplicates()

            cleaned_count = self.df.shape[0]
            removed_rows = original_count - cleaned_count

            self.logger.info(f"Dataset cleaned successfully. {removed_rows} rows have been removed.")
        else:
            self.logger.warning("No dataset has been loaded.")        
    
    def onehot_encode_columns(self, columns: list = None, mode: str = "replace"):
        """
        One-hot encode specified columns in the dataset.

        This method encodes categorical variables into multiple binary features,
        creating new columns for each unique value in the specified columns.

        Args:
            columns (list): A list of column names to encode. Defaults to all categorical columns in the dataset.
            mode (str): The mode to handle duplicate values in categorical columns. Options are "replace" (replace with a unique value) or "drop" (drop the duplicate values).

        Raises:
            ValueError: If a specified column doesn't exist in the dataset.
        """
        columns = [col for col in (columns if columns else self.df.select_dtypes(include=['object']).columns.tolist()) if col not in ['ts', 'uid', 'label', 'detailed-label', 'tunnel_parents']]


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
        columns = [col for col in (columns if columns else self.df.columns.tolist()) if col not in ['ts', 'uid', 'label', 'detailed-label', 'tunnel_parents', 'StartTime', 'LastTime']]
        self.outliers_text = ""
        ddos_text = "Possible DDoS attack detected, high frequency values in columns: "
        others_text = "Possible attack detected, anomalies in columns: "
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

                    if len(outliers) > 0:
                        others_text += f"'{column}', "
                    sns.boxplot(x=self.df[column])

                    plt.title(f'Boxplot de la columna {column}')
                    plt.xlabel(f'Valores de {column}')

                    plt.show()

                elif pd.api.types.is_string_dtype(self.df[column]):
                    self.logger.info(f"Using Frequency Distribution to detect outliers in categorical column {column}.")
                    category_counts = self.df[column].value_counts(normalize=True)
                    #self.logger.info(f"Category count for {column}: {category_counts}")
                    if self.attack_type == "DDOS":
                        self.logger.info(f"Since attack type is DDOS, categorical outliers will be those above a threshold.")
                        outlier_categories = category_counts[category_counts > 0.90].index.tolist()
                    elif self.attack_type == "All":
                        self.logger.info(f"Since attack type is All, categorical outliers will be those both below a threshold or above a threshold.")
                        if column == "SrcAddr":
                            categorias_deseadas = [
                                # 🦠 Infected host (botnet)
                                "147.32.84.165",

                                # ✅ Normal hosts confiables
                                "147.32.84.170",  # Normal-V42-Stribrek
                                "147.32.84.134",  # Normal-V42-Jist
                                "147.32.84.164",  # Normal-V42-Grill

                                # ⚠️ Normal hosts no tan confiables (pero los puedes incluir si quieres)
                                "147.32.87.36",   # CVUT-WebServer
                                "147.32.80.9",    # CVUT-DNS-Server
                                "147.32.87.11",   # MatLab-Server
                            ]
                            category_counts = category_counts[category_counts.index.isin(categorias_deseadas)]
                        outlier_categories_high = category_counts[category_counts > 0.90].index.tolist()
                    else:
                        self.logger.info(f"Since attack type is not DDOS, categorical outliers will be those below a threshold.")
                        outlier_categories = category_counts[category_counts < 0.10].index.tolist()
                    ddos_text += f"'{column}', "
                    sns.barplot(x=category_counts.index, y=category_counts.values)

                    # Añadir título y etiquetas
                    plt.title(f'Frecuencias de la columna {column}')
                    plt.xlabel('Categorías')
                    plt.ylabel('Proporción')

                    # Mostrar el gráfico
                    plt.xticks(rotation=45)  # Opcional: rotar las etiquetas del eje x si es necesario
                    plt.show()
                
            else:
                raise ValueError(f"Column '{column}' does not exist in the dataset.")
        
        ddos_text = ddos_text[:-2]
        others_text = others_text[:-2]
        self.outliers_text += f"\n{ddos_text}\n{others_text}"
        
    def detect_correlation(self, columns: list = None) -> None:
        """
        Detect correlation between specified columns of the dataset.

        This function calculates the Pearson correlation coefficient between each pair of specified columns
        and stores the results in a DataFrame.

        Args:
            columns (list): A list of column names to check correlation by pairs.

        Raises:
            ValueError: If a specified column doesn't exist in the dataset.                        
        """ 
        columns = [col for col in (columns if columns else self.df.columns.tolist()) if col not in ['ts', 'uid'] and pd.api.types.is_numeric_dtype(self.df[col])]

        missing = [col for col in columns if col not in self.df.columns]
    
        if missing:
            raise ValueError(f"Columns {missing} do not exist in the dataset.")
        
        correlation_matrix = self.df[columns].corr(method='pearson')

        plt.figure(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)

        plt.title("Matriz de Correlación (Filtrada)")
        #plt.savefig("./src/EDA/assets/correl_matrix.png", dpi=300, bbox_inches="tight")
        plt.show()

        strong_correlations = []
        for col1 in correlation_matrix.columns:
            for col2 in correlation_matrix.columns:
                if col1 != col2:
                    corr_value = correlation_matrix.loc[col1, col2]
                    if abs(corr_value) >= 0.75:
                        strong_correlations.append((col1, col2, corr_value))
        
        self.correlation_text = f"Correlaciones fuertes: "
        if strong_correlations:
            for col1, col2, value in sorted(strong_correlations, key=lambda x: -abs(x[2])):
                direction = "positiva" if value > 0 else "negativa"
                self.correlation_text += f"**{col1}** y **{col2}** tienen una correlación {direction} fuerte (**r = {value:.2f}**). "
        