"""
Unit tests for data preprocessing pipeline
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestDataPreprocessing:
    """Test data preprocessing functions"""

    def test_missing_value_handling(self):
        """Test that missing values are handled correctly"""
        # Create test data with missing values
        data = {
            "age": [63, 67, None, 37, 41],
            "sex": [1, 1, 0, 1, 0],
            "target": [1, 1, 0, 0, 1],
        }
        df = pd.DataFrame(data)

        # Replace None with NaN
        df.replace("?", pd.NA, inplace=True)

        # Convert to numeric
        for col in df.columns:
            if col != "target":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Fill missing values with median
        df.fillna(df.median(numeric_only=True), inplace=True)

        # Assert no missing values remain
        assert df.isna().sum().sum() == 0, "Missing values should be filled"

    def test_target_encoding(self):
        """Test target variable encoding"""
        # Create test data with target values > 0
        data = {"target": [0, 1, 2, 3, 4, 0]}
        df = pd.DataFrame(data)

        # Apply target encoding (0 = No disease, 1-4 = Disease)
        df["target"] = df["target"].apply(lambda x: 1 if x > 0 else 0)

        # Assert all values are binary
        assert set(df["target"].unique()).issubset({0, 1}), "Target should be binary"
        assert df["target"].dtype in [int, np.int64], "Target should be integer type"

    def test_data_types(self):
        """Test that data types are correct after preprocessing"""
        data = {"age": ["63", "67", "37"], "sex": ["1", "1", "0"], "target": [1, 1, 0]}
        df = pd.DataFrame(data)

        # Convert to numeric
        for col in df.columns:
            if col != "target":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Assert numeric columns are numeric
        assert pd.api.types.is_numeric_dtype(df["age"]), "Age should be numeric"
        assert pd.api.types.is_numeric_dtype(df["sex"]), "Sex should be numeric"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
