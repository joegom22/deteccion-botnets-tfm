import pandas as pd
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re
import random
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import LabelEncoder, StandardScaler

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
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()
        self.categorical_columns = []
        self.numeric_columns = []
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
        
        self.categorical_columns = self.df.select_dtypes(include=[object]).columns.tolist()
        self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()

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
        i = 0
        with open(self.file_path, "r") as f:
            for line in f:
                if i % 3 == 0:
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
    
    def clean_dataset(self, drop_nulls: bool = True) -> None:
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
                #self.df = self.df.dropna()
                self.df = self.df.fillna(value=0)

            self.df = self.df.drop_duplicates()

            cleaned_count = self.df.shape[0]
            removed_rows = original_count - cleaned_count

            self.logger.info(f"Dataset cleaned successfully. {removed_rows} rows have been removed.")
        else:
            self.logger.warning("No dataset has been loaded.")

    def normalize_columns(self, columns: list = None) -> None:
        """
        Normalize specified columns in the dataset.

        This method normalizes the values in the specified columns using Min-Max scaling,
        which scales the values to a range between 0 and 1.

        Args:
            columns (list): A list of column names to normalize. Defaults to all numeric columns in the dataset.

        Raises:
            ValueError: If a specified column doesn't exist in the dataset.
        """
        if self.df is not None:
            if columns is None:
                columns = self.numeric_columns
            else:
                missing = [col for col in columns if col not in self.df.columns]
                if missing:
                    raise ValueError(f"Some specified of the columns do not exist in the dataset: {missing}.")

            self.df[columns] = self.scaler.fit_transform(self.df[columns])
            
            self.logger.info(f"Columns {columns} normalized successfully.")
        else:
            self.logger.warning("No dataset has been loaded.")        
    
    def onehot_encode_columns(self, columns: list = None):
        """
        One-hot encode specified columns in the dataset.

        This method encodes categorical variables into multiple binary features,
        creating new columns for each unique value in the specified columns.

        Args:
            columns (list): A list of column names to encode. Defaults to all categorical columns in the dataset.

        Raises:
            ValueError: If a specified column doesn't exist in the dataset.
        """
        if self.df is not None:
            if columns is None:
                columns = self.categorical_columns
            else:
                missing = [col for col in columns if col not in self.df.columns]
                if missing:
                    raise ValueError(f"Some specified of the columns do not exist in the dataset: {missing}.")

            for column in columns:
                if "Time" not in column:
                    self.logger.info(f"One-hot encoding column: {column}")
                    encoded = self.encoder.fit_transform(self.df[column])
                    self.df[column] = encoded
                    self.logger.info(f"Column {column} one-hot encoded successfully.")

            self.logger.info(f"Columns {columns} one-hot encoded successfully.")
        else:
            self.logger.warning("No dataset has been loaded.")

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
            if column in self.numeric_columns:
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

            elif column in self.categorical_columns:
                self.logger.info(f"Using Frequency Distribution to detect outliers in categorical column {column}.")
                category_counts = self.df[column].value_counts(normalize=True) if "Addr" not in column and "port" not in column else self.df[column].value_counts(normalize=True).head(10)
                #self.logger.info(f"Category count for {column}: {category_counts}")
                
                outlier_categories_high = category_counts[category_counts > 0.90].index.tolist()

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

        plt.title("Matriz de Correlación")
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

    def analyze_temporal_ddos_patterns(self):
        """
        Realiza análisis temporal agrupado por minuto para detectar posibles patrones DDoS.
        Utiliza la columna 'StartTime' como índice de tiempo y grafica actividad por minuto.
        """
        if 'StartTime' not in self.df.columns:
            self.logger.error("'StartTime' column not found in the dataset.")
            return

        try:
            # Asegurar formato datetime y establecer índice
            self.df['StartTime'] = pd.to_datetime(self.df['StartTime'], format="%Y/%m/%d %H:%M:%S.%f", errors='coerce')
            df_time = self.df.set_index('StartTime')

            # Agrupación por minuto
            df_min = df_time.resample('1min').agg({
                'SrcAddr': 'count',              # Cantidad de conexiones por minuto
                'DstAddr': pd.Series.nunique,    # Número de destinos únicos
                'SrcPkts': 'sum',
                'DstPkts': 'sum',
                'TotBytes': 'sum',
                'Dur': 'mean',
            }).rename(columns={'SrcAddr': 'Connections', 'DstAddr': 'UniqueDest'})

            # Reemplazar NaNs por 0
            df_min.fillna(0, inplace=True)

            # Crear ratio Src/Dst packets
            df_min['PktRatio'] = df_min['SrcPkts'] / df_min['DstPkts'].replace(0, 1)

            # Plot 1: Conexiones por minuto
            df_min['Connections'].plot(figsize=(14, 4), title="Conexiones por minuto")
            plt.ylabel("Conexiones")
            plt.grid(True)
            plt.show()

            # Plot 2: Bytes totales por minuto
            df_min['TotBytes'].plot(figsize=(14, 4), title="Total de bytes por minuto")
            plt.ylabel("Bytes")
            plt.grid(True)
            plt.show()

            # Plot 3: Ratio SrcPkts / DstPkts
            df_min['PktRatio'].plot(figsize=(14, 4), title="Relación de paquetes enviados vs recibidos")
            plt.ylabel("Ratio")
            plt.grid(True)
            plt.show()

            if 'Dur' in df_time.columns:
                short_conns_per_min = df_time[df_time['Dur'] < 1.0].resample('1min').size()
                plt.figure(figsize=(12, 4))
                short_conns_per_min.plot(color='green')
                plt.title("Conexiones < 1s por minuto")
                plt.ylabel("Cortas")
                plt.xlabel("Tiempo")
                plt.grid(True)
                plt.tight_layout()
                plt.show()
            
            if 'DstAddr' in df_time.columns:
                dst_ips_per_min = df_min['UniqueDest']
                plt.figure(figsize=(12, 4))
                dst_ips_per_min.plot(color='orange')
                plt.title("Direcciones IP destino únicas por minuto")
                plt.ylabel("IPs únicas")
                plt.xlabel("Tiempo")
                plt.grid(True)
                plt.tight_layout()
                plt.show()

            self.logger.info("Análisis temporal completado.")
        except Exception as e:
            self.logger.error(f"Error during temporal analysis: {e}")

    def select_anova_features(self, target: str, alpha: float = 0.05) -> list:
        """
        Select features based on ANOVA F-test.

        This method selects features that are statistically significant
        with respect to the target variable using ANOVA F-test.

        Args:
            target (str): The target variable for the ANOVA test.
            alpha (float): The significance level for the ANOVA test. Defaults to 0.05.

        Returns:
            list: A list of selected feature names.
        """
        X = self.df.drop(columns=[target])
        # Take only numeric columns
        X = X.select_dtypes(include=[np.number])
        # Fill NaN values with the mean of each column
        X.fillna(X.mean(), inplace=True)
        y = self.df[target]

        selector = SelectKBest(score_func=f_classif, k='all')
        selector.fit(X, y)

        mask = selector.get_support()
        selected_features = X.columns[mask].tolist()

        return selected_features
    