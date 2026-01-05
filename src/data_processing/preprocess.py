"""
Data preprocessing pipeline for Heart Disease dataset
"""
import os
import zipfile
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def extract_data(zip_path: str, data_dir: str) -> None:
    """Extract data from zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    print(f"Data extracted to {data_dir}")


def load_data(data_dir: str) -> pd.DataFrame:
    """Load and combine all .data files"""
    columns = [
        "age", "sex", "cp", "trestbps", "chol",
        "fbs", "restecg", "thalach", "exang",
        "oldpeak", "slope", "ca", "thal", "target"
    ]
    
    dfs = []
    for file in os.listdir(data_dir):
        if file.endswith(".data"):
            try:
                df_part = pd.read_csv(
                    os.path.join(data_dir, file),
                    names=columns,
                    sep=",",
                    na_values="?",
                    encoding="latin1",
                    on_bad_lines="skip"
                )
                df_part["source"] = file
                dfs.append(df_part)
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}")
    
    if not dfs:
        raise ValueError("No data files found!")
    
    df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(df)} rows from {len(dfs)} files")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess the dataframe"""
    # Replace '?' with NaN
    df = df.copy()
    df.replace("?", pd.NA, inplace=True)
    
    # Convert columns to numeric
    for col in df.columns:
        if col != "source":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Fill missing values with median
    df.fillna(df.median(numeric_only=True), inplace=True)
    
    # Encode target variable (0 = No disease, 1-4 = Disease)
    if "target" in df.columns:
        df["target"] = df["target"].apply(lambda x: 1 if x > 0 else 0)
    
    print(f"Cleaned data: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def prepare_features(df: pd.DataFrame) -> tuple:
    """Prepare features and target for modeling"""
    X = df.drop(columns=["target", "source"])
    y = df["target"]
    return X, y


def split_data(X, y, test_size: float = 0.2, random_state: int = 42):
    """Split data into train and test sets"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    """Scale features using StandardScaler"""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("Features scaled using StandardScaler")
    return scaler, X_train_scaled, X_test_scaled


def preprocess_pipeline(zip_path: str, data_dir: str) -> tuple:
    """
    Complete preprocessing pipeline
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler, X_train_scaled, X_test_scaled)
    """
    # Extract data
    if os.path.exists(zip_path):
        extract_data(zip_path, data_dir)
    
    # Load data
    df = load_data(data_dir)
    
    # Clean data
    df = clean_data(df)
    
    # Prepare features
    X, y = prepare_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Scale features
    scaler, X_train_scaled, X_test_scaled = scale_features(X_train, X_test)
    
    return X_train, X_test, y_train, y_test, scaler, X_train_scaled, X_test_scaled

