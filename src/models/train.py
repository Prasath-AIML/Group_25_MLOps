"""
Model training script with MLflow integration
"""
import os
import sys
import numpy as np
import joblib
import mlflow
import mlflow.sklearn

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, precision_score,
    recall_score, roc_auc_score, cross_val_score
)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.data_processing.preprocess import preprocess_pipeline


def train_models(X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled):
    """Train both Logistic Regression and Random Forest models"""
    print("\n=== Training Models ===")
    
    # Train Logistic Regression
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    
    # Train Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
    rf_model.fit(X_train, y_train)
    
    return lr_model, rf_model


def evaluate_model(model, X_test, y_test, model_name: str, scaled: bool = False):
    """Evaluate model and return metrics"""
    if scaled:
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    else:
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # ROC-AUC (only if both classes present)
    if len(np.unique(y_test)) > 1:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
    else:
        roc_auc = 0.0
    
    print(f"\n=== {model_name} Metrics ===")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")
    print(classification_report(y_test, y_pred))
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'roc_auc': roc_auc,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }


def log_to_mlflow(model, metrics, model_name: str, params: dict, X_train, y_train, scaled: bool = False):
    """Log model to MLflow"""
    mlflow.set_experiment("Heart_Disease_Prediction")
    
    with mlflow.start_run(run_name=model_name):
        # Log parameters
        for key, value in params.items():
            mlflow.log_param(key, value)
        
        # Log metrics
        mlflow.log_metric("test_accuracy", metrics['accuracy'])
        mlflow.log_metric("test_precision", metrics['precision'])
        mlflow.log_metric("test_recall", metrics['recall'])
        mlflow.log_metric("test_roc_auc", metrics['roc_auc'])
        
        # Cross-validation
        if scaled:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        else:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        
        mlflow.log_metric("cv_accuracy_mean", cv_scores.mean())
        mlflow.log_metric("cv_accuracy_std", cv_scores.std())
        
        # Log model
        mlflow.sklearn.log_model(model, "model")


def save_models(lr_model, rf_model, scaler, model_dir: str, best_model_name: str):
    """Save models to disk"""
    os.makedirs(model_dir, exist_ok=True)
    
    # Save best model as model.pkl
    if best_model_name == "RandomForest":
        joblib.dump(rf_model, os.path.join(model_dir, "model.pkl"))
    else:
        joblib.dump(lr_model, os.path.join(model_dir, "model.pkl"))
    
    # Save scaler
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
    
    # Save both models separately
    joblib.dump(lr_model, os.path.join(model_dir, "logistic_regression.pkl"))
    joblib.dump(rf_model, os.path.join(model_dir, "random_forest.pkl"))
    
    print(f"\nModels saved to {model_dir}")


def main():
    """Main training function"""
    # Setup paths
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '../..')))
    ZIP_PATH = os.path.join(BASE_DIR, "heart_disease_dataset.zip")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
    
    print("Starting model training pipeline...")
    
    # Preprocess data
    X_train, X_test, y_train, y_test, scaler, X_train_scaled, X_test_scaled = preprocess_pipeline(
        ZIP_PATH, DATA_DIR
    )
    
    # Train models
    lr_model, rf_model = train_models(X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled)
    
    # Evaluate models
    lr_metrics = evaluate_model(lr_model, X_test_scaled, y_test, "Logistic Regression", scaled=True)
    rf_metrics = evaluate_model(rf_model, X_test, y_test, "Random Forest", scaled=False)
    
    # Model comparison
    print("\n=== Model Comparison ===")
    best_accuracy_model = "Random Forest" if rf_metrics['accuracy'] > lr_metrics['accuracy'] else "Logistic Regression"
    best_roc_auc_model = "Random Forest" if rf_metrics['roc_auc'] > lr_metrics['roc_auc'] else "Logistic Regression"
    print(f"Best Accuracy: {best_accuracy_model}")
    print(f"Best ROC-AUC: {best_roc_auc_model}")
    
    # Log to MLflow
    print("\n=== Logging to MLflow ===")
    log_to_mlflow(
        lr_model, lr_metrics, "LogisticRegression",
        {"model": "LogisticRegression", "max_iter": 1000, "scaler": "StandardScaler"},
        X_train_scaled, y_train, scaled=True
    )
    
    log_to_mlflow(
        rf_model, rf_metrics, "RandomForest",
        {"model": "RandomForest", "n_estimators": 200, "random_state": 42},
        X_train, y_train, scaled=False
    )
    
    # Save models
    save_models(lr_model, rf_model, scaler, MODEL_DIR, best_accuracy_model)
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()

