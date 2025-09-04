import pandas as pd
import numpy as np
import joblib
import os

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.compose import ColumnTransformer
from xgboost import XGBClassifier

FEATURES = ["num_packets_src", "num_packets_dst", "bytes_src", "bytes_dst", "duration"]
OUTPUT_DIR = "./pipelines"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_preprocessor(X):
    """
    Builds a preprocessor for numerical and categorical features.

    Args:
        X (DataFrame): Input data to determine column types.
    """
    num_cols = [col for col in FEATURES if col in X.select_dtypes(include=["int64", "float64"]).columns]
    cat_cols = [col for col in FEATURES if col in X.select_dtypes(include=["object", "category"]).columns]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ],
        remainder="drop"
    )
    return preprocessor


def build_pipelines(X):
    """
    Builds ML pipelines for different classifiers.

    Args:
        X (DataFrame): Input data to determine column types.
    """
    pre = build_preprocessor(X)
    pipelines = {}

    pipelines["xgboost"] = Pipeline([
        ("pre", pre),
        ("clf", XGBClassifier(learning_rate=0.05, max_depth=None, n_estimators=100, eval_metric="logloss", n_jobs=-1, tree_method="hist", random_state=42))
    ])

    pipelines["mlp"] = Pipeline([
        ("pre", pre),
        ("clf", MLPClassifier(hidden_layer_sizes=(100,), alpha=0.0001, activation="relu", max_iter=200, random_state=42))
    ])

    return pipelines

def preprocess_dataset(df):
    """
    Preprocess the dataset to create the required features.

    Args:
        df (DataFrame): Input dataset with raw features.
    """

    if "src_pkts" in df.columns and "dst_pkts" in df.columns:
        df["num_packets_src"] = pd.to_numeric(df["src_pkts"], errors="coerce").fillna(0).astype(int)
        df["num_packets_dst"] = pd.to_numeric(df["dst_pkts"], errors="coerce").fillna(0).astype(int)

    if "src_bytes" in df.columns and "dst_bytes" in df.columns:
        df["bytes_src"] = pd.to_numeric(df["src_bytes"], errors="coerce").fillna(0).astype(int)
        df["bytes_dst"] = pd.to_numeric(df["dst_bytes"], errors="coerce").fillna(0).astype(int)

    if "Flow Duration" in df.columns:
        df["duration"] = pd.to_numeric(df["Flow Duration"], errors="coerce").fillna(0).astype(float) / 1e6
        df.drop(columns=["Flow Duration"], inplace=True)

    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "src_pkts" in df.columns and "dst_pkts" in df.columns and "src_bytes" in df.columns and "dst_bytes" in df.columns:
        df.drop(columns=["src_pkts", "dst_pkts", "src_bytes", "dst_bytes"], inplace=True)

    return df

def train_and_export(X, y):
    """
    Train pipelines and export them to disk.

    Args:
        X (DataFrame): Feature data.
        y (Series): Target labels.
    """
    pipelines = build_pipelines(X)

    for name, pipe in pipelines.items():
        print(f"Training pipeline: {name.upper()}...")
        pipe.fit(X, y)
        model_path = os.path.join(OUTPUT_DIR, f"pipeline_{name}.sav")
        joblib.dump(pipe, model_path)
        print(f"{name.upper()} saved to {model_path}")


if __name__ == "__main__":
    df = pd.read_csv("../data/Network_dataset_1.csv")

    df = preprocess_dataset(df)

    assert all(col in df.columns for col in FEATURES), "Not all required features are present in the dataset."

    X = df[FEATURES]
    y = df["label"].map(lambda x: 1 if x in ["Malicious", 1] else 0)

    train_and_export(X, y)
