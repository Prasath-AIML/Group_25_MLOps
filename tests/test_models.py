"""
Unit tests for model training and evaluation
"""

import pytest
import numpy as np
import joblib
import os
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestModelTraining:
    """Test model training functionality"""

    def test_logistic_regression_training(self):
        """Test Logistic Regression model can be trained"""
        # Create dummy data
        X = np.random.rand(100, 13)
        y = np.random.randint(0, 2, 100)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(max_iter=1000)
        model.fit(X_scaled, y)

        # Assert model is trained
        assert hasattr(model, "coef_"), "Model should have coefficients"
        predictions = model.predict(X_scaled)
        assert len(predictions) == len(y), "Predictions should match input length"

    def test_random_forest_training(self):
        """Test Random Forest model can be trained"""
        # Create dummy data
        X = np.random.rand(100, 13)
        y = np.random.randint(0, 2, 100)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        # Assert model is trained
        assert hasattr(model, "estimators_"), "Model should have estimators"
        predictions = model.predict(X)
        assert len(predictions) == len(y), "Predictions should match input length"

    def test_model_prediction_shape(self):
        """Test model predictions have correct shape"""
        X = np.random.rand(50, 13)
        y = np.random.randint(0, 2, 50)

        model = LogisticRegression(max_iter=1000)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model.fit(X_scaled, y)

        predictions = model.predict(X_scaled)
        assert predictions.shape == (50,), "Predictions should be 1D array"
        assert all(p in [0, 1] for p in predictions), "Predictions should be binary"

    def test_model_probability_prediction(self):
        """Test model can predict probabilities"""
        X = np.random.rand(50, 13)
        y = np.random.randint(0, 2, 50)

        model = LogisticRegression(max_iter=1000)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model.fit(X_scaled, y)

        probabilities = model.predict_proba(X_scaled)
        assert probabilities.shape == (
            50,
            2,
        ), "Probabilities should be (n_samples, n_classes)"
        assert np.allclose(
            probabilities.sum(axis=1), 1.0
        ), "Probabilities should sum to 1"


class TestModelEvaluation:
    """Test model evaluation metrics"""

    def test_accuracy_calculation(self):
        """Test accuracy metric calculation"""
        y_true = np.array([0, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 1, 0])

        accuracy = accuracy_score(y_true, y_pred)
        assert accuracy == 1.0, "Perfect predictions should have accuracy 1.0"

    def test_precision_calculation(self):
        """Test precision metric calculation"""
        y_true = np.array([1, 1, 0, 1, 0])
        y_pred = np.array([1, 1, 1, 1, 0])

        precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        assert 0 <= precision <= 1, "Precision should be between 0 and 1"

    def test_recall_calculation(self):
        """Test recall metric calculation"""
        y_true = np.array([1, 1, 0, 1, 0])
        y_pred = np.array([1, 1, 1, 1, 0])

        recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        assert 0 <= recall <= 1, "Recall should be between 0 and 1"

    def test_roc_auc_calculation(self):
        """Test ROC-AUC metric calculation"""
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_scores = np.array([0.1, 0.9, 0.2, 0.8, 0.3, 0.7])

        if len(np.unique(y_true)) > 1:
            roc_auc = roc_auc_score(y_true, y_scores)
            assert 0 <= roc_auc <= 1, "ROC-AUC should be between 0 and 1"


class TestModelPersistence:
    """Test model saving and loading"""

    def test_model_saving(self, tmp_path):
        """Test model can be saved"""
        X = np.random.rand(50, 13)
        y = np.random.randint(0, 2, 50)

        model = LogisticRegression(max_iter=1000)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model.fit(X_scaled, y)

        # Save model
        model_path = tmp_path / "test_model.pkl"
        joblib.dump(model, model_path)

        assert model_path.exists(), "Model file should be created"

    def test_model_loading(self, tmp_path):
        """Test model can be loaded"""
        X = np.random.rand(50, 13)
        y = np.random.randint(0, 2, 50)

        model = LogisticRegression(max_iter=1000)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model.fit(X_scaled, y)

        # Save and load
        model_path = tmp_path / "test_model.pkl"
        joblib.dump(model, model_path)
        loaded_model = joblib.load(model_path)

        # Test loaded model
        predictions_original = model.predict(X_scaled)
        predictions_loaded = loaded_model.predict(X_scaled)

        assert np.array_equal(
            predictions_original, predictions_loaded
        ), "Loaded model should produce same predictions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
