# -*- coding: utf-8 -*-
"""
MLOps.ipynb - FIXED & PRODUCTION READY
"""

# =========================
# 0. COMMON IMPORTS
# =========================
import os
import zipfile
import numpy as np
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# =========================
# 1. ENVIRONMENT SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(BASE_DIR, "heart_disease_dataset.zip")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

IS_PRODUCTION = not os.path.exists(ZIP_PATH)

# =========================
# 2. TRAINING PIPELINE (LOCAL ONLY)
# =========================
if not IS_PRODUCTION:
    print("Running in TRAINING mode")

    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import mlflow
    import mlflow.sklearn

    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report

    # -------- DATA EXTRACTION --------
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)

    # -------- DATA LOADING --------
    columns = [
        "age", "sex", "cp", "trestbps", "chol",
        "fbs", "restecg", "thalach", "exang",
        "oldpeak", "slope", "ca", "thal", "target"
    ]

    dfs = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".data"):
            df_part = pd.read_csv(
                os.path.join(DATA_DIR, file),
                names=columns,
                sep=",",
                na_values="?",
                encoding="latin1",
                on_bad_lines="skip"
            )
            df_part["source"] = file
            dfs.append(df_part)

    df = pd.concat(dfs, ignore_index=True)

    # -------- CLEANING --------
    df.replace("?", pd.NA, inplace=True)
    for col in df.columns:
        if col != "source":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.fillna(df.median(numeric_only=True), inplace=True)
    df["target"] = df["target"].apply(lambda x: 1 if x > 0 else 0)

    # -------- TRAIN / TEST --------
    X = df.drop(columns=["target", "source"])
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # -------- MODELS --------
    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train_scaled, y_train)

    rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
    rf_model.fit(X_train, y_train)

    # -------- EVALUATION --------
    y_pred_lr = lr_model.predict(X_test_scaled)
    lr_cv = cross_val_score(lr_model, X_train_scaled, y_train, cv=5)

    # -------- MLFLOW --------
    mlflow.set_experiment("Heart_Disease_Prediction")
    with mlflow.start_run():
        mlflow.log_param("model", "LogisticRegression")
        mlflow.log_metric("test_accuracy", accuracy_score(y_test, y_pred_lr))
        mlflow.log_metric("cv_accuracy", lr_cv.mean())
        mlflow.sklearn.log_model(lr_model, "model")

    # -------- SAVE ARTIFACTS --------
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(lr_model, os.path.join(MODEL_DIR, "model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

    print("Training complete. Model & scaler saved.")

# =========================
# 3. FASTAPI (PRODUCTION + LOCAL)
# =========================
print("Running in PRODUCTION mode (serving only)")

import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True   # <-- THIS IS THE KEY
)

logger = logging.getLogger("heart-disease-api")


app = FastAPI()

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))


@app.get("/")
def home():
    return {"message": "ML Model API is running"}


class PredictionRequest(BaseModel):
    features: List[float]


@app.post("/predict")
def predict(request: PredictionRequest):
    start_time = time.time()

    logger.info("Prediction request received")
    logger.info(f"Input features count: {len(request.features)}")

    data = np.array(request.features).reshape(1, -1)
    data_scaled = scaler.transform(data)

    prediction = model.predict(data_scaled)[0]

    latency = (time.time() - start_time) * 1000
    logger.info(f"Prediction result: {int(prediction)}")
    logger.info(f"Latency: {latency:.2f} ms")

    return {
        "prediction": int(prediction),
        "latency_ms": round(latency, 2)
    }


