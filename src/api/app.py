"""
FastAPI application for Heart Disease Prediction
"""

import os
import sys
import logging
import time
import numpy as np
import joblib
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, field_validator
from typing import List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

logger = logging.getLogger("heart-disease-api")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "../..")))
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

# Metrics tracking
metrics = {
    "api_requests_total": 0,
    "api_request_latency_ms": [],
    "prediction_requests_total": 0,
    "predictions_by_class": defaultdict(int),
    "errors_total": 0,
}

# Initialize FastAPI app
app = FastAPI(
    title="Heart Disease Prediction API",
    description="ML model API for predicting heart disease risk",
    version="1.0.0",
)

# Load model and scaler
model = None
scaler = None
try:
    model_path = os.path.join(MODEL_DIR, "model.pkl")
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        logger.info("Model and scaler loaded successfully")
    else:
        logger.warning(
            f"Model files not found at {MODEL_DIR}. Model will not be available."
        )
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    logger.warning("Model will not be available. Please train the model first.")
    model = None
    scaler = None


@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware to log requests and track metrics"""
    start_time = time.time()
    metrics["api_requests_total"] += 1

    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        latency = (time.time() - start_time) * 1000
        metrics["api_request_latency_ms"].append(latency)
        logger.info(
            f"Response status: {response.status_code}, Latency: {latency:.2f} ms"
        )
        return response
    except Exception as e:
        metrics["errors_total"] += 1
        logger.error(f"Error processing request: {str(e)}")
        raise


@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "message": "ML Model API is running",
        "status": "healthy",
        "model_loaded": model is not None,
    }


class PredictionRequest(BaseModel):
    """Request model for predictions"""

    features: List[float] = Field(
        ..., min_length=13, max_length=13, description="Exactly 13 features required"
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, v):
        if len(v) != 13:
            raise ValueError(f"Expected exactly 13 features, got {len(v)}")
        return v


@app.post("/predict")
def predict(request: PredictionRequest):
    """Predict heart disease risk"""
    if model is None or scaler is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please check model files."
        )

    start_time = time.time()
    metrics["prediction_requests_total"] += 1

    logger.info("Prediction request received")
    logger.info(f"Input features count: {len(request.features)}")

    try:
        # Prepare data
        data = np.array(request.features).reshape(1, -1)
        data_scaled = scaler.transform(data)

        # Get prediction and confidence scores
        prediction = model.predict(data_scaled)[0]
        prediction_proba = model.predict_proba(data_scaled)[0]
        confidence = float(max(prediction_proba))

        metrics["predictions_by_class"][int(prediction)] += 1

        latency = (time.time() - start_time) * 1000
        logger.info(
            f"Prediction result: {int(prediction)}, Confidence: {confidence:.4f}"
        )
        logger.info(f"Latency: {latency:.2f} ms")

        return {
            "prediction": int(prediction),
            "confidence": round(confidence, 4),
            "probabilities": {
                "class_0": round(float(prediction_proba[0]), 4),
                "class_1": round(float(prediction_proba[1]), 4),
            },
            "latency_ms": round(latency, 2),
        }
    except Exception as e:
        metrics["errors_total"] += 1
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/metrics")
def get_metrics():
    """Prometheus-style metrics endpoint"""
    latency_values = metrics["api_request_latency_ms"]
    avg_latency = sum(latency_values) / len(latency_values) if latency_values else 0
    max_latency = max(latency_values) if latency_values else 0

    metrics_output = f"""# HELP api_requests_total Total number of API requests
# TYPE api_requests_total counter
api_requests_total {metrics["api_requests_total"]}

# HELP prediction_requests_total Total number of prediction requests
# TYPE prediction_requests_total counter
prediction_requests_total {metrics["prediction_requests_total"]}

# HELP api_request_latency_ms Request latency in milliseconds
# TYPE api_request_latency_ms summary
api_request_latency_ms{{quantile="0.5"}} {avg_latency:.2f}
api_request_latency_ms{{quantile="0.95"}} {max_latency:.2f}
api_request_latency_ms{{quantile="0.99"}} {max_latency:.2f}
api_request_latency_ms_sum {sum(latency_values):.2f}
api_request_latency_ms_count {len(latency_values)}

# HELP predictions_by_class_total Predictions by class
# TYPE predictions_by_class_total counter
predictions_by_class_total{{class="0"}} {metrics["predictions_by_class"][0]}
predictions_by_class_total{{class="1"}} {metrics["predictions_by_class"][1]}

# HELP errors_total Total number of errors
# TYPE errors_total counter
errors_total {metrics["errors_total"]}
"""
    return Response(content=metrics_output, media_type="text/plain")
