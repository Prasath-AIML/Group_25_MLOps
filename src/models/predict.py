"""
Inference script for making predictions with trained models
"""
import os
import sys
import joblib
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def load_model(model_path: str = None):
    """Load trained model and scaler"""
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '../..')))
    MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
    
    if model_path is None:
        model_path = os.path.join(MODEL_DIR, "model.pkl")
    
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    return model, scaler


def predict(features: list, model=None, scaler=None):
    """
    Make prediction on input features
    
    Args:
        features: List of 13 feature values
        model: Trained model (if None, loads from saved_models/)
        scaler: Trained scaler (if None, loads from saved_models/)
    
    Returns:
        dict: Prediction results with probabilities
    """
    if model is None or scaler is None:
        model, scaler = load_model()
    
    # Prepare data
    data = np.array(features).reshape(1, -1)
    data_scaled = scaler.transform(data)
    
    # Make prediction
    prediction = model.predict(data_scaled)[0]
    prediction_proba = model.predict_proba(data_scaled)[0]
    confidence = float(max(prediction_proba))
    
    return {
        "prediction": int(prediction),
        "confidence": round(confidence, 4),
        "probabilities": {
            "class_0": round(float(prediction_proba[0]), 4),
            "class_1": round(float(prediction_proba[1]), 4)
        }
    }


def main():
    """Example usage"""
    # Example features (13 features for heart disease dataset)
    # age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    example_features = [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
    
    print("Making prediction with example features...")
    result = predict(example_features)
    
    print(f"\nPrediction: {result['prediction']} ({'Heart Disease' if result['prediction'] == 1 else 'No Heart Disease'})")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Probabilities: {result['probabilities']}")


if __name__ == "__main__":
    main()

