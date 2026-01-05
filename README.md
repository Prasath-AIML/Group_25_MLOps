# Heart Disease Prediction - MLOps Project

An end-to-end MLOps solution for predicting heart disease risk using machine learning. This project implements a complete ML pipeline including data preprocessing, model training, experiment tracking, API deployment, containerization, and Kubernetes deployment.

## Features

- **Machine Learning Models**: Logistic Regression and Random Forest classifiers
- **Experiment Tracking**: MLflow integration for model versioning and metrics
- **REST API**: FastAPI-based prediction service with confidence scores
- **Monitoring**: Prometheus-style metrics endpoint
- **Containerization**: Docker support for easy deployment
- **Kubernetes**: Production-ready deployment manifests
- **CI/CD**: GitHub Actions pipeline for automated testing and training
- **Testing**: Comprehensive unit test suite

## Project Structure

```
├── notebooks/
│   └── eda.ipynb                    # Exploratory Data Analysis
├── src/
│   ├── data_processing/
│   │   └── preprocess.py            # Data preprocessing pipeline
│   ├── models/
│   │   ├── train.py                 # Model training script
│   │   └── predict.py               # Inference script
│   └── api/
│       └── app.py                   # FastAPI application
├── scripts/
│   └── download_data.py             # Dataset download script
├── tests/
│   ├── test_preprocessing.py        # Data processing tests
│   ├── test_models.py               # Model tests
│   └── test_api.py                  # API tests
├── .github/workflows/
│   └── ci_cd.yml                    # CI/CD pipeline
├── k8s/
│   ├── deployment.yaml              # Kubernetes deployment
│   └── service.yaml                 # Kubernetes service
├── data/                            # Dataset files
├── saved_models/                    # Trained models
├── mlruns/                          # MLflow tracking data
├── Dockerfile                       # Docker configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Docker (for containerization)
- Kubernetes/Minikube (for deployment, optional)
  - **Kubernetes installation instructions**: See [k8s/README.md](k8s/README.md) for detailed setup guides for Windows, macOS, and Linux

## Installation

### Windows Installation

#### Step 1: Install Python

1. Download Python 3.9 or higher from: https://www.python.org/downloads/
2. During installation, **check "Add Python to PATH"**
3. Verify installation by opening **Command Prompt** or **PowerShell**:
   ```cmd
   python --version
   pip --version
   ```

#### Step 2: Install Git (if not already installed)

1. Download Git for Windows: https://git-scm.com/download/win
2. Install with default options
3. Verify installation:
   ```cmd
   git --version
   ```

#### Step 3: Clone the Repository

Open **Command Prompt** or **PowerShell**:

```cmd
git clone <repository-url>
cd Group_25_MLOps
```

#### Step 4: Create Virtual Environment

**Using Command Prompt**:
```cmd
python -m venv venv
venv\Scripts\activate
```

**Using PowerShell**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Note**: If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 5: Install Dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Verify Installation

```cmd
python -c "import fastapi, sklearn, mlflow; print('All packages installed successfully!')"
```

### macOS Installation

#### Step 1: Install Python

**Option A: Using Homebrew (Recommended)**:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9

# Verify installation
python3 --version
pip3 --version
```

**Option B: Download from Python.org**:
1. Download Python 3.9 or higher from: https://www.python.org/downloads/macos/
2. Run the installer package (`.pkg` file)
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Step 2: Install Git (if not already installed)

Git is usually pre-installed on macOS. Verify:
```bash
git --version
```

If not installed, install via Homebrew:
```bash
brew install git
```

#### Step 3: Clone the Repository

Open **Terminal**:

```bash
git clone <repository-url>
cd Group_25_MLOps
```

#### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**Note**: You should see `(venv)` in your terminal prompt after activation.

#### Step 5: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Verify Installation

```bash
python3 -c "import fastapi, sklearn, mlflow; print('All packages installed successfully!')"
```

### Linux Installation

