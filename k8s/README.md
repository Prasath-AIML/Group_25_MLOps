# Kubernetes Deployment Guide

**This is the main documentation for Kubernetes deployment of the Heart Disease Prediction API.**

This directory contains all Kubernetes manifests and deployment instructions for deploying the API to Kubernetes (Minikube, Docker Desktop, or cloud providers).

## Directory Structure

```
k8s/
├── deployment.yaml          # API deployment manifest
├── service.yaml             # Service manifest (NodePort/LoadBalancer)
├── ingress.yaml             # Ingress manifest (optional, for ingress controller)
├── monitoring/              # Prometheus & Grafana setup
│   └── README.md            # Monitoring setup instructions
└── README.md                # This file
```

## Prerequisites

- Docker installed and running
- Kubernetes cluster (choose one):
  - Docker Desktop with Kubernetes enabled
  - Minikube
  - Cloud provider (GKE, EKS, AKS)
- kubectl configured and connected to your cluster
- Docker image built: `heart-disease-api`

## Kubernetes Setup Options

### Windows: Setup Options

#### Option 1: Docker Desktop Kubernetes (Recommended for Windows)

1. Open Docker Desktop
2. Go to **Settings → Kubernetes**
3. Check **"Enable Kubernetes"**
4. Click **"Apply & Restart"**
5. Wait for Kubernetes to start (green indicator)

**Install kubectl** (if not included):
- kubectl is usually included with Docker Desktop
- Verify: `kubectl version --client`

#### Option 2: Minikube for Windows

1. Download Minikube installer: https://minikube.sigs.k8s.io/docs/start/
2. Run the installer (`.exe` file)
3. Open **PowerShell as Administrator**:
   ```powershell
   minikube start --driver=docker
   ```

**Verify Minikube**:
```cmd
minikube status
kubectl get nodes
```

### macOS: Setup Options

#### Option 1: Docker Desktop Kubernetes

1. Open Docker Desktop
2. Go to **Settings → Kubernetes**
3. Check **"Enable Kubernetes"**
4. Click **"Apply & Restart"**
5. Wait for Kubernetes to start

#### Option 2: Minikube for macOS

**Using Homebrew**:
```bash
brew install minikube
minikube start --driver=docker
```

**Or download directly**:
1. Download from: https://minikube.sigs.k8s.io/docs/start/
2. Install the `.pkg` file
3. Open Terminal:
   ```bash
   minikube start --driver=docker
   ```

**Install kubectl** (if not included):
```bash
brew install kubectl
# or
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

**Verify Minikube**:
```bash
minikube status
kubectl get nodes
```

### Linux: Setup Options

#### Minikube for Linux

**Ubuntu/Debian**:
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start --driver=docker
```

**Install kubectl**:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

**Verify Minikube**:
```bash
minikube status
kubectl get nodes
```

## Deployment Steps

### Step 1: Build Docker Image

**From project root directory**:

**Windows (Docker Desktop Kubernetes)**:
```cmd
docker build -t heart-disease-api .
```

**Windows (Minikube)**:
```cmd
# Set Docker environment for Minikube
minikube docker-env | Invoke-Expression

# Build image (this builds in Minikube's Docker daemon)
docker build -t heart-disease-api .
```

**macOS/Linux (Docker Desktop Kubernetes)**:
```bash
docker build -t heart-disease-api .
```

**macOS/Linux (Minikube)**:
```bash
# Set Docker environment for Minikube
eval $(minikube docker-env)

# Build image (this builds in Minikube's Docker daemon)
docker build -t heart-disease-api .
```

**Verify image**:
```bash
docker images | grep heart-disease-api
```

### Step 2: Deploy to Kubernetes

**Windows**:
```cmd
# From project root
kubectl apply -f k8s\deployment.yaml
kubectl apply -f k8s\service.yaml

# Optional: Deploy ingress (if you have ingress controller)
kubectl apply -f k8s\ingress.yaml
```

**macOS/Linux**:
```bash
# From project root
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Optional: Deploy ingress (if you have ingress controller)
kubectl apply -f k8s/ingress.yaml
```

### Step 3: Verify Deployment

```bash
# Check pods are running
kubectl get pods -l app=heart-disease

# Check service
kubectl get svc heart-disease-service

# Check deployment status
kubectl get deployment heart-disease-deployment

# View detailed pod information
kubectl describe pod -l app=heart-disease
```

**Expected Output**:
```
NAME                                       READY   STATUS    RESTARTS   AGE
heart-disease-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
heart-disease-deployment-xxxxxxxxxx-yyyyy   1/1     Running   0          30s

NAME                      TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
heart-disease-service     NodePort   10.xx.xx.xx   <none>        80:30007/TCP   30s
```

