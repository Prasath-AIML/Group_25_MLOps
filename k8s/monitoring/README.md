# Prometheus & Grafana Monitoring Setup

**This is the main documentation for Prometheus and Grafana monitoring setup.**

This directory contains Kubernetes manifests and Docker Compose configuration for setting up Prometheus and Grafana monitoring for the Heart Disease Prediction API. All setup instructions, troubleshooting, and configuration details are documented here.

## Architecture

```
Heart Disease API (/metrics endpoint)
    ↓
Prometheus (scrapes metrics every 15s)
    ↓
Grafana (visualizes metrics with dashboards)
```

## Prerequisites

### For Kubernetes Deployment

- Kubernetes cluster running (Minikube, Docker Desktop Kubernetes, or cloud)
- kubectl configured and connected to your cluster
- Heart Disease API deployed (see main README for deployment steps)

### For Docker Compose Deployment

- Docker and Docker Compose installed
- Heart Disease API running (locally or in Docker)

## Setup Instructions

### Option 1: Kubernetes Deployment (Recommended for Production)

#### Step 1: Ensure API is Deployed

First, deploy the Heart Disease API:

```bash
# From project root
kubectl apply -f ../deployment.yaml
kubectl apply -f ../service.yaml

# Verify API is running
kubectl get pods -l app=heart-disease
kubectl get svc heart-disease-service
```

#### Step 2: Deploy Prometheus

```bash
# Navigate to monitoring directory
cd k8s/monitoring

# Create Prometheus configuration
kubectl apply -f prometheus-config.yaml

# Deploy Prometheus
kubectl apply -f prometheus-deployment.yaml

# Wait for Prometheus to be ready
kubectl wait --for=condition=ready pod -l app=prometheus --timeout=60s

# Verify deployment
kubectl get pods -l app=prometheus
kubectl get svc prometheus-service
```

**Expected Output**:
```
NAME                          READY   STATUS    RESTARTS   AGE
prometheus-xxxxxxxxxx-xxxxx   1/1     Running   0          30s

NAME                  TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
prometheus-service    NodePort   10.xx.xx.xx   <none>        9090:30090/TCP   30s
```

#### Step 3: Deploy Grafana

```bash
# Deploy Grafana
kubectl apply -f grafana-deployment.yaml

# Wait for Grafana to be ready
kubectl wait --for=condition=ready pod -l app=grafana --timeout=60s

# Verify deployment
kubectl get pods -l app=grafana
kubectl get svc grafana-service
```

**Expected Output**:
```
NAME                       READY   STATUS    RESTARTS   AGE
grafana-xxxxxxxxxx-xxxxx   1/1     Running   0          25s

NAME               TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
grafana-service    NodePort   10.xx.xx.xx   <none>        3000:30300/TCP   25s
```

#### Step 4: Access Services

**Prometheus UI**:

**Windows (Docker Desktop Kubernetes)**:
- Open browser: http://localhost:30090

**Windows (Minikube)**:
```cmd
minikube service prometheus-service --url
```
Then open the URL in browser

**macOS/Linux (Docker Desktop Kubernetes)**:
- Open browser: http://localhost:30090

**macOS/Linux (Minikube)**:
```bash
minikube service prometheus-service --url
# Or port-forward
kubectl port-forward svc/prometheus-service 9090:9090
```
Then open: http://localhost:9090

**Grafana UI**:

**Windows (Docker Desktop Kubernetes)**:
- Open browser: http://localhost:30300

**Windows (Minikube)**:
```cmd
minikube service grafana-service --url
```

**macOS/Linux (Docker Desktop Kubernetes)**:
- Open browser: http://localhost:30300

**macOS/Linux (Minikube)**:
```bash
minikube service grafana-service --url
# Or port-forward
kubectl port-forward svc/grafana-service 3000:3000
```
Then open: http://localhost:3000