#### Step 1: Install Python

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.9 python3-pip python3-venv
```

**CentOS/RHEL**:
```bash
sudo yum install python39 python39-pip
```

**Verify installation**:
```bash
python3 --version
pip3 --version
```

#### Step 2: Install Git

**Ubuntu/Debian**:
```bash
sudo apt install git
```

**CentOS/RHEL**:
```bash
sudo yum install git
```

#### Step 3: Clone the Repository

```bash
git clone <repository-url>
cd Group_25_MLOps
```

#### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 5: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Docker and Kubernetes (Optional)

For containerization and Kubernetes deployment:

- **Docker installation**: See the [Docker Deployment](#docker-deployment) section below
- **Kubernetes installation**: See [k8s/README.md](k8s/README.md) for complete setup instructions for:
  - Docker Desktop Kubernetes (Windows, macOS)
  - Minikube (Windows, macOS, Linux)
  - Cloud providers (GKE, EKS, AKS)

### 5. Download Dataset

The dataset should be placed in the `data/` directory. You can either:

**Option A**: Place the `heart_disease_dataset.zip` file in the project root, or

**Option B**: Run the download script:

```bash
python scripts/download_data.py
```

Then manually download the Heart Disease UCI dataset from:
https://archive.ics.uci.edu/ml/datasets/heart+Disease

Place all `.data` files in the `data/` directory.

## Running the Project

### 1. Train Models

Train both Logistic Regression and Random Forest models with MLflow tracking:

```bash
python -m src.models.train
```

This will:
- Load and preprocess the data
- Train both models
- Evaluate with comprehensive metrics (accuracy, precision, recall, ROC-AUC)
- Log experiments to MLflow
- Save models to `saved_models/`

**View MLflow UI**:
```bash
mlflow ui
```
Then open http://localhost:5000 in your browser

### 2. Run API Locally

**Windows (Command Prompt or PowerShell)**:
```cmd
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

**macOS**:
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Linux**:
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Health Check**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

### 3. Make Predictions

**Windows (PowerShell)**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body (@{
      features = @(63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0)
  } | ConvertTo-Json)
```

**Windows (Command Prompt with curl)**:
```cmd
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d "{\"features\": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]}"
```

**macOS/Linux (curl)**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
  }'
```

**macOS (using httpie - if installed)**:
```bash
http POST http://localhost:8000/predict features:='[63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]'
```

**Using Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "features": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
    }
)
print(response.json())
```

**Response Format**:
```json
{
  "prediction": 1,
  "confidence": 0.8542,
  "probabilities": {
    "class_0": 0.1458,
    "class_1": 0.8542
  },
  "latency_ms": 12.34
}
```

### 4. Run Tests

Run the complete test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

View coverage report:

**macOS**:
```bash
open htmlcov/index.html
```

**Linux**:
```bash
xdg-open htmlcov/index.html
# or
firefox htmlcov/index.html
```

**Windows**:
```cmd
start htmlcov\index.html
```

### 5. Run Inference Script

Use the standalone prediction script:

```bash
python -m src.models.predict
```

Or use it programmatically:
```python
from src.models.predict import predict