### Step 4: Access the API

#### Option A: Using NodePort (Default)

**Windows (Docker Desktop Kubernetes)**:
- Health: http://localhost:30007/
- Predict: http://localhost:30007/predict
- Metrics: http://localhost:30007/metrics

**Windows (Minikube)**:
```cmd
# Get service URL
minikube service heart-disease-service --url

# Or access directly
# Health: http://<minikube-ip>:30007/
```

**macOS/Linux (Docker Desktop Kubernetes)**:
- Health: http://localhost:30007/
- Predict: http://localhost:30007/predict
- Metrics: http://localhost:30007/metrics

**macOS/Linux (Minikube)**:
```bash
# Get service URL
minikube service heart-disease-service --url

# Or get Minikube IP
minikube ip
# Then access: http://<minikube-ip>:30007/
```

#### Option B: Using Port Forward

```bash
# Port-forward to service
kubectl port-forward svc/heart-disease-service 8000:80

# Access via:
# http://localhost:8000/
# http://localhost:8000/predict
# http://localhost:8000/metrics
```

#### Option C: Using Ingress (If Ingress Controller Installed)

1. **Install Ingress Controller** (if not already installed):

   **Minikube**:
   ```bash
   minikube addons enable ingress
   ```

   **Docker Desktop**: Usually pre-installed

2. **Apply Ingress**:
   ```bash
   kubectl apply -f ingress.yaml
   ```

3. **Access via Ingress**:
   - Add to `/etc/hosts` (or `C:\Windows\System32\drivers\etc\hosts`):
     ```
     <ingress-ip> heart-disease.local
     ```
   - Access: http://heart-disease.local/

### Step 5: Test the API

**Health Check**:
```bash
curl http://localhost:30007/
# Or if using port-forward
curl http://localhost:8000/
```

**Make a Prediction**:

**Windows (PowerShell)**:
```powershell
Invoke-RestMethod -Uri "http://localhost:30007/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body (@{
      features = @(63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0)
  } | ConvertTo-Json)
```

**macOS/Linux**:
```bash
curl -X POST "http://localhost:30007/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]
  }'
```

**Check Metrics**:
```bash
curl http://localhost:30007/metrics
```

## Viewing Logs

**Windows**:
```cmd
# Get pod name
kubectl get pods -l app=heart-disease

# View logs
kubectl logs <pod-name>

# Follow logs (live)
kubectl logs -f <pod-name>

# View logs from all pods
kubectl logs -l app=heart-disease
```

**macOS/Linux**:
```bash
# Get pod name
kubectl get pods -l app=heart-disease

# View logs
kubectl logs <pod-name>

# Follow logs (live)
kubectl logs -f <pod-name>

# View logs from all pods
kubectl logs -l app=heart-disease
```

## Scaling the Deployment

**Scale up** (increase replicas):
```bash
kubectl scale deployment heart-disease-deployment --replicas=3
```

**Scale down** (decrease replicas):
```bash
kubectl scale deployment heart-disease-deployment --replicas=1
```

**Check current replicas**:
```bash
kubectl get deployment heart-disease-deployment
```

## Updating the Deployment

### Update Docker Image

1. **Build new image**:
   ```bash
   docker build -t heart-disease-api:v2 .
   ```

2. **Update deployment**:
   ```bash
   kubectl set image deployment/heart-disease-deployment \
     heart-disease-container=heart-disease-api:v2
   ```

3. **Rollout status**:
   ```bash
   kubectl rollout status deployment/heart-disease-deployment
   ```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/heart-disease-deployment

# Rollback to previous version
kubectl rollout undo deployment/heart-disease-deployment

