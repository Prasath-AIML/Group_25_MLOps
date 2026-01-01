FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mlops.py .
COPY saved_models/ saved_models/

EXPOSE 8000

CMD ["uvicorn", "mlops:app", "--host", "0.0.0.0", "--port", "8000"]
