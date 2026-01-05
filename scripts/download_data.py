"""
Script to download Heart Disease UCI dataset
"""
import os
import urllib.request
import zipfile


def download_dataset(url: str, output_path: str):
    """Download dataset from URL"""
    print(f"Downloading dataset from {url}...")
    urllib.request.urlretrieve(url, output_path)
    print(f"Dataset downloaded to {output_path}")


def extract_dataset(zip_path: str, extract_dir: str):
    """Extract dataset from zip file"""
    print(f"Extracting dataset to {extract_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Dataset extracted to {extract_dir}")


def main():
    """Main function to download and extract dataset"""
    # Dataset information
    dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    
    # Alternative: If you have the zip file, use this:
    # dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/heart-disease.zip"
    
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    ZIP_PATH = os.path.join(BASE_DIR, "heart_disease_dataset.zip")
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("=" * 50)
    print("Heart Disease UCI Dataset Download Script")
    print("=" * 50)
    print("\nInstructions:")
    print("1. Download the dataset from: https://archive.ics.uci.edu/ml/datasets/heart+Disease")
    print("2. The dataset consists of multiple .data files")
    print("3. Place all .data files in the 'data/' directory")
    print("\nAlternatively, if you have a zip file:")
    print(f"   - Place it at: {ZIP_PATH}")
    print(f"   - Or run this script to download (if URL is available)")
    print("=" * 50)
    
    # Check if zip file already exists
    if os.path.exists(ZIP_PATH):
        print(f"\nZip file already exists at {ZIP_PATH}")
        extract_dataset(ZIP_PATH, DATA_DIR)
    else:
        print(f"\nZip file not found at {ZIP_PATH}")
        print("Please download the dataset manually and place it in the data/ directory")
        print("Or provide the zip file at the path above")


if __name__ == "__main__":
    main()