# Rollback to specific revision
kubectl rollout undo deployment/heart-disease-deployment --to-revision=2
```

## Monitoring Setup

For Prometheus and Grafana monitoring setup, see **[monitoring/README.md](monitoring/README.md)**.

## Troubleshooting

### Pods Not Starting

**Check pod status**:
```bash
kubectl get pods -l app=heart-disease
kubectl describe pod <pod-name>
```

**Common issues**:
- **ImagePullBackOff**: Image not found
  - Solution: Ensure image is built and available
  - For Minikube: Build image in Minikube's Docker daemon
  - Check: `docker images | grep heart-disease-api`

- **CrashLoopBackOff**: Container keeps crashing
  - Check logs: `kubectl logs <pod-name>`
  - Verify model files exist in image
  - Check resource limits

- **Pending**: Pod can't be scheduled
  - Check node resources: `kubectl describe nodes`
  - Check resource requests/limits in deployment.yaml

### Service Not Accessible

**Check service**:
```bash
kubectl get svc heart-disease-service
kubectl describe svc heart-disease-service
```

**Verify endpoints**:
```bash
kubectl get endpoints heart-disease-service
```

**Test connectivity**:
```bash
# From within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://heart-disease-service:80/
```

### Port Already in Use

If NodePort 30007 is already in use:

1. **Check what's using the port**:
   
   **Windows**:
   ```cmd
   netstat -ano | findstr :30007
   ```

   **macOS/Linux**:
   ```bash
   lsof -i :30007
   ```

2. **Change NodePort**:
   - Edit `service.yaml`
   - Change `nodePort: 30007` to an available port (30000-32767)
   - Apply: `kubectl apply -f service.yaml`

### Image Pull Errors

**For Minikube**:
```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)  # macOS/Linux
minikube docker-env | Invoke-Expression  # Windows PowerShell

# Rebuild image
docker build -t heart-disease-api .
```

**For Docker Desktop**:
- Ensure Docker Desktop is running
- Build image normally: `docker build -t heart-disease-api .`

### Resource Limits Issues

If pods are being killed due to resource limits:

1. **Check current resource usage**:
   ```bash
   kubectl top pods -l app=heart-disease
   ```

2. **Adjust limits in deployment.yaml**:
   ```yaml
   resources:
     requests:
       memory: "512Mi"  # Increase if needed
       cpu: "500m"
     limits:
       memory: "1Gi"     # Increase if needed
       cpu: "1000m"
   ```

3. **Apply changes**:
   ```bash
   kubectl apply -f deployment.yaml
   ```

## Cleanup

### Remove Deployment

```bash
# Delete all resources
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/ingress.yaml  # If deployed

# Or delete by label
kubectl delete all -l app=heart-disease
```

### Stop Minikube

```bash
minikube stop
# Or completely remove
minikube delete
```

## Cloud Deployment

### Google Cloud (GKE)

1. **Create cluster**:
   ```bash
   gcloud container clusters create heart-disease-cluster \
     --num-nodes=3 \
     --zone=us-central1-a
   ```

2. **Get credentials**:
   ```bash
   gcloud container clusters get-credentials heart-disease-cluster \
     --zone=us-central1-a
   ```

3. **Push image to GCR**:
   ```bash
   docker tag heart-disease-api gcr.io/PROJECT_ID/heart-disease-api
   docker push gcr.io/PROJECT_ID/heart-disease-api
   ```

4. **Update deployment.yaml**:
   - Change `imagePullPolicy: Never` to `imagePullPolicy: Always`
   - Change `image: heart-disease-api` to `image: gcr.io/PROJECT_ID/heart-disease-api`

5. **Update service.yaml**:
   - Change `type: NodePort` to `type: LoadBalancer`
   - Remove `nodePort: 30007` line

6. **Deploy**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

### AWS (EKS)

1. **Create cluster** (using eksctl):
   ```bash
   eksctl create cluster --name heart-disease-cluster --nodes=3
   ```

2. **Push image to ECR**:
   ```bash
   aws ecr create-repository --repository-name heart-disease-api
   docker tag heart-disease-api:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/heart-disease-api:latest
   docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/heart-disease-api:latest
   ```

3. **Update manifests** (similar to GKE steps above)

### Azure (AKS)

1. **Create cluster**:
   ```bash
   az aks create --resource-group myResourceGroup --name heart-disease-cluster --node-count 3
   ```

2. **Get credentials**:
   ```bash
   az aks get-credentials --resource-group myResourceGroup --name heart-disease-cluster
   ```

3. **Push image to ACR**:
   ```bash
   az acr create --resource-group myResourceGroup --name myregistry --sku Basic
   az acr login --name myregistry
   docker tag heart-disease-api myregistry.azurecr.io/heart-disease-api:latest
   docker push myregistry.azurecr.io/heart-disease-api:latest
   ```

4. **Update manifests** (similar to GKE steps above)

## Manifest Files Reference

### deployment.yaml

- **Replicas**: 2 (can be scaled)
- **Resource Limits**: 512Mi memory, 500m CPU
- **Health Checks**: Liveness and readiness probes
- **Prometheus Annotations**: Auto-discovery enabled

### service.yaml

- **Type**: NodePort (default: 30007)
- **For Cloud**: Change to LoadBalancer
- **Port Mapping**: 80 → 8000 (container)

### ingress.yaml

- **Class**: nginx
- **Host**: heart-disease.local
- **Requires**: Ingress controller installed

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