**Default Credentials**:
- Username: `admin`
- Password: `admin`
- (You'll be prompted to change password on first login)

#### Step 5: Verify Prometheus is Scraping Metrics

1. Open Prometheus UI (http://localhost:30090 or port-forwarded URL)
2. Go to **Status → Targets**
3. Verify `heart-disease-api` target shows as **UP**
4. If DOWN, check:
   - API pods are running: `kubectl get pods -l app=heart-disease`
   - Service is accessible: `kubectl get svc heart-disease-service`
   - Metrics endpoint works: See troubleshooting section

5. Test a query:
   - Go to **Graph** tab
   - Enter: `api_requests_total`
   - Click **Execute**
   - You should see metric values

#### Step 6: Configure Grafana Data Source

1. Log into Grafana (http://localhost:30300)
2. Go to **Configuration → Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Set URL: `http://prometheus-service:9090`
   - (For Kubernetes, use service name)
   - (For Docker Compose, use `http://prometheus:9090`)
6. Click **Save & Test**
7. You should see "Data source is working" message

#### Step 7: Import Dashboard

**Method 1: Import from JSON file**

1. In Grafana, go to **Dashboards → Import**
2. Click **Upload JSON file**
3. Select `grafana-dashboard.json` from this directory
4. Select **Prometheus** as data source
5. Click **Import**

**Method 2: Import from JSON content**

1. In Grafana, go to **Dashboards → Import**
2. Click **Import via panel json**
3. Copy and paste content from `grafana-dashboard.json`
4. Select **Prometheus** as data source
5. Click **Import**

**Method 3: Manual creation**

1. Go to **Dashboards → New Dashboard**
2. Add panels for:
   - API Requests Total (Stat panel)
   - Prediction Requests (Stat panel)
   - Request Latency (Graph panel with p50, p95, p99)
   - Predictions by Class (Pie chart)
   - Error Rate (Stat panel)
   - Request Rate (Graph panel)

### Option 2: Docker Compose Deployment (Local Development)

#### Step 1: Ensure API is Running

Make sure the Heart Disease API is running and accessible:
```bash
# Test API metrics endpoint
curl http://localhost:8000/metrics
```

#### Step 2: Update Prometheus Configuration

Edit `prometheus-config.yaml` and change the static target to point to your API:

```yaml
static_configs:
  - targets: ['host.docker.internal:8000']  # For Docker Desktop
  # Or use your machine's IP: ['192.168.1.100:8000']
```

#### Step 3: Start Monitoring Stack

```bash
# Navigate to monitoring directory
cd k8s/monitoring

# Start Prometheus and Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Verify containers are running
docker-compose -f docker-compose.monitoring.yml ps
```

**Expected Output**:
```
NAME                COMMAND                  SERVICE     CREATED         STATUS          PORTS
prometheus          "/bin/prometheus --c…"   prometheus  5 seconds ago   Up 4 seconds   0.0.0.0:9090->9090/tcp
grafana             "/run.sh"                grafana     5 seconds ago   Up 4 seconds   0.0.0.0:3000->3000/tcp
```

#### Step 4: Access Services

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`

#### Step 5: Configure and Import Dashboard

Follow steps 6-7 from Kubernetes deployment above, but use:
- Prometheus URL: `http://prometheus:9090` (for Docker Compose)

## Metrics Available

The Heart Disease API exposes the following Prometheus metrics at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `api_requests_total` | Counter | Total number of API requests |
| `prediction_requests_total` | Counter | Total number of prediction requests |
| `api_request_latency_ms` | Summary | Request latency in milliseconds (p50, p95, p99) |
| `predictions_by_class_total{class="0"}` | Counter | Total predictions for class 0 (No Disease) |
| `predictions_by_class_total{class="1"}` | Counter | Total predictions for class 1 (Disease) |
| `errors_total` | Counter | Total number of errors |

### Example Queries

**Total API Requests**:
```
api_requests_total
```

**Request Rate (requests per second)**:
```
rate(api_requests_total[5m])
```

**Average Latency**:
```
api_request_latency_ms{quantile="0.5"}
```

**95th Percentile Latency**:
```
api_request_latency_ms{quantile="0.95"}
```

**Error Rate**:
```
rate(errors_total[5m])
```

**Predictions Distribution**:
```
predictions_by_class_total
```

## Dashboard Features

The provided Grafana dashboard includes:

1. **API Requests Total** - Total number of requests received
2. **Prediction Requests** - Total number of predictions made
3. **Request Latency** - Graph showing p50, p95, p99 latency over time
4. **Predictions by Class** - Pie chart showing distribution of predictions
5. **Error Rate** - Total number of errors
6. **Request Rate** - Requests per second over time

## Troubleshooting

### Prometheus can't scrape metrics

**Symptom**: Target shows as DOWN in Prometheus UI

**Solutions**:

1. **Verify API is running**:
   ```bash
   kubectl get pods -l app=heart-disease
   kubectl get svc heart-disease-service
   ```

2. **Test metrics endpoint directly**:
   ```bash
   # Port-forward to API service
   kubectl port-forward svc/heart-disease-service 8000:80
   
   # In another terminal, test metrics
   curl http://localhost:8000/metrics
   ```

3. **Check Prometheus configuration**:
   ```bash
   # View Prometheus config
   kubectl get configmap prometheus-config -o yaml
   
   # Check Prometheus logs
   kubectl logs -l app=prometheus
   ```

4. **Verify service discovery**:
   - Check that API deployment has Prometheus annotations:
     ```bash
     kubectl get deployment heart-disease-deployment -o yaml | grep prometheus
     ```
   - Should show: `prometheus.io/scrape: "true"`

5. **For static config** (if service discovery fails):
   - Edit `prometheus-config.yaml`
   - Uncomment static_configs section
   - Update target to: `heart-disease-service:80`

### Grafana can't connect to Prometheus

**Symptom**: "Data source is not working" error

**Solutions**:

1. **Verify Prometheus service**:
   ```bash
   kubectl get svc prometheus-service
   ```

2. **Test connectivity from Grafana pod**:
   ```bash
   kubectl exec -it <grafana-pod-name> -- wget -O- http://prometheus-service:9090/api/v1/status/config
   ```

3. **Check Grafana datasource URL**:
   - Should be: `http://prometheus-service:9090` (for Kubernetes)
   - Or: `http://prometheus:9090` (for Docker Compose)

4. **Check Grafana logs**:
   ```bash
   kubectl logs -l app=grafana
   ```

### Port conflicts

**Symptom**: Services can't start or ports are already in use

**Solutions**:

1. **Check which ports are in use**:
   
   **Windows**:
   ```cmd
   netstat -ano | findstr :30090
   netstat -ano | findstr :30300
   ```

   **macOS/Linux**:
   ```bash
   lsof -i :30090
   lsof -i :30300
   ```

2. **Change NodePort values**:
   - Edit `prometheus-deployment.yaml` or `grafana-deployment.yaml`
   - Change `nodePort` to an available port (30000-32767 range)

3. **Use port-forward instead**:
   ```bash
   kubectl port-forward svc/prometheus-service 9090:9090
   kubectl port-forward svc/grafana-service 3000:3000
   ```

### No metrics appearing in Grafana

**Symptom**: Dashboard shows "No data"

**Solutions**:

1. **Verify metrics are being scraped**:
   - Open Prometheus UI
   - Go to Graph tab
   - Query: `api_requests_total`
   - If no data, see "Prometheus can't scrape metrics" above

2. **Check time range**:
   - In Grafana, ensure time range includes recent data
   - Try: Last 15 minutes or Last 1 hour

3. **Verify data source**:
   - Check Grafana data source is connected to Prometheus
   - Test query in Grafana: Go to Explore → Enter `api_requests_total`

4. **Generate some traffic**:
   ```bash
   # Make some API calls to generate metrics
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"features": [63.0, 1.0, 3.0, 145.0, 233.0, 1.0, 0.0, 150.0, 0.0, 2.3, 0.0, 0.0, 1.0]}'
   ```

### Prometheus pod keeps restarting

**Symptom**: `kubectl get pods` shows CrashLoopBackOff

**Solutions**:

1. **Check Prometheus logs**:
   ```bash
   kubectl logs -l app=prometheus --tail=50
   ```

2. **Verify ConfigMap exists**:
   ```bash
   kubectl get configmap prometheus-config
   ```

3. **Check storage permissions**:
   - Prometheus needs write access to `/prometheus`
   - Check pod security context if using restricted policies

### Grafana login issues

**Symptom**: Can't log in or password reset required

**Solutions**:

1. **Use default credentials**:
   - Username: `admin`
   - Password: `admin`

2. **Reset password** (if needed):
   ```bash
   # Access Grafana pod
   kubectl exec -it <grafana-pod-name> -- grafana-cli admin reset-admin-password admin
   ```

3. **Check environment variables**:
   ```bash
   kubectl get deployment grafana -o yaml | grep -A 5 env
   ```

## Cleanup

### Remove Kubernetes Deployment

```bash
# Delete Grafana
kubectl delete -f grafana-deployment.yaml

# Delete Prometheus
kubectl delete -f prometheus-deployment.yaml
kubectl delete -f prometheus-config.yaml
```

### Stop Docker Compose

```bash
cd k8s/monitoring
docker-compose -f docker-compose.monitoring.yml down

# Remove volumes (optional, removes all data)
docker-compose -f docker-compose.monitoring.yml down -v
```

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language (PromQL)](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard JSON Format](https://grafana.com/docs/grafana/latest/dashboards/json-model/)

## Next Steps

After setting up monitoring:

1. **Customize Dashboard**: Add more panels based on your needs
2. **Set Up Alerts**: Configure Grafana alerts for high error rates or latency
3. **Export Dashboard**: Share dashboard JSON with your team
4. **Persistent Storage**: Configure persistent volumes for Prometheus data retention
5. **Service Mesh Integration**: Consider integrating with Istio/Linkerd for advanced metrics
