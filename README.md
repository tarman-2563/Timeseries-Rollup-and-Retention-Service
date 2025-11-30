# Time Series Metrics API

A FastAPI-based time series metrics ingestion and query service with automatic rollups and retention policies.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `.env` file (already configured)

3. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Service status
- `GET /db/status` - Database connection status

### Metrics
- `POST /metrics/ingest` - Ingest a metric
- `POST /query` - Query metrics with aggregation

## Background Jobs

### Rollup Job (runs every 60 seconds)
```bash
python -m app.jobs.rollup_job
```

### Retention Job (runs every 24 hours)
```bash
python -m app.jobs.retention_job
```

## Data Generator

Generate test data:
```bash
python -m app.services.data_generator --metric cpu_usage --pattern sine_wave --duration 300 --interval 5 --base-url http://localhost:8000
```

Patterns: noise, sine_wave, linear_trend, spike, combined

## Example API Calls

### Ingest a metric:
```bash
curl -X POST "http://localhost:8000/metrics/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "value": 75.5,
    "timestamp": "2024-06-01T12:00:00Z",
    "labels": {"host": "server1", "region": "us-west"},
    "tenant_id": "tenant_123"
  }'
```

### Query metrics:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "start_time": "2024-01-01T00:00:00Z",
    "end_time": "2024-01-02T00:00:00Z",
    "labels": {"host": "server1"},
    "function": "avg"
  }'
```