result = predict([63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0])
print(result)
```

## Docker Deployment

> **Note**: For Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md) which includes Docker Desktop Kubernetes and Minikube setup for all platforms.

### Windows: Install Docker Desktop

1. Download Docker Desktop for Windows: https://www.docker.com/products/docker-desktop/
2. Install with default options
3. Enable **WSL 2** when prompted (if using WSL)
4. Restart your computer
5. Open Docker Desktop and wait until it shows "Docker Desktop is running"

**Verify Docker Installation**:
```cmd
docker --version
docker info
```

### macOS: Install Docker Desktop

1. Download Docker Desktop for Mac: https://www.docker.com/products/docker-desktop/
2. Choose the correct version:
   - **Apple Silicon (M1/M2/M3)**: Download "Mac with Apple chip"
   - **Intel Mac**: Download "Mac with Intel chip"
3. Open the downloaded `.dmg` file
4. Drag Docker to Applications folder
5. Open Docker from Applications
6. Complete the setup wizard
7. Wait until Docker Desktop shows "Docker Desktop is running"

**Verify Docker Installation**:
```bash
docker --version
docker info
```

### Linux: Install Docker

**Ubuntu/Debian**:
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

**Verify Docker Installation**:
```bash
docker --version
docker info
```

### Build Docker Image

**Windows (Command Prompt or PowerShell)**:
```cmd
docker build -t heart-disease-api .
```

**macOS**:
```bash
docker build -t heart-disease-api .
```

**Linux**:
```bash
docker build -t heart-disease-api .
```

### Run Container

**Windows**:
```cmd
docker run -p 8000:8000 heart-disease-api
```

**macOS**:
```bash
docker run -p 8000:8000 heart-disease-api
```

**Linux**:
```bash
docker run -p 8000:8000 heart-disease-api
```

### Test Container

```bash
curl http://localhost:8000/
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]}'
```

## Kubernetes Deployment

For complete Kubernetes deployment instructions, including setup for Windows, macOS, and Linux, see **[k8s/README.md](k8s/README.md)**.

The Kubernetes deployment includes:
- Setup instructions for Docker Desktop Kubernetes and Minikube
- Step-by-step deployment guide
- Access methods (NodePort, Port Forward, Ingress)
- Scaling and update procedures
- Cloud deployment guides (GKE, EKS, AKS)
- Complete troubleshooting guide

**Quick Start**:
```bash
# Build image
docker build -t heart-disease-api .

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Access
# http://localhost:30007 (NodePort)
```

## API Endpoints

### `GET /`
Health check endpoint.

**Response**:
```json
{
  "message": "ML Model API is running",
  "status": "healthy",
  "model_loaded": true
}
```

### `POST /predict`
Make a heart disease prediction.

**Request Body**:
```json
{
  "features": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
}
```

**Response**:
```json
{
  "prediction": 1,
  "confidence": 0.8542,
  "probabilities": {
    "class_0": 0.1458,
    "class_1": 0.8542
  },
  "latency_ms": 12.34
}
```

**Feature Description** (13 features in order):
1. age - Age in years
2. sex - Sex (1 = male, 0 = female)
3. cp - Chest pain type (0-3)
4. trestbps - Resting blood pressure
5. chol - Serum cholesterol
6. fbs - Fasting blood sugar > 120 mg/dl (1 = yes, 0 = no)
7. restecg - Resting electrocardiographic results
8. thalach - Maximum heart rate achieved
9. exang - Exercise induced angina (1 = yes, 0 = no)
10. oldpeak - ST depression induced by exercise
11. slope - Slope of peak exercise ST segment
12. ca - Number of major vessels colored by flourosopy
13. thal - Thalassemia (3 = normal, 6 = fixed defect, 7 = reversable defect)

### `GET /metrics`
Prometheus-style metrics endpoint.

**Response**: Plain text with metrics including:
- `api_requests_total` - Total API requests
- `prediction_requests_total` - Total predictions
- `api_request_latency_ms` - Request latency statistics
- `predictions_by_class_total` - Predictions by class
- `errors_total` - Total errors

## CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/ci_cd.yml`) that:

1. **Linting**: Runs Black and Flake8 code quality checks
2. **Testing**: Executes unit tests with coverage reporting
3. **Training**: Trains models and uploads artifacts

The pipeline runs on:
- Push to `main` or `master` branch
- Pull requests to `main` or `master` branch

## Development

### Code Structure

- **Data Processing** (`src/data_processing/`): Data loading, cleaning, and preprocessing
- **Models** (`src/models/`): Model training, evaluation, and inference
- **API** (`src/api/`): FastAPI application and endpoints
- **Tests** (`tests/`): Unit tests for all components

### Running Linters

```bash
# Black (code formatting)
black --check src/ tests/

# Flake8 (linting)
flake8 src/ tests/
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add/update tests
4. Run tests: `pytest tests/ -v`
5. Run linters: `black src/ tests/ && flake8 src/ tests/`
6. Commit and push

## Dataset

- **Source**: UCI Machine Learning Repository
- **URL**: https://archive.ics.uci.edu/ml/datasets/heart+Disease
- **Description**: Heart disease prediction dataset with 14+ features
- **Target**: Binary classification (presence/absence of heart disease)

## Model Performance

The models are evaluated using:
- **Accuracy**: Overall prediction accuracy
- **Precision**: Weighted precision score
- **Recall**: Weighted recall score
- **ROC-AUC**: Area under ROC curve
- **Cross-Validation**: 5-fold CV accuracy

Both Logistic Regression and Random Forest models are trained and compared. The best model (based on accuracy) is saved as `saved_models/model.pkl`.

## Monitoring

The API includes:
- **Request Logging**: All requests are logged with method, path, and status
- **Metrics Endpoint**: Prometheus-style metrics for monitoring (`/metrics`)
- **Error Tracking**: Errors are logged and counted in metrics

### Prometheus & Grafana Setup

For complete Prometheus and Grafana monitoring setup with detailed instructions, see **[k8s/monitoring/README.md](k8s/monitoring/README.md)**.

The monitoring setup includes:
- Prometheus configuration and deployment
- Grafana deployment with pre-configured dashboard
- Docker Compose setup for local development
- Complete troubleshooting guide

## Troubleshooting

### Model Not Found Error

Ensure models are trained first:

**Windows**:
```cmd
python -m src.models.train
```

**macOS/Linux**:
```bash
python -m src.models.train
```

### Port Already in Use

Change the port:

**Windows**:
```cmd
uvicorn src.api.app:app --host 0.0.0.0 --port 8080
```

**macOS/Linux**:
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8080
```

