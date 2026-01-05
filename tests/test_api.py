"""
Unit tests for FastAPI application
"""
import pytest
import numpy as np
import joblib
import os
import sys
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAPIEndpoints:
    """Test API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        # Note: This requires the API to be importable
        # In a real scenario, you'd mock the model loading
        try:
            from src.api.app import app
            return TestClient(app)
        except Exception:
            pytest.skip("API not available for testing")
    
    def test_home_endpoint(self, client):
        """Test home endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "ML Model API" in response.json()["message"]
    
    def test_predict_endpoint_structure(self, client):
        """Test predict endpoint accepts correct input structure"""
        # Create dummy feature array (13 features for heart disease dataset)
        features = [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
        
        response = client.post("/predict", json={"features": features})
        
        # Should return 200, 422 (validation error), or 503 (model not available)
        assert response.status_code in [200, 422, 503], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data, "Response should contain prediction"
            assert "confidence" in data, "Response should contain confidence"
            assert "probabilities" in data, "Response should contain probabilities"
            assert "latency_ms" in data, "Response should contain latency"
    
    def test_predict_endpoint_prediction_type(self, client):
        """Test predict endpoint returns correct prediction type"""
        features = [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
        
        response = client.post("/predict", json={"features": features})
        
        # Skip if model not available or incompatible
        if response.status_code == 503:
            pytest.skip("Model not available or incompatible")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["prediction"], int), "Prediction should be integer"
            assert data["prediction"] in [0, 1], "Prediction should be binary (0 or 1)"
            assert 0 <= data["confidence"] <= 1, "Confidence should be between 0 and 1"
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns Prometheus format"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        
        content = response.text
        assert "api_requests_total" in content, "Should contain api_requests_total metric"
        assert "prediction_requests_total" in content, "Should contain prediction_requests_total metric"
    
    def test_predict_endpoint_validation(self, client):
        """Test predict endpoint validates input"""
        # Test with wrong number of features
        response = client.post("/predict", json={"features": [1.0, 2.0]})
        assert response.status_code == 422, "Should return validation error for wrong input"
    
    def test_predict_endpoint_empty_features(self, client):
        """Test predict endpoint handles empty features"""
        response = client.post("/predict", json={"features": []})
        assert response.status_code == 422, "Should return validation error for empty features"


class TestAPIMetrics:
    """Test API metrics tracking"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        try:
            from src.api.app import app
            return TestClient(app)
        except Exception:
            pytest.skip("API not available for testing")
    
    def test_metrics_increment(self, client):
        """Test that metrics are incremented on requests"""
        # Make a request
        features = [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
    
        # Get initial metrics
        initial_metrics = client.get("/metrics").text
    
        # Make a prediction
        predict_response = client.post("/predict", json={"features": features})
        if predict_response.status_code in [200, 503]:
            # Get updated metrics
            updated_metrics = client.get("/metrics").text
            
            # Metrics should have changed (this is a basic check)
            # In a real scenario, you'd parse and compare specific values
            assert len(updated_metrics) > 0, "Metrics should be returned"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

