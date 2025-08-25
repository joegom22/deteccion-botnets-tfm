import pandas as pd
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re
import random
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Dict

class DataLoader:
    def __init__(self) -> None:
        """
        Initialize the DataLoader object.

        This constructor sets up the initial state of the DataLoader,
        including a configured logger.
        
        Attributes:
            - logger (logging.Logger): Configured logger for the class instance.
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_dataset(self, file_path:str, file_type:str) -> None:
        """
        Load the dataset from the specified file into a pandas DataFrame based on the provided file type.
        
        This method uses the provided file type to determine how to process the file. It supports 
        CSV and Zeek log files.
        Args:
            file_path (str): The path to the file to be loaded.
            file_type (str): The type of the file to be loaded. Supported types are "csv", "zeek", and "txt".

        Raises:
            ValueError: If the provided file type is unsupported.
        """
        if file_type == "csv":
            df = self._load_csv(file_path)
        elif file_type == "zeek":
            df = self._load_zeek(file_path)
        elif file_type == "txt":
            df = self._load_pcapg(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        return df

    def _load_csv(self, file_path:str) -> None:
        """
        Helper method to load standard CSV files into a pandas DataFrame.

        Args:
            file_path (str): The path to the CSV file to be loaded.
        """
        df = None
        try:
            # first row as header
            df = pd.read_csv(file_path, header=0, low_memory=False)
            df = df.drop(df.columns[0], axis=1)
            self.logger.info(f"CSV file loaded successfully: {df.head()}")
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {str(e)}")
        
        return df
    
    def _load_pcapg(self, file_path:str) -> None:
        """
        Helper method to load PCAPG-formatted TXT files into a pandas DataFrame.

        Assumes the first line contains headers and that the file is comma-delimited.

        Args:
            file_path (str): The path to the PCAPG-formatted TXT file to be loaded.
        """
        df = None
        try:
            df = pd.read_csv(file_path, sep=",", header=0, low_memory=False)
            self.logger.info(f"PCAPG-formatted file sampled successfully: {df.shape[0]} rows, {df.shape[1]} columns.")
    
        except Exception as e:
            self.logger.error(f"Error loading PCAPG sample: {str(e)}")
        
        return df

    def _load_zeek(self, file_path:str) -> pd.DataFrame:
        """
        Helper method to load Zeek log files into a pandas DataFrame.

        This method reads the Zeek log file, extracts fields and types from the header,
        and processes the data into a DataFrame. It handles various data types and formats
        according to the Zeek log specifications.

        Args:
            file_path (str): The path to the Zeek log file to be loaded.

        Returns:
            pd.DataFrame: DataFrame containing the processed Zeek log data.
        """
        df = None
        try:
            separator = "\x09"
            empty_field = "(empty)"
            unset_field = "-"
            set_separator = ","
            fields = []
            types = []

            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                for line in file:
                    if not line.startswith("#"):
                        break
                    elif line.startswith("#fields"):
                        fields = line.strip().split()[1:]
                    elif line.startswith("#types"):
                        types = line.strip().split()[1:]

            if not fields:
                raise ValueError("No se encontró línea #fields en el log Zeek y por tanto no pueden extrapolarse los campos.")
            if types and len(types) != len(fields):
                raise ValueError("El número de #types no coincide con #fields.")

            # Carga datos con pandas respetando separadores y comentarios
            df = pd.read_csv(
                file_path,
                sep=separator,
                comment="#",
                names=fields,
                engine="python",
                na_values=[unset_field, empty_field, ""],
                keep_default_na=False
            )

            type_map: Dict[str, str] = {
                "time": "time",
                "interval": "float",
                "count": "int",
                "port": "int",
                "bool": "bool",
                "double": "float",
                "int": "int",
                "string": "str",
                "addr": "str",
                "enum": "str"
            }

            if types:
                for col, t in zip(fields, types):
                    base_t = t
                    if t.startswith("set["):
                        base_t = "str" 
                    base_t = type_map.get(base_t, "str")
                    if base_t == "int":
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                    elif base_t == "float":
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    elif base_t == "bool":
                        df[col] = df[col].map({"T": True, "F": False}).astype("boolean")
                    elif base_t == "time":
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            if "label" in df.columns and df["label"].isna().all():
                split_cols = df["tunnel_parents"].astype(str).apply(
                    lambda x: x.rsplit("  ", 2) if x and x != "nan" else [None]
                )

            tunnel, label, detailed = [], [], []
            for parts in split_cols:
                if len(parts) == 3:
                    tunnel.append(parts[0])
                    label.append(parts[1])
                    detailed.append(parts[2])
                elif len(parts) == 2:
                    tunnel.append(parts[0])
                    label.append(parts[1])
                    detailed.append(None)
                else:
                    tunnel.append(parts[0] if parts else None)
                    label.append(None)
                    detailed.append(None)

            df["tunnel_parents"] = tunnel
            df["label"] = label
            df["detailed-label"] = detailed

            df["label"] = df["label"].str.strip()
            df["detailed-label"] = df["detailed-label"].str.strip()

        except Exception as e:
            self.logger.error(f"Error loading Zeek log file: {str(e)}")
            
        return df
    
    def clean_dataset(self, df: pd.DataFrame) -> None:
        """
        Clean the loaded dataset by removing duplicate entries.

        This method performs a cleaning operation on the loaded dataset:
            1. Removes any duplicate data rows.
        
        Args:
            df (pd.DataFrame): The DataFrame containing the loaded dataset to be cleaned.
        """
        original_count = df.shape[0]

        df = df.drop_duplicates()

        cleaned_count = df.shape[0]
        removed_rows = original_count - cleaned_count

        self.logger.info(f"Dataset cleaned successfully. {removed_rows} rows have been removed.")

        return df