### Import Errors

Ensure you're in the project root and virtual environment is activated:

**Windows**:
```cmd
cd Group_25_MLOps
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS**:
```bash
cd Group_25_MLOps
source venv/bin/activate
pip install -r requirements.txt
```

**Linux**:
```bash
cd Group_25_MLOps
source venv/bin/activate
pip install -r requirements.txt
```

### Windows-Specific Issues

#### PowerShell Execution Policy Error

If you see: `cannot be loaded because running scripts is disabled on this system`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating the virtual environment again:
```powershell
venv\Scripts\Activate.ps1
```

#### Python Not Found Error

If `python` command doesn't work:

1. Check if Python is installed:
   ```cmd
   py --version
   ```

2. If `py` works, use `py` instead of `python`:
   ```cmd
   py -m venv venv
   py -m pip install -r requirements.txt
   ```

3. Or add Python to PATH:
   - Search for "Environment Variables" in Windows
   - Edit "Path" variable
   - Add Python installation directory (e.g., `C:\Python39\`)

#### Long Path Issues

If you encounter path length errors:

1. Enable long paths in Windows:
   - Open PowerShell as Administrator
   - Run: `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`
   - Restart your computer

#### Virtual Environment Activation Issues

**Command Prompt**:
```cmd
venv\Scripts\activate.bat
```

**PowerShell**:
```powershell
venv\Scripts\Activate.ps1
```

If PowerShell script execution is blocked, use Command Prompt instead.

#### MLflow UI Not Opening

**Windows**:
1. Check if port 5000 is available:
   ```cmd
   netstat -ano | findstr :5000
   ```

2. Use a different port:
   ```cmd
   mlflow ui --port 5001
   ```

3. Access manually: Open browser and go to `http://localhost:5000`

**macOS**:
1. Check if port 5000 is available:
   ```bash
   lsof -i :5000
   ```

2. Use a different port:
   ```bash
   mlflow ui --port 5001
   ```

3. Access manually: Open browser and go to `http://localhost:5000`

**Linux**:
1. Check if port 5000 is available:
   ```bash
   netstat -tuln | grep :5000
   # or
   ss -tuln | grep :5000
   ```

2. Use a different port:
   ```bash
   mlflow ui --port 5001
   ```

3. Access manually: Open browser and go to `http://localhost:5000`

### macOS-Specific Issues

#### Python3 Command Not Found

If `python3` doesn't work, try:
```bash
# Check if Python is installed
which python3

# If not found, install via Homebrew
brew install python@3.9

# Or create an alias
alias python3=/usr/local/bin/python3
```

#### Permission Denied Errors

If you get permission errors:
```bash
# Fix pip permissions
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

#### Homebrew Installation Issues

If Homebrew installation fails:
```bash
# Install Homebrew with proper permissions
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (for Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

#### Docker Desktop Issues on Apple Silicon

If Docker Desktop doesn't work on M1/M2/M3 Macs:
1. Ensure you downloaded the Apple Silicon version
2. Check System Settings → Privacy & Security → Allow Docker
3. Restart Docker Desktop
4. Verify architecture:
   ```bash
   docker info | grep Architecture
   ```

## License

This project is part of an MLOps assignment.

## Contact

For questions or issues, please refer to the project repository.

---

## Video Demo

[Link to video demonstration will be added here]

## Deployed API URL

- **Local**: http://localhost:8000
- **Kubernetes**: [URL will be provided after deployment]
