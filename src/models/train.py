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
    recall_score, roc_auc_score
)
from sklearn.model_selection import cross_val_score

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


def log_to_mlflow(model, metrics, model_name: str, params: dict, X_train, y_train, artifact_root: str, scaled: bool = False):
    """Log model to MLflow"""
    try:
        print(f"  Logging {model_name} to MLflow...")
        # Create or get experiment with explicit artifact location
        try:
            experiment = mlflow.get_experiment_by_name("Heart_Disease_Prediction")
            if experiment is None:
                # Create new experiment with correct artifact location
                print(f"  Creating new experiment with artifact location: {artifact_root}")
                experiment_id = mlflow.create_experiment(
                    "Heart_Disease_Prediction",
                    artifact_location=artifact_root
                )
            else:
                experiment_id = experiment.experiment_id
                print(f"  Using existing experiment (ID: {experiment_id})")
        except Exception as e:
            # If experiment exists but has issues, try to set it
            print(f"  Warning: Could not get experiment, trying to set it: {e}")
            mlflow.set_experiment("Heart_Disease_Prediction")
            experiment_id = mlflow.get_experiment_by_name("Heart_Disease_Prediction").experiment_id
        
        mlflow.set_experiment("Heart_Disease_Prediction")
        
        with mlflow.start_run(run_name=model_name, experiment_id=experiment_id) as run:
            run_id = run.info.run_id
            print(f"    Run ID: {run_id}")
            
            # Log parameters
            print(f"    Logging parameters:")
            for key, value in params.items():
                mlflow.log_param(key, value)
                print(f"      - {key}: {value}")
            
            # Log metrics
            print(f"    Logging metrics:")
            mlflow.log_metric("test_accuracy", metrics['accuracy'])
            print(f"      - test_accuracy: {metrics['accuracy']:.4f}")
            mlflow.log_metric("test_precision", metrics['precision'])
            print(f"      - test_precision: {metrics['precision']:.4f}")
            mlflow.log_metric("test_recall", metrics['recall'])
            print(f"      - test_recall: {metrics['recall']:.4f}")
            mlflow.log_metric("test_roc_auc", metrics['roc_auc'])
            print(f"      - test_roc_auc: {metrics['roc_auc']:.4f}")
            
            # Cross-validation
            print(f"    Running 5-fold cross-validation...")
            if scaled:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            mlflow.log_metric("cv_accuracy_mean", cv_mean)
            mlflow.log_metric("cv_accuracy_std", cv_std)
            print(f"      - CV Accuracy: {cv_mean:.4f} (+/- {cv_std:.4f})")
            print(f"      - CV Scores: {[f'{s:.4f}' for s in cv_scores]}")
            
            # Log model (using 'name' parameter instead of deprecated 'artifact_path')
            print(f"    Saving model artifact...")
            mlflow.sklearn.log_model(model, name="model")
            artifact_uri = run.info.artifact_uri
            print(f"    Model artifact URI: {artifact_uri}")
            print(f"  Successfully logged {model_name} to MLflow (Run ID: {run_id})")
    except Exception as e:
        print(f"  Error logging {model_name} to MLflow: {e}")
        import traceback
        traceback.print_exc()
        raise


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
    MLFLOW_DB = os.path.join(BASE_DIR, "mlflow.db")
    MLFLOW_ARTIFACTS_DIR = os.path.join(BASE_DIR, "mlruns")
    
    # Set MLflow tracking URI to SQLite database (recommended over filesystem)
    # SQLite stores metadata (parameters, metrics), artifacts stored separately in mlruns/
    mlflow.set_tracking_uri(f"sqlite:///{os.path.abspath(MLFLOW_DB)}")
    
    # Ensure artifact directory exists
    os.makedirs(MLFLOW_ARTIFACTS_DIR, exist_ok=True)
    
    # Convert artifact directory to file:// URI format (absolute path)
    artifact_uri = f"file://{os.path.abspath(MLFLOW_ARTIFACTS_DIR)}"
    
    # If database exists, check if artifact location matches current project directory
    # This handles cases where paths differ across OS, users, or project locations
    if os.path.exists(MLFLOW_DB):
        try:
            # Try to get the experiment to check if it's valid
            experiment = mlflow.get_experiment_by_name("Heart_Disease_Prediction")
            if experiment and experiment.artifact_location:
                artifact_loc = experiment.artifact_location
                # Normalize paths for comparison (handle file:// URI and different OS separators)
                expected_artifact_path = os.path.abspath(MLFLOW_ARTIFACTS_DIR)
                # Remove file:// prefix if present and normalize
                artifact_path_clean = artifact_loc.replace("file://", "").replace("\\", "/")
                expected_path_clean = expected_artifact_path.replace("\\", "/")
                
                # Check if artifact location matches current project's mlruns directory
                # If it doesn't match, the database was created on a different machine/OS/user
                if artifact_path_clean != expected_path_clean:
                    print(f"Warning: Artifact location mismatch detected:")
                    print(f"  Stored: {artifact_loc}")
                    print(f"  Expected: file://{expected_artifact_path}")
                    print("Deleting database to recreate with correct artifact location...")
                    os.remove(MLFLOW_DB)
                    # Also remove any associated SQLite files
                    for suffix in ["-shm", "-wal"]:
                        db_file = MLFLOW_DB + suffix
                        if os.path.exists(db_file):
                            os.remove(db_file)
        except Exception as e:
            # If we can't access the experiment, delete the database
            print(f"Warning: Could not access experiment, deleting database: {e}")
            if os.path.exists(MLFLOW_DB):
                os.remove(MLFLOW_DB)
                for suffix in ["-shm", "-wal"]:
                    db_file = MLFLOW_DB + suffix
                    if os.path.exists(db_file):
                        os.remove(db_file)
    
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
    # Convert artifact directory to file:// URI format
    artifact_uri = f"file://{os.path.abspath(MLFLOW_ARTIFACTS_DIR)}"
    log_to_mlflow(
        lr_model, lr_metrics, "LogisticRegression",
        {"model": "LogisticRegression", "max_iter": 1000, "scaler": "StandardScaler"},
        X_train_scaled, y_train, artifact_root=artifact_uri, scaled=True
    )
    
    log_to_mlflow(
        rf_model, rf_metrics, "RandomForest",
        {"model": "RandomForest", "n_estimators": 200, "random_state": 42},
        X_train, y_train, artifact_root=artifact_uri, scaled=False
    )
    
    # Save models
    save_models(lr_model, rf_model, scaler, MODEL_DIR, best_accuracy_model)
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()

